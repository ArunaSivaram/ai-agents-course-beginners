"""Module 2 - Your first tool (function calling).

GOAL: let the model DECIDE to call a function, then you run it and hand the
      result back.
SUCCESS: you can see the model request `get_stock_price` for AAPL, you execute
         it, and the model uses the returned price/day-change in its answer.

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

# MOCK prices - made up for the exercise, NOT real market data.
# In production you'd swap this dict for a real market-data API call.
FAKE_PRICES = {
    "AAPL": {"price": 223.50, "previous_close": 220.00},
    "MSFT": {"price": 442.10, "previous_close": 430.00},
    "NVDA": {"price": 118.90, "previous_close": 120.00},
}


def get_stock_price(ticker: str) -> dict:
    data = FAKE_PRICES.get(ticker.upper())
    if not data:
        return {"ticker": ticker, "error": "unknown ticker"}
    return {
        "ticker": ticker.upper(),
        "price": data["price"],
        "previous_close": data["previous_close"],
        "day_change_pct": round((data["price"] / data["previous_close"] - 1) * 100, 2),
    }


TOOLS = [
    {
        "name": "get_stock_price",
        "description": "Look up today's price and previous close for a single stock ticker (e.g. AAPL, MSFT, NVDA).",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    }
]


def main() -> None:
    client = get_client()
    messages = [{"role": "user", "content": "How is Apple stock doing today?"}]

    resp = client.messages.create(model=MODEL, max_tokens=500, tools=TOOLS, messages=messages)

    # TODO 1: check resp.stop_reason. If it's "tool_use", locate the tool_use block.
    # TODO 2: call get_stock_price(**block.input) to get the real result.
    # TODO 3: append the assistant's turn (resp.content) to messages, then append a
    #         user turn containing a tool_result block:
    #         {"role":"user","content":[{"type":"tool_result",
    #             "tool_use_id": block.id, "content": str(result)}]}
    # TODO 4: call the model again and print the final text answer.
    print("stop_reason:", resp.stop_reason)


if __name__ == "__main__":
    main()
