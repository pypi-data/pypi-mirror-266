import os
import shutil
import subprocess
from typing import List, Optional

import yaml

from komo.api_client import APIClient
from komo.types import Cloud, Job, Machine, MachineStatus
from komo.utils import _load_project_config


def login(api_key: str):
    komo_dir = os.path.expanduser("~/.komo")
    os.makedirs(komo_dir, exist_ok=True)
    api_key_file = os.path.join(komo_dir, "api-key")
    with open(api_key_file, "w") as f:
        f.write(api_key)


def run_command(
    command: str,
    num_nodes: Optional[int] = None,
    gpus: Optional[str] = None,
    name: Optional[str] = None,
    cloud: Optional[Cloud] = None,
):
    """
    Run the given command.
    """
    project_config = _load_project_config()
    api_client = APIClient()

    resources = project_config.get("resources", {})
    if gpus:
        resources["gpus"] = gpus

    if not cloud:
        cloud = project_config.get("cloud", None)

    if num_nodes is None:
        num_nodes = 1

    if not cloud:
        raise Exception("Cloud not provided")

    job = api_client.create_job(
        project_config.get("setup", ""),
        command,
        num_nodes,
        project_config.get("env", {}),
        resources,
        project_config.get("storage", {}),
        project_config.get("workdir", "."),
        cloud=cloud,
        docker_image=project_config.get("docker_image", None),
        name=name,
    )

    return job


def _override_project_config(project_config: dict, job_config: dict, key: str):
    if job_config.get(key, None):
        if key in project_config:
            job_config[key] = project_config[key]


def run_job_file(
    job_file: str,
    num_nodes: Optional[int] = None,
    gpus: Optional[str] = None,
    name: Optional[str] = None,
    cloud: Optional[Cloud] = None,
):
    """
    Run the given job file
    """
    project_config = _load_project_config()
    api_client = APIClient()

    with open(job_file, "r") as f:
        job_config = yaml.safe_load(f)

    for key in [
        "setup",
        "run",
        "num_nodes",
        "env",
        "resources",
        "storage",
        "workdir",
        "cloud",
        "docker_image",
        "name",
    ]:
        _override_project_config(project_config, job_config, key)

    if num_nodes is not None:
        job_config["num_nodes"] = num_nodes

    if gpus is not None:
        job_config["resources"]["gpus"] = gpus

    if name is not None:
        job_config["name"] = name

    if cloud is not None:
        job_config["cloud"] = cloud

    if "run" not in job_config:
        raise Exception("run script not provided")

    if "cloud" not in job_config:
        raise Exception("Cloud not provided")

    job = api_client.create_job(
        job_config.get("setup", ""),
        job_config["run"],
        job_config.get("num_nodes", 1),
        job_config.get("env", {}),
        job_config.get("resources", {}),
        job_config.get("storage", {}),
        job_config.get("workdir", "."),
        job_config["cloud"],
    )

    return job


def list_jobs() -> List[Job]:
    api_client = APIClient()
    jobs = api_client.get_jobs()
    return jobs


def get_job(job_id) -> Job:
    api_client = APIClient()
    job = api_client.get_job(job_id)
    return job


def print_job_logs(job_id, node_index: int = 0, follow: bool = False):
    api_client = APIClient()
    api_client.print_job_logs(job_id, node_index, follow)


def cancel_job(job_id):
    api_client = APIClient()
    api_client.cancel_job(job_id)


def _get_private_ssh_key() -> str:
    api_client = APIClient()
    ssh_key = api_client.get_private_ssh_key()
    return ssh_key


def ssh_job(job_id):
    api_client = APIClient()

    host_info = api_client.get_job_host_info(job_id)
    host_name = host_info["host_name"]
    user = host_info["user"]

    key_file = _get_private_key_file()

    subprocess.call(
        [
            "ssh",
            "-t",
            "-i",
            key_file,
            "-o",
            "IdentitiesOnly=yes",
            f"{user}@{host_name}",
            f"cd ~/sky_workdir; bash --login",
        ]
    )


