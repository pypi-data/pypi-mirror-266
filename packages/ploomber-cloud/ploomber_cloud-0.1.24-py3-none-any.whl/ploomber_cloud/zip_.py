import zipfile
from pathlib import Path
from contextlib import contextmanager
from uuid import uuid4

import click
import shutil
import json
from dotenv import dotenv_values

IGNORED = {".DS_Store", ".ipynb_checkpoints", "ploomber-cloud.json"}


def _is_git(path):
    """Return True if path is in a .git directory"""
    return ".git" in Path(path).parts


def _is_pyc(path):
    """Return True if path is a .pyc file"""
    return Path(path).suffix == ".pyc"


def _is_env(path):
    """Return True if path is an .env file"""
    return str(path) == ".env"


def _is_blacklisted_file(path):
    return Path(path).name in IGNORED


def _is_ignored_file(path):
    return _is_git(path) or _is_pyc(path) or _is_blacklisted_file(path)


def _generate_random_suffix():
    return str(uuid4()).replace("-", "")[:8]


def _clear_env_file(path):
    """Overwrite .env file with an empty file"""
    copied_path = f"copy_{path}"
    shutil.copy(path, copied_path)

    with open(path, "w") as env_file:
        env_file.truncate(0)

    return path, copied_path


def _load_env_file_contents(path):
    """Load .env secrets into JSON string to send to API"""
    config = dotenv_values(path)
    if not config:
        return None

    click.echo("Reading .env file...")
    config_arr = []
    output_message = [
        "Adding the following secrets to the app: ",
    ]

    for key, value in config.items():
        config_arr.append({"key": key, "value": value})
        output_message.append(f"{key}, ")

    click.echo("".join(output_message))
    return json.dumps(config_arr)


@contextmanager
def zip_app(verbose, base_dir=None):
    """Compress app in a zip file.
    Parses secrets from .env and empties .env before zipping it.
    Returns path to zip file, and secrets as JSON string."""
    base_dir = Path(base_dir or "")

    suffix = _generate_random_suffix()
    path_to_zip = base_dir / f"app-{suffix}.zip"
    env_path, copied_env_path = None, None
    secrets = None

    if path_to_zip.exists():
        if verbose:
            click.echo(f"Deleting existing {path_to_zip}...")

        path_to_zip.unlink()

    if verbose:
        click.secho("Compressing app...", fg="green")

    files = [f for f in Path(base_dir).glob("**/*") if Path(f).is_file()]
    files.sort()  # Sorting so that .env is processed first if present

    with zipfile.ZipFile(path_to_zip, "w", zipfile.ZIP_DEFLATED) as zip:
        for path in files:
            if _is_ignored_file(path) or Path(path).name == path_to_zip.name:
                continue

            # If .env file found, read and empty it before adding to zip
            if _is_env(path):
                secrets = _load_env_file_contents(path)
                env_path, copied_env_path = _clear_env_file(path)
            else:
                click.echo(f"Adding {path}...")

            arcname = Path(path).relative_to(base_dir)
            zip.write(path, arcname=arcname)

    # If we cleared the .env file, put its contents back in
    if env_path:
        shutil.copy(copied_env_path, env_path)
        Path(copied_env_path).unlink()

    if verbose:
        click.secho("App compressed successfully!", fg="green")

    try:
        yield path_to_zip, secrets
    finally:
        if path_to_zip.exists():
            path_to_zip.unlink()
