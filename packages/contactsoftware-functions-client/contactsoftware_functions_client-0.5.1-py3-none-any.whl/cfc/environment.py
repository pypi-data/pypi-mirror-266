import os
import re
import sys
import tarfile
from time import sleep

import requests
import typer
from rich.console import Console
from rich.table import Table

from .config import config

NAME_PATTERN = r"^[^\-\.][\w\-\.]+$"
ENV_VARS_PATTERN = r"^([\w:.\/]+=[\w:.\/]+)(,[\w:.\/]+=[\w:.\/]+)*$"
ENVIRONMENT_ENVVAR_NAME = "CFC_ENVIRONMENT"

env_app = typer.Typer()
console = Console()


def name_callback(name: str) -> str:
    if not re.fullmatch(NAME_PATTERN, name) or len(name) > 50:
        raise typer.BadParameter(
            f"Name must match pattern {NAME_PATTERN} and must not be longer than 50 characters"
        )
    return name


def tag_callback(name: str) -> str:
    if not name:
        return name

    return name_callback(name)


def env_var_callback(env_vars: str) -> dict:
    if not env_vars:
        return env_vars
    if not re.fullmatch(ENV_VARS_PATTERN, env_vars):
        raise typer.BadParameter(f"Variables must match pattern {ENV_VARS_PATTERN}")

    return env_vars


def _ensure_token_set():
    try:
        return config.access_token
    except ValueError as e:
        print(e)
        console.print("Auth token not set. You need to login first, using 'cfc login'!")
        sys.exit(1)


@env_app.command(name="create")
def create(name: str = typer.Argument(..., callback=name_callback)):
    """creates a new empty environment"""
    _ensure_token_set()
    console.print(f"Creating new environment '{name}' ... (This may take a while)")

    response = requests.post(  # nosec pylint: disable=missing-timeout
        config.service_url + "/api/environments/" + name,
        headers={"Authorization": f"Bearer {config.access_token}"},
    )

    if response.status_code == 201:
        console.print("Environment successfully created")

    elif response.status_code in (400, 500):
        console.print(
            "Error while creating environment: " + response.json()["detail"]["msg"]
        )
        raise typer.Exit(code=1)

    else:
        console.print("Unknown error while creating environment")
        raise typer.Exit(code=1)


@env_app.command(name="delete")
def delete(
    name: str = typer.Argument(..., callback=name_callback),
    force: bool = typer.Option(False),
):
    """deletes an environment"""
    _ensure_token_set()
    console.print(f"Deleting environment '{name}' ...")
    force = "?force=true" if force else ""
    response = requests.delete(  # nosec pylint: disable=missing-timeout
        config.service_url + "/api/environments/" + name + force,
        headers={"Authorization": f"Bearer {config.access_token}"},
    )
    if response.status_code == 201:
        console.print("Environment successfully deleted")


@env_app.command(name="list")
def list_environments():
    """list all environments"""
    _ensure_token_set()
    result = requests.get(  # nosec pylint: disable=missing-timeout
        config.service_url + "/api/environments/",
        headers={"Authorization": f"Bearer {config.access_token}"},
    )

    table = Table()

    table.add_column("Name")
    table.add_column("Runtime")
    table.add_column("Version")
    table.add_column("Active Tag")
    table.add_column("Status")
    table.add_column("Functions")
    environments = result.json()["environments"]
    for env in environments:
        table.add_row(
            env["name"],
            env["runtime"],
            env["version"],
            env["active_tag"],
            env["status_environment"],
            env["status_function"],
            "\n".join(str(e) for e in env["functions"]),
        )

    console.print(table)


@env_app.command(name="describe")
def describe_env(
    environment_name: str = typer.Argument(
        ..., callback=name_callback, envvar=ENVIRONMENT_ENVVAR_NAME
    )
):
    """describes an environment"""
    _ensure_token_set()
    result = requests.get(  # nosec pylint: disable=missing-timeout
        config.service_url + "/api/environments/" + environment_name,
        headers={"Authorization": f"Bearer {config.access_token}"},
    )
    console.print(result.json())


@env_app.command(name="deploy")
def deploy_env(
    environment_name: str = typer.Argument(
        ..., callback=name_callback, envvar=ENVIRONMENT_ENVVAR_NAME
    ),
    source_path: str = typer.Option("."),
    tag: str = typer.Option("", callback=tag_callback),
    environment_variables: str = typer.Option("", callback=env_var_callback),
):
    """deploy code into an environment"""
    _ensure_token_set()

    if not os.path.exists(os.path.join(source_path, "environment.yaml")):
        raise typer.BadParameter("Directory is not a valid environment")

    with tarfile.open("source.tar.gz", "w:gz") as f:
        f.add(source_path, "/")

    tag_info = {"tagname": tag} if tag else {}
    data = tag_info
    if environment_variables:
        data["environment_variables"] = environment_variables

    with open("source.tar.gz", "rb") as codepackage:
        console.print("Uploading code (This can take a while)")
        response = requests.post(  # nosec pylint: disable=missing-timeout
            config.service_url
            + "/api/environments/"
            + environment_name
            + "/upload_code",
            files={"codepackage": codepackage},
            data=data,
            headers={"Authorization": f"Bearer {config.access_token}"},
        )

    if response.status_code in (200, 202):
        console.print("Waiting for build job to complete")
        job_id = response.json()["job_id"]
        success = _wait_for_job(job_id)
        if success:
            console.print("Code successfully deployed")
        else:
            console.print("Code deployment failed")
    else:
        console.print(f"Error: received status code {response.status_code}")
        print(response.text)

    os.unlink("source.tar.gz")


def _get_new_logs(old_logs: list[str], current_logs: str) -> list[str]:
    current_logs_list = current_logs.rstrip("\n").split(
        "\n"
    )  # rstrip \n, to prevent empty lines
    common_index = len(old_logs)
    return current_logs_list[common_index:]


def _wait_for_job(job_id: str, sleep_time: int = 5) -> bool:
    log_lines: list[str] = []
    while True:
        response = requests.get(
            config.service_url + "/api/job/by_id/" + job_id,
            headers={"Authorization": f"Bearer {config.access_token}"},
            timeout=30,
        )
        job_data = response.json()
        new_log_lines = _get_new_logs(log_lines, job_data["log"])
        for line in new_log_lines:
            console.print(line, highlight=False, markup=False)
        log_lines += new_log_lines

        if job_data["status"] == "finished":
            return True
        elif job_data["status"] == "error":
            return False

        sleep(sleep_time)
