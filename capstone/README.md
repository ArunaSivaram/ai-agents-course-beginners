# Capstone - one small agent, end to end

Pick a narrow task you'd actually use (message triage + draft replies, a
research assistant, a notes Q&A agent, etc.). Build it once - by hand or in your
framework, your call. You've now done both.

## Requirements - hit all five
- [ ] At least **two tools**
- [ ] **Memory**: short-term conversation + one long-term fact store
- [ ] A **plan-then-execute** step for any multi-part work
- [ ] One **guardrail** and one **human-in-the-loop** gate
- [ ] A **5-case eval** with a recorded pass rate

## Deliverable
A half-page write-up in this folder covering: what it does, its tools, its
failure modes, and its eval results. That write-up is the proof you understand
agents.

## Suggested files
- `agent.py` - your agent
- `evals.py` - your 5 test cases + pass-rate runner
- `NOTES.md` - the write-up
