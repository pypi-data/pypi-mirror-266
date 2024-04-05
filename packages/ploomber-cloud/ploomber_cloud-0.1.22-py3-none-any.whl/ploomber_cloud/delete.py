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


def delete():
    """Delete an application"""
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
