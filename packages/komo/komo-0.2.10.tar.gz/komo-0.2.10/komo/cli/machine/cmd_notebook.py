import webbrowser

import click

from komo import printing
from komo.core import get_machine, get_machine_notebook_url
from komo.types import MachineStatus


@click.command("notebook")
@click.argument(
    "machine_name",
    type=str,
)
def cmd_notebook(machine_name: str):
    url = get_machine_notebook_url(machine_name)
    printing.success(f"Opening notebook at {url}")
    webbrowser.open(url)
