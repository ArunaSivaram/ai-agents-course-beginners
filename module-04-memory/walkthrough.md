# Module 4 - Memory walkthrough

**Goal:** conversation memory across turns (short-term) + a fact store that
survives a restart (long-term).
**Time:** ~45 min.
**Before you start:** your Module 3 loop works - you'll reuse it.

## Two memories, don't conflate them
- **Short-term** = the `messages` list you keep appending to within a run. It lives
  only as long as the process.
- **Long-term** = data written OUTSIDE the model (here, `memory_store.json`) that you
  read back later. `remember()` and `recall()` are already written for you.

## Steps
1. **TODO 1 - declare tools.** Give `remember` and `recall` the same tool schema
   shape as Module 3. `remember` takes `{"fact": string}`; `recall` takes no args
   (`"properties": {}`, no `required`).
2. **TODO 2 - a REPL loop for short-term memory.** Wrap your Module 3 agent in:
   ```python
   messages = []
   while True:
       user = input("you: ")
       if user.strip() in {"quit", "exit"}:
           break
       messages.append({"role": "user", "content": user})
       # ... run your ReAct loop, appending assistant + tool_result turns to `messages`
   ```
   Because `messages` persists across turns, the agent remembers earlier things you
   said within the session.
3. **TODO 3 - prove long-term memory.**
   - Run it, say `my name is <you>` (the agent should call `remember`), then `quit`.
   - Run it AGAIN, ask `what's my name?` - it should call `recall` and answer correctly.

## What success looks like
After a full restart of the script, the agent still knows your name because it read
it from `memory_store.json`. (That file is gitignored - it won't be committed.)

## Commit
```bash
git add module-04-memory/ && git commit -m "Module 4: short-term REPL + persistent long-term memory" && git push
```
