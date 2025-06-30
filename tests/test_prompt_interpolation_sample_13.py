import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from repository.prompt_repository import PromptRepository
from domain.domain_objects import DialogueSample

def test_prompt_interpolation_sample_13():
    # 构造 sample_13.yml 对应的 DialogueSample
    sample = DialogueSample(
        id="13",
        date="2025-05-23",
        round5_parent="小孩子懂什么情感！就应该掐灭在萌芽里，不然等发展起来就晚了！",
        round5_coach="你觉得对待孩子刚刚萌发的情感和好奇心，最直接有效的方式就是\"掐灭\"，能否分享一下你尝试这样做之后，通常会看到什么样的结果？",
        round10_parent="她能有什么感觉？小孩子家家的，父母关心不是应该的吗？我小时候我妈管我严多了！",
        round10_coach="你提到你妈妈当年管你更严，你还记得那时候当你妈妈非常严格地关心你时，你内心的感受是怎样的吗？"
    )
    round5 = "家长：" + sample.round5_parent + "\n" + "教练：" + sample.round5_coach
    round10 = "家长：" + sample.round10_parent + "\n" + "教练：" + sample.round10_coach
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "P2.md")
    prompt_repo = PromptRepository()
    prompt_text = prompt_repo.load(
        prompt_path,
        id=sample.id,
        编号=sample.id,
        对话编号=sample.id,
        round5=round5,
        round10=round10
    )
    print("\n===== Interpolated Prompt for sample_13 =====\n")
    print(prompt_text)
    print("\n===== END =====\n")

if __name__ == "__main__":
    test_prompt_interpolation_sample_13()
