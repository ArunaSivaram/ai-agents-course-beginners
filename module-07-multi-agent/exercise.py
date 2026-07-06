"""Module 7 - A two-agent pipeline.

GOAL: a Researcher agent gathers facts, then HANDS OFF to a Writer agent that
      turns them into a tight 5-sentence brief.
SUCCESS: two agents complete a task neither did alone - AND you've watched how
         a bad Researcher output poisons the Writer (run it on a topic with no
         good info and observe the failure propagate).

You can do this with plain SDK calls (two functions) OR your Module 6 framework.

Run:  python module-07-multi-agent/exercise.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL


def researcher(client, topic: str) -> str:
    # TODO: prompt the model to return a bulleted list of factual points on `topic`.
    return ""


def writer(client, notes: str) -> str:
    # TODO: prompt the model to turn `notes` into exactly 5 sentences.
    return ""


def main() -> None:
    client = get_client()
    topic = "why observability matters for AI agents"
    notes = researcher(client, topic)
    brief = writer(client, notes)
    print("NOTES:\n", notes, "\n\nBRIEF:\n", brief)
    # Then: rerun with a nonsense topic and watch the failure flow downstream.


if __name__ == "__main__":
    main()
