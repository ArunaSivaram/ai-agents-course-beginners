"""Module 2 - PRACTICAL example: a portfolio agent that "talks to FactIQ".

Same tool-use mechanic as exercise.py (the ticket demo), but in a real-feeling
scenario: you ask "how's my portfolio doing today?" and the agent calls a tool
to fetch the numbers, then reports them back in plain English.

Unlike exercise.py, this file is COMPLETE and runnable. Read it, run it, and
watch the phone-call pattern work end to end - then compare it to your own
ticket solution to see it's the exact same four beats.

    python module-02-tool-use/portfolio_agent.py

------------------------------------------------------------------------------
ABOUT FACTIQ (this part is real):
FactIQ (https://www.factiq.com) is a genuine investment/economic data service
built for AI agents. In production you'd reach it through its MCP server
(https://api.factiq.com/mcp) over an OAuth connection, using tools like
get_market_data / get_series. Setting up real OAuth would bury the lesson here,
so `factiq_get_market_data()` below is a clearly-labelled MOCK returning fake
prices.

The whole point of the tool-use pattern: swapping the mock for a real FactIQ
call is a change to ONE function - the agent loop never changes. That
swappability is the payoff of this design.

This reports numbers only. It is not financial advice.
------------------------------------------------------------------------------
"""
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL


# --- YOUR data: the holdings you own -----------------------------------------
# Stand-in for a brokerage export or a file you maintain. In Module 4 you'll
# move this into real long-term memory so the agent remembers it for you.
MY_HOLDINGS = [
    {"ticker": "AAPL", "shares": 10},
    {"ticker": "MSFT", "shares": 5},
    {"ticker": "NVDA", "shares": 8},
]

# Baseline "previous close" prices so the demo is stable.
# !!! MOCK NUMBERS - made up for the exercise, NOT real prices. !!!
_PREV_CLOSE = {"AAPL": 220.00, "MSFT": 430.00, "NVDA": 120.00}


def factiq_get_market_data(ticker: str) -> dict:
    """STAND-IN for a real FactIQ market-data call.

    Returns today's price and previous close for one ticker. In production,
    replace this function's body with a real FactIQ MCP/API call - everything
    else in this file stays exactly the same.
    """
    prev = _PREV_CLOSE.get(ticker)
    if prev is None:
        return {"ticker": ticker, "error": "unknown ticker"}
    daily_move = random.uniform(-0.03, 0.03)  # fake +/-3% daily move (MOCK)
    price = round(prev * (1 + daily_move), 2)
    return {"ticker": ticker, "price": price, "previous_close": prev}


def get_portfolio_performance() -> dict:
    """The ONE tool the agent can call. Pulls market data for each holding and
    sums it into a today-vs-yesterday performance summary."""
    holdings, total_today, total_yesterday = [], 0.0, 0.0
    for h in MY_HOLDINGS:
        md = factiq_get_market_data(h["ticker"])
        if "error" in md:
            continue
        value_today = h["shares"] * md["price"]
        value_yesterday = h["shares"] * md["previous_close"]
        total_today += value_today
        total_yesterday += value_yesterday
        holdings.append({
            "ticker": h["ticker"],
            "shares": h["shares"],
            "price": md["price"],
            "previous_close": md["previous_close"],
            "day_change_pct": round((md["price"] / md["previous_close"] - 1) * 100, 2),
            "value_today": round(value_today, 2),
        })
    return {
        "holdings": holdings,
        "total_value_today": round(total_today, 2),
        "total_value_yesterday": round(total_yesterday, 2),
        "total_day_change": round(total_today - total_yesterday, 2),
        "total_day_change_pct": (
            round((total_today / total_yesterday - 1) * 100, 2) if total_yesterday else 0
        ),
    }


# --- The menu we hand the model: one tool it can ask us to run ---------------
TOOLS = [
    {
        "name": "get_portfolio_performance",
        "description": (
            "Get today's performance of the user's stock portfolio: per-holding "
            "prices and day change, plus total value and total day change. "
            "Takes no arguments."
        ),
        "input_schema": {"type": "object", "properties": {}},
    }
]


def run_tool(name: str, tool_input: dict):
    if name == "get_portfolio_performance":
        return get_portfolio_performance()
    return {"error": "unknown tool"}


def main() -> None:
    client = get_client()
    messages = [{
        "role": "user",
        "content": "How is my portfolio doing today? Give me a short plain-English summary.",
    }]

    # BEAT 1 - Ask. The model sees the tool menu and decides whether to use it.
    resp = client.messages.create(model=MODEL, max_tokens=700, tools=TOOLS, messages=messages)

    # BEATS 2-3 - If the model asked for the tool, run it and report back.
    if resp.stop_reason == "tool_use":
        tool_block = next(b for b in resp.content if b.type == "tool_use")
        print(f"[agent asked to run: {tool_block.name}]")
        result = run_tool(tool_block.name, tool_block.input)

        # Record the assistant's request FIRST, then our answer (a user turn).
        messages.append({"role": "assistant", "content": resp.content})
        messages.append({"role": "user", "content": [{
            "type": "tool_result",
            "tool_use_id": tool_block.id,
            "content": str(result),
        }]})

        # BEAT 4 - Ask again. Now the model has the data and writes the summary.
        resp = client.messages.create(model=MODEL, max_tokens=700, tools=TOOLS, messages=messages)

    text = next(b.text for b in resp.content if b.type == "text")
    print("\n" + text)


if __name__ == "__main__":
    main()
