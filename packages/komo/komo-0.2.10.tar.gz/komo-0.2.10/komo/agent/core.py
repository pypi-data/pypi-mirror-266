import os
import subprocess
import tempfile
import time

from komo.api_client import APIClient


class Logger:
    _TIME_BETWEEN_LOGS = 1

    def __init__(
        self,
        api_client: APIClient,
        job_or_machine_id: str,
        node_index: int,
        is_machine: bool,
    ):
        self.api_client = api_client
        self.job_or_machine_id = job_or_machine_id
        self.node_index = node_index
        self.buffer = []
        self.last_log_time = None
        self.is_machine = is_machine

    def flush(self):
        if len(self.buffer) == 0:
            return

        try:
            if self.is_machine:
                self.api_client.post_machine_setup_logs(
                    self.job_or_machine_id, self.buffer
                )
            else:
                self.api_client.post_job_logs(
                    self.job_or_machine_id, self.node_index, self.buffer
                )
            self.buffer = []
            self.last_log_time = time.time()
        except:
            # TODO
            pass

    def flush_if_necessary(self):
        curr_time = time.time()

        if (
            not self.last_log_time
            or (curr_time - self.last_log_time) > self._TIME_BETWEEN_LOGS
        ):
            self.flush()

    def log(self, message: str):
        self.flush_if_necessary()

        self.buffer.append(
            {
                "timestamp": int(time.time() * 1000),
                "message": message,
            }
        )

    def __del__(self):
        self.flush()


def _get_node_index():
    node_index = os.environ.get("SKYPILOT_NODE_RANK", 0)
    return node_index


def _execute(
    api_client: APIClient,
    job_or_machine_id: str,
    node_index: int,
    script: str,
    is_machine: bool,
):
    logger = Logger(api_client, job_or_machine_id, node_index, is_machine)

    with tempfile.TemporaryDirectory() as td:
        script_file = os.path.join(td, "script.sh")

        with open(script_file, "w") as f:
            f.write(script)

        proc = subprocess.Popen(
            ["bash", "-l", script_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        for line in proc.stdout:
            logger.log(line.decode("utf-8"))


def setup(job_id: str, setup_script: str):
    api_client = APIClient()
    api_client.mark_job_as_running(job_id)
    node_index = _get_node_index()
    _execute(api_client, job_id, node_index, setup_script, False)


def run(job_id: str, run_script: str):
    api_client = APIClient()
    try:
        api_client.mark_job_as_running(job_id)
        node_index = _get_node_index()
        _execute(api_client, job_id, node_index, run_script, False)
    finally:
        api_client.finish_job(job_id)


def setup_machine(machine_id: str, setup_script: str):
    api_client = APIClient()
    api_client.mark_machine_as_initializing(machine_id)
    _execute(api_client, machine_id, 0, setup_script, True)
    api_client.mark_machine_as_running(machine_id)
