# Module 0 - Setup walkthrough

**Goal:** confirm your whole toolchain works before writing any agent code.
**Time:** ~10 minutes.

## Steps

1. From the repo root, create and activate a virtual environment (optional but tidy):
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create your env file and add your key:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and replace the placeholder after `ANTHROPIC_API_KEY=` with your real key.
4. Run the check:
   ```bash
   python module-00-setup/hello_world.py
   ```

## What success looks like
The script prints a one-sentence greeting from the model. No errors.

## Understand what just happened
- `common/client.py` loaded your key from `.env` and created an `Anthropic()` client.
- `client.messages.create(...)` sent one message and got one reply.
- `resp.content` is a **list of blocks**; a plain text reply is `resp.content[0].text`.
That single request/response is the atom every later module builds a loop around.

## Commit
```bash
git add -A && git commit -m "Module 0: setup verified" && git push
```
