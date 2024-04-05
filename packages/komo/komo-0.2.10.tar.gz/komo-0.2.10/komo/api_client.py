import json
import os
import shutil
import tempfile
import time
from typing import Dict, List, Optional, Union

import requests

from komo import printing
from komo.types import (ClientException, Cloud, Job, JobStatus, Machine,
                        MachineStatus)

KOMODO_API_URL = os.environ.get("KOMODO_API_URL", "https://api.komodoai.dev")

# refresh JWT token at this interval
TOKEN_REFRESH_INTERVAL = 60 * 60  # 1hr


class APIClient:
    def __init__(self):
        api_key = os.environ.get("KOMODO_API_KEY", None)
        if not api_key:
            api_key_file = os.path.expanduser("~/.komo/api-key")
            if not os.path.isfile(api_key_file):
                raise ClientException(f"{api_key_file} does not exist")

            with open(api_key_file, "r") as f:
                api_key = f.read().strip()

        self.api_key = api_key
        self.refresh_token()

    @classmethod
    def register(cls, email: str, password: str):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = json.dumps(
            {
                "email": email,
                "password": password,
            },
        )

        response = requests.request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/auth/register",
            headers=headers,
            data=payload,
        )
        response.raise_for_status()

    def refresh_token(self):
        response = requests.request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/auth/jwt/api_key/login?api_key={self.api_key}",
        )
        response.raise_for_status()
        auth = response.json()

        self._token = auth["token"]
        self.last_token_refresh_time = time.time()

    @property
    def token(self):
        curr_time = time.time()
        if (curr_time - self.last_token_refresh_time) > TOKEN_REFRESH_INTERVAL:
            self.refresh_token()

        return self._token

    @classmethod
    def get_api_key(cls, email: str, password: str):
        files = {
            "username": (None, email),
            "password": (None, password),
        }

        response = requests.request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/auth/jwt/login",
            files=files,
        )
        response.raise_for_status()
        auth = response.json()

        token, token_type = auth["access_token"], auth["token_type"]

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{token_type} {token}",
        }

        response = requests.request(
            "GET",
            f"{KOMODO_API_URL}/api/v1/auth/jwt/api_key",
            headers=headers,
        )
        response.raise_for_status()
        auth = response.json()

        api_key = auth["api_key"]
        return api_key

    def api_request(
        self,
        method: str,
        url: str,
        files: Dict = None,
        data: Dict = None,
    ) -> Union[Dict, List]:  # Not using | for > 1 return type for < Py 3.10 compat
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        # Generic way to make HTTP requests w/ standard error handling
        # TODO: debug-level info logs?
        response = requests.request(
            method,
            url,
            headers=headers,
            files=files,
            data=data,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Catch HTTP errors like 401, 500 etc.
            text = e.response.text
            try:
                j = e.response.json()
            except requests.exceptions.JSONDecodeError:
                j = None
            if j:
                if "detail" in j:
                    text = j["detail"]
            print(f"Got HTTP Error Code {e.response.status_code}: {text}")
            exit(1)

        retval = response.json()
        return retval

    def get_user_id(self):
        result = self.api_request(
            "GET",
            f"{KOMODO_API_URL}/api/v1/user-id",
        )

        return result["user-id"]

    def connect_aws(self, iam_role_arn):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/aws/connect?iam_role_arn={iam_role_arn}",
        )

    def create_job(
        self,
        setup_script: str,
        run_script: str,
        num_nodes: int,
        env: Dict[str, str],
        resources: dict,
        storage: dict,
        workdir: Optional[str] = None,
        cloud: Optional[Cloud] = None,
        docker_image: Optional[str] = None,
        name: Optional[str] = None,
    ) -> Job:
        payload = {
            "name": name,
            "setup_script": setup_script,
            "run_script": run_script,
            "num_nodes": num_nodes,
            "env": env,
            "resources": resources,
            "storage": storage,
            "cloud": cloud.value,
            "docker_image": docker_image,
        }

        if workdir:
            with tempfile.TemporaryDirectory() as td:
                workdir_zipfile = os.path.join(td, "workdir")
                workdir_zipfile = shutil.make_archive(
                    workdir_zipfile, "zip", workdir, workdir
                )

                upload_info = self.api_request(
                    "GET", f"{KOMODO_API_URL}/api/v1/jobs/upload_info"
                )
                workdir_upload_id = upload_info["upload_id"]
                upload_url = upload_info["url"]
                fields = upload_info["fields"]

                with open(workdir_zipfile, "rb") as f:
                    files = {"file": f}

                    if workdir == ".":
                        workdir_str = "current working directory"
                    else:
                        workdir_str = f"directory {workdir}"
                    printing.info(f"Uploading {workdir_str}")
                    response = requests.request(
                        "POST",
                        url=upload_url,
                        data=fields,
                        files=files,
                    )

                    response.raise_for_status()
                    printing.success(f"Uploaded {workdir_str}")

                payload["workdir_upload_id"] = workdir_upload_id

        payload = json.dumps(payload)
        job_dict = self.api_request(
            "POST", f"{KOMODO_API_URL}/api/v1/jobs", data=payload
        )
        job = Job.from_dict(job_dict)

        return job

    def get_job(self, job_id: str):
        job_dict = self.api_request("GET", f"{KOMODO_API_URL}/api/v1/jobs/{job_id}")
        job = Job.from_dict(job_dict)
        return job

    def get_jobs(self):
        job_dicts = self.api_request("GET", f"{KOMODO_API_URL}/api/v1/jobs")
        jobs = [Job.from_dict(d) for d in job_dicts]
        return jobs

    def _get_log_chunk(
        self,
        job_or_machine_id: str,
        node_index: str,
        next_token: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        is_machine: bool = False,
    ):
        if is_machine:
            url = f"{KOMODO_API_URL}/api/v1/machines/{job_or_machine_id}/setup_logs"
        else:
            url = f"{KOMODO_API_URL}/api/v1/jobs/{job_or_machine_id}/{node_index}/logs"
        if next_token or start_time or end_time:
            url += "?"

        args = []
        if next_token:
            args.append(f"next_token={next_token}")
        if start_time:
            args.append(f"start_time={start_time * 1000}")
        if end_time:
            args.append(f"end_time={end_time * 1000}")

        url += "&".join(args)

        logs = self.api_request("GET", url)

        return logs

    def print_job_logs(self, job_id: str, node_index: int, follow: bool):
        job = self.get_job(job_id)
        if job.status in [JobStatus.PENDING, JobStatus.INITIALIZING]:
            raise Exception(f"Job {job_id} has not started")

        live = (
            job.status == JobStatus.RUNNING
            or job.status
            in [
                JobStatus.CANCELLED,
                JobStatus.CANCELLING,
                JobStatus.FINISHED,
                JobStatus.SHUTTING_DOWN,
            ]
            and (time.time() - job.updated_timestamp) < 30
        )

        # time between server queries, in seconds (so we don't overload the server)
        TIME_BETWEEN_QUERIES = 1
        # the number of seconds after a job finishes to wait before assuming no more logs are coming
        JOB_FINISH_WAIT_TIME = 30
        next_token = None
        job_finished_time = None
        last_query_time = time.time() - TIME_BETWEEN_QUERIES
        end_time = None
        if not follow:
            end_time = int(time.time())
        while True:
            time.sleep(max(TIME_BETWEEN_QUERIES - (time.time() - last_query_time), 0))
            response = self._get_log_chunk(
                job_id, node_index, next_token, end_time=end_time
            )
            last_query_time = time.time()

            for event in response["logs"]:
                printing.info(event["message"])

            if response["next_token"] == next_token:
                # we've reached the end of the currently available logs
                if not follow or not live:
                    break

                job = self.get_job(job_id)
                if job.status != JobStatus.RUNNING:
                    if live:
                        if job_finished_time is None:
                            job_finished_time = time.time()
                        elif (time.time() - job_finished_time) >= JOB_FINISH_WAIT_TIME:
                            break

            next_token = response["next_token"]

    def cancel_job(self, job_id: str):
        self.api_request("POST", f"{KOMODO_API_URL}/api/v1/jobs/{job_id}/cancel")

    def finish_job(self, job_id: str):
        self.api_request("POST", f"{KOMODO_API_URL}/api/v1/jobs/{job_id}/finish")

    def get_private_ssh_key(self) -> str:
        response = self.api_request("GET", f"{KOMODO_API_URL}/api/v1/ssh-key")
        ssh_key = response["ssh-key"]
        return ssh_key

    def get_job_host_info(self, job_id: str):
        host_info = self.api_request(
            "GET", f"{KOMODO_API_URL}/api/v1/jobs/{job_id}/host-info"
        )
        return host_info

    def create_machine(
        self,
        setup_script: str,
        env: Dict[str, str],
        resources: dict,
        storage: dict,
        workdir: Optional[str] = None,
        cloud: Optional[Cloud] = None,
        docker_image: Optional[str] = None,
        name: Optional[str] = None,
        notebook: bool = False,
    ) -> Machine:
        payload = {
            "name": name,
            "setup_script": setup_script,
            "env": env,
            "resources": resources,
            "storage": storage,
            "cloud": cloud.value,
            "docker_image": docker_image,
            "start_notebook": notebook,
        }

        if workdir:
            with tempfile.TemporaryDirectory() as td:
                workdir_zipfile = os.path.join(td, "workdir")
                workdir_zipfile = shutil.make_archive(
                    workdir_zipfile, "zip", workdir, workdir
                )

                upload_info = self.api_request(
                    "GET", f"{KOMODO_API_URL}/api/v1/jobs/upload_info"
                )
                workdir_upload_id = upload_info["upload_id"]
                upload_url = upload_info["url"]
                fields = upload_info["fields"]

                with open(workdir_zipfile, "rb") as f:
                    files = {"file": f}

                    if workdir == ".":
                        workdir_str = "current working directory"
                    else:
                        workdir_str = f"directory {workdir}"
                    printing.info(f"Uploading {workdir_str}")
                    response = requests.request(
                        "POST",
                        url=upload_url,
                        data=fields,
                        files=files,
                    )

                    response.raise_for_status()
                    printing.success(f"Uploaded {workdir_str}")

                payload["workdir_upload_id"] = workdir_upload_id

        payload = json.dumps(payload)
        machine_dict = self.api_request(
            "POST", f"{KOMODO_API_URL}/api/v1/machines", data=payload
        )
        machine = Machine.from_dict(machine_dict)

        return machine

    def get_machines(self) -> List[Machine]:
        machine_dicts = self.api_request("GET", f"{KOMODO_API_URL}/api/v1/machines")
        machines = [Machine.from_dict(d) for d in machine_dicts]
        return machines

    def get_machine(self, machine_name: str, is_name: bool = True) -> Machine:
        machine_dict = self.api_request(
            "GET",
            f"{KOMODO_API_URL}/api/v1/machines/{machine_name}?is_name={str(is_name).lower()}",
        )
        machine = Machine.from_dict(machine_dict)
        return machine

    def terminate_machine(self, machine_name: str):
        self.api_request("DELETE", f"{KOMODO_API_URL}/api/v1/machines/{machine_name}")

    def get_machine_host_info(self, machine_name: str):
        host_info = self.api_request(
            "GET", f"{KOMODO_API_URL}/api/v1/machines/{machine_name}/host-info"
        )
        return host_info

    def mark_job_as_running(self, job_id: str):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/jobs/{job_id}/running",
        )

    def post_job_logs(self, job_id: str, node_index: int, logs: List[Dict[str, str]]):
        payload = json.dumps(
            {
                "logs": logs,
            }
        )
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/jobs/{job_id}/{node_index}/logs",
            data=payload,
        )

    def post_machine_setup_logs(self, machine_id: str, logs: List[Dict[str, str]]):
        payload = json.dumps(
            {
                "logs": logs,
            }
        )
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/machines/{machine_id}/setup_logs",
            data=payload,
        )

    def print_machine_setup_logs(self, machine_id: str, follow: bool):
        machine = self.get_machine(machine_id, is_name=False)
        if machine.status == MachineStatus.PENDING:
            raise Exception(f"Machine {machine_id} has not started")

        live = machine.status == MachineStatus.INITIALIZING

        # time between server queries, in seconds (so we don't overload the server)
        TIME_BETWEEN_QUERIES = 1
        # the number of seconds after a machine finishes setup to wait before assuming no more logs are coming
        MACHINE_FINISH_WAIT_TIME = 30
        next_token = None
        machine_finished_time = None
        last_query_time = time.time() - TIME_BETWEEN_QUERIES
        end_time = None
        if not follow:
            end_time = int(time.time())
        while True:
            time.sleep(max(TIME_BETWEEN_QUERIES - (time.time() - last_query_time), 0))
            response = self._get_log_chunk(
                machine_id,
                0,
                next_token,
                end_time=end_time,
                is_machine=True,
            )
            last_query_time = time.time()

            for event in response["logs"]:
                printing.info(event["message"])

            if response["next_token"] == next_token or not response["next_token"]:
                # we've reached the end of the currently available logs
                if not follow or not live:
                    break

                machine = self.get_machine(machine_id, is_name=False)
                if machine.status != MachineStatus.INITIALIZING:
                    if live:
                        if machine_finished_time is None:
                            machine_finished_time = time.time()
                        elif (
                            time.time() - machine_finished_time
                        ) >= MACHINE_FINISH_WAIT_TIME:
                            break

            next_token = response["next_token"]

    def mark_machine_as_running(self, machine_id: str):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/machines/{machine_id}/running",
        )

    def mark_machine_as_initializing(self, machine_id: str):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/machines/{machine_id}/initializing",
        )
