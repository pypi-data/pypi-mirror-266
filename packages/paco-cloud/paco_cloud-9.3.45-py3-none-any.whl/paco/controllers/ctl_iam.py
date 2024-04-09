from paco.cftemplates import IAMRoles, IAMManagedPolicies,IAMUsers, IAMUserAccountDelegates, IAMSLRoles, IAMOIDCIdentityProvider
from paco.controllers.controllers import Controller
from paco.core.exception import StackException, InvalidAccountPermission, PacoErrorCode
from paco.core.yaml import YAML
from paco.models.references import Reference
from paco.models.locations import get_parent_by_interface
from paco.models import schemas
from paco.models.base import Named
from paco.stack import StackOrder, StackGroup, StackTags, StackHooks
from paco.utils import md5sum, get_support_resource_ref_ext
from parliament import analyze_policy_string
import paco

yaml=YAML(typ='safe')


class IAMUserStackGroup(StackGroup):
    def __init__(self, paco_ctx, account_ctx, group_name, controller):
        super().__init__(
            paco_ctx,
            account_ctx,
            group_name,
            'User',
            controller
        )

class IAMIdentityProvidersStackGroup(StackGroup):
    def __init__(self, paco_ctx, account_ctx, group_name, controller):
        super().__init__(
            paco_ctx,
            account_ctx,
            group_name,
            'IdentityProviders',
            controller
        )

class IAMRoleStackGroup(StackGroup):
    def __init__(self, paco_ctx, account_ctx, group_name, controller):
        super().__init__(
            paco_ctx,
            account_ctx,
            group_name,
            'Roles',
            controller
        )

class IAMPoliciesStackGroup(StackGroup):
    def __init__(self, paco_ctx, account_ctx, group_name, controller):
        super().__init__(
            paco_ctx,
            account_ctx,
            group_name,
            'Policies',
            controller
        )

class SLRoleContext():
    def __init__(
        self,
        paco_ctx,
        account_ctx,
        region,
        resource,
        stack_group,
        servicename
    ):
        self.paco_ctx = paco_ctx
        self.account_ctx = account_ctx
        self.region = region
        self.stack_group = stack_group
        self.servicename = servicename
        self.resource= resource
        self.sl_role_stack = self.stack_group.add_new_stack(
            self.region,
            self.resource,
            IAMSLRoles,
            account_ctx=self.account_ctx,
            extra_context={'servicename': servicename},
        )
        self.sl_role_stack.singleton = True

    def aws_name(self):
        return self.servicename


