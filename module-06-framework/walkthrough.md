# Module 6 - Framework walkthrough

**Goal:** rebuild your Module 3 agent with a real framework and feel how much
boilerplate disappears.
**Time:** ~1 hr (mostly reading the framework's quickstart).
**Before you start:** Module 3 works - you'll port it.

## Pick one (mid-2026 snapshot - re-verify before relying on it)
- **CrewAI** - gentlest start, role-based. `pip install crewai`
- **LangGraph** - industry standard, agent-as-state-graph, steeper but most transferable.
  `pip install langgraph`

Uncomment your pick in `requirements.txt`, then `pip install -r requirements.txt`.

## Steps
1. Read your chosen framework's official quickstart (5-10 min).
2. **TODO 2 - tools.** Re-declare the same `search` and `calculator` in the
   framework's tool format.
3. **TODO 3 - agent.** Build ONE agent with those tools and run the same
   Tokyo+Yokohama question from Module 3.
4. **TODO 4 - reflect in a comment.** Write one line naming something the framework
   did for you that you hand-coded in Module 3 (the tool loop? message state? retries?).

## What success looks like
Same ~17,770,000 answer as your hand-built agent, with noticeably less code - and
you can articulate exactly what the framework abstracted away.

## Commit
```bash
git add module-06-framework/ requirements.txt && git commit -m "Module 6: ported ReAct agent to <framework>" && git push
```
