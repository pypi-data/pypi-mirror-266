from paco import utils
from paco.cftemplates.cftemplates import StackTemplate
from paco.models import schemas
import troposphere
import troposphere.appconfig




class AppConfigApplication(StackTemplate):

    def __init__(self, stack, paco_ctx):
        config = stack.resource
        config_ref = config.paco_ref_parts
        super().__init__(stack, paco_ctx)
        self.set_aws_name(None, 'application', self.resource.name)

        # Troposphere Template Initialization

        # Application
        self.init_template('AppConfig Application')
        app_config_dict = {
            'Name': config.name,
        }
        app_res = troposphere.appconfig.Application.from_dict(
            'Application',
            app_config_dict)
        self.template.add_resource(app_res)

        self.create_output(
            title='Applicationid',
            description="The AppConfig Applciation id",
            value=troposphere.Ref(app_res),
            ref=config_ref + ".id"
        )

        # Profiles
        for profile_config in config.profiles.values():
            profile_config_dict = {
                'ApplicationId': troposphere.Ref(app_res),
                'LocationUri': 'hosted',
                'Name': profile_config.name
            }
            profile_cf_name = self.create_cfn_logical_id_join(
                str_list=['ConfigurationProfile', profile_config.name],
                camel_case=True)
            profile_res = troposphere.appconfig.ConfigurationProfile.from_dict(
                profile_cf_name,
                profile_config_dict
            )
            profile_res.DependsOn = app_res
            self.template.add_resource(profile_res)

        # Environments
        for env_config in config.environments.values():
            env_config_dict = {
                'ApplicationId': troposphere.Ref(app_res),
                'Name': env_config.name
            }
            env_cf_name = self.create_cfn_logical_id_join(
                str_list=['Environment', env_config.name],
                camel_case=True)
            env_res = troposphere.appconfig.Environment.from_dict(
                env_cf_name,
                env_config_dict
            )
            env_res.DependsOn = app_res
            self.template.add_resource(env_res)
