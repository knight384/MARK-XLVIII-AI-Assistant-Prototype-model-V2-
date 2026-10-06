import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

from core.config import get_config_service
from .models import GitHubRepositoryMetadata

logger = logging.getLogger(__name__)

class GitHubError(Exception):
    pass

class GitHubClient:
    """Bounded GitHub API interactions. Never logs tokens. Requires token via config."""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        # Fetch securely from ConfigService/SecretStore
        self._token = get_config_service().get("github_token")

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        url = f"{self.BASE_URL}{endpoint}"
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "MARK-XLVIII-V2"
        }
        
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        req_data = None
        if data:
            req_data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode("utf-8")
                return json.loads(content) if content else None
        except urllib.error.HTTPError as e:
            # Do NOT log the exception directly if it might contain the request with auth headers
            error_body = e.read().decode("utf-8")
            raise GitHubError(f"GitHub API {method} {endpoint} failed: {e.code} {e.reason} - {error_body}")
        except urllib.error.URLError as e:
            raise GitHubError(f"Network error communicating with GitHub: {e.reason}")

    def get_repository(self, owner: str, repo: str) -> GitHubRepositoryMetadata:
        """READ operation: get repository metadata."""
        data = self._request("GET", f"/repos/{owner}/{repo}")
        
        return GitHubRepositoryMetadata(
            owner=owner,
            name=data["name"],
            description=data.get("description"),
            private=data.get("private", False),
            url=data.get("html_url", ""),
            default_branch=data.get("default_branch", "main"),
            permissions=data.get("permissions", {})
        )

    def create_repository(self, name: str, description: str = "", private: bool = True) -> str:
        """WRITE operation: create a new repository for the authenticated user."""
        if not self._token:
            raise GitHubError("Authentication required to create a repository.")
            
        data = self._request("POST", "/user/repos", data={
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True
        })
        
        return data.get("html_url", "")
