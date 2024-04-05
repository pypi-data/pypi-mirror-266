import click

from komo.agent.core import setup


@click.command("setup")
@click.option("--job-id", type=str, required=True)
@click.option("--script", type=str, required=True)
def cmd_setup(
    job_id: str,
    script: str,
):
    setup(job_id, script)