class RoleContext():
    def __init__(
        self,
        account_ctx,
        region,
        resource,
        role_id,
        role,
        stack_group,
        stack_tags,
        template_params,
    ):
        self.account_ctx = account_ctx
        self.region = region
        self.resource = resource
        self.role_id = role_id
        self.role = role
        self.role_ref = role.paco_ref_parts
        self.stack_group = stack_group
        self.stack_tags = stack_tags
        self.template_params = template_params
        self.role_name = None
        self.role_template = None
        self.role_stack = None
        self.policy_context = {}

        # Create a Role stack and add it to the StackGroup
        role_stack_tags = StackTags(self.stack_tags)
        role_stack_tags.add_tag('Paco-IAM-Resource-Type', 'Role')

        # set the resolve_ref_obj on the model
        self.role.resolve_ref_obj = self

        # Resources such as a service might not have change_protected
        change_protected = getattr(self.resource, 'change_protected', False)
        role_ext = get_support_resource_ref_ext(self.resource, self.role)

        # Stack Hooks
        self.role_stack = self.stack_group.add_new_stack(
            self.region,
            self.resource,
            IAMRoles,
            account_ctx=self.account_ctx,
            stack_tags=role_stack_tags,
            change_protected=change_protected,
            extra_context={
                'template_params': self.template_params,
                'role': self.role,
            },
            support_resource_ref_ext=role_ext,
        )
        self.role_template = self.role_stack.template
        self.role_name = self.role_template.gen_iam_role_name("Role", self.role)
        self.role_arn = "arn:aws:iam::{0}:role/{1}".format(self.account_ctx.get_id(), self.role_name)
        role_profile_name = self.role_template.gen_iam_role_name("Profile", self.role)
        self.role_profile_arn = "arn:aws:iam::{0}:instance-profile/{1}".format(self.account_ctx.get_id(), role_profile_name)

        # Stack hooks now that we have role_name
        stack_hooks = StackHooks()
        stack_hooks.add(
            name='IAMRoleCleanup',
            stack_action='delete',
            stack_timing='pre',
            hook_method=self.stack_hook_cleanup_policies,
            hook_arg=self.role_name
        )
        self.role_stack.set_hooks(stack_hooks)

    def aws_name(self):
        return self.role.paco_ref_parts

    def get_aws_name(self):
        return self.aws_name()

    def stack_hook_cleanup_policies(self, hook, hook_arg):
        role_name = hook_arg
        iam_client = hook['stack'].account_ctx.get_aws_client('iam')
        try:
            role_policies = iam_client.list_role_policies(
                RoleName=role_name
            )
            attach_role_policies = iam_client.list_attached_role_policies(
                RoleName=role_name
            )
        except iam_client.exceptions.NoSuchEntityException:
            return

        for policy_name in role_policies['PolicyNames']:
            iam_client.delete_role_policy(
                RoleName=role_name,
                PolicyName=policy_name
            )

        for policy in attach_role_policies['AttachedPolicies']:
            try:
                iam_client.detach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy['PolicyArn']
                )
            except Exception as e:
                if e.response['Error']['Code'] != 'NoSuchEntity':
                    raise e

    def add_managed_policy(
        self,
        resource,
        policy_name,
        policy_config_yaml=None,
        template_params=None,
        change_protected=False,
        extra_ref_names=None,
    ):
        "Adds a Managed Policy stack that is attached to this Role"
        # create a Policy object from YAML and add it to the model
        policy_dict = yaml.load(policy_config_yaml)
        policy_dict['roles'] = [self.role_name]
        # extra_ref_names adds extra parts to the Policy paco.ref
        # This is because the paco.ref is used to generate the a Policy hash used in the AWS
        # Policy name. The ref should not change otherwise the Policy names change.
        parent = resource
        for name in extra_ref_names:
            container = Named(name, parent)
            parent = container
        policy = paco.models.iam.ManagedPolicy(policy_name, parent)
        paco.models.loader.apply_attributes_from_config(policy, policy_dict)

        if policy.paco_ref_parts in self.policy_context.keys():
            print(f"Managed policy already exists: {policy.paco_ref_parts}")
            raise StackException(PacoErrorCode.Unknown)

        # set the resolve_ref_obj to this RoleContext
        policy.resolve_ref_obj = self
        policy_context = {
            'id': policy_name,
            'config': policy,
            'ref': policy.paco_ref_parts,
            'template_params': template_params,
        }
        policy_stack_tags = StackTags(self.stack_tags)
        policy_stack_tags.add_tag('Paco-IAM-Resource-Type', 'ManagedPolicy')
        policy_ext = get_support_resource_ref_ext(resource, policy)
        policy_context['stack'] = self.stack_group.add_new_stack(
            self.region,
            resource,
            IAMManagedPolicies,
            stack_tags=policy_stack_tags,
            extra_context={'policy': policy, 'template_params': template_params},
            support_resource_ref_ext=policy_ext
        )
        policy_context['template'] = policy_context['stack'].template
        policy_context['name'] = policy_context['template'].gen_policy_name(policy.name)
        policy_context['arn'] = "arn:aws:iam::{0}:policy/{1}".format(self.account_ctx.get_id(), policy_context['name'])
        self.policy_context[policy.paco_ref_parts] = policy_context

    def get_role_arn(self):
        return self.role_arn

    def resolve_ref(self, ref):
        if ref.ref.startswith(self.role_ref):
            if ref.resource_ref == 'profile.arn':
                return self.role_profile_arn
            elif ref.resource_ref == 'arn':
                return self.role_arn
            elif ref.resource_ref == 'name':
                return self.role_name
        else:
            for policy_ref in self.policy_context.keys():
                if ref.ref.startswith(policy_ref) == False:
                    continue
                if ref.resource_ref == 'arn':
                    return self.policy_context[policy_ref]['arn']
                elif ref.resource_ref == 'name':
                    return self.policy_context[policy_ref]['name']
        return None


