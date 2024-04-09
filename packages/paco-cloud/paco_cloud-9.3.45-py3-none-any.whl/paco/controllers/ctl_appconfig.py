import os, sys
from paco.core.exception import StackException
from paco.core.exception import PacoErrorCode, InvalidPacoScope
from paco.controllers.controllers import Controller
from paco.stack_grps.grp_appconfig import AppConfigStackGroup
from botocore.exceptions import ClientError, BotoCoreError
from paco.core.yaml import YAML
from paco.models import schemas


yaml=YAML()
yaml.default_flow_sytle = False

class AppConfigController(Controller):
    def __init__(self, paco_ctx):
        super().__init__(
            paco_ctx,
            "Resource",
            "AppConfig"
        )
        # breakpoint()
        self.init_done = False
        paco_ctx.project['resource']['appconfig'].resolve_ref_obj = self
        self.stack_group_map = {}
        self.stack_group_list = []


    def init(self, command=None, model_obj=None):
        if self.init_done:
            return
        self.init_done = True
        if command == 'init':
            return

        # Detectors
        config = self.paco_ctx.project['resource']['appconfig']
        if config != None:
            for account_name in config.keys():
                if 'account_name' not in self.stack_group_map.keys():
                    self.stack_group_map[account_name] = {}
                    for region_config in config[account_name].values():
                        region = region_config.name
                        self.create_stack_group(account_name, region, region_config)

    def create_stack_group(self, account_name, region, region_config):
        account_ctx = self.paco_ctx.get_account_context(account_name=account_name)
        stack_group = AppConfigStackGroup(
            self.paco_ctx,
            account_ctx,
            region,
            region_config,
            self
        )
        if account_name not in self.stack_group_map.keys():
            self.stack_group_map[account_name] = {}
        if region not in self.stack_group_map[account_name].keys():
            self.stack_group_map[account_name][region] = {}
        self.stack_group_map[account_name][region] = stack_group
        self.stack_group_list.append(stack_group)

    def validate(self):
        for stack_group in self.stack_group_list:
            stack_group.validate()

    def provision(self):
        for stack_group in self.stack_group_list:
            stack_group.provision()

    def delete(self):
        for stack_group in self.stack_group_list:
            stack_group.delete()

    def resolve_ref(self, ref):
        return None