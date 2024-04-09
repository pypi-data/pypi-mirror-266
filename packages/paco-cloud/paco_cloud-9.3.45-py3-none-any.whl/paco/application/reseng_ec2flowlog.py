from paco import cftemplates
from paco.application.res_engine import ResourceEngine

class EC2FlowLogResourceEngine(ResourceEngine):

    def init_resource(self):
        # EC2 Flow Log
        self.stack_group.add_new_stack(
            self.aws_region,
            self.resource,
            cftemplates.EC2FlowLog,
            stack_tags=self.stack_tags,
            extra_context={
                'role_name_prefix': self.env_ctx.get_aws_name()
            }
        )
