"""
小任务：定义领域对象结构
功能：定义 Prompt、DialogueSample、ScoreResult 的数据结构和基本属性，参考 schema.yml 和 P2.md
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class Prompt:
    content: str  # P2.md 的完整内容

@dataclass
class DialogueSample:
    id: str  # schema.yml: metadata.id
    date: Optional[str] = None  # schema.yml: metadata.date
    round5_parent: str = ""  # round_5_messages[0].content
    round5_coach: str = ""   # round_5_messages[1].content
    round10_parent: str = ""  # round_10_messages[0].content
    round10_coach: str = ""   # round_10_messages[1].content
    meta: Optional[Dict] = field(default_factory=dict)

@dataclass
class ScoreResult:
    sample_id: str
    output_json: Dict[str, Any]  # P2.md Output Format 生成的完整JSON
    machine_scores: Optional[Dict[str, float]] = None  # 可选：自动评分数值
    expert_scores: Optional[Dict[str, float]] = None   # 可选：专家评分数值
    error: Optional[float] = None
    extra: Optional[Dict] = field(default_factory=dict)
