from paco.stack import StackOrder, Stack, StackGroup, StackHooks
import paco.cftemplates
from paco.core.exception import StackException
from paco.core.exception import PacoErrorCode
from paco.utils import md5sum
from paco.stack import StackTags
from paco.application import EventsRuleResourceEngine
from paco import models
from paco.stack.botostacks.inspector import InspectorBotoStack


class CloudWatchStackGroup(StackGroup):
    def __init__(
        self,
        paco_ctx,
        account_ctx,
        aws_region,
        region_config,
        controller,
        service_type='monitoring-account'
    ):
        super().__init__(
            paco_ctx,
            account_ctx,
            account_ctx.get_name(),
            None,
            controller
        )

        # Initialize config with a deepcopy of the project defaults
        self.stack_list = []
        self.stack_ref_map = {}
        self.account_ctx = account_ctx
        self.aws_region = aws_region
        self.config = region_config
        self.config.resolve_ref_obj = self

        # For EventsRuleResourceEngine
        self.stack_group = self
        self.app = self.paco_ctx.project['resource']['cloudwatch']
        self.ref_type = 'resource'


        if service_type == 'monitoring-account':
            self.create_monitoring_account_stack(service_type)
        elif service_type == 'logs':
            self.create_log_groups_stack()


    def create_monitoring_account_stack(self, service_type):
        # Monitoring Account
        monitoring_account_stack = self.add_new_stack(
            self.aws_region,
            self.config,
            paco.cftemplates.MonitoringAccount,
            extra_context={'service_type': service_type}
        )

        self.stack_list.append(monitoring_account_stack)
        self.stack_ref_map[self.config.paco_ref_parts] = monitoring_account_stack

    def create_log_groups_stack(self):
        # Logs
        log_groups_stack = self.add_new_stack(
            self.aws_region,
            self.config.log_groups,
            paco.cftemplates.CloudWatchLogGroups
        )

        self.stack_list.append(log_groups_stack)
        self.stack_ref_map[self.config.paco_ref_parts] = log_groups_stack


    def resolve_ref(self, ref):
        for stack in self.stack_list:
            if ref.ref.startswith(stack.resource.paco_ref_parts):
                return stack
        return None

