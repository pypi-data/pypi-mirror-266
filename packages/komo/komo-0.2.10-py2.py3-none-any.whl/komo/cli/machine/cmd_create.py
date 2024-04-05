import time
from typing import Optional

import click

from komo import printing
from komo.core import (create_machine, get_machine, get_machine_notebook_url,
                       print_machine_setup_logs)
from komo.types import Cloud, MachineStatus


@click.command("create")
@click.option("--gpus", type=str, default=None)
@click.option("--cloud", "-c", type=str, default=None)
@click.option("--detach", "-d", is_flag=True, default=False)
@click.option("--notebook", is_flag=True, default=False)
@click.argument("name", nargs=1)
def cmd_create(
    gpus: Optional[str],
    cloud: Optional[str],
    detach: bool,
    notebook: bool,
    name: str,
):
    if cloud:
        cloud = Cloud(cloud)
    machine = create_machine(gpus, name, cloud, notebook)
    printing.success(f"Machine {machine.name} successfully created")

    if detach:
        return

    printing.info("Waiting for machine to start...")

    last_messsage = None
    while True:
        machine = get_machine(name)

        should_break = False
        error = False
        if machine.status == MachineStatus.PENDING:
            pass
        elif machine.status in [MachineStatus.INITIALIZING, MachineStatus.RUNNING]:
            should_break = True
        else:
            should_break = True
            error = True

        if machine.status_message and machine.status_message != last_messsage:
            if error:
                printing.error(machine.status_message)
            else:
                printing.info(machine.status_message)

            last_messsage = machine.status_message

        if should_break:
            break

        time.sleep(5)

    print_machine_setup_logs(machine.name, True)

    machine = get_machine(name)
    while machine.status == MachineStatus.INITIALIZING:
        time.sleep(5)
        machine = get_machine(name)

    if machine.status == MachineStatus.RUNNING:
        printing.success(f"Machine {name} successfully created")

        if machine.notebook_token:
            url = get_machine_notebook_url(machine.name)
            printing.info(f"Open this link to access the notebook: {url}")
    else:
        printing.error(
            f"Machine {name} has status {machine.status.value} with the following message:\n{machine.status_message}"
        )
