import pytest
from core.developer.project import ProjectAnalyzer

def test_project_analyzer(tmp_path):
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    
    analyzer = ProjectAnalyzer()
    index = analyzer.analyze(str(tmp_path))
    
    assert "TypeScript/JavaScript" in index.languages
    assert "npm" in index.package_managers
    assert "src" in index.source_directories
    assert "tests" in index.test_directories
    assert index.file_count == 1
