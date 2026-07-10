"""Module 5 - PRACTICAL example: portfolio review with plan+execute+reflect.

Same portfolio scenario as Module 4, but instead of a single ReAct pass we run
THREE passes:

  PLAN     - one text-only call. Model outputs a short numbered plan.
  EXECUTE  - full ReAct loop (from Module 4) that follows the plan and uses
             the tools to gather data, then drafts an analysis.
  REFLECT  - one text-only call. Model critiques the draft and rewrites it.

Total: ~5-7 API calls per run instead of 3-4. In exchange, the final answer is
consistently tighter and less hand-wavy than the first draft.

This file is COMPLETE and runnable. Read it, run it, watch the three passes.

    python module-05-planning-reflection/portfolio_agent.py

------------------------------------------------------------------------------
Long-term holdings come from the SAME Supabase table (or JSON fallback) you
set up in Module 4. To keep this module self-contained, we import Module 4's
holdings_store adapter via a small sys.path hack. In a real codebase you'd
promote it to common/ for cleaner sharing.
This reports numbers only. It is not financial advice.
------------------------------------------------------------------------------
"""
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL

# Reuse Module 4's holdings store (same Supabase table / JSON file).
sys.path.append(str(Path(__file__).resolve().parents[1] / "module-04-memory"))
import holdings_store


# --- The portfolio review task -----------------------------------------------
TASK = (
    "Give me an actionable review of my portfolio today: how it's performing, "
    "which positions are working and which aren't, and ONE concrete "
    "recommendation. Keep the whole review under ~150 words."
)


# --- MOCK previous-close prices + FactIQ stand-in (same shape as Module 4) --
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


# Note: for a REVIEW task we only need read-only tools. add/remove would let
# the agent silently mutate your portfolio during a review, which is not what
# you want. Same tools, less surface area.
TOOLS = [
    {
        "name": "get_holdings",
        "description": (
            "Return the user's stock holdings as a list of {ticker, shares}. "
            "Takes no arguments."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_market_data",
        "description": (
            "Get today's price and previous close for a SINGLE stock ticker "
            "(e.g. AAPL). Call once per ticker."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
]


# --- The two API primitives we call ------------------------------------------
def call(client, prompt: str, max_tokens: int = 1000) -> str:
    """Simple one-shot text call, no tools. Used for plan and reflect."""
    resp = client.messages.create(
        model=MODEL, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "\n".join(b.text for b in resp.content if b.type == "text")


def react_execute(client, messages: list, max_steps: int = 8) -> str:
    """Module 4's ReAct loop. Runs until the model stops asking for tools."""
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


# --- The three passes --------------------------------------------------------
def plan(client, task: str, tool_names: list) -> str:
    prompt = (
        "You have these tools available during execution: " + ", ".join(tool_names) + ".\n"
        "Break the following task into a short numbered plan (3-5 steps).\n"
        "Output ONLY the numbered plan. No preamble, no explanation.\n\n"
        f"Task: {task}"
    )
    return call(client, prompt, max_tokens=400)


def execute(client, task: str, the_plan: str) -> str:
    """Run the ReAct loop with the plan as context, produce a first draft."""
    messages = [{
        "role": "user",
        "content": (
            f"Task: {task}\n\n"
            f"Plan:\n{the_plan}\n\n"
            "Follow the plan using the tools available. When you have the "
            "information you need, write the final review as your answer."
        ),
    }]
    return react_execute(client, messages)


def reflect(client, task: str, draft: str) -> str:
    prompt = (
        "You are reviewing a portfolio analysis draft. Critique it for "
        "accuracy, actionability, and concision. Follow this format:\n\n"
        "CRITIQUE:\n- (bullet points listing specific problems)\n\n"
        "IMPROVED VERSION:\n(the rewritten analysis; must still address the task below)\n\n"
        f"Original task: {task}\n\n"
        f"Draft to critique:\n{draft}"
    )
    return call(client, prompt, max_tokens=1200)


def main() -> None:
    client = get_client()
    print(f"long-term memory backend: {holdings_store.backend_name()}\n")

    print("=" * 60)
    print("PASS 1 - PLAN")
    print("=" * 60)
    the_plan = plan(client, TASK, [t["name"] for t in TOOLS])
    print(the_plan)

    print("\n" + "=" * 60)
    print("PASS 2 - EXECUTE (ReAct loop follows the plan)")
    print("=" * 60)
    draft = execute(client, TASK, the_plan)
    print("\nDRAFT:\n" + draft)

    print("\n" + "=" * 60)
    print("PASS 3 - REFLECT")
    print("=" * 60)
    improved = reflect(client, TASK, draft)
    print(improved)


if __name__ == "__main__":
    main()
