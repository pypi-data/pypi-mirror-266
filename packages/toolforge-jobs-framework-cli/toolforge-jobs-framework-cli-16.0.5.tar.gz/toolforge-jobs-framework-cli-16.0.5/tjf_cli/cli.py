# (C) 2021 by Arturo Borrero Gonzalez <aborrero@wikimedia.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is the command line interface part of the Toolforge Jobs Framework.
#
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from os import environ
from pathlib import Path
from tabulate import tabulate
from typing import List, Optional, Set, Any
import textwrap
import argparse
import getpass
import urllib3
import logging
import socket
import time
import yaml
import sys

from toolforge_weld.api_client import ToolforgeClient
from toolforge_weld.config import Section, load_config
from toolforge_weld.kubernetes import MountOption
from toolforge_weld.kubernetes_config import Kubeconfig

from tjf_cli.api import TjfCliHttpUserError, TjfCliConfigLoadError, handle_http_exception
from tjf_cli.errors import TjfCliError, TjfCliUserError, print_error_context
from tjf_cli.loader import calculate_changes

# TODO: disable this for now, review later
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# for --wait: 10 minutes default timeout, check every 5 seconds
DEFAULT_WAIT_TIMEOUT = 60 * 10
WAIT_SLEEP = 5
# deletion timeout when replacing a job with load: 5 minutes
# TODO: this can be lowered once job deletion is faster (T352874)
DELETE_WAIT_TIMEOUT = 5 * 60

# link is to https://wikitech.wikimedia.org/wiki/Help:Cloud_Services_communication
REPORT_MESSAGE = "Please report this issue to the Toolforge admins: https://w.wiki/6Zuu"

EXIT_USER_ERROR = 1
EXIT_INTERNAL_ERROR = 2


JOB_TABULATION_HEADERS_SHORT = {
    "name": "Job name:",
    "type": "Job type:",
    "status_short": "Status:",
}

JOB_TABULATION_HEADERS_LONG = {
    "name": "Job name:",
    "cmd": "Command:",
    "type": "Job type:",
    "image": "Image:",
    "filelog": "File log:",
    "filelog_stdout": "Output log:",
    "filelog_stderr": "Error log:",
    "emails": "Emails:",
    "resources": "Resources:",
    "mount": "Mounts:",
    "retry": "Retry:",
    "health_check": "Health check:",
    "status_short": "Status:",
    "status_long": "Hints:",
}

IMAGES_TABULATION_HEADERS = {
    "shortname": "Short name",
    "image": "Container image URL",
}

RUN_ARGS = {
    "name": {
        "args": ["name"],
        "kwargs": {"help": "new job name"},
    },
    "command": {
        "args": ["--command"],
        "kwargs": {"required": True, "help": "full path of command to run in this job"},
    },
    "image": {
        "args": ["--image"],
        "kwargs": {"required": True, "help": "image shortname (check them with `images`)"},
    },
    "no-filelog": {
        "args": ["--no-filelog"],
        "kwargs": {
            "dest": "filelog",
            "action": "store_false",
            "default": None,
            "required": False,
            "help": "disable redirecting job output to files in the home directory",
        },
    },
    "filelog": {
        "args": ["--filelog"],
        "kwargs": {
            "action": "store_true",
            "required": False,
            "default": None,
            "help": "explicitly enable file logs on jobs using a build service created image",
        },
    },
    "filelog-stdout": {
        "args": ["-o", "--filelog-stdout"],
        "kwargs": {"required": False, "help": "location to store stdout logs for this job"},
    },
    "filelog-stderr": {
        "args": ["-e", "--filelog-stderr"],
        "kwargs": {"required": False, "help": "location to store stderr logs for this job"},
    },
    "retry": {
        "args": ["--retry"],
        "kwargs": {
            "required": False,
            "choices": [0, 1, 2, 3, 4, 5],
            "default": 0,
            "type": int,
            "help": "specify the retry policy of failed jobs.",
        },
    },
    "mem": {
        "args": ["--mem"],
        "kwargs": {
            "required": False,
            "help": "specify additional memory limit required for this job",
        },
    },
    "cpu": {
        "args": ["--cpu"],
        "kwargs": {
            "required": False,
            "help": "specify additional CPU limit required for this job",
        },
    },
    "emails": {
        "args": ["--emails"],
        "kwargs": {
            "required": False,
            "choices": ["none", "all", "onfinish", "onfailure"],
            "default": "none",
            "help": (
                "specify if the system should email notifications about this job. "
                "(default: '%(default)s')"
            ),
        },
    },
    "mount": {
        "args": ["--mount"],
        "kwargs": {
            "required": False,
            "type": MountOption.parse,
            "choices": list(MountOption),
            "help": (
                "specify which shared storage (NFS) directories to mount to this job. "
                "(default: 'none' on build service images, 'all' otherwise)"
            ),
        },
    },
    "schedule": {
        "args": ["--schedule"],
        "kwargs": {
            "required": False,
            "help": "run a job with a cron-like schedule (example '1 * * * *')",
        },
    },
    "continuous": {
        "args": ["--continuous"],
        "kwargs": {"required": False, "action": "store_true", "help": "run a continuous job"},
    },
    "wait": {
        "args": ["--wait"],
        "kwargs": {
            "required": False,
            "nargs": "?",
            "const": DEFAULT_WAIT_TIMEOUT,
            "type": int,
            "help": (
                "wait for job one-off job to complete, "
                f"optionally specify a value to override default timeout of {DEFAULT_WAIT_TIMEOUT}s"
            ),
        },
    },
    "health-check-script": {
        "args": ["--health-check-script"],
        "kwargs": {
            "required": False,
            "default": None,
            "help": "specify a health check command to run on the job if any.",
        },
    },
}


