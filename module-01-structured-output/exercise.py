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
    prompt = (
        "Extract the fields as JSON. Allowed keys: issue_type, product, urgency. "
        "urgency must be exactly one of: low, med, high. "
        "If product is unknown, use null. "
        "Respond with a single JSON object and nothing else - no prose, no markdown fences.\n\n"
        f"Input: {text}"
    )

    resp = client.messages.create(
        model=MODEL,
        max_tokens=300,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text

    return json.loads(raw)


def main() -> None:
    client = get_client()
    for text in SAMPLES:
        result = extract(client, text)
        print(result)


if __name__ == "__main__":
    main()
