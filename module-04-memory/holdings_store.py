"""Holdings store - the LONG-TERM MEMORY that survives a script restart.

TWO BACKENDS, one API. Which one is used depends on your environment:

  MOCK (default):  a local JSON file at holdings_store.json in this folder.
                   Zero setup. Runs offline. Great for the first read-through.
  REAL (Supabase): a `course_holdings` table in your local Supabase project.
                   Activated automatically when SUPABASE_URL and SUPABASE_KEY
                   are set in .env.

The public API - get_holdings(), add_holding(), remove_holding() - is IDENTICAL
across backends, so the tools that call this module never change. That "swap
one function's body, everything else stays" pattern is the same one you saw in
Module 2 with the FactIQ mock.

To go live: fill in SUPABASE_URL + SUPABASE_KEY in .env. That's it.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the repo root so SUPABASE_URL/KEY are picked up whichever
# folder you run a script from. Same pattern as common/client.py.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

_JSON_PATH = Path(__file__).resolve().parent / "holdings_store.json"

# Seed used on FIRST run of the mock backend, so you don't start empty.
_SEED = [
    {"ticker": "AAPL", "shares": 10},
    {"ticker": "MSFT", "shares": 5},
    {"ticker": "NVDA", "shares": 8},
]


def _use_supabase() -> bool:
    return bool(os.environ.get("SUPABASE_URL")) and bool(os.environ.get("SUPABASE_KEY"))


def backend_name() -> str:
    """For a one-line status print at agent startup."""
    return "supabase (course_holdings)" if _use_supabase() else f"mock json ({_JSON_PATH.name})"


# --- MOCK backend: JSON file --------------------------------------------------
def _load_json() -> list:
    if not _JSON_PATH.exists():
        _JSON_PATH.write_text(json.dumps(_SEED, indent=2))
    return json.loads(_JSON_PATH.read_text())


def _save_json(data: list) -> None:
    _JSON_PATH.write_text(json.dumps(data, indent=2))


# --- REAL backend: Supabase ---------------------------------------------------
_client = None


def _get_client():
    """Lazy so the import doesn't fail when running in mock mode."""
    global _client
    if _client is None:
        from supabase import create_client
        _client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    return _client


# --- Public API: same shape for both backends --------------------------------
def get_holdings() -> list:
    """Return every ticker/shares row currently stored."""
    if _use_supabase():
        return _get_client().table("course_holdings").select("*").execute().data
    return _load_json()


def add_holding(ticker: str, shares: float) -> str:
    """Upsert semantics: adding an existing ticker replaces its share count."""
    ticker = ticker.upper()
    if _use_supabase():
        _get_client().table("course_holdings").upsert(
            {"ticker": ticker, "shares": shares}
        ).execute()
    else:
        data = _load_json()
        data = [h for h in data if h["ticker"] != ticker]
        data.append({"ticker": ticker, "shares": shares})
        _save_json(data)
    return f"saved {ticker}: {shares} shares"


def remove_holding(ticker: str) -> str:
    ticker = ticker.upper()
    if _use_supabase():
        _get_client().table("course_holdings").delete().eq("ticker", ticker).execute()
    else:
        data = _load_json()
        data = [h for h in data if h["ticker"] != ticker]
        _save_json(data)
    return f"removed {ticker}"
