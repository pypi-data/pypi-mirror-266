from datetime import datetime
from paco import utils
from paco.controllers.controllers import Controller
from paco.controllers.mixins import LambdaDeploy
from paco.core.exception import UnknownSetCommand
from paco.core.yaml import YAML
from paco.models import schemas
from paco.models.locations import get_parent_by_interface
from paco.models.references import Reference
from paco.stack_grps.grp_application import ApplicationStackGroup
from paco.stack_grps.grp_network import NetworkStackGroup
from paco.stack_grps.grp_secretsmanager import SecretsManagerStackGroup
from paco.stack_grps.grp_backup import BackupVaultsStackGroup
from paco.stack import StackTags, StackGroup
import getpass


yaml=YAML(typ="safe", pure=True)
yaml.default_flow_sytle = False


class EnvironmentRegionContext():
    "EnvironmentRegion Controller-ish"

    def __init__(self, paco_ctx, netenv_ctl, netenv, env, env_region):
        self.paco_ctx = paco_ctx
        self.netenv_ctl = netenv_ctl
        self.netenv = netenv
        self.env = env
        self.env_region = env_region
        self.region = env_region.name
        self.network_stack_grp = None
        self.application_stack_grps = {}
        self.iam_stack_grps = {}
        self.stack_grps = []
        self.account_ctx = paco_ctx.get_account_context(
            account_ref=self.env_region.network.aws_account
        )
        self.init_done = False
        self.resource_yaml_filename = "{}-{}-{}.yaml".format(
            self.netenv.name,
            self.env.name,
            self.env_region.name,
        )
        self.resource_yaml_path = self.paco_ctx.outputs_path / 'NetworkEnvironments'
        self.resource_yaml = self.resource_yaml_path / self.resource_yaml_filename
        self.stack_tags = StackTags()
        self.stack_tags.add_tag('paco.netenv.name', self.netenv.name)
        self.stack_tags.add_tag('paco.env.name', self.env.name)

    @property
    def stack_group_filter(self):
        # The stack_group_filter can change so we need to get it from the network environment itself
        return self.netenv_ctl.stack_group_filter

    def init(self):
        if self.init_done:
            return
        self.init_done = True
        self.paco_ctx.log_start('Init', self.env_region)

        # Secrets Manager
        self.secrets_stack_grp = SecretsManagerStackGroup(
            self.paco_ctx,
            self.account_ctx,
            self,
            self.env_region.secrets_manager,
            StackTags(self.stack_tags)
        )
        self.secrets_stack_grp.init()
        self.stack_grps.append(self.secrets_stack_grp)

        # Network Stack: VPC, Subnets, Etc
        self.network_stack_grp = NetworkStackGroup(
            self.paco_ctx,
            self.account_ctx,
            self,
            StackTags(self.stack_tags)
        )
        self.stack_grps.append(self.network_stack_grp)
        self.network_stack_grp.init()

        # Application Engine Stacks
        for app_name in self.ordered_application_names():
            application_stack_grp = ApplicationStackGroup(
                self.paco_ctx,
                self.account_ctx,
                self,
                self.env_region['applications'][app_name],
                StackTags(self.stack_tags)
            )
            self.application_stack_grps[app_name] = application_stack_grp
            self.stack_grps.append(application_stack_grp)
            application_stack_grp.init()

        # Backup
        if self.env_region.backup_vaults:
            self.backup_stack_grp = BackupVaultsStackGroup(
                self.paco_ctx,
                self.account_ctx,
                self,
                self.env_region.backup_vaults,
                StackTags(self.stack_tags)
            )
            self.backup_stack_grp.init()
            self.stack_grps.append(self.backup_stack_grp)

        self.paco_ctx.log_finish('Init', self.env_region)

    def get_aws_name(self):
        aws_name = '-'.join([self.netenv_ctl.get_aws_name(), self.env.name])
        return aws_name

    def get_vpc_stack(self):
        return self.network_stack_grp.get_vpc_stack()

    def ordered_application_names(self):
        "List of application names sorted according to their order"
        ordered_config_list = []
        ordered_id_list = []
        for app_id, app_config in self.env_region['applications'].items():
            new_app_config = [app_id, app_config]
            insert_idx = 0
            for ordered_config in ordered_config_list:
                if app_config.order < ordered_config[1].order:
                    ordered_config_list.insert(insert_idx, new_app_config)
                    ordered_id_list.insert(insert_idx, app_id)
                    break
                insert_idx += 1
            else:
                ordered_config_list.append(new_app_config)
                ordered_id_list.append(app_id)

        return ordered_id_list

    def save_stack_output_config(self):
        merged_config = {}
        for stack_grp in self.stack_grps:
            for stack in stack_grp.stacks:
                if isinstance(stack, StackGroup):
                    continue
                config_dict = stack.output_config_dict
                if config_dict == None:
                    continue
                merged_config = utils.dict_of_dicts_merge(merged_config, config_dict)

        # Save merged_config to yaml file
        if 'netenv' in merged_config.keys():
            utils.write_to_file(
                folder=self.resource_yaml_path,
                filename=self.resource_yaml_filename,
                data= merged_config['netenv'][self.netenv.name][self.env.name][self.env_region.name]
            )

    def validate(self):
        for stack_grp in self.stack_grps:
            stack_grp.validate()

    def provision(self):
        self.paco_ctx.log_start('Provision', self.env_region)
        # provision EC2LM SSM Document first
        if self.env_region.has_ec2lm_resources():
            ssm_ctl = self.paco_ctx.get_controller('SSM')
            ssm_ctl.provision(f'resource.ssm.ssm_documents.paco_ec2lm_update_instance.{self.account_ctx.name}.{self.env_region.name}')
            ssm_ctl.provision(f'resource.ssm.ssm_documents.paco_ec2lm_update_system_packages.{self.account_ctx.name}.{self.env_region.name}')
            ssm_ctl.provision(f'resource.ssm.ssm_documents.paco_ec2lm_prepare_create_ami.{self.account_ctx.name}.{self.env_region.name}')
            ssm_ctl.provision(f'resource.ssm.ssm_documents.paco_ec2lm_amazon_live_patching.{self.account_ctx.name}.{self.env_region.name}')
        if 'paco_ecs_docker_exec' in self.paco_ctx.project['resource']['ssm'].ssm_documents:
            ssm_ctl.provision(f'resource.ssm.ssm_documents.paco_ecs_docker_exec.{self.account_ctx.name}.{self.env_region.name}')
        if len(self.stack_grps) > 0:
            for stack_grp in self.stack_grps:
                stack_grp.provision()
            # self.save_stack_output_config()
        else:
            self.paco_ctx.log_action_col("Provision", "Nothing to provision.")
        self.paco_ctx.log_finish('Provision', self.env_region)

    def delete(self):
        for stack_grp in reversed(self.stack_grps):
            stack_grp.delete()


