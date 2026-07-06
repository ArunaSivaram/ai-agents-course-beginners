# Module 3 - ReAct agent walkthrough  (THE core module)

**Goal:** a loop that reasons -> acts -> observes -> repeats, chaining multiple
tool calls on its own until it produces a final answer.
**Time:** ~1 hr. Worth every minute - this is where agents stop being mysterious.
**Before you start:** Module 2's single round-trip works.

## The insight
Module 2 handled ONE tool call. An agent is that same handling wrapped in a
`while`/`for` loop, so the model can call a tool, see the result, decide it needs
ANOTHER tool, and keep going until it's done. You already know every piece - now
you're just repeating it until `stop_reason != "tool_use"`.

## Steps (fill in the `agent()` function)
1. **TODO 1 - done check.** At the top of each iteration, after `create(...)`:
   if `resp.stop_reason != "tool_use"`, the model is finished. Find the text block
   and `return` its `.text`.
2. **TODO 2 - append the assistant turn.**
   ```python
   messages.append({"role": "assistant", "content": resp.content})
   ```
3. **TODO 3 - run every tool call.** A single turn can contain more than one
   `tool_use` block, so loop:
   ```python
   tool_results = []
   for block in resp.content:
       if block.type == "tool_use":
           result = run_tool(block.name, block.input)
           print(f"  -> {block.name}({block.input}) = {result}")   # watch the loop
           tool_results.append({
               "type": "tool_result",
               "tool_use_id": block.id,
               "content": str(result),
           })
   messages.append({"role": "user", "content": tool_results})
   ```
4. Keep the `max_steps` cap - it stops a confused agent from looping forever.
5. Run:
   ```bash
   python module-03-react-agent/exercise.py
   ```

## What success looks like
Your prints show the agent call `search("tokyo population")`, then
`search("yokohama population")`, then `calculator("14000000 + 3770000")`, and the
FINAL line reports ~17,770,000. Two-plus tool calls chained with zero help from you.

## Try this after it works
- Ask a 3-city question and watch it make more calls.
- Add a print of the model's reasoning text blocks too - you'll literally see it think.

## Commit
```bash
git add module-03-react-agent/ && git commit -m "Module 3: working ReAct loop, multi-tool chaining" && git push
```
