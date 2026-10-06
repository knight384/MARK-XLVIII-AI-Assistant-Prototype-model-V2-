import pytest
from core.developer.search import CodeSearcher

def test_bounded_code_search(tmp_path):
    # Setup files
    (tmp_path / "test.py").write_text("def hello():\n    print('hello world')")
    (tmp_path / "other.js").write_text("console.log('hello there');")
    
    searcher = CodeSearcher(tmp_path)
    res = searcher.search("hello")
    
    assert res.truncated is False
    assert len(res.matches) == 3
    
def test_search_file_size_limit(tmp_path):
    searcher = CodeSearcher(tmp_path)
    searcher.MAX_FILE_SIZE = 10  # 10 bytes max
    
    # Exceeds max file size
    (tmp_path / "test.py").write_text("def hello():\n    print('hello world')")
    
    res = searcher.search("hello")
    assert len(res.matches) == 0
