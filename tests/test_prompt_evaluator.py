"""
小任务：实现单条对话评分的接口（Mock LLM）单元测试
目标：输入 Prompt 和 DialogueSample，能返回模拟评分结果 ScoreResult
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务
"""

import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
from service.prompt_evaluator import PromptEvaluator
from domain.domain_objects import Prompt, DialogueSample, ScoreResult
import pytest

def test_score_mock_llm():
    prompt = Prompt(content="测试Prompt")
    sample = DialogueSample(
        id="sample-id",
        round5_parent="家长消息5",
        round5_coach="教练回复5",
        round10_parent="家长消息10",
        round10_coach="教练回复10"
    )
    evaluator = PromptEvaluator(mode="mock")
    result = evaluator.score(prompt, sample)
    assert isinstance(result, ScoreResult)
    assert result.sample_id == "sample-id"
    assert result.machine_scores is None
    assert result.error is None
    assert result.extra.get("llm") == "mock"

# 跳过已废弃的 requests 相关测试
@pytest.mark.skip(reason="requests.post 已不再用于实现，且本地无 requests 包")
def test_score_deepseek_http_error(monkeypatch):
    prompt = Prompt(content="测试Prompt")
    sample = DialogueSample(id="sample-id", round5_parent="家长消息5", round5_coach="教练回复5", round10_parent="家长消息10", round10_coach="教练回复10")
    evaluator = PromptEvaluator()
    # 模拟 requests.post 抛出异常
    def mock_post(*args, **kwargs):
        raise Exception("mock http error")
    monkeypatch.setattr("requests.post", mock_post)
    result = evaluator.score(prompt, sample)
    assert isinstance(result, ScoreResult)
    assert "error" in result.output_json


@pytest.mark.skip(reason="requests.post 已不再用于实现，且本地无 requests 包")
def test_score_deepseek_parse_error(monkeypatch):
    prompt = Prompt(content="测试Prompt")
    sample = DialogueSample(id="sample-id", round5_parent="家长消息5", round5_coach="教练回复5", round10_parent="家长消息10", round10_coach="教练回复10")
    evaluator = PromptEvaluator()
    # 模拟返回无法解析的 json
    class MockResp:
        def raise_for_status(self):
            pass
        def json(self):
            return {"choices": [{"message": {"content": "not a json string"}}]}
    monkeypatch.setattr("requests.post", lambda *a, **k: MockResp())
    result = evaluator.score(prompt, sample)
    assert isinstance(result, ScoreResult)
    assert "error" in result.output_json


def test_score_deepseek_http_error_v2(monkeypatch):
    prompt = Prompt(content="测试Prompt")
    sample = DialogueSample(id="sample-id", round5_parent="家长消息5", round5_coach="教练回复5", round10_parent="家长消息10", round10_coach="教练回复10")
    evaluator = PromptEvaluator()
    # 模拟 client.chat.completions.create 抛出异常
    class MockClient:
        class chat:
            class completions:
                @staticmethod
                def create(*args, **kwargs):
                    raise Exception("mock http error")
    evaluator.client = MockClient()
    result = evaluator.score(prompt, sample)
    assert isinstance(result, ScoreResult)
    assert "error" in result.output_json


def test_score_deepseek_parse_error_v2(monkeypatch):
    prompt = Prompt(content="测试Prompt")
    sample = DialogueSample(id="sample-id", round5_parent="家长消息5", round5_coach="教练回复5", round10_parent="家长消息10", round10_coach="教练回复10")
    evaluator = PromptEvaluator()
    # 模拟返回无法解析的 json
    class MockResp:
        class choices:
            class message:
                content = "not a json string"
        def __getattr__(self, item):
            return self.choices
    class MockClient:
        class chat:
            class completions:
                @staticmethod
                def create(*args, **kwargs):
                    class R:
                        choices = [type('msg', (), {"message": type('m', (), {"content": "not a json string"})()})]
                    return R()
    evaluator.client = MockClient()
    result = evaluator.score(prompt, sample)
    assert isinstance(result, ScoreResult)
    assert "raw" in result.output_json or "error" in result.output_json


def test_score_mock_mode():
    prompt = Prompt(content="测试Prompt for mock")
    sample = DialogueSample(
        id="mock-id",
        round5_parent="家长消息5",
        round5_coach="教练回复5",
        round10_parent="家长消息10",
        round10_coach="教练回复10"
    )
    evaluator = PromptEvaluator(mode="mock")
    result = evaluator.score(prompt, sample)
    assert isinstance(result, ScoreResult)
    assert result.sample_id == "mock-id"
    assert isinstance(result.output_json, dict)
    assert "score" in result.output_json
    assert result.output_json["explanation"].startswith("This is a mock score")
    assert result.extra.get("llm") == "mock"
    assert result.error is None


def test_score_llm_deepseek(monkeypatch):
    prompt = Prompt(content="测试Prompt")
    sample = DialogueSample(
        id="sample-id",
        round5_parent="家长消息5",
        round5_coach="教练回复5",
        round10_parent="家长消息10",
        round10_coach="教练回复10"
    )
    # mock DeepSeekLLM，避免真实API调用
    class DummyDeepSeekLLM:
        def __init__(self, api_key=None, base_url=None, model=None):
            pass
        def score(self, prompt, sample):
            return {"score": 5, "explanation": "dummy", "raw": "..."}
    monkeypatch.setattr("service.prompt_evaluator.DeepSeekLLM", DummyDeepSeekLLM)
    evaluator = PromptEvaluator(mode="real", llm="deepseek")
    result = evaluator.score(prompt, sample)
    assert isinstance(result, ScoreResult)
    assert result.output_json["score"] == 5
    assert result.extra.get("llm") == "deepseek"


def test_score_deepseek_http_error_v2(monkeypatch):
    prompt = Prompt(content="测试Prompt")        
    sample = DialogueSample(id="sample-id", round5_parent="家长消息5", round5_coach="教练回复5", round10_parent="家长消息10", round10_coach="教练回复10")  
    # mock DeepSeekLLM.score 抛出异常
    class DummyDeepSeekLLM:
        def __init__(self, *a, **kw):
            pass
        def score(self, prompt, sample):
            raise Exception("mock http error")
    monkeypatch.setattr("service.prompt_evaluator.DeepSeekLLM", DummyDeepSeekLLM)
    evaluator = PromptEvaluator(mode="real", llm="deepseek")
    result = evaluator.score(prompt, sample)
    assert isinstance(result, ScoreResult)
    assert "error" in result.output_json
