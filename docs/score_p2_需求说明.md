# score_p2.py 需求说明

## 一、开发目标

实现一个自动化评分脚本 `score_p2.py`，用于评估 prompts/P2.md 在专家测试集 D1 上的四维分、与专家分差距及 Top-5 误判样例，支持一键运行、自动生成报告和终端摘要。

## 二、架构设计

- **开发方式**：TDD（测试驱动开发）
- **项目架构**：DDD（领域驱动设计）
- **并发处理**：ReactiveX（RxPY），调度用其 scheduler
- **辅助工具**：VS Code Copilot

## 三、输入输出

- **输入**：
  - `prompts/P2.md`（待评估 Prompt）
  - `data/D1/*.yml`（专家已评分对话，格式见 `data/schema.yml`）

- **输出**：
  - `reports/P2_eval_<timestamp>.json`（机器分、专家分、误差、指标）
  - 终端摘要（彩色呈现平均分 & 指标）

## 四、核心功能

1. 计算四维平均分（共情、积极关注、目标一致、咨访同盟）
2. 计算与专家分差距（RMSE、Spearman ρ 或 Cohen’s κ）
3. 输出 Top-5 误判样例（分差最大）

## 五、实现建议

- Python 3 + LLM SDK（如 openai、google.generativeai）
- 读取环境变量 `API_KEY_GEMINI`
- 并发处理用 RxPY，调度用 scheduler，自动重试 ≤3 次
- 指标计算用 scipy/sklearn
- 命令示例：
  ```
  python scripts/score_p2.py \
    --prompt prompts/P2.md \
    --data data/D1 \
    --out reports/<date>.json
  ```

## 六、验收标准

- 50 条样例 ≤ 10 分钟完成
- 生成 JSON 报告 + 终端摘要
- 调用失败可自动重试

## 七、开发节奏与TDD策略

- 采用“小步快跑”TDD，每个开发循环目标控制在10分钟内完成。
- 每次只实现一个小功能（如：数据加载、单条评分、指标计算等），写好测试，确保自动化测试通过后再进入下一个小功能开发。
- Copilot 生成代码时，请优先聚焦当前小目标，避免一次性生成过多内容。

---