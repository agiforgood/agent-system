"""
小任务：集成真实 LLM (DeepSeek)，使用 OpenAI SDK 兼容方式
功能：调用 DeepSeek API，使用 openai.OpenAI，支持 .env 中 API_KEY_DEEPSEEK，输入 Prompt 和 DialogueSample，返回 LLM 评分结果
"""

import os
from typing import Dict, Any
import json
from domain.domain_objects import Prompt, DialogueSample, ScoreResult
from openai import OpenAI

class DeepSeekLLM:
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or os.getenv("API_KEY_DEEPSEEK")
        self.base_url = base_url or "https://api.deepseek.com"
        self.model = model or "deepseek-chat"
        if self.api_key:
            os.environ['OPENAI_API_KEY'] = self.api_key
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def score(self, prompt: Prompt, sample: DialogueSample):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt.content}],
                stream=False
            )
            content = response.choices[0].message.content
            try:
                output_json = json.loads(content)
            except Exception:
                output_json = {"raw": content}
        except Exception as e:
            output_json = {"error": str(e)}
        return output_json

class PromptEvaluator:
    def __init__(self, mode: str = "real", llm: str = "deepseek"):
        from dotenv import load_dotenv
        load_dotenv()
        self.mode = mode
        self.llm = llm
        if self.mode == "real":
            if self.llm == "deepseek":
                self.llm_client = DeepSeekLLM()
            else:
                raise NotImplementedError(f"LLM {self.llm} not implemented")
        else:
            self.llm_client = None

    def score(self, prompt: Prompt, sample: DialogueSample) -> ScoreResult:
        import random
        if self.mode == "mock":
            # mock模式下返回随机分数和结构
            output_json = {
                "score": random.randint(1, 5),
                "explanation": "This is a mock score.",
                "raw": prompt.content[:20] + "..."
            }
            return ScoreResult(
                sample_id=sample.id,
                output_json=output_json,
                machine_scores=None,
                expert_scores=None,
                error=None,
                extra={"llm": "mock"}
            )
        # 兼容 legacy mock: 如果 llm_client 为 None 且有 client 属性，则 fallback
        if self.llm_client is not None:
            try:
                output_json = self.llm_client.score(prompt, sample)
            except Exception as e:
                output_json = {"error": str(e)}
        elif hasattr(self, "client") and self.client is not None:
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt.content}],
                    stream=False
                )
                content = response.choices[0].message.content
                try:
                    output_json = json.loads(content)
                except Exception:
                    output_json = {"raw": content}
            except Exception as e:
                output_json = {"error": str(e)}
        else:
            output_json = {"error": "No LLM client available"}
        return ScoreResult(
            sample_id=sample.id,
            output_json=output_json,
            machine_scores=None,
            expert_scores=None,
            error=None,
            extra={"llm": self.llm}
        )