@dataclass
class JobsConfig(Section):
    _NAME_: str = field(default="jobs", init=False)
    jobs_endpoint: str = "/jobs/api/v1"
    timeout: int = 30

    @classmethod
    def from_dict(cls, my_dict: dict[str, Any]):
        params = {}
        if "jobs_endpoint" in my_dict:
            params["jobs_endpoint"] = my_dict["jobs_endpoint"]
        if "timeout" in my_dict:
            params["timeout"] = my_dict["timeout"]
        return cls(**params)


class ListDisplayMode(Enum):
    NORMAL = "normal"
    LONG = "long"
    NAME = "name"

    def display_header(self) -> bool:
        """Whether to display the table headers."""
        return self != ListDisplayMode.NAME

    def __str__(self) -> str:
        """Needed to play nice with argparse."""
        return self.value


def arg_parser():
    toolforge_cli_in_use = "TOOLFORGE_CLI" in environ
    toolforge_cli_debug = environ.get("TOOLFORGE_DEBUG", "0") == "1"

    description = "Toolforge Jobs Framework, command line interface"
    parser = argparse.ArgumentParser(
        description=description,
        prog="toolforge jobs" if toolforge_cli_in_use else None,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help=argparse.SUPPRESS if toolforge_cli_in_use else "activate debug mode",
        default=toolforge_cli_debug,
    )

    subparser = parser.add_subparsers(
        help="possible operations (pass -h to know usage of each)",
        dest="operation",
        required=True,
    )

    subparser.add_parser(
        "images",
        help="list information on available container image types for Toolforge jobs",
    )

    runparser = subparser.add_parser(
        "run",
        help="run a new job of your own in Toolforge",
    )
    runparser_exclusive_group = runparser.add_mutually_exclusive_group()
    filelog_parser = runparser.add_mutually_exclusive_group()

    for key, value in RUN_ARGS.items():
        if key in ["continuous", "schedule", "wait"]:
            runparser_exclusive_group.add_argument(*value["args"], **value["kwargs"])
        elif key in ["no-filelog", "filelog"]:
            filelog_parser.add_argument(*value["args"], **value["kwargs"])
        else:
            runparser.add_argument(*value["args"], **value["kwargs"])

    showparser = subparser.add_parser(
        "show",
        help="show details of a job of your own in Toolforge",
    )
    showparser.add_argument("name", help="job name")

    logs_parser = subparser.add_parser(
        "logs",
        help="show output from a running job",
    )
    logs_parser.add_argument("name", help="job name")
    logs_parser.add_argument(
        "-f",
        "--follow",
        required=False,
        action="store_true",
        help="stream updates",
    )
    logs_parser.add_argument(
        "-l",
        "--last",
        required=False,
        type=int,
        help="number of recent log lines to display",
    )

    listparser = subparser.add_parser(
        "list",
        help="list all running jobs of your own in Toolforge",
    )
    listparser.add_argument(
        "-o",
        "--output",
        type=ListDisplayMode,
        choices=list(ListDisplayMode),
        default=ListDisplayMode.NORMAL,
        help="specify output format (defaults to %(default)s)",
    )
    # deprecated, remove in a few releases
    listparser.add_argument(
        "-l",
        "--long",
        required=False,
        action="store_true",
        help=argparse.SUPPRESS,
    )

    deleteparser = subparser.add_parser(
        "delete",
        help="delete a running job of your own in Toolforge",
    )
    deleteparser.add_argument("name", help="job name")

    subparser.add_parser(
        "flush",
        help="delete all running jobs of your own in Toolforge",
    )

    loadparser = subparser.add_parser(
        "load",
        help="flush all jobs and load a YAML file with job definitions and run them",
    )
    loadparser.add_argument("file", help="path to YAML file to load")
    loadparser.add_argument("--job", required=False, help="load a single job only")

    restartparser = subparser.add_parser("restart", help="restarts a running job")
    restartparser.add_argument("name", help="job name")

    subparser.add_parser("quota", help="display quota information")

    dumpparser = subparser.add_parser(
        "dump",
        help="dump all defined jobs in YAML format, suitable for a later `load` operation",
    )
    dumpparser.add_argument("-f", "--to-file", required=False, help="write YAML dump to given file")

    return parser.parse_args()


