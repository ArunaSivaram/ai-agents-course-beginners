"""Module 3 - PRACTICAL example: a portfolio ReAct agent.

Same portfolio scenario as Module 2's portfolio_agent.py, rebuilt as a real
multi-step ReAct agent. Instead of ONE composite tool that hides the plan, the
model sees TWO primitives and chains them itself:

    Step 0 (Action):      get_holdings()
    Step 0 (Observation): [{AAPL:10}, {MSFT:5}, {NVDA:8}]

    Step 1 (Actions, parallel): get_market_data("AAPL"),
                                get_market_data("MSFT"),
                                get_market_data("NVDA")
    Step 1 (Observations):      3 x {price, previous_close}

    Step 2 (Answer): "Your portfolio is $5,396 today, up 1.6%..."

This file is COMPLETE and runnable. Read it, run it, watch the loop print each
step, then compare it to your exercise.py.

    python module-03-react-agent/portfolio_agent.py

------------------------------------------------------------------------------
ABOUT FACTIQ:
FactIQ's actual shape is market data PER TICKER - you fetch prices one ticker
at a time. Your holdings are YOUR data (a brokerage export, a file, or in
Module 4 a long-term memory store). So the two primitives naturally split:
  - get_holdings()          - your data
  - get_market_data(ticker) - FactIQ's data

To go live: replace `factiq_get_market_data()`'s body with a real FactIQ MCP
call. The agent loop, tools, and message-passing all stay the same.

This reports numbers only. It is not financial advice.
------------------------------------------------------------------------------
"""
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL


# --- YOUR data: what you own -------------------------------------------------
MY_HOLDINGS = [
    {"ticker": "AAPL", "shares": 10},
    {"ticker": "MSFT", "shares": 5},
    {"ticker": "NVDA", "shares": 8},
]

# Baseline "previous close" prices so the demo is stable.
# !!! MOCK NUMBERS - made up for the exercise, NOT real prices. !!!
_PREV_CLOSE = {"AAPL": 220.00, "MSFT": 430.00, "NVDA": 120.00}


def factiq_get_market_data(ticker: str) -> dict:
    """STAND-IN for a real FactIQ market-data call. Fake +/-3% daily move."""
    prev = _PREV_CLOSE.get(ticker)
    if prev is None:
        return {"ticker": ticker, "error": "unknown ticker"}
    daily_move = random.uniform(-0.03, 0.03)
    price = round(prev * (1 + daily_move), 2)
    return {"ticker": ticker, "price": price, "previous_close": prev}


# --- The TWO primitives the agent chains ------------------------------------
def get_holdings() -> list:
    return MY_HOLDINGS


def get_market_data(ticker: str) -> dict:
    return factiq_get_market_data(ticker)


def run_tool(name: str, tool_input: dict):
    if name == "get_holdings":
        return get_holdings()
    if name == "get_market_data":
        return get_market_data(tool_input["ticker"])
    return {"error": f"unknown tool: {name}"}


TOOLS = [
    {
        "name": "get_holdings",
        "description": (
            "Return the user's stock holdings as a list of {ticker, shares}. "
            "Takes no arguments. Call this first to learn what tickers to look up."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_market_data",
        "description": (
            "Get today's price and previous close for a SINGLE stock ticker "
            "(e.g. AAPL). Call it once per ticker you need."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
]


def agent(question: str, max_steps: int = 8) -> str:
    """The ReAct loop: iterate until stop_reason != 'tool_use' or max_steps hit."""
    client = get_client()
    messages = [{"role": "user", "content": question}]

    for step in range(max_steps):
        resp = client.messages.create(
            model=MODEL, max_tokens=1000, tools=TOOLS, messages=messages
        )

        # ANSWER? Model didn't request another tool -> we're done.
        if resp.stop_reason != "tool_use":
            return next(b.text for b in resp.content if b.type == "text")

        # THOUGHT + ACTIONS: keep the assistant's turn intact.
        messages.append({"role": "assistant", "content": resp.content})

        # OBSERVATIONS: run every tool the model asked for (can be several).
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                print(f"[step {step}] {block.name}({block.input}) = {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        messages.append({"role": "user", "content": tool_results})

    return "Hit max_steps without finishing."


if __name__ == "__main__":
    q = "How is my portfolio doing today? Give me a short plain-English summary."
    print("\nFINAL:", agent(q))
