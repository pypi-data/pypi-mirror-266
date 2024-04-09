from paco import utils
from paco.cftemplates.cftemplates import StackTemplate
from paco.models import schemas
import troposphere
import troposphere.guardduty




class GuardDuty(StackTemplate):

    def __init__(self, stack, paco_ctx):
        detector_config = stack.resource
        config_ref = detector_config.paco_ref_parts
        super().__init__(stack, paco_ctx)
        group_name = self.resource_group_name
        if group_name == None:
            group_name = 'detector'
        self.set_aws_name('GuardDuty', group_name, self.resource.name)

        template_fmt = """
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AWS GuardDuty'

Parameters:
    DetectorEnabled:
        Type: String
        Description: Boolean indicating whether the Detector is enabled or not

Resources:
{0[detector_yaml]:s}"""


        template_table = {
            'resources_yaml': ""
        }

        detector_fmt = """
    GuardDutyDetector:
        Type: AWS::GuardDuty::Detector
        Properties:
            Enable: !Ref DetectorEnabled
{0[data_sources_yaml]:s}"""

        data_sources_fmt = """
            DataSources:{0[malware_yaml]:s}
{0[s3_logs_yaml]:s}"""

        data_sources_malware_fmt = """
                MalwareProtection:
                    ScanEc2InstanceWithFindings:
                        EbsVolumes: {0[ebs_volumes_enabled]:s}"""

        data_sources_s3_logs_fmt = """
                S3Logs:
                    Enable: {0[s3_logs_enabled]:s}"""

        template_yaml = """
AWSTemplateFormatVersion: '2010-09-09'
Description: 'AWS GuardDuty'
"""

        self.set_parameter('DetectorEnabled', 'True' if detector_config.is_enabled() else 'False')

        detector_table = {
            'data_sources_yaml': ''
        }
        # Detector Enabled
        if detector_config.is_enabled():
            data_sources_config = detector_config.data_sources
            data_sources_table = {
                'malware_yaml': '',
                's3_logs': ''
            }
            # Malware Protection
            if data_sources_config.malware_protection != None:
                ebs_volumes_enabled = 'True' if data_sources_config.malware_protection.scan_ec2_instance_with_findings.ebs_volumes == True else 'False'
                malware_table = {'ebs_volumes_enabled': ebs_volumes_enabled}
                data_sources_table['malware_yaml'] = data_sources_malware_fmt.format(malware_table)
            # S3 Logs
            if data_sources_config.s3_logs != None:
                s3_logs_enabled = 'True' if data_sources_config.s3_logs.enabled == True else 'False'
                s3_logs_table = {'s3_logs_enabled': s3_logs_enabled}
                data_sources_table['s3_logs_yaml'] = data_sources_s3_logs_fmt.format(s3_logs_table)
            detector_table['data_sources_yaml'] = data_sources_fmt.format(data_sources_table)


        template_table['detector_yaml'] = detector_fmt.format(detector_table)
        template_yaml = template_fmt.format(template_table)

        self.set_template(template_yaml)

        # Troposphere Template Initialization
        # self.init_template('GuardDuty Detector')
        # detector_dict_config = {
        #     'Enable': detector_config.is_enabled()
        # }
        # data_sources_cfn = None
        # if detector_config.is_enabled():
        #     data_sources_config = detector_config.data_sources

        #     if data_sources_config.malware_protection != None:
        #         data_sources_dict['MalwareProtection'] = {
        #             'ScanEc2InstanceWithFindings': {
        #                 'EbsVolumes': data_sources_config.malware_protection.scan_ec2_instance_with_findings.ebs_volumes
        #             }
        #         }
        #     if data_sources_config.s3_logs != None:
        #         data_sources_dict['S3Logs'] = {
        #             'Enable': data_sources_config.s3_logs.enabled
        #         }
        #     if len(data_sources_dict.keys()) > 0:
        #         data_sources_cfn = troposphere.guardduty.CFNDataSourceConfigurations.from_dict(data_sources_dict)

        # template = self.template


        # Outputs
        # self.create_output(
        #     title='ElasticIPAddress',
        #     description="The Elastic IP Address.",
        #     value=eip_address_value,
        #     ref=config_ref + ".address",
        # )

