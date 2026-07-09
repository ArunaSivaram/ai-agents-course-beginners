# Module 2 - Tool use walkthrough

**Goal:** the model decides to call a function; you run it and hand the result back.
**Time:** ~45 min. This is the mechanic every agent is built from - go slow here.
**Before you start:** Module 1 done.

## The four-beat pattern (memorize it)
1. You describe tools -> `tools=[{"name","description","input_schema"}]`.
2. Model replies. If it wants a tool: `resp.stop_reason == "tool_use"`.
3. Inside `resp.content` there's a block with `.type == "tool_use"`, carrying
   `.id`, `.name`, and `.input` (a dict of arguments).
4. You run the function, then send the result back as a **new user message**
   containing a `tool_result` block that points at that `.id`.

## Steps
1. Open `exercise.py`. `TOOLS` and `get_ticket_status` are already defined.
2. **TODO 1 - find the tool call.** After the first `create(...)`, loop over
   `resp.content` and grab the block where `block.type == "tool_use"`.
3. **TODO 2 - run it.** `result = get_ticket_status(**block.input)`.
4. **TODO 3 - close the loop.** Append two turns to `messages`:
   ```python
   messages.append({"role": "assistant", "content": resp.content})
   messages.append({"role": "user", "content": [{
       "type": "tool_result",
       "tool_use_id": block.id,
       "content": str(result),
   }]})
   ```
5. **TODO 4 - final answer.** Call `create(...)` again with the updated `messages`
   and print the text. (Find the block where `.type == "text"` and print `.text`.)
6. Run:
   ```bash
   python module-02-tool-use/exercise.py
   ```

## What success looks like
You see the model request `get_ticket_status` for id `403`, you return the dict,
and the model's final answer describes it as escalated / owned by billing / 6 days old.

## Common pitfalls
- Forgetting to append the assistant turn (`resp.content`) before the tool_result -
  the API needs both, in order.
- `tool_use_id` must exactly equal `block.id`.
- Passing tools but never handling `stop_reason == "tool_use"` -> the model just
  keeps asking for the tool.

## Commit
```bash
git add module-02-tool-use/ && git commit -m "Module 2: single tool call round-trip" && git push
```

---

## Practical example: a portfolio agent that talks to FactIQ

Once the ticket demo makes sense, open **`portfolio_agent.py`** in this folder. It's
the same four-beat mechanic in a real scenario: you ask *"how's my portfolio doing
today?"*, the agent calls a tool to fetch the numbers, then reports back in plain
English. Unlike `exercise.py`, this file is **complete and runnable** - read it, run
it, and watch the pattern work:

```bash
python module-02-tool-use/portfolio_agent.py
```

Map it back to the phone-call analogy:
- **The menu** = `TOOLS` lists one tool, `get_portfolio_performance`.
- **The friend asks** = `stop_reason == "tool_use"`; the agent requests that tool.
- **You do the work** = `run_tool(...)` runs it locally (pulling prices, summing values).
- **You report back** = assistant turn appended first, then the `tool_result` user turn.
- **The friend answers** = the second `create(...)` call, where it narrates the summary.

### About FactIQ (real) and the mock
FactIQ (https://www.factiq.com) is a genuine data service **built for AI agents**. In
production you reach it through its **MCP server** (`https://api.factiq.com/mcp`) over an
OAuth connection - there's a free account, and a ready-made Claude Code plugin at
`github.com/defog-ai/factiq-plugin`. Real OAuth would bury this lesson, so
`factiq_get_market_data()` is a clearly-labelled **MOCK with fake prices**.

Here's the payoff of the tool-use pattern: to go live, you replace the body of that
**one function** with a real FactIQ call. The agent loop, the tools menu, the
message-passing - none of it changes. That clean seam between "the agent" and "where
the data comes from" is exactly what tool use buys you.

> Note: this reports numbers, not investment advice.

### How this evolves in Module 3
Right now the agent calls **one** tool that does everything internally. In Module 3
you'll instead expose **two** tools - `get_holdings()` and `get_market_data(ticker)` -
and let the agent **chain them itself**: fetch your holdings, then loop calling market
data for each ticker, then total it up. That's the same portfolio, rebuilt as a real
multi-step agent. (It also matches FactIQ's actual shape: FactIQ gives you market data
per ticker; your holdings are your own data.)