def op_images(api: ToolforgeClient):
    images = api.get("/images/")

    try:
        output = tabulate(images, headers=IMAGES_TABULATION_HEADERS, tablefmt="pretty")
    except Exception as e:
        raise TjfCliError("Failed to format image table") from e

    print(output)


def job_prepare_for_output(api: ToolforgeClient, job, headers: List[str], suppress_hints=True):
    schedule = job.get("schedule", None)
    cont = job.get("continuous", None)
    retry = job.get("retry")
    if schedule is not None:
        job["type"] = f"schedule: {schedule}"
        job.pop("schedule", None)
    elif cont is not None:
        job["type"] = "continuous"
        job.pop("continuous", None)
    else:
        job["type"] = "one-off"

    filelog = job.get("filelog", False)
    # We are currently sending a stringified boolean, remove str support once
    # https://gitlab.wikimedia.org/repos/cloud/toolforge/jobs-api/-/merge_requests/70
    # is in
    if str(filelog) == "True":
        job["filelog"] = "yes"
    else:
        job["filelog"] = "no"

    if retry == 0:
        job["retry"] = "no"
    else:
        job["retry"] = f"yes: {retry} time(s)"

    health_check = job.get("health_check", None)
    if health_check is not None:
        script = health_check.get("script", None)
        if script:
            job["health_check"] = f"script: {script}"
    else:
        job["health_check"] = "none"

    mem = job.pop("memory", "default")
    cpu = job.pop("cpu", "default")
    if mem == "default" and cpu == "default":
        job["resources"] = "default"
    else:
        job["resources"] = f"mem: {mem}, cpu: {cpu}"

    if suppress_hints:
        if job.get("status_long", None) is not None:
            job.pop("status_long", None)
    else:
        job["status_long"] = textwrap.fill(job.get("status_long", "Unknown"))

    if job["image_state"] != "stable":
        job["image"] += " ({})".format(job["image_state"])

    # not interested in these fields ATM
    for key in job.copy():
        if key not in headers:
            logging.debug(f"supressing job API field '{key}' before output")
            job.pop(key)

    # normalize key names for easier printing
    for key in headers:
        if key == "status_long" and suppress_hints:
            continue

        oldkey = key
        newkey = headers[key]
        job[newkey] = job.pop(oldkey, "Unknown")


def _list_jobs(api: ToolforgeClient):
    return api.get("/jobs/")


def op_list(api: ToolforgeClient, output_format: ListDisplayMode):
    list = _list_jobs(api)

    if len(list) == 0:
        logging.debug("no jobs to be listed")
        return

    if output_format == ListDisplayMode.NAME:
        for job in list:
            print(job["name"])
        return

    try:
        if output_format == ListDisplayMode.LONG:
            headers = JOB_TABULATION_HEADERS_LONG
        else:
            headers = JOB_TABULATION_HEADERS_SHORT

        for job in list:
            logging.debug(f"job information from the API: {job}")
            job_prepare_for_output(api, job, headers=headers, suppress_hints=True)

        output = tabulate(list, headers=headers, tablefmt="pretty")
    except Exception as e:
        raise TjfCliError("Failed to format job table") from e

    print(output)


