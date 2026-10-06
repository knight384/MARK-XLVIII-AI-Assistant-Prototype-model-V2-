from pathlib import Path

class SourceContextManager:
    """Bounded source context retrieval."""
    
    MAX_FILE_SIZE = 1_000_000  # 1MB
    MAX_LINES = 500

    def __init__(self, workspace_root: str | Path):
        self.root = Path(workspace_root).resolve()
        if not self.root.is_dir():
            raise ValueError(f"Workspace root is not a directory: {self.root}")

    def get_context(self, file_path: str, line_number: int, lines_before: int = 10, lines_after: int = 10) -> str:
        """Retrieves a bounded excerpt around a specific line."""
        
        target = (self.root / file_path).resolve()
        if self.root not in target.parents and target != self.root:
            raise ValueError(f"Path traversal detected: {file_path}")
            
        if not target.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if target.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {file_path}")
            
        if lines_before + lines_after + 1 > self.MAX_LINES:
            raise ValueError(f"Context window too large (max {self.MAX_LINES} lines).")
            
        start_line = max(1, line_number - lines_before)
        end_line = line_number + lines_after
        
        excerpt = []
        try:
            with open(target, "r", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if i > end_line:
                        break
                    if i >= start_line:
                        marker = ">> " if i == line_number else "   "
                        excerpt.append(f"{i:4d} {marker}{line.rstrip()}")
        except UnicodeDecodeError:
            raise ValueError(f"Cannot decode file as text: {file_path}")
            
        return "\n".join(excerpt)
