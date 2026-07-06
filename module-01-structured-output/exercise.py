"""Module 1 - Structured extraction.

GOAL: turn messy text into a reliable Python dict.
SUCCESS: your script prints a parsed dict for all 5 sample inputs without a
         single JSON parse error.

Run:  python module-01-structured-output/exercise.py
"""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL

SAMPLES = [
    "hey my dishwasher (model DW-90) has been leaking for 3 days, getting urgent!",
    "Order #4412 never arrived. Been two weeks. Not happy.",
    "quick q - does the X200 router support 5ghz? no rush",
    "CHARGED TWICE for my subscription this month, please fix ASAP",
    "the app keeps crashing when I open settings on my Pixel, minor annoyance",
]


def extract(client, text: str) -> dict:
    # TODO 1: write a prompt that instructs the model to return ONLY a JSON
    #         object with these keys: issue_type, product, urgency (low/med/high).
    #         Be explicit: "Respond with JSON only, no prose, no markdown fences."
    prompt = f"..."  # <-- replace this

    resp = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text

    # TODO 2: parse `raw` into a dict with json.loads and return it.
    #         If parsing fails on some input, tighten the prompt until it never does.
    #         (Hint: lower hallucination by telling it exactly which keys/values are allowed.)
    return {}


def main() -> None:
    client = get_client()
    for text in SAMPLES:
        result = extract(client, text)
        print(result)


if __name__ == "__main__":
    main()
