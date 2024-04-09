from paco.stack.botostack import BotoStack
from paco.aws_api.acm import DNSValidatedACMCertClient
import time


class InspectorBotoStack(BotoStack):

    def init(self):
        "Prepare Resource State"
        # self.register_stack_output_config(self.stack_ref + '.arn', 'ViewerCertificateArn')
        self.enabled = self.resource.is_enabled()


    def get_outputs(self):
        "Get all Outputs of a Resource"
        acm_client = DNSValidatedACMCertClient(
            self.account_ctx,
            self.resource.domain_name,
            self.cert_aws_region,
        )
        cert_arn = acm_client.get_certificate_arn()
        return {'ViewerCertificateArn': cert_arn}

    def provision(self):
        """
        Creates a certificate if one does not exists, then adds DNS validation records
        to the Route53 Hosted Zone.
        """
        inspector_client = self.account_ctx.get_aws_client('inspector2')
        if not self.enabled:
            inspector_client.disable(
                accountIds=[self.account_ctx.id],
                resourceTypes=['EC2', 'ECR', 'LAMBDA']
            )
            return

        response = inspector_client.enable(
            accountIds=[self.account_ctx.id],
            resourceTypes=self.resource.resource_types
        )

