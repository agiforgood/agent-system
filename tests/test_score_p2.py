"""
测试目标：
  覆盖 score_p2.py 的主要功能，包括数据加载、评分流程、指标计算、并发与重试逻辑。
开发方式：
  TDD，DDD，ReactiveX 并发。
验收标准：
  所有核心功能均有单元测试覆盖，便于重构和持续集成。
开发节奏：
  采用“小步快跑”TDD，每次只实现一个10分钟内可完成的小功能，配套单元测试，测试通过后再进入下一个功能开发。
Copilot 请聚焦当前小目标，逐步推进。
"""
import sys
import os
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)
scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

"""
小任务：实现评分流程的 RxPY 并发管道（Mock）
目标：多条对话评分能并发执行，结果全部收集。
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务。
"""
import pytest
from service.prompt_evaluator import PromptEvaluator
from domain.domain_objects import Prompt, DialogueSample
import rx
import rx.operators as ops
from rx.scheduler import ThreadPoolScheduler

def test_rxpy_parallel_score():
    prompt = Prompt(content="测试Prompt for rxpy")
    samples = [
        DialogueSample(id=f"id-{i}", round5_parent="p", round5_coach="c", round10_parent="p10", round10_coach="c10")
        for i in range(5)
    ]
    evaluator = PromptEvaluator(mode="mock")
    scheduler = ThreadPoolScheduler(2)
    results = []
    rx.from_iterable(samples).pipe(
        ops.flat_map(lambda s: rx.just(s).pipe(
            ops.map(lambda x: evaluator.score(prompt, x)),
            ops.subscribe_on(scheduler)
        ))
    ).subscribe(results.append)
    import time; time.sleep(1)  # 等待线程池完成
    assert len(results) == 5
    for r in results:
        assert r.extra.get("llm") == "mock"
        assert r.output_json.get("score")

"""
小任务：实现自动重试机制
目标：评分失败时能自动重试最多3次。
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务。
"""
def test_rxpy_score_with_retry():
    prompt = Prompt(content="测试Prompt for retry")
    # 构造部分会失败的样本
    class FailingEvaluator(PromptEvaluator):
        def __init__(self):
            super().__init__(mode="mock")
            self.call_count = {}
        def score(self, prompt, sample):
            # 第一次遇到每个样本都抛异常，第二次正常
            cnt = self.call_count.get(sample.id, 0)
            self.call_count[sample.id] = cnt + 1
            if cnt < 1:
                raise Exception("mock fail")
            return super().score(prompt, sample)
    samples = [DialogueSample(id=f"id-{i}", round5_parent="p", round5_coach="c", round10_parent="p10", round10_coach="c10") for i in range(3)]
    evaluator = FailingEvaluator()
    scheduler = ThreadPoolScheduler(2)
    results = []
    rx.from_iterable(samples).pipe(
        ops.flat_map(lambda s: rx.just(s).pipe(
            ops.map(lambda x: evaluator.score(prompt, x)),
            ops.retry(3),
            ops.subscribe_on(scheduler)
        ))
    ).subscribe(results.append)
    import time; time.sleep(1)
    assert len(results) == 3
    for r in results:
        assert r.extra.get("llm") == "mock"
        assert r.output_json.get("score")

"""
小任务：实现四维平均分统计功能
目标：输入多条评分结果，能正确计算四维平均分。
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务。
"""
def test_score_aggregator_mean():
    # 构造模拟评分结果，output_json 内含四维分
    from domain.domain_objects import ScoreResult
    results = []
    for i in range(4):
        results.append(ScoreResult(
            sample_id=f"id-{i}",
            output_json={
                "empathy": 3 + i % 2,
                "positive_regard": 4,
                "concreteness": 2 + i,
                "immediacy": 5 - i
            },
            machine_scores=None, expert_scores=None, error=None, extra={}
        ))
    import score_p2
    mean_scores = score_p2.ScoreAggregator.mean(results)
    assert isinstance(mean_scores, dict)
    assert set(mean_scores.keys()) == {"empathy", "positive_regard", "concreteness", "immediacy"}
    # 检查均值正确
    assert abs(mean_scores["empathy"] - 3.5) < 1e-6
    assert abs(mean_scores["positive_regard"] - 4.0) < 1e-6
    assert abs(mean_scores["concreteness"] - 3.5) < 1e-6
    assert abs(mean_scores["immediacy"] - 3.5) < 1e-6

