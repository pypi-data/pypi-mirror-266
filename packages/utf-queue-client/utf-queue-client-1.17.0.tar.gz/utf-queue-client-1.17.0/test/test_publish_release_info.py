import pytest
from otel_extensions import inject_context_to_env, instrumented
import os
import subprocess
import sys
from utf_queue_client.scripts.publish_release_info_cli import publish_release_information, update_artifacts_retention_days_to_keep_forever
import requests
from unittest import mock
from unittest.mock import MagicMock, patch


@pytest.fixture
def publish_release_info():
    yield [
        ("releaseDate", "2023-06-16"),
        ("branchName", "release/gecko_sdk_3.2"),
        ("releaseType", "GA"),
        ("releaseName", "23Q2-GA"),
        ("SDKBuildNum", "407"),
        ("installerURLSDK", "https://jenkins-cbs-gecko-sdk.silabs.net/job/Gecko_SDK_Suite_super/job/release%252F21q4/284/"),
        ("IARVersionNum", "9.20.4"),
        ("GCCVersionNum", "10.3.1"),
        ("CommanderVersionNum", "v1.8.1"),
        ("SEVersionNum", "1.2.4"),
        ("WSTKFirmwareVersionNum", "v1.4.4")
    ]


@instrumented
def test_publish_release_info(request, publish_release_info):
    args = ["--username", "svc_sqabot", "--password", "password"]
    for k, v in publish_release_info:
        args += ["--data", k, v]

    base_dir = os.path.dirname(os.path.dirname(__file__))
    @inject_context_to_env
    def call_cli_script():
        assert "TRACEPARENT" in os.environ
        process = subprocess.Popen(
            [
                sys.executable,
                os.path.join(
                    base_dir, "utf_queue_client", "scripts", "publish_release_info_cli.py"
                ),
            ]
            + args,
        )
        process.communicate()
        assert process.poll() == 0

    call_cli_script()


def test_publish_release_information():
    requests_post = requests.post
    requests.post = MagicMock()
    publish_release_information("", "", {})
    assert requests.post.call_count == 2
    requests.post = requests_post


def test_update_artifacts_retention_days_to_keep_forever():
    requests_patch = requests.patch
    requests.patch = MagicMock()
    data_dict = {"branchName": "release/gec", "SDKBuildNum": "407"}
    update_artifacts_retention_days_to_keep_forever(data_dict)
    assert requests.patch.call_count == 1
    requests.patch = requests_patch
    patch_response = MagicMock()
    mocked_patch =mock.patch.object(requests, "patch", return_value=patch_response)
    patch_response.status_code = 200
    update_artifacts_retention_days_to_keep_forever(data_dict)
