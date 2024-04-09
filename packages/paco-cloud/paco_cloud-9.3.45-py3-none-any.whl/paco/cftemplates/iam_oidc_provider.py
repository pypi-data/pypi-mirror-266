from paco.cftemplates.cftemplates import StackTemplate
import troposphere.iam


class IAMOIDCIdentityProvider(StackTemplate):
    def __init__(self, stack, paco_ctx):

        super().__init__(
            stack,
            paco_ctx,
            iam_capabilities=["CAPABILITY_NAMED_IAM"],
        )
        # config_ref = 'resource.iam.identity_providers' + '.' + self.resource.name
        self.set_aws_name(self.resource.provider_type.capitalize(), self.resource.name)

        # Troposphere Template Generation
        self.init_template(f'IAM {self.resource.name.upper()} Identity Provider: {self.resource.name}')

        # Resource
        if self.resource.provider_type == 'openid':
            # TODO: Calculate this automatically
            if self.resource.provider == 'token.actions.githubusercontent.com':
                thumbprints = [ '6938fd4d98bab03faadb97b34396831e3780aea1', '1c58a3a8518e8759bf075b76b750d4f2df264fcd' ]
            else:
                raise
            provider = troposphere.iam.OIDCProvider(
                'OIDCProvider',
                template=self.template,
                ClientIdList=self.resource.audiences,
                ThumbprintList=thumbprints,
                Url=f'https://{self.resource.provider}'
            )
            self.create_output(
                title='OIDCProviderArn',
                value=troposphere.Ref(provider),
                ref=self.resource.paco_ref_parts+'.arn'
            )

        # All Done
        self.set_template()
