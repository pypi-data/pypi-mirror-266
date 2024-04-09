from paco.stack import StackOrder, Stack, StackGroup, StackHooks
import paco.cftemplates
from paco.core.exception import StackException
from paco.core.exception import PacoErrorCode
from paco.utils import md5sum
from paco.stack import StackTags
from paco import models


class AppConfigStackGroup(StackGroup):
    def __init__(
        self,
        paco_ctx,
        account_ctx,
        aws_region,
        region_config,
        controller
    ):
        super().__init__(
            paco_ctx,
            account_ctx,
            account_ctx.get_name(),
            account_ctx.get_name(),
            controller
        )

        # Initialize config with a deepcopy of the project defaults
        self.stack_list = []
        self.stack_ref_map = {}
        self.account_ctx = account_ctx
        self.aws_region = aws_region
        self.config = region_config

        # For EventsRuleResourceEngine
        self.stack_group = self
        self.app = self.paco_ctx.project['resource']['appconfig']
        self.ref_type = 'resource'

        for app_config in self.config.applications.values():
            #stack_hooks = StackHooks()
            stack = self.add_new_stack(
                self.aws_region,
                app_config,
                paco.cftemplates.AppConfigApplication,
                #stack_hooks=stack_hooks
            )
            self.stack_list.append(stack)
            self.stack_ref_map[self.config.paco_ref_parts] = stack

    def resolve_ref(self, ref):
        return self.stack_ref_map[ref.ref]

