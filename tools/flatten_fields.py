"""
当前小任务：实现字段拉平与字段名自动收集
目标：实现一个方法，将所有 dict 的 key 自动收集，确保所有样本的字段齐全（缺失字段补空）。
TDD：写pytest单元测试，输入多条 dict，断言输出的字段名集合和每行字段齐全。
"""
from typing import List, Dict, Tuple

def flatten_dicts_and_collect_fields(dicts: List[Dict]) -> Tuple[List[str], List[Dict]]:
    """
    输入：dict列表
    输出：所有字段名（去重排序）和拉平成齐全字段的dict列表（缺失字段补空字符串）
    """
    all_fields = set()
    for d in dicts:
        all_fields.update(d.keys())
    all_fields = sorted(all_fields)
    flat_rows = []
    for d in dicts:
        row = {k: d.get(k, "") for k in all_fields}
        flat_rows.append(row)
    return all_fields, flat_rows
