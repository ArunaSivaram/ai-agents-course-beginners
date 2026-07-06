# Module 7 - Multi-agent walkthrough

**Goal:** a Researcher agent hands off to a Writer agent; together they do a task
neither does alone.
**Time:** ~45 min.
**Before you start:** Module 5 done (you're comfortable with multi-call flows).

## The shape
This is the simplest multi-agent pattern: a **sequential handoff**. Output of agent
A becomes input to agent B. You can build it with two plain functions (provided as
stubs) - no framework required, though you may use your Module 6 one if you like.

## Steps
1. **TODO - researcher.** Prompt the model to return a bulleted list of factual
   points on `topic`. Return the text.
2. **TODO - writer.** Prompt the model to turn those notes into exactly 5 sentences.
   Return the text.
3. Run:
   ```bash
   python module-07-multi-agent/exercise.py
   ```
4. **Now break it on purpose.** Change `topic` to something nonsensical the model
   can't research well, rerun, and watch the weak notes produce a weak brief. That
   failure flowing downstream is the real lesson of multi-agent systems.

## What success looks like
Two clearly separate outputs (NOTES then BRIEF), where the brief is a clean 5-sentence
distillation of the notes - and, in the broken run, you can see how bad input to the
Researcher corrupts the Writer's output.

## Commit
```bash
git add module-07-multi-agent/ && git commit -m "Module 7: researcher->writer handoff + failure propagation" && git push
```
