import copy
from paco import models
from paco.application.res_engine import ResourceEngine
from paco.core import exception
from paco.core.yaml import YAML
from paco.models import vocabulary
from paco.models.references import is_ref, Reference
import paco.cftemplates


yaml=YAML()
yaml.default_flow_sytle = False

LAMBDA_FUNC_ARN_ACTION_MAP = [
    'InvokeFunction',
    'PublishVersion',
    'UpdateFunctionCode',
    'UpdateFunctionConfiguration'
]
LAMBDA_PUBLISH_LAYER_MAP = [
    'PublishLayerVersion'
]

class LambdaResourceEngine(ResourceEngine):

    def init_resource(self):
        # is this for Lambda@Edge?
        edge_enabled = False
        if self.resource.region != None:
            self.aws_region = self.resource.region
        if self.resource.edge != None and self.resource.edge.is_enabled():
            edge_enabled = True

        if self.resource.account != None:
            account_ctx = self.paco_ctx.get_account_context(self.resource.account)
        else:
            account_ctx = self.account_ctx

        # Create function execution role
        role_name = 'iam_role'
        if self.resource.iam_role and self.resource.iam_role.enabled == False:
            role_config_yaml = """
instance_profile: false
path: /
role_name: %s""" % ("LambdaFunction")
            role_config_dict = yaml.load(role_config_yaml)
            role_config = models.iam.Role(role_name, self.resource)
            role_config.apply_config(role_config_dict)
        else:
            role_config = self.resource.iam_role

        # Note that CloudWatch LogGroup permissions are added in the Lambda stack
        # This is to allow CloudFormation to create the LogGroup to manage it's Retention policy
        # and to prevent the Lambda from being invoked and writing to the LogGroup before it's
        # created by CloudFormation and creating a LogGroup and causing a race condition in the stack.
        # Also, by setting the Policy after the Lambda it's possible to restrict the policy to just
        # the Lambda LogGroups and not leave it wide open like AWSLambdaBasicExecutionRole does.

        if self.resource.vpc_config != None:
            # ToDo: Security: restrict resource
            vpc_config_policy = """
name: VPCAccess
statement:
  - effect: Allow
    action:
      - ec2:CreateNetworkInterface
      - ec2:DescribeNetworkInterfaces
      - ec2:DeleteNetworkInterface
    resource:
      - '*'
"""
            role_config.add_policy(yaml.load(vpc_config_policy))

        # The ID to give this role is: group.resource.iam_role
        iam_role_id = self.gen_iam_role_id(self.res_id, role_name)
        # If no assume policy has been added, force one here since we know its
        # a Lambda function using it.
        # Set defaults if assume role policy was not explicitly configured
        if not hasattr(role_config, 'assume_role_policy') or role_config.assume_role_policy == None:
            service = ['lambda.amazonaws.com']
            # allow Edge if it's enabled
            if edge_enabled:
                service.append('edgelambda.amazonaws.com')
            policy_dict = {
                'effect': 'Allow',
                'aws': [f"arn:aws:iam::{account_ctx.get_id()}:root"],
                'service': service
            }
            role_config.set_assume_role_policy(policy_dict)
        # Always turn off instance profiles for Lambda functions
        role_config.instance_profile = False
        role_config.enabled = self.resource.is_enabled()
        iam_ctl = self.paco_ctx.get_controller('IAM')
        iam_ctl.add_role(
            region=self.aws_region,
            resource=self.resource,
            role=role_config,
            iam_role_id=iam_role_id,
            stack_group=self.stack_group,
            stack_tags=self.stack_tags
        )

        self.stack = self.stack_group.add_new_stack(
            self.aws_region,
            self.resource,
            paco.cftemplates.Lambda,
            account_ctx=account_ctx,
            stack_tags=self.stack_tags
        )

        # Provision Lambda subscriptions in the same region as the SNS Topics
        # This is required for cross account + cross region lambda/sns
        region_topic_list = {}
        for topic in self.resource.sns_topics:
            if is_ref(topic):
                region_name = topic.split('.')[4]
            else:
                region_name = topic.split(':')[3]
            if region_name not in vocabulary.aws_regions.keys():
                raise exception.InvalidAWSRegion(f'Invalid SNS Topic region in reference: {region_name}: {topic}')
            if region_name not in region_topic_list.keys():
                region_topic_list[region_name] = []
            region_topic_list[region_name].append(topic)

        for region_name in region_topic_list.keys():
            topic_list = region_topic_list[region_name]
            self.stack = self.stack_group.add_new_stack(
                region_name,
                self.resource,
                paco.cftemplates.LambdaSNSSubscriptions,
                stack_tags=self.stack_tags,
                extra_context={'sns_topic_list': topic_list}
            )

        # OIDC Idetity Provider Role
        if self.resource.identity_provider_roles != None:
            policy_template = {
                'name': 'IDPLambdaStatements',
                'statement': []
            }

            invoke_func_statement_template = {
                'effect': "Allow",
                'action': [],
                'resource': [
                    "!Ref LambdaFunctionArn"
                ]
            }

            publish_layer_statement_template = {
                "effect": "Allow",
                "action": [
                    "lambda:PublishLayerVersion"
                ],
                "resource": [
                    f"arn:aws:lambda:{self.aws_region}:{self.account_ctx.id}:layer:*"
                ]
            }


            for idp_role_config in self.resource.identity_provider_roles.values():
                provider_arn_ref = Reference(idp_role_config.provider + '.arn')
                provider_arn = provider_arn_ref.resolve(self.paco_ctx.project, account_ctx=None, resolve_from_outputs=True)
                assume_role_policy_statements = []
                for repo_filter in idp_role_config.repository_filters:
                    assume_role_policy_statement = {
                        'effect': 'Allow',
                        'action': 'sts:AssumeRoleWithWebIdentity',
                        'principal': {
                            'federated': provider_arn
                        },
                        'condition': {
                            'StringEquals': {
                                "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                            },
                            'StringLike': {
                                "token.actions.githubusercontent.com:sub": repo_filter
                            }
                        }
                    }
                    assume_role_policy_statements.append(assume_role_policy_statement)

                policy = copy.deepcopy(policy_template)
                invoke_func_statement = copy.deepcopy(invoke_func_statement_template)
                for policy_action in idp_role_config.policy_actions:
                    if policy_action in LAMBDA_FUNC_ARN_ACTION_MAP:
                        invoke_func_statement['action'].append(f'lambda:{policy_action}')
                    elif policy_action in LAMBDA_PUBLISH_LAYER_MAP:
                        policy['statement'].append(publish_layer_statement_template)

                policy['statement'].append(invoke_func_statement)
                role_name = f'IDPRole'
                role_dict = {
                    'enabled': idp_role_config.is_enabled(),
                    'path': '/',
                    'role_name': role_name,
                    'assume_role_policies': {
                        'statement': assume_role_policy_statements
                    },
                    'policies': [policy]
                    #'policies': [{'name': 'IoTTopicRule', 'statement': statements}]
                }
                role_params = [
                    {
                        'description': 'Lambda Function ARN',
                        'type': 'String',
                        'key': 'LambdaFunctionArn',
                        'value': self.resource.paco_ref+'.arn'
                    }
                ]

                role = models.iam.Role(role_name, self.resource)
                role.apply_config(role_dict)

                #role.policies = idp_role_config.policies
                iam_ctl = self.paco_ctx.get_controller('IAM')
                iam_role_id = self.gen_iam_role_id(idp_role_config.name, 'IDPRole')
                iam_ctl.add_role(
                    region=self.aws_region,
                    resource=self.resource,
                    role=role,
                    iam_role_id=iam_role_id,
                    stack_group=self.stack_group,
                    stack_tags=self.stack_tags,
                    template_params=role_params,
                )