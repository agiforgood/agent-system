"""
小任务：定义领域对象结构的单元测试
目标：验证 Prompt、DialogueSample、ScoreResult 的数据结构和属性，覆盖 schema.yml 和 P2.md 的主要字段
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务
"""

import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
from domain.domain_objects import Prompt, DialogueSample, ScoreResult

def test_prompt():
    p = Prompt(content="test prompt")
    assert p.content == "test prompt"

def test_dialogue_sample():
    d = DialogueSample(
        id="sample-id",
        date="2025-05-23",
        round5_parent="家长消息5",
        round5_coach="教练回复5",
        round10_parent="家长消息10",
        round10_coach="教练回复10",
        meta={"source": "test"}
    )
    assert d.id == "sample-id"
    assert d.date == "2025-05-23"
    assert d.round5_parent == "家长消息5"
    assert d.round5_coach == "教练回复5"
    assert d.round10_parent == "家长消息10"
    assert d.round10_coach == "教练回复10"
    assert d.meta["source"] == "test"

def test_score_result():
    output_json = {"编号": 1, "round5": "内容", "对话编号": 1}
    s = ScoreResult(
        sample_id="sample-id",
        output_json=output_json,
        machine_scores={"empathy": 4.5},
        expert_scores={"empathy": 5.0},
        error=0.5,
        extra={"note": "test"}
    )
    assert s.sample_id == "sample-id"
    assert s.output_json["编号"] == 1
    assert s.machine_scores["empathy"] == 4.5
    assert s.expert_scores["empathy"] == 5.0
    assert s.error == 0.5
    assert s.extra["note"] == "test"
