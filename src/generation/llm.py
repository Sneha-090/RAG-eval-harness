"""Provider-replaceable LLM calls (Groq and Gemini) using plain HTTP requests."""
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# The models are chosen in ONE place. Every evaluation run must record them.
GENERATOR = {"provider": "groq", "model": "openai/gpt-oss-120b"}
JUDGE = {"provider": "gemini", "model": "gemini-3.5-flash"}


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _post(url: str, headers: dict, body: dict, retries: int = 3) -> requests.Response:
    for attempt in range(retries + 1):
        r = requests.post(url, headers=headers, json=body, timeout=120)
        if r.status_code == 429 and attempt < retries:
            wait = float(r.headers.get("retry-after", 20))
            print(f"  Rate limited (429). Waiting {wait:.0f} seconds...")
            time.sleep(wait)
            continue
        return r
    return r


def _call_groq(model: str, prompt: str, system: str | None) -> tuple[str, dict]:
    messages = ([{"role": "system", "content": system}] if system else [])
    messages.append({"role": "user", "content": prompt})
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_completion_tokens": 1024,
    }
    if model.startswith("openai/gpt-oss"):
        body["reasoning_effort"] = "low"  # keeps the hidden reasoning short
    r = _post(GROQ_URL, {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"}, body)
    if not r.ok:
        raise RuntimeError(f"Groq error {r.status_code}: {r.text[:300]}")
    text = r.json()["choices"][0]["message"].get("content") or ""
    return text.strip(), dict(r.headers)


def _call_gemini(model: str, prompt: str, system: str | None) -> tuple[str, dict]:
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    r = _post(
        GEMINI_URL.format(model=model),
        {"x-goog-api-key": os.getenv("GEMINI_API_KEY")},
        body,
    )
    if not r.ok:
        raise RuntimeError(f"Gemini error {r.status_code}: {r.text[:300]}")
    candidates = r.json().get("candidates", [])
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    return "".join(p.get("text", "") for p in parts).strip(), dict(r.headers)


def generate(config: dict, prompt: str, system: str | None = None) -> dict:
    """Call one model. Returns the text, the latency in seconds and the response headers."""
    start = time.perf_counter()
    if config["provider"] == "groq":
        text, headers = _call_groq(config["model"], prompt, system)
    elif config["provider"] == "gemini":
        text, headers = _call_gemini(config["model"], prompt, system)
    else:
        raise ValueError(f"Unknown provider: {config['provider']}")
    return {"text": text, "latency_s": time.perf_counter() - start, "headers": headers}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for label, cfg in [("GENERATOR", GENERATOR), ("JUDGE", JUDGE)]:
        print(f"\n=== {label}: {cfg['provider']} / {cfg['model']} ===")
        try:
            out = generate(cfg, "Reply with the single word: ready")
            print(f"Answer: {out['text']!r}")
            print(f"Latency: {out['latency_s']:.2f} seconds")
            limits = {k: v for k, v in out["headers"].items() if k.lower().startswith("x-ratelimit")}
            for k, v in sorted(limits.items()):
                print(f"  {k}: {v}")
        except Exception as e:
            print("FAILED:", e)