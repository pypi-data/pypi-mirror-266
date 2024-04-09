from paco import cftemplates
from paco.application.res_engine import ResourceEngine
from paco.stack import StackHooks
from paco.models.references import Reference


class ECSClusterResourceEngine(ResourceEngine):

    def init_resource(self):
        # Stack hooks now that we have role_name
        stack_hooks = StackHooks()
        stack_hooks.add(
            name='ECSClusterDelete',
            stack_action='delete',
            stack_timing='pre',
            hook_method=self.stack_hook_delete_ecs_services,
            hook_arg=self.resource
        )

        self.stack_group.add_new_stack(
            self.aws_region,
            self.resource,
            cftemplates.ECSCluster,
            stack_tags=self.stack_tags,
            stack_hooks=stack_hooks
        )

    def stack_hook_delete_ecs_services(self, hook, hook_arg):
        cluster = hook_arg
        if cluster.is_enabled()== False:
            return
        ecs_client = hook['stack'].account_ctx.get_aws_client('ecs')
        cluster_arn_ref = Reference(cluster.paco_ref+'.arn')
        cluster_arn = cluster_arn_ref.resolve(self.paco_ctx.project, resolve_from_outputs=True)

        try:
            response = ecs_client.list_services(
                cluster=cluster_arn
            )
        except ecs_client.exceptions.ClusterNotFoundException:
            return
        for service_arn in response['serviceArns']:
            service_name = service_arn.split('service/')[1]
            ecs_client.update_service(
                cluster=cluster_arn,
                service=service_name,
                desiredCount=0,
                deploymentConfiguration = {
                    'maximumPercent': 0
                }
            )