def _wait_for_job(api: ToolforgeClient, name: str, seconds: int) -> None:
    starttime = time.time()
    while time.time() - starttime < seconds:
        time.sleep(WAIT_SLEEP)

        job = _show_job(api, name, missing_ok=True)
        if job is None:
            logging.info(f"job '{name}' completed (and already deleted)")
            return

        if job["status_short"] == "Completed":
            logging.info(f"job '{name}' completed")
            return

        if job["status_short"] == "Failed":
            logging.error(f"job '{name}' failed:")
            op_show(api, name)
            sys.exit(EXIT_USER_ERROR)

    logging.error(f"timed out {seconds} seconds waiting for job '{name}' to complete:")
    op_show(api, name)
    sys.exit(EXIT_INTERNAL_ERROR)


def _image_is_buildservice(image: str) -> bool:
    return "/" in image


def op_run(
    api: ToolforgeClient,
    name: str,
    command: str,
    schedule: Optional[str],
    continuous: bool,
    image: str,
    wait: int | None,
    filelog: bool | None,
    filelog_stdout: Optional[str],
    filelog_stderr: Optional[str],
    mem: Optional[str],
    cpu: Optional[str],
    retry: int,
    emails: str,
    mount: MountOption | None,
    health_check_script: Optional[str],
) -> None:
    if not mount:
        mount = MountOption.NONE if _image_is_buildservice(image) else MountOption.ALL

    payload = {
        "name": name,
        "imagename": image,
        "cmd": command,
        "emails": emails,
        "retry": retry,
        "mount": mount.value,
    }

    if continuous and schedule:
        raise TjfCliUserError("Only one of 'continuous' and 'schedule' can be set at the same time")
    elif continuous:
        payload["continuous"] = True
    elif schedule:
        payload["schedule"] = schedule

    if filelog is not None:
        payload["filelog"] = filelog
    else:
        payload["filelog"] = not _image_is_buildservice(image)

    if mount == MountOption.NONE and payload["filelog"]:
        raise TjfCliUserError("Specifying --filelog on a build service image requires --mount=all")
    if (filelog_stdout or filelog_stderr) and not payload["filelog"]:
        raise TjfCliUserError(
            "Specifying --filelog-stdout or --filelog-stderr on a build service image requires --filelog"
        )

    if filelog_stdout:
        payload["filelog_stdout"] = filelog_stdout

    if filelog_stderr:
        payload["filelog_stderr"] = filelog_stderr

    if mem:
        payload["memory"] = mem

    if cpu:
        payload["cpu"] = cpu

    if health_check_script:
        if not continuous:
            logging.warning(
                "\033[93mHealth checks are only supported for continuous jobs. --health-check-script ignored\033[0m"
            )
        payload["health_check"] = {"type": "script", "script": health_check_script}

    logging.debug(f"payload: {payload}")

    try:
        api.post("/jobs/", json=payload)
    except TjfCliHttpUserError as e:
        if e.status_code == 409:
            raise TjfCliUserError("A job with this name already exists") from e

        raise e

    logging.debug("job was created")

    if wait:
        _wait_for_job(api, name, wait)


def _show_job(api: ToolforgeClient, name: str, missing_ok: bool):
    try:
        job = api.get(f"/jobs/{name}")
    except TjfCliHttpUserError as e:
        if e.status_code == 404:
            if missing_ok:
                return None  # the job doesn't exist, but that's ok!

            raise TjfCliUserError(f"Job '{name}' does not exist") from e

        raise e

    logging.debug(f"job information from the API: {job}")
    return job


def op_show(api: ToolforgeClient, name):
    job = _show_job(api, name, missing_ok=False)
    job_prepare_for_output(api, job, suppress_hints=False, headers=JOB_TABULATION_HEADERS_LONG)

    # change table direction
    kvlist = []
    for key in job:
        kvlist.append([key, job[key]])

    try:
        output = tabulate(kvlist, tablefmt="grid")
    except Exception as e:
        raise TjfCliError("Failed to format job display") from e

    print(output)


