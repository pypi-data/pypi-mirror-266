"""
EC2 Launch Manager supports applications by creating a launch bundle that
is a zip file of configuration and scripts to initialize them,
storing the launch bundle in S3 and ensuring that the configuration is
applied in the user_data when instances launch.

For example, if an ASG of instances has monitoring configuration,
the CloudWatch Agent will be installed and configured to collect
the metrics needed to support that monitoring.

EC2 Launch Mangaer is currently linux-centric and does not yet work with Windows instances.
"""


import base64
import paco.cftemplates
import json
import os
import pathlib
import shutil
import tarfile
from paco.stack import StackHooks, Stack, StackTags
from paco import models
from paco import utils
from paco.application import ec2lm_commands, ec2lm_scripts
from paco.models import schemas
from paco.models.locations import get_parent_by_interface
from paco.models.references import Reference, is_ref, resolve_ref, get_model_obj_from_ref
from paco.models.base import Named
from paco.models.resources import SSMDocument
from paco.utils import md5sum, prefixed_name
from paco.core.exception import StackException
from paco.core.exception import PacoErrorCode
from paco.application.reseng_deploymentpipeline import RELEASE_PHASE_SCRIPT, RELEASE_PHASE_SCRIPT_SSM_DOCUMENT_CONTENT, \
        ECR_DEPLOY_SCRIPT_HEAD, ECR_DEPLOY_SCRIPT_BODY, ECR_DEPLOY_SCRIPT_CONFIG
from paco.cftemplates.ecs import ECS_SCRIPT_HEAD, ECS_SCRIPT_BODY, ECS_SCRIPT_CONFIG

class LaunchBundle():
    """
    A zip file sent to an S3 Bucket to support initializing a new EC2 instance.
    """

    def __init__(self, resource, manager, name):
        self.name = name
        self.manager = manager
        self.resource = resource
        self.build_path = os.path.join(
            self.manager.build_path,
            self.resource.group_name,
            self.resource.name,
        )
        self.bundle_files = []
        self.cache_id = ""
        self.bucket_ref = resource.paco_ref_parts + '.ec2lm'
        self.bundles_path = os.path.join(self.build_path, 'LaunchBundles')
        self.bundle_folder = self.name
        self.package_filename = str.join('.', [self.bundle_folder, 'tgz'])
        self.package_path = os.path.join(self.bundles_path, self.package_filename)
        self.cache_id_filename = str.join('.', [self.bundle_folder, 'cache_id'])
        self.package_cache_id_path = os.path.join(self.bundles_path, self.cache_id_filename)

    def is_cached(self):
        if os.path.isfile(self.package_cache_id_path):
            last_cache_id = None
            with open(self.package_cache_id_path, "r") as cache_fd:
                last_cache_id = cache_fd.read()
            if last_cache_id == self.cache_id:
                # print(f"LB is cached: {self.name}")
                return True
        # print(f"LB not cached: {self.name}")
        return False

    def upload(self, paco_ctx, account_ctx):

        if not paco_ctx.nocache and self.is_cached():
            return

        s3_ctl = paco_ctx.get_controller('S3')
        bucket_name = s3_ctl.get_bucket_name(self.bucket_ref)


        s3_ref = Reference('paco.ref ' + self.bucket_ref)
        s3_client = account_ctx.get_aws_client('s3', s3_ref.region)

        # Bundle
        bundle_s3_key = os.path.join("LaunchBundles", self.package_filename)
        response = s3_client.upload_file(self.package_path, bucket_name, bundle_s3_key)
        # Cache ID
        utils.write_to_file(self.bundles_path, self.cache_id_filename, self.cache_id)
        cache_id_s3_key = os.path.join("LaunchBundles", self.cache_id_filename)
        response = s3_client.upload_file(self.package_cache_id_path, bucket_name, cache_id_s3_key)

    def set_launch_script(self, launch_script, enabled=True, is_windows=False):
        """Set the script run to launch the bundle. By convention, this file
        is named 'launch.sh', and is a reserved filename in a launch bundle.
        """
        if enabled == True:
            launch_bundle_enabled="true"
        else:
           launch_bundle_enabled="false"

        if is_windows == True:
            enabled_script = ""
            filename="launch.ps1"
        else:
            filename="launch.sh"
            enabled_script = f"""
    # This script is auto-generated. Do not edit.
    LAUNCH_BUNDLE_ENABLED={launch_bundle_enabled}
    if [ "$LAUNCH_BUNDLE_ENABLED" == "true" ] ; then
        run_launch_bundle
    else
        disable_launch_bundle
    fi
    """
        self.add_file(filename, launch_script + enabled_script)

    def add_file(self, name, contents):
        """Add a file to the launch bundle"""
        file_config = {
            'name': name,
            'contents': contents
        }
        self.bundle_files.append(file_config)

    def build(self):
        """Builds the launch bundle. Puts the files for the bundle in a bundles tmp dir
        and then creates a gzip archive.
        Updates the bundle cache id based on the contents of the bundle.
        """
        filelock = utils.lock_file(self.manager.paco_ctx, self.bundle_folder + '/lockfile')
        orig_cwd = os.getcwd()
        pathlib.Path(self.bundles_path).mkdir(parents=True, exist_ok=True)
        os.chdir(self.bundles_path)
        pathlib.Path(self.bundle_folder).mkdir(parents=True, exist_ok=True)
        contents_md5 = ""
        for bundle_file in self.bundle_files:
            utils.write_to_file(self.bundle_folder, bundle_file['name'], bundle_file['contents'], supress_file_lock=True)
            contents_md5 += md5sum(str_data=bundle_file['contents'])
        lb_tar = tarfile.open(self.package_filename, "w:gz")
        lb_tar.add(self.bundle_folder, recursive=True)
        lb_tar.close()
        os.chdir(orig_cwd)
        self.cache_id = md5sum(str_data=contents_md5)
        filelock.release()


