import json
import os
import subprocess  # nosec
import sys

import typer
import yaml
from rich.console import Console

from .auth import CredentialsInvalid
from .config import config
from .environment import env_app

app = typer.Typer()
console = Console()

app.add_typer(env_app, name="env")


def get_environment(source_path: str):
    envfile = os.path.join(source_path, "environment.yaml")

    if not os.path.exists(envfile):
        raise typer.BadParameter(
            "Directory is not a valid environment", param_hint="source_path"
        )

    with open(envfile, "rb") as f:
        return yaml.safe_load(f)


@app.command(name="login")
def login(
    client_id: str = typer.Option(..., prompt=True),
    client_secret: str = typer.Option(..., prompt=True, hide_input=True),
    service_url: str = typer.Option(default=config.service_url),
):
    """Login to function backend using client ID and client secret"""

    if service_url != config.service_url and typer.confirm(
        "There is already another service url saved. Override?"
    ):
        config.service_url = service_url
        config.save()

    config.client_id = client_id
    config.client_secret = client_secret

    try:
        config.refresh_token()  # will save config on success, otherwise raises an Exception
    except CredentialsInvalid:
        console.print("Login failed! Credentials are invalid!")
        sys.exit(1)


func_app = typer.Typer()

app.add_typer(func_app, name="function")


@func_app.command(name="test")
def test_function(
    function_name: str = typer.Argument(...),
    source_path: str = typer.Option("."),
):
    # Test must be executed respecting the given runtime
    # Python could be executed in process, but nodejs must be triggered by a separate process

    source_path = os.path.abspath(source_path)

    environment_config = get_environment(source_path)

    if environment_config.get("runtime") == "python3.10":
        from cs.functions.test import test  # pylint: disable=import-outside-toplevel

        console.print(test(source_path, environment_config, function_name))

    else:
        subprocess.call(  # nosec
            [
                "node",
                "libs/nodejs/test.js",
                "--config",
                json.dumps(environment_config),
                "--source",
                source_path,
                "--function",
                function_name,
            ]
        )
