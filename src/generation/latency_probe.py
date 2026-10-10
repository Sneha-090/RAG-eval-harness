"""Measure the latency of candidate judge models (two calls each)."""
import sys

from src.generation.llm import generate

CANDIDATES = [
    {"provider": "gemini", "model": "gemini-3.8-flash"},
    {"provider": "gemini", "model": "gemini-3.5-flash"},
    {"provider": "gemini", "model": "gemini-3.1-flash-lite"},
    {"provider": "groq", "model": "openai/gpt-oss-20b"},
]
PROMPT = "Reply with the single word: ready"

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for cfg in CANDIDATES:
        print(f"\n=== {cfg['provider']} / {cfg['model']} ===")
        for attempt in (1, 2):
            try:
                out = generate(cfg, PROMPT)
                print(f"  call {attempt}: {out['text']!r} in {out['latency_s']:.2f} s")
            except Exception as e:
                print(f"  call {attempt}: FAILED: {str(e)[:150]}")
                break