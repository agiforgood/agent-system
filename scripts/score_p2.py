"""
任务目标：
  自动评估 prompts/P2.md 在 data/D1 上的四维分、误差、Top-5 误判。
开发方式：
  TDD（测试驱动开发），DDD（领域驱动设计），并发处理用 ReactiveX（RxPY）及 scheduler。
输入输出：
  输入：prompts/P2.md, data/D1/*.yml
  输出：reports/P2_eval_<timestamp>.json，终端摘要
验收标准：
  50 条样例 ≤ 10 分钟，自动重试，JSON 报告 + 终端摘要
开发节奏：
  采用“小步快跑”TDD，每次只实现一个10分钟内可完成的小功能，配套单元测试，测试通过后再进入下一个功能开发。
Copilot 请聚焦当前小目标，逐步推进。
"""

"""
小任务：实现评分流程的 RxPY 并发管道（Mock）
功能：并发对多条 DialogueSample 进行评分，收集所有结果。
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from service.prompt_evaluator import PromptEvaluator
from domain.domain_objects import Prompt, DialogueSample
import rx
from rx.scheduler import ThreadPoolScheduler
from rx import operators as ops

def rxpy_parallel_score(prompt, samples, max_workers=4):
    evaluator = PromptEvaluator(mode="mock")
    scheduler = ThreadPoolScheduler(max_workers)
    results = []
    rx.from_iterable(samples).pipe(
        rx.operators.flat_map(lambda s: rx.just(s).map(lambda x: evaluator.score(prompt, x)).subscribe_on(scheduler))
    ).subscribe(results.append)
    import time; time.sleep(1)  # 等待线程池完成
    return results

"""
小任务：实现自动重试机制
功能：在 RxPY 并发评分管道中集成 retry，评分失败时自动重试最多3次。
"""
def rxpy_parallel_score_with_retry(prompt, samples, max_workers=4, retry_count=3):
    evaluator = PromptEvaluator(mode="mock")
    scheduler = ThreadPoolScheduler(max_workers)
    results = []
    rx.from_iterable(samples).pipe(
        ops.flat_map(lambda s: rx.just(s).pipe(
            ops.map(lambda x: evaluator.score(prompt, x)),
            ops.retry(retry_count),
            ops.subscribe_on(scheduler)
        ))
    ).subscribe(results.append)
    import time; time.sleep(1)
    return results

"""
小任务：实现四维平均分统计功能
功能：输入多条评分结果，能正确计算 empathy、positive_regard、concreteness、immediacy 四维均值。
"""
import math
from scipy.stats import spearmanr
class ScoreAggregator:
    @staticmethod
    def mean(score_results):
        keys = ["empathy", "positive_regard", "concreteness", "immediacy"]
        sums = {k: 0.0 for k in keys}
        count = 0
        for r in score_results:
            for k in keys:
                v = r.output_json.get(k)
                if v is not None:
                    sums[k] += float(v)
            count += 1
        return {k: (sums[k] / count if count else 0.0) for k in keys}

    @staticmethod
    def rmse(score_results):
        keys = ["empathy", "positive_regard", "concreteness", "immediacy"]
        sums = {k: 0.0 for k in keys}
        count = {k: 0 for k in keys}
        for r in score_results:
            for k in keys:
                m = r.output_json.get(k)
                e = None
                if r.expert_scores:
                    e = r.expert_scores.get(k)
                if m is not None and e is not None:
                    sums[k] += (float(m) - float(e)) ** 2
                    count[k] += 1
        return {k: math.sqrt(sums[k] / count[k]) if count[k] else None for k in keys}

    @staticmethod
    def spearman(score_results):
        keys = ["empathy", "positive_regard", "concreteness", "immediacy"]
        result = {}
        for k in keys:
            machine = []
            expert = []
            for r in score_results:
                m = r.output_json.get(k)
                e = None
                if r.expert_scores:
                    e = r.expert_scores.get(k)
                if m is not None and e is not None:
                    machine.append(float(m))
                    expert.append(float(e))
            if len(machine) > 1:
                rho, _ = spearmanr(machine, expert)
                result[k] = rho
            else:
                result[k] = None
        return result

    @staticmethod
    def top5_misjudge(score_results):
        # 以四维分差平方和为误差，取Top-5
        keys = ["empathy", "positive_regard", "concreteness", "immediacy"]
        def diff(r):
            if not r.expert_scores:
                return -1
            s = 0.0
            for k in keys:
                m = r.output_json.get(k)
                e = r.expert_scores.get(k) if r.expert_scores else None
                if m is not None and e is not None:
                    s += (float(m) - float(e)) ** 2
            return s
        sorted_results = sorted(score_results, key=diff, reverse=True)
        return sorted_results[:5]

import json
def save_json_report(results, mean_scores, path):
    # 生成 JSON 报告
    data = {
        "results": [r.__dict__ for r in results],
        "mean_scores": mean_scores
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def summary_text(mean_scores):
    # 生成终端摘要
    lines = ["评分均值摘要："]
    for k, v in mean_scores.items():
        lines.append(f"{k}: {v:.2f}")
    return "\n".join(lines)

"""
主流程：命令行参数 --prompt --data --out，批量加载数据，调用真实 deepseek，输出 JSON 报告和终端摘要。
"""
import argparse
import glob
import yaml
import datetime
from repository.prompt_repository import PromptRepository
from repository.dialogue_repository import DialogueRepository
from service.prompt_evaluator import PromptEvaluator
from domain.domain_objects import ScoreResult

def main():
    parser = argparse.ArgumentParser(description="自动评估 prompts/P2.md 在 data/D1 上的四维分、误差、Top-5 误判")
    parser.add_argument('--prompt', required=True, help='Prompt 文件路径')
    parser.add_argument('--data', required=True, help='数据集目录')
    parser.add_argument('--out', required=True, help='输出 JSON 路径')
    args = parser.parse_args()

    # 加载 Prompt
    prompt_repo = PromptRepository()
    prompt = prompt_repo.load(args.prompt)

    # 加载数据集
    dialogue_repo = DialogueRepository()
    samples = dialogue_repo.load(args.data)

    # 动态调整并发度，最大不超过16
    max_workers = min(16, max(8, len(samples) // 4))

    # 评分
    max_workers = min(len(samples), 16)
    def score_one(sample):
        round5 = "家长：" + sample.round5_parent + "\n" + "教练：" + sample.round5_coach
        round10 = "家长：" + sample.round10_parent + "\n" + "教练：" + sample.round10_coach
        prompt_text = prompt_repo.load(
            args.prompt,
            id=sample.id,
            round5=round5,
            round10=round10
        )
        prompt_obj = Prompt(content=prompt_text)
        return evaluator.score(prompt_obj, sample)

    evaluator = PromptEvaluator(mode="real")
    from rx import from_iterable
    from rx.scheduler import ThreadPoolScheduler
    from rx import operators as ops
    scheduler = ThreadPoolScheduler(max_workers)
    results = []
    import threading
    from tqdm import tqdm
    progress = tqdm(total=len(samples), desc="评分进度", ncols=80)
    lock = threading.Lock()
    def on_next(r):
        with lock:
            results.append(r)
            progress.update(1)
    (
        from_iterable(samples)
        .pipe(
            ops.map(score_one),
            ops.subscribe_on(scheduler),
            ops.do_action(on_next)
        )
        .run()
    )
    progress.close()

    # 统计
    mean_scores = ScoreAggregator.mean(results)
    rmse = ScoreAggregator.rmse(results)
    spearman = ScoreAggregator.spearman(results)
    top5 = ScoreAggregator.top5_misjudge(results)

    # 输出 JSON
    save_json_report(results, mean_scores, args.out)

    # 同步生成 TSV 文件
    try:
        from tools.json_report_to_tsv import json_report_to_tsv
    except ImportError:
        from tools.json_report_to_tsv import json_report_to_tsv
    tsv_path = os.path.splitext(args.out)[0] + ".tsv"
    json_report_to_tsv(args.out, tsv_path)
    print(f"TSV 文件已生成: {tsv_path}")

    # 终端摘要
    print(summary_text(mean_scores))
    print("RMSE:", rmse)
    print("Spearman ρ:", spearman)
    print("Top-5 误判样例:")
    for r in top5:
        if r.expert_scores:
            diff = sum((float(r.output_json.get(k, 0)) - float(r.expert_scores.get(k, 0))) ** 2 for k in ['empathy', 'positive_regard', 'concreteness', 'immediacy'])
            print(f"id={r.sample_id}, diff={diff}")
        else:
            print(f"id={r.sample_id}, 无专家分")

if __name__ == "__main__":
    main()
