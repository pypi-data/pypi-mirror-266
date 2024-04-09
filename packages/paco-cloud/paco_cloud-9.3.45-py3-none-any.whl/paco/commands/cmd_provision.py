import click
from paco.commands.helpers import paco_home_option, pass_paco_context, handle_exceptions, \
    cloud_options, init_cloud_command, cloud_args, config_types


@click.command(name='provision', short_help='Provision resources to the cloud.')
@click.option(
    '--auto-publish-code',
    default=False,
    is_flag=True,
    help="""
Automatically update Lambda Code assets. Lambda resources that use the `zipfile:` to a local filesystem path will automatically publish new code if it differs from the currently published code asset.
"""
)
@click.option(
    '--ssm',
    is_flag=False,
    flag_value=None,
    help="""
Run a Paco SSM command on each instance that is in the provisioning filter.
"""
)
@paco_home_option
@cloud_args
@cloud_options
@pass_paco_context
@handle_exceptions
def provision_command(
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
    auto_publish_code=False,
    ssm=None
):
    """Provision Cloud Resources"""
    paco_ctx.auto_publish_code = auto_publish_code
    paco_ctx.ssm_command = ssm

    valid_ssm_commands = ['update-packages']
    if ssm != None:
        if ssm not in valid_ssm_commands:
            valid_commands_str = ' | '.join(valid_ssm_commands)
            print(f"ERROR: Invalid SSM command: {ssm}\n")
            print(f"Valid commands are: {valid_commands_str}")
            return

    command = 'provision'
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
    controller.provision()

provision_command.help = """
Provision Cloud Resources.

""" + config_types