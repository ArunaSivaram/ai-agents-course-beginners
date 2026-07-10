"""Module 4 - Memory.

GOAL: give your agent both kinds of memory:
  - SHORT-TERM: the `messages` list persists across REPL turns, so the agent
                remembers what you said earlier in this session.
  - LONG-TERM:  holdings live in a store that survives script restart.
                Backend is Supabase if configured, else a local JSON file.

SUCCESS: run once and say "add TSLA, 3 shares", then quit. Run AGAIN and ask
         "what do I own?" - the agent finds TSLA in long-term memory.

Build on Module 3's ReAct loop. Now with 4 tools:
  - get_holdings()               - long-term read
  - add_holding(ticker, shares)  - long-term write
  - remove_holding(ticker)       - long-term write
  - get_market_data(ticker)      - the FactIQ mock from Module 3

Run:  python module-04-memory/exercise.py
"""
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL

# holdings_store is in this same folder.
sys.path.append(str(Path(__file__).resolve().parent))
import holdings_store


# --- MOCK previous-close prices (same shape as Module 3, a few extras added) ---
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


# --- Tool implementations: three call the long-term store; one is FactIQ ------
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


# TODO 1: declare the 4 tools using the same schema shape as Module 3.
#         - get_holdings:    no args        (properties: {})
#         - add_holding:     ticker, shares (shares is number)
#         - remove_holding:  ticker
#         - get_market_data: ticker
TOOLS = [
    # your 4 tool schemas here
]


def agent_turn(client, messages: list, max_steps: int = 8) -> str:
    """One user question -> multi-step ReAct loop -> final answer.

    Mutates `messages` in place, so the assistant's reasoning + tool calls +
    final text are all retained for the NEXT user turn (short-term memory).
    """
    for step in range(max_steps):
        resp = client.messages.create(
            model=MODEL, max_tokens=1000, tools=TOOLS, messages=messages
        )

        # ANSWER?
        if resp.stop_reason != "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            return "\n".join(b.text for b in resp.content if b.type == "text")

        # THOUGHT + ACTIONS: keep the assistant's turn intact.
        messages.append({"role": "assistant", "content": resp.content})

        # OBSERVATIONS.
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
    # TODO 2: wire up the short-term-memory REPL.
    #   1. print(f"backend = {holdings_store.backend_name()}") so you see
    #      which store is live (mock or supabase).
    #   2. client = get_client()
    #   3. messages = []
    #   4. while True:
    #        user = input("you: ")
    #        if user.strip().lower() in {"quit", "exit"}:
    #            break
    #        messages.append({"role": "user", "content": user})
    #        answer = agent_turn(client, messages)
    #        print(f"agent: {answer}\n")
    #   Because `messages` persists across iterations, the agent remembers
    #   what you said earlier in this session (short-term memory).
    #
    # TODO 3: prove long-term memory
    #   - Run: `python module-04-memory/exercise.py`, say "add TSLA, 3 shares",
    #     the agent should call add_holding. Then type "quit".
    #   - Run it AGAIN: ask "what do I own?" - the agent should call
    #     get_holdings and see TSLA is still there.
    print("Wire up the REPL, then test the restart behavior.")


if __name__ == "__main__":
    repl()
