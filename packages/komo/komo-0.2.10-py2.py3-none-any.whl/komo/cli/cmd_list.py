import os
from typing import List, Optional

import click
import textwrap3
from tabulate import tabulate

from komo import printing
from komo.core import list_jobs


@click.command("list")
@click.option("--limit", "-l", type=int, default=10)
@click.option("--skip", "-s", type=int, default=0)
def cmd_list(
    limit: int,
    skip: int,
):
    jobs = list_jobs()
    jobs_to_print = [
        [
            job.id,
            job.name,
            job.status.value,
            textwrap3.fill(
                job.status_message,
                width=50,
                replace_whitespace=False,
                drop_whitespace=False,
            ),
        ]
        for job in jobs
    ]

    printing.header(f"Found {len(jobs)} Komodo jobs\n", bold=True)
    printing.info(
        tabulate(
            jobs_to_print,
            headers=[
                "Job ID",
                "Name",
                "Status",
                "Message",
            ],
            tablefmt="simple_grid",
        ),
    )
