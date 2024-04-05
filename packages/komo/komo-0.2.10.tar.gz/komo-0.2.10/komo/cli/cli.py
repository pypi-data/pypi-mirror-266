import os

import click

from komo.cli.agent.agent import agent
from komo.cli.aws.aws import aws
from komo.cli.cmd_cancel import cmd_cancel
from komo.cli.cmd_list import cmd_list
from komo.cli.cmd_login import cmd_login
from komo.cli.cmd_logs import cmd_logs
from komo.cli.cmd_run import cmd_run
from komo.cli.cmd_ssh import cmd_ssh
from komo.cli.machine.machine import machine


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    ctx.ensure_object(dict)


cli.add_command(cmd_run)
cli.add_command(cmd_list)
cli.add_command(cmd_logs)
cli.add_command(cmd_login)
cli.add_command(cmd_cancel)
cli.add_command(cmd_ssh)
cli.add_command(aws)
cli.add_command(machine)

# agent is not to be used by the user, but only but running komodo workflows
if os.environ.get("__KOMODO_INTERNAL_AGENT__", None):
    cli.add_command(agent)