def op_logs(api: ToolforgeClient, name: str, follow: bool, last: Optional[int]):
    params = {"follow": "true" if follow else "false"}
    if last:
        params["lines"] = last

    try:
        for raw_line in api.get_raw_lines(
            f"/jobs/{name}/logs",
            params=params,
        ):
            parsed = json.loads(raw_line)
            print(f"{parsed['datetime']} [{parsed['pod']}] {parsed['message']}")
    except KeyboardInterrupt:
        pass


def op_delete(api: ToolforgeClient, name: str):
    try:
        api.delete(f"/jobs/{name}")
    except TjfCliHttpUserError as e:
        if e.status_code == 404:
            logging.warning(f"job '{name}' does not exist")
            return
        raise e

    logging.debug("job was deleted")


def op_flush(api: ToolforgeClient):
    api.delete("/jobs/")
    logging.debug("all jobs were flushed (if any existed anyway, we didn't check)")


def _delete_and_wait(api: ToolforgeClient, names: Set[str]):
    for name in names:
        op_delete(api, name)

    curtime = starttime = time.time()
    while curtime - starttime < DELETE_WAIT_TIMEOUT:
        logging.debug(f"waiting for {len(names)} job(s) to be gone, sleeping {WAIT_SLEEP} seconds")
        time.sleep(WAIT_SLEEP)
        curtime = time.time()

        jobs = _list_jobs(api)
        if not any([job for job in jobs if job["name"] in names]):
            # ok!
            return

    raise TjfCliError("Timed out while waiting for old jobs to be deleted")


def _load_job(api: ToolforgeClient, job: dict, n: int):
    # these are mandatory
    try:
        name = job["name"]
        command = job["command"]
        image = job["image"]
    except KeyError as e:
        raise TjfCliUserError(
            f"Unable to load job number {n}: missing configuration parameter {str(e)}"
        ) from e

    # these are optional
    schedule = job.get("schedule", None)
    continuous = job.get("continuous", False)

    filelog = job.get("filelog", None)
    if filelog is None and "no-filelog" in job:
        filelog = not job["no-filelog"]

    filelog_stdout = job.get("filelog-stdout", None)
    filelog_stderr = job.get("filelog-stderr", None)
    retry = job.get("retry", 0)
    mem = job.get("mem", None)
    cpu = job.get("cpu", None)
    emails = job.get("emails", "none")
    health_check_script = job.get("health-check-script", None)

    try:
        mount = MountOption.parse(job["mount"]) if "mount" in job else None
    except ValueError as e:
        raise TjfCliUserError(
            f"Unable to load job number {n}: failed to parse mount option '{str(e)}'"
        ) from e

    if not schedule and not continuous:
        wait = job.get("wait", None)
        if wait is True:
            wait = DEFAULT_WAIT_TIMEOUT
        elif wait is False:
            wait = None
    else:
        wait = None

    op_run(
        api=api,
        name=name,
        command=command,
        schedule=schedule,
        continuous=continuous,
        image=image,
        wait=wait,
        filelog=filelog,
        filelog_stdout=filelog_stdout,
        filelog_stderr=filelog_stderr,
        retry=retry,
        mem=mem,
        cpu=cpu,
        emails=emails,
        mount=mount,
        health_check_script=health_check_script,
    )


def op_load(api: ToolforgeClient, file: str, job_name: Optional[str]):
    try:
        with open(file) as f:
            jobslist = yaml.safe_load(f.read())
    except Exception as e:
        raise TjfCliUserError(f"Unable to parse yaml file '{file}'") from e

    logging.debug(f"loaded content from YAML file '{file}':")
    logging.debug(f"{jobslist}")

    filter = (lambda name: name == job_name) if job_name else None
    changes = calculate_changes(
        conf=api,
        configured_job_data=jobslist,
        job_keys=RUN_ARGS.keys(),
        filter=filter,
    )

    if len(changes.delete) > 0 or len(changes.modify) > 0:
        _delete_and_wait(api, {*changes.delete, *changes.modify})

    for n, job in enumerate(jobslist, start=1):
        if "name" not in job:
            raise TjfCliUserError(
                f"Unable to load job number {n}: missing configuration parameter name"
            )

        name = job["name"]
        if name not in changes.add and name not in changes.modify:
            continue

        try:
            _load_job(api, job, n)
        except TjfCliUserError as e:
            raise TjfCliUserError(f"Invalid job {name}: {str(e)}") from e
        except Exception as e:
            raise TjfCliError(f"Failed to load job {name}") from e


