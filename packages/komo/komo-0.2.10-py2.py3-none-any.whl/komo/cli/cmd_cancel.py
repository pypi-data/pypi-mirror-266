import click

from komo import printing
from komo.core import cancel_job


@click.command("cancel")
@click.argument(
    "job_id",
    type=str,
)
def cmd_cancel(job_id: str):
    cancel_job(job_id)
    printing.success(f"Job {job_id} is being cancelled")
