"""
当前小任务：实现 raw 字段提取与解析方法
目标：实现一个方法，输入为 JSON 报告路径，输出为所有解析成功的 raw 字段的 dict 列表。
TDD：写测试用例，给定一个含 raw 字段的 JSON，断言能正确解析为 dict。
"""
import json
import re
from typing import List, Dict

def extract_and_parse_raw_fields(json_report_path: str) -> List[Dict]:
    """
    读取 JSON 报告，提取每个 result 的 output_json["raw"] 字段，解析为 dict。
    返回所有解析成功的 dict 列表。
    """
    with open(json_report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    results = report.get('results', [])
    parsed = []
    for r in results:
        raw = r.get('output_json', {}).get('raw')
        if not raw:
            continue
        # 去除 markdown 代码块包裹
        raw_clean = re.sub(r'^```json\n|```$', '', raw.strip())
        try:
            d = json.loads(raw_clean)
            parsed.append(d)
        except Exception as e:
            print(f"解析失败: sample_id={r.get('sample_id')}, error={e}")
    return parsed
