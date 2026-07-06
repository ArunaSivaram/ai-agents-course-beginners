"""Shared setup so each exercise doesn't repeat boilerplate.

The Anthropic SDK reads your key from the ANTHROPIC_API_KEY environment
variable automatically. We load it from a local .env file via python-dotenv.

NOTE ON MODEL NAMES: these change every few months. If you ever get a
"model not found" / deprecation error, update MODEL below with a current
one from https://docs.claude.com/en/docs/about-claude/models
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from anthropic import Anthropic

# Load .env from the repo root no matter which folder you run a script from.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# A small, fast model is more than enough for every exercise here.
MODEL = "claude-sonnet-4-6"


def get_client() -> Anthropic:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return Anthropic()
