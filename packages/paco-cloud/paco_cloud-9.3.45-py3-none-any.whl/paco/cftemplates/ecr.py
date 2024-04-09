from awacs.aws import Allow, Action, Principal, Statement, Condition, MultiFactorAuthPresent, PolicyDocument, StringEquals
from paco.cftemplates.cftemplates import StackTemplate
from paco.utils import prefixed_name
from paco.models.references import get_model_obj_from_ref
import troposphere
import troposphere.ecr


class ECRRepository(StackTemplate):
    def __init__(self, stack, paco_ctx):
        ecr_repository = stack.resource
        super().__init__(stack, paco_ctx)
        self.set_aws_name('ECRRepository', self.resource_group_name, self.resource.name)


        self.init_template('Elastic Container Registry (ECR) Repository')
        if not ecr_repository.is_enabled(): return

        repository_name = ecr_repository.full_repository_name
        repo_dict = {
            'RepositoryName': repository_name
        }

        if ecr_repository.image_scanning != None:
            repo_dict['ImageScanningConfiguration'] = {
                'ScanOnPush': ecr_repository.image_scanning.scan_on_push
            }

        if ecr_repository.lifecycle_policy_text != None and ecr_repository.lifecycle_policy_text != "":
            repo_dict['LifecyclePolicy'] = troposphere.ecr.LifecyclePolicy(
                LifecyclePolicyText = ecr_repository.lifecycle_policy_text
            )
        if ecr_repository.lifecycle_policies != None and len(ecr_repository.lifecycle_policies.keys()) > 0:
            policy_rule_json_text = ""
            comma = ""
            for policy_id in ecr_repository.lifecycle_policies.keys():
                policy_config = ecr_repository.lifecycle_policies[policy_id]
                tag_prefix_list = ""
                count_unit = ""
                if len(policy_config.tag_prefix_list) > 0:
                    tag_prefix_list = '"tagPrefixList": ['
                    for tag_prefix in policy_config.tag_prefix_list:
                        tag_prefix_list += f'"{tag_prefix}"'
                    tag_prefix_list = '],'
                if policy_config.count_type == "sinceImagePushed":
                    count_unit = '"countUnit": "days",'

                policy_selection_json_text = f"""
            "selection": {{
                {count_unit}
                {tag_prefix_list}
                "tagStatus": "{policy_config.tag_status}",
                "countType": "{policy_config.count_type}",
                "countNumber": {policy_config.count_number}
            }},
"""
                policy_rule_json_text += f"""
        {{
            "rulePriority": {policy_config.rule_priority},
            "description": "{policy_config.description}",
            {policy_selection_json_text}
            "action": {{
                "type": "expire"
            }}
        }}{comma}
"""
                comma=","
            policy_json_text = f"""
{{
    "rules": [
        {policy_rule_json_text}
    ]
}}
"""
            repo_dict['LifecyclePolicy'] = {
                "LifecyclePolicyText": policy_json_text,
            }
        if ecr_repository.repository_policy != None or ecr_repository.cross_account_access != []:
            policy_statements = []
            if ecr_repository.repository_policy != None:
                index = 0
                for policy_statement in ecr_repository.repository_policy.statement:
                    statement_dict = {
                        'Sid': f'Policy{index}',
                        'Effect': policy_statement.effect,
                        'Action': [
                            Action(*action.split(':')) for action in policy_statement.action
                        ]
                    }
                    if policy_statement.principal != None:
                        if len(policy_statement.principal.aws) > 0:
                            statement_dict['Principal'] = Principal("AWS", policy_statement.principal.aws)
                        elif len(policy_statement.principal.service) > 0:
                            statement_dict['Principal'] = Principal("Service", policy_statement.principal.service)
                    policy_statements.append(
                        Statement(**statement_dict)
                    )
                    index += 1
            if ecr_repository.cross_account_access != []:
                account_ids = []
                for account_ref in ecr_repository.cross_account_access:
                    account = get_model_obj_from_ref(account_ref, self.paco_ctx.project)
                    account_ids.append(account.account_id)
                statement_dict = {
                    'Sid': 'AllowCrossAccountAccess',
                    'Effect': 'Allow',
                    'Action': [
                        Action('ecr', 'BatchCheckLayerAvailability'),
                        Action('ecr', 'BatchGetImage'),
                        Action('ecr', 'CompleteLayerUpload'),
                        Action('ecr', 'DescribeImageScanFindings'),
                        Action('ecr', 'DescribeImages'),
                        Action('ecr', 'DescribeRepositories'),
                        Action('ecr', 'GetAuthorizationToken'),
                        Action('ecr', 'GetDownloadUrlForLayer'),
                        Action('ecr', 'GetLifecyclePolicy'),
                        Action('ecr', 'GetLifecyclePolicyPreview'),
                        Action('ecr', 'GetRepositoryPolicy'),
                        Action('ecr', 'InitiateLayerUpload'),
                        Action('ecr', 'ListImages'),
                        Action('ecr', 'ListTagsForResource'),
                        Action('ecr', 'PutImage'),
                        Action('ecr', 'UploadLayerPart'),
                    ],
                    'Principal': Principal("AWS", account_ids),
                }
                policy_statements.append(Statement(**statement_dict))
            repo_dict['RepositoryPolicyText'] = PolicyDocument(
                Version="2012-10-17",
                Statement=policy_statements
            )
        repository_res = troposphere.ecr.Repository.from_dict(
            'Repository', repo_dict
        )
        self.template.add_resource(repository_res)

        # Outputs
        self.create_repository_outputs(
            ecr_repository=ecr_repository,
            repository_arn=troposphere.GetAtt(repository_res, 'Arn'),
            repository_name=repository_name
        )



    def create_repository_outputs(self, ecr_repository, repository_arn, repository_name):
        self.create_output(
            title='RepositoryArn',
            description="ECR Repository Arn",
            value=repository_arn,
            ref=ecr_repository.paco_ref_parts + ".arn")

        self.create_output(
            title='RepositoryName',
            description="ECR Repository Name",
            value=repository_name,
            ref=ecr_repository.paco_ref_parts + ".name")


