from pathlib import Path
from typing import Optional

from .models import ProjectIndex

class ProjectAnalyzer:
    """Bounded repository intelligence abstraction."""
    
    IGNORE_DIRS = {".git", "node_modules", "venv", "__pycache__", "dist", "build", ".pytest_cache", ".idea", ".vscode", "vendor"}
    MAX_FILES = 10_000
    
    def analyze(self, path: str) -> ProjectIndex:
        root = Path(path).resolve()
        if not root.is_dir():
            raise ValueError(f"Path is not a directory: {root}")
            
        git_root = self._find_git_root(root)
        
        languages = set()
        package_managers = set()
        src_dirs = []
        test_dirs = []
        build_configs = []
        
        file_count = 0
        
        # Bounded scan
        for item in root.iterdir():
            if file_count > self.MAX_FILES:
                break
                
            if item.is_file():
                file_count += 1
                name = item.name
                if name == "package.json":
                    package_managers.add("npm")
                    languages.add("TypeScript/JavaScript")
                elif name in ("requirements.txt", "pyproject.toml", "setup.py"):
                    package_managers.add("pip")
                    languages.add("Python")
                elif name == "pom.xml":
                    package_managers.add("maven")
                    languages.add("Java")
                elif name == "go.mod":
                    package_managers.add("go mod")
                    languages.add("Go")
                elif name in ("Makefile", "CMakeLists.txt", "build.gradle", "docker-compose.yml"):
                    build_configs.append(name)
            elif item.is_dir() and item.name not in self.IGNORE_DIRS:
                name_lower = item.name.lower()
                if name_lower in ("src", "source", "app", "lib", "core", "internal"):
                    src_dirs.append(item.name)
                elif name_lower in ("tests", "test", "spec", "specs", "e2e"):
                    test_dirs.append(item.name)
                    
        return ProjectIndex(
            root_path=str(root),
            git_root=str(git_root) if git_root else None,
            languages=sorted(list(languages)),
            package_managers=sorted(list(package_managers)),
            source_directories=sorted(src_dirs),
            test_directories=sorted(test_dirs),
            build_configs=sorted(build_configs),
            file_count=file_count
        )

    def _find_git_root(self, current: Path) -> Optional[Path]:
        while current != current.parent:
            if (current / ".git").is_dir():
                return current
            current = current.parent
        return None
