import subprocess
from pathlib import Path
import logging
from typing import List, Optional

from .models import GitStatus, GitCommit

logger = logging.getLogger(__name__)

class GitError(Exception):
    """Base exception for Git operations."""
    pass

class GitCommandError(GitError):
    def __init__(self, command: str, stderr: str, returncode: int):
        self.command = command
        self.stderr = stderr
        self.returncode = returncode
        super().__init__(f"Git command failed: {command}\n{stderr}")

class GitIntelligence:
    """Bounded, safe Git interactions. Never uses shell=True. Prevents path escapes."""
    
    def __init__(self, workspace_root: str | Path):
        self.root = Path(workspace_root).resolve()
        if not self.root.is_dir():
            raise ValueError(f"Workspace root does not exist or is not a directory: {self.root}")

    def _verify_path(self, path: str | Path) -> Path:
        """Ensure path is within the workspace."""
        p = (self.root / path).resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError(f"Path traversal detected. {path} escapes {self.root}")
        return p

    def _run_git(self, args: List[str], cwd: Optional[Path] = None, timeout: int = 15) -> str:
        """Safely execute git with no shell injection."""
        working_dir = cwd or self.root
        self._verify_path(working_dir)
        
        # Obfuscate tokens in args if any slip through
        clean_args = []
        for arg in args:
            if "://" in arg and "@" in arg:
                # Naive redaction for logging/error messages
                import re
                arg = re.sub(r'://[^@]+@', '://***@', arg)
            clean_args.append(arg)

        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=str(working_dir),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                encoding="utf-8",
                errors="replace"
            )
            
            # Truncate output to prevent memory DOS
            stdout = result.stdout[:500_000]
            stderr = result.stderr[:500_000]

            if result.returncode != 0:
                raise GitCommandError(" ".join(cmd), stderr, result.returncode)
                
            return stdout
        except subprocess.TimeoutExpired:
            raise GitError(f"Git command timed out after {timeout} seconds.")
        except FileNotFoundError:
            raise GitError("Git executable not found in system PATH.")

    def is_git_repo(self) -> bool:
        return (self.root / ".git").is_dir()

    def status(self) -> GitStatus:
        if not self.is_git_repo():
            raise GitError("Not a Git repository.")

        # Porcelein v1 is stable
        out = self._run_git(["status", "--porcelain", "-b"])
        
        staged = []
        unstaged = []
        untracked = []
        conflicted = []
        branch = ""
        ahead = 0
        behind = 0
        
        lines = out.splitlines()
        if not lines:
            return GitStatus(is_clean=True, current_branch="")

        for line in lines:
            if line.startswith("##"):
                branch_info = line[3:].strip()
                if "..." in branch_info:
                    parts = branch_info.split("...")
                    branch = parts[0]
                    if "[" in branch_info:
                        tracking = branch_info[branch_info.index("[")+1:-1]
                        import re
                        m_ahead = re.search(r"ahead (\d+)", tracking)
                        m_behind = re.search(r"behind (\d+)", tracking)
                        if m_ahead: ahead = int(m_ahead.group(1))
                        if m_behind: behind = int(m_behind.group(1))
                else:
                    branch = branch_info.split(" ")[0]
                continue

            if len(line) < 3:
                continue
                
            xy = line[:2]
            path = line[3:].strip()
            
            if xy in ("UU", "AA", "DD", "AU", "UA", "UD", "DU"):
                conflicted.append(path)
                continue
                
            if xy == "??":
                untracked.append(path)
                continue
                
            x, y = xy[0], xy[1]
            if x != " " and x != "?":
                staged.append(path)
            if y != " " and y != "?":
                unstaged.append(path)

        is_clean = not (staged or unstaged or untracked or conflicted)
        return GitStatus(
            is_clean=is_clean,
            staged=staged,
            unstaged=unstaged,
            untracked=untracked,
            conflicted=conflicted,
            ahead=ahead,
            behind=behind,
            current_branch=branch
        )

    def current_branch(self) -> str:
        return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()

    def branches(self) -> List[str]:
        out = self._run_git(["branch", "--format=%(refname:short)"])
        return [b.strip() for b in out.splitlines() if b.strip()]

    def log(self, max_count: int = 10) -> List[GitCommit]:
        out = self._run_git([
            "log", 
            f"-n{max_count}", 
            "--format=%H%x00%an%x00%aI%x00%B%x1E"
        ])
        commits = []
        for block in out.split('\x1E'):
            if not block.strip():
                continue
            parts = block.strip().split('\x00', 3)
            if len(parts) == 4:
                commits.append(GitCommit(
                    hash=parts[0],
                    author=parts[1],
                    date=parts[2],
                    message=parts[3].strip()
                ))
        return commits

    def diff(self, staged: bool = False, file_path: Optional[str] = None) -> str:
        args = ["diff"]
        if staged:
            args.append("--cached")
        if file_path:
            self._verify_path(file_path)
            args.extend(["--", file_path])
        return self._run_git(args)

    def commit(self, message: str, allow_empty: bool = False) -> str:
        """Create a commit. This is a WRITE operation."""
        status = self.status()
        if status.conflicted:
            raise GitError("Cannot commit: repository has unresolved conflicts.")
        if not status.staged and not allow_empty:
            raise GitError("Cannot commit: no staged changes.")
            
        args = ["commit", "-m", message]
        if allow_empty:
            args.append("--allow-empty")
            
        out = self._run_git(args)
        
        # Verify
        head = self._run_git(["rev-parse", "HEAD"]).strip()
        if not head:
            raise GitError("Commit verification failed: HEAD unresolvable.")
            
        return head

    def fetch(self, remote: str = "origin") -> None:
        self._run_git(["fetch", remote])

    def pull(self, remote: str = "origin", branch: Optional[str] = None) -> None:
        if not branch:
            branch = self.current_branch()
        self._run_git(["pull", remote, branch])

    def push(self, remote: str = "origin", branch: Optional[str] = None) -> None:
        if not branch:
            branch = self.current_branch()
        self._run_git(["push", remote, branch])

    def remote_url(self, remote: str = "origin") -> str:
        return self._run_git(["remote", "get-url", remote]).strip()
