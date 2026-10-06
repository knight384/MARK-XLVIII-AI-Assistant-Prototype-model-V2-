import pytest
from pathlib import Path
import subprocess
from core.developer.git import GitIntelligence, GitError

def test_git_init_non_repo(tmp_path):
    gi = GitIntelligence(tmp_path)
    assert gi.is_git_repo() is False
    with pytest.raises(GitError):
        gi.status()

def test_git_path_boundary(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    gi = GitIntelligence(repo)
    
    with pytest.raises(ValueError, match="Path traversal detected"):
        gi.diff(file_path="../outside.txt")

def test_git_status_clean(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "Initial"], cwd=repo, check=True)
    
    gi = GitIntelligence(repo)
    status = gi.status()
    assert status.is_clean is True

def test_git_status_untracked(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    (repo / "new_file.txt").write_text("hello")
    
    gi = GitIntelligence(repo)
    status = gi.status()
    assert status.is_clean is False
    assert "new_file.txt" in status.untracked

def test_git_commit(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True)
    (repo / "new_file.txt").write_text("hello")
    subprocess.run(["git", "add", "new_file.txt"], cwd=repo, check=True)
    
    gi = GitIntelligence(repo)
    head = gi.commit("Add file")
    
    assert len(head) == 40
    status = gi.status()
    assert status.is_clean is True
