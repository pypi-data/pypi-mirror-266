from paco.stack import StackOrder, Stack, StackGroup, StackHooks
import paco.cftemplates
from paco.core.exception import StackException
from paco.core.exception import PacoErrorCode
from paco.utils import md5sum
from paco.stack import StackTags
from paco.application import EventsRuleResourceEngine
from paco import models


class EventBridgeStackGroup(StackGroup):
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
            'Buses-Rules',
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
        self.app = self.paco_ctx.project['resource']['eventbridge']
        self.ref_type = 'resource'

        for rules_config in self.config.buses.rules.values():

            stack_tags = StackTags()
            group_id = self.account_ctx.get_name()
            resource_id = self.config.name
            stack_tags.add_tag('Paco-Application-Group-Name', group_id)
            stack_tags.add_tag('Paco-Application-Resource-Name', resource_id)
            rules_config.resolve_ref_obj = self
            # Create a resource_engine object and initialize it
            resource_engine = EventsRuleResourceEngine(
                self,
                group_id,
                resource_id,
                rules_config,
                StackTags(stack_tags),
            )
            resource_engine.init_resource()
            # resource_engine.init_monitoring()

    def resolve_ref(self, ref):
        return self.stack_ref_map[ref.ref]

