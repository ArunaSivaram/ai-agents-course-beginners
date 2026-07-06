"""Module 0 - verify your whole setup end to end.

    python module-00-setup/hello_world.py

Success: the model prints a short greeting. If it does, your key, SDK,
and imports all work and you're ready for Module 1.
"""
import sys
from pathlib import Path

# Make `common` importable when running this file directly.
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.client import get_client, MODEL


def main() -> None:
    client = get_client()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hello in one short sentence."}],
    )
    # A response's .content is a list of blocks; a plain text reply is block 0.
    print(resp.content[0].text)


if __name__ == "__main__":
    main()
