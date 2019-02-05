import re
from functools import partial
from traceback import print_tb

import pytest
from more_itertools import ilen

from elisctl.workspace import create_command, list_command, delete_command
from tests.conftest import API_URL, TOKEN, match_uploaded_json

USERNAME = "test_user@rossum.ai"
PASSWORD = "secret"
ORGANIZATIONS_URL = f"{API_URL}/v1/organizations"
ORGANIZATION_ID = "1"
ORGANIZATION_URL = f"{ORGANIZATIONS_URL}/{ORGANIZATION_ID}"
WORKSPACES_URL = f"{API_URL}/v1/workspaces"
DOCUMENTS_URL = f"{API_URL}/v1/documents"
QUEUES_URL = f"{API_URL}/v1/queues"


@pytest.mark.runner_setup(
    env={"ELIS_URL": API_URL, "ELIS_USERNAME": USERNAME, "ELIS_PASSWORD": PASSWORD}
)
@pytest.mark.usefixtures("mock_login_request", "mock_organization_urls")
class TestCreate:
    def test_success(self, requests_mock, cli_runner):
        name = "TestName"
        new_id = "2"

        requests_mock.post(
            WORKSPACES_URL,
            additional_matcher=partial(
                match_uploaded_json, {"name": name, "organization": ORGANIZATION_URL}
            ),
            request_headers={"Authorization": f"Token {TOKEN}"},
            status_code=201,
            json={"id": new_id},
        )
        result = cli_runner.invoke(create_command, [name])
        assert not result.exit_code, print_tb(result.exc_info[2])
        assert f"{new_id}\n" == result.output


@pytest.mark.runner_setup(
    env={"ELIS_URL": API_URL, "ELIS_USERNAME": USERNAME, "ELIS_PASSWORD": PASSWORD}
)
@pytest.mark.usefixtures("mock_login_request")
class TestList:
    def test_success(self, requests_mock, cli_runner):
        workspace_id = 1
        name = "test@example.com"
        queue_id = 1

        queue_url = f"{QUEUES_URL}/{queue_id}"

        requests_mock.get(
            WORKSPACES_URL,
            json={
                "pagination": {"total": 1, "next": None},
                "results": [{"id": workspace_id, "queues": [queue_url], "name": name}],
            },
        )
        requests_mock.get(
            QUEUES_URL,
            json={
                "pagination": {"total": 1, "next": None},
                "results": [{"id": queue_id, "url": queue_url}],
            },
        )

        result = cli_runner.invoke(list_command)
        assert not result.exit_code, print_tb(result.exc_info[2])
        expected_table = f"""\
  id  name                queues
----  ----------------  --------
   {workspace_id}  {name}         {queue_id}
"""
        assert result.output == expected_table


@pytest.mark.runner_setup(
    env={"ELIS_URL": API_URL, "ELIS_USERNAME": USERNAME, "ELIS_PASSWORD": PASSWORD}
)
@pytest.mark.usefixtures("mock_login_request")
class TestDelete:
    def test_success(self, requests_mock, cli_runner):
        workspace_id = "1"
        queue_id = "1"
        workspace_url = f"{WORKSPACES_URL}/{workspace_id}"
        n_documents = 2

        requests_mock.get(
            workspace_url,
            request_headers={"Authorization": f"Token {TOKEN}"},
            json={"id": workspace_id, "url": workspace_url},
        )

        requests_mock.get(
            f"{QUEUES_URL}?workspace={workspace_id}",
            complete_qs=True,
            request_headers={"Authorization": f"Token {TOKEN}"},
            json={"pagination": {"next": None, "total": 1}, "results": [{"id": queue_id}]},
        )

        requests_mock.get(
            f"{API_URL}/v1/annotations?queue={queue_id}&page_size=50&sideload=documents",
            complete_qs=True,
            request_headers={"Authorization": f"Token {TOKEN}"},
            json={
                "pagination": {"next": None, "total": 1},
                "documents": [
                    {"id": i, "url": fr"{DOCUMENTS_URL}/{i}"} for i in range(n_documents)
                ],
            },
        )

        requests_mock.delete(
            workspace_url, request_headers={"Authorization": f"Token {TOKEN}"}, status_code=204
        )

        requests_mock.delete(
            re.compile(fr"{DOCUMENTS_URL}/\d+"),
            request_headers={"Authorization": f"Token {TOKEN}"},
            status_code=204,
        )
        result = cli_runner.invoke(delete_command, [workspace_id, "--yes"])
        assert not result.exit_code, print_tb(result.exc_info[2])
        assert not result.output
        assert (
            ilen(r for r in requests_mock.request_history if r.method == "DELETE")
            == n_documents + 1
        )
