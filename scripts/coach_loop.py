import argparse
import json
import os
import datetime
import re
from typing import List, Dict

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def call_llm(provider: str, messages: List[Dict[str, str]], model: str | None = None) -> str:
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError("API_KEY environment variable not set")

    if provider == "openai":
        if openai is None:
            raise RuntimeError("openai package not installed")
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(model=model or "gpt-3.5-turbo", messages=messages)
        return resp.choices[0].message.content.strip()

    if provider == "google":
        if genai is None:
            raise RuntimeError("google-generativeai package not installed")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model or "gemini-pro")
        resp = model.generate_content(messages)
        return resp.text.strip()

    raise ValueError(f"Unknown provider {provider}")


def simulate_conversation(p1: str, p3: str, turns: int, provider: str) -> str:
    prompt = (
        f"Simulate a {turns}-turn conversation between an AI coach and a parent.\n"
        f"The coach follows these instructions:\n{p1}\n"
        f"The parent persona:\n{p3}\n"
        "Format each turn as:\nParent: ...\nCoach: ...\n"
    )
    messages = [{"role": "user", "content": prompt}]
    return call_llm(provider, messages)


def score_conversation(conversation: str, p2: str, provider: str) -> Dict[str, float]:
    messages = [
        {"role": "system", "content": p2},
        {"role": "user", "content": conversation},
    ]
    result = call_llm(provider, messages)
    try:
        data = json.loads(result)
        return {
            "empathy": float(data.get("empathy")),
            "positive_affect": float(data.get("positive_affect")),
            "goal": float(data.get("goal")),
            "alliance": float(data.get("alliance")),
        }
    except Exception:
        numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", result)[:4]]
        if len(numbers) != 4:
            raise ValueError(f"Could not parse scores from LLM output: {result}")
        return {
            "empathy": numbers[0],
            "positive_affect": numbers[1],
            "goal": numbers[2],
            "alliance": numbers[3],
        }


def run_session(p1_path: str, p2_path: str, p3_path: str, turns: int, provider: str) -> Dict:
    p1 = load_text(p1_path)
    p2 = load_text(p2_path)
    p3 = load_text(p3_path)
    conversation = simulate_conversation(p1, p3, turns, provider)
    scores = score_conversation(conversation, p2, provider)
    scores["average"] = sum(scores.values()) / 4
    return {"conversation": conversation, "scores": scores}


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate coach prompt effectiveness")
    parser.add_argument("--turns", type=int, default=6, help="Conversation turns")
    parser.add_argument("--sessions", type=int, default=1, help="Number of sessions")
    parser.add_argument("--persona", default="strict_parent", help="Persona file name under prompts/P3")
    parser.add_argument("--p1", default="prompts/P1.md", help="Path to coach prompt")
    parser.add_argument("--p2", default="prompts/P2.md", help="Path to scoring prompt")
    parser.add_argument("--out", default=None, help="Output JSON file")
    args = parser.parse_args()

    provider = os.environ.get("LLM_PROVIDER", "openai")
    sessions = []
    for _ in range(args.sessions):
        p3_path = os.path.join("prompts", "P3", f"{args.persona}.md")
        result = run_session(args.p1, args.p2, p3_path, args.turns, provider)
        sessions.append(result)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.out or os.path.join("reports", f"P1_session_{timestamp}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

    for i, sess in enumerate(sessions, 1):
        s = sess["scores"]
        print(
            f"Session {i}: Emp {s['empathy']} | PosAff {s['positive_affect']} | "
            f"Goal {s['goal']} | Alliance {s['alliance']} | AVG {s['average']:.2f}"
        )
    overall = sum(s["scores"]["average"] for s in sessions) / len(sessions)
    print(f"Overall Average: {overall:.2f}")


if __name__ == "__main__":  # pragma: no cover
    main()
