# Module 8 - Evaluation & guardrails walkthrough

**Goal:** know whether your agent works, stop it from guessing with no evidence,
and gate risky actions behind human approval.
**Time:** ~1 hr.
**Before you start:** Module 3+ agent available to test.

## Three things to add
1. **Eval set** - fixed inputs with an expected substring, so "good" is defined
   BEFORE you look at outputs.
2. **Guardrail** - if there's no supporting evidence, the agent must say
   "insufficient evidence" instead of hallucinating.
3. **Human-in-the-loop (HITL)** - before any write action, pause for approval.

## Steps
1. **EVAL_CASES.** Add 3 more `(input, expected_substring)` tuples with clear
   acceptable answers. Keep the Atlantis case - it should trigger the guardrail.
2. **`guardrail_check`.** Return `False` when evidence is empty or `"no result"`,
   so your agent branches to an "insufficient evidence" reply.
3. **Wire the guardrail into your agent.** Before it answers from a tool result,
   call `guardrail_check(evidence)`; if False, return the refusal instead.
4. **`human_gate` (already written).** Call it before any action that would write /
   send / delete. Only proceed if it returns True.
5. **`run_evals`.** Run the agent on each case, check the expected substring appears,
   tally, and print `X / N passed`.
6. Run:
   ```bash
   python module-08-eval-guardrails/exercise.py
   ```

## What success looks like
- A printed pass rate like `4 / 5 passed`.
- The Atlantis question returns "insufficient evidence", not a made-up number.
- A write action prints its intent and waits for you to type `approve`.

## Why this matters
This is the difference between a demo and something trustworthy. Note how the
"refuse without evidence" guardrail is the same principle as grounding an agent in
real retrieved data rather than letting it invent answers.

## Commit
```bash
git add module-08-eval-guardrails/ && git commit -m "Module 8: eval set + evidence guardrail + HITL gate" && git push
```
