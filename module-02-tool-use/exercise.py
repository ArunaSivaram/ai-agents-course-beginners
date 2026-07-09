"""Module 2 - Your first tool (function calling).

GOAL: let the model DECIDE to call a function, then you run it and hand the
      result back.
SUCCESS: you can see the model request `get_ticket_status`, you execute it,
         and the model uses the returned data in its final answer.

Key facts about the loop (verified against current Anthropic docs):
  - Pass tools=[{"name","description","input_schema"}]
  - If resp.stop_reason == "tool_use", find the content block with .type == "tool_use"
  - It has .id, .name, .input
  - You reply with a user message containing a "tool_result" block that
    references that .id via "tool_use_id"

Run:  python module-02-tool-use/exercise.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL

FAKE_DB = {
    "403": {"status": "escalated", "owner": "billing", "age_days": 6},
    "119": {"status": "resolved", "owner": "support", "age_days": 1},
}


def get_ticket_status(ticket_id: str) -> dict:
    return FAKE_DB.get(ticket_id, {"status": "not_found"})


TOOLS = [
    {
        "name": "get_ticket_status",
        "description": "Look up the current status of a support ticket by its id.",
        "input_schema": {
            "type": "object",
            "properties": {"ticket_id": {"type": "string"}},
            "required": ["ticket_id"],
        },
    }
]


def main() -> None:
    client = get_client()
    messages = [{"role": "user", "content": "What's going on with ticket 403?"}]

    resp = client.messages.create(model=MODEL, max_tokens=500, tools=TOOLS, messages=messages)

    # TODO 1: check resp.stop_reason. If it's "tool_use", locate the tool_use block.
    # TODO 2: call get_ticket_status(**block.input) to get the real result.
    # TODO 3: append the assistant's turn (resp.content) to messages, then append a
    #         user turn containing a tool_result block:
    #         {"role":"user","content":[{"type":"tool_result",
    #             "tool_use_id": block.id, "content": str(result)}]}
    # TODO 4: call the model again and print the final text answer.
    print("stop_reason:", resp.stop_reason)


if __name__ == "__main__":
    main()