"""
小任务：实现与专家分差距指标计算
目标：能计算 RMSE、Spearman ρ。
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务。
"""
import math
import numpy as np
def test_score_aggregator_metrics():
    # 构造模拟评分结果，output_json 内含四维分，expert_scores 为专家分
    from domain.domain_objects import ScoreResult
    import random
    results = []
    for i in range(10):
        results.append(ScoreResult(
            sample_id=f"id-{i}",
            output_json={
                "empathy": 3 + random.randint(-1, 1),
                "positive_regard": 4 + random.randint(-1, 1),
                "concreteness": 2 + random.randint(-1, 1),
                "immediacy": 5 + random.randint(-1, 1)
            },
            machine_scores=None,
            expert_scores={
                "empathy": 3,
                "positive_regard": 4,
                "concreteness": 2,
                "immediacy": 5
            },
            error=None, extra={}
        ))
    import score_p2
    rmse = score_p2.ScoreAggregator.rmse(results)
    spearman = score_p2.ScoreAggregator.spearman(results)
    assert isinstance(rmse, dict)
    assert isinstance(spearman, dict)
    for k in ["empathy", "positive_regard", "concreteness", "immediacy"]:
        assert k in rmse
        assert k in spearman
        val = spearman[k]
        # 允许 None 或 nan
        if val is not None:
            assert np.isnan(val) or (0 <= abs(val) <= 1)

"""
小任务：实现 Top-5 误判样例筛选功能
目标：能找出分差最大的5条样本。
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务。
"""
def test_score_aggregator_top5_misjudge():
    from domain.domain_objects import ScoreResult
    import random
    results = []
    # 构造10条样本，分差逐渐增大
    for i in range(10):
        results.append(ScoreResult(
            sample_id=f"id-{i}",
            output_json={"empathy": 3, "positive_regard": 4, "concreteness": 2, "immediacy": 5},
            machine_scores=None,
            expert_scores={"empathy": 3 + i, "positive_regard": 4, "concreteness": 2, "immediacy": 5},
            error=None, extra={}
        ))
    import score_p2
    top5 = score_p2.ScoreAggregator.top5_misjudge(results)
    assert isinstance(top5, list)
    assert len(top5) == 5
    # 分差最大的样本id应为id-9, id-8, ... id-5
    top_ids = [r.sample_id for r in top5]
    assert top_ids == [f"id-{i}" for i in range(9, 4, -1)]

"""
小任务：实现 JSON 报告与终端摘要输出
目标：能正确生成 JSON 文件和终端摘要内容。
TDD：先写测试，再实现功能，测试通过后再进入下一个小任务。
"""
def test_score_report_and_summary(tmp_path):
    import score_p2
    import json
    from domain.domain_objects import ScoreResult
    # 构造3条样本
    results = [
        ScoreResult(
            sample_id=f"id-{i}",
            output_json={"empathy": 3+i, "positive_regard": 4, "concreteness": 2, "immediacy": 5},
            machine_scores=None, expert_scores=None, error=None, extra={}
        ) for i in range(3)
    ]
    mean_scores = score_p2.ScoreAggregator.mean(results)
    report_path = tmp_path / "report.json"
    score_p2.save_json_report(results, mean_scores, str(report_path))
    # 检查 JSON 文件内容
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "results" in data and "mean_scores" in data
    assert len(data["results"]) == 3
    # 测试终端摘要输出
    summary = score_p2.summary_text(mean_scores)
    assert "empathy" in summary and "positive_regard" in summary

"""
集成测试：主流程命令行参数，mock模式下全流程跑通，验证 JSON 报告和终端摘要。
"""
import subprocess
import sys
import tempfile
import os
import json
import score_p2

def test_main_integration(tmp_path, monkeypatch):
    # 构造 mock Prompt 和数据集
    prompt_path = tmp_path / "P2.md"
    data_dir = tmp_path / "D1"
    data_dir.mkdir()
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write("测试Prompt内容")
    # 构造2条样本yml
    for i in range(2):
        with open(data_dir / f"sample_{i}.yml", "w", encoding="utf-8") as f:
            f.write(f"id: id-{i}\nround5_parent: p\nround5_coach: c\nround10_parent: p10\nround10_coach: c10\n")
    out_path = tmp_path / "report.json"
    # monkeypatch service.prompt_evaluator.PromptEvaluator 为 mock
    import service.prompt_evaluator as pe
    monkeypatch.setattr(pe, "PromptEvaluator", lambda mode="mock": pe.PromptEvaluator(mode="mock"))
    import score_p2
    sys_argv = sys.argv
    sys.argv = ["score_p2.py", "--prompt", str(prompt_path), "--data", str(data_dir), "--out", str(out_path)]
    try:
        score_p2.main()
        # 检查输出文件
        with open(out_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "results" in data and "mean_scores" in data
        assert len(data["results"]) == 2
    finally:
        sys.argv = sys_argv
