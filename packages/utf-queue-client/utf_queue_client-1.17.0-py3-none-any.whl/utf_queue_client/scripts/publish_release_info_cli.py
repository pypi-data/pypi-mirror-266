import click
from utf_queue_client.scripts import setup_telemetry
from retry import retry
from typing import Iterable, Tuple
from otel_extensions import instrumented
import requests

NUM_RETRIES = 6


@click.command()
@click.option(
    "--username",
    type=str,
    required=True,
    help="username",
)
@click.option(
    "--password",
    type=str,
    required=True,
    help="password",
)
@click.option(
    "--data",
    multiple=True,
    type=(str, str),
    required=True,
    help="data in dictionary format",
)
def cli_entrypoint(username, password, data):
    cli(username, password, data)


def cli(username: str, password: str, data: Iterable[Tuple[str, str]]):
    with setup_telemetry():
        data_dict = {}
        for key, value in data:
            data_dict[key] = value

        @retry(Exception, delay=5, backoff=2, max_delay=30, tries=NUM_RETRIES + 1)
        def retry_wrapper():
            response = publish_release_information(username, password, data_dict)
            if response is not None:
                update_artifacts_retention_days_to_keep_forever(data_dict)
        retry_wrapper()


@instrumented
def publish_release_information(username: str, password: str, data_dict: dict):
    url = 'https://auth.silabs.net/api/v1/auth'

    # Create a dictionary with the username and password
    credentials = {
        'username': username,
        'password': password
    }

    try:
        response = requests.post(url, json=credentials, verify=False)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes

        # Extract the JWT token from the response
        jwt_token = response.json()['access_token']

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

    url = 'https://releaseinfo.silabs.net/api/v1/releases'

    # Create the Authorization header with the Bearer token
    headers = {
        'Authorization': f'JWT {jwt_token}'
    }

    # Send the POST request with the headers
    response = requests.post(url, json=data_dict, headers=headers, verify=False)

    # Check the response status code
    if response.status_code == 201:
        # Request successful
        print('Publish release information successful!')
        print('Response:', response.json())
        return True
    else:
        # Request failed
        print('Publish release information failed.')
        print('Status Code:', response.status_code)
        return None


@instrumented
def update_artifacts_retention_days_to_keep_forever(data_dict: dict):
    url = 'https://ubai.silabs.net/api/v1/artifacts'

    artifact_search_spec = {
        "metadata": {
            "branch": data_dict["branchName"],
            "build_number": data_dict["SDKBuildNum"]
        },
        "retentionDays": -1
    }

    # Send the PATCH request with the headers
    response = requests.patch(url, json=artifact_search_spec, verify=False)

    # Check the response status code
    if response.status_code == 200:
        # Request successful
        print("Updated Retention days in UBAI for release artifact to keep forever!")
        print("Response:", response.json())
    else:
        # Request failed
        print('Update Retention days in UBAI for release artifact to keep forever failed.')
        print('Status Code:', response.status_code)
        print('Response:', response.json())
        return None


if __name__ == "__main__":
    cli_entrypoint()
