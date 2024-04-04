import json
import pytest
import asyncio

from unittest.mock import ANY, Mock, patch, MagicMock
from ..handlers import register_handlers, InstanceMetricsHandler, GitCloneHandler


@pytest.fixture
def jp_server_config(jp_template_dir):
    return {
        "ServerApp": {"jpserver_extensions": {"sagemaker_jupyterlab_extension": True}},
    }


def test_mapping_added():
    mock_nb_app = Mock()
    mock_web_app = Mock()
    mock_nb_app.web_app = mock_web_app
    mock_web_app.settings = {"base_url": "nb_base_url"}
    register_handlers(mock_nb_app)
    mock_web_app.add_handlers.assert_called_once_with(".*$", ANY)


# We need to mock the log method from handler class to prevent from invoking
# internal code from common package during unit testing.
@patch("sagemaker_jupyterlab_extension.handlers.InstanceMetricsHandler.log")
async def test_get_instance_metrics_success(mock_logger, jp_fetch):
    mock_logger.return_value = "someInfoLog"
    response = await jp_fetch("/aws/sagemaker/api/instance/metrics", method="GET")
    resp = json.loads(response.body.decode("utf-8"))
    assert response.code == 200

    # Assert metric attributes are present metrics is populated
    metrics_object = resp["metrics"]
    assert "memory" in metrics_object
    assert "cpu" in metrics_object
    assert "storage" in metrics_object

    # Assert attributes of memory present
    memory_metric = resp["metrics"]["memory"]
    assert memory_metric is not None
    assert "rss_in_bytes" in memory_metric
    assert "total_in_bytes" in memory_metric
    assert "memory_percentage" in memory_metric

    # Assert CPU metrics is populated
    cpu_metric = resp["metrics"]["cpu"]
    assert cpu_metric is not None
    assert "cpu_count" in cpu_metric
    assert "cpu_percentage" in cpu_metric

    # Assert Disk usage metrics is populated
    storage_metric = resp["metrics"]["storage"]
    assert storage_metric is not None


@patch.object(
    InstanceMetricsHandler, "get", side_effect=Exception("No parent process found")
)
async def test_get_instance_metrics_failed(jp_fetch):
    with pytest.raises(Exception) as e:
        await jp_fetch("/aws/sagemaker/api/instance/metrics", method="GET")
    assert str(e.value) == "No parent process found"


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.handlers._get_domain_repositories")
@patch(
    "sagemaker_jupyterlab_extension.handlers._get_user_profile_and_space_repositories"
)
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util._get_space_settings")
@patch(
    "sagemaker_jupyterlab_extension.handlers.GitCloneHandler.log",
    return_value="infoLogs",
)
async def test_get_git_repositories_empty_userprofile_repositories_success(
    mock_logger,
    mock_get_space_settings,
    mock_get_profile_repositories,
    mock_get_domain_repo,
    jp_fetch,
):
    mock_get_domain_repo.return_value = ["https://github.com/domain/domain.git"]
    mock_get_space_settings.return_value = {
        "CodeRepositories": [],
        "OwnerUserProfileName": "test-profile",
    }
    mock_get_profile_repositories.return_value = []
    response = await jp_fetch("/aws/sagemaker/api/git/list-repositories", method="GET")
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {"GitCodeRepositories": ["https://github.com/domain/domain.git"]}


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.handlers._get_domain_repositories")
@patch(
    "sagemaker_jupyterlab_extension.handlers._get_user_profile_and_space_repositories"
)
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util._get_space_settings")
@patch(
    "sagemaker_jupyterlab_extension.handlers.GitCloneHandler.log",
    return_value="someInfoLog",
)
async def test_get_git_repositories_success(
    mock_logger,
    mock_get_space_settings,
    mock_get_profile_repositories,
    mock_get_domain_repo,
    jp_fetch,
):
    mock_get_domain_repo.return_value = ["https://github.com/domain/domain.git"]
    mock_get_space_settings.return_value = {
        "CodeRepositories": ["https://github.com/space/space.git"],
        "OwnerUserProfileName": "test-profile",
    }
    mock_get_profile_repositories.return_value = [
        "https://github.com/user/userprofile.git",
        "https://github.com/space/space.git",
    ]
    response = await jp_fetch("/aws/sagemaker/api/git/list-repositories", method="GET")
    resp = json.loads(response.body.decode("utf-8"))
    assert resp.get("GitCodeRepositories") is not None
    assert set(resp.get("GitCodeRepositories")) == set(
        [
            "https://github.com/domain/domain.git",
            "https://github.com/user/userprofile.git",
            "https://github.com/space/space.git",
        ]
    )


@patch.object(
    GitCloneHandler, "get", side_effect=Exception("Internal Server error occurred")
)
async def test_get_git_repositories_failure(jp_fetch):
    with pytest.raises(Exception) as e:
        await jp_fetch("/aws/sagemaker/api/git/list-repositories", method="GET")
    assert str(e.value) == "Internal Server error occurred"
