import paco.models
import click
import sys
from paco.commands.helpers import (
    paco_home_option, init_paco_home_option, pass_paco_context,
    handle_exceptions, cloud_options, init_cloud_command, cloud_args, config_types
)
from paco.core.exception import StackException


@click.command(name='patch', short_help='Patch kernel and packages on EC2 Amazon Linux instances of ASG resources.')
@paco_home_option
@cloud_args
@cloud_options
@pass_paco_context
@handle_exceptions
def patch_command(
    paco_ctx,
    verbose,
    nocache,
    yes,
    warn,
    disable_validation,
    quiet_changes_only,
    hooks_only,
    cfn_lint,
    alarms_only,
    config_scope,
    home='.',
):
    """Patch kernel and packages on EC2 Amazon Linux instances of ASG resources"""
    command = 'patch'
    controller_type, obj = init_cloud_command(
        command,
        paco_ctx,
        verbose,
        nocache,
        yes,
        warn,
        disable_validation,
        quiet_changes_only,
        hooks_only,
        cfn_lint,
        alarms_only,
        config_scope,
        home
    )
    controller = paco_ctx.get_controller(controller_type, command, obj)
    controller.patch_command(obj)

patch_command.help = """
Patch kernel and packages on EC2 Amazon Linux instances of ASG resources.

""" + config_types
