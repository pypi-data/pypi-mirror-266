import httpx
import typer
from rich import print

from systema.__version__ import VERSION
from systema.cli.migration import create_submodels
from systema.management import (
    DB_FILENAME,
    DOTENV_FILENAME,
    InstanceType,
    Settings,
)
from systema.server.auth.utils import create_superuser
from systema.server.db import create_db_and_tables
from systema.server.main import serve as _serve
from systema.tui.app import SystemaTUIApp

from .query import app as query_app

ART = r"""
  ___         _
 / __|_  _ __| |_ ___ _ __  __ _
 \__ \ || (_-<  _/ -_) '  \/ _` |
 |___/\_, /__/\__\___|_|_|_\__,_|
      |__/
"""


def print_art():
    typer.echo(ART)


app = typer.Typer(name="systema", callback=print_art, no_args_is_help=True)
app.add_typer(query_app)


@app.command()
def serve(dev: bool = typer.Option(False)):
    """Start web server"""

    _serve(dev=dev)


@app.command()
def tui():
    """Start TUI client"""

    SystemaTUIApp().run()


@app.command()
def setup():
    """Run setup wizard"""

    settings = Settings()
    replace = typer.prompt(
        "New defaults?",
        default=True,
        type=bool,
    )
    if replace:
        settings.to_dotenv()
        print(f"New config file generated at {settings.base_path / DOTENV_FILENAME}")

    replace = typer.prompt(
        "New empty database?",
        default=True,
        type=bool,
    )
    if replace:
        db_file = settings.base_path / DB_FILENAME
        db_file.unlink(missing_ok=True)

    create_db_and_tables()
    if typer.prompt("Create superuser?", type=bool, default=True):
        prompt_for_superuser()

    if typer.prompt("Run migration routine?", type=bool, default=False):
        create_submodels()


def prompt_for_superuser():
    username = typer.prompt("Username", type=str)
    password = typer.prompt(
        "Password", type=str, hide_input=True, confirmation_prompt=True
    )
    create_superuser(username, password)
    print(f"Superuser {username} created")


@app.command()
def superuser():
    """Create superuser"""

    prompt_for_superuser()


@app.command()
def generate_token():
    """Generate token for remote access"""

    settings = Settings()
    if settings.instance_type == InstanceType.SERVER:
        print("Instance type is server")
        raise typer.Abort()

    response = httpx.post(
        f"{settings.server_base_url}token",
        data={
            "username": typer.prompt("Username"),
            "password": typer.prompt("Password", hide_input=True),
        },
        params={"permanent": True},
    )
    response.raise_for_status()
    if token := response.json().get("access_token"):
        settings.token = token
        settings.to_dotenv()
        print("Token stored!")


@app.command()
def change_instance_type():
    """Change instance type"""

    settings = Settings()
    instance_type = settings.instance_type
    print(f"Current instance type: {instance_type.value}")
    if typer.prompt("Change type?", default=True, type=bool):
        settings.instance_type = settings.instance_type.other()
        print(settings.instance_type)
        settings.to_dotenv()
        print(f"Instance type changed to {settings.instance_type}")


@app.command()
def generate_unit():
    """Generate unit configuration file for systemd"""

    import subprocess
    from pathlib import Path
    from textwrap import dedent

    bin_location = subprocess.getoutput("which systema")
    print(f"which systema: {bin_location}")

    unit_config_content = f"""\
        [Unit]
        Description=Systema Server
        After=networking.target

        [Service]
        ExecStart={bin_location} serve
        Restart=always
        RestartSec=30

        [Install]
        WantedBy=default.target
    """

    unit_config_content = dedent(unit_config_content).strip()

    unit_config_dir = Path(typer.get_app_dir("systemd")) / "user"
    unit_config_dir.mkdir(parents=True, exist_ok=True)

    unit_config_path = unit_config_dir / "systema.service"
    unit_config_path.touch(exist_ok=True)

    unit_config_path.write_text(unit_config_content)
    print(unit_config_content)


@app.command()
def version():
    """Show version"""

    print(VERSION)


@app.command(help="Generate file with all the data")
def dump():
    pass
