from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class GitCommit:
    hash: str
    author: str
    date: str
    message: str

@dataclass
class GitStatus:
    is_clean: bool
    staged: List[str] = field(default_factory=list)
    unstaged: List[str] = field(default_factory=list)
    untracked: List[str] = field(default_factory=list)
    conflicted: List[str] = field(default_factory=list)
    ahead: int = 0
    behind: int = 0
    current_branch: str = ""

@dataclass
class GitHubRepositoryMetadata:
    owner: str
    name: str
    description: Optional[str]
    private: bool
    url: str
    default_branch: str
    permissions: Dict[str, bool] = field(default_factory=dict)

@dataclass
class ProjectIndex:
    root_path: str
    git_root: Optional[str]
    languages: List[str]
    package_managers: List[str]
    source_directories: List[str]
    test_directories: List[str]
    build_configs: List[str]
    file_count: int

@dataclass
class SearchResultItem:
    file_path: str
    line_number: int
    content: str

@dataclass
class SearchResult:
    query: str
    matches: List[SearchResultItem]
    truncated: bool = False
    error: Optional[str] = None
