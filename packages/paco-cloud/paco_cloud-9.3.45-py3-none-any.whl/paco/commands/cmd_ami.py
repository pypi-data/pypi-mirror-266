import paco.models
import click
import sys
from paco.commands.helpers import (
    paco_home_option, init_paco_home_option, pass_paco_context,
    handle_exceptions, cloud_options, init_cloud_command, cloud_args, config_types
)
from paco.core.exception import StackException


@click.command(name='ami', short_help='Manage EC2 Amazon Machine Images of ASG resources.')
@paco_home_option
@cloud_args
@cloud_options
@pass_paco_context
@handle_exceptions
def ami_command(
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
    """Manage EC2 Amazon Machine Images of ASG resources"""
    command = 'ami'
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
    controller.ami_command(obj)

ami_command.help = """
Manage EC2 Amazon Machine Images of ASG resources.

""" + config_types
