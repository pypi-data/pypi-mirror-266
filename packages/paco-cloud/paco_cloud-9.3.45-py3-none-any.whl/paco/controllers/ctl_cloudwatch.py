import os
import paco.cftemplates
from paco.controllers.controllers import Controller
from paco.models.references import Reference
from paco.stack import Stack, StackGroup
from paco.stack_grps.grp_cloudwatch import CloudWatchStackGroup


class CloudWatchController(Controller):
    def __init__(self, paco_ctx):
        if paco_ctx.legacy_flag('cloudwatch_controller_type_2019_09_18') == True:
            controller_type = 'Service'
        else:
            controller_type = 'Resource'
        super().__init__(paco_ctx,
                         controller_type,
                         "CloudWatch")

        self.event_stacks = {}
        self.second = False
        self.init_done = False
        self.stack_grps = []
        self.stack_grp_map = {}

        if not 'cloudwatch' in self.paco_ctx.project['resource']:
            self.init_done = True
            return
        self.config = self.paco_ctx.project['resource']['cloudwatch']
        if self.config != None:
            self.config.resolve_ref_obj = self

        #self.paco_ctx.log("Route53 Service: Configuration: %s" % (name)

    def init(self, command=None, model_obj=None):
        if self.init_done:
            return
        self.config.resolv_ref_obj = self
        self.init_done = True

        # Centralized Monitoring Accounts
        monitoring_config = self.paco_ctx.project['resource']['cloudwatch'].monitoring_accounts
        if monitoring_config != None:
            for account_name in monitoring_config.keys():
                if 'account_name' not in self.stack_grp_map.keys():
                    self.stack_grp_map[account_name] = {}
                    for account_config in monitoring_config[account_name].values():
                        # Monitoring Account
                        region = account_config.name
                        self.create_stack_group(account_name, region, account_config, 'monitoring-account')
                        # Source Accounts
                        for source_account in account_config.source_accounts:
                            source_account_name = Reference(source_account).get_account(self.paco_ctx.project).name
                            self.create_stack_group(source_account_name, region, account_config, 'monitoring-account-source')

        # Logs
        logs_config = self.paco_ctx.project['resource']['cloudwatch'].logs
        if logs_config != None:
            for account_name in logs_config.keys():
                if 'account_name' not in self.stack_grp_map.keys():
                    self.stack_grp_map[account_name] = {}
                    for account_config in logs_config[account_name].values():
                        # Monitoring Account
                        region = account_config.name
                        self.create_stack_group(account_name, region, account_config, 'logs')


    def create_stack_group(self, account_name, region, monitor_account_obj, service_type):
        account_ctx = self.paco_ctx.get_account_context(account_name=account_name)
        cloudwatch_stack_group = CloudWatchStackGroup(
            self.paco_ctx,
            account_ctx,
            region,
            monitor_account_obj,
            self,
            service_type
        )
        if account_name not in self.stack_grp_map.keys():
            self.stack_grp_map[account_name] = {}
        if region not in self.stack_grp_map[account_name].keys():
            self.stack_grp_map[account_name][region] = {}
        self.stack_grp_map[account_name][region] = cloudwatch_stack_group
        self.stack_grps.append(cloudwatch_stack_group)

    def create_event_rule(  self,
                            paco_ctx,
                            account_ctx,
                            aws_region,
                            stack_group,
                            event_description,
                            schedule_expression,
                            target_arn,
                            target_id,
                            config_ref):
        event_rule_template = paco.cftemplates.CWEventRule(
            self.paco_ctx,
            account_ctx,
            aws_region,
            stack_group,
            None, # stack_tags
            event_description,
            schedule_expression,
            target_arn,
            target_id,
            config_ref
        )

        self.event_stacks[config_ref] = event_rule_template.stack

    def validate(self):
        for stack_group in self.stack_grps:
            stack_group.validate()

    def provision(self):
        for stack_group in self.stack_grps:
            stack_group.provision()

    def delete(self):
        for stack_group in reversed(self.stack_grps):
            stack_group.delete()

    def get_event_stack(self, config_ref):
        return self.event_stacks[config_ref]

    def resolve_ref(self, ref):
        account = ref.get_account(self.paco_ctx.project)
        region = ref.region
        return self.stack_grp_map[account][region].resolve_ref(ref)
