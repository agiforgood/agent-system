import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.write_tsv import write_tsv

def test_write_tsv(tmp_path):
    # 构造测试数据
    fieldnames = ["a", "b", "c"]
    dict_rows = [
        {"a": 1, "b": 2, "c": 3},
        {"a": 4, "b": 5, "c": 6},
        {"a": 7, "b": 8, "c": 9}
    ]
    tsv_path = tmp_path / "test.tsv"
    write_tsv(dict_rows, fieldnames, str(tsv_path))
    # 读取并断言内容
    with open(tsv_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    assert lines[0] == "a\tb\tc"
    assert lines[1] == "1\t2\t3"
    assert lines[2] == "4\t5\t6"
    assert lines[3] == "7\t8\t9"
