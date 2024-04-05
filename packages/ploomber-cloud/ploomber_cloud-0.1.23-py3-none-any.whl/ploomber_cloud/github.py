from pathlib import Path
import click
import requests

from ploomber_core.exceptions import modify_exceptions

from ploomber_cloud.exceptions import BasePloomberCloudException
from ploomber_cloud._telemetry import telemetry

GITHUB_DOCS_URL = "https://docs.cloud.ploomber.io/en/latest/user-guide/github.html"


def fetch_workflow_template_from_github():
    """Function to fetch the template GitHub workflow file"""
    yaml_file_url = "https://raw.githubusercontent.com/edublancas/cloud-template/main/.github/workflows/ploomber-cloud.yaml"  # noqa

    response = requests.get(yaml_file_url)

    if response.status_code == 200:
        return response.content
    else:
        raise BasePloomberCloudException(
            "Failed to fetch GitHub workflow template. Please refer: "
            f"{GITHUB_DOCS_URL}"
        )


def _create_github_workflow_file():
    """Function to create a local copy of the GitHub
    workflow template"""

    content = fetch_workflow_template_from_github()
    with open("./.github/workflows/ploomber-cloud.yaml", "wb") as file:
        file.write(content)
    click.echo(
        "'ploomber-cloud.yaml' file created in the path "
        ".github/workflows.\nPlease add, commit and push "
        "this file along with the 'ploomber-cloud.json' "
        "file to trigger an action.\nFor details on "
        "configuring a GitHub secret please refer: "
        f"{GITHUB_DOCS_URL}"
    )


def _workflow_file_exists():
    """Function to check if GitHub workflow file
    is present in repository"""
    return Path(".github", "workflows", "ploomber-cloud.yaml").exists()


def _workflow_needs_update():
    """Function to check if the GitHub workflow
    file needs to be updated with the latest template"""
    if _workflow_file_exists():
        latest_workflow_template = fetch_workflow_template_from_github()
        # Check if the workflow template has been updated
        if (
            Path(".github", "workflows", "ploomber-cloud.yaml").read_text().strip()
            != latest_workflow_template.decode("utf-8").strip()
        ):
            return True
    return False


def display_github_workflow_info_message():
    """Display informative messages on creation
    or updation of GitHub workflow file"""
    if Path(".git").is_dir():
        workflow_message = (
            f"To learn more about GitHub actions refer: {GITHUB_DOCS_URL}"
        )
        if _workflow_needs_update():
            click.echo(
                ".github/workflows/ploomber-cloud.yaml seems outdated. "
                "You may update it by running 'ploomber-cloud github'.\n"
                f"{workflow_message}"
            )

        elif _workflow_file_exists() is False:
            click.echo(
                "You may create a GitHub workflow file for "
                "deploying your application by running 'ploomber-cloud github'.\n"
                f"{workflow_message}"
            )


@modify_exceptions
@telemetry.log_call()
def github():
    """Create or update GitHub workflow file ploomber-cloud.yaml"""
    if Path(".git").is_dir():
        if Path(".github", "workflows", "ploomber-cloud.yaml").exists():
            if _workflow_needs_update():
                confirm_msg = (
                    "Please confirm that you want to update the GitHub workflow file"
                )
            else:
                click.echo("Workflow file is up-to-date.")
                return
        else:
            confirm_msg = (
                "Please confirm that you want to generate a GitHub workflow file"
            )
        create_github_action = click.confirm(confirm_msg)
        if create_github_action:
            Path(".github", "workflows").mkdir(exist_ok=True, parents=True)
            _create_github_workflow_file()
    else:
        raise BasePloomberCloudException(
            "Expected a .git/ directory in the current working "
            "directory. Run this from the repository root directory."
        )