def op_restart(api: ToolforgeClient, name: str):
    try:
        api.post(f"/jobs/{name}/restart")
    except TjfCliHttpUserError as e:
        if e.status_code == 404:
            raise TjfCliUserError(f"Job '{name}' does not exist") from e
        raise e

    logging.debug("job was restarted")


def op_quota(api: ToolforgeClient):
    data = api.get("/quota/")

    logging.debug("Got quota data: %s", data)

    for i, category in enumerate(data["categories"]):
        if i != 0:
            # Empty line to separate categories
            print()

        has_used = "used" in category["items"][0]
        items = [
            (
                # use category["name"] as the header of the
                # first column to indicate category names
                {category["name"]: item["name"], "Used": item["used"], "Limit": item["limit"]}
                if has_used
                else {category["name"]: item["name"], "Limit": item["limit"]}
            )
            for item in category["items"]
        ]

        print(tabulate(items, tablefmt="simple", headers="keys"))


def get_tool_account() -> str:
    project_file = Path("/etc/wmcs-project")
    if project_file.exists():
        project = project_file.read_text().strip()
    else:
        project = "unknown-project"

    user = getpass.getuser()
    if user.startswith(f"{project}."):
        tool_account = user.split(f"{project}.", 1)[1]
    else:
        tool_account = "unknown-tool-account"

    return tool_account


def is_default_filelog_file(filelog: str, jobname: str, filesuffix: str) -> bool:
    if not filelog:
        return True

    if filelog == f"$TOOL_DATA_DIR/{jobname}.{filesuffix}":
        return True

    tool_account = get_tool_account()
    if filelog == f"/data/project/{tool_account}/{jobname}.{filesuffix}":
        return True

    return False


# TODO: this removeprefix() function is available natively starting with python 3.9
# but toolforge bastions run python 3.7 as of this writing
def _removeprefix(input_string: str, prefix: str) -> str:
    if prefix and input_string.startswith(prefix):
        return input_string[len(prefix) :]  # noqa: E203
    return input_string


def shorten_filelog_path(filelog: str) -> str:
    tool_account = get_tool_account()
    return _removeprefix(
        _removeprefix(filelog, "$TOOL_DATA_DIR/"), f"/data/project/{tool_account}/"
    )


def job_prepare_for_dump(job: dict[str, Any]) -> None:
    """The goal is to produce a YAML representation suitable for a later `load` operation, cleaning
    some defaults along the way in order to minimize the output.
    """
    # TODO: see T327280 about inconsistent dictionary keys across the framework

    # let's fail if these key are not present. It would be very unexpected, we want the explicit failure
    job["command"] = job["cmd"]
    image = job["image"]
    jobname = job["name"]

    filelog = job.pop("filelog", False)
    if filelog == "True":
        if _image_is_buildservice(image):
            # this was explicitly set for a buildservice image, show it
            job["filelog"] = "yes"
    else:
        if not _image_is_buildservice(image):
            # this was explicitly set for a non-buildservice image, show it
            job["no-filelog"] = "true"

    # drop default and None filelog paths
    stdout = job.get("filelog_stdout")
    if not is_default_filelog_file(filelog=stdout, jobname=jobname, filesuffix="out"):
        job["filelog-stdout"] = shorten_filelog_path(stdout)

    stderr = job.get("filelog_stderr")
    if not is_default_filelog_file(filelog=stderr, jobname=jobname, filesuffix="err"):
        job["filelog-stderr"] = shorten_filelog_path(stderr)

    if job.get("mount") == "none":
        if _image_is_buildservice(image):
            # this is the default for a buildservice image, hide it
            job.pop("mount")
    elif job.get("mount") == "all":
        if not _image_is_buildservice(image):
            # this is the default for a non buildservice image, hide it
            job.pop("mount")

    # hide default retry
    retry = job.get("retry", 0)
    if retry == 0:
        job.pop("retry")

    # hide default emails
    emails = job.get("emails")
    if emails == "none":
        job.pop("emails")

    mem = job.get("memory")
    if mem:
        job["mem"] = mem

    remove_keys = [
        "cmd",
        "memory",
        "image_state",
        "status_short",
        "status_long",
        "schedule_actual",
        "filelog_stdout",
        "filelog_stderr",
    ]

    for key in remove_keys:
        try:
            job.pop(key)
        except KeyError:
            # we don't care, this is harmless anyway. For example, schedule_actual is only present on cronjobs
            pass


