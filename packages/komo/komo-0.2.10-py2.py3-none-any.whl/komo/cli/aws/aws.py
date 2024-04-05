import click

from komo.cli.aws.cmd_connect import cmd_connect


@click.group()
@click.pass_context
def aws(ctx: click.Context):
    pass


aws.add_command(cmd_connect)
