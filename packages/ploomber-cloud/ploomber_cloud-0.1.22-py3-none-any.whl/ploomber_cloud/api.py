import os

import click
import requests

from ploomber_cloud import exceptions, client
from ploomber_cloud.constants import FORCE_INIT_MESSAGE

# mapping to easily switch between environments
HOSTS = {
    "prod": {
        "api": "https://cloud-prod.ploomber.io",
        "dashboard": "https://www.platform.ploomber.io",
    },
    "dev": {
        "api": "https://cloud-dev.ploomber.io",
        "dashboard": "https://www.platform-dev.ploomber.io",
    },
    "local": {
        "api": "http://localhost:8000",
        "dashboard": "http://localhost:3000",
    },
}


class PloomberCloudEndpoints:
    """Manages URLs depending on the environment set in _PLOOMBER_CLOUD_ENV"""

    def __init__(self) -> None:
        _ploomber_cloud_env = os.environ.get("_PLOOMBER_CLOUD_ENV", "prod")

        if _ploomber_cloud_env not in HOSTS:
            raise exceptions.BasePloomberCloudException(
                f"Unknown environment: {_ploomber_cloud_env}. "
                "Valid options are: prod, dev, local"
            )

        self._ploomber_cloud_host_api = HOSTS[_ploomber_cloud_env]["api"]
        self._ploomber_cloud_host_dashboard = HOSTS[_ploomber_cloud_env]["dashboard"]

    @property
    def API_ROOT(self):
        return self._ploomber_cloud_host_api

    def status_page(self, project_id, job_id):
        return f"{self._ploomber_cloud_host_dashboard}/applications/{project_id}/{job_id}"  # noqa


endpoints = PloomberCloudEndpoints()
API_ROOT = endpoints.API_ROOT


class PloomberCloudClient(client.PloomberBaseClient):
    """Client for the Ploomber Cloud API"""

    def _process_response(self, response):
        """Process response and raise an exception if the status code is not 200"""
        if response.ok:
            return response.json()
        else:
            error_message = response.json()["detail"]
            # if project is deleted from app re-initialization
            # required with new config file
            if response.status_code == 404:
                error_message = f"{error_message}\n{FORCE_INIT_MESSAGE}"
            raise exceptions.BasePloomberCloudException(
                f"An error occurred: {error_message}"
            )

    def me(self):
        """Return information about the current user"""
        response = requests.get(
            f"{API_ROOT}/users/me",
            headers={
                "api_key": self.api_key,
                "Content-Type": "application/json",
            },
        )

        response.raise_for_status()

    def get_projects(self):
        """Return user's current projects"""
        response = requests.get(
            f"{API_ROOT}/projects",
            headers=self._get_headers(),
        )

        return self._process_response(response)

    def get_project_by_id(self, id):
        """Return a specific project by ID"""
        response = requests.get(
            f"{API_ROOT}/projects/{id}",
            headers=self._get_headers(),
        )

        return self._process_response(response)

    def create(self, project_type):
        """Create a new project"""
        response = requests.post(
            f"{API_ROOT}/projects/{project_type}",
            headers=self._get_headers(),
        )

        return self._process_response(response)

    def delete(self, project_id):
        """Create a new project"""
        response = requests.delete(
            f"{API_ROOT}/projects/{project_id}",
            headers=self._get_headers(),
        )

        return self._process_response(response)

    def deploy(self, path_to_zip, project_type, project_id, secrets=None):
        """Deploy a project"""

        with open(path_to_zip, "rb") as file:
            files = {
                "files": (
                    "app.zip",
                    file,
                    "application/zip",
                ),
            }
            data = {
                "secrets": secrets,
            }
            response = requests.post(
                f"{API_ROOT}/jobs/webservice/{project_type}?project_id={project_id}",
                headers=self._get_headers(),
                files=files,
                data=data,
            )

        output = self._process_response(response)
        url = endpoints.status_page(output["project_id"], output["id"])

        click.echo(f"The deployment process started! Track its status at: {url}")

        return output

    def get_job_by_id(self, id):
        """Return job summary by job id"""
        response = requests.get(
            f"{API_ROOT}/jobs/{id}",
            headers=self._get_headers(),
        )

        return self._process_response(response)

    def get_job_logs_by_id(self, id):
        """Return docker logs and webservice logs by job id"""
        response = requests.get(
            f"{API_ROOT}/jobs/{id}/logs",
            headers=self._get_headers(),
        )

        return self._process_response(response)
