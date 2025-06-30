"""
小任务：实现 Prompt 文件加载功能
功能：读取指定路径的 Prompt 文件内容并返回字符串，支持动态插值，适配 P2.md 作为 Prompt 模板
"""

import re


class PromptRepository:
    def load(self, filepath: str, **kwargs) -> str:
        """
        读取 Prompt 文件内容，并用自定义占位符进行插值（仅替换[]包裹的特殊标记，避免与JSON花括号冲突）。
        用法示例：repo.load('prompts/P2.md', id=13, round5='...', round10='...')
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        # 只替换[]包裹的自定义占位符
        if kwargs:
            # 替换 [Current Dialogue ID, e.g., 16]
            if 'id' not in kwargs or 'round5' not in kwargs or 'round10' not in kwargs:
                raise ValueError("Prompt 模板插值失败: 缺少必要字段")
            content = re.sub(r'\[Current Dialogue ID, e\.g\.,? ?\d+\]', str(kwargs.get('id', '')), content)
            content = re.sub(r'\[Full text of Parent and Coach turns for round 5 from data/D1/\*\.yml\]', str(kwargs.get('round5', '')), content)
            content = re.sub(r'\[Full text of Parent and Coach turns for round 10 from data/D1/\*\.yml\]', str(kwargs.get('round10', '')), content)
        return content
