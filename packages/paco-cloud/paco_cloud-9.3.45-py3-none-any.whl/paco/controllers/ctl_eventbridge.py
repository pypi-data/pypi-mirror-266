import os, sys
from paco.core.exception import StackException
from paco.core.exception import PacoErrorCode, InvalidPacoScope
from paco.controllers.controllers import Controller
from paco.stack_grps.grp_eventbridge import EventBridgeStackGroup
from botocore.exceptions import ClientError, BotoCoreError
from paco.core.yaml import YAML
from paco.models import schemas


yaml=YAML()
yaml.default_flow_sytle = False

class EventBridgeController(Controller):
    def __init__(self, paco_ctx):
        super().__init__(
            paco_ctx,
            "Resource",
            "EventBridge"
        )
        # breakpoint()
        self.init_done = False
        paco_ctx.project['resource']['eventbridge'].resolve_ref_obj = self


    def init(self, command=None, model_obj=None):
        if self.init_done:
            return
        self.init_done = True
        if command == 'init':
            return

        self.stack_grps = []
        self.stack_grp_map = {}

        # Detectors
        eventbridge_config = self.paco_ctx.project['resource']['eventbridge'].services
        if eventbridge_config != None:
            for account_name in eventbridge_config.keys():
                if 'account_name' not in self.stack_grp_map.keys():
                    self.stack_grp_map[account_name] = {}
                    for eventbridge_config in eventbridge_config[account_name].values():
                        region = eventbridge_config.name
                        self.create_stack_group(account_name, region, eventbridge_config)

    def create_stack_group(self, account_name, region, eventbridge_obj):
        account_ctx = self.paco_ctx.get_account_context(account_name=account_name)
        eventbridge_stack_group = EventBridgeStackGroup(
            self.paco_ctx,
            account_ctx,
            region,
            eventbridge_obj,
            self
        )
        if account_name not in self.stack_grp_map.keys():
            self.stack_grp_map[account_name] = {}
        if region not in self.stack_grp_map[account_name].keys():
            self.stack_grp_map[account_name][region] = {}
        self.stack_grp_map[account_name][region] = eventbridge_stack_group
        self.stack_grps.append(eventbridge_stack_group)

    def validate(self):
        for stack_group in self.stack_grps:
            stack_group.validate()

    def provision(self):
        for stack_group in self.stack_grps:
            stack_group.provision()

    def delete(self):
        for stack_group in self.stack_grps:
            stack_group.delete()

    def resolve_ref(self, ref):
        return None