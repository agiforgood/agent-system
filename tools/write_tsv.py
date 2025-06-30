"""
当前小任务：实现 TSV 文件写出方法
目标：实现一个方法，输入 dict 列表和字段名，输出为标准 TSV 文件。
TDD：写pytest单元测试，断言生成的 TSV 文件内容与预期一致。
"""
import csv
from typing import List

def write_tsv(dict_rows: List[dict], fieldnames: List[str], tsv_path: str):
    """
    将 dict_rows 按 fieldnames 顺序写入 tsv 文件，首行为字段名。
    """
    with open(tsv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
        writer.writeheader()
        for row in dict_rows:
            writer.writerow(row)