class IAMController(Controller):
    def __init__(self, paco_ctx):
        super().__init__(
            paco_ctx,
            "Resource",
            "IAM"
        )
        self.role_context = {}
        self.sl_role_context = {}
        self.policy_context = {}
        self.iam = self.paco_ctx.project['resource']['iam']
        self.iam_user_stack_groups = {}
        self.iam_user_access_keys_sdb_domain = 'Paco-IAM-Users-Access-Keys-Meta'
        self.init_done = False
        self.identity_provider_stacks = []
        self.identity_provider_stack_groups = {}
        self.roles_stack_groups = {}
        self.policies_stack_groups = {}

    # Administrator
    def init_custompolicy_permission(self, permission_config, permissions_by_account):
        """
        Adds each permission config to a map of permissions by account. This map
        is used to determines the policies a user will have created in each
        account.
        """
        accounts = permission_config.accounts
        if 'all' in accounts:
            accounts = self.paco_ctx.project['accounts'].keys()

        for account_name in accounts:
            permissions_by_account[account_name].append(permission_config)

    # CodeCommit
    def init_codecommit_permission(self, permission_config, permissions_by_account):
        for repo_config in permission_config.repositories:
            # Account Delegate Role
            if repo_config.console_access_enabled == True:
                codecommit_config = self.paco_ctx.get_ref(repo_config.codecommit)
                if codecommit_config.is_enabled():
                    account_ref = codecommit_config.account
                    account_name = self.paco_ctx.get_ref(account_ref+'.name')
                    if permission_config not in permissions_by_account[account_name]:
                        permissions_by_account[account_name].append(permission_config)

    # Administrator
    def init_administrator_permission(self, permission_config, permissions_by_account):
        """
        Adds each permission config to a map of permissions by account. This map
        is used to determines the policies a user will have created in each
        account.
        """
        accounts = permission_config.accounts
        if 'all' in accounts:
            accounts = self.paco_ctx.project['accounts'].keys()

        for account_name in accounts:
            permissions_by_account[account_name].append(permission_config)

    # CodeBuild
    def init_codebuild_permission(self, permission_config, permissions_by_account):
        """
        Iterates over each codebuild reference and adds its permission config
        to the map of permissions by account.
        """
        for resource in permission_config.resources:
            codebuild_ref = Reference(resource.codebuild)
            account_ref = 'paco.ref ' + '.'.join(codebuild_ref.parts[:-2]) + '.configuration.account'
            account_ref = self.paco_ctx.get_ref(account_ref)
            account_name = self.paco_ctx.get_ref(account_ref + '.name')
            if permission_config not in permissions_by_account[account_name]:
                permissions_by_account[account_name].append(permission_config)

    # DeploymentPipelines
    def init_deploymentpipelines_permission(self, permission_config, permissions_by_account):
        """
        Iterates over each pipeline reference and adds its permission config
        to the map of permissions by account.
        """
        for resource in permission_config.resources:
            pipeline_ref = Reference(resource.pipeline)
            account_ref = 'paco.ref ' + '.'.join(pipeline_ref.parts) + '.configuration.account'
            account_ref = self.paco_ctx.get_ref(account_ref)
            account_name = self.paco_ctx.get_ref(account_ref + '.name')
            if permission_config not in permissions_by_account[account_name]:
                permissions_by_account[account_name].append(permission_config)


            # Initialize The network environments that we need access into
            pipeline_config = pipeline_ref.get_model_obj(self.paco_ctx.project)
            self.paco_ctx.get_controller(pipeline_ref.parts[0], model_obj=pipeline_config)

            # Some actions in the pipeline might be in different account so we must
            # iterate the pipeline stages and actions and add them too.
            if pipeline_config.deploy == None:
                continue
            for action_name in pipeline_config.deploy.keys():
                action = pipeline_config.deploy[action_name]
                account_name = None
                if action.type == 'CodeDeploy.Deploy':
                    # TODO: Need a CodeDeployPacoService service hook here
                    if action.auto_scaling_group != None:
                        asg_ref = Reference(action.auto_scaling_group)
                        asg_config = asg_ref.get_model_obj(self.paco_ctx.project)
                        account_name = self.paco_ctx.get_ref(asg_config.get_account().paco_ref + '.name')
                if account_name != None:
                    if permission_config not in permissions_by_account[account_name]:
                        permissions_by_account[account_name].append(permission_config)

    # Session Manager Sessions
    def init_systemsmanagersession_permission(self, permission_config, permissions_by_account):
        """
        Iterates over each SystemsManagerSession resource reference and adds its permission config
        to the map of permissions by account.
        """
        for resource_ref in permission_config.resources:
            ref = Reference(resource_ref)
            account_name = ref.get_account(self.paco_ctx.project).name
            if permission_config not in permissions_by_account[account_name]:
                permissions_by_account[account_name].append(permission_config)

    # Acces Keys
    def init_accesskeys_permission(self, permission_config, permissions_by_account):
        """
        Iterates over each AcessKey resource reference and adds its permission config
        to the map of permissions by account.
        """
        if permission_config not in permissions_by_account['master']:
            permissions_by_account['master'].append(permission_config)

    def get_sdb_attribute_value(self, sdb_client, sdb_domain, item_name, attribute_name):
        attributes = sdb_client.get_attributes(
            DomainName=sdb_domain,
            ItemName=item_name,
            AttributeNames=[ attribute_name ],
            ConsistentRead=True
        )
        #print("SDB: Get: {}: {}: {}".format(sdb_domain, item_name, attribute_name))
        if attributes == None or 'Attributes' not in attributes.keys():
            return None

        for attribute in attributes['Attributes']:
            if attribute['Name'] == attribute_name:
                return attribute['Value']
        return None

    def put_sdb_attribute(self, sdb_client, sdb_domain, item_name, attribute_name, value):
        sdb_client.put_attributes(
            DomainName=sdb_domain,
            ItemName=item_name,
            Attributes=[
                {
                    'Name': attribute_name,
                    'Value': str(value),
                    'Replace': True
                }
            ]
        )
        #print("SDB: Put: {}: {}: {}: {}".format(sdb_domain, item_name, attribute_name, str(value)))

    def delete_sdb_attribute(self, sdb_client, sdb_domain, item_name, attribute_name, value):
        sdb_client.delete_attributes(
            DomainName=sdb_domain,
            ItemName=item_name,
            Attributes=[
                {
                    'Name': attribute_name,
                    'Value': str(value)
                }
            ]
        )
        #print("SDB: Delete: {}".format(attribute_name))

    def iam_user_create_access_key(self, username, key_num, key_version, iam_client, sdb_client):
        sdb_item_name = md5sum(str_data=username)
        access_key_meta = iam_client.create_access_key(
            UserName=username
        )
        access_key_id = access_key_meta['AccessKey']['AccessKeyId']
        secret_key = access_key_meta['AccessKey']['SecretAccessKey']
        version_attribute = access_key_meta['AccessKey']['AccessKeyId']+'Version'
        key_num_attribute = access_key_meta['AccessKey']['AccessKeyId']+'KeyNum'

        self.put_sdb_attribute(
            sdb_client,
            self.iam_user_access_keys_sdb_domain,
            sdb_item_name,
            version_attribute,
            key_version
        )
        self.put_sdb_attribute(
            sdb_client,
            self.iam_user_access_keys_sdb_domain,
            sdb_item_name,
            key_num_attribute,
            key_num
        )
        print("{}: Created Access Key {}: Key Id    : {}".format(username, key_num, access_key_id))
        print("{}:                    {}: Secret Key: {}".format(username, key_num, secret_key))

    def iam_user_delete_access_key(self, username, key_config, iam_client, sdb_client):
        access_key_id = key_config['access_key_id']
        sdb_item_name = md5sum(str_data=username)
        iam_client.delete_access_key(
            UserName=username,
            AccessKeyId=access_key_id,
        )
        version_attribute = [access_key_id+'Version', key_config['version']]
        key_num_attribute = [access_key_id+'KeyNum', key_config['key_num']]

        for attribute_conf in [version_attribute, key_num_attribute]:
            self.delete_sdb_attribute(
                sdb_client,
                self.iam_user_access_keys_sdb_domain,
                sdb_item_name,
                attribute_conf[0],
                attribute_conf[1],
            )

        print("{}: Deleted Access Key {}: Key Id    : {}".format(username, key_config['key_num'], access_key_id))

    def iam_user_rotate_access_key(self, username, new_key_version, old_key_config, iam_client, sdb_client):
        key_num = old_key_config['key_num']
        print("{}: Rotating Access Key {}: Begin".format(username, key_num))
        self.iam_user_delete_access_key(username, old_key_config, iam_client, sdb_client)
        self.iam_user_create_access_key(username, key_num, new_key_version, iam_client, sdb_client)
        print("{}: Rotating Access Key {}: End".format(username, key_num))

    def iam_user_enable_access_keys(self, iam_client, user_config):
        keys_meta = iam_client.list_access_keys(
            UserName=user_config.username
        )
        for key_meta in keys_meta['AccessKeyMetadata']:
            if key_meta['Status'] == 'Inactive':
                print("{}: Modifying Access Key Status to: Active: {}".format(user_config.username, key_meta['AccessKeyId']))
                iam_client.update_access_key(
                    UserName=user_config.username,
                    AccessKeyId=key_meta['AccessKeyId'],
                    Status='Active'
                )


    def iam_user_disable_access_keys(self, iam_client, user_config):
        keys_meta = iam_client.list_access_keys(
            UserName=user_config.username
        )
        for key_meta in keys_meta['AccessKeyMetadata']:
            if key_meta['Status'] == 'Active':
                print("{}: Modifying Access Key Status to: Inctive: {}".format(user_config.username, key_meta['AccessKeyId']))
                iam_client.update_access_key(
                    UserName=user_config.username,
                    AccessKeyId=key_meta['AccessKeyId'],
                    Status='Inactive'
                )

    def iam_user_access_keys_hook(self, hook, user_config):
        # Access Keys
        if user_config.is_enabled() == False:
            return
        master_account_ctx = self.paco_ctx.get_account_context(account_ref='paco.ref accounts.master')
        iam_client = master_account_ctx.get_aws_client('iam')
        access_key_config = user_config.programmatic_access
        if access_key_config and access_key_config.enabled == True:
            self.iam_user_enable_access_keys(iam_client, user_config)
            # Create SDB Domain for Account wide access keys
            # Use us-west-2 region as ca-central-1 does not support SDB yet and the
            # region does not mattter here.
            if master_account_ctx.config.region == 'ca-central-1':
                sdb_region = 'us-west-2'
            else:
                sdb_region = master_account_ctx.config.region
            sdb_client = master_account_ctx.get_aws_client('sdb', aws_region=sdb_region)
            sdb_domain = self.iam_user_access_keys_sdb_domain
            sdb_item_name = md5sum(str_data=user_config.username)
            sdb_client.create_domain(
                DomainName=sdb_domain
            )
            # Get list of access keys and load their versions
            keys_meta = iam_client.list_access_keys(
                UserName=user_config.username
            )
            old_keys = {
                '1': None,
                '2': None
            }
            for key_meta in keys_meta['AccessKeyMetadata']:
                key_num = self.get_sdb_attribute_value(sdb_client, sdb_domain, sdb_item_name, key_meta['AccessKeyId']+'KeyNum')
                if key_num == None:
                    print("Creating missing KeyNum Access Key Meta data for: {} + {}".format(user_config.username, key_meta['AccessKeyId']))
                    key_num = str(keys_meta['AccessKeyMetadata'].index(key_meta)+1)
                    self.put_sdb_attribute(
                        sdb_client,
                        sdb_domain,
                        sdb_item_name,
                        key_meta['AccessKeyId']+'KeyNum',
                        key_num
                    )
                key_version = self.get_sdb_attribute_value(sdb_client, sdb_domain, sdb_item_name, key_meta['AccessKeyId']+'Version')
                if key_version == None:
                    print("Creating missing Version Access Key Meta data for: {} + {}".format(user_config.username, key_meta['AccessKeyId']))
                    key_version = getattr(access_key_config, 'access_key_{}_version'.format(key_num))
                    self.put_sdb_attribute(
                        sdb_client,
                        sdb_domain,
                        sdb_item_name,
                        key_meta['AccessKeyId']+'Version',
                        key_version
                    )
                if key_num == None or key_version == None:
                    continue
                key_config = {
                    'access_key_id': key_meta['AccessKeyId'],
                    'version': int(key_version),
                    'key_num': key_num
                }
                if old_keys[key_num] != None:
                    print("Error: Cur keys have already been set.")
                    raise StackException(PacoErrorCode.Unknown, message='Cur keys have already been set')
                old_keys[key_num] = key_config

            # Loop through user configuration and update keys
            for key_num in ['1', '2']:
                new_key_version = getattr(access_key_config, 'access_key_{}_version'.format(key_num))
                if old_keys[key_num] == None and new_key_version > 0:
                    self.iam_user_create_access_key(
                        user_config.username,
                        key_num, new_key_version,
                        iam_client,
                        sdb_client
                    )
                elif old_keys[key_num] != None and new_key_version == 0:
                    self.iam_user_delete_access_key(
                        user_config.username,
                        old_keys[key_num],
                        iam_client,
                        sdb_client
                    )
                elif old_keys[key_num] != None and old_keys[key_num]['version'] != new_key_version:
                    self.iam_user_rotate_access_key(
                        user_config.username,
                        new_key_version,
                        old_keys[key_num],
                        iam_client,
                        sdb_client,
                    )
        else:
            self.iam_user_disable_access_keys(iam_client, user_config)

    def iam_user_access_keys_hook_cache_id(self, hook, user_config):
        cache_data = "AccessKeysCacheId"
        if user_config.programmatic_access != None:
            access_config = user_config.programmatic_access
            cache_data += str(access_config.enabled)
            cache_data += str(access_config.access_key_1_version)
            cache_data += str(access_config.access_key_2_version)

        cache_id = md5sum(str_data=cache_data)
        return cache_id

    def init_users(self, model_obj):
        "Initialize IAM User StackGroups"
        self.init_account_delegate_users()
        self.init_account_users()

    def init_account_users(self):
        for iam_user in self.iam.users.values():
            if iam_user.disable_account_delegates == False:
                continue
            self.iam_user_stack_groups[iam_user.name] = IAMUserStackGroup(self.paco_ctx, self.paco_ctx, iam_user.username, self)
            account_ctx = self.paco_ctx.get_account_context(account_ref=iam_user.account)
            # stack for the IAM User - this only exists in the Master account
            # and delegate roles are provisioned in accounts
            self.iam_user_stack_groups[iam_user.name].add_new_stack(
                account_ctx.config.region,
                iam_user,
                IAMUsers,
                account_ctx=account_ctx
            )


    def init_account_delegate_users(self):
        master_account_ctx = self.paco_ctx.get_account_context(account_ref='paco.ref accounts.master')
        # StackGroup
        for account_name in self.paco_ctx.project['accounts'].keys():
            account_ctx = self.paco_ctx.get_account_context('paco.ref accounts.'+account_name)
            self.iam_user_stack_groups[account_name] = IAMUserStackGroup(self.paco_ctx, account_ctx, account_name, self)

        stack_hooks = StackHooks()
        for user_name in self.iam.users.keys():
            user_config = self.iam.users[user_name]
            if user_config.disable_account_delegates == True:
                continue
            # Stack hooks for managing access keys
            if user_config.programmatic_access.externally_managed == False:
                for hook_action in ['create', 'update']:
                    stack_hooks.add(
                        name='IAMUserAccessKeys',
                        stack_action=hook_action,
                        stack_timing='post',
                        hook_method=self.iam_user_access_keys_hook,
                        cache_method=self.iam_user_access_keys_hook_cache_id,
                        hook_arg=user_config
                )

        # If account_whitelist is not ['all'] then validate that there are no accounts specified
        # in permissions that are not part of the account_whitelist
        for iam_user in self.iam.users.values():
            if iam_user.disable_account_delegates == True:
                continue
            allowed = {}
            for account in iam_user.account_whitelist:
                allowed[account] = None
            # If all accounts are allowed, no need to do this check.
            if 'all' in allowed:
                break
            for permission in iam_user.permissions.values():
                # Some permissions don't have accounts so we ignore them here
                if hasattr(permission, 'accounts') == False:
                    continue
                for account in permission.accounts:
                    if account != 'all' and account not in allowed:
                        raise InvalidAccountPermission(
    f"User {iam_user.name} has permission {permission.name} for account {account} - that account is not granted in that user's account_whitelist."
                        )

        # stack for the IAM User - this only exists in the Master account
        # and delegate roles are provisioned in accounts
        self.iam_user_stack_groups['master'].add_new_stack(
            master_account_ctx.config.region,
            self.iam.users,
            IAMUsers,
            account_ctx=master_account_ctx,
            stack_hooks=stack_hooks,
        )

        for user in self.iam.users.values():
            if user.disable_account_delegates == True:
                continue
            # Build a list of permissions for each account
            permissions_by_account = {}
            # Initialize permission_by_account for all accounts
            for account_name in self.paco_ctx.project['accounts'].keys():
                permissions_by_account[account_name] = []

            for permission_name in user.permissions.keys():
                permission_config = user.permissions[permission_name]
                init_method = getattr(self, "init_{}_permission".format(permission_config.type.lower()))
                init_method(permission_config, permissions_by_account)

            # Give access to accounts the user has explicit access to
            for account_name in self.paco_ctx.project['accounts'].keys():
                account_ctx = self.paco_ctx.get_account_context('paco.ref accounts.' + account_name)
                # IAM User delegate stack
                self.iam_user_stack_groups[account_name].add_new_stack(
                    master_account_ctx.config.region,
                    user,
                    IAMUserAccountDelegates,
                    stack_orders=[StackOrder.PROVISION ,StackOrder.WAITLAST],
                    account_ctx=account_ctx,
                    extra_context={
                        'permissions_list': permissions_by_account[account_name],
                        'account_id': account_ctx.id,
                        'master_account_id': master_account_ctx.id,
                    }
                )

        # Print out the SwitchRole URLs for each user
        for user in self.iam.users.values():
            if user.disable_account_delegates == True:
                continue
            print(f'{user.description} Switch Role URLs')
            for account_name in self.paco_ctx.project['accounts'].keys():
                if account_name not in user.account_whitelist and 'all' not in user.account_whitelist:
                    continue
                account_id = self.paco_ctx.get_account_context(account_name=account_name).id
                print(f'{account_name.capitalize()}:\nhttps://signin.aws.amazon.com/switchrole?account={account_id}&roleName=IAM-User-Account-Delegate-Role-{user.name}')
            print()

    def init_identity_providers(self, model_obj):
        if self.iam.identity_providers == None:
            return
        for provider in self.iam.identity_providers.values():
            if provider.provider_type == 'openid':
                # Create OIDC Provider CFtemplate stack
                for account_ref in provider.accounts:
                    account_ctx = self.paco_ctx.get_account_context(account_ref)
                    if account_ctx.name not in self.identity_provider_stack_groups.keys():
                        provider_stack_group = IAMIdentityProvidersStackGroup(self.paco_ctx, account_ctx, account_ctx.name, self)
                        self.identity_provider_stack_groups[account_ctx.name] = provider_stack_group
                    else:
                        provider_stack_group = self.identity_provider_stack_groups[account_ctx.name]
                    provider_stack = provider_stack_group.add_new_stack(
                        'us-east-1', # IAM is global, default to us-east-1
                        provider,
                        IAMOIDCIdentityProvider,
                        account_ctx=account_ctx,
                    )
                    self.identity_provider_stacks.append(provider_stack)


    def create_managed_policy(
        self,
        account_ctx,
        region,
        policy,
        policy_stack_group,
        template_params=None,
    ):
        "Adds a Managed Policy stack that is attached to this Role"

        if policy.paco_ref_parts in self.policy_context.keys():
            print(f"Managed policy already exists: {policy.paco_ref_parts}")
            raise StackException(PacoErrorCode.Unknown)

        # set the resolve_ref_obj to this RoleContext
        policy.resolve_ref_obj = self
        policy_context = {
            'id': policy.policy_name,
            'config': policy,
            'ref': policy.paco_ref_parts,
            'template_params': template_params,
        }
        policy_stack_tags = StackTags()
        policy_stack_tags.add_tag('Paco-IAM-Resource-Type', 'ManagedPolicy')
        policy_ext = get_support_resource_ref_ext(policy, policy)
        policy_context['stack'] = policy_stack_group.add_new_stack(
            region,
            policy,
            IAMManagedPolicies,
            stack_tags=policy_stack_tags,
            extra_context={'policy': policy, 'template_params': template_params},
            support_resource_ref_ext=policy_ext
        )
        policy_context['template'] = policy_context['stack'].template
        policy_context['name'] = policy_context['template'].gen_policy_name(policy.name)
        policy_context['arn'] = "arn:aws:iam::{0}:policy/{1}".format(account_ctx.get_id(), policy_context['name'])
        self.policy_context[policy.paco_ref_parts] = policy_context

    # resource.iam.roles
    def init_roles(self, model_obj):
        if self.iam.roles == None:
            return
        for role in self.iam.roles.values():
            for account in role.accounts:
                account_ctx = self.paco_ctx.get_account_context(account)
                if account_ctx.name not in self.roles_stack_groups.keys():
                    roles_stack_group = IAMRoleStackGroup(self.paco_ctx, account_ctx, account_ctx.name, self)
                    self.roles_stack_groups[account_ctx.name] = roles_stack_group
                else:
                    roles_stack_group = self.roles_stack_groups[account_ctx.name]
                self.add_role(
                    region='us-east-1',
                    resource=self.iam.roles,
                    role=role,
                    iam_role_id='',
                    stack_group=roles_stack_group,
                    stack_tags=None,
                    account_ctx=account_ctx
                )

    # resource.iam.policies
    def init_policies(self, model_obj):
        if hasattr(self.iam, 'policies') == False or self.iam.policies == None:
            return
        for policy in self.iam.policies.values():
            for account in policy.accounts:
                account_ctx = self.paco_ctx.get_account_context(account)
                if account_ctx.name not in self.policies_stack_groups.keys():
                    policies_stack_group = IAMPoliciesStackGroup(self.paco_ctx, account_ctx, account_ctx.name, self)
                    self.policies_stack_groups[account_ctx.name] = policies_stack_group
                else:
                    policies_stack_group = self.policies_stack_groups[account_ctx.name]

                if policy.policy_name == None:
                    policy.policy_name = policy.paco_ref_parts
                    policy.policy_name = policy.policy_name.replace('.', '-')
                    policy.policy_name = policy.policy_name.replace('_', '-')

                self.create_managed_policy(
                    account_ctx,
                    'us-east-1',
                    policy,
                    policies_stack_group,
                    template_params=None
                )



    def init(self, command=None, model_obj=None):
        "Initialize Controller's StackGroup for resource.iam scope"
        if model_obj == None:
            return
        if self.init_done == True:
            return
        self.init_done = True
        if model_obj.paco_ref_parts.startswith('resource.iam') == False:
            return
        if len(model_obj.paco_ref_list) == 2 or model_obj.paco_ref_list[2] == 'users':
            self.stack_group_filter = model_obj.paco_ref_parts
            self.init_users(model_obj)
        if len(model_obj.paco_ref_list) == 2 or model_obj.paco_ref_list[2] == 'identity_providers':
            self.stack_group_filter = model_obj.paco_ref_parts
            self.init_identity_providers(model_obj)
        if len(model_obj.paco_ref_list) == 2 or model_obj.paco_ref_list[2] == 'roles':
            self.stack_group_filter = model_obj.paco_ref_parts
            self.init_roles(model_obj)
        if len(model_obj.paco_ref_list) == 2 or model_obj.paco_ref_list[2] == 'policies':
            self.stack_group_filter = model_obj.paco_ref_parts
            self.init_policies(model_obj)

    def add_managed_policy(self, role, *args, **kwargs):
        return self.role_context[role.paco_ref_parts].add_managed_policy(*args, **kwargs)

    def add_service_linked_role(
        self,
        paco_ctx,
        account_ctx,
        region,
        stack_group,
        resource,
        servicename
    ):
        "Add a ServiceLinked Role for this account and region if it doesn't already exist"
        # ToDo: Each service-linked role can only be enabled once in each account/region.
        # These roles can be created by different resources, each request to
        # add a SL Role should check if the Role already exists, rather than creating it again
        sl_id = f"{account_ctx.id}-{region}-{servicename}"

        # SericeLinked Role already created/seen
        if sl_id in self.sl_role_context.keys():
            return

        # check if the role already exists
        client = account_ctx.get_aws_client(
            'iam',
            aws_region=region
        )
        roles = client.list_roles(
            PathPrefix=f"/aws-service-role/{servicename}/",
        )
        if len(roles["Roles"]) > 0:
            # cache result
            if sl_id not in self.sl_role_context:
                self.sl_role_context[sl_id] = True
        else:
            self.sl_role_context[sl_id] = SLRoleContext(
                paco_ctx,
                account_ctx,
                region,
                resource,
                stack_group,
                servicename
            )

    def add_role(
        self,
        region,
        resource,
        role,
        iam_role_id,
        stack_group,
        stack_tags=None,
        account_ctx=None,
        template_params=None
    ):
        # resource.iam.roles.vanta-prod-read-only
        if role.paco_ref_parts.startswith('resource.iam.roles'):
            role_ref = f'{role.paco_ref_parts}.{account_ctx.name}'
        else:
            role_ref = role.paco_ref_parts
        # default account_ctx is the StackGroup's account_ctx
        if account_ctx == None:
            account_ctx = stack_group.account_ctx

        if self.paco_ctx.warn:
            # lint all IAM Policies and report on complaints
            for policy in role.policies:
                policy_json = policy.export_as_json()
                policy_analysis = analyze_policy_string(policy_json)

                # Possible Findings:
                # UNKNOWN_ACTION
                # UNKNOWN_PREFIX
                # UNKNOWN_PRINCIPAL
                # UNKNOWN_FEDERATION_SOURCE
                # UNKNOWN_OPERATOR
                # MISMATCHED_TYPE_OPERATION_TO_NULL
                # BAD_PATTERN_FOR_MFA
                # MISMATCHED_TYPE
                # UNKNOWN_CONDITION_FOR_ACTION
                # MALFORMED
                # INVALID_ARN
                # RESOURCE_MISMATCH

                if len(policy_analysis.findings) > 0:
                    print("\nWARNING: Problems detected for IAM Policy for Role named {}.".format(role.name))
                    print("  Role paco.ref     : {}".format(role.paco_ref_parts))
                    resource = get_parent_by_interface(role, schemas.IResource)
                    if resource != None:
                        print("  Role for Resource : {} ({})".format(resource.name, resource.type))
                    for finding in policy_analysis.findings:
                        print("  {} - {}".format(finding.issue, finding.detail))
                        print()
                    print()

        if role_ref not in self.role_context.keys():
            self.role_context[role_ref] = RoleContext(
                account_ctx=account_ctx,
                region=region,
                resource=resource,
                role_id=iam_role_id,
                role=role,
                stack_group=stack_group,
                stack_tags=stack_tags,
                template_params=template_params,
            )
        else:
            print("Role already exists: %s" % (role_ref))
            raise StackException(PacoErrorCode.Unknown)

    def role_arn(self, role_ref):
        role_ref = role_ref.replace('paco.ref ', '')
        return self.role_context[role_ref].role_arn

    def role_profile_arn(self, role_ref):
        role_ref = role_ref.replace('paco.ref ', '')
        return self.role_context[role_ref].role_profile_arn

    def role_name(self, role_ref):
        role_ref = role_ref.replace('paco.ref ', '')
        return self.role_context[role_ref].role_name

    def validate(self):
        # Policies
        for account_name in self.policies_stack_groups.keys():
            self.policies_stack_groups[account_name].validate()

        # Users
        if 'master' in self.iam_user_stack_groups.keys():
            # Master first
            self.iam_user_stack_groups['master'].validate()
            for account_name in self.iam_user_stack_groups.keys():
                if account_name == 'master':
                    continue
                self.iam_user_stack_groups[account_name].validate()

        # Identity Providers
        for account_name in self.identity_provider_stack_groups.keys():
            self.identity_provider_stack_groups[account_name].validate()

        # Roles
        for account_name in self.roles_stack_groups.keys():
            self.roles_stack_groups[account_name].validate()

    def provision(self):

        # Policies
        for account_name in self.policies_stack_groups.keys():
            self.policies_stack_groups[account_name].provision()

        # Master first due to IAM Users needing to be created first
        # before account delegate roles
        if 'master' in self.iam_user_stack_groups.keys():
            self.iam_user_stack_groups['master'].provision()
            for account_name in self.iam_user_stack_groups.keys():
                if account_name == 'master':
                    continue
                self.iam_user_stack_groups[account_name].provision()

        # Identity Providers
        for account_name in self.identity_provider_stack_groups.keys():
            self.identity_provider_stack_groups[account_name].provision()

        # Roles
        for account_name in self.roles_stack_groups.keys():
            self.roles_stack_groups[account_name].provision()

    def delete(self):
        #print("Not doing anything because this deletes all of the users.")
        #print("TODO: Implement a per user delete!")

        # Roles
        for account_name in self.roles_stack_groups.keys():
            self.roles_stack_groups[account_name].delete()

        # Identity Providers
        for account_name in self.identity_provider_stack_groups.keys():
            self.identity_provider_stack_groups[account_name].delete()

        if 'master' in self.iam_user_stack_groups.keys():
            print("\nIAM User delete is unavailable. Please disable users to remove them.")
            return
            # for account_name in self.iam_user_stack_groups.keys():
            #     if account_name == 'master':
            #         continue
            #     self.iam_user_stack_groups[account_name].delete()
            # self.iam_user_stack_groups['master'].delete()

        # Policies
        for account_name in self.policies_stack_groups.keys():
            self.policies_stack_groups[account_name].delete()