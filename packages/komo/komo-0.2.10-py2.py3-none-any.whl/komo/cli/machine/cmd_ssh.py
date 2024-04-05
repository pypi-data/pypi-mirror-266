import click

from komo import printing
from komo.core import get_machine, ssh_machine
from komo.types import MachineStatus


@click.command("ssh")
@click.argument(
    "machine_name",
    type=str,
)
def cmd_ssh(machine_name: str):
    machine = get_machine(machine_name)
    if machine.status != MachineStatus.RUNNING:
        printing.error(f"Machine {machine_name} is not running")
        exit(1)

    ssh_machine(machine_name)
