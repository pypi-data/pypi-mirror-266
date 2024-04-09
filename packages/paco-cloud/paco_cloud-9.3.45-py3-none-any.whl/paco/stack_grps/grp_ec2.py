from paco.stack import StackOrder, Stack, StackGroup, StackHooks
import paco.cftemplates
from paco.core.exception import StackException
from paco.core.exception import PacoErrorCode
from paco.utils import md5sum

class EC2StackGroup(StackGroup):
    def __init__(
        self,
        paco_ctx,
        account_ctx,
        aws_region,
        region_config,
        controller
    ):
        super().__init__(
            paco_ctx,
            account_ctx,
            account_ctx.get_name(),
            'Resource',
            controller
        )

        # Initialize config with a deepcopy of the project defaults
        self.stack_list = []
        self.stack_ref_map = {}
        self.account_ctx = account_ctx
        self.aws_region = aws_region
        self.config = region_config

        stack_hooks = StackHooks()
        # CodeCommit Repository
        ec2_eip_stack = self.add_new_stack(
            self.aws_region,
            self.config,
            paco.cftemplates.EIP,
            stack_hooks=stack_hooks
        )
        self.stack_list.append(ec2_eip_stack)
        self.stack_ref_map[self.config.paco_ref_parts] = ec2_eip_stack

    def resolve_ref(self, ref):
        return self.stack_ref_map[ref.ref]

