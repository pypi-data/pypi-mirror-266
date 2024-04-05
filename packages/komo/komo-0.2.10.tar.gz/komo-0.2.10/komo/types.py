from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ClientException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Cloud(Enum):
    AWS = "aws"


class JobStatus(Enum):
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    FINISHED = "finished"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    ERROR = "error"
    UNKNOWN = "unknown"
    NOT_FOUND = "not found"
    UNAUTHORIZED = "unauthorized"
    UNREACHABLE = "unreachable"


class MachineStatus(Enum):
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    TERMINATING = "terminating"
    TERINATED = "terminated"
    ERROR = "error"
    UNKNOWN = "unknown"
    NOT_FOUND = "not found"
    UNAUTHORIZED = "unauthorized"
    UNREACHABLE = "unreachable"


@dataclass
class Job:
    id: str
    name: str
    status: JobStatus
    status_message: str
    setup_script: str
    run_script: str
    num_nodes: int
    env: dict
    resources: dict
    storage: dict
    cloud: Optional[Cloud]
    docker_image: Optional[str]
    created_timestamp: int
    updated_timestamp: int

    @classmethod
    def from_dict(cls, d):
        d["status"] = JobStatus(d["status"])
        if d.get("cloud", None):
            d["cloud"] = Cloud(d["cloud"])

        job = Job(**d)
        return job


@dataclass
class Machine:
    id: str
    name: str
    status: MachineStatus
    status_message: str
    setup_script: str
    env: dict
    resources: dict
    storage: dict
    cloud: Optional[Cloud]
    docker_image: Optional[str]
    notebook_token: Optional[str]

    @classmethod
    def from_dict(cls, d):
        d["status"] = MachineStatus(d["status"])
        if d.get("cloud", None):
            d["cloud"] = Cloud(d["cloud"])

        machine = Machine(**d)
        return machine
