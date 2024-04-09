from pathlib import Path
import click
import re

from ploomber_core.exceptions import modify_exceptions

from ploomber_cloud.exceptions import BasePloomberCloudException
from ploomber_cloud import api

from ploomber_cloud.constants import VALID_PROJECT_TYPES, VALID_DOCKER_PROJECT_TYPES
from ploomber_cloud.config import PloomberCloudConfig
from ploomber_cloud.github import display_github_workflow_info_message
from ploomber_cloud._telemetry import telemetry


def _check_imports_for_project_type(types):
    """Search app.py for imports to infer project type"""
    if not Path("app.py").exists():
        return None

    text = Path("app.py").read_text()
    for proj in types:
        regex_import = r"\bimport " + proj + r"\b"
        regex_from_import = r"\bfrom " + proj + r" import\b"
        if re.findall(regex_import, text) or re.findall(regex_from_import, text):
            return proj

    return None


def _infer_project_type():
    """Infer project type based on the existing files in the current directory"""
    native_type = _check_imports_for_project_type(sorted(list(VALID_PROJECT_TYPES)))
    docker_type = _check_imports_for_project_type(
        sorted(list(VALID_DOCKER_PROJECT_TYPES))
    )
    found_dockerfile = Path("Dockerfile").exists()

    if docker_type:
        click.echo(
            f"This looks like a {docker_type.capitalize()} project, \
which is supported via Docker."
        )
        if not found_dockerfile:
            click.secho(
                f"Your app is missing a Dockerfile. To learn more, \
go to: https://docs.cloud.ploomber.io/en/latest/apps/{docker_type}.html",
                fg="yellow",
            )
        return "docker"
    elif found_dockerfile:
        return "docker"
    elif Path("app.R").exists():
        return "shiny-r"
    elif Path("app.ipynb").exists():
        return "voila"
    elif native_type:
        return native_type
    else:
        return None


def _prompt_for_project_type(prefix=None):
    """Prompt the user for a project type"""
    prefix = prefix or ""
    click.echo(f"{prefix}Please specify one of: " f"{', '.join(VALID_PROJECT_TYPES)}")

    return click.prompt(
        "Project type",
        type=click.Choice(VALID_PROJECT_TYPES),
        show_choices=False,
    )


def _init_from_existing():
    """Generate ploomber-cloud.json from existing project"""
    click.echo("Initializing from existing project...")
    client = api.PloomberCloudClient()

    # Get user's available projects
    project_choices = [project["id"] for project in client.get_projects()["projects"]]
    if len(project_choices) == 0:
        click.echo("You have no existing projects. Initialize without --from-existing.")
        return

    project_choices.append("exit")
    prompt = ["These are your existing projects, choose the one you're configuring:\n"]
    for i, item in enumerate(project_choices):
        prompt.append(f"  {i+1}. {item}\n")
    prompt_str = "".join(prompt)

    # Prompt user for choice of existing project
    while True:
        choice = click.prompt(prompt_str, type=str)
        # Case: user enters number
        if choice.isnumeric() and 0 < int(choice) <= len(project_choices):
            choice = project_choices[int(choice) - 1]
            break
        elif choice in project_choices:  # Case: user enters id
            break
        else:  # Case: user enters invalid
            click.echo("Please enter a valid choice.")

    # Allow user to exit menu without init
    if choice == "exit":
        click.echo("Exited.")
        return

    # Call API to get project type
    click.echo(f"Configuring project with id '{choice}'.")
    config_json = {"id": choice}
    project_info = client.get_project_by_id(config_json["id"])
    config_json["type"] = project_info["type"]

    # Write id and type to ploomber-cloud.json
    config = PloomberCloudConfig()
    config.dump(config_json)

    click.echo(f"Your app {config_json['id']!r} has been configured successfully!")
    display_github_workflow_info_message()


@modify_exceptions
@telemetry.log_call(log_args=True)
def init(from_existing, force):
    """Initialize a project"""
    config = PloomberCloudConfig()

    if config.exists() and not force:
        config.load()
        raise BasePloomberCloudException(
            f"Project already initialized with id: {config.data['id']}. "
            "Run 'ploomber-cloud deploy' to deploy your project. "
            "To track its progress, add the --watch flag."
        )
    else:
        if from_existing:
            _init_from_existing()
            return

        if force:
            click.echo("Re-initializing project...")
        else:
            click.echo("Initializing new project...")

        project_type = _infer_project_type()

        if project_type is None:
            project_type = _prompt_for_project_type(
                prefix="Could not infer project type. "
            )
        else:
            click.echo(f"Inferred project type: {project_type!r}")
            correct_project_type = click.confirm("Is this correct?")

            if not correct_project_type:
                project_type = _prompt_for_project_type()

        client = api.PloomberCloudClient()
        output = client.create(project_type=project_type)
        config.dump(output)
        click.echo(f"Your app {output['id']!r} has been configured successfully!")
        display_github_workflow_info_message()
