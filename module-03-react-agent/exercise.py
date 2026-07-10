"""Module 3 - THE CORE ONE. Build a ReAct agent loop by hand.

GOAL: an agent that REASONS about what it needs, ACTS (calls a tool), OBSERVES
      the result, and repeats - chaining MULTIPLE tool calls on its own until
      it can answer.
SUCCESS: ask "how is my portfolio doing today?" and your prints show:
    step 0: get_holdings() -> [...]
    step 1: get_market_data("AAPL"), get_market_data("MSFT"), get_market_data("NVDA")
    step 2: (final answer, no tool call - the loop returns the text)

The trick: the MODEL decides the plan. You just provide primitives and a loop.

Run:  python module-03-react-agent/exercise.py
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

# !!! MOCK previous-close prices - made up for the exercise. !!!
_PREV_CLOSE = {"AAPL": 220.00, "MSFT": 430.00, "NVDA": 120.00}


def factiq_get_market_data(ticker: str) -> dict:
    """STAND-IN for a real FactIQ market-data call. Fake +/-3% daily move."""
    prev = _PREV_CLOSE.get(ticker)
    if prev is None:
        return {"ticker": ticker, "error": "unknown ticker"}
    daily_move = random.uniform(-0.03, 0.03)
    price = round(prev * (1 + daily_move), 2)
    return {"ticker": ticker, "price": price, "previous_close": prev}


# --- The TWO primitives the agent will chain --------------------------------
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
    client = get_client()
    messages = [{"role": "user", "content": question}]

    for step in range(max_steps):
        resp = client.messages.create(
            model=MODEL, max_tokens=1000, tools=TOOLS, messages=messages
        )

        # TODO 1: if resp.stop_reason != "tool_use", the model is done ->
        #         return the text block's .text.
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
    q = "How is my portfolio doing today? Give me a short plain-English summary."
    print("\nFINAL:", agent(q))
