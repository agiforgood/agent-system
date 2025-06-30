import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.flatten_fields import flatten_dicts_and_collect_fields
import pytest

def test_flatten_dicts_and_collect_fields():
    dicts = [
        {"a": 1, "b": 2},
        {"b": 3, "c": 4},
        {"a": 5, "c": 6, "d": 7}
    ]
    fields, rows = flatten_dicts_and_collect_fields(dicts)
    assert set(fields) == {"a", "b", "c", "d"}
    assert len(rows) == 3
    # 检查每行字段齐全
    for row in rows:
        for k in fields:
            assert k in row
    # 检查缺失字段补空
    assert rows[0]["c"] == ""
    assert rows[1]["a"] == ""
    assert rows[2]["b"] == ""

if __name__ == "__main__":
    pytest.main([__file__])