class NetEnvController(Controller, LambdaDeploy):
    "NetworkEnvironment Controller"

    def __init__(self, paco_ctx):
        super().__init__(paco_ctx, "NE", None)
        self.sub_envs = {}
        self.cur_network_env = None

    def init(self, command=None, model_obj=None):
        # Stack group filter is always set as the netenv controller object is cached and reused.
        # Not setting the filter each time can result in the filter failing
        self.stack_group_filter = model_obj.paco_ref_parts

        # Cache the controller based on the netenv being initialized
        netenv_cache_id = '.'.join(model_obj.paco_ref_parts.split('.', 4)[:3])
        if self.cur_network_env == netenv_cache_id:
            return
        self.cur_network_env = netenv_cache_id

        # Initialize Globals
        self.env = None
        self.env_region = None
        netenv_arg = model_obj.paco_ref_parts
        netenv_parts = netenv_arg.split('.', 4)
        self.netenv = self.paco_ctx.project['netenv'][netenv_parts[1]]
        if self.netenv.name not in self.sub_envs.keys():
            self.sub_envs[self.netenv.name] = {}
        self.env = self.netenv[netenv_parts[2]]
        if len(netenv_parts) > 3:
            self.env_region = self.env[netenv_parts[3]]

        # if no region specified, apply to every region in the environment
        if self.env_region == None:
            regions = [region for region in self.env.env_regions.keys()]
        else:
            regions = [self.env_region.name]

        self.paco_ctx.log_section_start("Init", self.netenv)
        for region in regions:
            self.init_env_region(self.env, region)

    def init_env_region(self, env, region):
        "Initialize an EnvironmentRegion or return an EnvironmentRegionContext if already initialized"

        # SubEnv Cache
        netenv_name = self.netenv.name
        if env.name in self.sub_envs[netenv_name].keys():
            if region in self.sub_envs[netenv_name][env.name].keys():
                return self.sub_envs[netenv_name][env.name][region]
        env_region = self.netenv[env.name][region]
        env_ctx = EnvironmentRegionContext(self.paco_ctx, self, self.netenv, self.env, env_region)
        if env.name not in self.sub_envs[netenv_name]:
            self.sub_envs[netenv_name][env.name] = {}
        self.sub_envs[netenv_name][env.name][region] = env_ctx
        env_ctx.init()

    def add_vpc_stack_hooks(self, stack_hooks):
        "Adds StackHooks to every VPC in the NetEnv"
        for env_name in self.sub_envs[self.netenv.name].keys():
            for region in self.sub_envs[self.netenv.name][env_name].keys():
                vpc_stack = self.sub_envs[self.netenv.name][env_name][region].get_vpc_stack()
                vpc_stack.add_hooks(stack_hooks)

    def secrets_manager(self, secret_name, account_ctx, region):
        print("Modifying secret: " + secret_name)
        secret_string = getpass.getpass("Enter new secret value: ")
        secrets_client = account_ctx.get_aws_client('secretsmanager')
        secrets_client.put_secret_value(
            SecretId=secret_name,
            SecretString=secret_string
        )

    def set_command(self, resource):
        "Set a cloud resource or property"
        secrets_manager = get_parent_by_interface(resource, schemas.ISecretsManager)
        if secrets_manager != None:
            if resource.account == None:
                secret_account = self.env_region.network.aws_account
            else:
                secret_account = resource.account
            account_ctx = self.paco_ctx.get_account_context(account_ref=secret_account)
            secret_name = resource.paco_ref_parts
            self.secrets_manager(secret_name, account_ctx, self.env_region.name)
        else:
            raise UnknownSetCommand(f"Unable to apply set command for resource of type '{resource.__class__.__name__}'\nObject: {resource.paco_ref_parts}")

    # AMI Command
    # Creates an Amazon Machine Image from the selected instance
    # Auto-generates an image name based on the ASG name and appends a version string, v1, v2, etc.
    def ami_command(self, resource):
        asg_ref = Reference(resource.paco_ref)
        asg_name_ref = Reference(resource.paco_ref+'.name')
        asg_name = asg_name_ref.resolve(self.paco_ctx.project, resolve_from_outputs=True)
        account_name = asg_ref.get_account(self.paco_ctx.project).name
        region = asg_ref.region
        account_ctx = self.paco_ctx.get_account_context(account_name=account_name)
        ec2_client = account_ctx.get_aws_client('ec2')
        response = ec2_client.describe_instances(
            Filters=[
                    {
                        'Name': 'tag:aws:autoscaling:groupName',
                        'Values': [
                            asg_name,
                        ]
                    },
                    {
                        'Name': 'instance-state-name',
                        'Values': [
                            'running',
                        ]
                    }
                ]
        )
        if len(response['Reservations']) > 0:
            instance_id = None
            if len(response['Reservations'][0]['Instances']) > 1:
                print("\nMore than one instance exists, please select one:\n")
                idx = 0
                valid = {}
                for instance in response['Reservations'][0]['Instances']:
                    idx += 1
                    print(f"\t{idx}: {instance['InstanceId']}")
                    valid[f"{idx}"] = instance['InstanceId']

                question = f"\nSelect an instance [1-{idx}]: "
                while True:
                    answer = input(question).lower()
                    if answer in valid.keys():
                        break
                    else:
                        print(f"\nERROR: Please respond with a number between 1 and {idx}.")
                instance_id = valid[answer]
            elif len(response['Reservations'][0]['Instances']) == 1:
                instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
            else:
                print(f"There are no instances running in ASG '{asg_name}'.")
                return

            now = datetime.now()
            image_date = now.strftime("%Y-%m-%d")

            image_name_pre_date = f"{asg_name.lower()}"

            response = ec2_client.describe_images(
                Owners=['self'],
                IncludeDeprecated=False
            )

            print(f"\nCreate AMI\n")

            # Gather some info
            image_name_input = utils.enhanced_input(
                prompt=f"Enter an image name, or leave blank to use the default [{image_name_pre_date}]"
            )
            if image_name_input != None:
                image_name_pre_version = f"{image_name_input}-{image_date}"
            else:
                image_name_pre_version = f"{image_name_pre_date}-{image_date}"

            # Get the version
            version = 1
            match_list = []
            for image in response['Images']:
                if image['Name'].startswith(image_name_pre_version):
                    match_list.append(image['Name'])
                    version += 1
            image_name = f"{image_name_pre_version}-v{version}"

            create_image = self.paco_ctx.input_confirm_action(
                question=f"Create image for instance '{instance_id}' named '{image_name}'?"
            )

            if create_image == True:
                # SSM Command to cleanup the instance first
                ctl_ssm = self.paco_ctx.get_controller('ssm')
                ctl_ssm.command_prepare_create_ami(resource, account_ctx, region, 'True')
                # TODO: Make NoReboot and other options configurable
                response = ec2_client.create_image(
                    Name=image_name,
                    InstanceId=instance_id,
                    NoReboot=True,
                    DryRun=False
                )
                print(f"Creating AMI: {response['ImageId']} # {image_name}")
        else:
            print(f"There are no instances running in ASG '{asg_name}'.")
            return

    def patch_command(self, resource):
        asg_ref = Reference(resource.paco_ref)
        asg_name_ref = Reference(resource.paco_ref+'.name')
        asg_name = asg_name_ref.resolve(self.paco_ctx.project, resolve_from_outputs=True)
        account_name = asg_ref.get_account(self.paco_ctx.project).name
        region = asg_ref.region
        account_ctx = self.paco_ctx.get_account_context(account_name=account_name)
        ec2_client = account_ctx.get_aws_client('ec2')
        response = ec2_client.describe_instances(
            Filters=[
                    {
                        'Name': 'tag:aws:autoscaling:groupName',
                        'Values': [
                            asg_name,
                        ]
                    },
                    {
                        'Name': 'instance-state-name',
                        'Values': [
                            'running',
                        ]
                    }
                ]
        )
        if len(response['Reservations']) > 0 and len(response['Reservations'][0]['Instances']) > 0:
            print(f"\nPatching ASG: {asg_name}")
            ctl_ssm = self.paco_ctx.get_controller('ssm')
            ctl_ssm.command_amazon_live_patching(resource, account_ctx, region)
        else:
            print(f"There are no instances running in ASG '{asg_name}'.")
            return

    def validate(self):
        self.paco_ctx.log_start("Validate", self.netenv)
        for env_name in self.sub_envs[self.netenv.name].keys():
            for region in self.sub_envs[self.netenv.name][env_name].keys():
                self.paco_ctx.log_start('Validate', self.netenv[env_name][region])
                self.sub_envs[self.netenv.name][env_name][region].validate()
                self.paco_ctx.log_finish('Validate', self.netenv[env_name][region])
        self.paco_ctx.log_finish("Validate", self.netenv)

    def provision(self):
        self.confirm_yaml_changes(self.netenv)
        self.paco_ctx.log_start("Provision", self.netenv)
        for env_name in self.sub_envs[self.netenv.name].keys():
            for region in self.sub_envs[self.netenv.name][env_name].keys():
                self.sub_envs[self.netenv.name][env_name][region].provision()
        self.apply_model_obj()
        self.paco_ctx.log_finish("Provision", self.netenv)

    def delete(self):
        for env_name in self.sub_envs[self.netenv.name].keys():
            for region in self.sub_envs[self.netenv.name][env_name].keys():
                self.sub_envs[self.netenv.name][env_name][region].delete()

    def get_aws_name(self):
        return '-'.join([super().get_aws_name(), self.netenv.name])
