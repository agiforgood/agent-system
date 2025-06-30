"""
小任务：实现 Prompt 文件加载功能的单元测试
目标：能正确读取并返回 prompts/P2.md 的内容，支持动态插值
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务
"""

import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
from repository.prompt_repository import PromptRepository

def test_load_prompt_file(tmp_path):
    # 创建临时的 prompts 目录和 P2.md 文件
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    prompt_file = prompts_dir / "P2.md"
    prompt_content = (
        "编号: [Current Dialogue ID, e.g., 42]\n"
        "round5: [Full text of Parent and Coach turns for round 5 from data/D1/*.yml]\n"
        "round10: [Full text of Parent and Coach turns for round 10 from data/D1/*.yml]"
    )
    prompt_file.write_text(prompt_content, encoding="utf-8")

    repo = PromptRepository()
    loaded_content = repo.load(
        str(prompt_file),
        id=42,
        round5="家长内容",
        round10="教练内容"
    )
    assert loaded_content == "编号: 42\nround5: 家长内容\nround10: 教练内容"

    # 测试无插值时原样返回
    loaded_content2 = repo.load(str(prompt_file))
    assert loaded_content2 == prompt_content

    # 测试插值缺失字段时报错
    try:
        repo.load(str(prompt_file), id=1)
        assert False, "缺失字段应抛出异常"
    except ValueError as e:
        assert "Prompt 模板插值失败" in str(e)
