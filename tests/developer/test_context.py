import pytest
from core.developer.context import SourceContextManager

def test_source_context_retrieval(tmp_path):
    file = tmp_path / "test.py"
    lines = [f"line {i}" for i in range(1, 100)]
    file.write_text("\n".join(lines))
    
    ctx = SourceContextManager(tmp_path)
    res = ctx.get_context("test.py", 50, 2, 2)
    
    expected = (
        "  48    line 48\n"
        "  49    line 49\n"
        "  50 >> line 50\n"
        "  51    line 51\n"
        "  52    line 52"
    )
    assert res == expected

def test_source_context_path_traversal(tmp_path):
    ctx = SourceContextManager(tmp_path)
    with pytest.raises(ValueError, match="Path traversal detected"):
        ctx.get_context("../outside.py", 10)
