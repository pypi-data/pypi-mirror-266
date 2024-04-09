from paco import cftemplates
from paco.application.res_engine import ResourceEngine
from paco.models.references import Reference
from paco.models.iam import Role
from paco.stack import StackHooks


class ECRRepositoryResourceEngine(ResourceEngine):
    def init_resource(self):
        account_ctx = self.account_ctx
        if hasattr(self.resource, 'account') and self.resource.account != None:
            account_ctx = self.paco_ctx.get_account_context(account_ref=self.resource.account)
        self.resource._reseng = self


        # This saves the information needed by ECR resource when called
        # by paco.refs
        if self.resource.external_repository_arn != None:
            self.resource._external_repository_name = self.resource.external_repository_arn.split('/')[1]
            return

        stack_hooks = StackHooks()
        # Stack hooks for saving state to the Paco bucket
        stack_hooks.add(
            name='ECRRepository.Cleanup',
            stack_action=['delete'],
            stack_timing='pre',
            hook_method=self.stack_hook_ecr_repository_cleanup,
        )

        ecr_repo_stack = self.stack_group.add_new_stack(
            self.aws_region,
            self.resource,
            cftemplates.ECRRepository,
            stack_tags=self.stack_tags,
            account_ctx=account_ctx,
            stack_hooks=stack_hooks
        )

        # Identity Provider Roles
        if self.resource.identity_provider_roles != None:
            repository_arn = self.resource.repository_arn(self.aws_region, self.account_ctx.id)
            repository_policies = [
                {
                    'name': 'RepositoryAccess',
                    'statement': [
                        {
                            "effect": "Allow",
                            "action": [
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:BatchGetImage",
                                "ecr:CompleteLayerUpload",
                                "ecr:UploadLayerPart",
                                "ecr:InitiateLayerUpload",
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:PutImage"
                            ],
                            "resource": [
                                repository_arn
                            ]
                        },
                        {
                            "effect": "Allow",
                            "action": "ecr:GetAuthorizationToken",
                            "resource": "*"
                        }
                    ]
                }
            ]

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
                role_name = f'IDPRole'
                role_dict = {
                    'enabled': idp_role_config.is_enabled(),
                    'path': '/',
                    'role_name': role_name,
                    'assume_role_policies': {
                        'statement': assume_role_policy_statements
                    },
                    'policies': repository_policies
                    #'policies': [{'name': 'IoTTopicRule', 'statement': statements}]
                }
                role = Role(role_name, self.resource)
                role.apply_config(role_dict)
                iam_ctl = self.paco_ctx.get_controller('IAM')
                iam_role_id = self.gen_iam_role_id(idp_role_config.name, 'IDPRole')
                iam_ctl.add_role(
                    region=self.aws_region,
                    resource=self.resource,
                    role=role,
                    iam_role_id=iam_role_id,
                    stack_group=self.stack_group,
                    stack_tags=self.stack_tags,
                    #template_params=role_params,
                )

    def stack_hook_ecr_repository_cleanup(self, hook, config):
        ecr_client = self.account_ctx.get_aws_client('ecr', aws_region=self.aws_region)
        try:
            images_list = ecr_client.list_images(
                registryId=self.account_ctx.id,
                repositoryName=self.resource.full_repository_name
            )
        except ecr_client.exceptions.RepositoryNotFoundException as e:
            return

        if len(images_list['imageIds']) > 0:
            response = ecr_client.batch_delete_image(
                registryId=self.account_ctx.id,
                repositoryName=self.resource.full_repository_name,
                imageIds=images_list['imageIds']
            )
