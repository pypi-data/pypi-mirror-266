from paco.cftemplates.cftemplates import StackTemplate
from paco.cftemplates.cftemplates import StackOutputParam
from paco.models.locations import get_parent_by_interface
from paco.models.references import get_model_obj_from_ref, is_ref
from paco.models.registry import SECURITY_GROUPS_HOOKS
from paco.models.schemas import IEnvironmentRegion
from paco import utils
import troposphere
import troposphere.elasticloadbalancingv2
import troposphere.wafv2

# Troposphere elasticloadbalancingv2 monkey patch
# troposphere 2.6.2 changed these props to ([basestring], False) - this change breaks use of the
# List<AWS::EC2::SecurityGroup::Id> Parameter for these two fields
troposphere.elasticloadbalancingv2.LoadBalancer.props['Subnets'] = (list, False)
troposphere.elasticloadbalancingv2.LoadBalancer.props['SecurityGroups'] = (list, False)

class LBBase(StackTemplate):
    def __init__(
        self,
        stack,
        paco_ctx,
        env_ctx,
        app_id,
    ):
        self.lb_config = stack.resource
        self.env_ctx = env_ctx
        self.app_id = app_id
        self.config_ref = self.lb_config.paco_ref_parts
        super().__init__(stack, paco_ctx)

    def init_lb(self, aws_name, template_title):
        self.set_aws_name(aws_name, self.resource_group_name, self.lb_config.name)
        self.network = self.lb_config.env_region_obj.network

        # Init Troposphere template
        self.init_template(template_title)
        if not self.lb_config.is_enabled():
            return self.set_template()

        # Parameters
        if self.lb_config.is_enabled():
            lb_enable = 'true'
        else:
            lb_enable = 'false'

        lb_is_enabled_param = self.create_cfn_parameter(
            param_type='String',
            name='LBEnabled',
            description='Enable the LB in this template',
            value=lb_enable
        )

        lb_is_cost_disabled_param = self.create_cfn_parameter(
            param_type='String',
            name='LBIsCostDisabled',
            description='Boolean indicating whether LB is disabled for cost savings.',
            value=self.lb_config.cost_disabled
        )

        vpc_stack = self.env_ctx.get_vpc_stack()
        vpc_param = self.create_cfn_parameter(
            param_type='String',
            name='VPC',
            description='VPC ID',
            value=StackOutputParam('VPC', vpc_stack, 'VPC', self)
        )
        lb_region = self.env_ctx.region
        if self.lb_config.type == 'LBApplication':
            lb_type = 'alb'
        else:
            lb_type = 'nlb'
        lb_hosted_zone_id_param = self.create_cfn_parameter(
            param_type='String',
            name='LBHostedZoneId',
            description='The Regonal AWS Route53 Hosted Zone ID',
            value=self.lb_hosted_zone_id(lb_type, lb_region)
        )

        # 32 Characters max
        # <proj>-<env>-<app>-<lb.name>
        # TODO: Limit each name item to 7 chars
        # Name collision risk:, if unique identifying characrtes are truncated
        #   - Add a hash?
        #   - Check for duplicates with validating template
        load_balancer_name = self.resource.get_aws_name(hash_long_names=True)
        load_balancer_name_param = self.create_cfn_parameter(
            param_type='String',
            name='LoadBalancerName',
            description='The name of the load balancer',
            value=load_balancer_name
        )
        scheme_param = self.create_cfn_parameter(
            param_type='String',
            min_length=1,
            max_length=128,
            name='Scheme',
            description='Specify internal to create an internal load balancer with a DNS name that resolves to private IP addresses or internet-facing to create a load balancer with a publicly resolvable DNS name, which resolves to public IP addresses.',
            value=self.lb_config.scheme
        )

        # Security Groups
        if self.lb_config.type == 'LBApplication':
            sg_group_list = []
            sg_group_list.extend(self.lb_config.security_groups)
            # Known to be used by the CloudFront Paco Service
            for hook in SECURITY_GROUPS_HOOKS:
                env_config = get_parent_by_interface(self.lb_config, IEnvironmentRegion)
                vpc_id = self.paco_ctx.get_ref(f'{env_config.network.vpc.paco_ref}.id').get_outputs_value('VPC')
                hook_sg_list = hook(self.lb_config, self.account_ctx, self.aws_region, vpc_id)
                sg_group_list.extend(hook_sg_list)

            security_group_list_param = self.create_cfn_ref_list_param(
                param_type='List<AWS::EC2::SecurityGroup::Id>',
                name='SecurityGroupList',
                description='A List of security groups to attach to the LB',
                value=sg_group_list,
                ref_attribute='id'
            )

        idle_timeout_param = self.create_cfn_parameter(
            param_type='String',
            name='IdleTimeoutSecs',
            description='The idle timeout value in seconds.',
            value=self.lb_config.idle_timeout_secs
        )

        # Conditions
        self.template.add_condition(
            "LBIsEnabled",
            troposphere.Equals(troposphere.Ref(lb_is_enabled_param), "true")
        )

        self.template.add_condition(
            "LBIsCostDisabled",
            troposphere.Equals(troposphere.Ref(lb_is_cost_disabled_param), "true")
        )

        self.template.add_condition(
            "LBResourceIsEnabled",
            troposphere.And(
                troposphere.Condition("LBIsEnabled"),
                troposphere.Not(troposphere.Condition("LBIsCostDisabled"))
            )
        )

        # Resources

        # LoadBalancer
        load_balancer_logical_id = 'LoadBalancer'
        cfn_export_dict = {}
        cfn_export_dict['Name'] = troposphere.Ref(load_balancer_name_param)
        if self.lb_config.type == 'LBApplication':
            lb_v2_type = 'application'
        else:
            lb_v2_type = 'network'
        cfn_export_dict['Type'] = lb_v2_type
        cfn_export_dict['Scheme'] = troposphere.Ref(scheme_param)
        if self.lb_config.type == 'LBApplication' or len(self.lb_config.static_ips) == 0:
            # Segment SubnetList is a Segment stack Output based on availability zones
            subnet_list_ref = self.network.vpc.segments[self.lb_config.segment].paco_ref + '.subnet_id_list'
            subnet_list_param = self.create_cfn_parameter(
                param_type='List<AWS::EC2::Subnet::Id>',
                name='SubnetList',
                description='A list of subnets where the LBs instances will be provisioned',
                value=subnet_list_ref,
            )
            cfn_export_dict['Subnets'] = troposphere.Ref(subnet_list_param)
        if self.lb_config.type == 'LBNetwork':
            # Add SubnetMapping for Static IP
            if len(self.lb_config.static_ips) > 0:
                cfn_export_dict['SubnetMappings'] = []
                for segment_az in range(0, len(self.lb_config.static_ips)):
                    static_ip_param = self.create_cfn_parameter(
                        param_type='String',
                        name=f'StaticEIPAZ{segment_az+1}AllocationId',
                        description='The EIP IP allocation Id to associate with this Subnet',
                        value=self.lb_config.static_ips[segment_az] + '.allocation_id'
                    )
                    static_ip_subnet_id_param = self.create_cfn_parameter(
                        param_type='String',
                        name=f'StaticEIPAZ{segment_az+1}SubnetId',
                        description='The Subnet Id to associate with this EIP',
                        value=self.network.vpc.segments[self.lb_config.segment].paco_ref + f'.az{segment_az+1}.subnet_id'
                    )
                    cfn_export_dict['SubnetMappings'].append(
                        {
                            'AllocationId': troposphere.Ref(static_ip_param),
                            'SubnetId': troposphere.Ref(static_ip_subnet_id_param)
                        }
                    )

        # Application Load Balancer Logic
        lb_attributes = []
        if self.lb_config.type == 'LBApplication':
            cfn_export_dict['SecurityGroups'] = troposphere.Ref(security_group_list_param)

            lb_attributes.append(
                {'Key': 'idle_timeout.timeout_seconds', 'Value': troposphere.Ref(idle_timeout_param)}
            )

        if self.lb_config.enable_access_logs:
            # ToDo: automatically create a bucket when access_logs_bucket is not set
            s3bucket = get_model_obj_from_ref(self.lb_config.access_logs_bucket, self.paco_ctx.project)
            lb_attributes.append(
                {'Key': 'access_logs.s3.enabled', 'Value': 'true'}
            )
            lb_attributes.append(
                {'Key': 'access_logs.s3.bucket', 'Value': s3bucket.get_bucket_name() }
            )
            if self.lb_config.access_logs_prefix:
                lb_attributes.append(
                    {'Key': 'access_logs.s3.prefix', 'Value': self.lb_config.access_logs_prefix}
                )
        if self.lb_config.cross_zone_balancing:
            lb_attributes.append(
                {'Key': 'load_balancing.cross_zone.enabled', 'Value': 'true'}
            )

        cfn_export_dict['LoadBalancerAttributes'] = lb_attributes

        lb_resource = troposphere.elasticloadbalancingv2.LoadBalancer.from_dict(
            load_balancer_logical_id,
            cfn_export_dict
        )
        lb_resource.Condition = "LBResourceIsEnabled"
        self.template.add_resource(lb_resource)

        # Target Groups
        for target_group_name, target_group in sorted(self.lb_config.target_groups.items()):
            if target_group.is_enabled() == False:
                continue
            target_group_id = self.create_cfn_logical_id(target_group_name)
            target_group_logical_id = 'TargetGroup' + target_group_id
            cfn_export_dict = {}
            if self.paco_ctx.legacy_flag('target_group_name_2019_10_29') == True:
                name = self.create_resource_name_join(
                    name_list=[load_balancer_name, target_group_id], separator='',
                    camel_case=True, hash_long_names=True,
                    filter_id='EC2.ElasticLoadBalancingV2.TargetGroup.Name',
                )
            else:
                name = troposphere.Ref('AWS::NoValue')
            cfn_export_dict['Name'] = name
            cfn_export_dict['HealthCheckIntervalSeconds'] = target_group.health_check_interval
            cfn_export_dict['HealthCheckTimeoutSeconds'] = target_group.health_check_timeout
            cfn_export_dict['HealthyThresholdCount'] = target_group.healthy_threshold
            cfn_export_dict['HealthCheckProtocol'] = target_group.health_check_protocol
            # HTTP Health Checks
            if target_group.health_check_protocol in ['HTTP', 'HTTPS']:
                cfn_export_dict['HealthCheckPath'] = target_group.health_check_path
                cfn_export_dict['Matcher'] = {'HttpCode': target_group.health_check_http_code }

            if target_group.health_check_port != 'traffic-port':
                cfn_export_dict['HealthCheckPort'] = target_group.health_check_port
            if target_group.port != None:
                cfn_export_dict['Port'] = target_group.port
            cfn_export_dict['Protocol'] = target_group.protocol
            cfn_export_dict['UnhealthyThresholdCount'] = target_group.unhealthy_threshold
            # Ignore if ALB Target type
            cfn_export_dict['VpcId'] = troposphere.Ref(vpc_param)
            if target_group.target_type != 'alb':
                cfn_export_dict['TargetGroupAttributes'] = [
                    {'Key': 'deregistration_delay.timeout_seconds', 'Value': str(target_group.connection_drain_timeout) }
                ]
            # TODO: Preserve Client IP
            # if self.lb_config.type == 'LBNetwork':
            #     cfn_export_dict['TargetGroupAttributes'].append({
            #         'Key': 'preserve_client_ip.enabled', 'Value': 'false'
            #     })

            cfn_export_dict['VpcId'] = troposphere.Ref(vpc_param)
            cfn_export_dict['Tags'] = [{
                'Key': 'Paco-TargetGroup-Name',
                'Value': target_group.name
            }]
            if target_group.target_type != 'instance':
                cfn_export_dict['TargetType'] = target_group.target_type
            if target_group.target_type == 'alb':
                cfn_export_dict['Targets'] = []
                for alb_target in target_group.targets:
                    target_param = self.create_cfn_parameter(
                        param_type='String',
                        # md5sum of the alb_target string
                        name='TargetGroupTarget' + utils.md5sum(str_data=f'{target_group.name}-{alb_target}'),
                        description='The Arn of the Target to associate with this Target Group',
                        value=alb_target + '.arn'
                    )
                    cfn_export_dict['Targets'].append(
                        {
                            'Id': troposphere.Ref(target_param),
                        }
                    )
            target_group_resource = troposphere.elasticloadbalancingv2.TargetGroup.from_dict(
                target_group_logical_id,
                cfn_export_dict
            )
            target_group_resource.Condition = 'LBIsEnabled'
            self.template.add_resource(target_group_resource)

            # Target Group Outputs
            target_group_ref = '.'.join([self.lb_config.paco_ref_parts, 'target_groups', target_group_name])
            target_group_arn_ref = '.'.join([target_group_ref, 'arn'])
            self.create_output(
                title='TargetGroupArn' + target_group_id,
                value=troposphere.Ref(target_group_resource),
                ref=target_group_arn_ref
            )

            target_group_name_ref = '.'.join([target_group_ref, 'name'])
            self.create_output(
                title='TargetGroupName' + target_group_id,
                value=troposphere.GetAtt(target_group_resource, 'TargetGroupName'),
                ref=target_group_name_ref
            )

            self.create_output(
                title='TargetGroupFullName' + target_group_id,
                value=troposphere.GetAtt(target_group_resource, 'TargetGroupFullName'),
                ref=target_group_ref + '.fullname'
            )

        # Listeners
        for listener_name, listener in self.lb_config.listeners.items():
            logical_listener_name = self.create_cfn_logical_id('Listener' + listener_name)
            cfn_export_dict = listener.cfn_export_dict

            # Listener - Default Actions
            da_redirect = None
            da_target_group = None
            if listener.default_action != None:
                default_action = listener.default_action
                if default_action.target_group != None and default_action.target_group != '':
                    da_target_group = default_action.target_group
                elif default_action.redirect != None:
                    da_redirect = default_action.redirect
                elif default_action.fixed_response != None:
                    fixed_response = default_action.fixed_response
                    action = {
                        'Type': 'fixed-response',
                        'FixedResponseConfig': {
                            'ContentType': fixed_response.content_type,
                            'MessageBody': fixed_response.message_body,
                            'StatusCode': fixed_response.status_code
                        }
                    }
            elif listener.redirect:
                da_redirect = listener.redirect
            elif listener.target_group != None and listener.target_group != '':
                da_target_group = listener.target_group

            if da_redirect != None:
                action = {
                    'Type': 'redirect',
                    'RedirectConfig': {
                        'Port': str(listener.redirect.port),
                        'Protocol': listener.redirect.protocol,
                        'StatusCode': 'HTTP_301'
                    }
                }
            elif da_target_group != None:
                target_group_id = self.create_cfn_logical_id(da_target_group)
                action = {
                    'Type': 'forward',
                    #'TargetGroupArn': troposphere.Ref('TargetGroup' + target_group_id)
                    # arn:aws:elasticloadbalancing:us-west-2:833840083808:targetgroup/NE-ko-Targe-EDHCT4CBFK96/cc15bf1049eeb530
                    'TargetGroupArn': troposphere.Sub('arn:aws:elasticloadbalancing:${AWS::Region}:${AWS::AccountId}:${TargetGroup'+target_group_id+'.TargetGroupFullName}')
                }
            cfn_export_dict['DefaultActions'] = [action]

            cfn_export_dict['LoadBalancerArn'] = troposphere.Ref(lb_resource)

            # Listener - SSL Certificates
            ssl_cert_param_obj_list = []
            unique_listener_cert_name = ""
            if len(listener.ssl_certificates) > 0 and self.lb_config.is_enabled():
                if listener.ssl_policy != '':
                    cfn_export_dict['SslPolicy'] = listener.ssl_policy
                cfn_export_dict['Certificates'] = []
                for ssl_cert_idx in range(0, len(listener.ssl_certificates)):
                    listener_cert = listener.ssl_certificates[ssl_cert_idx]
                    ssl_certificate_arn = listener_cert
                    if is_ref(ssl_certificate_arn):
                        ssl_certificate_arn = listener_cert + '.arn'
                    ssl_cert_param = self.create_cfn_parameter(
                        param_type='String',
                        name='SSLCertificateIdL%sC%d' % (listener_name, ssl_cert_idx),
                        description='The Arn of the SSL Certificate to associate with this Load Balancer',
                        value=ssl_certificate_arn
                    )
                    if ssl_cert_idx == 0:
                        cfn_export_dict['Certificates'] = [ {
                            'CertificateArn': troposphere.Ref(ssl_cert_param)
                        } ]
                    else:
                        unique_listener_cert_name = f'{unique_listener_cert_name}{listener.ssl_certificates[ssl_cert_idx]}'
                        ssl_cert_param_obj_list.append(
                            troposphere.elasticloadbalancingv2.Certificate(
                                CertificateArn=troposphere.Ref(ssl_cert_param)
                            )
                        )

            listener_resource = troposphere.elasticloadbalancingv2.Listener.from_dict(
                logical_listener_name,
                cfn_export_dict
            )
            listener_resource.Condition = 'LBResourceIsEnabled'
            self.template.add_resource(listener_resource)

            # ListenerCertificates
            if len(ssl_cert_param_obj_list) > 0:
                unique_listener_cert_name = utils.md5sum(str_data=unique_listener_cert_name)
                logical_listener_cert_name = self.create_cfn_logical_id_join([logical_listener_name, 'Certificate', unique_listener_cert_name])
                troposphere.elasticloadbalancingv2.ListenerCertificate(
                    title=logical_listener_cert_name,
                    template=self.template,
                    Certificates=ssl_cert_param_obj_list,
                    ListenerArn=troposphere.Ref(listener_resource),
                    Condition='LBResourceIsEnabled'
                )

            # Listener - Rules
            if listener.rules != None:
                for rule_name, rule in listener.rules.items():
                    if rule.enabled == False:
                      continue
                    logical_rule_name = self.create_cfn_logical_id(rule_name)
                    cfn_export_dict = {}
                    rule_conditions = []
                    if rule.rule_type == "forward":
                        ignore_changes=self.lb_config.ignore_listener_rule_target_group_changes
                        listener_rule_target_group_arn_param = self.create_cfn_parameter(
                            param_type='String',
                            name=f'ListenerRuleTargetGroupArn{logical_rule_name}',
                            description=f'Listener Rule Target Group ARN for {logical_rule_name}',
                            value='',
                            ignore_changes=ignore_changes
                        )
                        target_group_arn_condition_name = f'ListenerRuleTargetGroupArnIsEmpty{logical_rule_name}'
                        self.template.add_condition(
                            target_group_arn_condition_name,
                            troposphere.Equals(troposphere.Ref(listener_rule_target_group_arn_param), "")
                        )
                        logical_target_group_id = self.create_cfn_logical_id('TargetGroup' + rule.target_group)
                        cfn_export_dict['Actions'] = [
                            {
                                'Type': 'forward',
                                #'TargetGroupArn': troposphere.Ref(logical_target_group_id)
                                'TargetGroupArn': troposphere.If(
                                    target_group_arn_condition_name,
                                    troposphere.Sub('arn:aws:elasticloadbalancing:${AWS::Region}:${AWS::AccountId}:${'+logical_target_group_id+'.TargetGroupFullName}'),
                                    troposphere.Ref(listener_rule_target_group_arn_param))
                            }
                        ]
                        if len(rule.host) > 0:
                            rule_conditions.append({'Field': 'host-header', 'Values': rule.host})
                        if len(rule.path_pattern) > 0:
                            rule_conditions.append({'Field': 'path-pattern', 'Values': rule.path_pattern})
                    elif rule.rule_type == "redirect":
                        redirect_config = {'Type': 'redirect', 'RedirectConfig': {'Host': rule.redirect_host, 'StatusCode': 'HTTP_301'} }
                        if rule.redirect_path != None:
                            redirect_config['RedirectConfig']['Path'] = rule.redirect_path
                        cfn_export_dict['Actions'] = [
                            redirect_config
                        ]
                        rule_conditions.append({'Field': 'host-header', 'Values': rule.host})
                        if len(rule.path_pattern) > 0:
                            rule_conditions.append({'Field': 'path-pattern', 'Values': rule.path_pattern})

                    cfn_export_dict['Conditions'] = rule_conditions

                    cfn_export_dict['ListenerArn'] = troposphere.Ref(logical_listener_name)
                    cfn_export_dict['Priority'] = rule.priority
                    logical_listener_rule_name = self.create_cfn_logical_id_join(
                        str_list=[logical_listener_name, 'Rule', logical_rule_name]
                    )

                    listener_rule_resource = troposphere.elasticloadbalancingv2.ListenerRule.from_dict(
                        logical_listener_rule_name,
                        cfn_export_dict
                    )
                    listener_rule_resource.Condition = "LBResourceIsEnabled"
                    self.template.add_resource(listener_rule_resource)
                    self.create_output(
                        title='ListenerRuleArn' + logical_rule_name,
                        value=troposphere.Ref(listener_rule_resource),
                        ref=rule.paco_ref_parts+'.arn',
                        condition="LBResourceIsEnabled"
                    )
                    #print(f'{rule.paco_ref_parts}.arn')

            # WAF Web ACL
            if listener.webacl_id != None:
                webacl_id_value = listener.webacl_id
                if is_ref(webacl_id_value):
                    webacl_id_value = listener.webacl_id + '.arn'
                webacl_id_param = self.create_cfn_parameter(
                    param_type='String',
                    name=logical_listener_name+'WebAclId',
                    description='WAF Web Acl Arn',
                    value=webacl_id_value
                )

                web_acl_assoc_res = troposphere.wafv2.WebACLAssociation(
                    title=self.create_cfn_logical_id_join([logical_listener_name, 'WebACLAssociation']),
                    template=self.template,
                    ResourceArn=troposphere.Ref(lb_resource),
                    WebACLArn=troposphere.Ref(webacl_id_param)
                )
                web_acl_assoc_res.DependsOn = lb_resource

            # Listener Stack Outputs
            self.create_output(
                title=f'{logical_listener_name}Arn',
                value=troposphere.Ref(listener_resource),
                ref=listener.paco_ref_parts + '.arn',
                condition="LBResourceIsEnabled"
            )

        # Record Sets
        if self.paco_ctx.legacy_flag('route53_record_set_2019_10_16'):
            record_set_index = 0
            for lb_dns in self.lb_config.dns:
                if self.lb_config.is_dns_enabled() == True:
                    hosted_zone_param = self.create_cfn_parameter(
                        param_type='String',
                        description='LB DNS Hosted Zone ID',
                        name='HostedZoneID%d' % (record_set_index),
                        value=lb_dns.hosted_zone+'.id'
                    )
                    cfn_export_dict = {}
                    cfn_export_dict['HostedZoneId'] = troposphere.Ref(hosted_zone_param)
                    cfn_export_dict['Name'] = lb_dns.domain_name
                    cfn_export_dict['Type'] = 'A'
                    cfn_export_dict['AliasTarget'] = {
                        'DNSName': troposphere.GetAtt(lb_resource, 'DNSName'),
                        'HostedZoneId': troposphere.GetAtt(lb_resource, 'CanonicalHostedZoneID')
                    }
                    record_set_resource = troposphere.route53.RecordSet.from_dict(
                        'RecordSet' + str(record_set_index),
                        cfn_export_dict
                    )
                    record_set_resource.Condition = "LBResourceIsEnabled"
                    self.template.add_resource(record_set_resource)
                    record_set_index += 1

        if self.enabled == True:
            self.create_output(
                title='LoadBalancerArn',
                value=troposphere.Ref(lb_resource),
                ref=self.lb_config.paco_ref_parts + '.arn',
                condition="LBResourceIsEnabled"
            )
            self.create_output(
                title='LoadBalancerName',
                value=troposphere.GetAtt(lb_resource, 'LoadBalancerName'),
                ref=self.lb_config.paco_ref_parts + '.name',
                condition="LBResourceIsEnabled"
            )
            self.create_output(
                title='LoadBalancerFullName',
                value=troposphere.GetAtt(lb_resource, 'LoadBalancerFullName'),
                ref=self.lb_config.paco_ref_parts + '.fullname',
                condition="LBResourceIsEnabled"
            )
            self.create_output(
                title='LoadBalancerCanonicalHostedZoneID',
                value=troposphere.GetAtt(lb_resource, 'CanonicalHostedZoneID'),
                ref=self.lb_config.paco_ref_parts + '.canonicalhostedzoneid',
                condition="LBResourceIsEnabled"
            )
            self.create_output(
                title='LoadBalancerDNSName',
                value=troposphere.GetAtt(lb_resource, 'DNSName'),
                ref=self.lb_config.paco_ref_parts + '.dnsname',
                condition="LBResourceIsEnabled"
            )

            if self.paco_ctx.legacy_flag('route53_record_set_2019_10_16') == False:
                route53_ctl = self.paco_ctx.get_controller('route53')
                for lb_dns in self.lb_config.dns:
                    if self.lb_config.is_dns_enabled() == True and self.lb_config.cost_disabled == False:
                        alias_dns_ref = self.lb_config.paco_ref + '.dnsname'
                        alias_hosted_zone_ref = self.lb_config.paco_ref + '.canonicalhostedzoneid'
                        hosted_zone = get_model_obj_from_ref(lb_dns.hosted_zone, self.paco_ctx.project)
                        account_ctx = self.paco_ctx.get_account_context(account_ref=hosted_zone.account)
                        route53_ctl.add_record_set(
                            account_ctx,
                            self.aws_region,
                            self.lb_config,
                            enabled=self.lb_config.is_enabled(),
                            dns=lb_dns,
                            record_set_type='Alias',
                            alias_dns_name=alias_dns_ref,
                            alias_hosted_zone_id=alias_hosted_zone_ref,
                            stack_group=self.stack.stack_group,
                            async_stack_provision=True,
                            config_ref=self.lb_config.paco_ref_parts + '.dns'
                        )


class ALB(LBBase):

    def __init__(self, stack, paco_ctx, env_ctx, app_id):
        super().__init__(stack, paco_ctx, env_ctx, app_id)
        self.init_lb('ALB', 'Application Load Balancer')

class NLB(LBBase):

    def __init__(self, stack, paco_ctx, env_ctx, app_id):
        super().__init__(stack, paco_ctx, env_ctx, app_id)
        self.init_lb('NLB', 'Network Load Balancer')
