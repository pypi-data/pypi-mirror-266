import os
import time
from typing import List, Optional

import click

from komo import printing
from komo.core import get_job, print_job_logs, run_command, run_job_file
from komo.types import Cloud, JobStatus


@click.command("run")
@click.option("--num-nodes", type=Optional[int], default=None)
@click.option("--gpus", type=str, default=None)
@click.option("--name", type=str, default=None)
@click.option("--cloud", "-c", type=str, default=None)
@click.option("--detach", "-d", is_flag=True)
@click.argument("args", nargs=-1)
def cmd_run(
    num_nodes: Optional[int],
    gpus: Optional[str],
    name: Optional[str],
    cloud: Optional[str],
    detach: bool,
    args: List[str],
):
    if cloud:
        cloud = Cloud(cloud)

    if len(args) == 1 and os.path.isfile(args[0]):
        job = run_job_file(args[0], num_nodes, gpus, name, cloud)
    else:
        job = run_command(" ".join(args), num_nodes, gpus, name, cloud)

    printing.success(f"Created job {job.name} (ID {job.id})")

    if detach:
        return

    last_message = None
    printing.info("Waiting for job to start...")
    while True:
        job = get_job(job.id)

        should_break = False
        error = False
        if job.status in [JobStatus.PENDING, JobStatus.INITIALIZING]:
            pass
        elif job.status in [
            JobStatus.RUNNING,
            JobStatus.FINISHED,
            JobStatus.SHUTTING_DOWN,
        ]:
            should_break = True
        else:
            printing.error(f"Job status is {job.status.name}")
            should_break = True
            error = True

        if job.status_message and job.status_message != last_message:
            if error:
                printing.error(job.status_message)
            else:
                printing.info(job.status_message)

            last_message = job.status_message

        if should_break:
            break

        time.sleep(2)

    if job.status in [JobStatus.RUNNING, JobStatus.FINISHED, JobStatus.SHUTTING_DOWN]:
        printing.success(f"Job successfully started")

        print_job_logs(job.id, 0, True)
