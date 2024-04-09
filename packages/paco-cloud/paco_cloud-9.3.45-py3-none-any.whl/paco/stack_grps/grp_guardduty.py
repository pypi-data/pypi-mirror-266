from paco.stack import StackOrder, Stack, StackGroup, StackHooks
import paco.cftemplates
from paco.core.exception import StackException
from paco.core.exception import PacoErrorCode
from paco.utils import md5sum
from paco.stack import StackTags
from paco.application import EventsRuleResourceEngine
from paco import models


class GuardDutyStackGroup(StackGroup):
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
            'Resource',
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
        self.app = self.paco_ctx.project['resource']['guardduty']
        self.ref_type = 'resource'
        self.config.external_resource = True

        #stack_hooks = StackHooks()
        if self.config.external_resource == False:
            detector_stack = self.add_new_stack(
                self.aws_region,
                self.config,
                paco.cftemplates.GuardDuty,
                #stack_hooks=stack_hooks
            )
            self.stack_list.append(detector_stack)
            self.stack_ref_map[self.config.paco_ref_parts] = detector_stack

        if self.config.monitoring:
            events_rule_dict = {
                'type': 'EventsRule',
                'enabled': self.config.monitoring.is_enabled(),
                'description': '',
                'event_pattern': {
                    "source": [
                        self.config.paco_ref
                    ],
                    "detail_type": [
                        "GuardDuty Finding"
                    ],
                    "detail": {
                        "severity": []
                    }
                }
            }

            enabled_severities = [1, 2, 3, 4, 5, 6, 7, 8]
            severity_list = []
            for severity_major in enabled_severities:
                severity_list.append(severity_major)
                for severity_minor in range(0, 9):
                    severity_minor_str = f'{severity_major}.{severity_minor}'
                    severity_list.append(float(severity_minor_str))
            events_rule_dict['event_pattern']['detail']['severity'] = severity_list


            events_rule_config = models.events.EventsRule('detector_events_rule', self.config)
            events_rule_config.apply_config(events_rule_dict)
            events_rule_config.monitoring = self.config.monitoring

            stack_tags = StackTags()
            group_id = self.account_ctx.get_name()
            resource_id = self.config.name
            stack_tags.add_tag('Paco-Application-Group-Name', group_id)
            stack_tags.add_tag('Paco-Application-Resource-Name', resource_id)
            events_rule_config.resolve_ref_obj = self
            # Create a resource_engine object and initialize it
            resource_engine = EventsRuleResourceEngine(
                self,
                group_id,
                resource_id,
                events_rule_config,
                StackTags(stack_tags),
            )
            resource_engine.init_resource()
            # resource_engine.init_monitoring()

    def resolve_ref(self, ref):
        return self.stack_ref_map[ref.ref]

