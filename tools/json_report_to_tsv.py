"""
当前小任务：集成方法：一键从 JSON 报告生成 TSV
目标：实现一个高阶方法，串联前面步骤，输入 JSON 报告路径和 TSV 输出路径，一键完成转换。
TDD：写集成测试，断言调用后 TSV 文件存在且内容正确。
"""
import os
from tools.extract_raw_fields import extract_and_parse_raw_fields
from tools.flatten_fields import flatten_dicts_and_collect_fields
from tools.write_tsv import write_tsv

def json_report_to_tsv(json_path: str, tsv_path: str):
    """
    一键从 JSON 报告生成 TSV 文件
    """
    dicts = extract_and_parse_raw_fields(json_path)
    fields, rows = flatten_dicts_and_collect_fields(dicts)
    write_tsv(rows, fields, tsv_path)
