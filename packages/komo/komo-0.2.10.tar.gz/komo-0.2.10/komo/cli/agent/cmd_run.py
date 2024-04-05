import click

from komo.agent.core import run


@click.command("run")
@click.option("--job-id", type=str, required=True)
@click.option("--script", type=str, required=True)
def cmd_run(
    job_id: str,
    script: str,
):
    run(job_id, script)