def op_dump(api: ToolforgeClient, to_file: str) -> None:
    joblist = _list_jobs(api)

    if len(joblist) == 0:
        logging.warning(
            f"no jobs defined{f', file {to_file} will not be created' if to_file else ''}"
        )
        return

    for job in joblist:
        job_prepare_for_dump(job=job)

    if to_file:
        with open(to_file, "w") as file:
            yaml.dump(joblist, file)
    else:
        print(yaml.dump(joblist))


def run_subcommand(args: argparse.Namespace, api: ToolforgeClient):
    if args.operation == "images":
        op_images(api)
    elif args.operation == "run":
        op_run(
            api=api,
            name=args.name,
            command=args.command,
            schedule=args.schedule,
            continuous=args.continuous,
            image=args.image,
            wait=args.wait,
            filelog=args.filelog,
            filelog_stdout=args.filelog_stdout,
            filelog_stderr=args.filelog_stderr,
            retry=args.retry,
            mem=args.mem,
            cpu=args.cpu,
            emails=args.emails,
            mount=args.mount,
            health_check_script=args.health_check_script,
        )
    elif args.operation == "show":
        op_show(api, args.name)
    elif args.operation == "logs":
        op_logs(api, args.name, args.follow, args.last)
    elif args.operation == "delete":
        op_delete(api, args.name)
    elif args.operation == "list":
        output_format = args.output
        if args.long:
            logging.warning("the `--long` flag is deprecated, use `--output long` instead")
            output_format = ListDisplayMode.LONG
        op_list(api, output_format)
    elif args.operation == "flush":
        op_flush(api)
    elif args.operation == "load":
        op_load(api, args.file, args.job)
    elif args.operation == "restart":
        op_restart(api, args.name)
    elif args.operation == "quota":
        op_quota(api)
    elif args.operation == "dump":
        op_dump(api=api, to_file=args.to_file)


def main():
    args = arg_parser()

    logging_format = "%(levelname)s: %(message)s"
    if args.debug:
        logging_level = logging.DEBUG
        logging_format = f"[%(asctime)s] [%(filename)s] {logging_format}"
    else:
        logging_level = logging.INFO

    logging.addLevelName(
        logging.WARNING, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING)
    )
    logging.addLevelName(
        logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR)
    )
    logging.basicConfig(
        format=logging_format, level=logging_level, stream=sys.stdout, datefmt="%Y-%m-%d %H:%M:%S"
    )

    user = getpass.getuser()
    project_file = Path("/etc/wmcs-project")
    if project_file.exists():
        project = project_file.read_text().strip()
    else:
        logging.warning(
            "Unable to find project file '%s', continuing as project `tools`", project_file
        )
        project = "tools"

    if not user.startswith(f"{project}."):
        logging.warning(
            "not running as the tool account? Likely to fail. Perhaps you forgot `become <tool>`?"
        )

    try:
        kubeconfig = Kubeconfig.load()
        host = socket.gethostname()
        user_agent = f"{kubeconfig.current_namespace}@{host}"

        config = load_config("jobs-cli", extra_sections=[JobsConfig])
    except Exception as e:
        raise TjfCliConfigLoadError("Failed to load configuration") from e

    api = ToolforgeClient(
        server=f"{config.api_gateway.url}{config.jobs.jobs_endpoint}",
        exception_handler=handle_http_exception,
        user_agent=user_agent,
        kubeconfig=kubeconfig,
        timeout=config.jobs.timeout,
    )

    logging.debug("session configuration generated correctly")

    try:
        run_subcommand(args=args, api=api)
    except TjfCliUserError as e:
        logging.error(f"Error: {str(e)}")
        if args.debug:
            print_error_context(e)

        sys.exit(EXIT_USER_ERROR)
    except TjfCliError as e:
        logging.exception("An internal error occured while executing this command.", exc_info=True)
        if args.debug:
            print_error_context(e)

        logging.error(REPORT_MESSAGE)

        sys.exit(EXIT_INTERNAL_ERROR)
    except Exception:
        logging.exception("An internal error occured while executing this command.", exc_info=True)
        logging.error(REPORT_MESSAGE)

        sys.exit(EXIT_INTERNAL_ERROR)

    logging.debug("-- end of operations")
