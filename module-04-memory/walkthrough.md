# Module 4 - Memory walkthrough

**Goal:** a portfolio agent with TWO kinds of memory - one that lasts a
conversation, one that lasts across restarts.
**Time:** ~1 hr (add ~10 min if you're standing up Supabase for the first time).
**Before you start:** Module 3's portfolio ReAct agent works.

## The two memories - don't conflate them

| | Short-term | Long-term |
|---|---|---|
| **What** | The `messages` list you keep appending to | Data written OUTSIDE the model |
| **Lives for** | One process / one REPL session | Forever (or until you delete it) |
| **Dies when** | You quit the script | Never (unless you `remove_holding`) |
| **Backed by** | Python memory | Supabase table (or JSON file) |
| **Tools involved** | None - it's just message history | `get_holdings`, `add_holding`, `remove_holding` |

Both are needed. Short-term lets the agent say "sure, add TSLA" and then in
the next turn understand "how are they doing?" means the stocks you just added.
Long-term lets you close the script, come back tomorrow, and still have your
holdings there.

## The long-term backend: Supabase (with a JSON fallback)

Long-term memory needs somewhere OUTSIDE Python to live. This module gives you
two backends, chosen automatically:

- **Supabase (real DB)** - used if `SUPABASE_URL` and `SUPABASE_KEY` are set in
  `.env`. Persists in a `course_holdings` table.
- **Mock JSON file** - used otherwise. Writes to `holdings_store.json` in this
  folder (gitignored). Zero setup, offline, great for a first read-through.

The public API in `holdings_store.py` is IDENTICAL either way - the tools
that call it never need to know which backend is live. That's the same
mock-and-swap pattern you saw with FactIQ in Modules 2/3.

### Set up Supabase (skip if you'll use the mock)

Using the local Supabase CLI:

```bash
# In a project directory where you've run `supabase init` and `supabase start`
supabase status   # copy the API URL and the publishable / anon key
```

Then in **Studio** (usually http://127.0.0.1:54323) → SQL Editor:

```sql
create table course_holdings (
  ticker text primary key,
  shares numeric not null check (shares > 0)
);

alter table course_holdings disable row level security;
grant select, insert, update, delete on public.course_holdings to anon;

insert into course_holdings (ticker, shares) values
  ('AAPL', 10), ('MSFT', 5), ('NVDA', 8);
```

> **Why both `disable RLS` AND `grant`?** RLS off means "no policy filters
> apply". `grant` is standard Postgres permissions - the `anon` role still
> needs privileges on the table. Supabase Studio may re-enable RLS after
> table creation; if `get_holdings` returns 0 rows, run the `alter table ...
> disable row level security` again from Studio or via `docker exec`.

Add these two lines to `.env`:

```
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=sb_publishable_...   # the publishable key from `supabase status`
```

If you leave them out, `holdings_store.py` will fall back to the mock JSON
file - the rest of the module works identically.

## Steps (fill in `exercise.py`)

1. **TODO 1 - declare the 4 tools.** Same schema shape as Module 3:
   - `get_holdings` - no args (`"properties": {}`)
   - `add_holding` - `ticker` (string), `shares` (number)
   - `remove_holding` - `ticker` (string)
   - `get_market_data` - `ticker` (string)
2. **TODO 2 - the REPL.** Loop `input()` -> append user turn -> call
   `agent_turn(client, messages)` -> print answer. Because `messages` isn't
   reset between iterations, the agent remembers earlier turns
   (short-term memory).
3. **TODO 3 - prove long-term memory.** Restart-proof test:
   - Run it. Say "add TSLA to my portfolio, 3 shares." The agent should call
     `add_holding`.
   - Type `quit`.
   - Run it AGAIN. Ask "what do I own?" The agent should call `get_holdings`
     and TSLA should be in the answer.

## What success looks like

After a full script restart, the agent still knows about TSLA because it read
it from `course_holdings` (or `holdings_store.json`). That crossing-the-restart
moment is the whole point of long-term memory.

## Try this after it works

- **Short-term flex:** run the REPL, say "add TSLA, 3 shares", then in the NEXT
  turn ask "how are they doing today?" - watch it understand "they" via
  short-term memory and call `get_market_data("TSLA")`.
- **Combined flex:** ask "what's my portfolio worth today?" - watch it chain
  `get_holdings` -> N x `get_market_data` -> multiply/sum. Same ReAct pattern
  as Module 3, plus persistent holdings.
- **Backend swap:** delete the `SUPABASE_URL` line from `.env` and restart.
  The banner at the top says `mock json` instead of `supabase`. Add a holding.
  Restart. It's still there - but in `holdings_store.json` this time.

## Common pitfalls

- **`permission denied for table course_holdings`** - the `anon` role has no
  privileges. Re-run the `grant` statement in the SQL block above.
- **Client returns 0 rows even though `SELECT` in psql shows rows** - RLS is
  still enabled. Re-run `alter table ... disable row level security`.
- **REPL loses context between turns** - you accidentally reset `messages`
  inside the loop instead of appending. It has to persist across iterations.
- **`get_holdings` returns stale data mid-session** - the agent's own answer
  might reference cached data; make sure the tool actually re-reads the store.

## Commit

```bash
git add module-04-memory/ requirements.txt .gitignore \
  && git commit -m "Module 4: portfolio memory - short-term REPL + Supabase long-term" \
  && git push
```

Note: `holdings_store.json` is gitignored - it never gets committed.

---

## Practical example: `portfolio_agent.py`

Once your `exercise.py` runs, open **`portfolio_agent.py`** in this folder.
Same 4-tool ReAct agent + REPL, complete and runnable. Read it, run it, and
watch the same pattern from another angle:

```bash
python module-04-memory/portfolio_agent.py
```

### The mock-and-swap pattern (recap)

`holdings_store.py` is deliberately two-headed:
- The mock JSON path is trivially simple and offline.
- The Supabase path is production-shaped (a real DB with SQL, roles, and RLS).

The tools call the same three functions either way. If you deploy this to real
users, the ONLY change is `.env`. That "one seam, one swap" is the same
architectural pattern you saw with FactIQ in Modules 2/3.

### How this evolves in Module 5
Module 5 layers **planning and reflection** on top of what you have now. The
agent will draft a plan BEFORE acting (e.g., "1. get holdings, 2. get market
data for each, 3. summarize") and CRITIQUE its own answer before returning it.
Same tools, same memory - just a smarter loop around them.
