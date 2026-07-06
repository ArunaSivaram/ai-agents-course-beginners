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
