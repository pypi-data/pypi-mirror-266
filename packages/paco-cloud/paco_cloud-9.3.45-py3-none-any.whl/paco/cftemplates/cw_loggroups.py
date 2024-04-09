from paco.cftemplates.cftemplates import StackTemplate
from paco.utils import prefixed_name
import troposphere
import troposphere.logs

class CloudWatchLogGroups(StackTemplate):
    def __init__(self, stack, paco_ctx):
        super().__init__(stack, paco_ctx)
        self.set_aws_name('LogGroups', self.resource_group_name, self.resource.name)

        # Troposphere Template Initialization
        self.init_template('CloudWatch Log Groups')
        if not self.resource.__parent__.is_enabled():
            return

        cfn_export_dict = {}
        for log_group in self.resource.values():
            if log_group.is_enabled() == False:
                continue
            log_group_name = log_group.get_full_log_group_name()
            loggroup_logical_id = self.create_cfn_logical_id('LogGroup' + log_group_name)

            # LogGroup name as a CFN Parameter
            param_name = 'Name' + loggroup_logical_id
            log_group_name_parameter = self.create_cfn_parameter(
                param_type='String',
                name=param_name,
                description='LogGroup name',
                value=log_group_name,
            )
            cfn_export_dict['LogGroupName'] = troposphere.Ref(log_group_name_parameter)

            if log_group.expire_events_after_days != 'Never':
                cfn_export_dict["RetentionInDays"] = log_group.expire_events_after_days

            if log_group.external_resource == False:
                log_group_resource = troposphere.logs.LogGroup.from_dict(
                    loggroup_logical_id,
                    cfn_export_dict
                )
                self.template.add_resource(log_group_resource)

            # TODO: Metric Filters
            self.create_output(
                title=f'{loggroup_logical_id}Arn',
                description=f'LogGroup {loggroup_logical_id} Arn',
                value=troposphere.GetAtt(log_group_resource, 'Arn'),
                ref=f'{self.resource.paco_ref_parts}.{log_group.name}.arn'
            )
