# Module 1 - Structured output walkthrough

**Goal:** reliably turn messy text into a Python dict.
**Time:** ~30 min.
**Before you start:** Module 0 prints a greeting.

## Steps
1. Open `module-01-structured-output/exercise.py`. Read the 5 `SAMPLES`.
2. **TODO 1 - the prompt.** Write a prompt that (a) includes the input text and
   (b) demands JSON only. Be blunt and specific - vague prompts are why parsing fails:
   > "Extract the fields as JSON. Allowed keys: issue_type, product, urgency.
   > urgency must be exactly one of: low, med, high. If product is unknown, use null.
   > Respond with a single JSON object and nothing else - no prose, no markdown fences."
3. **TODO 2 - parse.** `json.loads(raw)` and `return` the dict.
4. Run it:
   ```bash
   python module-01-structured-output/exercise.py
   ```
5. If any input throws a `JSONDecodeError`, don't add try/except to hide it -
   tighten the prompt until all 5 parse cleanly. That prompt-hardening IS the exercise.

## Hints
- Lower randomness helps consistency: you can pass `temperature=0` to `messages.create`.
- If the model wraps output in ```json fences, either tell it not to, or strip them
  before `json.loads`.

## What success looks like
Five Python dicts printed, one per sample, each with your three keys. Zero parse errors.

## Commit
```bash
git add module-01-structured-output/ && git commit -m "Module 1: reliable structured extraction" && git push
```
