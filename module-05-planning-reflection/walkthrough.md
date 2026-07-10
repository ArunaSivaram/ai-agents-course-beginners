# Module 5 - Planning + reflection walkthrough

**Goal:** for a real portfolio-review task, run THREE passes - plan, execute,
reflect - and see the reflected output beat the first draft.
**Time:** ~40 min.
**Before you start:** Module 4 works. Your holdings sit in Supabase (or in the
JSON fallback).

## Why three passes

One-shot ReAct answers to a multi-part task (get data + analyze + recommend)
are often mediocre - the first thing off the tongue mixes reasoning with
output. Splitting the work into three passes reliably improves quality:

- **PLAN** - the model writes down what it's about to do BEFORE touching tools.
  Cheap, no tool cost. Catches "what am I actually solving?" mistakes early.
- **EXECUTE** - the ReAct loop from Module 4 gathers data and drafts an answer,
  guided by the plan.
- **REFLECT** - the model reads its own draft, lists problems with it, and
  rewrites. Same generator, adversarial hat on. This is where hand-waving,
  bad recommendations, and inconsistencies get caught.

Total: ~5-7 API calls per run instead of 3-4. In exchange, the output is
tighter, more actionable, and less prone to "on the one hand / on the other
hand" fluff.

## The task

```
Give me an actionable review of my portfolio today: how it's performing,
which positions are working and which aren't, and ONE concrete recommendation.
Keep the whole review under ~150 words.
```

Three constraints in one sentence (performance, winners/losers, ONE rec, word
budget) - the kind of prompt where reflection actually improves things.

## Steps (fill in `main()` in exercise.py)

1. **TODO 1 - PLAN.** Ask the model for a short numbered plan for the task.
   Text-only call, no tools:
   ```
   You have these tools available: get_holdings, get_market_data.
   Break the following task into a short numbered plan (3-5 steps).
   Output ONLY the numbered plan. Task: {TASK}
   ```
   Naming the tools in the plan prompt is important - otherwise the model
   plans in the abstract and the plan doesn't match what EXECUTE can do.
2. **TODO 2 - EXECUTE.** Build a `messages` list whose first user turn contains
   BOTH the task and the plan, then call `react_execute(client, messages)`.
   The ReAct loop will chain `get_holdings` and `get_market_data` on its own,
   guided by the plan text.
3. **TODO 3 - REFLECT.** Feed the first draft back for critique + rewrite:
   ```
   Critique this portfolio analysis draft for accuracy, actionability, and
   concision. Output two sections:
   CRITIQUE: bullet points listing specific problems
   IMPROVED VERSION: the rewritten analysis
   Original task: {TASK}
   Draft to critique: {draft}
   ```
4. Run:
   ```bash
   python module-05-planning-reflection/exercise.py
   ```

## What success looks like

Three visibly distinct outputs on screen:
- A numbered plan (3-5 short steps).
- A first-draft review (~150-250 words - draft often overshoots the budget).
- A critique + improved version. The improved version should feel tighter and
  more actionable than the draft. Diff them mentally.

## Try this after it works

- **Two reflections instead of one.** Feed the improved version back for a
  second reflection. Diminishing returns after ~2 passes - useful signal for
  how much reflection is worth in production.
- **Ablation: skip the plan.** Comment out TODO 1 and pass an empty plan to
  EXECUTE. Compare the drafts. When does the plan matter most?
- **Adversarial critique prompt.** Change REFLECT's prompt to "critique as if
  you were a skeptical portfolio manager who thinks the draft is naive."
  Watch the recommendation get more specific / better-justified.

## Common pitfalls

- **Plan mentions tools that don't exist.** If your plan says "search the web
  for news" but there's no such tool, EXECUTE will either hallucinate or
  refuse. Fix: name your available tools in the PLAN prompt.
- **Draft and reflection use different context.** REFLECT only sees the draft
  text - it can't fact-check numbers. If numbers matter, either include the
  raw data in the reflect prompt, or trust EXECUTE's tool calls to be right.
- **Reflection makes it worse.** Occasionally the "improved" version is more
  verbose or misses the point. Trigger for a real system: run BOTH draft and
  reflection past a scorer (Module 8) and pick the better one.

## Commit

```bash
git add module-05-planning-reflection/ \
  && git commit -m "Module 5: portfolio review with plan+execute+reflect" \
  && git push
```

---

## Practical example: `portfolio_agent.py`

Once your `exercise.py` works, open **`portfolio_agent.py`** in this folder.
Same three-pass pipeline, complete and runnable:

```bash
python module-05-planning-reflection/portfolio_agent.py
```

### Design note: read-only tools for a review task

The exercise uses only `get_holdings` and `get_market_data` - even though
Module 4 gave the agent `add_holding` and `remove_holding` too. A review
task shouldn't be able to silently mutate your portfolio. Deliberately
narrowing the tool set for the current job is the same principle as least
privilege in security: give the agent exactly what it needs to succeed and
nothing more.

### How this evolves in Module 6

Module 6 rebuilds today's pipeline using a **framework** (LangGraph or
CrewAI). You'll see the same three passes expressed as a graph of nodes
with edges, and how much scaffolding a framework hides. It also shows the
cost of the framework - what YOU know about the loop that the framework
abstracts away.
