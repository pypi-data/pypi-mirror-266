import click

from komo import printing
from komo.core import get_machine, open_machine_in_vscode
from komo.types import MachineStatus


@click.command("vscode")
@click.argument(
    "machine_name",
    type=str,
)
def cmd_vscode(machine_name: str):
    machine = get_machine(machine_name)
    if machine.status != MachineStatus.RUNNING:
        printing.error(f"Machine {machine_name} is not running")
        exit(1)

    open_machine_in_vscode(machine_name)
