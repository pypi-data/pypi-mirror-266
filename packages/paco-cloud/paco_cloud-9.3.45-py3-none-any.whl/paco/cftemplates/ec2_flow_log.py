from awacs.aws import Allow, Statement, Policy, PolicyDocument, Principal, Action, Condition, StringEquals, StringLike
from awacs.sts import AssumeRole
from paco import utils
from paco.cftemplates.cftemplates import StackTemplate
from paco.models import schemas
import troposphere
import troposphere.ec2


class EC2FlowLog(StackTemplate):
    def __init__(self, stack, paco_ctx, role_name_prefix):
        flow_log_config = stack.resource
        config_ref = flow_log_config.paco_ref_parts
        super().__init__(stack, paco_ctx)
        self.set_aws_name('EC2FlowLog', self.resource_group_name, self.resource.name)

        # Troposphere Template Initialization
        self.init_template('EC2 Flow Log')

        if not flow_log_config.is_enabled():
            return

        # self.add_deliver_logs_role(role_name_prefix)

        log_destination_param = self.create_cfn_parameter(
            param_type='String',
            name='LogDestination',
            description='The Log Destination for this EC2 Flow Log.',
            value=flow_log_config.log_destination + '.arn',
        )

        resource_id_param = self.create_cfn_parameter(
            param_type='String',
            name='ResourceId',
            description='The Id of the resource for this EC2 Flow Log.',
            value=flow_log_config.resource_id + '.id',
        )

        flow_log_dict = {
            # 'DeliverLogsPermissionArn': '',
            # 'DestinationOptions': {
            #     'FileFormat': flow_log_config.destination_options.file_format,
            #     'HiveCompatiblePartitions': flow_log_config.destination_options.hive_compatible_partitions,
            #     'PerHourPartition': flow_log_config.destination_options.per_hour_partition
            # },
            'LogDestinationType': flow_log_config.log_destination_type,
            'LogDestination': troposphere.Ref(log_destination_param),
            # 'LogGroupName': None,
            'MaxAggregationInterval': flow_log_config.max_aggregation_interval,
            'ResourceId': troposphere.Ref(resource_id_param),
            'ResourceType': flow_log_config.resource_type,
            'TrafficType': flow_log_config.traffic_type

        }
        if flow_log_config.log_format != None:
            flow_log_dict['LogFormat'] = flow_log_config.log_format

        flow_log_res = troposphere.ec2.FlowLog.from_dict(
            'EC2FlowLog',
            flow_log_dict
        )
        self.template.add_resource(flow_log_res)

        # Outputs
        # self.create_output(
        #     title='ElasticIPAddress',
        #     description="The Elastic IP Address.",
        #     value=eip_address_value,
        #     ref=config_ref + ".address",
        # )
        # self.create_output(
        #     title='ElasticIPAllocationId',
        #     description="The Elastic IPs allocation id.",
        #     value=eip_allocation_id,
        #     ref=config_ref + ".allocation_id"
        # )


    # def add_deliver_logs_role(self, role_name_prefix):
    #     "Create a Role for delivering logs to the destination resource"

    #     self.deliver_logs_role_name = self.create_iam_resource_name(
    #         name_list=[role_name_prefix, self.app_name, self.resource_group_name, self.resource.name, 'EC2FlowLogs-Role'],
    #         filter_id='IAM.Role.RoleName'
    #     )
    #     role_res = troposphere.iam.Role(
    #         title='EC2FlowLogDeliverLogsRole',
    #         template = self.template,
    #         RoleName=self.deliver_logs_role_name,
    #         AssumeRolePolicyDocument=PolicyDocument(
    #             Version="2012-10-17",
    #             Statement=[
    #                 Statement(
    #                     Effect=Allow,
    #                     Action=[ AssumeRole ],
    #                     Principal=Principal("Service", ['codepipeline.amazonaws.com']),
    #                 )
    #             ]
    #         )
    #     )
    #     statement_list = [
    #         Statement(
    #             Sid='CodePipelineAccess',
    #             Effect=Allow,
    #             Action=[
    #                 Action('?', '*'),
    #             ],
    #             Resource=[ '*' ]
    #         ),
    #     ]