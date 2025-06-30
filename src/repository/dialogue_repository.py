"""
小任务：实现 D1 数据集加载功能
功能：读取 data/D1 目录下所有 yml 文件，解析为 DialogueSample 对象列表，适配 schema.yml 格式
"""

import os
import yaml
from typing import List
from domain.domain_objects import DialogueSample

class DialogueRepository:
    def load_all(self, dir_path: str) -> List[DialogueSample]:
        samples = []
        for fname in os.listdir(dir_path):
            if fname.endswith('.yml') or fname.endswith('.yaml'):
                fpath = os.path.join(dir_path, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    meta = data.get('conversation', {}).get('metadata', {})
                    round5 = data.get('conversation', {}).get('round_5_messages', [])
                    round10 = data.get('conversation', {}).get('round_10_messages', [])
                    sample = DialogueSample(
                        id=meta.get('id', fname),
                        date=meta.get('date'),
                        round5_parent=round5[0]['content'] if len(round5) > 0 else '',
                        round5_coach=round5[1]['content'] if len(round5) > 1 else '',
                        round10_parent=round10[0]['content'] if len(round10) > 0 else '',
                        round10_coach=round10[1]['content'] if len(round10) > 1 else '',
                        meta=meta
                    )
                    samples.append(sample)
        return samples

    def load(self, dir_path: str) -> List[DialogueSample]:
        # 兼容主流程调用，等价于 load_all
        return self.load_all(dir_path)
