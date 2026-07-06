# AI Agents - Hands-On Course (my working repo)

My exercises for learning the basics of AI agents, built from scratch in Python.
Each module pairs one concept with an exercise I actually run. I commit after each
one so I have a reference trail.

## Setup (once)

```bash
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
cp .env.example .env                                 # then paste my real API key into .env
python module-00-setup/hello_world.py                # should print a greeting
```

My API key lives only in `.env`, which is gitignored and never committed.

## How to work through it

Do the modules in order - each builds on the last. The scaffolds have `TODO`
markers; I fill them in. The single most important one is **Module 3** (the
hand-built ReAct loop) - don't skip it for a framework.

| # | Module | Core idea | Done |
|---|--------|-----------|------|
| 0 | setup | verify the toolchain works | [ ] |
| 1 | structured-output | reliable JSON out of an LLM | [ ] |
| 2 | tool-use | model calls a function, I run it | [ ] |
| 3 | react-agent | the reason-act-observe loop, by hand | [ ] |
| 4 | memory | short-term + long-term (survives restart) | [ ] |
| 5 | planning-reflection | plan, execute, self-critique | [ ] |
| 6 | framework | rebuild M3 with CrewAI or LangGraph | [ ] |
| 7 | multi-agent | researcher -> writer handoff | [ ] |
| 8 | eval-guardrails | pass rates, guardrail, human-in-the-loop | [ ] |
| - | capstone | one small agent, end to end | [ ] |

## Notes to self
- Model names change every few months. If I hit a "model not found" error,
  update `MODEL` in `common/client.py` from the current models doc.
- Frameworks move fast too - the M6 picks are a mid-2026 snapshot.
