"""Module 03 - THE CORE ONE. Build a ReAct agent loop by hand.

GOAL: an agent that reasons -> acts (calls a tool) -> observes -> repeats,
      chaining MULTIPLE tool calls on its own until it produces a final answer.
SUCCESS: ask a question needing both tools in sequence and get a correct answer,
         while your print() statements show every step of the loop.

Run:  python module-03-react-agent/exercise.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL

# --- Two tools ---------------------------------------------------------------
FACTS = {
    "tokyo population": 14_000_000,
    "yokohama population": 3_770_000,
    "osaka population": 2_750_000,
}


def search(query: str) -> str:
    return str(FACTS.get(query.lower().strip(), "no result"))


def calculator(expression: str) -> str:
    # Tiny + safe-ish eval for the exercise. Don't ship eval() to production.
    return str(eval(expression, {"__builtins__": {}}, {}))


def run_tool(name: str, tool_input: dict) -> str:
    if name == "search":
        return search(tool_input["query"])
    if name == "calculator":
        return calculator(tool_input["expression"])
    return "unknown tool"


TOOLS = [
    {
        "name": "search",
        "description": "Look up a single fact. Query must be like 'tokyo population'.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression like '14000000 + 3770000'.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
]


def agent(question: str, max_steps: int = 8) -> str:
    client = get_client()
    messages = [{"role": "user", "content": question}]

    for step in range(max_steps):
        resp = client.messages.create(
            model=MODEL, max_tokens=800, tools=TOOLS, messages=messages
        )

        # TODO 1: if resp.stop_reason != "tool_use", the model is done ->
        #         return the final text (resp.content[0].text).
        #
        # TODO 2: otherwise, append resp.content to messages (the assistant turn),
        #         then for EACH tool_use block in resp.content:
        #           - run_tool(block.name, block.input)
        #           - collect a tool_result dict referencing block.id
        #         append one user message whose content is the list of tool_result blocks.
        #
        # TODO 3: print(step, block.name, block.input, result) so you can watch the loop.
        print(f"[step {step}] stop_reason={resp.stop_reason}")

    return "Hit max_steps without finishing."


if __name__ == "__main__":
    q = "What is the combined population of Tokyo and Yokohama?"
    print("\nFINAL:", agent(q))
