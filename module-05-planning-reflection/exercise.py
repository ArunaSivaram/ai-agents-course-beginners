"""Module 5 - Plan, execute, reflect on a portfolio review task.

GOAL: instead of ONE ReAct pass, run THREE:
    PLAN     - the model outputs a short numbered plan (text-only, no tools).
    EXECUTE  - the ReAct loop (from Module 4) follows the plan using tools,
               produces a first-draft review.
    REFLECT  - the model critiques the draft and outputs an improved version
               (text-only, no tools).

SUCCESS: three visibly distinct outputs printed - a plan, a first draft, then
         a critique + rewritten review that's tighter than the draft.

Build on Module 4's agent. Same portfolio, same holdings store, same FactIQ
mock. What's new: the plan/execute/reflect meta-loop AROUND the agent.

Run:  python module-05-planning-reflection/exercise.py
"""
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL

# Reuse Module 4's holdings store (same Supabase table / JSON file).
sys.path.append(str(Path(__file__).resolve().parents[1] / "module-04-memory"))
import holdings_store


TASK = (
    "Give me an actionable review of my portfolio today: how it's performing, "
    "which positions are working and which aren't, and ONE concrete "
    "recommendation. Keep the whole review under ~150 words."
)


# --- FactIQ mock + tools (read-only slice of Module 4's set) ----------------
_PREV_CLOSE = {
    "AAPL": 220.00, "MSFT": 430.00, "NVDA": 120.00,
    "TSLA": 250.00, "GOOGL": 180.00, "AMZN": 200.00,
}


def factiq_get_market_data(ticker: str) -> dict:
    prev = _PREV_CLOSE.get(ticker.upper())
    if prev is None:
        return {"ticker": ticker, "error": "unknown ticker (not in mock)"}
    daily_move = random.uniform(-0.03, 0.03)
    price = round(prev * (1 + daily_move), 2)
    return {"ticker": ticker.upper(), "price": price, "previous_close": prev}


def run_tool(name: str, tool_input: dict):
    if name == "get_holdings":
        return holdings_store.get_holdings()
    if name == "get_market_data":
        return factiq_get_market_data(tool_input["ticker"])
    return {"error": f"unknown tool: {name}"}


TOOLS = [
    {
        "name": "get_holdings",
        "description": "Return the user's holdings as [{ticker, shares}]. No args.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_market_data",
        "description": "Today's price + previous close for ONE ticker. Call once per ticker.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
]


# --- API primitives you'll use in the three passes --------------------------
def call(client, prompt: str, max_tokens: int = 1000) -> str:
    """One-shot text call, no tools. Used in PLAN and REFLECT."""
    resp = client.messages.create(
        model=MODEL, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "\n".join(b.text for b in resp.content if b.type == "text")


def react_execute(client, messages: list, max_steps: int = 8) -> str:
    """The Module 4 ReAct loop. Used in EXECUTE."""
    for step in range(max_steps):
        resp = client.messages.create(
            model=MODEL, max_tokens=1200, tools=TOOLS, messages=messages
        )
        if resp.stop_reason != "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            return "\n".join(b.text for b in resp.content if b.type == "text")
        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                print(f"    [step {step}] {block.name}({block.input}) = {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        messages.append({"role": "user", "content": tool_results})
    return "Hit max_steps without finishing execution."


def main() -> None:
    client = get_client()
    print(f"long-term memory backend: {holdings_store.backend_name()}\n")

    # TODO 1 (PLAN): ask the model for a short numbered plan for TASK.
    #   Use call() with a prompt like:
    #     "You have these tools available: get_holdings, get_market_data.
    #      Break the following task into a short numbered plan (3-5 steps).
    #      Output ONLY the numbered plan. Task: {TASK}"
    #   Store the result in `the_plan` and print it.
    the_plan = ""  # replace me

    # TODO 2 (EXECUTE): run the plan through the ReAct agent.
    #   Build a messages list whose first user turn contains BOTH the task and
    #   the plan, telling the model to follow the plan using the tools and
    #   produce a first-draft review as its final answer. Then call
    #   react_execute(client, messages) and store the result in `draft`.
    draft = ""  # replace me

    # TODO 3 (REFLECT): critique the draft and produce an improved version.
    #   Use call() with a prompt that asks for two sections:
    #     CRITIQUE: (bullet points listing specific problems)
    #     IMPROVED VERSION: (the rewritten analysis)
    #   Include the original task and the draft in the prompt.
    #   Store the result in `improved` and print it.
    improved = ""  # replace me

    print("=" * 60, "\nPLAN\n", "=" * 60)
    print(the_plan)
    print("=" * 60, "\nDRAFT\n", "=" * 60)
    print(draft)
    print("=" * 60, "\nREFLECTION\n", "=" * 60)
    print(improved)


if __name__ == "__main__":
    main()
