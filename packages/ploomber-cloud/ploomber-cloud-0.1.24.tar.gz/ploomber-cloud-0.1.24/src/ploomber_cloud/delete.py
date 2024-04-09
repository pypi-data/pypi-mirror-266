import click
from pathlib import Path

from ploomber_cloud import api
from ploomber_cloud.config import PloomberCloudConfig
from ploomber_cloud.exceptions import PloomberCloudRuntimeException


def _find_project_id():
    """Parse config file for project ID"""
    config = PloomberCloudConfig()
    config.load()
    data = config.data
    return data["id"]


def _remove_config_file():
    """Remove the config file"""
    if Path("ploomber-cloud.json").exists():
        Path("ploomber-cloud.json").unlink()


def delete(project_id=None):
    """Delete an application"""
    if not project_id:
        project_id = _find_project_id()
    client = api.PloomberCloudClient()

    try:
        client.delete(project_id=project_id)
    except Exception as e:
        raise PloomberCloudRuntimeException(
            "Error deleting project",
        ) from e

    _remove_config_file()

    click.echo("Project successfully deleted.")


def delete_all():
    """Delete all applications"""
    confirmed = click.confirm(
        "Are you sure you want to delete all projects?\n"
        "This action is irreversible and cannot be undone.\n"
        "Pressing forward with this will result in a loss of "
        "all project data and configurations.\n"
        "If you're unsure or wish to reconsider, "
        "please cancel immediately by pressing Ctrl + C."
    )
    if not confirmed:
        click.echo("Deletion cancelled.")
        return
    client = api.PloomberCloudClient()

    try:
        client.delete_all()
    except Exception as e:
        raise PloomberCloudRuntimeException(
            "Error deleting all projects",
        ) from e
