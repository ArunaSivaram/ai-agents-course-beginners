# Module 3 - ReAct agent walkthrough  (THE core module)

**Goal:** an agent that chains multiple tool calls itself until it can answer.
**Time:** ~1 hr. Worth every minute - this is where "agent" stops feeling like magic.
**Before you start:** Module 2's `exercise.py` (single-stock lookup) and
`portfolio_agent.py` (one composite tool) both work.

## What ReAct means
ReAct = **Reason + Act.** The model interleaves reasoning and action:

    Thought -> Action -> Observation -> Thought -> Action -> Observation -> ... -> Answer

In Anthropic's API this is structured (no string parsing needed):
- **Action**      = a `tool_use` block the model emits
- **Observation** = the `tool_result` you send back
- **Answer**      = `stop_reason == "end_turn"` with a text block

Module 2 handled ONE tool call. An agent is that same handling wrapped in a
`for` loop, so the model can call a tool, see the result, decide it needs
another, and keep going until it's done.

## The insight vs Module 2's portfolio_agent
Module 2 exposed ONE composite tool: `get_portfolio_performance()`. Your Python
knew the plan (loop over holdings, sum values). Module 3 exposes TWO primitives:
`get_holdings()` and `get_market_data(ticker)`. **The model decides the plan.**

Trade-off:
- Module 2 composite - predictable, but the plan is hardcoded. Add "just show
  me AAPL today" and you need a new tool.
- Module 3 ReAct - the same 2 primitives handle "full portfolio", "just AAPL",
  "how many shares of MSFT do I own" - the model composes at runtime. Cost:
  less predictable; the model might chain wrong.

## Steps (fill in the `agent()` function in exercise.py)
1. **TODO 1 - done check.** At the top of each iteration, after `create(...)`:
   if `resp.stop_reason != "tool_use"`, the model is finished. Find the text
   block in `resp.content` and `return` its `.text`.
2. **TODO 2 - append the assistant turn.**
   ```python
   messages.append({"role": "assistant", "content": resp.content})
   ```
3. **TODO 3 - run every tool call.** A single turn can contain MORE THAN ONE
   `tool_use` block (parallel tool calls), so loop:
   ```python
   tool_results = []
   for block in resp.content:
       if block.type == "tool_use":
           result = run_tool(block.name, block.input)
           print(f"[step {step}] {block.name}({block.input}) = {result}")  # watch the loop
           tool_results.append({
               "type": "tool_result",
               "tool_use_id": block.id,
               "content": str(result),
           })
   messages.append({"role": "user", "content": tool_results})
   ```
4. Keep the `max_steps` cap - it's the circuit breaker that stops a confused
   agent from looping forever.
5. Run:
   ```bash
   python module-03-react-agent/exercise.py
   ```

## What success looks like
Your prints show step 0 calling `get_holdings()`, step 1 calling
`get_market_data(...)` (probably in parallel for all 3 tickers in one turn),
and the FINAL answer summarizing total value and day change. **Zero help from
you between calls** - the model figured out the plan.

## Try this after it works
- Ask "just show me AAPL today" - watch it call `get_holdings` first (or skip
  it), then only one `get_market_data`. Same tools, different plan.
- Ask "how many shares of MSFT do I own?" - watch it call ONLY `get_holdings`
  and skip market data entirely.
- Print the text blocks in each turn too, and you'll literally see the model
  reason between actions.

**Same 2 tools, three different plans, zero code changes.** THAT is what
ReAct buys you.

## Common pitfalls
- Forgetting `messages.append({"role": "assistant", "content": resp.content})`
  before the tool_results - the API needs both, in order.
- Not looping over `resp.content` - a single turn can contain multiple
  `tool_use` blocks (parallel calls) and if you handle only the first, the
  model will keep asking for the others.
- No `max_steps` cap - a confused model will loop forever.
- `tool_use_id` must exactly match the incoming `block.id`.

## Commit
```bash
git add module-03-react-agent/ && git commit -m "Module 3: portfolio ReAct agent" && git push
```

---

## Practical example: `portfolio_agent.py`

Once your `exercise.py` runs, open **`portfolio_agent.py`** in this folder.
Same two-primitive ReAct agent, complete and runnable. Read it, run it, then
compare it to your `exercise.py` to see the same pattern from another angle:

```bash
python module-03-react-agent/portfolio_agent.py
```

### About FactIQ (real) and the mock
Same as Module 2 - `factiq_get_market_data()` is a MOCK. To go live you replace
its body with a real FactIQ MCP/API call. The primitives, tools list, agent
loop, and message-passing all stay identical.

The two-tool split matches FactIQ's real shape: FactIQ serves market data per
ticker; your holdings live in your own data. That clean seam is why the ReAct
agent transfers cleanly to production.

### How this evolves in Module 4
You'll add **memory**. The `MY_HOLDINGS` list you're hardcoding here moves into
a long-term store (JSON, DB, or an MCP memory server) that persists across
conversations. The agent will look up holdings on demand instead of having them
sitting in a Python global - and remember them between sessions.
