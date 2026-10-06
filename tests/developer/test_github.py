import pytest
from unittest.mock import patch, MagicMock
from core.developer.github import GitHubClient, GitHubError

@patch("urllib.request.urlopen")
@patch("core.developer.github.get_config_service")
def test_github_get_repository(mock_get_config, mock_urlopen):
    mock_get_config.return_value.get.return_value = "fake_token"
    
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"name": "test-repo", "private": true, "html_url": "http://git/test-repo", "default_branch": "main"}'
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp
    
    client = GitHubClient()
    repo = client.get_repository("owner", "test-repo")
    
    assert repo.name == "test-repo"
    assert repo.private is True

@patch("urllib.request.urlopen")
@patch("core.developer.github.get_config_service")
def test_github_token_redaction(mock_get_config, mock_urlopen):
    import urllib.error
    mock_get_config.return_value.get.return_value = "fake_token"
    
    mock_resp = MagicMock()
    mock_resp.read.return_value = b'{"message": "Not found"}'
    
    mock_urlopen.side_effect = urllib.error.HTTPError("http://git", 404, "Not Found", {}, mock_resp)
    
    client = GitHubClient()
    with pytest.raises(GitHubError) as exc:
        client.get_repository("owner", "test-repo")
        
    # Ensure token is not in the exception message
    assert "fake_token" not in str(exc.value)
