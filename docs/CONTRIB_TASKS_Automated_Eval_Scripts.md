# 📋 Contributor Task Brief – Automated Evaluation Scripts  
_Updated: 2025-05-23_

本文件列出两个当下最迫切的可贡献任务，帮助项目完成「Prompt → 一键跑 → 得分 → 误差反馈」的闭环。  
欢迎任何人直接认领并提交 PR！若有疑问，请在对应 Issue / Discussion 提问。

---

## ⚙️ Task 1 — `score_p2.py` &nbsp;📝  
**目标**：让贡献者改完 **自动评分 Prompt (P2)** 后，一条命令即可在专家测试集 **D1** 上跑分并看到：

1. 四维平均分（共情、积极关注、目标一致、咨访同盟）  
2. 与专家分差距（任选一种指标：RMSE、Spearman ρ 或 Cohen’s κ）  
3. Top-5 误判样例（机器 vs. 专家分差最大，对调 Prompt 最有帮助）

| 项目        | 说明 |
|-------------|------|
| **输入**    | - `prompts/P2.md`（待评估 Prompt）<br>- `data/D1/*.yml`（专家已评分对话，格式见 `data/schema.yml`） |
| **输出**    | - `reports/P2_eval_<timestamp>.json`（机器分、专家分、误差、指标）<br>- 终端摘要（彩色呈现平均分 & 指标） |
| **实现建议** | 1. Python 3 + LLM SDK (`openai`、`google.generativeai` 等)<br>2. 读取环境变量 `API_KEY_GEMINI`<br>3. `asyncio` 并发 + 自动重试 ≤3 次<br>4. 指标计算用 `scipy`/`sklearn`<br>5. 命令示例：<br>&nbsp;&nbsp;```bash<br>python scripts/score_p2.py \ <br>  --prompt prompts/P2.md \ <br>  --data data/D1 \ <br>  --out reports/<date>.json<br>``` |
| **验收标准** | - 50 条样例 ≤ 10 min 完成<br>- 生成 JSON 报告 + 终端摘要<br>- 调用失败可自动重试 |

---

## ⚙️ Task 2 — `coach_loop.py` &nbsp;🤖  
**目标**：一键评估 **AI 教练 Prompt (P1)** 的实际效果。脚本自动完成：

1. 用 **P1**（咨询师）+ **P3**（家长 persona）对话 *N* 轮（默认 6）  
2. 将整段对话喂给 **P2** 打四维分  
3. 输出本轮四维分、平均分，以及与目标阈值的差距  
4. 支持多轮取均值，便于快速迭代 P1

| 项目        | 说明 |
|-------------|------|
| **输入**    | - `prompts/P1.md`（待调优 Coach Prompt）<br>- `prompts/P3.md`（家长 Persona，可多选）<br>- `prompts/P2.md`（评分 Prompt，复用 Task 1 逻辑） |
| **输出**    | - `reports/P1_session_<timestamp>.json`（完整对话 + 四维分）<br>- 终端摘要，如：<br>&nbsp;&nbsp;`Emp 3.8 | PosAff 4.1 | Goal 3.5 | Alliance 3.9 | AVG 3.83` |
| **实现建议** | 1. Python 脚本 `scripts/coach_loop.py`<br>2. 使用统一 LLM，模型由环境变量 `LLM_PROVIDER` & `API_KEY` 决定<br>3. 参数示例：<br>&nbsp;&nbsp;```bash<br>python scripts/coach_loop.py \ <br>  --turns 6 \ <br>  --sessions 5 \ <br>  --persona strict_parent<br>``` |
| **验收标准** | - 单次 6 轮对话 + 打分 ≤ 2 min<br>- JSON 含完整对话，便于复盘<br>- 终端显示四维分及均值 |

---

## 🚀 如何贡献

1. **Fork → 新分支 → 提 PR**  
2. 在 `scripts/` 里添加或修改脚本，确保 `--help` 可运行。  
3. _暂未启用 pre-commit_，请自行运行 `flake8` / `black`（或等价工具）保持代码整洁。  
4. PR 描述请附一次脚本跑分摘要，方便 Reviewer 复现。  

> **Issue 标签**：`good first issue` 已预留，欢迎自选或提出新任务！

---


_有任何疑问或改进建议，欢迎在 Discussions 或 Issues 中提出！_  
