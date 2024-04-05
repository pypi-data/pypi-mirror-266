import os

import yaml

from komo.constants import PROJECT_FILE_NAME
from komo.types import Cloud


def _set_default(config, key, value):
    if key not in config:
        config[key] = value


def _load_project_config():
    project_file = os.path.join(os.getcwd(), PROJECT_FILE_NAME)
    if os.path.isfile(project_file):
        with open(project_file, "r") as f:
            project_config = yaml.load(f, Loader=yaml.SafeLoader)
            if "cloud" in project_config:
                project_config["cloud"] = Cloud(project_config["cloud"])
    else:
        project_config = {
            # if a project config wasn't provided at all, we assume the cwd should
            # be copied to the workdir
            "workdir": "."
        }

    _set_default(project_config, "resources", {"cpus": "1+"})
    _set_default(project_config, "workdir", None)
    _set_default(project_config, "setup", "")
    _set_default(project_config, "storage", {})

    return project_config
