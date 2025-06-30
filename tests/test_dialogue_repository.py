"""
小任务：实现 D1 数据集加载功能
目标：能正确读取 data/D1/*.yml 并解析为对话样本对象
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务
"""

import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
from repository.dialogue_repository import DialogueRepository
import yaml

def test_load_all_dialogues(tmp_path):
    # 创建临时 data/D1 目录和两个 yml 文件
    d1_dir = tmp_path / "data" / "D1"
    d1_dir.mkdir(parents=True)
    sample1 = {"id": 1, "text": "对话样本1"}
    sample2 = {"id": 2, "text": "对话样本2"}
    (d1_dir / "sample_1.yml").write_text(yaml.dump(sample1), encoding="utf-8")
    (d1_dir / "sample_2.yml").write_text(yaml.dump(sample2), encoding="utf-8")

    repo = DialogueRepository()
    samples = repo.load_all(str(d1_dir))
    assert len(samples) == 2
    assert samples[0]["id"] == 1
    assert samples[1]["id"] == 2

"""
小任务：实现 D1 数据集加载功能的单元测试
目标：能正确读取 data/D1/*.yml 并解析为结构化 DialogueSample 对象，字段适配 schema.yml
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务
"""

import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
from repository.dialogue_repository import DialogueRepository
from domain.domain_objects import DialogueSample
import yaml

def test_load_all_dialogues(tmp_path):
    # 创建临时 data/D1 目录和一个 yml 文件，内容模拟 schema.yml
    d1_dir = tmp_path / "data" / "D1"
    d1_dir.mkdir(parents=True)
    sample_data = {
        "conversation": {
            "metadata": {"id": "sample-id", "date": "2025-05-23"},
            "round_5_messages": [
                {"role": "parent", "content": "家长消息5"},
                {"role": "coach", "content": "教练回复5"}
            ],
            "round_10_messages": [
                {"role": "parent", "content": "家长消息10"},
                {"role": "coach", "content": "教练回复10"}
            ]
        }
    }
    (d1_dir / "sample_1.yml").write_text(yaml.dump(sample_data), encoding="utf-8")

    repo = DialogueRepository()
    samples = repo.load_all(str(d1_dir))
    assert len(samples) == 1
    s = samples[0]
    assert s.id == "sample-id"
    assert s.date == "2025-05-23"
    assert s.round5_parent == "家长消息5"
    assert s.round5_coach == "教练回复5"
    assert s.round10_parent == "家长消息10"
    assert s.round10_coach == "教练回复10"
    assert s.meta["id"] == "sample-id"
