"""Module 4 - PRACTICAL example: portfolio agent with short-term + long-term memory.

Same portfolio scenario as Module 3, now with MEMORY:
  - SHORT-TERM: the `messages` list survives across REPL turns, so you can
    say "add TSLA, 3 shares" and then "how are they doing?" and the agent
    understands "they" means the stocks you just talked about.
  - LONG-TERM: holdings persist across script restarts. Backend is decided at
    startup: Supabase (course_holdings table) if SUPABASE_URL/KEY are set,
    otherwise a local JSON file.

Read this, run it, watch the loop. Then fill in your exercise.py.

    python module-04-memory/portfolio_agent.py

------------------------------------------------------------------------------
STORE SWAP: see holdings_store.py. Mock JSON is the offline default; adding
SUPABASE_URL and SUPABASE_KEY to .env flips it to a real database, and the
agent doesn't care. Same shape as the FactIQ mock in Modules 2/3.
This reports numbers only. It is not financial advice.
------------------------------------------------------------------------------
"""
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL

sys.path.append(str(Path(__file__).resolve().parent))
import holdings_store


# --- MOCK previous-close prices ---------------------------------------------
_PREV_CLOSE = {
    "AAPL": 220.00, "MSFT": 430.00, "NVDA": 120.00,
    "TSLA": 250.00, "GOOGL": 180.00, "AMZN": 200.00,
}


def factiq_get_market_data(ticker: str) -> dict:
    """STAND-IN for a real FactIQ market-data call. Fake +/-3% daily move."""
    prev = _PREV_CLOSE.get(ticker.upper())
    if prev is None:
        return {"ticker": ticker, "error": "unknown ticker (not in mock)"}
    daily_move = random.uniform(-0.03, 0.03)
    price = round(prev * (1 + daily_move), 2)
    return {"ticker": ticker.upper(), "price": price, "previous_close": prev}


# --- Tools: 3 memory + 1 market ---------------------------------------------
def get_holdings() -> list:
    return holdings_store.get_holdings()


def add_holding(ticker: str, shares: float) -> str:
    return holdings_store.add_holding(ticker, shares)


def remove_holding(ticker: str) -> str:
    return holdings_store.remove_holding(ticker)


def get_market_data(ticker: str) -> dict:
    return factiq_get_market_data(ticker)


def run_tool(name: str, tool_input: dict):
    if name == "get_holdings":
        return get_holdings()
    if name == "add_holding":
        return add_holding(tool_input["ticker"], tool_input["shares"])
    if name == "remove_holding":
        return remove_holding(tool_input["ticker"])
    if name == "get_market_data":
        return get_market_data(tool_input["ticker"])
    return {"error": f"unknown tool: {name}"}


TOOLS = [
    {
        "name": "get_holdings",
        "description": (
            "Return the user's stock holdings as a list of {ticker, shares}. "
            "Takes no arguments. Call this to learn what tickers the user owns."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "add_holding",
        "description": (
            "Save (or update) a ticker+shares pair to the user's long-term "
            "holdings. Upsert semantics: adding an existing ticker replaces "
            "its share count."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "shares": {"type": "number"},
            },
            "required": ["ticker", "shares"],
        },
    },
    {
        "name": "remove_holding",
        "description": "Remove a ticker from the user's long-term holdings.",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
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


def agent_turn(client, messages: list, max_steps: int = 8) -> str:
    """One user question -> multi-step ReAct loop -> final answer.

    Mutates `messages` in place so the assistant's reasoning + tool calls +
    final answer are all retained for the NEXT user turn (short-term memory).
    """
    for step in range(max_steps):
        resp = client.messages.create(
            model=MODEL, max_tokens=1000, tools=TOOLS, messages=messages
        )

        if resp.stop_reason != "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            return "\n".join(b.text for b in resp.content if b.type == "text")

        messages.append({"role": "assistant", "content": resp.content})

        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                print(f"  [step {step}] {block.name}({block.input}) = {result}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        messages.append({"role": "user", "content": tool_results})

    return "Hit max_steps without finishing."


def repl() -> None:
    print(f"long-term memory backend: {holdings_store.backend_name()}")
    print("Type 'quit' or 'exit' to leave. Your holdings survive restart.\n")

    client = get_client()
    messages = []  # short-term memory: persists across REPL turns, dies on quit

    while True:
        try:
            user = input("you: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user.lower() in {"quit", "exit"}:
            break

        messages.append({"role": "user", "content": user})
        answer = agent_turn(client, messages)
        print(f"agent: {answer}\n")


if __name__ == "__main__":
    repl()
