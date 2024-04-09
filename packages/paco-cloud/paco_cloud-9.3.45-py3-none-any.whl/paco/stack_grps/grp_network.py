from paco import utils
from paco.core.exception import InvalidAWSConfiguration
from paco.core.yaml import YAML
from paco.models import schemas, iam
from paco.models.locations import get_parent_by_interface
from paco.models.references import Reference
from paco.stack import StackOrder, Stack, StackGroup, StackTags, StackHooks
from pprint import pprint
import paco.cftemplates
import paco.models.networks
import paco.models.loader
import time
import zope

yaml=YAML()
yaml.default_flow_sytle = False

class NetworkStackGroup(StackGroup):
    """StackGroup to manage all the stacks for a Network: VPC, NAT Gateway, VPC Peering, Security Groups, Segments"""
    def __init__(self, paco_ctx, account_ctx, env_ctx, stack_tags):
        super().__init__(
            paco_ctx,
            account_ctx,
            env_ctx.netenv.name,
            "Net",
            env_ctx
        )
        self.env_ctx = env_ctx
        self.region = self.env_ctx.region
        self.stack_tags = stack_tags

    def init(self):
        # Network Stack Templates
        # VPC Stack
        vpc_config = self.env_ctx.env_region.network.vpc
        if vpc_config == None or vpc_config.is_enabled() == False:
            # NetworkEnvironment with no network - serverless
            return
        network_config = get_parent_by_interface(vpc_config, schemas.INetwork)
        vpc_config.resolve_ref_obj = self
        vpc_config.private_hosted_zone.resolve_ref_obj = self

        stack_hooks = StackHooks()
        # Stack hooks for saving state to the Paco bucket
        stack_hooks.add(
            name='VPC.Cleanup',
            stack_action=['delete'],
            stack_timing='pre',
            hook_method=self.stack_hook_vpc_cleanup,
        )

        self.vpc_stack = self.add_new_stack(
            self.region,
            vpc_config,
            paco.cftemplates.VPC,
            stack_tags=StackTags(self.stack_tags),
            stack_hooks=stack_hooks
        )

        # Segments
        self.segment_list = []
        self.segment_dict = {}
        segments = network_config.vpc.segments
        for segment in segments.values():
            segment.resolve_ref_obj = self
            segment_stack = self.add_new_stack(
                self.region,
                segment,
                paco.cftemplates.Segment,
                stack_tags=StackTags(self.stack_tags),
                stack_orders=[StackOrder.PROVISION],
                extra_context={'env_ctx': self.env_ctx},
            )
            self.segment_dict[segment.name] = segment_stack
            self.segment_list.append(segment_stack)

        # Security Groups
        sg_config = network_config.vpc.security_groups
        self.sg_list = []
        self.sg_dict = {}
        # EC2 NATGateway Security Groups
        # Creates a security group for each Availability Zone in the segment
        sg_nat_id = 'bastion_nat_' + utils.md5sum(str_data='gateway')[:8]
        for nat_config in vpc_config.nat_gateway.values():
            if nat_config.is_enabled() == False:
                continue
            if nat_config.type == 'EC2':
                sg_nat_config_dict = {}
                if sg_nat_id not in sg_config.keys():
                    sg_config[sg_nat_id] = paco.models.networks.SecurityGroups(sg_nat_id, sg_config)
                for az_idx in range(1, network_config.availability_zones + 1):
                    sg_nat_config_dict['enabled'] = True
                    sg_nat_config_dict['ingress'] = []
                    for route_segment in nat_config.default_route_segments:
                        route_segment_id = route_segment.split('.')[-1]
                        az_cidr = getattr(vpc_config.segments[route_segment_id], f"az{az_idx}_cidr")
                        sg_nat_config_dict['ingress'].append(
                            {
                                'name': 'SubnetAZ',
                                'cidr_ip': az_cidr,
                                'protocol': '-1'
                            }
                        )
                    sg_nat_config_dict['egress'] = [
                        {
                            'name': 'ANY',
                            'cidr_ip': '0.0.0.0/0',
                            'protocol': '-1'
                        }
                    ]
                    sg_nat_rule_id = nat_config.name + '_az' + str(az_idx)
                    sg_config[sg_nat_id][sg_nat_rule_id] = paco.models.networks.SecurityGroup(sg_nat_rule_id, vpc_config)
                    paco.models.loader.apply_attributes_from_config(
                        sg_config[sg_nat_id][sg_nat_rule_id],
                        sg_nat_config_dict
                    )

        # Declared Security Groups
        for sg_id in sg_config:
            # Set resolve_ref_obj
            for sg_obj_id in sg_config[sg_id]:
                sg_config[sg_id][sg_obj_id].resolve_ref_obj = self
            sg_stack = self.add_new_stack(
                self.region,
                sg_config[sg_id],
                paco.cftemplates.SecurityGroups,
                stack_tags=StackTags(self.stack_tags),
                extra_context={'env_ctx': self.env_ctx, 'template_type': 'Groups'},
                # stack_orders=[StackOrder.PROVISION, StackOrder.WAITLAST]
            )
            self.sg_list.append(sg_stack)
            self.sg_dict[sg_id] = sg_stack

        # Ingress/Egress Stacks
        for sg_id in sg_config:
            self.add_new_stack(
                self.region,
                sg_config[sg_id],
                paco.cftemplates.SecurityGroups,
                stack_tags=StackTags(self.stack_tags),
                extra_context={'env_ctx': self.env_ctx, 'template_type': 'Rules'}
            )

        # Wait for Segment Stacks
        for segment_stack in self.segment_list:
            self.add_stack_order(segment_stack, [StackOrder.WAIT])

        # VPC Peering Stack
        if vpc_config.peering != None:
            peering_config = self.env_ctx.env_region.network.vpc.peering
            for peer_id in peering_config.keys():
                peer_config = peering_config[peer_id]
                peer_config.resolve_ref_obj = self
                # Add role to the accepter network account
                if peer_config.network_environment != None and peer_config.peer_type == 'requester':
                    accepter_netenv_ref = Reference(peer_config.network_environment)
                    accepter_account_ref = self.paco_ctx.get_ref(f'{peer_config.network_environment}.network.aws_account')
                    accepter_account_ctx = self.paco_ctx.get_account_context(accepter_account_ref)
                    accepter_vpc_id = self.paco_ctx.get_ref(f'{peer_config.network_environment}.network.vpc.id')
                    # Only create the role if we are cross account or cross region
                    if self.account_ctx.id != accepter_account_ctx.id or self.env_ctx.env_region.name != accepter_netenv_ref.region:
                        if peer_config.peer_role_name == None:
                            self.gen_vpc_peering_accepter_role(
                                peer_config,
                                vpc_config,
                                accepter_vpc_id,
                                accepter_account_ctx,
                                accepter_netenv_ref.region,
                                self.account_ctx
                            )

            peering_stack_hooks = StackHooks()
            peering_stack_hooks.add(
                name='VPCPeering.Cleanup',
                stack_action=['delete'],
                stack_timing='pre',
                hook_method=self.stack_hook_vpc_peering_cleanup,
                hook_arg=peering_config
            )
            peering_stack_hooks.add(
                name='VPCPeering.Post',
                stack_action=['create', 'update'],
                stack_timing='post',
                hook_method=self.stack_hook_vpc_peering_post,
                cache_method=self.stack_hook_vpc_peering_post_cache_id,
                hook_arg=peering_config
            )
            self.peering_stack = self.add_new_stack(
                self.region,
                vpc_config.peering,
                paco.cftemplates.VPCPeering,
                stack_tags=StackTags(self.stack_tags),
                stack_hooks=peering_stack_hooks

            )

        # VPC EIPs
        for eip_config in vpc_config.eip.values():
            eip_stack = self.add_new_stack(
                self.region,
                eip_config,
                paco.cftemplates.EIP,
                stack_tags=StackTags(self.stack_tags)
            )

        # NAT Gateway
        self.nat_list = []
        for nat_config in vpc_config.nat_gateway.values():
            if sg_nat_id in sg_config.keys():
                nat_sg_config = sg_config[sg_nat_id]
            else:
                nat_sg_config = None
            # We now disable the NAT Gateway in the template so that we can delete it and recreate it when disabled.
            nat_stack = self.add_new_stack(
                self.region,
                nat_config,
                paco.cftemplates.NATGateway,
                stack_tags=StackTags(self.stack_tags),
                stack_orders=[StackOrder.PROVISION],
                extra_context={'nat_sg_config': nat_sg_config},
            )
            self.nat_list.append(nat_stack)

        for nat_stack in self.nat_list:
            self.add_stack_order(nat_stack, [StackOrder.WAIT])

        # VPC Endpoints
        vpc_endpoints_stack = self.add_new_stack(
            self.region,
            vpc_config,
            paco.cftemplates.VPCEndpoints,
            stack_tags=StackTags(self.stack_tags),
            stack_orders=[StackOrder.PROVISION]
        )
        self.add_stack_order(vpc_endpoints_stack, [StackOrder.WAIT])

        # VPN Client Endpoint
        if vpc_config.vpn_client_endpoint != None:
            vpn_client_endpoint_stack = self.add_new_stack(
                self.region,
                vpc_config.vpn_client_endpoint,
                paco.cftemplates.VPNClientEndpoint,
                stack_tags=StackTags(self.stack_tags)
            )

    # Stack Hooks
    def vpc_peering_disassociate_hosted_zone(self, requester_route53_client, requester_vpc_config, hosted_zone_id, requester_vpc_id):
        wait_for_disassociation = True
        while wait_for_disassociation:
            try:
                response = requester_route53_client.disassociate_vpc_from_hosted_zone(
                    HostedZoneId=hosted_zone_id,
                    VPC=requester_vpc_config
                )
            except Exception as e:
                if e.response['Error']['Code'] == 'VPCAssociationNotFound':
                    print(f"Success: HostedZone ({hosted_zone_id}) disassociated VPC ({requester_vpc_id})")
                    break
                else:
                    raise InvalidAWSConfiguration(f"Unable to create associate HostedZone ({hosted_zone_id}) with VPC ({requester_vpc_id}): {e.response['Error']['Code']}")

            if response['ChangeInfo']['Status'] == 'INSYNC':
                wait_for_disassociation = False
                print(f"Success: HostedZone ({hosted_zone_id}) disassociated VPC ({requester_vpc_id})")
            else:
                print(f"Waiting: HostedZone ({hosted_zone_id}) is disassociating VPC ({requester_vpc_id})")
                time.sleep(1)

    def stack_hook_vpc_peering_cleanup(self, hook, peering_config):
        # Disassociate VPCs
        for peer_id in peering_config.keys():
            peer_config = peering_config[peer_id]
            if peer_config.peer_type == 'requester':
                continue
            # Create VPC Association Authoriziation
            if peer_config.associate_private_hosted_zone == None:
                continue

            requester_account_ref = self.paco_ctx.get_ref(f'{peer_config.network_environment}.network.aws_account')
            requester_account_ctx = self.paco_ctx.get_account_context(requester_account_ref)
            requester_route53_client = requester_account_ctx.get_aws_client('route53')
            accepter_route53_client = self.account_ctx.get_aws_client('route53')

            hosted_zone_id_ref = Reference(self.env_ctx.env_region.network.vpc.paco_ref+'.private_hosted_zone.id')
            hosted_zone_id = hosted_zone_id_ref.resolve(self.paco_ctx.project, resolve_from_outputs=True)
            requester_vpc_id = self.paco_ctx.get_ref(f'{peer_config.network_environment}.network.vpc.id')
            requester_vpc_config = {
                'VPCRegion': self.region,
                'VPCId': requester_vpc_id
            }
            # Disassociate VPC from HostedZone
            self.vpc_peering_disassociate_hosted_zone(requester_route53_client, requester_vpc_config, hosted_zone_id, requester_vpc_id)



    def stack_hook_vpc_peering_post_cache_id(self, hook, peering_config):
        cache_list = []
        for peer_id in peering_config.keys():
            peer_config = peering_config[peer_id]
            cache_list.append(peer_config.obj_hash())
        return '-'.join(cache_list)


    def stack_hook_vpc_peering_post(self, hook, peering_config):
        # Create HostedZone VPC assocations
        for peer_id in peering_config.keys():
            peer_config = peering_config[peer_id]
            if peer_config.peer_type == 'requester':
                continue
            # Create VPC Association Authoriziation
            if peer_config.associate_private_hosted_zone == None:
                continue

            requester_account_ref = self.paco_ctx.get_ref(f'{peer_config.network_environment}.network.aws_account')
            requester_account_ctx = self.paco_ctx.get_account_context(requester_account_ref)
            requester_route53_client = requester_account_ctx.get_aws_client('route53')
            accepter_route53_client = self.account_ctx.get_aws_client('route53')

            hosted_zone_id_ref = Reference(self.env_ctx.env_region.network.vpc.paco_ref+'.private_hosted_zone.id')
            hosted_zone_id = hosted_zone_id_ref.resolve(self.paco_ctx.project, resolve_from_outputs=True)
            requester_vpc_id = self.paco_ctx.get_ref(f'{peer_config.network_environment}.network.vpc.id')
            requester_vpc_config = {
                'VPCRegion': self.region,
                'VPCId': requester_vpc_id
            }
            if peer_config.associate_private_hosted_zone == 'associate':
                accepter_route53_client.create_vpc_association_authorization(
                    HostedZoneId=hosted_zone_id,
                    VPC=requester_vpc_config
                )
                wait_for_association = True
                while wait_for_association:
                    try:
                        response = requester_route53_client.associate_vpc_with_hosted_zone(
                            HostedZoneId=hosted_zone_id,
                            VPC=requester_vpc_config
                        )
                    except Exception as e:
                        if e.response['Error']['Code'] == 'ConflictingDomainExists':
                            print(f"Success: HostedZone ({hosted_zone_id}) associated with VPC ({requester_vpc_id})")
                            break
                        else:
                            raise InvalidAWSConfiguration(f"Unable to create associate HostedZone ({hosted_zone_id}) with VPC ({requester_vpc_id}): {e.response['Error']['Code']}")

                    if response['ChangeInfo']['Status'] == 'INSYNC':
                        wait_for_association = False
                        print(f"Success: HostedZone ({hosted_zone_id}) associated with VPC ({requester_vpc_id})")
                    else:
                        print(f"Waiting: HostedZone ({hosted_zone_id}) is associating with VPC ({requester_vpc_id})")
                        time.sleep(1)
                # Delete the authorzation as suggested by AWS best practices
                accepter_route53_client.delete_vpc_association_authorization(
                    HostedZoneId=hosted_zone_id,
                    VPC=requester_vpc_config
                )
            elif peer_config.associate_private_hosted_zone == 'disassociate':
                # Disassociate VPC from HostedZone
                self.vpc_peering_disassociate_hosted_zone(requester_route53_client, requester_vpc_config, hosted_zone_id, requester_vpc_id)


    def stack_hook_vpc_cleanup(self, hook, config):

        if self.vpc_stack.template.resource.private_hosted_zone.enabled == False:
            return
        # Clean up the Private Hosted Zone
        ref = Reference(self.vpc_stack.template.resource.paco_ref+'.private_hosted_zone.id')
        route53_client = self.account_ctx.get_aws_client('route53', self.region)
        hosted_zone_id = ref.resolve(self.paco_ctx.project, resolve_from_outputs=True)
        try:
            response = route53_client.get_hosted_zone(
                Id=hosted_zone_id
            )
        except Exception as e:
            if hasattr(e, 'response') == False or e.response['Error']['Code'] != 'NoSuchHostedZone':
                raise e
            else:
                return
        hosted_zone_name = response['HostedZone']['Name']
        response = route53_client.list_resource_record_sets(
            HostedZoneId=hosted_zone_id
        )
        if len(response['ResourceRecordSets']) == 0:
            return

        change_list = []
        for record_set in response['ResourceRecordSets']:
            if record_set['Type'] in ('SOA'):
                continue
            if record_set['Type'] == 'NS' and record_set['Name'] == hosted_zone_name:
                continue

            change_list.append({
                'Action': 'DELETE',
                'ResourceRecordSet': {
                    'Name': record_set['Name'],
                    'ResourceRecords': record_set['ResourceRecords'],
                    'TTL': record_set['TTL'],
                    'Type': record_set['Type'],
                },
            })

        if len(change_list) > 0:
            response = route53_client.change_resource_record_sets(
                ChangeBatch={
                    'Changes':  change_list,
                    'Comment': 'Delete VPC Private Hosted Zone',
                },
                HostedZoneId=hosted_zone_id,
            )

    def get_vpc_stack(self):
        return self.vpc_stack

    def get_security_group_stack(self, sg_id):
        return self.sg_dict[sg_id]

    def get_segment_stack(self, segment_id):
        return self.segment_dict[segment_id]

    def gen_vpc_peering_accepter_role(self, peer_config, vpc_config, accepter_vpc_id, accepter_account_ctx, acceptor_region, requester_account_ctx):
        iam_ctl = self.paco_ctx.get_controller('IAM')
        netenv_ref = Reference(peer_config.network_environment + '.network')
        requester_region = netenv_ref.region
        accepter_region = self.region
        accepter_account_id = self.account_ctx.id

        role_yaml = f"""
assume_role_policy:
  effect: Allow
  aws:
    - '{requester_account_ctx.id}'
instance_profile: false
path: /
policies:
  - name: VPCPeeringAcceptor
    statement:
      - effect: Allow
        action:
          - ec2:AcceptVpcPeeringConnection
        resource:
          - '*'
"""
        #         condition:
        #         ArnEquals:
        #             ec2:RequesterVpc: 'arn:aws:ec2:{requester_region}:{requester_account_id}:vpc/{requester_vpc_id}'

        # condition:
        #   StringEquals:
        #     'ec2:AccepterVpc': 'arn:aws:ec2:{accepter_region}:{accepter_account_id}:vpc/{accepter_vpc_id}'


        role_config_dict = yaml.load(role_yaml)
        # role_config_dict['policies'][0]['statement'][1]['condition'] = {
        #     'StringEquals': {
        #          'ec2:AccepterVpc': { "Fn::Sub" : [ f'arn:aws:ec2:{accepter_region}:{accepter_account_id}:vpc/${{VpcId}}', { "VpcId": {"Ref" : "VpcId"} } ] }
        #     }
        # }
        role_config = iam.Role(f'Peering-{peer_config.name}-accepter-role', peer_config)
        role_config.apply_config(role_config_dict)
        role_config.enabled = True
        role_config.role_name = 'Peer-Accepter'

        #role_config.policies[0].statement[0].resource = [f"!Sub 'arn:aws:ec2:{accepter_region}:{accepter_account_id}:vpc/${{VpcId}}'"]

        # IAM Roles Parameters
        # iam_role_params = [{
        #     'key': 'VpcId',
        #     'value': vpc_config.paco_ref+'.id',
        #     'type': 'String',
        #     'description': 'Acceptor VPC ID'
        # }]
        iam_ctl.add_role(
            account_ctx=accepter_account_ctx,
            region=acceptor_region,
            resource=vpc_config,
            role=role_config,
            iam_role_id=f'VPC-Peer-{peer_config.name}-Accepter',
            stack_group=self,
            stack_tags=self.stack_tags,
            # template_params=iam_role_params
        )
        peer_config.peer_role_name = iam_ctl.role_name(role_config.paco_ref_parts)

    def resolve_ref(self, ref):
        if ref.raw.endswith('network.vpc.id'):
            return self.vpc_stack
        if schemas.IPrivateHostedZone.providedBy(ref.resource):
            return self.vpc_stack
        if ref.raw.find('network.vpc.segments') != -1:
            segment_id = ref.next_part('network.vpc.segments')
            return self.get_segment_stack(segment_id)
        if schemas.ISecurityGroup.providedBy(ref.resource):
            if ref.resource_ref == 'id':
                sg_id = ref.parts[-3]
                return self.get_security_group_stack(sg_id)
