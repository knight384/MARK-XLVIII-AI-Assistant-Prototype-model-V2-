import os
from pathlib import Path
import time
from typing import List, Optional

from .models import SearchResult, SearchResultItem

class CodeSearcher:
    """Bounded, safe code search. Prevents deep recursion and huge files."""
    
    IGNORE_DIRS = {".git", "node_modules", "venv", "__pycache__", "dist", "build", ".pytest_cache", ".idea", ".vscode", "vendor"}
    MAX_FILE_SIZE = 1_000_000  # 1MB
    MAX_FILES_SCANNED = 10_000
    MAX_RESULTS = 100
    TIMEOUT_SEC = 5.0

    def __init__(self, workspace_root: str | Path):
        self.root = Path(workspace_root).resolve()
        if not self.root.is_dir():
            raise ValueError(f"Workspace root is not a directory: {self.root}")

    def search(self, query: str) -> SearchResult:
        start_time = time.time()
        matches = []
        files_scanned = 0
        truncated = False
        
        for root_dir, dirs, files in os.walk(self.root):
            if time.time() - start_time > self.TIMEOUT_SEC:
                truncated = True
                break
                
            # Filter directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            for file in files:
                if files_scanned >= self.MAX_FILES_SCANNED or len(matches) >= self.MAX_RESULTS:
                    truncated = True
                    break
                
                if not file.endswith((".py", ".js", ".ts", ".go", ".java", ".json", ".md", ".txt", ".yml", ".yaml", ".html", ".css", ".rs", ".cpp", ".c", ".h")):
                    continue

                path = Path(root_dir) / file
                try:
                    if path.stat().st_size > self.MAX_FILE_SIZE:
                        continue
                        
                    with open(path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            if query in line:
                                rel_path = path.relative_to(self.root).as_posix()
                                matches.append(SearchResultItem(
                                    file_path=rel_path,
                                    line_number=i,
                                    content=line.rstrip()
                                ))
                                if len(matches) >= self.MAX_RESULTS:
                                    break
                except Exception:
                    pass  # Ignore decode errors or permission errors
                    
                files_scanned += 1
                
            if truncated:
                break
                
        return SearchResult(query=query, matches=matches, truncated=truncated)