class EC2LaunchManager():
    """
    Creates and stores a launch bundle in S3 and ensures that the bundle
    will be installed when an EC2 instance launches in an ASG via user_data.
    """
    def __init__(
        self,
        paco_ctx,
        app_engine,
        application,
        account_ctx,
        aws_region,
        stack_group,
        stack_tags
    ):
        self.paco_ctx = paco_ctx
        self.app_engine = app_engine
        self.application = application
        self.account_ctx = account_ctx
        self.aws_region = aws_region
        self.stack_group = stack_group
        self.cloudwatch_agent = False
        self.cloudwatch_agent_config = None
        self.id = 'ec2lm'
        self.launch_bundles = {}
        self.cache_id = {}
        self.stack_tags = stack_tags
        self.ec2lm_functions_script = {}
        self.ec2lm_buckets = {}
        self.launch_bundle_names = [
            'SSM', 'EIP', 'CloudWatchAgent', 'EFS', 'EBS', 'cfn-init', 'SSHAccess', 'ECS', 'CodeDeploy', 'ScriptManager', 'DNS'
        ]
        self.build_path = os.path.join(
            self.paco_ctx.build_path,
            'EC2LaunchManager',
            self.application.paco_ref_parts,
            self.account_ctx.get_name(),
            self.aws_region,
            self.application.name,
        )
        self.paco_base_path_linux = '/opt/paco'
        # legacy_flag: aim_name_2019_11_28 - Use AIM name
        if self.paco_ctx.legacy_flag('aim_name_2019_11_28') == True:
            self.paco_base_path_linux = '/opt/aim'

        self.paco_base_path_windows = 'c:\ProgramData\Paco'

    def get_cache_id(self, resource):
        """Return a cache id unique to an ASG resource.
        Cache id is an aggregate of all bundle cache ids and the ec2lm functions script cache id.
        """
        cache_context = '.'.join([resource.app_name, resource.group_name, resource.name])
        bucket_name = self.get_ec2lm_bucket_name(resource)
        ec2lm_functions_cache_id = ''
        if bucket_name in self.ec2lm_functions_script.keys():
            ec2lm_functions_cache_id = utils.md5sum(str_data=self.ec2lm_functions_script[bucket_name])
        if cache_context not in self.cache_id.keys():
            return ec2lm_functions_cache_id
        return self.cache_id[cache_context] + ec2lm_functions_cache_id

    def upload_bundle_stack_hook(self, hook, bundle):
        "Uploads the launch bundle to an S3 bucket"
        bundle.upload(self.paco_ctx, self.account_ctx)

    def stack_hook_cache_id(self, hook, bundle):
        "Cache method to return a bundle's cache id"
        return bundle.cache_id

    def add_bundle_to_s3_bucket(self, bundle):
        """Adds stack hook which will upload launch bundle to an S3 bucket when
        the stack is created or updated."""
        cache_context = '.'.join([bundle.resource.app_name, bundle.resource.group_name, bundle.resource.name])
        if cache_context not in self.cache_id.keys():
            self.cache_id[cache_context] = ''
        self.cache_id[cache_context] += bundle.cache_id
        stack_hooks = StackHooks()
        stack_hooks.add(
            name='UploadBundle.'+bundle.name,
            stack_action=['create', 'update'],
            stack_timing='post',
            hook_method=self.upload_bundle_stack_hook,
            cache_method=self.stack_hook_cache_id,
            hook_arg=bundle
        )
        s3_ctl = self.paco_ctx.get_controller('S3')
        s3_ctl.add_stack_hooks(resource_ref=bundle.bucket_ref, stack_hooks=stack_hooks)

    def ec2lm_functions_hook_cache_id(self, hook, hook_args):
        "Cache method for EC2LM functions cache id"
        s3_ctl = self.paco_ctx.get_controller('S3')
        bucket_name = s3_ctl.get_bucket_name(hook_args['s3_bucket_ref'])
        return utils.md5sum(str_data=self.ec2lm_functions_script[bucket_name])

    def ec2lm_functions_hook(self, hook, hook_args):
        "Hook to upload ec2lm_functions.bash to S3"
        s3_ctl = self.paco_ctx.get_controller('S3')
        bucket_name = s3_ctl.get_bucket_name(hook_args['s3_bucket_ref'])
        s3_ref = Reference('paco.ref ' + hook_args['s3_bucket_ref'])
        s3_client = self.account_ctx.get_aws_client('s3', s3_ref.region)
        if hook_args['is_windows']:
            filename='ec2lm_functions.ps1'
        else:
            filename='ec2lm_functions.bash'
        s3_client.put_object(
            Bucket=bucket_name,
            Body=self.ec2lm_functions_script[bucket_name],
            Key=filename
        )

    def ec2lm_update_instances_hook(self, hook, bucket_resource):
        "Hook to upload ec2lm_cache_id.md5 to S3 and invoke SSM Run Command on paco_ec2lm_update_instance"
        s3_bucket_ref, resource = bucket_resource
        cache_id = self.get_cache_id(resource)
        # update ec2lm_cache_id.md5 file
        s3_ctl = self.paco_ctx.get_controller('S3')
        bucket_name = s3_ctl.get_bucket_name(s3_bucket_ref)
        s3_ref = Reference('paco.ref ' + s3_bucket_ref)
        s3_client = self.account_ctx.get_aws_client('s3', s3_ref.region)
        s3_client.put_object(
            Bucket=bucket_name,
            Body=cache_id,
            Key="ec2lm_cache_id.md5"
        )
        # send SSM command to update existing instances
        ssm_ctl = self.paco_ctx.get_controller('SSM')
        ssm_ctl.paco_ec2lm_update_instance(
            resource=resource,
            account_ctx=self.account_ctx,
            region=self.aws_region,
            cache_id=cache_id
        )

    def ec2lm_update_instances_cache(self, hook, bucket_resource):
        "Cache method for EC2LM resource"
        s3_bucket_ref, resource = bucket_resource
        return self.get_cache_id(resource)

    def init_ec2lm_s3_bucket(self, resource):
        "Initialize the EC2LM S3 Bucket stack if it does not already exist"
        bucket_config_dict = {
            'enabled': True,
            'bucket_name': 'lb',
            'deletion_policy': 'delete',
            'policy': [ {
                'aws': [ "%s" % (resource._instance_iam_role_arn) ],
                'effect': 'Allow',
                'action': [
                    's3:Get*',
                    's3:List*'
                ],
                'resource_suffix': [
                    '/*',
                    ''
                ]
            } ]
        }
        bucket = models.applications.S3Bucket('ec2lm', resource)
        bucket.update(bucket_config_dict)
        bucket.resolve_ref_obj = self
        bucket.enabled = resource.is_enabled()

        s3_bucket_ref = bucket.paco_ref_parts
        if s3_bucket_ref in self.ec2lm_buckets.keys():
            return

        hook_args = {
            's3_bucket_ref': s3_bucket_ref,
            'is_windows': resource.instance_ami_type.startswith("windows")
        }

        s3_ctl = self.paco_ctx.get_controller('S3')
        s3_ctl.init_context(
            self.account_ctx,
            self.aws_region,
            s3_bucket_ref,
            self.stack_group,
            StackTags(self.stack_tags)
        )

        # EC2LM Common Functions StackHooks
        stack_hooks = StackHooks()
        stack_hooks.add(
            name='UploadEC2LMFunctions',
            stack_action='create',
            stack_timing='post',
            hook_method=self.ec2lm_functions_hook,
            cache_method=self.ec2lm_functions_hook_cache_id,
            hook_arg=hook_args
        )
        stack_hooks.add(
            name='UploadEC2LMFunctions',
            stack_action='update',
            stack_timing='post',
            hook_method=self.ec2lm_functions_hook,
            cache_method=self.ec2lm_functions_hook_cache_id,
            hook_arg=hook_args
        )
        s3_ctl.add_bucket(
            bucket,
            config_ref=s3_bucket_ref,
            stack_hooks=stack_hooks,
            change_protected=resource.change_protected
        )

        # save the bucket to the EC2LaunchManager
        self.ec2lm_buckets[s3_bucket_ref] = bucket
        return bucket

    def get_ec2lm_bucket_name(self, resource):
        "Paco reference to the ec2lm bucket for a resource"
        s3_ctl = self.paco_ctx.get_controller('S3')
        return s3_ctl.get_bucket_name(resource.paco_ref_parts + '.ec2lm')

    def init_ec2lm_live_patching(self, resource, live_patching_config):
        if resource.is_enabled() == False:
            return
        s3_ctl = self.paco_ctx.get_controller('S3')
        policy_dict = {
            'aws': [ "%s" % (resource._instance_iam_role_arn) ],
            'effect': 'Allow',
            'action': [
                's3:Get*',
                's3:List*',
                's3:PutObject'
            ],
            'resource_suffix': [
                '/packages.list',
                '/release.version',
                ''
            ]
        }
        s3_ctl.add_bucket_policy(live_patching_config.s3_bucket, policy_dict)


    def init_ec2lm_function(self, ec2lm_bucket_name, resource, stack_name):
        """Init ec2lm_functions.bash script and add managed policies"""
        oldest_health_check_timeout = 0
        if resource.target_groups != None and len(resource.target_groups) > 0:
            for target_group in resource.target_groups:
                if is_ref(target_group):
                    target_group_obj = self.paco_ctx.get_ref(target_group)
                    health_check_timeout = (target_group_obj.healthy_threshold * target_group_obj.health_check_interval)
                    if oldest_health_check_timeout < health_check_timeout:
                        oldest_health_check_timeout = health_check_timeout

        launch_bundle_names = ' '.join(self.launch_bundle_names)
        if self.paco_ctx.legacy_flag('aim_name_2019_11_28') == True:
            tool_name = 'AIM'
        else:
            tool_name = 'PACO'

        if resource.instance_ami_type.startswith("windows") == True:
            windows_dict = ec2lm_scripts.functions['windows_dict'].copy()
            windows_dict['launch_bundle_names'] = "'codedeploy'"
            self.ec2lm_functions_script[ec2lm_bucket_name] = ec2lm_scripts.functions['windows'].format(
                **windows_dict
            )
        else:
            linux_dict = ec2lm_scripts.functions['linux_dict'].copy()
            linux_dict['account_id'] = self.account_ctx.id
            linux_dict['paco_base_path'] = self.paco_base_path_linux
            linux_dict['tool_name'] = tool_name
            linux_dict['netenv'] = resource.netenv_name
            linux_dict['environment'] = resource.env_name
            linux_dict['environment_ref'] = resource.env_region_obj.paco_ref_parts
            linux_dict['ec2lm_bucket_name'] = ec2lm_bucket_name
            linux_dict['launch_bundle_names'] = launch_bundle_names
            linux_dict['oldest_health_check_timeout'] = oldest_health_check_timeout
            linux_dict['install_wget'] = ec2lm_commands.user_data_script['install_wget'][resource.instance_ami_type_generic]
            linux_dict['install_package'] = ec2lm_commands.user_data_script['install_package'][resource.instance_ami_type_generic]
            linux_dict['update_packages'] = ec2lm_commands.user_data_script['update_packages'][resource.instance_ami_type_generic]
            linux_dict['purge_codedeploy'] = ec2lm_commands.user_data_script['purge_codedeploy'][resource.instance_ami_type_generic]
            live_patching_config = resource.launch_options.amazon_linux_live_patching
            if live_patching_config != None and live_patching_config.enabled == True:
                linux_dict['live_patch_enabled'] = 'true'
                linux_dict['live_patch_release_version'] = live_patching_config.release_version
                linux_dict['live_patch_kernel_version'] = live_patching_config.kernel_version
                s3_ctl = self.paco_ctx.get_controller('S3')
                linux_dict['live_patch_s3_bucket'] = s3_ctl.get_bucket_name(live_patching_config.s3_bucket)
                self.init_ec2lm_live_patching(resource, live_patching_config)

            self.ec2lm_functions_script[ec2lm_bucket_name] = ec2lm_scripts.functions['linux'].format(**linux_dict)
            if resource.secrets != None and len(resource.secrets) > 0:
                self.ec2lm_functions_script[ec2lm_bucket_name] += self.add_secrets_function_policy(resource)

             # Async run commands for bash
            self.ec2lm_functions_script[ec2lm_bucket_name] += ec2lm_scripts.async_run['linux']

        # Add a base IAM Managed Policy to allow access to EC2 Tags
        iam_policy_name = '-'.join([resource.name, 'ec2lm'])
        policy_config_yaml = f"""
policy_name: '{iam_policy_name}'
enabled: true
statement:
  - effect: Allow
    action:
      - "ec2:DescribeTags"
    resource:
      - '*'
"""
        # allow cloudformation SignalResource and DescribeStacks if needed
        if resource.rolling_update_policy.wait_on_resource_signals == True:
            policy_config_yaml += f"""

  - effect: Allow
    action:
      - "cloudformation:SignalResource"
      - "cloudformation:DescribeStacks"
      - "cloudformation:ListStacks"
    resource:
      - 'arn:aws:cloudformation:{self.aws_region}:{self.account_ctx.id}:stack/{stack_name}/*'
"""
        iam_ctl = self.paco_ctx.get_controller('IAM')
        iam_ctl.add_managed_policy(
            role=resource.instance_iam_role,
            resource=resource,
            policy_name='policy',
            policy_config_yaml=policy_config_yaml,
            extra_ref_names=['ec2lm','ec2lm'],
        )

    def user_data_script_windows(self, resource, stack_name):
        """BASH script that will load the launch bundle from user_data"""
        if resource.change_protected == True:
            return "<powershell></powershell>\n"
        self.init_ec2lm_s3_bucket(resource)
        ec2lm_bucket_name = self.get_ec2lm_bucket_name(resource)

        # EC2LM Functions and Managed Policies
        self.init_ec2lm_function(ec2lm_bucket_name, resource, stack_name)

        install_aws_cli = "Start-Process msiexec.exe -ArgumentList '/quiet  /i https://awscli.amazonaws.com/AWSCLIV2.msi' -Wait"
        windows_dict = ec2lm_scripts.user_data_script['windows_dict'].copy()
        windows_dict['ec2lm_bucket_name'] = ec2lm_bucket_name
        windows_dict['region'] = resource.region_name
        windows_dict['paco_base_path'] = self.paco_base_path_windows
        windows_dict['pre_script'] = resource.user_data_pre_script
        windows_dict['install_aws_cli'] = install_aws_cli
        windows_dict['user_provided_script'] = resource.user_data_script
        return ec2lm_scripts.user_data_script['windows'].format(**windows_dict)

    def user_data_script_linux(self, resource, stack_name):
        """BASH script that will load the launch bundle from user_data"""
        if resource.change_protected == True:
            return "#!/bin/bash\n"
        self.init_ec2lm_s3_bucket(resource)
        ec2lm_bucket_name = self.get_ec2lm_bucket_name(resource)

        # EC2LM Functions and Managed Policies
        self.init_ec2lm_function(ec2lm_bucket_name, resource, stack_name)

        # Checks and warnings
        update_packages =''
        if resource.launch_options.update_packages == True:
            update_packages = ec2lm_commands.user_data_script['update_packages'][resource.instance_ami_type_generic]
        if self.paco_ctx.warn:
            if resource.rolling_update_policy != None and \
                resource.rolling_update_policy.wait_on_resource_signals == True and \
                    resource.user_data_script.find('ec2lm_signal_asg_resource') == -1:
                print("WARNING: {}.rolling_update_policy.wait_on_resource_signals == True".format(resource.paco_ref_parts))
                print("'ec2lm_signal_asg_resource <SUCCESS|FAILURE>' was not detected in your user_data_script for this resource.")

        # Newer Ubuntu (>20) does not have Python 2
        if resource.instance_ami_type in ('ubuntu_20', 'amazon_ecs', 'amazon_ecs_arm', 'ubuntu_18', 'ubuntu_18_cis'):
            install_aws_cli = ec2lm_commands.user_data_script['install_aws_cli'][resource.instance_ami_type]
        else:
            install_aws_cli = ec2lm_commands.user_data_script['install_aws_cli'][resource.instance_ami_type_generic]

        linux_dict = ec2lm_scripts.user_data_script['linux_dict'].copy()
        linux_dict['ec2lm_bucket_name'] = ec2lm_bucket_name
        linux_dict['region'] = resource.region_name
        linux_dict['paco_base_path'] = self.paco_base_path_linux
        linux_dict['pre_script'] = resource.user_data_pre_script
        linux_dict['install_aws_cli'] = install_aws_cli
        linux_dict['update_packages'] = update_packages
        linux_dict['user_provided_script'] = resource.user_data_script

        return ec2lm_scripts.user_data_script['linux'].format(**linux_dict)

    def user_data_script(self, resource, stack_name):
        """BASH script that will load the launch bundle from user_data"""
        if resource.instance_ami_type.startswith("windows"):
            return self.user_data_script_windows(resource, stack_name)
        else:
            return self.user_data_script_linux(resource, stack_name)

    def add_secrets_function_policy(self, resource):
        "Add ec2lm_functions.bash function for Secrets and managed policy to allow access to secrets"
        secrets_script = ec2lm_scripts.secrets['linux']
        iam_policy_name = '-'.join([resource.name, 'secrets'])
        template_params = []
        secret_arn_list_yaml = ""
        for secret in resource.secrets:
            secret_ref = Reference(secret)
            secret_hash = utils.md5sum(str_data='.'.join(secret_ref.parts))
            param = {
                'description': 'Secrets Manager Secret ARN',
                'type': 'String',
                'key': 'SecretArn' + secret_hash,
                'value': secret + '.arn'
            }
            template_params.append(param)
            secret_arn_list_yaml += "      - !Ref SecretArn" + secret_hash + "\n"

        policy_config_yaml = f"""
policy_name: '{iam_policy_name}'
enabled: true
statement:
  - effect: Allow
    action:
      - secretsmanager:GetSecretValue
    resource:
{secret_arn_list_yaml}
"""
        iam_ctl = self.paco_ctx.get_controller('IAM')
        iam_ctl.add_managed_policy(
            role=resource.instance_iam_role,
            resource=resource,
            policy_name='policy',
            policy_config_yaml=policy_config_yaml,
            template_params=template_params,
            extra_ref_names=['ec2lm','secrets'],
        )
        return secrets_script

    def add_bundle(self, bundle):
        "Build and add a bundle to the ec2lm S3 Bucket"
        bundle.build()
        if bundle.bucket_ref not in self.launch_bundles:
            self.init_ec2lm_s3_bucket(bundle.resource)
            self.launch_bundles[bundle.bucket_ref] = []
        # Add the bundle to the S3 Context ID bucket
        self.add_bundle_to_s3_bucket(bundle)
        self.launch_bundles[bundle.bucket_ref].append(bundle)

    def lb_add_cfn_init(self, bundle_name, resource):
        """Launch bundle to install and run cfn-init configsets"""
        cfn_init_lb = LaunchBundle(resource, self, bundle_name)

        cfn_init_enabled = True
        if resource.cfn_init == None or len(resource.launch_options.cfn_init_config_sets) == 0:
            cfn_init_enabled = False

        # cfn-init base path
        if resource.instance_ami_type_generic in ['amazon', 'centos']:
            # Amazon Linux and CentOS have cfn-init pre-installed at /opt/aws/
            cfn_base_path = '/opt/aws'
        else:
            # other OS types will install cfn-init into the Paco directory
            cfn_base_path = self.paco_base_path_linux

        if resource.instance_ami_type in ec2lm_commands.user_data_script['install_cfn_init']:
            install_cfn_init_command = ec2lm_commands.user_data_script['install_cfn_init'][resource.instance_ami_type]
        else:
            install_cfn_init_command = ec2lm_commands.user_data_script['install_cfn_init'][resource.instance_ami_type_generic]
        install_cfn_init_command = install_cfn_init_command.format(cfn_base_path=cfn_base_path)

        config_sets_str = ','.join(resource.launch_options.cfn_init_config_sets)
        launch_script = f"""#!/bin/bash
. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash

function run_launch_configuration() {{
    {cfn_base_path}/bin/cfn-init --stack=$EC2LM_STACK_NAME --resource=LaunchConfiguration --region=$REGION --configsets={config_sets_str}
}}

function run_launch_bundle() {{
    # cfn-init configsets are only run by Paco during initial launch
    if [[ ! -f ./initialized-configsets.txt  || "$EC2LM_IGNORE_CACHE" == "true" ]]; then
        {install_cfn_init_command}
        echo "{config_sets_str}" >> ./initialized-configsets.txt
        run_launch_configuration
        set +e
        {cfn_base_path}/bin/cfn-signal -e $? --stack $EC2LM_STACK_NAME --resource=LaunchConfiguration --region=$REGION
        set -e
    fi
}}

function disable_launch_bundle() {{
    # touch the initialized-configsets.txt file to prevent a later addition
    # of a cfn-init ConfigSet from running unexpectedly
    touch ./initialized-configsets.txt
}}

# enable local running of launch configset with:
# $EC2LM_FOLDER/LaunchBundles/cfn-init/launch.sh run
RUN_LAUNCH_CFN=$1
if [ "$RUN_LAUNCH_CFN" == "run" ] ; then
    run_launch_configuration
fi

"""
        cfn_init_lb.set_launch_script(launch_script, cfn_init_enabled)
        self.add_bundle(cfn_init_lb)

    def lb_add_efs(self, bundle_name, resource):
        """Launch bundle to configure and mount EFS"""
        efs_lb = LaunchBundle(resource, self, bundle_name)

        efs_enabled = False
        if len(resource.efs_mounts) >= 0:
            process_mount_targets = ""
            for efs_mount in resource.efs_mounts:
                if efs_mount.enabled == False:
                    continue
                efs_enabled = True
                if is_ref(efs_mount.target) == True:
                    stack = resolve_ref(efs_mount.target, self.paco_ctx.project, self.account_ctx)
                    efs_stack_name = stack.get_name()
                else:
                    # ToDo: Paco EC2LM does not yet support string EFS Ids
                    raise AttributeError('String EFS Id values not yet supported by EC2LM')
                if efs_mount.read_only_mode == True:
                    read_only_flag = "true"
                else:
                    read_only_flag = "false"
                process_mount_targets += "process_mount_target {} {} {}\n".format(efs_mount.folder, efs_stack_name, read_only_flag)

        # ToDo: add other unsupported OSes here (Suse? CentOS 6)
        if resource.instance_ami_type in ['ubuntu_14',]:
            raise AttributeError(f"OS type {resource.instance_ami_type} does not support EFS")
        install_efs_utils = ec2lm_commands.user_data_script['install_efs_utils'][resource.instance_ami_type_generic]
        mount_efs = ec2lm_commands.user_data_script['mount_efs'][resource.instance_ami_type_generic]
        if resource.instance_ami_type_generic == 'ubuntu':
            install_efs_utils = ec2lm_commands.user_data_script['install_efs_utils'][resource.instance_ami_type_generic]
            mount_efs = ec2lm_commands.user_data_script['mount_efs'][resource.instance_ami_type_generic]

        launch_script = f"""#!/bin/bash

. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash
EFS_MOUNT_FOLDER_LIST=./efs_mount_folder_list
EFS_ID_LIST=./efs_id_list

mkdir -p /root/tmp
TMP_DIR=/root/tmp

function process_mount_target()
{{
    MOUNT_FOLDER=$1
    EFS_STACK_NAME=$2
    READ_ONLY_MODE=$3

    # Get EFS ID from Tag
    EFS_ID=$(aws efs describe-file-systems --region $REGION --no-paginate --query "FileSystems[].{{Tags: Tags[?Key=='Paco-Stack-Name'].Value, FileSystemId: FileSystemId}} | [].{{stack: Tags[0], fs: FileSystemId}} | [?stack=='$EFS_STACK_NAME'].fs | [0]" | tr -d '"')

    # Setup the mount folder
    set +e
    # Verify we are mounting the correct EFS IDs
    if [ -e $MOUNT_FOLDER ] ; then
        if mountpoint -q -- $MOUNT_FOLDER; then
            mount |grep " on $MOUNT_FOLDER" |grep "$EFS_ID"
            if [ $? -ne 0 ] ; then
                echo "EFS: A new EFS_ID detected: unmounting folder: $MOUNT_FOLDER"
                umount $MOUNT_FOLDER
            else
                echo "EFS: Folder already mounted: $MOUNT_FOLDER -> $EFS_ID"
            fi
        fi
    else
        mkdir -p $MOUNT_FOLDER
    fi
    set -e

    # Setup fstab
    READ_ONLY_FLAG=""
    if [ "$READ_ONLY_MODE" == "true" ]; then
        READ_ONLY_FLAG="ro,"
    fi
    grep -v -E "^$EFS_ID:/" /etc/fstab >${{TMP_DIR}}/fstab.efs_new
    mv ${{TMP_DIR}}/fstab.efs_new /etc/fstab
    grep -v -E " $MOUNT_FOLDER efs " /etc/fstab >${{TMP_DIR}}/fstab.efs_new
    echo "$EFS_ID:/ $MOUNT_FOLDER efs ${{READ_ONLY_FLAG}}defaults,_netdev,fsc 0 0" >>${{TMP_DIR}}/fstab.efs_new
    mv ${{TMP_DIR}}/fstab.efs_new /etc/fstab
    chmod 0664 /etc/fstab
    echo "$MOUNT_FOLDER" >>$EFS_MOUNT_FOLDER_LIST".new"
    echo "$EFS_ID" >>$EFS_ID_LIST".new"
    cat /etc/fstab
    df -h
}}

function run_launch_bundle() {{
    # Install EFS Utils
    {install_efs_utils}
    # Enable EFS Utils
    {ec2lm_commands.user_data_script['enable_efs_utils'][resource.instance_ami_type_generic]}

    # Process Mounts
    :>$EFS_MOUNT_FOLDER_LIST".new"
    :>$EFS_ID_LIST".new"
    {process_mount_targets}
    mv $EFS_MOUNT_FOLDER_LIST".new" $EFS_MOUNT_FOLDER_LIST
    mv $EFS_ID_LIST".new" $EFS_ID_LIST

    # Mount EFS folders
    {mount_efs}
}}

function disable_launch_bundle() {{
    # Remove them if they exist
    if [ -e "$EFS_MOUNT_FOLDER_LIST" ] ; then
        for MOUNT_FOLDER in $(cat $EFS_MOUNT_FOLDER_LIST)
        do
            umount $MOUNT_FOLDER
        done
        rm $EFS_MOUNT_FOLDER_LIST
    fi
    if [ -e "$EFS_ID_LSIT" ] ; then
        for EFS_ID in $(cat $EFS_ID_LIST)
        do
            grep -v -E "^$EFS_ID:/" /etc/fstab >${{TMP_DIR}}/fstab.efs_new
            mv ${{TMP_DIR}}/fstab.efs_new /etc/fstab
            chmod 0664 /etc/fstab
        done
        rm $EFS_ID_LIST
    fi
}}
"""
        efs_lb.set_launch_script(launch_script, efs_enabled)
        self.add_bundle(efs_lb)

        # IAM Managed Policy to allow EFS
        if efs_enabled:
            iam_policy_name = '-'.join([resource.name, 'efs'])
            policy_config_yaml = """
policy_name: '{}'
enabled: true
statement:
  - effect: Allow
    action:
      - 'elasticfilesystem:DescribeFileSystems'
      - 'elasticfilesystem:DescribeMountTargets'
    resource:
      - '*'
""".format(iam_policy_name)
            iam_ctl = self.paco_ctx.get_controller('IAM')
            iam_ctl.add_managed_policy(
                role=resource.instance_iam_role,
                resource=resource,
                policy_name='policy',
                policy_config_yaml=policy_config_yaml,
                extra_ref_names=['ec2lm','efs'],
            )

    def lb_add_ebs(self, bundle_name, resource):
        """Launch bundle to configure and mount EBS Volumes"""
        ebs_lb = LaunchBundle(resource, self, bundle_name)

        # is EBS enabled? if yes, create process_volume_mount commands
        ebs_enabled = False
        process_mount_volumes = ""
        for ebs_volume_mount in resource.ebs_volume_mounts:
            if ebs_volume_mount.enabled == False:
                continue
            ebs_enabled = True

            ebs_volume_id = ebs_volume_mount.volume
            if is_ref(ebs_volume_mount.volume) == True:
                ebs_stack = resolve_ref(ebs_volume_mount.volume, self.paco_ctx.project, self.account_ctx)
                ebs_stack_name = ebs_stack.get_name()
                ebs_volume_id = ebs_stack_name

            process_mount_volumes += "process_volume_mount {} {} {} {}\n".format(
                ebs_volume_mount.folder,
                ebs_volume_id,
                ebs_volume_mount.filesystem,
                ebs_volume_mount.device
            )

        launch_script = f"""#!/bin/bash

. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash

INSTANCE_AMI_TYPE_GENERIC={resource.instance_ami_type_generic}
NVME_CLI=nvme-cli

EBS_MOUNT_FOLDER_LIST=ebs_mount_folder_list
EBS_VOLUME_UUID_LIST=ebs_volume_uuid_list
LINUX_DEVICE=""

# Attach EBS Volume
function ec2lm_attach_ebs_volume() {{
    EBS_VOLUME_ID=$1
    EBS_DEVICE=$2
    INSTANCE_ID=$3

    set +e
    ATTACHED_INSTANCE_ID=$(aws ec2 describe-volumes --volume-ids $EBS_VOLUME_ID --region $REGION --query "Volumes[*].Attachments[*].[InstanceId]" --filter Name=volume-id,Values=$EBS_VOLUME_ID --output text)
    set -e
    if [ "$ATTACHED_INSTANCE_ID" == "$INSTANCE_ID" ] ; then
        echo "EC2LM: EBS: $EBS_VOLUME_ID is already attached to $INSTANCE_ID as $EBS_DEVICE"
        return 0
    fi

    aws ec2 attach-volume --region $REGION --volume-id $EBS_VOLUME_ID --instance-id $INSTANCE_ID --device $EBS_DEVICE 2>/tmp/ec2lm_attach.output
    RES=$?
    if [ $RES -eq 0 ] ; then
        echo "EC2LM: EBS: Successfully attached $EBS_VOLUME_ID to $INSTANCE_ID as $EBS_DEVICE"
        return 0
    fi
    return 1
}}


function ec2lm_volume_linux_device() {{
    EBS_VOLUME_ID=$1
    DEVICE=$2
    if [ "$INSTANCE_AMI_TYPE_GENERIC" == "ubuntu" ] ; then
        for BLK_DEVICE in $(lsblk -n -o NAME -p -d |grep -v loop)
        do
            if [ "$BLK_DEVICE" == $DEVICE ] ; then
                echo $DEVICE
                return 0
            fi
            DEVICE_VOLUME_ID="vol-"$(nvme id-ctrl -H $BLK_DEVICE |grep 'sn        : vol' | awk -F 'vol' '{{print $2}}')
            if [ "$DEVICE_VOLUME_ID" == "$EBS_VOLUME_ID" ]; then
                echo $BLK_DEVICE
                return 0
            fi
        done
        return 1
    else
        OUTPUT=$(file -s $DEVICE)
        if [[ $OUTPUT == *"No such file or directory"* ]] ; then
            return 1
        else
            echo $DEVICE
            return 0
        fi
    fi
    return 1
}}

# Checks if a volume has been attached
# ec2lm_volume_is_attached <device>
# Return: 0 == True
#         1 == False
function ec2lm_volume_is_attached() {{
    EBS_VOLUME_ID=$1
    DEVICE=$2
    LINUX_DEVICE=$(ec2lm_volume_linux_device $EBS_VOLUME_ID $DEVICE)
    RET=$?
    return $RET
}}

# Get the Volume UUID
# ec2lm_get_volume_uuid <device>
# Return: 0 == True
#         1 == False
function ec2lm_get_volume_uuid() {{
    EBS_DEVICE=$1
    VOLUME_UUID=$(/sbin/blkid $EBS_DEVICE |grep UUID |cut -d'"' -f 2)
    if [ "${{VOLUME_UUID}}" != "" ] ; then
        echo $VOLUME_UUID
        return 0
    fi
    return 1
}}

function ec2lm_mount_folder()
{{
    FOLDER=$1
    mount $FOLDER 2>&1
    RET=$?
    if [ $RET -eq 32 ] ; then
        # 32 == Already mounted
        return 0
    fi
    return 1

}}

# Attach and Mount an EBS Volume
function process_volume_mount()
{{
    MOUNT_FOLDER=$1
    EBS_VOLUME_ID=$2
    FILESYSTEM=$3
    EBS_DEVICE=$4

    echo "EC2LM: EBS: Process Volume Mount: Begin"

    # Get EBS Volume Id
    if [[ "$EBS_VOLUME_ID" != "vol-"* ]]; then
        EBS_VOLUME_ID=$(aws ec2 describe-volumes --filters Name=tag:aws:cloudformation:stack-name,Values=$EBS_VOLUME_ID --query "Volumes[*].VolumeId | [0]" --region $REGION | tr -d '"')
    fi

    # Setup the mount folder
    # if [ -e $MOUNT_FOLDER ] ; then
    #     mv $MOUNT_FOLDER ${{MOUNT_FOLDER%%/}}.old
    # fi
    mkdir -p $MOUNT_FOLDER

    TIMEOUT_SECS=300
    echo "EC2LM: EBS: Attaching $EBS_VOLUME_ID to $INSTANCE_ID as $EBS_DEVICE: Timeout = $TIMEOUT_SECS"
    OUTPUT=$(ec2lm_timeout $TIMEOUT_SECS ec2lm_attach_ebs_volume $EBS_VOLUME_ID $EBS_DEVICE $INSTANCE_ID)
    if [ $? -eq 1 ] ; then
        echo "[ERROR] EC2LM: EBS: Unable to attach $EBS_VOLUME_ID to $INSTANCE_ID as $EBS_DEVICE"
        echo "[ERROR] EC2LM: EBS: $OUTPUT"
        cat /tmp/ec2lm_attach.output
        exit 1
    else
        echo $OUTPUT
    fi

    # Initialize filesystem if blank
    echo "EC2LM: EBS: Waiting for volume to become available: $EBS_VOLUME_ID on $EBS_DEVICE"
    TIMEOUT_SECS=120
    OUTPUT=$(ec2lm_timeout $TIMEOUT_SECS ec2lm_volume_is_attached $EBS_VOLUME_ID $EBS_DEVICE)
    RET=$?
    if [ $RET -eq 1 ] ; then
        echo "EC2LM: EBS: Error: Unable to detect the attached volume $EBS_VOLUME_ID to $INSTANCE_ID as $EBS_DEVICE."
        echo "[ERROR] EC2LM: EBS: $OUTPUT"
        exit 1
    fi

    LINUX_DEVICE=$(ec2lm_volume_linux_device $EBS_VOLUME_ID $EBS_DEVICE)
    echo "EC2LM: EBS: Initializing Volume $EBS_VOLUME_ID on linux device $LINUX_DEVICE"

    # Format: Make a filesystem if the device
    FILE_FMT=$(file -s $LINUX_DEVICE)
    BLANK_FMT="$LINUX_DEVICE: data"
    if [ "$FILE_FMT" == "$BLANK_FMT" ] ; then
        echo "EC2LM: EBS: Initializing EBS Volume with FS type $FILESYSTEM"
        /sbin/mkfs -t $FILESYSTEM $LINUX_DEVICE
    fi

    # Setup fstab
    echo "EC2LM: EBS: Getting Volume UUID for $LINUX_DEVICE"
    TIMEOUT_SECS=30
    VOLUME_UUID=$(ec2lm_timeout $TIMEOUT_SECS ec2lm_get_volume_uuid $LINUX_DEVICE)
    if [ $? -eq 1 ] ; then
        echo "[ERROR] EC2LM: EBS: Unable to get volume UUID for $LINUX_DEVICE"
        echo "[ERROR] EC2LM: EBS: Error: $OUTPUT"
        /sbin/blkid
        exit 1
    fi

    # /etc/fstab entry
    echo "EC2LM: EBS: $LINUX_DEVICE UUID: $VOLUME_UUID"
    FSTAB_ENTRY="UUID=$VOLUME_UUID $MOUNT_FOLDER $FILESYSTEM defaults,nofail 0 2"
    echo "EC2LM: EBS: Configuring /etc/fstab: $FSTAB_ENTRY"
    grep -v -E "^UUID=$VOLUME_UUID" /etc/fstab | grep -v "$MOUNT_FOLDER" >/tmp/fstab.ebs_new
    echo $FSTAB_ENTRY >>/tmp/fstab.ebs_new
    mv /tmp/fstab.ebs_new /etc/fstab
    chmod 0664 /etc/fstab

    # Mount Volume
    echo "EC2LM: EBS: Mounting $MOUNT_FOLDER"
    echo "EC2LM: EBS: Waiting for folder to be mounted: $MOUNT_FOLDER"
    OUTPUT=$(ec2lm_timeout 60 ec2lm_mount_folder $MOUNT_FOLDER)
    RET=$?
    if [ $RET -eq 0 ] ; then
        echo "EC2LM: EBS: Folder $MOUNT_FOLDER was mounted successfully"
    else
    echo "EC2LM: EBS: Folder $MOUNT_FOLDER failed to mount before the timeout."
        echo $OUTPUT
        return 1
    fi
    echo "$MOUNT_FOLDER" >>$EBS_MOUNT_FOLDER_LIST".new"
    echo "$VOLUME_UUID" >>$EBS_VOLUME_UUID_LIST".new"
    echo "EC2LM: EBS: Process Volume Mount: Done"

    return 0
}}

function run_launch_bundle()
{{
    # Initialize
    if [ "$INSTANCE_AMI_TYPE_GENERIC" == "ubuntu" ] ; then
        apt-get install nvme-cli -y
        export NVME_CLI=nvme-cli
    fi
    # Process Mounts
    :>$EBS_MOUNT_FOLDER_LIST".new"
    :>$EBS_VOLUME_UUID_LIST".new"
    {process_mount_volumes}
    mv $EBS_MOUNT_FOLDER_LIST".new" $EBS_MOUNT_FOLDER_LIST
    mv $EBS_VOLUME_UUID_LIST".new" $EBS_VOLUME_UUID_LIST
}}

# Remove any previous mounts that existed
function disable_launch_bundle()
{{
    if [ "$EFS_MOUNT_FOLDER_LIST" != "" ] ; then
        for MOUNT_FOLDER in $(cat $EBS_MOUNT_FOLDER_LIST)
        do
            umount $MOUNT_FOLDER
        done

        for VOLUME_UUID in $(cat $EBS_VOLUME_UUID_LIST)
        do
            grep -v -E "^UUID=$VOLUME_UUID" /etc/fstab >/tmp/fstab.ebs_new
            mv /tmp/fstab.ebs_new /etc/fstab
        done
    fi
}}
"""
        ebs_lb.set_launch_script(launch_script, ebs_enabled)
        self.add_bundle(ebs_lb)

        # IAM Managed Policy to allow attaching volumes
        if ebs_enabled:
            iam_policy_name = '-'.join([resource.name, 'ebs'])
            policy_config_yaml = f"""
policy_name: '{iam_policy_name}'
enabled: true
statement:
  - effect: Allow
    action:
      - "ec2:AttachVolume"
    resource:
      - 'arn:aws:ec2:*:*:volume/*'
      - 'arn:aws:ec2:*:*:instance/*'
  - effect: Allow
    action:
      - "ec2:DescribeVolumes"
    resource:
      - "*"
"""
            iam_ctl = self.paco_ctx.get_controller('IAM')
            iam_ctl.add_managed_policy(
                role=resource.instance_iam_role,
                resource=resource,
                policy_name='policy',
                policy_config_yaml=policy_config_yaml,
                extra_ref_names=['ec2lm','ebs'],
            )

    def lb_add_eip(self, bundle_name, resource):
        """Creates a launch bundle to configure Elastic IPs"""
        # Create the Launch Bundle and configure it
        eip_lb = LaunchBundle(resource, self, bundle_name)

        enabled = True
        if resource.eip == None:
            enabled = False

        # get the EIP Stack Name
        eip_alloc_id = ''
        eip_stack_name = ''
        if is_ref(resource.eip) == True:
            eip_stack = resolve_ref(resource.eip, self.paco_ctx.project, self.account_ctx)
            eip_stack_name = eip_stack.get_name()
        elif resource.eip != None:
            eip_alloc_id = resource.eip

        launch_script = f"""#!/bin/bash

. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash

EIP_STATE_FILE=$EC2LM_FOLDER/LaunchBundles/EIP/eip-association-id.txt

function ec2lm_eip_is_associated() {{
    EIP_IP=$1
    EIP_ALLOC_ID=$2
    PUBLIC_IP=$(ec2_metadata public-ipv4/)
    if [ "$PUBLIC_IP" == "$EIP_IP" ] ; then
        echo "EC2LM: EIP: Association Successful"
        # save association id to allow later disassociation
        EIP_ASSOCIATION_ID=$(aws ec2 describe-addresses --allocation-ids $EIP_ALLOC_ID --query 'Addresses[0].AssociationId' --region $REGION | tr -d '"')
        echo "$EIP_ASSOCIATION_ID" > $EIP_STATE_FILE
        return 0
    fi
    return 1
}}

function run_launch_bundle()
{{
    # Allocation ID
    EIP_ALLOCATION_EC2_TAG_KEY_NAME="Paco-EIP-Allocation-Id"
    echo "EC2LM: EIP: Getting Allocation ID from EIP matching stack: {eip_stack_name}"
    EIP_ALLOC_ID=$(aws ec2 describe-tags --region $REGION --filter "Name=resource-type,Values=elastic-ip" "Name=tag:aws:cloudformation:stack-name,Values={eip_stack_name}" --query 'Tags[0].ResourceId' |tr -d '"')
    if [ "$EIP_ALLOC_ID" == "null" ] ; then
        EIP_ALLOC_ID=$(aws ec2 describe-tags --region $REGION --filter "Name=resource-type,Values=elastic-ip" "Name=tag:Paco-Stack-Name,Values={eip_stack_name}" --query 'Tags[0].ResourceId' |tr -d '"')
        if [ "$EIP_ALLOC_ID" == "null" ] ; then
            echo "EC2LM: EIP: ERROR: Unable to get EIP Allocation ID"
            exit 1
        fi
    fi

    # IP Address
    echo "EC2LM: EIP: Getting IP Address for $EIP_ALLOC_ID"
    EIP_IP=$(aws ec2 describe-addresses --allocation-ids $EIP_ALLOC_ID --query 'Addresses[0].PublicIp' --region $REGION | tr -d '"')

    # Association
    echo "EC2LM: EIP: Assocating $EIP_ALLOC_ID - $EIP_IP"
    aws ec2 associate-address --instance-id $INSTANCE_ID --allocation-id $EIP_ALLOC_ID --region $REGION

    # Wait for Association
    TIMEOUT_SECS=300
    OUTPUT=$(ec2lm_timeout $TIMEOUT_SECS ec2lm_eip_is_associated $EIP_IP $EIP_ALLOC_ID)
    RES=$?
    if [ $RES -lt 2 ] ; then
        echo "$OUTPUT"
    else
        echo "EC2LM: EIP: Error: $OUTPUT"
    fi
}}

function disable_launch_bundle()
{{
    if [ -e $EIP_STATE_FILE ] ; then
        EIP_ASSOCIATION_ID=$(<$EIP_STATE_FILE)
        aws ec2 disassociate-address --association-id $EIP_ASSOCIATION_ID --region $REGION
    fi
}}
"""
        eip_lb.set_launch_script(launch_script, enabled)
        self.add_bundle(eip_lb)

        # IAM Managed Policy to allow EIP
        if enabled:
            iam_policy_name = '-'.join([resource.name, 'eip'])
            policy_config_yaml = """
policy_name: '{}'
enabled: true
statement:
  - effect: Allow
    action:
      - 'ec2:AssociateAddress'
      - 'ec2:DisassociateAddress'
      - 'ec2:DescribeAddresses'
    resource:
      - '*'
""".format(iam_policy_name)
            iam_ctl = self.paco_ctx.get_controller('IAM')
            iam_ctl.add_managed_policy(
                role=resource.instance_iam_role,
                resource=resource,
                policy_name='policy',
                policy_config_yaml=policy_config_yaml,
                extra_ref_names=['ec2lm','eip'],
            )

    def lb_add_cloudwatchagent(self, bundle_name, resource):
        """Creates a launch bundle to install and configure a CloudWatch Agent:

         - Adds a launch script to install the agent

         - Adds a CW Agent JSON configuration file for the agent

         - Adds an IAM Policy to the instance IAM role that will allow the agent
           to do what it needs to do (e.g. send metrics and logs to CloudWatch)
        """
        cw_lb = LaunchBundle(resource, self, bundle_name)

        # is the cloudwatchagent bundle enabled?
        monitoring = resource.monitoring
        cw_enabled = True
        if monitoring == None or monitoring.enabled == False:
            cw_enabled = False

        # Launch script
        agent_path = ec2lm_commands.cloudwatch_agent[resource.instance_ami_type_generic]['path']
        if resource.instance_ami_type_family == 'redhat':
            agent_object = 'amazon-cloudwatch-agent.rpm'
            if resource.instance_ami_type in ('amazon_ecs', 'amazon'):
                download_agent_command=''
                install_command = 'yum install amazon-cloudwatch-agent -y'
                installed_command = 'yum list installed amazon-cloudwatch-agent'
                uninstall_command = 'yum remove amazon-cloudwatch-agent -y'
            else:
                download_agent_command = 'download_agent'
                install_command = f'rpm -U {agent_object}'
                installed_command = 'rpm -q amazon-cloudwatch-agent'
                uninstall_command = 'rpm -e amazon-cloudwatch-agent'
        elif resource.instance_ami_type_family == 'debian':
            agent_object = 'amazon-cloudwatch-agent.deb'
            install_command = f'dpkg -i -E {agent_object}'
            installed_command = 'dpkg --status amazon-cloudwatch-agent'
            uninstall_command = 'dpkg -P amazon-cloudwatch-agent'
            download_agent_command = 'download_agent'
        launch_script = f"""#!/bin/bash
echo "EC2LM: CloudWatch: Begin"
. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash

function download_agent() {{
        echo "EC2LM: CloudWatch: Downloading agent"
        wget -nv https://s3.amazonaws.com/amazoncloudwatch-agent{agent_path}/{agent_object}
        wget -nv https://s3.amazonaws.com/amazoncloudwatch-agent{agent_path}/{agent_object}.sig

        # Verify the agent
        echo "EC2LM: CloudWatch: Downloading and importing agent GPG key"
        TRUSTED_FINGERPRINT=$(echo "9376 16F3 450B 7D80 6CBD 9725 D581 6730 3B78 9C72" | tr -d ' ')
        wget -nv https://s3.amazonaws.com/amazoncloudwatch-agent/assets/amazon-cloudwatch-agent.gpg
        gpg --import amazon-cloudwatch-agent.gpg

        echo "EC2LM: CloudWatch: Verify agent signature"
        KEY_ID="$(gpg --list-packets amazon-cloudwatch-agent.gpg 2>&1 | awk '/keyid:/{{ print $2 }}' | tr -d ' ')"
        FINGERPRINT="$(gpg --fingerprint ${{KEY_ID}} 2>&1 | tr -d ' ')"
        OBJECT_FINGERPRINT="$(gpg --verify {agent_object}.sig {agent_object} 2>&1 | tr -d ' ')"
        if [[ ${{FINGERPRINT}} != *${{TRUSTED_FINGERPRINT}}* || ${{OBJECT_FINGERPRINT}} != *${{TRUSTED_FINGERPRINT}}* ]]; then
            # Log error here
            echo "[ERROR] CloudWatch Agent signature invalid: ${{KEY_ID}}: ${{OBJECT_FINGERPRINT}}"
            exit 1
        fi
        return 0
}}

function run_launch_bundle() {{
    LB_DIR=$(pwd)
    $({installed_command} &> /dev/null)
    RES=$?
    if [[ $RES -ne 0 ]]; then
        # Download the agent
        mkdir -p /tmp/paco/
        cd /tmp/paco/
        ec2lm_install_wget # built in function

        {download_agent_command}

        # Install the agent
        echo "EC2LM: CloudWatch: Installing agent: {install_command}"
        {install_command}
    fi

    cd ${{LB_DIR}}
    echo "EC2LM: CloudWatch: Updating configuration"
    /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:amazon-cloudwatch-agent.json -s
    echo "EC2LM: CloudWatch: Done"
}}

function disable_launch_bundle() {{
    $({installed_command} &> /dev/null)
    if [[ $? -eq 0 ]]; then
        {uninstall_command}
    fi
}}
"""
        if cw_enabled:
            # Agent Configuration file
            # /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
            agent_config = {
                "agent": {
                    "metrics_collection_interval": 60,
                    "region": self.aws_region,
                    "logfile": "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log"
                }
            }

            # if there is metrics, add to the cwagent config
            if monitoring.metrics:
                agent_config["metrics"] = {
                    "metrics_collected": {},
                    "append_dimensions": {
                        #"ImageId": "${aws:ImageId}",
                        #"InstanceId": "${aws:InstanceId}",
                        #"InstanceType": "${aws:InstanceType}",
                        "AutoScalingGroupName": "${aws:AutoScalingGroupName}"
                    },
                    "aggregation_dimensions" : [["AutoScalingGroupName"]]
                }
                collected = agent_config['metrics']['metrics_collected']
                for metric in monitoring.metrics:
                    if metric.collection_interval:
                        interval = metric.collection_interval
                    else:
                        interval = monitoring.collection_interval
                    collected[metric.name] = {
                        "measurement": metric.measurements,
                        "collection_interval": interval,
                    }
                    if metric.resources and len(metric.resources) > 0:
                        collected[metric.name]['resources'] = metric.resources
                    if metric.name == 'disk':
                        collected[metric.name]['drop_device'] = metric.drop_device

            # if there is logging, add it to the cwagent config
            if monitoring.log_sets:
                agent_config["logs"] = {
                    "logs_collected": {
                        "files": {
                            "collect_list": []
                        }
                    }
                }
                collect_list = agent_config['logs']['logs_collected']['files']['collect_list']
                for log_source in monitoring.log_sets.get_all_log_sources():
                    log_group = get_parent_by_interface(log_source, schemas.ICloudWatchLogGroup)
                    log_set = get_parent_by_interface(log_group, schemas.ICloudWatchLogSet)
                    prefixed_log_group_name = prefixed_name(
                        resource, log_group.get_full_log_group_name(), self.paco_ctx.legacy_flag,
                        app_name=log_set.log_group_app_name
                    )
                    source_config = {
                        "file_path": log_source.path,
                        "log_group_name": prefixed_log_group_name,
                        "log_stream_name": log_source.log_stream_name,
                        "encoding": log_source.encoding,
                        "timezone": log_source.timezone
                    }
                    if log_source.multi_line_start_pattern:
                        source_config["multi_line_start_pattern"] = log_source.multi_line_start_pattern
                    if log_source.timestamp_format:
                        source_config["timestamp_format"] = log_source.timestamp_format
                    collect_list.append(source_config)

            # Convert CW Agent data structure to JSON string
            agent_config = json.dumps(agent_config)
            cw_lb.add_file('amazon-cloudwatch-agent.json', agent_config)

            # Create instance managed policy for the agent
            iam_policy_name = '-'.join([resource.name, 'cloudwatchagent'])
            policy_config_yaml = f"""
policy_name: '{iam_policy_name}'
enabled: true
statement:
  - effect: Allow
    resource: "*"
    action:
      - "cloudwatch:PutMetricData"
      - "autoscaling:Describe*"
      - "ec2:DescribeTags"
"""
            if monitoring.log_sets:
                # allow a logs:CreateLogGroup action
                policy_config_yaml += """      - "logs:CreateLogGroup"\n"""
                log_group_resources = ""
                log_stream_resources = ""
                for log_group in monitoring.log_sets.get_all_log_groups():
                    lg_name = prefixed_name(resource, log_group.get_full_log_group_name(), self.paco_ctx.legacy_flag)
                    log_group_resources += "      - arn:aws:logs:{}:{}:log-group:{}:*\n".format(
                        self.aws_region,
                        self.account_ctx.id,
                        lg_name,
                    )
                    log_stream_resources += "      - arn:aws:logs:{}:{}:log-group:{}:log-stream:*\n".format(
                        self.aws_region,
                        self.account_ctx.id,
                        lg_name,
                    )
                policy_config_yaml += f"""
  - effect: Allow
    action:
      - "logs:DescribeLogStreams"
      - "logs:DescribeLogGroups"
      - "logs:CreateLogStream"
    resource:
{log_group_resources}
  - effect: Allow
    action:
      - "logs:PutLogEvents"
    resource:
{log_stream_resources}
"""
            policy_name = 'policy_ec2lm_cloudwatchagent'
            iam_ctl = self.paco_ctx.get_controller('IAM')
            iam_ctl.add_managed_policy(
                role=resource.instance_iam_role,
                resource=resource,
                policy_name='policy',
                policy_config_yaml=policy_config_yaml,
                extra_ref_names=['ec2lm','cloudwatchagent'],
            )

        # Set the launch script
        cw_lb.set_launch_script(launch_script, cw_enabled)
        self.add_bundle(cw_lb)

    def add_update_instance_ssm_document(self):
        "Add paco_ec2lm_update_instance SSM Document to the model"
        ssm_documents = self.paco_ctx.project['resource']['ssm'].ssm_documents
        if 'paco_ec2lm_update_instance' not in ssm_documents:
            ssm_doc = SSMDocument('paco_ec2lm_update_instance', ssm_documents)
            ssm_doc.add_location(self.account_ctx.paco_ref, self.aws_region)
            content = {
                "schemaVersion": "2.2",
                "description": "Paco EC2 LaunchManager update instance state",
                "parameters": {
                    "CacheId": {
                        "type": "String",
                        "description": "EC2LM Cache Id"
                    }
                },
                "mainSteps": [
                    {
                        "action": "aws:runShellScript",
                        "name": "updateEC2LMInstance",
                        "inputs": {
                            "runCommand": [
                                '#!/bin/bash',
                                f'. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash',
                                # Sync the folder
                                f'ec2lm_sync_folder >>/var/log/paco/ec2lm.log 2>&1',
                                # Reload the ec2lm_functions.bash just in case it has changed
                                f'. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash',
                                # Pass in 'nosync' because we just synced above
                                'ec2lm_launch_bundles ' + '{{CacheId}}' + ' nosync >>/var/log/paco/ec2lm.log 2>&1',
                            ]
                        }
                    }
                ]
            }
            ssm_doc.content = json.dumps(content)
            ssm_doc.document_type = 'Command'
            ssm_doc.enabled = True
            ssm_documents['paco_ec2lm_update_instance'] = ssm_doc
        else:
            ssm_documents['paco_ec2lm_update_instance'].add_location(
                self.account_ctx.paco_ref,
                self.aws_region,
            )

    def add_update_system_packages_ssm_command(self):
        "Add paco_ec2lm_update_system_packages SSM Document to the model"
        ssm_documents = self.paco_ctx.project['resource']['ssm'].ssm_documents

        if 'paco_ec2lm_update_system_packages' not in ssm_documents:
            ssm_doc = SSMDocument('paco_ec2lm_update_system_packages', ssm_documents)
            ssm_doc.add_location(self.account_ctx.paco_ref, self.aws_region)
            content = {
                "schemaVersion": "2.2",
                "description": "Paco EC2 Update System Packages",
                "mainSteps": [
                    {
                        "action": "aws:runShellScript",
                        "name": "updateSystemPackages",
                        "inputs": {
                            "runCommand": [
                                '#!/bin/bash',
                                # Reload the ec2lm_functions.bash just in case it has changed
                                f'. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash',
                                'ec2lm_update_packages >>/var/log/paco/ec2lm.log'
                            ]
                        }
                    }
                ]
            }
            ssm_doc.content = json.dumps(content)
            ssm_doc.document_type = 'Command'
            ssm_doc.enabled = True
            ssm_documents['paco_ec2lm_update_system_packages'] = ssm_doc
        else:
            ssm_documents['paco_ec2lm_update_system_packages'].add_location(
                self.account_ctx.paco_ref,
                self.aws_region,
            )

    def add_prepare_create_ami_ssm_command(self):
        "Add paco_ec2lm_prepare_create_ami SSM Document to the model"
        ssm_documents = self.paco_ctx.project['resource']['ssm'].ssm_documents

        if 'paco_ec2lm_prepare_create_ami' not in ssm_documents:
            ssm_doc = SSMDocument('paco_ec2lm_prepare_create_ami', ssm_documents)
            ssm_doc.add_location(self.account_ctx.paco_ref, self.aws_region)
            content = {
                "schemaVersion": "2.2",
                "description": "Paco EC2 Prepare for Create AMI",
                "parameters": {
                    "PurgeCodeDeploy": {
                        "type": "String",
                        "description": "Purge CodeDeploy"
                    }
                },
                "mainSteps": [
                    {
                        "action": "aws:runShellScript",
                        "name": "prepareCreateAMI",
                        "inputs": {
                            "runCommand": [
                                '#!/bin/bash',
                                # Reload the ec2lm_functions.bash just in case it has changed
                                f'. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash',
                                'ec2lm_prepare_create_ami ' + '{{PurgeCodeDeploy}}' + ' >>/var/log/paco/ec2lm.log 2>&1'
                            ]
                        }
                    }
                ]
            }
            ssm_doc.content = json.dumps(content)
            ssm_doc.document_type = 'Command'
            ssm_doc.enabled = True
            ssm_documents['paco_ec2lm_prepare_create_ami'] = ssm_doc
        else:
            ssm_documents['paco_ec2lm_prepare_create_ami'].add_location(
                self.account_ctx.paco_ref,
                self.aws_region,
            )

    def add_amazon_live_patching_ssm_command(self):
        "Add paco_ec2lm_amazon_live_patching SSM Document to the model"
        ssm_documents = self.paco_ctx.project['resource']['ssm'].ssm_documents

        if 'paco_ec2lm_amazon_live_patching' not in ssm_documents:
            ssm_doc = SSMDocument('paco_ec2lm_amazon_live_patching', ssm_documents)
            ssm_doc.add_location(self.account_ctx.paco_ref, self.aws_region)
            content = {
                "schemaVersion": "2.2",
                "description": "Paco Amazon Linux 2023 Live Patching",
                "parameters": {
                },
                "mainSteps": [
                    {
                        "action": "aws:runShellScript",
                        "name": "amazonLivePatching",
                        "inputs": {
                            "runCommand": [
                                '#!/bin/bash',
                                # Reload the ec2lm_functions.bash just in case it has changed
                                f'. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash',
                                'ec2lm_amazon_live_patching >>/var/log/paco/ec2lm.log 2>&1'
                            ]
                        }
                    }
                ]
            }
            ssm_doc.content = json.dumps(content)
            ssm_doc.document_type = 'Command'
            ssm_doc.enabled = True
            ssm_documents['paco_ec2lm_amazon_live_patching'] = ssm_doc
        else:
            ssm_documents['paco_ec2lm_amazon_live_patching'].add_location(
                self.account_ctx.paco_ref,
                self.aws_region,
            )

    def lb_add_sshaccess(self, bundle_name, resource):
        "SSH Access Bundle"
        ssh_lb = LaunchBundle(resource, self, bundle_name)
        ssh_access = resource.ssh_access
        launch_script = f"""#!/bin/bash
echo "EC2LM: SSHAccess: Begin"
. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash
"""
        ssh_enabled = False
        auth_key_file = ec2lm_commands.default_user[resource.instance_ami_type_generic] + '/.ssh/authorized_keys'
        auth_key_contents=''
        if len(ssh_access.users) > 0 or len(ssh_access.groups) > 0:
            ssh_enabled = True
            public_keys = {}
            public_keys_user = {}
            project = get_parent_by_interface(resource)
            ec2_users = project.resource['ec2'].users
            ec2_groups = project.resource['ec2'].groups
            for username in ssh_access.users:
                public_keys[ec2_users[username].public_ssh_key] = True
                public_keys_user[ec2_users[username].public_ssh_key] = username
            for groupname in ssh_access.groups:
                group = ec2_groups[groupname]
                for username in group.members:
                    public_keys[ec2_users[username].public_ssh_key] = True
                    public_keys_user[ec2_users[username].public_ssh_key] = username

            key_lines = ['# Autogenerated by Paco - do not edit after this line',]
            idx = 0
            for public_key in public_keys.keys():
                key_lines.append(f'{public_key} {public_keys_user[public_key]}')
                idx += 1
            auth_key_contents = "\n".join(key_lines)

        launch_script += f"""
AUTH_KEY_FILE={auth_key_file}
AUTH_CONTENTS='{auth_key_contents}'

function run_launch_bundle() {{
    # Remove everything after '# Autogenerated by Paco'
    echo "EC2LM: SSHAccess: Updating SSH authentication file: $AUTH_KEY_FILE"
    sed -i '/# Autogenerated by Paco - do not edit after this line/Q' $AUTH_KEY_FILE
    # append Paco public keys
    echo -e "$AUTH_CONTENTS" >> $AUTH_KEY_FILE
    echo "EC2LM: SSHAccess: End"
}}

function disable_launch_bundle() {{
    # Remove everything after '# Autogenerated by Paco'
    echo "EC2LM: SSHAccess: Disabling Paco SSH authentication: $AUTH_KEY_FILE"
    sed -i '/# Autogenerated by Paco - do not edit after this line/Q' $AUTH_KEY_FILE
    echo "EC2LM: SSHAccess: End"
}}
"""
        ssh_lb.set_launch_script(launch_script, ssh_enabled)
        self.add_bundle(ssh_lb)

    def lb_add_ecs(self, bundle_name, resource):
        "ECS Launch Bundle"
        ecs_lb = LaunchBundle(resource, self, bundle_name)
        ecs = resource.ecs
        launch_script = f"""#!/bin/bash

. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash

function disable_launch_bundle() {{
    rm -f /etc/ecs/ecs.config
}}
"""


        # is the ECS bundle enabled?
        ecs_enabled = False
        if ecs != None:
            ecs_enabled = True
            # ECS Policy
            iam_policy_name = '-'.join([resource.name, 'ecs'])
            policy_config_yaml = f"""
policy_name: '{iam_policy_name}'
enabled: true
path: /
statement:
  - effect: Allow
    action:
      - 'ecs:CreateCluster'
      - 'ecs:DeregisterContainerInstance'
      - 'ecs:DiscoverPollEndpoint'
      - 'ecs:Poll'
      - 'ecs:RegisterContainerInstance'
      - 'ecs:StartTelemetrySession'
      - 'ecs:Submit*'
      - 'logs:CreateLogStream'
      - 'logs:PutLogEvents'
      - 'ecr:GetAuthorizationToken'
      - 'ecr:BatchCheckLayerAvailability'
      - 'ecr:GetDownloadUrlForLayer'
      - 'ecr:GetRepositoryPolicy'
      - 'ecr:DescribeRepositories'
      - 'ecr:ListImages'
      - 'ecr:DescribeImages'
      - 'ecr:BatchGetImage'
      - 'ecr:GetLifecyclePolicy'
      - 'ecr:GetLifecyclePolicyPreview'
      - 'ecr:ListTagsForResource'
      - 'ecr:DescribeImageScanFindings'
    resource:
      - '*'
"""
            iam_ctl = self.paco_ctx.get_controller('IAM')
            iam_ctl.add_managed_policy(
                role=resource.instance_iam_role,
                resource=resource,
                policy_name='policy',
                policy_config_yaml=policy_config_yaml,
                extra_ref_names=['ec2lm','ecs'],
            )

            launch_script += f"""
function run_launch_bundle() {{
    echo "EC2LM: ECS: Begin"
    mkdir -p /etc/ecs/
    CLUSTER_NAME=$(ec2lm_instance_tag_value 'Paco-ECSCluster-Name')
    echo ECS_CLUSTER=$CLUSTER_NAME > /etc/ecs/ecs.config
    echo ECS_LOGLEVEL={ecs.log_level} >> /etc/ecs/ecs.config

    # Upgrade the agent
    if [ "$EC2LM_ON_LAUNCH" == "true" ] ; then
        echo "EC2LM: ECS: Upgrade ECS agent if a newer version exists"
        yum update -y ecs-init
        systemctl restart docker
    fi

    # restart the ecs service to reload the new config
    # do not do this on initial launch or ecs just hangs
    if [ "$EC2LM_ON_LAUNCH" == "false" ] ; then
        echo "EC2LM: ECS: Restarting ECS agent"
        systemctl restart ecs.service
    fi
    echo "EC2LM: ECS: End"
}}
"""
        ecs_lb.set_launch_script(launch_script, ecs_enabled)
        self.add_bundle(ecs_lb)

    def lb_add_ssm(self, bundle_name, resource):
        """Creates a launch bundle to install and configure the SSM agent"""
        # Create the Launch Bundle
        ssm_lb = LaunchBundle(resource, self, bundle_name)
        ssm_enabled = True
        if not resource.launch_options.ssm_agent:
            ssm_enabled = False

        # Install SSM Agent - except where it is pre-baked in the image
        download_url = ''
        agent_install = ''
        agent_object = ''
        download_command = 'wget -nv'
        if resource.instance_ami_type_family == 'redhat':
            installed_command = 'rpm -q amazon-ssm-agent'
        elif resource.instance_ami_type_family == 'debian':
            installed_command = 'dpkg --status amazon-ssm-agent'
        if resource.instance_ami_type_generic != 'amazon':
            agent_config = ec2lm_commands.ssm_agent[resource.instance_ami_type]
            agent_install = agent_config["install"]
            agent_object = agent_config["object"]
            if resource.instance_ami_type not in ('ubuntu_16_snap', 'ubuntu_18', 'ubuntu_18_cis', 'ubuntu_20'):            # use regional URL for faster download
                if self.aws_region in ec2lm_commands.ssm_regions:
                    download_url = f'https://s3.{self.aws_region}.amazonaws.com/amazon-ssm-{self.aws_region}/latest'
                else:
                    download_url = f'https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest'
                download_url += f'{agent_config["path"]}/{agent_config["object"]}'
            else:
                installed_command = 'snap list amazon-ssm-agent'
                download_command = ""
                download_url = ""

        launch_script = f"""#!/bin/bash

echo "EC2LM: SSM Agent: Begin"

$({installed_command} &> /dev/null)
if [[ $? -eq 0 ]]; then
    SSM_INSTALLED=true
else
    SSM_INSTALLED=false
fi

echo "EC2LM: SSM Agent: End"

function run_launch_bundle() {{
    if [ "$SSM_INSTALLED" == "false" ] ; then
        # Load EC2 Launch Manager helper functions
        . {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash

        # Download the agent
        LB_DIR=$(pwd)
        mkdir /tmp/paco/
        cd /tmp/paco/
        # ensure wget is installed
        ec2lm_install_wget

        echo "EC2LM: SSM: Downloading agent"
        {download_command} {download_url}

        # Install the agent
        echo "EC2LM: SSM: Installing agent: {agent_install} {agent_object}"
        {agent_install} {agent_object}
    fi
}}

function disable_launch_bundle() {{
    # No-op: Paco will not remove SSM agent
    :
}}
"""
        ssm_lb.set_launch_script(launch_script, ssm_enabled)
        self.add_bundle(ssm_lb)

        if ssm_enabled:
            # Create instance managed policy for the agent
            iam_policy_name = '-'.join([resource.name, 'ssmagent-policy'])
            ssm_prefixed_name = prefixed_name(resource, 'paco_ssm', self.paco_ctx.legacy_flag)
            # allows instance to create a LogGroup with any name - this is a requirement of the SSM Agent
            # if you limit the resource to just the LogGroups names you want SSM to use, the agent will not work
            ssm_log_group_arn = f"arn:aws:logs:{self.aws_region}:{self.account_ctx.id}:log-group:*"
            ssm_log_stream_arn = f"arn:aws:logs:{self.aws_region}:{self.account_ctx.id}:log-group:{ssm_prefixed_name}:log-stream:*"
            ssm_software_inventory_doc_arn = f"arn:aws:ssm:{self.aws_region}::document/AWS-GatherSoftwareInventory"
            policy_config_yaml = f"""
policy_name: '{iam_policy_name}'
enabled: true
statement:
  - effect: Allow
    action:
      - ssmmessages:CreateControlChannel
      - ssmmessages:CreateDataChannel
      - ssmmessages:OpenControlChannel
      - ssmmessages:OpenDataChannel
      - ec2messages:AcknowledgeMessage
      - ec2messages:DeleteMessage
      - ec2messages:FailMessage
      - ec2messages:GetEndpoint
      - ec2messages:GetMessages
      - ec2messages:SendReply
      - ssm:UpdateInstanceInformation
      - ssm:ListInstanceAssociations
      - ssm:DescribeInstanceProperties
      - ssm:DescribeDocumentParameters
      - ssm:UpdateInstanceAssociationStatus
      - ssm:PutInventory
      - ssm:PutComplianceItems
    resource:
      - '*'
  - effect: Allow
    action:
      - ssm:GetDocument
    resource:
      - '{ssm_software_inventory_doc_arn}'

  - effect: Allow
    action:
      - s3:GetEncryptionConfiguration
    resource:
      - '*'
  - effect: Allow
    action:
      - logs:CreateLogGroup
      - logs:CreateLogStream
      - logs:DescribeLogGroups
      - logs:DescribeLogStreams
    resource:
      - {ssm_log_group_arn}
  - effect: Allow
    action:
      - logs:PutLogEvents
    resource:
      - {ssm_log_stream_arn}
"""
            iam_ctl = self.paco_ctx.get_controller('IAM')
            iam_ctl.add_managed_policy(
                role=resource.instance_iam_role,
                resource=resource,
                policy_name='policy',
                policy_config_yaml=policy_config_yaml,
                extra_ref_names=['ec2lm','ssmagent'],
            )

    def lb_scriptmanager_ecr_deploy(self, resource, scripts):

        ecr_deploy_idx = 0
        for ecr_deploy_name in resource.script_manager.ecr_deploy.keys():
            ecr_deploy = resource.script_manager.ecr_deploy[ecr_deploy_name]
            ecr_deploy_name_var = ecr_deploy_name.replace('-', '_')
            ecr_deploy_name_filename = ecr_deploy_name.replace('_', '-')
            ecr_deploy_script = ECR_DEPLOY_SCRIPT_HEAD.format(
                paco_base_path=self.paco_base_path_linux,
                ecr_deploy_list=ecr_deploy_name_var
            )
            repo_idx = 0
            for repository in ecr_deploy.repositories:
                # ECR Deploy Script
                # ECS Relase Phase Script
                source_ecr_obj = get_model_obj_from_ref(repository.source_repo, self.paco_ctx.project)
                source_env = get_parent_by_interface(source_ecr_obj, schemas.IEnvironmentRegion)
                source_account_id = self.paco_ctx.get_ref(source_env.network.aws_account+".id")

                dest_ecr_obj = get_model_obj_from_ref(repository.dest_repo, self.paco_ctx.project)
                dest_env = get_parent_by_interface(dest_ecr_obj, schemas.IEnvironmentRegion)
                dest_account_id = self.paco_ctx.get_ref(dest_env.network.aws_account+".id")

                dest_ecr_obj = get_model_obj_from_ref(repository.dest_repo, self.paco_ctx.project)
                ecr_deploy_script += ECR_DEPLOY_SCRIPT_CONFIG.format(
                    ecr_deploy_name=ecr_deploy_name_var,
                    source_repo_name=source_ecr_obj.full_repository_name,
                    source_repo_domain=f'{source_account_id}.dkr.ecr.{source_env.region}.amazonaws.com',
                    source_repo_account_id=source_account_id,
                    idx=repo_idx,
                    source_tag=repository.source_tag,
                    dest_repo_name=dest_ecr_obj.full_repository_name,
                    dest_repo_domain=f'{dest_account_id}.dkr.ecr.{dest_env.region}.amazonaws.com',
                    dest_tag=repository.dest_tag,
                    release_phase=repository.release_phase
                )
                repo_idx += 1

            if repo_idx > 0:
                ecr_deploy_script += f'\n{ecr_deploy_name_var}_ECR_DEPLOY_LEN={repo_idx}\n'

            if ecr_deploy.release_phase and len(ecr_deploy.release_phase.ecs) > 0:
                # Genreate script
                release_phase_script = RELEASE_PHASE_SCRIPT
                idx = 0
                release_phase_script += f". {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash\n\n"
                for command in ecr_deploy.release_phase.ecs:
                    release_phase_name = command.service.split(' ')[1]
                    release_phase_script += f"""
CLUSTER_ID_{idx}=$(ec2lm_instance_tag_value PACO_CB_RP_ECS_CLUSTER_ID_{idx})
SERVICE_ID_{idx}=$(ec2lm_instance_tag_value PACO_CB_RP_ECS_SERVICE_ID_{idx})
RELEASE_PHASE_NAME_{idx}={release_phase_name}
RELEASE_PHASE_COMMAND_{idx}="{command.command}"
run_release_phase "${{CLUSTER_ID_{idx}}}" "${{SERVICE_ID_{idx}}}" "${{RELEASE_PHASE_NAME_{idx}}}" "${{RELEASE_PHASE_COMMAND_{idx}}}"
"""
                    idx += 1
                scripts[f'ecr_deploy_{ecr_deploy_name_var}_release_phase'] = {
                    'path': f'/usr/local/bin/paco-ecr-deploy-{ecr_deploy_name_filename}-release-phase',
                    'mode': '0755',
                    'owner': 'root',
                    'group': 'root',
                    'data': base64.b64encode(release_phase_script.encode('ascii')).decode('ascii')
                }

                # Create the SSM Document if it does not exist
                ssm_documents = self.paco_ctx.project['resource']['ssm'].ssm_documents
                if 'paco_ecs_docker_exec' not in ssm_documents:
                    ssm_doc = SSMDocument('paco_ecs_docker_exec', ssm_documents)
                    ssm_doc.add_location(self.account_ctx.paco_ref, self.aws_region)
                    ssm_doc.content = json.dumps(RELEASE_PHASE_SCRIPT_SSM_DOCUMENT_CONTENT)
                    ssm_doc.document_type = 'Command'
                    ssm_doc.enabled = True
                    ssm_documents['paco_ecs_docker_exec'] = ssm_doc
                else:
                    ssm_documents['paco_ecs_docker_exec'].add_location(
                        self.account_ctx.paco_ref,
                        self.aws_region,
                    )
            ecr_deploy_idx += 1

            ecr_deploy_script += ECR_DEPLOY_SCRIPT_BODY
            scripts[f'ecr_deploy_{ecr_deploy_name_var}'] = {
                'path': f'/usr/local/bin/paco-ecr-deploy-{ecr_deploy_name_filename}',
                'mode': '0755',
                'owner': 'root',
                'group': 'root',
                'data': base64.b64encode(ecr_deploy_script.encode('ascii')).decode('ascii')
            }

        return scripts

    def lb_scriptmanager_ecs(self, resource, scripts):
        ecs_script = ECS_SCRIPT_HEAD.format(
            paco_base_path=self.paco_base_path_linux,
            ecs_list=' '.join(resource.script_manager.ecs.keys())
        )

        for ecs_name in resource.script_manager.ecs.keys():
            ecs = resource.script_manager.ecs[ecs_name]
            ecs_script += ECS_SCRIPT_CONFIG.format(ecs_name=ecs_name)

        ecs_script += ECS_SCRIPT_BODY
        scripts[f'ecs'] = {
            'path': f'/usr/local/bin/paco-ecs',
            'mode': '0755',
            'owner': 'root',
            'group': 'root',
            'data': base64.b64encode(ecs_script.encode('ascii')).decode('ascii')
        }

        return scripts

    def lb_scriptmanager_custom(self, resource, scripts):
        for script_name in resource.script_manager.custom.keys():
            script = resource.script_manager.custom[script_name]
            content = utils.load_content(script.content)
            scripts[f'custom'] = {
                'path': script.location,
                'mode': script.mode,
                'owner': script.owner,
                'group': script.group,
                'data': base64.b64encode(content.encode('ascii')).decode('ascii')
            }

        return scripts

    def lb_add_scriptmanager(self, bundle_name, resource):
        "EC2 Script Manager Launch Bundle"
        script_lb = LaunchBundle(resource, self, bundle_name)
        launch_script = ""
        scripts = {}
        script_manager_enabled = False
        # ECS Release Phase Script
        if resource.script_manager:
            if resource.script_manager.ecr_deploy and len(resource.script_manager.ecr_deploy) > 0:
                scripts = self.lb_scriptmanager_ecr_deploy(resource, scripts)
            if resource.script_manager.ecs and len(resource.script_manager.ecs) > 0:
                scripts = self.lb_scriptmanager_ecs(resource, scripts)
            if resource.script_manager.custom and len(resource.script_manager.custom) > 0:
                scripts = self.lb_scriptmanager_custom(resource, scripts)



        # Script Manager
        launch_script = f"""#!/bin/bash

. {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash

"""
        idx = 0
        for script_name in scripts.keys():
            launch_script += f"""
declare -a SCRIPTS
SCRIPTS[{idx}]="{script_name}"
{script_name}_DATA="{scripts[script_name]['data']}"
{script_name}_PATH="{scripts[script_name]['path']}"
{script_name}_MODE="{scripts[script_name]['mode']}"
{script_name}_OWNER="{scripts[script_name]['owner']}"
{script_name}_GROUP="{scripts[script_name]['group']}"
"""
            idx += 1

        launch_script += f"""
function run_launch_bundle() {{
    echo "EC2LM: Script Manager: Begin"
    echo "EC2LM: ScriptManager: Installing scripts"
    ec2lm_install_package jq
    for NAME in ${{SCRIPTS[@]}}
    do
        SCRIPT_PATH_VAR=${{NAME}}_PATH
        SCRIPT_DATA_VAR=${{NAME}}_DATA
        SCRIPT_MODE_VAR=${{NAME}}_MODE
        SCRIPT_OWNER_VAR=${{NAME}}_OWNER
        SCRIPT_GROUP_VAR=${{NAME}}_GROUP

        SCRIPT_PATH=${{!SCRIPT_PATH_VAR}}
        SCRIPT_DATA=${{!SCRIPT_DATA_VAR}}
        SCRIPT_MODE=${{!SCRIPT_MODE_VAR}}
        SCRIPT_OWNER=${{!SCRIPT_OWNER_VAR}}
        SCRIPT_GROUP=${{!SCRIPT_GROUP_VAR}}
        if [ -e "${{SCRIPT_PATH}}" ] ; then
            echo "EC2LM: ScriptManager: $NAME: Updating script: ${{SCRIPT_PATH}}"
        else
            echo "EC2LM: ScriptManager: $NAME: Creating script: ${{SCRIPT_PATH}}"
            mkdir -p $(dirname ${{SCRIPT_PATH}})
        fi
        echo ${{SCRIPT_DATA}} | base64 -d >${{SCRIPT_PATH}}
        chmod ${{SCRIPT_MODE}} ${{SCRIPT_PATH}}
        if [ "${{SCRIPT_OWNER}}" != "" ] ; then
            chown ${{SCRIPT_OWNER}} ${{SCRIPT_PATH}}
        fi
        if [ "${{SCRIPT_GROUP}}" != "" ] ; then
            chown :${{SCRIPT_GROUP}} ${{SCRIPT_PATH}}
        fi

    done
    echo "EC2LM: Script Manager: End"
}}

function disable_launch_bundle() {{
    :
}}

"""

        if len(scripts.keys()) > 0:
            script_manager_enabled = True
        script_lb.set_launch_script(launch_script, script_manager_enabled)
        self.add_bundle(script_lb)

    # TODO: Blocked until cftemplates/iam_managed_policies.py supports toposphere
    # and paco.ref Parameters!
    def lb_add_dns(self, bundle_name, resource):
        """Creates a launch bundle to install and configure the DNS agent"""
        # Create the Launch Bundle
        dns_lb = LaunchBundle(resource, self, bundle_name)
        dns_enabled = True
        if len(resource.dns) == 0:
            dns_enabled = False


        launch_script = f"""#!/bin/bash

function set_dns() {{
    INSTANCE_HOSTNAME="$(ec2_metadata hostname)"
    RECORD_SET_FILE=/tmp/internal_record_set.json
    HOSTED_ZONE_ID=$1
    DOMAIN=$2
    cat << EOF >$RECORD_SET_FILE
{{
    "Comment": "API Server",
    "Changes": [ {{
        "Action": "UPSERT",
        "ResourceRecordSet": {{
            "Name": "$DOMAIN",
            "Type": "CNAME",
            "TTL": 60,
            "ResourceRecords": [ {{
                "Value": "$INSTANCE_HOSTNAME"
            }} ]
        }}
    }} ]
}}
EOF
    OUTPUT=$(aws route53 change-resource-record-sets --hosted-zone-id $HOSTED_ZONE_ID --change-batch file://$RECORD_SET_FILE 2>&1)
    RET=$?
    if [ $RET -ne 0 ] ; then
        echo "EC2LM: DNS: ERROR: Unable to set DNS: $HOSTED_ZONE_ID: $DOMAIN -> $INSTANCE_HOSTNAME"
        echo $OUTPUT
    fi
    echo "EC2LM: DNS: $HOSTED_ZONE_ID: $DOMAIN -> $INSTANCE_HOSTNAME"
}}

function run_launch_bundle() {{
    echo "EC2LM: DNS: Begin"
    # Load EC2 Launch Manager helper functions
    . {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash

    NUM_DOMAINS={len(resource.dns)}
    for (( IDX=0; IDX < $NUM_DOMAINS; IDX++))
    do
        HOSTED_ZONE_ID=$(ec2lm_instance_tag_value Paco-DNS-Hosted-Zone-$IDX)
        DOMAIN=$(ec2lm_instance_tag_value Paco-DNS-Domain-$IDX)

        set_dns $HOSTED_ZONE_ID $DOMAIN
    done
    echo "EC2LM: DNS: End"
}}

function disable_launch_bundle() {{
    :
}}
"""

        dns_lb.set_launch_script(launch_script, dns_enabled)
        self.add_bundle(dns_lb)

        if dns_enabled == True:
            hosted_zone_cache = []
            policy_resources = ""
            for dns_config in resource.dns:
                if dns_config.hosted_zone in hosted_zone_cache:
                    continue
                # Create instance managed policy for the agent
                template_params = []
                iam_policy_name = '-'.join([resource.name, 'dns-policy'])
                hostedzone_hash = utils.md5sum(str_data=dns_config.hosted_zone)
                hosted_zone_param_key = 'DNSHostedZoneId' + hostedzone_hash
                param = {
                    'description': 'DNS Hosted Zone ID',
                    'type': 'String',
                    'key': hosted_zone_param_key,
                    'value': dns_config.hosted_zone + '.arn'
                }
                template_params.append(param)
                policy_resources+= f"      - !Ref {hosted_zone_param_key}\n"

            policy_config_yaml = f"""
policy_name: '{iam_policy_name}'
enabled: true
statement:
  - effect: Allow
    action:
      - route53:ChangeResourceRecordSets
    resource:
{policy_resources}
"""
            iam_ctl = self.paco_ctx.get_controller('IAM')
            iam_ctl.add_managed_policy(
                role=resource.instance_iam_role,
                resource=resource,
                policy_name='policy',
                policy_config_yaml=policy_config_yaml,
                template_params=template_params,
                extra_ref_names=['ec2lm','dns'],
            )

    def lb_add_codedeploy(self, bundle_name, resource):
        """Creates a launch bundle to install and configure the CodeDeploy agent"""
        # Create the Launch Bundle
        codedeploy_lb = LaunchBundle(resource, self, bundle_name)
        if resource.instance_ami_type_generic in ['amazon', 'centos']:
            uninstall_command='yum erase codedeploy-agent -y'
            package_exists_command='yum list installed codedeploy-agent >/dev/null 2>&1'
        elif resource.instance_ami_type.startswith("windows") == False:
            uninstall_command='dpkg --purge codedeploy-agent'
            package_exists_command='dpkg -l codedeploy-agent >/dev/null 2>&1'
        else:
            pass

        is_windows = resource.instance_ami_type.startswith("windows")

        if is_windows:
            launch_script = f"""
# Install CodeDeploy
# Set-ExecutionPolicy RemoteSigned
Import-Module AWSPowerShell
New-Item -Path C:\\temp -ItemType Directory -Force
Read-S3Object -BucketName aws-codedeploy-{self.aws_region} -Key latest/codedeploy-agent.msi -File c:\\temp\\codedeploy-agent.msi
c:\\temp\codedeploy-agent.msi /quiet /l c:\\temp\\host-agent-install-log.txt
"""
        else:
            launch_script = f"""#!/bin/bash

CODEDEPLOY_BIN="/opt/codedeploy-agent/bin/codedeploy-agent"
function stop_agent() {{

    if [ ! -e $CODEDEPLOY_BIN ] ; then
        return 0
    fi
    set +e
    TIMEOUT=90
    SLEEP_SECS=10
    T_COUNT=0
    echo "EC2LM: CodeDeploy: Attempting to stop Agent"
    while :
    do
        OUTPUT=$($CODEDEPLOY_BIN stop 2>/dev/null)
        if [ $? -eq 0 ] ; then
            break
        fi
        echo "EC2LM: CodeDeploy: A deployment is in progress, waiting for deployment to complete."
        sleep $SLEEP_SECS
        T_COUNT=$(($T_COUNT+1))
        if [ $T_COUNT -eq $TIMEOUT ] ; then
            echo "EC2LM: CodeDeploy: ERROR: Timeout after $(($TIMEOUT*$SLEEP_SECS)) seconds waiting for deployment to complete."
            exit 1
        fi
    done
    echo "EC2LM: Agent has been stopped."
    set -e
}}

function run_launch_bundle() {{
    echo "EC2LM: CodeDeploy: Agent Install: Begin"
    # Load EC2 Launch Manager helper functions
    . {self.paco_base_path_linux}/EC2Manager/ec2lm_functions.bash

    mkdir -p /root/tmp
    cd /root/tmp/
    ec2lm_install_wget
    ec2lm_install_package ruby
    # Stopping the current agent
    echo "EC2LM: CodeDeploy: Stopping the agent"
    stop_agent

    echo "EC2LM: CodeDeploy: Downloading Agent"
    rm -f install
    wget https://aws-codedeploy-ca-central-1.s3.amazonaws.com/latest/install
    chmod u+x ./install

    echo "EC2LM: CodeDeploy: Installing Agent"
    ./install auto
    stop_agent
    CODEDEPLOY_AGENT_CONF="/etc/codedeploy-agent/conf/codedeployagent.yml"
    grep -v max_revisions $CODEDEPLOY_AGENT_CONF >$CODEDEPLOY_AGENT_CONF.new
    echo ":max_revisions: 1" >>$CODEDEPLOY_AGENT_CONF.new
    mv $CODEDEPLOY_AGENT_CONF.new $CODEDEPLOY_AGENT_CONF
    echo "EC2LM: CodeDeploy: Restarting Agent"
    $CODEDEPLOY_BIN restart
    echo
    echo "EC2LM: CodeDeploy: Agent install complete."

    echo "EC2LM: CodeDeploy: End"
}}

function disable_launch_bundle() {{
    set +e
    {package_exists_command}
    RES=$?
    set -e
    if [ $RES -eq 0 ] ; then
        stop_agent
        {uninstall_command}
    fi
}}
"""
        codedeploy_lb.set_launch_script(launch_script, resource.launch_options.codedeploy_agent, is_windows)
        self.add_bundle(codedeploy_lb)

    def process_bundles(self, resource, instance_iam_role_ref):
        "Initialize launch bundle S3 bucket and iterate through all launch bundles and add every applicable bundle"
        resource._instance_iam_role_arn_ref = 'paco.ref ' + instance_iam_role_ref + '.arn'
        resource._instance_iam_role_arn = self.paco_ctx.get_ref(resource._instance_iam_role_arn_ref)
        if resource._instance_iam_role_arn == None:
            raise StackException(
                    PacoErrorCode.Unknown,
                    message="ec2_launch_manager: user_data_script: Unable to locate value for ref: " + resource._instance_iam_role_arn_ref
                )

        bucket = self.init_ec2lm_s3_bucket(resource)

        if resource.instance_ami_type.startswith("windows") == True:
            bundle_name = 'codedeploy'
            bundle_method = getattr(self, 'lb_add_' + bundle_name.replace('-', '_').lower())
            bundle_method(bundle_name, resource)
        else:
            # EC2LM SSM Document Initialization
            self.add_update_instance_ssm_document()
            self.add_update_system_packages_ssm_command()
            self.add_prepare_create_ami_ssm_command()
            self.add_amazon_live_patching_ssm_command()

            for bundle_name in self.launch_bundle_names:
                bundle_method = getattr(self, 'lb_add_' + bundle_name.replace('-', '_').lower())
                bundle_method(bundle_name, resource)

            # Create CloudWatch Log Groups for SSM and CloudWatch Agent
            if resource.launch_options.ssm_agent or (resource.monitoring != None and resource.monitoring.log_sets):
                self.stack_group.add_new_stack(
                    self.aws_region,
                    resource,
                    paco.cftemplates.LogGroups,
                    change_protected=False,
                    stack_tags=self.stack_tags,
                    support_resource_ref_ext='log_groups',
            )
        return bucket
