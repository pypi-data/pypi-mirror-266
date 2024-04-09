import os, sys
from paco.core.exception import StackException
from paco.core.exception import PacoErrorCode, InvalidPacoScope
from paco.controllers.controllers import Controller
from paco.stack_grps.grp_ec2 import EC2StackGroup
from botocore.exceptions import ClientError, BotoCoreError
from paco.core.yaml import YAML
from paco.models import schemas


yaml=YAML()
yaml.default_flow_sytle = False

class EC2Controller(Controller):
    def __init__(self, paco_ctx):
        super().__init__(
            paco_ctx,
            "Resource",
            "EC2"
        )
        self.init_done = False
        paco_ctx.project['resource']['ec2'].resolve_ref_obj = self
        self.eip_stack_group_map = {}

    def print_keypair(self, keypair, message, sub_entry=False):
        service_name = "keypairs: "
        header = "EC2 Service: "
        if sub_entry == True:
            header = "             "
            service_name_space = ""
            for _ in range(len(service_name)):
                service_name_space += " "
            service_name = service_name_space
        print("%s%s%s: %s" % (header, service_name, keypair.keypair_name, message))

    def init(self, command=None, model_obj=None):
        if self.init_done:
            return
        self.init_done = True
        if command == 'init':
            return

        self.stack_grps = []
        self.stack_grp_map = {}

        # currently EC2.yaml only holds keypairs
        # ToDo: enable resource.ec2.keypairs
        if schemas.IEC2Resource.providedBy(model_obj):
            self.keypairs = model_obj.keypairs.values()
        elif schemas.IEC2KeyPairs.providedBy(model_obj):
            self.keypairs = model_obj.values()
        elif schemas.IEC2KeyPair.providedBy(model_obj):
            self.keypairs = [ model_obj ]
        elif schemas.IVPCEIP.providedBy(model_obj):
            self.keypairs = []
            region = model_obj.__parent__.name
            account_name = model_obj.__parent__.__parent__.name
            self.create_stack_group(account_name, region, model_obj)
        elif model_obj != None:
            raise InvalidPacoScope("Scope of {} not operable.".format(model_obj.paco_ref_parts))
        else:
            self.keypairs = self.paco_ctx.project['resource']['ec2'].keypairs.values()

        for keypair in self.keypairs:
            aws_account_ref = keypair.account
            keypair._account_ctx = self.paco_ctx.get_account_context(account_ref=aws_account_ref)
            keypair._ec2_client = keypair._account_ctx.get_aws_client(
                'ec2',
                aws_region=keypair.region
            )
            try:
                keypair._aws_info = keypair._ec2_client.describe_key_pairs(
                    KeyNames=[keypair.keypair_name]
                )['KeyPairs'][0]
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
                    pass
                else:
                    # TOOD: Make this more verbose
                    raise StackException(PacoErrorCode.Unknown)

        # EIPS
        eips_config = self.paco_ctx.project['resource']['ec2'].eips
        if eips_config != None:
            for account_name in eips_config.keys():
                if 'account_name' not in self.stack_grp_map.keys():
                    self.stack_grp_map[account_name] = {}
                    for region in eips_config[account_name].keys():
                        if region not in self.stack_grp_map[account_name].keys():
                            for eip_config in eips_config[account_name][region].values():
                                self.create_stack_group(account_name, region, eip_config)

    def create_stack_group(self, account_name, region, eip_obj):
        account_ctx = self.paco_ctx.get_account_context(account_name=account_name)
        ec2_stack_group = EC2StackGroup(
            self.paco_ctx,
            account_ctx,
            region,
            eip_obj,
            self
        )
        if account_name not in self.stack_grp_map.keys():
            self.stack_grp_map[account_name] = {}
        if region not in self.stack_grp_map[account_name].keys():
            self.stack_grp_map[account_name][region] = {}
        self.stack_grp_map[account_name][region] = ec2_stack_group
        self.stack_grps.append(ec2_stack_group)
        self.eip_stack_group_map[f'{account_name}-{region}'] = ec2_stack_group

    def validate(self):
        for keypair in self.keypairs:
            if hasattr(keypair, '_aws_info'):
                self.print_keypair(keypair, "Key pair has been previously provisioned.")
                self.print_keypair(keypair, "Fingerprint: %s" % (keypair._aws_info['KeyFingerprint']), sub_entry=True)
            else:
                self.print_keypair(keypair, "Key pair has NOT been provisioned.")
        for stack_group in self.stack_grps:
            stack_group.validate()

    def provision(self):
        for keypair in self.keypairs:
            if hasattr(keypair, '_aws_info'):
                self.print_keypair(keypair, "Key pair already provisioned.")
            else:
                keypair._aws_info = keypair._ec2_client.create_key_pair(KeyName=keypair.keypair_name)
                self.print_keypair(keypair, "Key pair created successfully.")
                self.print_keypair(keypair, "Account: %s" % (keypair._account_ctx.get_name()), sub_entry=True)
                self.print_keypair(keypair, "Region:  %s" % (keypair.region), sub_entry=True)
                self.print_keypair(keypair, "Fingerprint: %s" % (keypair._aws_info['KeyFingerprint']), sub_entry=True)
                self.print_keypair(keypair, "Key: \n%s" % (keypair._aws_info['KeyMaterial']), sub_entry=True)

        for stack_group in self.stack_grps:
            stack_group.provision()

    def delete(self):
        for keypair in self.keypairs:
            if hasattr(keypair, '_aws_info'):
                self.print_keypair(keypair,"Deleting key pair.")
                keypair._ec2_client.delete_key_pair(KeyName=keypair.keypair_name)
                self.print_keypair(keypair, "Delete successful.", sub_entry=True)
            else:
                self.print_keypair(keypair, "Key pair does not exist.")

        for stack_group in self.stack_grps:
            stack_group.delete()

    def resolve_ref(self, ref):
        if ref.parts[2] == 'eips':
            account_name = ref.parts[3]
            region = ref.parts[4]
            return self.eip_stack_group_map[f'{account_name}-{region}'].resolve_ref(ref)
        return None