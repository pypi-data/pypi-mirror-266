import click
import time

from ploomber_core.exceptions import modify_exceptions

from ploomber_cloud import api, zip_
from ploomber_cloud.config import PloomberCloudConfig
from ploomber_cloud.github import display_github_workflow_info_message
from ploomber_cloud._telemetry import telemetry
from ploomber_cloud.util import print_divider

STATUS_COLOR = {
    "pending": "white",
    "active": "yellow",
    "finished": "green",
    "success": "green",
    "failed": "red",
    "inactive": "red",
    "stopped": "magenta",
}

FAILED_STATUSES = (
    "docker-failed",
    "provisioning-failed",
    "infrastructure-failed",
    "failed",
)

INTERVAL_SECS = 15.0
TIMEOUT_MINS = 15.0


def _unpack_job_status(job):
    """
    Format and output a job status message.
    Return job status (and URL if success).

    Parameters
    ----------
    job: JSON
        Contains job status information to output and process.

    Returns
    ----------
    job_status: str
        Status of job. Possible values: "success", "running", or "failed".

    app_url: str
        URL to view dashboard. Only returned if job_status == "success".
    """
    tasks = job["summary"]
    status_msg = []

    for name, status in tasks:
        status_msg.append(f"{name}: {click.style(status, fg=STATUS_COLOR[status])} | ")

    click.echo("".join(status_msg))

    # grab job status as reported by backend api
    status = job["status"]

    # job is running and reporting healthy
    if status == "running":
        return "success", job["resources"]["webservice"]

    # job has failed or stopped
    if status in FAILED_STATUSES:
        return "failed", None

    # job is still pending, continue watching
    return "pending", None


def _watch(client, project_id, job_id):
    """Display status bar and logs of project deployment"""
    start_time = time.time()
    interval = INTERVAL_SECS
    timeout = 60.0 * TIMEOUT_MINS

    # poll every 'interval' secs until 'timeout' mins
    while True:
        status_page = api.PloomberCloudEndpoints().status_page(project_id, job_id)

        curr_time = time.time()
        time_diff = curr_time - start_time

        if time_diff >= timeout:
            click.secho("Timeout reached.", fg="yellow")
            click.echo(f"For more details, go to: {status_page}")
            return

        # get job status and logs from API
        job = client.get_job_by_id(job_id)
        logs = client.get_job_logs_by_id(job_id)

        # decide which logs to show based on status
        logs_to_show = "build-docker"
        # if deploy-docker is finished, show webservice logs
        if job["summary"][1][1] in ("success", "finished"):
            logs_to_show = "webservice"

        curr_time_formatted = time.strftime("%H:%M:%S", time.localtime(curr_time))

        # Display link to status page, status bar, and logs
        click.clear()
        click.echo(
            f"[{curr_time_formatted}] \
Deploying project: {project_id} with job ID: {job_id}..."
        )
        print_divider()
        click.echo(f"Web status page: {status_page}")
        print_divider()
        job_status, app_url = _unpack_job_status(job)
        print_divider()
        click.echo(f"Showing {logs_to_show} logs...")
        print_divider()
        click.echo(logs["logs"][logs_to_show])

        # deploy has either succeeded or failed
        if job_status != "pending":
            click.secho(f"Deployment {job_status}.", fg=STATUS_COLOR[job_status])
            click.echo(f"View project dashboard: {status_page}")
            if job_status == "success":
                click.echo(f"View your deployed app: {app_url}")
            break

        time.sleep(interval - (time_diff % interval))


@modify_exceptions
@telemetry.log_call(log_args=True)
def deploy(watch):
    """Deploy a project to Ploomber Cloud, requires a project to be initialized"""
    print("deploying. watch:", watch)
    client = api.PloomberCloudClient()
    config = PloomberCloudConfig()
    config.load()

    with zip_.zip_app(verbose=True) as (path_to_zip, secrets):
        click.echo(f"Deploying project with id: {config.data['id']}...")
        output = client.deploy(
            path_to_zip=path_to_zip,
            project_type=config.data["type"],
            project_id=config.data["id"],
            secrets=secrets,
        )
        if watch:
            _watch(client, output["project_id"], output["id"])

    display_github_workflow_info_message()
