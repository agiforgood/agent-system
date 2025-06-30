import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.json_report_to_tsv import json_report_to_tsv

def test_json_report_to_tsv(tmp_path):
    json_path = os.path.join(os.path.dirname(__file__), "..", "reports", "P2_eval_20250628.json")
    tsv_path = tmp_path / "out.tsv"
    json_report_to_tsv(json_path, str(tsv_path))
    # 检查文件存在且内容非空
    assert os.path.exists(tsv_path)
    with open(tsv_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    assert len(lines) > 1  # 至少有表头和一行数据
    assert '\t' in lines[0]  # 表头为TSV格式

def test_json_report_to_tsv_integration(tmp_path):
    # 使用真实的json报告
    json_path = os.path.join(os.path.dirname(__file__), "..", "reports", "P2_eval_20250628.json")
    tsv_path = tmp_path / "out.tsv"
    json_report_to_tsv(json_path, str(tsv_path))
    # 检查文件存在且内容非空
    assert os.path.exists(tsv_path)
    with open(tsv_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    assert len(lines) > 1  # 至少有表头和一行数据
    # 检查表头和部分字段
    header = lines[0].split('\t')
    assert "编号" in header
    assert "round5" in header
    assert "round10" in header
    # 检查每行字段数一致
    for line in lines[1:]:
        assert len(line.split('\t')) == len(header)
