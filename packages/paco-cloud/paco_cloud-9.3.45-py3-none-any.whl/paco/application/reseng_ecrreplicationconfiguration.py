from paco import cftemplates
from paco.application.res_engine import ResourceEngine
from paco.models.references import Reference
from paco.models.iam import Role
from paco.stack import StackHooks


class ECRReplicationConfigurationResourceEngine(ResourceEngine):
    def init_resource(self):
        account_ctx = self.account_ctx
        if hasattr(self.resource, 'account') and self.resource.account != None:
            account_ctx = self.paco_ctx.get_account_context(account_ref=self.resource.account)
        self.resource._reseng = self

        ecr_repo_stack = self.stack_group.add_new_stack(
            self.aws_region,
            self.resource,
            cftemplates.ECRReplicationConfiguration,
            stack_tags=self.stack_tags,
            account_ctx=account_ctx
        )

