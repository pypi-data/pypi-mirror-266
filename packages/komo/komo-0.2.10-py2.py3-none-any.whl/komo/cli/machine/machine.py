import click

from komo.cli.machine.cmd_create import cmd_create
from komo.cli.machine.cmd_list import cmd_list
from komo.cli.machine.cmd_notebook import cmd_notebook
from komo.cli.machine.cmd_setup_logs import cmd_setup_logs
from komo.cli.machine.cmd_ssh import cmd_ssh
from komo.cli.machine.cmd_terminate import cmd_terminate
from komo.cli.machine.cmd_vscode import cmd_vscode


@click.group()
def machine():
    pass


machine.add_command(cmd_create)
machine.add_command(cmd_list)
machine.add_command(cmd_terminate)
machine.add_command(cmd_ssh)
machine.add_command(cmd_vscode)
machine.add_command(cmd_setup_logs)
machine.add_command(cmd_notebook)
