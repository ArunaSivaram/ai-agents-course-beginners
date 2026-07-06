# Capstone walkthrough

**Goal:** combine everything into one small agent you'd actually use.
**Time:** 2-4 hrs.

## Steps
1. **Pick a narrow task.** Good scopes: message triage + draft replies; a research
   assistant; a Q&A agent over a folder of your own notes. Narrow beats ambitious.
2. **Scaffold three files in this folder:**
   - `agent.py` - the agent
   - `evals.py` - 5 test cases + a pass-rate runner
   - `NOTES.md` - your write-up
3. **Hit all five requirements** (checklist in this folder's README):
   two tools, memory (short + long), a plan-then-execute step, one guardrail + one
   HITL gate, and a 5-case eval with a recorded pass rate.
4. **Reuse your own code.** Lift the ReAct loop from M3, memory from M4, the
   plan/reflect pattern from M5, and the guardrail + eval harness from M8. The
   capstone is assembly, not invention.
5. **Write NOTES.md:** what it does, its tools, its failure modes, its eval results.
   That write-up is the proof you understand agents end to end.

## What success looks like
A running agent that passes most of its own eval set, refuses to act on thin
evidence, asks before writing, and remembers across restarts - plus a NOTES.md that
honestly documents where it still fails.

## Commit
```bash
git add capstone/ && git commit -m "Capstone: <your agent> - end to end with evals" && git push
```