class ECRReplicationConfiguration(StackTemplate):
    def __init__(self, stack, paco_ctx):
        ecr_replication_config = stack.resource
        super().__init__(stack, paco_ctx)
        self.set_aws_name('ECRReplicationConfiguration', self.resource_group_name, self.resource.name)


        self.init_template('Elastic Container Registry (ECR) Replication Configuration')
        if not ecr_replication_config.is_enabled(): return

        cfn_template_yaml = """
AWSTemplateFormatVersion: '2010-09-09'
Description: Elastic Container Registry (ECR) Replication Configuration
Resources:
  EmptyTemplatePlaceholder:
    Type: AWS::CloudFormation::WaitConditionHandle
  ReplicationConfiguration:
    Properties:
      ReplicationConfiguration:
        Rules:
{0[rules]:s}
    Type: AWS::ECR::ReplicationConfiguration
"""

        cfn_rule_destination_yaml = """
            - Destinations:
{0[rule_destinations]:s}
"""
        cfn_rule_filters_yaml = """
              RepositoryFilters:
{0[rule_filters]:s}
"""

        cfn_rule_dest_yaml = """
                - Region: '{0[region]:s}'
                  RegistryId: '{0[account_id]:s}'
"""
        cfn_rule_filter_yaml = """
                - Filter: {0[filter]:s}
                  FilterType: PREFIX_MATCH
"""

        env_name = self.config_ref.split('.')[2]
        rules_yaml = ""
        for (rule_name, rule_config) in ecr_replication_config.rules.items():
            # Destinations
            destinations_yaml = ""
            for region in rule_config.regions:
                destination_table = {
                    'region': region,
                    'account_id': self.account_ctx.id
                }
                destinations_yaml += cfn_rule_dest_yaml.format(destination_table)
            rule_dest_table = {
                'rule_destinations': destinations_yaml,
            }
            rules_yaml += cfn_rule_destination_yaml.format(rule_dest_table)
            # Filters
            if len(rule_config.repositories) > 0:
                filters_yaml = ""
                for repository in rule_config.repositories:
                    repository = repository.replace('<environment>', env_name)
                    filter_table = {
                        'filter': repository
                    }
                    filters_yaml += cfn_rule_filter_yaml.format(filter_table)
                rule_filter_table = {
                    'rule_filters': filters_yaml,
                }
                rules_yaml += cfn_rule_filters_yaml.format(rule_filter_table)

        replication_config_table = {
            'rules': rules_yaml
        }
        replication_config_yaml = cfn_template_yaml.format(replication_config_table)

        self.set_template(replication_config_yaml)