def create_machine(
    gpus: Optional[str] = None,
    name: Optional[str] = None,
    cloud: Optional[Cloud] = None,
    notebook: bool = False,
):
    api_client = APIClient()
    project_config = _load_project_config()

    machine_config = project_config.copy()
    if gpus:
        machine_config["resources"]["gpus"] = gpus

    if name:
        machine_config["name"] = name

    if cloud:
        machine_config["cloud"] = cloud

    if not machine_config.get("cloud", None):
        raise Exception("No cloud was provided")

    machine = api_client.create_machine(
        machine_config.get("setup", ""),
        machine_config.get("env", {}),
        machine_config.get("resources", {}),
        machine_config.get("storage", {}),
        machine_config.get("workdir", "."),
        machine_config.get("cloud", None),
        machine_config.get("docker_image", None),
        machine_config.get("name", None),
        notebook,
    )

    return machine


def list_machines() -> List[Machine]:
    api_client = APIClient()
    machines: List[Machine] = api_client.get_machines()

    running_machine_names = set(
        [m.name for m in machines if m.status == MachineStatus.RUNNING]
    )
    ssh_dir = os.path.expanduser("~/.komo/ssh")
    os.makedirs(ssh_dir, exist_ok=True)
    for machine_name in os.listdir(ssh_dir):
        if machine_name not in running_machine_names:
            os.remove(os.path.join(ssh_dir, machine_name))

    return machines


def terminate_machine(machine_name: str):
    api_client = APIClient()
    api_client.terminate_machine(machine_name)


def get_machine(machine_name: str) -> Machine:
    api_client = APIClient()
    machine = api_client.get_machine(machine_name)
    return machine


def _get_private_key_file():
    ssh_dir = os.path.expanduser("~/.ssh")
    os.makedirs(ssh_dir, exist_ok=True)
    key_file = os.path.join(ssh_dir, "komodo-key")
    if not os.path.isfile(key_file):
        ssh_key = _get_private_ssh_key()
        with open(key_file, "w") as f:
            f.write(ssh_key)
        os.chmod(key_file, 0o600)

    return key_file


def ssh_machine(job_id):
    api_client = APIClient()

    host_info = api_client.get_machine_host_info(job_id)
    host_name = host_info["host_name"]
    user = host_info["user"]

    key_file = _get_private_key_file()

    subprocess.call(
        [
            "ssh",
            "-t",
            "-i",
            key_file,
            "-o",
            "IdentitiesOnly=yes",
            f"{user}@{host_name}",
            f"cd ~/sky_workdir; bash --login",
        ]
    )


def _setup_ssh_config():
    ssh_config_file = os.path.expanduser("~/.ssh/config")
    include_entry = "Include ~/.komo/ssh/*\n"

    config = ""
    if not os.path.isfile(ssh_config_file):
        os.makedirs(os.path.expanduser("~/.ssh"), exist_ok=True)
    else:
        with open(ssh_config_file, "r") as f:
            config = f.read()

    config = include_entry + config

    with open(ssh_config_file, "w") as f:
        f.write(config)


def open_machine_in_vscode(machine_name):
    _setup_ssh_config()
    api_client = APIClient()

    code = shutil.which("code")
    if code is None:
        raise Exception(
            "Please install the VSCode CLI (https://code.visualstudio.com/docs/editor/command-line)"
        )

    host_info = api_client.get_machine_host_info(machine_name)
    key_file = _get_private_key_file()

    ssh_file = os.path.expanduser(f"~/.komo/ssh/{machine_name}")
    os.makedirs(os.path.expanduser("~/.komo/ssh"), exist_ok=True)

    with open(ssh_file, "w") as f:
        f.write(
            f"Host {machine_name}\n"
            f'\tHostname {host_info["host_name"]}\n'
            f"\tIdentityFile {key_file}\n"
            "\tIdentitiesOnly=yes\n"
            f'\tUser {host_info["user"]}\n'
        )

    subprocess.call(
        [
            "code",
            "--remote",
            f"ssh-remote+{machine_name}",
            f'/home/{host_info["user"]}/sky_workdir',
        ]
    )


def get_machine_notebook_url(machine_name):
    api_client = APIClient()

    machine = api_client.get_machine(machine_name)
    host_info = api_client.get_machine_host_info(machine_name)
    host_name = host_info["host_name"]

    if not host_name.startswith("http"):
        host_name = f"http://{host_name}"

    url = f"{host_name}:8888?token={machine.notebook_token}"
    return url


def print_machine_setup_logs(machine_name: str, follow: bool):
    api_client = APIClient()
    machine = api_client.get_machine(machine_name)
    api_client.print_machine_setup_logs(machine.id, follow)
