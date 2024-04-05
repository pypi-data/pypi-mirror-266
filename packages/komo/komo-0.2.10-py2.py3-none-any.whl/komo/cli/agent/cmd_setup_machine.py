import click

from komo.agent.core import setup_machine


@click.command("setup-machine")
@click.option("--machine-id", type=str, required=True)
@click.option("--script", type=str, required=True)
def cmd_setup_machine(
    machine_id: str,
    script: str,
):
    setup_machine(machine_id, script)
