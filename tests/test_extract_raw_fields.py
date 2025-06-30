import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.extract_raw_fields import extract_and_parse_raw_fields

def test_extract_and_parse_raw_fields():
    test_path = os.path.join(os.path.dirname(__file__), "..", "reports", "P2_eval_20250628.json")
    dicts = extract_and_parse_raw_fields(test_path)
    assert isinstance(dicts, list)
    assert len(dicts) > 0, "raw 字段解析结果应大于0条"
    for d in dicts:
        assert isinstance(d, dict)
