# Module 5 - Planning & reflection walkthrough

**Goal:** for a multi-part task, make the agent plan first, execute, then critique
and rewrite its own output.
**Time:** ~40 min.
**Before you start:** Module 4 done.

## Why three passes
One-shot answers to multi-part tasks are mediocre. Splitting into plan -> execute ->
reflect reliably improves quality, at the cost of extra calls. A `call()` helper is
already provided so you can focus on the prompts.

## Steps
1. **TODO 1 - PLAN.** Ask for a short numbered plan for `TASK`. Print it.
   > "Break this task into a short numbered plan. Output only the plan."
2. **TODO 2 - EXECUTE.** Ask it to carry out the plan and produce a first draft.
   You can pass the plan back in the prompt so it follows its own steps. Print the draft.
3. **TODO 3 - REFLECT.** Feed the first draft back:
   > "Critique this draft for accuracy and concision, list the specific problems,
   > then output an improved final version."
   Print both the critique and the improved version.
4. Run:
   ```bash
   python module-05-planning-reflection/exercise.py
   ```

## What success looks like
You can see three distinct outputs, and the reflected version is tighter / more
accurate than the first draft. Compare them side by side.

## Commit
```bash
git add module-05-planning-reflection/ && git commit -m "Module 5: plan-execute-reflect pipeline" && git push
```
