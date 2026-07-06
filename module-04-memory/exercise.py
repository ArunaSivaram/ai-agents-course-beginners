"""Module 4 - Memory.

GOAL: give your agent (a) conversation memory across turns and (b) long-term
      memory that survives a restart via a JSON file.
SUCCESS: tell it your name in one run, restart the script, and it can recall
         your name in a new run.

Build on your Module 3 loop. Add two tools: remember(fact) and recall().

Run:  python module-04-memory/exercise.py
"""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL

STORE = Path(__file__).resolve().parent / "memory_store.json"  # gitignored


def remember(fact: str) -> str:
    data = json.loads(STORE.read_text()) if STORE.exists() else []
    data.append(fact)
    STORE.write_text(json.dumps(data))
    return "saved"


def recall() -> str:
    return json.loads(STORE.read_text()) if STORE.exists() else []


# TODO 1: declare remember + recall as tools (see Module 3 for the schema shape).
# TODO 2: reuse your Module 3 agent loop, but keep `messages` alive across
#         multiple user inputs in a while-loop REPL (short-term memory).
# TODO 3: prove long-term memory: run once and say "my name is X", quit,
#         run again and ask "what's my name?" -> it should call recall().

if __name__ == "__main__":
    print("Scaffold ready. Wire up the tools + loop, then test the restart behavior.")
