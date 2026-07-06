# Start here

This is your guided path through the course. Work top to bottom; each module has
its own `walkthrough.md` with click-by-click steps.

## One-time setup

```bash
cd ai-agents-course
python -m venv .venv && source .venv/bin/activate    # recommended
pip install -r requirements.txt
cp .env.example .env
# open .env and paste your real key after ANTHROPIC_API_KEY=
python module-00-setup/hello_world.py                # prints a greeting = you're good
```

If that last command prints a sentence, your key, SDK, and imports all work.

## The loop you'll repeat for every module

1. Open the module folder and read its `walkthrough.md`.
2. Open `exercise.py` and fill in the `TODO`s, following the walkthrough.
3. Run it. Check it against the "What success looks like" box in the walkthrough.
4. Commit before moving on:
   ```bash
   git add module-0X-name/
   git commit -m "Module X: <what you got working>"
   git push
   ```

## Order (don't skip Module 3)

0. setup - verify toolchain
1. structured-output - reliable JSON from an LLM
2. tool-use - model calls a function you run
3. **react-agent - the core loop, by hand** <- the one that makes agents click
4. memory - short-term + long-term
5. planning-reflection - plan, execute, self-critique
6. framework - rebuild M3 with less code
7. multi-agent - researcher -> writer
8. eval-guardrails - pass rates, guardrail, human approval
9. capstone - one small agent, end to end

## If something breaks

- `RuntimeError: ANTHROPIC_API_KEY is not set` -> you didn't create `.env` or didn't paste the key.
- `model not found` / deprecation -> update `MODEL` in `common/client.py` from
  https://docs.claude.com/en/docs/about-claude/models
- `ModuleNotFoundError: common` -> run scripts from the repo root, e.g.
  `python module-01-structured-output/exercise.py` (not from inside the folder).
