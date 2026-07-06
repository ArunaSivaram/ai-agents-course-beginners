"""Module 5 - Plan, execute, reflect.

GOAL: for a multi-part task, make the agent (1) output an explicit plan,
      (2) execute each step, (3) run ONE reflection pass that critiques and
      rewrites its own output.
SUCCESS: you can see the plan, the execution, and a visibly better 2nd draft.

Run:  python module-05-planning-reflection/exercise.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL

TASK = "Research 'the benefits of RAG for agents', list 3 key points, then write a 4-sentence summary."


def call(client, prompt: str) -> str:
    resp = client.messages.create(
        model=MODEL, max_tokens=800, messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text


def main() -> None:
    client = get_client()

    # TODO 1 (PLAN): ask the model for a short numbered plan for TASK. Print it.
    # TODO 2 (EXECUTE): ask it to carry out the plan and produce a first draft. Print it.
    # TODO 3 (REFLECT): feed the first draft back and ask: "Critique this for
    #         accuracy and concision, then output an improved version." Print both.
    print("Scaffold ready. Implement the three passes above.")


if __name__ == "__main__":
    main()
