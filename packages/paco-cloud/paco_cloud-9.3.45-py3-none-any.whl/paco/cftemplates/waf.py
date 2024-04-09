from paco.cftemplates.cftemplates import StackTemplate
from paco.utils import prefixed_name
import troposphere
import troposphere.wafv2
from troposphere import AWSProperty

integer = int

class CustomResponse(AWSProperty):
    props = {
        'ResponseCode': (integer, True)
    }

class BlockAction(AWSProperty):
    props = {
        'CustomResponse': (CustomResponse, True)
    }

troposphere.wafv2.RuleAction.props['Block'] = (BlockAction, False)


class WAFWebACL(StackTemplate):
    def __init__(self, stack, paco_ctx):
        super().__init__(stack, paco_ctx)
        self.set_aws_name('WAFWebACL', self.resource_group_name, self.resource.name)

        # Troposphere Template Initialization
        self.init_template('WAFWebACL')
        if not self.resource.is_enabled():
            return

        webacl_config = stack.resource
        webacl_name = self.create_resource_name(
            webacl_config.paco_ref_parts,
            filter_id='WAFWebACL.RuleName', hash_long_names=True)
        webacl_dict = {
            'Name': webacl_name,
            'DefaultAction': {
                'Allow': {}
            },
            'Rules': [],
            'Scope': webacl_config.scope,
            'VisibilityConfig': {
                'CloudWatchMetricsEnabled': webacl_config.visibility_config.cloudwatch_metrics_enabled,
                'MetricName': webacl_config.visibility_config.metric_name,
                'SampledRequestsEnabled': webacl_config.visibility_config.sample_requests_enabled

            }
        }

        if webacl_config.rules != None:
            priority_index = 10
            for rule_name in webacl_config.rules.keys():
                rule_config = webacl_config.rules[rule_name]
                if rule_config.enabled == False:
                    continue
                if rule_config.statement == None:
                    continue
                rule_resoure_name = self.create_resource_name(
                    f'{webacl_config.paco_ref_parts}.{rule_name}',
                    filter_id='WAFWebACL.RuleName', hash_long_names=True)
                rule_config_dict = {
                    'Name': rule_resoure_name,
                    'Priority': priority_index,
                    'VisibilityConfig': {
                        'CloudWatchMetricsEnabled': rule_config.visibility_config.cloudwatch_metrics_enabled,
                        'MetricName': rule_config.visibility_config.metric_name,
                        'SampledRequestsEnabled': rule_config.visibility_config.sample_requests_enabled
                    },
                    'Statement': {}
                }
                if rule_config.action != None:
                    rule_config_dict['Action'] = {
                        'Block': {
                            'CustomResponse': {
                                'ResponseCode': rule_config.action.block.custom_response.response_code
                            }
                        }
                    }
                else:
                    rule_config_dict['OverrideAction'] = {}
                    if rule_config.override_action and rule_config.override_action.count == True:
                        rule_config_dict['OverrideAction']['Count'] = {}
                    else:
                        rule_config_dict['OverrideAction']['None'] = {}

                priority_index += 10

                # Managed Rules
                if rule_config.statement.managed_rule_group:
                    statement_config = rule_config.statement.managed_rule_group
                    rule_statement_dict = {
                        'Name': statement_config.rule_name,
                        'VendorName': statement_config.vendor
                    }
                    if len(statement_config.excluded_rules) > 0:
                        rule_statement_dict['ExcludedRules'] = []
                        for excluded_rule_name in rule_config.statement.managed_rule_group.excluded_rules:
                            excluded_rule = {
                                'Name': excluded_rule_name
                            }
                            rule_statement_dict['ExcludedRules'].append(excluded_rule)
                    if len(statement_config.rule_action_overrides) > 0:
                        rule_statement_dict['RuleActionOverrides'] = []
                        for override_rule in statement_config.rule_action_overrides:
                            rule_action_override = {
                                'Name': override_rule.rule_name
                            }
                            if override_rule.action_to_use.block != None:
                                rule_action_override['ActionToUse'] = {
                                    'Block': {
                                        'CustomResponse': {
                                            'ResponseCode': override_rule.action.block.custom_response.response_code
                                        }
                                    }
                                }
                            else:
                                rule_action_override['ActionToUse'] = {
                                    'Count': {}
                                }
                            rule_statement_dict['RuleActionOverrides'].append(rule_action_override)
                    rule_statement_res = troposphere.wafv2.ManagedRuleGroupStatement.from_dict(
                        'ManagedRuleGroupStatement',
                        rule_statement_dict
                    )
                    rule_config_dict['Statement'] = troposphere.wafv2.Statement(
                        ManagedRuleGroupStatement=rule_statement_res
                    )

                rule_config_dict['VisibilityConfig']['CloudWatchMetricsEnabled'] = rule_config.visibility_config.cloudwatch_metrics_enabled
                rule_config_dict['VisibilityConfig']['MetricName'] = rule_config.visibility_config.metric_name
                rule_config_dict['VisibilityConfig']['SampledRequestsEnabled'] = rule_config.visibility_config.sample_requests_enabled
                webacl_dict['Rules'].append(rule_config_dict)


        webacl_res = troposphere.wafv2.WebACL.from_dict(
            'WAFWebACL',
            webacl_dict
        )

        self.template.add_resource( webacl_res )

        # Logging
        if webacl_config.logging != None and webacl_config.logging.is_enabled():
            # WebACL LogGroup names must start with 'aws-waf-logs-'
            loggroup_name = f'aws-waf-logs-{prefixed_name(webacl_config, "WAFWebACL")}'
            # Create a loggroup using troposphere for the WebACL
            loggroup_res = troposphere.logs.LogGroup(
                'WAFWebACLLogGroup',
                LogGroupName=loggroup_name,
                RetentionInDays=webacl_config.logging.log_retention_days
            )
            self.template.add_resource( loggroup_res )

            # WebACL Troposphere Logging Configuration
            logging_dict = {
                'LogDestinationConfigs': [
                    troposphere.GetAtt(loggroup_res, 'Arn')
                ],
                'ResourceArn': troposphere.GetAtt(webacl_res, 'Arn'),
            }
            logging_res = troposphere.wafv2.LoggingConfiguration.from_dict(
                'WAFWebACLLogging',
                logging_dict,
            )
            self.template.add_resource( logging_res )
            logging_res.DependsOn = [webacl_res, loggroup_res]

        # Outputs
        self.create_output(
            title='WebACLId',
            description="WebACL Id.",
            value=troposphere.GetAtt(webacl_res, 'Id'),
            ref=self.resource.paco_ref_parts + ".id"
        )
        self.create_output(
            title='WebACLArn',
            description="WebACL Arn.",
            value=troposphere.GetAtt(webacl_res, 'Arn'),
            ref=self.resource.paco_ref_parts + ".arn"
        )
