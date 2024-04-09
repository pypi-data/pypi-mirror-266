from paco import utils
from paco.cftemplates.cftemplates import StackTemplate
from paco.models import schemas
from paco.models.references import Reference
import troposphere
import troposphere.guardduty




class MonitoringAccount(StackTemplate):

    def __init__(self, stack, paco_ctx, service_type):
        account_config = stack.resource
        config_ref = account_config.paco_ref_parts
        super().__init__(stack, paco_ctx)

        if service_type == 'monitoring-account':
            account_type = 'monitoring'
        elif service_type == 'monitoring-account-source':
            account_type = 'source'
        else:
            raise Exception(f"Unknown service_type: {service_type}")

        group_name = self.resource_group_name
        if group_name == None:
            group_name = f'{account_type.title()}Account'
        self.set_aws_name('CloudWatch', 'OAM', group_name)

        template_fmt = f"""
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AWS CloudWatch {account_type.title()} Account'
{{0[monitoring_params]:s}}

Resources:
{{0[monitoring_yaml]:s}}"""


        template_table = {
            'monitoring_yaml': '',
            'monitoring_params': ''
        }

        sink_table = {
            'sink_name': None,
            'sink_policy': None
        }
        sink_fmt = """
    MonitoringAccountSink:
        Type: AWS::Oam::Sink
        Properties:
            Name: {0[sink_name]:s}
            Policy: {0[sink_policy]:s}

Outputs:
    MonitoringAccountSinkId:
        Value: !Ref MonitoringAccountSink
"""

        cfn_data_type_map = {
            'metrics': 'AWS::CloudWatch::Metric',
            'logs': 'AWS::Logs::LogGroup',
            'traces': 'AWS::XRay::Trace'
        }
        sink_policy_table = {
            'sink_policy_principles': None,
            'sink_policy_data_types': None
        }
        sink_policy_principle_fmt = """                            - {}
"""
        sink_data_type_fmt = """                                    - {}
"""
        sink_policy_fmt = """
                Version: '2012-10-17'
                Statement:
                    - Effect: Allow
                      Resource: "*"
                      Action: "oam:*"
                      Principal:
                        AWS:
{0[sink_policy_principles]:s}
                      Condition:
                          ForAllValues:StringEquals:
                              oam:ResourceTypes:
{0[sink_policy_data_types]:s}
        """

        link_params_fmt = """
Parameters:
    MonitoringAccountSinkId:
        Type: String
"""

        link_table = {
            'monitor_account_name': None,
            'resource_types': None
        }

        link_data_type_fmt = """                - {}
"""

        link_fmt = """
    MonitoringAccountLink{0[monitor_account_name]:s}:
        Type: AWS::Oam::Link
        Properties:
            LabelTemplate: "$AccountName"
            ResourceTypes:
{0[resource_types]:s}
            SinkIdentifier: !Ref MonitoringAccountSinkId
"""

        sink_account_name = Reference(account_config.paco_ref).get_account(self.paco_ctx.project).title()
        if account_type == 'source':
            # Source Account
            self.set_parameter('MonitoringAccountSinkId', account_config.paco_ref+'.id')
            link_table['monitor_account_name'] = sink_account_name
            link_data_types = ""
            for data_type in account_config.data_types:
                link_data_types += link_data_type_fmt.format(cfn_data_type_map[data_type])
            link_table['resource_types'] = link_data_types

            template_table['monitoring_params'] = link_params_fmt
            template_table['monitoring_yaml'] = link_fmt.format(link_table)
        else:
            # Centralized Monitoring Account
            sink_table['sink_name'] = sink_account_name
            source_id_list = ""
            for source_account_ref in account_config.source_accounts:
                source_account_id = Reference(source_account_ref+'.id').resolve(self.paco_ctx.project)
                source_id_list += sink_policy_principle_fmt.format(source_account_id)
            source_data_types = ""
            for data_type in account_config.data_types:
                source_data_types += sink_data_type_fmt.format(cfn_data_type_map[data_type])
            sink_policy_table = {
                'sink_policy_principles': source_id_list,
                'sink_policy_data_types': source_data_types
            }
            sink_table['sink_policy'] = sink_policy_fmt.format(sink_policy_table)
            template_table['monitoring_yaml'] = sink_fmt.format(sink_table)
            self.stack.register_stack_output_config(account_config.paco_ref_parts+'.id', 'MonitoringAccountSinkId')

        template_yaml = template_fmt.format(template_table)

        self.set_template(template_yaml)


