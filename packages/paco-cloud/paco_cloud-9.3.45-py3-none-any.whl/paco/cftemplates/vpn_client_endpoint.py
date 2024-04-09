from paco.cftemplates.cftemplates import StackTemplate
from paco.models import schemas
from paco.models.locations import get_parent_by_interface
from paco.utils import md5sum
import troposphere.ec2
import troposphere.logs

troposphere.ec2.ClientVpnEndpoint.props['SecurityGroupIds'] = (list, False)

class VPNClientEndpoint(StackTemplate):
    def __init__(self, stack, paco_ctx):
        super().__init__(stack, paco_ctx)
        self.set_aws_name('VPNClientEndpoint', self.resource_group_name)

        # Troposphere Template Initialization
        self.init_template('VPN Client Endpoint')
        vpn_endpoint_config = self.resource

        if self.resource.is_enabled() == False:
            return

        network_config = get_parent_by_interface(self.resource, schemas.INetwork)

        # LogGroup
        vpn_endpoint_log_group_name = f'{self.resource.paco_ref_parts}'
        vpn_endpoint_log_stream_name = 'vpn-connection-data'
        vpn_endpoint_log_group_dict = {
            'LogGroupName': vpn_endpoint_log_group_name,
            'RetentionInDays': 365
        }
        vpn_endpoint_log_group_res = troposphere.logs.LogGroup.from_dict(
            'VPNClientEndpointLogGroup',
            vpn_endpoint_log_group_dict
        )
        self.template.add_resource(vpn_endpoint_log_group_res)
        # Log Stream
        vpn_endpoint_log_stream_dict = {
            'LogGroupName': vpn_endpoint_log_group_name,
            'LogStreamName': vpn_endpoint_log_stream_name
        }
        vpn_endpoint_log_stream_res = troposphere.logs.LogStream.from_dict(
            'VPNClientEndpointLogStream',
            vpn_endpoint_log_stream_dict
        )
        vpn_endpoint_log_stream_res.DependsOn = vpn_endpoint_log_group_res
        self.template.add_resource(vpn_endpoint_log_stream_res)

        # ClientVpnEndpoint
        vpc_id_param = self.create_cfn_parameter(
            name='VpcId',
            param_type='AWS::EC2::VPC::Id',
            description='The VPC Id',
            value=f'{network_config.paco_ref}.vpc.id'
        )
        security_group_list_param = self.create_cfn_ref_list_param(
            param_type='List<AWS::EC2::SecurityGroup::Id>',
            name='SecurityGroupList',
            description='A List of security groups to attach to the LB',
            value=vpn_endpoint_config.security_groups,
            ref_attribute='id'
        )

        vpn_endpoint_dict = {
            'AuthenticationOptions': [
                {
                    'Type': 'certificate-authentication',
                    'MutualAuthentication': {
                        'ClientRootCertificateChainArn': vpn_endpoint_config.server_certificate_arn
                    }
                }
            ],
            'ClientCidrBlock': vpn_endpoint_config.client_cidr_block,
            'ConnectionLogOptions': {
                'Enabled': False
            },
            'SelfServicePortal': vpn_endpoint_config.self_service_portal,
            'ServerCertificateArn': vpn_endpoint_config.server_certificate_arn,
            'SessionTimeoutHours': vpn_endpoint_config.session_timeout_hours,
            'SplitTunnel': vpn_endpoint_config.split_tunnel,
            'TransportProtocol': vpn_endpoint_config.transport_protocol,
            'VpnPort': vpn_endpoint_config.vpn_port,
            'VpcId': troposphere.Ref(vpc_id_param),
            'SecurityGroupIds': troposphere.Ref(security_group_list_param),
            'ConnectionLogOptions': {
                'Enabled': True,
                'CloudwatchLogGroup': vpn_endpoint_log_group_name,
                'CloudwatchLogStream': vpn_endpoint_log_stream_name
            }
        }

        vpn_endpoint_res = troposphere.ec2.ClientVpnEndpoint.from_dict(
            'VPNClientEndpoint',
            vpn_endpoint_dict
        )
        vpn_endpoint_res.DependsOn = vpn_endpoint_log_stream_res
        self.template.add_resource( vpn_endpoint_res )

        # ClientVpnTargetNetworkAssociation
        cur_az = 0
        vpn_auth_rule_depends_list = []
        network_assoc_subnet_param = {}
        while cur_az < network_config.availability_zones:
            cur_az += 1
            # Isolate to a specific AZ if configured
            if vpn_endpoint_config.availability_zone != 'all' and vpn_endpoint_config.availability_zone != str(cur_az):
                continue
            network_assoc_subnet_param[cur_az] = self.create_cfn_parameter(
                name=f'NetworkAssociationSubnetAZ{cur_az}',
                param_type='AWS::EC2::Subnet::Id',
                description=f'Subnet Id for AZ{cur_az}',
                value=f'{network_config.paco_ref}.vpc.segments.{vpn_endpoint_config.segment}.az{cur_az}.subnet_id'
            )
            network_assoc_dict = {
                'ClientVpnEndpointId': troposphere.Ref(vpn_endpoint_res),
                'SubnetId': troposphere.Ref(network_assoc_subnet_param[cur_az])
            }
            network_assoc_res = troposphere.ec2.ClientVpnTargetNetworkAssociation.from_dict(
                f'ClientVpnTargetNetworkAssociationAZ{cur_az}',
                network_assoc_dict
            )
            network_assoc_res.DependsOn = vpn_endpoint_res
            self.template.add_resource(network_assoc_res)
            vpn_auth_rule_depends_list.append(network_assoc_res)

        # ClientVpnAuthorizationRule
        vpn_auth_rule_dict = {
            'ClientVpnEndpointId': troposphere.Ref(vpn_endpoint_res),
            'AuthorizeAllGroups': 'True',
            'TargetNetworkCidr': '0.0.0.0/0'
        }
        vpn_auth_rule_res = troposphere.ec2.ClientVpnAuthorizationRule.from_dict(
            'ClientVpnAuthorizationRule',
            vpn_auth_rule_dict
        )
        vpn_auth_rule_res.DependsOn = vpn_auth_rule_depends_list
        self.template.add_resource(vpn_auth_rule_res)

        # ClientVpnRoute
        cur_az = 0
        while cur_az < network_config.availability_zones:
            cur_az += 1
            # Isolate to a specific AZ if configured
            if vpn_endpoint_config.availability_zone != 'all' and vpn_endpoint_config.availability_zone != str(cur_az):
                continue
            vpn_route_dict = {
                'ClientVpnEndpointId': troposphere.Ref(vpn_endpoint_res),
                'DestinationCidrBlock': '0.0.0.0/0',
                'TargetVpcSubnetId': troposphere.Ref(network_assoc_subnet_param[cur_az])
            }
            vpn_route_res = troposphere.ec2.ClientVpnRoute.from_dict(
                f'ClientVpnRouteAZ{cur_az}',
                vpn_route_dict
            )
            vpn_route_res.DependsOn = vpn_auth_rule_res
            self.template.add_resource(vpn_route_res)

        return