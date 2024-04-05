import click

from komo.aws.connect import connect


@click.command("connect")
def cmd_connect():
    connect()
