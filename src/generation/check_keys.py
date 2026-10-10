"""Check that the API keys work and list the models each key can use (keys are never printed)."""
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def check_groq() -> None:
    key = os.getenv("GROQ_API_KEY")
    print("\n=== GROQ ===")
    if not key:
        print("GROQ_API_KEY not found in .env")
        return
    r = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers={"Authorization": f"Bearer {key}"},
        timeout=30,
    )
    print("HTTP status:", r.status_code)
    if r.ok:
        for m in sorted(item["id"] for item in r.json().get("data", [])):
            print("  ", m)
    else:
        print(r.text[:300])


def check_gemini() -> None:
    key = os.getenv("GEMINI_API_KEY")
    print("\n=== GOOGLE GEMINI ===")
    if not key:
        print("GEMINI_API_KEY not found in .env")
        return
    r = requests.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        headers={"x-goog-api-key": key},
        params={"pageSize": 200},
        timeout=30,
    )
    print("HTTP status:", r.status_code)
    if r.ok:
        names = sorted(
            m["name"].replace("models/", "")
            for m in r.json().get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])
        )
        for n in names:
            print("  ", n)
    else:
        print(r.text[:300])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    check_groq()
    check_gemini()