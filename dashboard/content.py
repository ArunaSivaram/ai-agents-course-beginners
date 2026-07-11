"""All dashboard content lives here as plain Python data.

Each chapter has:
  id, title, theory (markdown), diagram (markdown/ascii), code_snippet (python),
  todo (markdown), questions (list of dicts with q, options, correct, explain).

Module 4 also has a `setup` block for the Supabase step-by-step, shown before
the chapter body.
"""

CHAPTERS = [
    # =====================================================================
    # CHAPTER 1: Structured Output
    # =====================================================================
    {
        "id": "m1",
        "title": "Module 1 - Structured Output",
        "one_liner": "Getting a Python dict out of an LLM, reliably.",
        "badge": "📋",
        "tldr": "LLMs are chatty by default. A strict prompt turns them into a form-filler.",
        "key_terms": [
            ("LLM", "Large Language Model. Anthropic's Claude is one."),
            ("JSON", "A text format for structured data. Always the same shape."),
            ("Prompt", "The instructions you send the model with your question."),
            ("temperature=0", "A setting that makes the model pick its top guess every time - same input, same output. Great for testing."),
            ("Few-shot", "Giving the model 2-3 example inputs+outputs in the prompt to teach it a pattern."),
        ],
        "theory": """
LLMs are chatty by default. Ask one to extract three fields from a customer
message and it might give you a friendly paragraph, a bulleted list, a
`json`-fenced code block, or the JSON you actually wanted - all depending on
its mood.

**The lesson of Module 1:** you don't fix this with defensive parsing code.
You fix it with a strict prompt.

Four things a good extraction prompt does:
1. **Names the exact keys** allowed (`issue_type`, `product`, `urgency`).
2. **Constrains the values** (e.g. `urgency` must be one of `low`, `med`, `high`).
3. **Says what "unknown" means** (`product` -> `null` if not in text).
4. **Forbids prose and fences** ("Respond with a single JSON object and
   nothing else").

Add `temperature=0` and you get reproducible output - same input, same JSON
every time. That reproducibility is what lets you actually *test* your prompt.

**Analogy:** it's like giving a support agent a strict form to fill out. If
you hand them a blank sheet and say "capture the customer's issue", you get
five different formats. Give them a form with named fields and dropdowns,
and you get the same shape every time.

Prompt discipline replaces defensive code. Whenever you find yourself
wanting to add `try/except`, `str.strip("```")`, or fuzzy matching on the
model's output, go back and tighten the prompt first. That prompt-hardening
IS the exercise.
""",
        "diagram": """
```
Bad prompt:                        Good prompt:
"summarize this"                   "Respond with a single JSON object.
     |                              Keys: issue_type, product, urgency.
     v                              urgency must be one of: low, med, high.
Model output varies:                No prose, no markdown fences."
- prose                                    |
- markdown table                           v
- json fenced                       Every response:
- json bare                         {"issue_type": "...", ...}
- json with typos                   (parseable, reproducible)
```
""",
        "code_snippet": """def extract(client, text: str) -> dict:
    prompt = (
        "Extract the fields as JSON. Allowed keys: issue_type, product, urgency. "
        "urgency must be exactly one of: low, med, high. "
        "If product is unknown, use null. "
        "Respond with a single JSON object and nothing else - "
        "no prose, no markdown fences.\\n\\n"
        f"Input: {text}"
    )
    resp = client.messages.create(
        model=MODEL, max_tokens=300, temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(resp.content[0].text)""",
        "todo": """
1. Open `module-01-structured-output/exercise.py` and fill in the two TODOs
   (the prompt string, and `json.loads` at the end).
2. Run it: `python module-01-structured-output/exercise.py`
3. All five samples should print as parsed dicts. If any fail, TIGHTEN
   the prompt - don't add try/except.
4. **Bonus:** add a "med"-worthy sample of your own. Does the model use "med",
   or does it hedge toward "low"/"high"? Try adding a few-shot example.
""",
        "questions": [
            {
                "q": "Why does the exercise use `temperature=0`?",
                "options": [
                    "It makes the model faster.",
                    "It picks the highest-probability token each time so outputs are reproducible.",
                    "It disables tool use.",
                    "It reduces cost.",
                ],
                "correct": 1,
                "explain": "`temperature=0` gives deterministic output: same input, same JSON every time. That's what lets you A/B test prompt changes.",
            },
            {
                "q": "The prompt says urgency must be low/med/high. The model produces `{\"urgency\": \"critical\"}`. Best fix?",
                "options": [
                    "Add `if urgency == 'critical': urgency = 'high'` in Python.",
                    "Wrap `json.loads` in try/except and retry.",
                    "Tighten the prompt: repeat the allowed values and forbid others.",
                    "Increase max_tokens.",
                ],
                "correct": 2,
                "explain": "Defensive parsing masks the real problem. The prompt is what's teaching the model what's allowed. Fix it there.",
            },
            {
                "q": "What does `resp.content[0].text` extract?",
                "options": [
                    "The full raw HTTP response body.",
                    "The text of the FIRST content block in the response (there can be many).",
                    "The system prompt.",
                    "The model name.",
                ],
                "correct": 1,
                "explain": "Anthropic responses always contain a *list* of blocks. For a plain text reply there's one text block at index 0. Later modules will see multiple blocks.",
            },
            {
                "q": "In the few-shot experiment we ran, adding 3 'med'-labeled examples caused 1 of 5 test samples to flip from low to med. Why so few?",
                "options": [
                    "The model ignores few-shot examples.",
                    "The examples all had a concrete deadline, so the model learned 'med = has a deadline' rather than 'med = ongoing friction'.",
                    "temperature=0 disables few-shot learning.",
                    "The model only reads the first example.",
                ],
                "correct": 1,
                "explain": "The model generalizes from the *shape* of the examples, not the label you assigned. If every 'med' example has feature X, X becomes the definition of med.",
            },
        ],
    },
    # =====================================================================
    # CHAPTER 2: Tool Use
    # =====================================================================
    {
        "id": "m2",
        "title": "Module 2 - Tool Use",
        "one_liner": "The model asks; your Python answers; the model composes.",
        "badge": "🔧",
        "tldr": "The model can't run your code. It asks. You run. It writes the answer.",
        "key_terms": [
            ("Tool", "A Python function you describe to the model so it can ask you to run it."),
            ("stop_reason", "Tells you WHY the model stopped. `tool_use` = wants a tool. `end_turn` = done."),
            ("tool_use block", "The model's request for a tool, with `.name` and `.input`."),
            ("tool_result", "Your reply to the model with the tool's output."),
            ("Round trip", "One API call plus response. Module 2 uses 2 round trips per question."),
        ],
        "theory": """
The model can't run your code. It can only *ask* you to run it.

That's the whole trick of tool use. You describe a menu of tools; the model
decides one is needed; you execute the function; you feed the result back;
the model reads it and writes an English answer.

**The four-beat pattern - memorize it:**

1. **You describe tools** - a list of `{name, description, input_schema}`
   dicts passed as `tools=[...]` to `messages.create()`.
2. **Model replies with `stop_reason="tool_use"`** if it wants one. Inside
   `resp.content` there's a block with `type == "tool_use"` carrying
   `.id`, `.name`, and `.input`.
3. **You run it** - `result = your_function(**block.input)`.
4. **You send it back** - append the assistant's turn AS-IS, then append a
   new **user** turn containing a `tool_result` block referencing `block.id`.

**Analogy:** think of a phone call with a friend at the library. You ask
"can you look up X for me?" The friend says "sure, hold on" and puts the
phone down (that's the tool_use signal). You wait. They come back with the
answer. You take it and continue.

The library card is `tool_use_id` - it links "here's what I asked for" to
"here's the answer" so multiple tool calls don't get scrambled.

**Two agent shapes in Module 2:**
- `exercise.py` uses ONE simple tool (`get_stock_price`) with one round-trip.
- `portfolio_agent.py` uses ONE **composite** tool that internally loops over
  your holdings, sums values, and returns a summary. The model sees one
  tool; the composition happens in Python. Predictable, but rigid.

Module 3 flips this: expose the primitives and let the MODEL compose.
""",
        "diagram": """
```
Call #1:                        Call #2:
messages: [user: "how's AAPL?"] messages: [
tools:    [get_stock_price]        user: "how's AAPL?",
     |                              assistant: [tool_use{id:X,
     v                                              name: get_stock_price,
API returns:                                        input:{ticker:"AAPL"}}],
  stop_reason: "tool_use"           user: [tool_result{
  content: [tool_use{                 tool_use_id: X,
    id: X,                            content: "{'price': 223.50, ...}"
    name: get_stock_price,          }]
    input: {ticker:"AAPL"}       ]
  }]                                 |
     |                                v
     v                          API returns:
YOU run:                          stop_reason: "end_turn"
  get_stock_price("AAPL")         content: [text{"AAPL is up 1.6%..."}]
  = {price: 223.50, ...}
```
""",
        "code_snippet": """# The four beats in main():
resp = client.messages.create(
    model=MODEL, max_tokens=500, tools=TOOLS, messages=messages
)

if resp.stop_reason == "tool_use":
    block = next(b for b in resp.content if b.type == "tool_use")
    result = get_stock_price(**block.input)

    messages.append({"role": "assistant", "content": resp.content})
    messages.append({"role": "user", "content": [{
        "type": "tool_result",
        "tool_use_id": block.id,
        "content": str(result),
    }]})

    resp = client.messages.create(
        model=MODEL, max_tokens=500, tools=TOOLS, messages=messages
    )

print(next(b.text for b in resp.content if b.type == "text"))""",
        "todo": """
1. Open `module-02-tool-use/exercise.py` and fill in the four TODOs.
2. Run it: `python module-02-tool-use/exercise.py` - should print a summary
   naming AAPL, its price, and whether it's up or down.
3. Now open `module-02-tool-use/portfolio_agent.py` and run:
   `python module-02-tool-use/portfolio_agent.py`
4. Notice: the agent only sees ONE tool, but the tool internally hits
   3 tickers. Where is the "loop over holdings" logic? (Hint: Python.)
""",
        "questions": [
            {
                "q": "Why does the tool_result get sent back in a `role: \"user\"` turn?",
                "options": [
                    "Anthropic's API alternates user/assistant. The tool_result is your response, so it goes in a user turn.",
                    "Tools always run under the user role for security.",
                    "It's a legacy quirk from GPT.",
                    "There's no reason, `role: \"tool\"` also works.",
                ],
                "correct": 0,
                "explain": "Anthropic messages alternate user/assistant. You're the one supplying the tool result, so it wraps in a user turn.",
            },
            {
                "q": "The `tool_use_id` field on tool_result must match what?",
                "options": [
                    "The tool's schema name.",
                    "The `id` of the tool_use block from the assistant's previous turn.",
                    "A random UUID you generate.",
                    "The message id.",
                ],
                "correct": 1,
                "explain": "The id links your answer to the specific tool call the model made. With multiple parallel tool calls (Module 3), this is what keeps them straight.",
            },
            {
                "q": "In `portfolio_agent.py`, the agent asks for ONE tool but 3 tickers get looked up. Where does the loop over the 3 holdings live?",
                "options": [
                    "In the model's reasoning between tool calls.",
                    "Inside the Python function `get_portfolio_performance` - it loops over holdings and sums.",
                    "In the tool schema.",
                    "The 3 tickers are 3 separate tool calls the model makes in parallel.",
                ],
                "correct": 1,
                "explain": "M2's portfolio_agent uses a COMPOSITE tool. The loop is Python. The model sees one thing to call, and gets one composite result back.",
            },
            {
                "q": "What common bug will cause the model to keep asking for the same tool over and over?",
                "options": [
                    "Forgetting `temperature=0`.",
                    "Forgetting to append the assistant's tool_use turn before your tool_result turn.",
                    "Setting max_tokens too high.",
                    "Not calling `json.loads` on the result.",
                ],
                "correct": 1,
                "explain": "The API needs BOTH turns present. Skip the assistant turn and the model doesn't see its own request was acknowledged.",
            },
        ],
    },
    # =====================================================================
    # CHAPTER 3: ReAct
    # =====================================================================
    {
        "id": "m3",
        "title": "Module 3 - ReAct Agent",
        "one_liner": "The tool loop, wrapped in a for loop. That's the whole agent.",
        "badge": "🔄",
        "tldr": "An agent is just Module 2's tool call, wrapped in a while-loop. Nothing magical.",
        "key_terms": [
            ("Agent", "A loop that lets the model call tools repeatedly until it can answer."),
            ("ReAct", "Reason + Act. The model alternates thinking and taking actions."),
            ("Chained tool calls", "Multiple tools in sequence, where later calls depend on earlier results."),
            ("Parallel tool use", "The model asks for multiple independent tools in one turn - runs faster."),
            ("max_steps", "A safety cap so the loop doesn't run forever if the model gets stuck."),
        ],
        "theory": """
An "agent" sounds mysterious. It isn't. It's this:

```python
for step in range(max_steps):
    resp = client.messages.create(..., tools=TOOLS, messages=messages)
    if resp.stop_reason != "tool_use":
        return the_text_answer
    run_the_tools_and_append_results_to_messages
```

That's Module 3. Everything you'll ever see labeled "agent framework" is
this pattern with more ergonomic APIs on top.

**ReAct = Reason + Act.** The model interleaves reasoning and action:

```
Thought -> Action -> Observation -> Thought -> Action -> Observation -> ... -> Answer
```

- **Action** = a `tool_use` block the model emits.
- **Observation** = the `tool_result` you send back.
- **Answer** = `stop_reason == "end_turn"` with a text block.

**Analogy:** it's cooking without a recipe. Look in the fridge (Action:
get_holdings). See eggs and tomatoes (Observation). Decide to make a
scramble (Thought). Grab a pan (Action). Repeat until you're plating.

**The key difference vs Module 2's composite:**
- M2 portfolio_agent: ONE composite tool. The plan (loop over holdings)
  lives in your Python. Predictable but rigid.
- M3 portfolio_agent: TWO primitives (`get_holdings`, `get_market_data`).
  The MODEL decides the plan. Same tools handle "full portfolio",
  "just AAPL", "add TSLA and re-run" - no code changes.

The trade: you shift orchestration from Python (safe, rigid) to the
model (flexible, less predictable). The `max_steps` cap is your circuit
breaker if the model gets confused.

**Watch for parallel tool calls.** When the model recognises multiple
tool calls are independent (like fetching 3 stock prices), it can put
them all in ONE assistant turn as parallel `tool_use` blocks. You loop
over them and return all results in one `user` turn.
""",
        "diagram": """
```
User: "How's my portfolio?"

Step 0 (1 tool):
  Model -> Action: get_holdings()
  You   -> Observation: [{AAPL:10}, {MSFT:5}, {NVDA:8}]

Step 1 (3 tools, PARALLEL - all in one turn!):
  Model -> Actions: get_market_data("AAPL"),
                    get_market_data("MSFT"),
                    get_market_data("NVDA")
  You   -> Observations: 3 x {price, previous_close}

Step 2:
  stop_reason == "end_turn"
  Model -> Answer: "Your portfolio is $5,396 today, up 1.6%..."

Total round trips: 3
Round trips saved by parallelization: 2
```
""",
        "code_snippet": """def agent(question: str, max_steps: int = 8) -> str:
    client = get_client()
    messages = [{"role": "user", "content": question}]

    for step in range(max_steps):
        resp = client.messages.create(
            model=MODEL, max_tokens=1000, tools=TOOLS, messages=messages
        )
        if resp.stop_reason != "tool_use":
            return next(b.text for b in resp.content if b.type == "text")

        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
        messages.append({"role": "user", "content": tool_results})

    return "Hit max_steps without finishing."
""",
        "todo": """
1. Open `module-03-react-agent/exercise.py` and fill in the ReAct loop TODOs.
2. Run `python module-03-react-agent/portfolio_agent.py` and count the round
   trips. Should be 3.
3. In the second round trip, how many tool calls happen? Answer: 3, IN
   PARALLEL. The model recognised they're independent.
4. **Try:** change the question in the file to "Just show me AAPL today."
   Watch the model skip `get_holdings` and go straight to
   `get_market_data("AAPL")`. Same tools, different plan.
""",
        "questions": [
            {
                "q": "Why does the loop check `if resp.stop_reason != \"tool_use\"`?",
                "options": [
                    "To catch errors.",
                    "It's the model's signal that it's done reasoning and produced a final answer.",
                    "To count tokens.",
                    "It's optional - you can skip it.",
                ],
                "correct": 1,
                "explain": "`end_turn` (or `max_tokens`, etc.) means 'no more tools requested, return the text'. `tool_use` means 'keep looping'.",
            },
            {
                "q": "In M3's portfolio_agent trace, step 1 shows 3 tool calls in a single turn. What's this called?",
                "options": [
                    "Chained tool use.",
                    "Parallel tool use.",
                    "Nested tool use.",
                    "Batched tool use.",
                ],
                "correct": 1,
                "explain": "The model recognises 3 independent calls and emits all 3 tool_use blocks in one assistant turn. Saves round trips.",
            },
            {
                "q": "M3 exposes `get_holdings` and `get_market_data`. Where does the plan (fetch holdings first, then prices, then sum) live?",
                "options": [
                    "In Python code, hardcoded.",
                    "In the model, decided at runtime from the tool descriptions.",
                    "In the tool schema.",
                    "In a config file.",
                ],
                "correct": 1,
                "explain": "This is THE difference vs M2's composite tool. Same portfolio, but the plan is the model's, not yours.",
            },
            {
                "q": "What's `max_steps` in the ReAct loop for?",
                "options": [
                    "Limiting the token count.",
                    "A safety cap so a confused model doesn't loop forever.",
                    "The number of tools available.",
                    "Cache size.",
                ],
                "correct": 1,
                "explain": "If the model keeps asking for a tool that fails, or gets stuck, the loop needs a hard exit. Real agents always have this.",
            },
            {
                "q": "If you ask the M3 agent 'how many shares of MSFT do I own?', which tool(s) will it call?",
                "options": [
                    "get_holdings only.",
                    "get_market_data only.",
                    "Both, in that order.",
                    "Neither - it will hallucinate.",
                ],
                "correct": 0,
                "explain": "The model reads tool descriptions and picks the minimum needed. No market data needed for a share count. Same primitives, adapted plan.",
            },
        ],
    },
    # =====================================================================
    # CHAPTER 4: Memory (with Supabase setup)
    # =====================================================================
    {
        "id": "m4",
        "title": "Module 4 - Memory",
        "one_liner": "Two memories: one that lives a session, one that survives restart.",
        "badge": "🧠",
        "tldr": "Two kinds of memory: your desk (short-term) and your filing cabinet (long-term).",
        "key_terms": [
            ("Short-term memory", "The `messages` list. Remembers the current conversation. Dies when you quit."),
            ("Long-term memory", "Data written to disk or a database. Survives restarts."),
            ("REPL", "Read-Eval-Print Loop. A back-and-forth chat prompt in your terminal."),
            ("Supabase", "An open-source backend built on Postgres. We use it for long-term memory."),
            ("RLS", "Row-Level Security. A Postgres feature that filters rows by policy - can trip you up if you forget it."),
            ("Mock-and-swap", "Ship with a fake JSON backend; swap to real DB via env vars. Zero code change."),
        ],
        "setup": """
### Set up Supabase locally (5-10 minutes)

Module 4's long-term memory lives in a Supabase table. Here's how to spin
up a local Supabase and wire it in. Skip this section if you're happy to
use the JSON fallback - the code works either way.

**1. Install the Supabase CLI:**
```bash
brew install supabase/tap/supabase   # macOS
# or npm i -g supabase / see supabase.com/docs
```

**2. Start a local stack** (in ANY project directory - can be this repo):
```bash
supabase init      # creates a supabase/ folder with config
supabase start     # spins up docker containers
```

Wait ~1 minute. When it's done, run:
```bash
supabase status
```

Copy two values:
- **API URL** (typically `http://127.0.0.1:54321`)
- **publishable key** (starts with `sb_publishable_...` - or in older
  installs the `anon key` starting `eyJ...`)

**3. Create the `course_holdings` table.** Open Studio at
http://127.0.0.1:54323 -> SQL Editor -> New query -> paste + Run:

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

**4. Verify.** In a fresh terminal (from your Supabase project dir),
`supabase status` again to confirm it's still up. Then check the table
was created via Studio's Table Editor.

**5. Add credentials to your `.env`:**
```
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=sb_publishable_...
```

**Common gotchas we hit while building this module:**
- **`permission denied for table`** - `anon` role has no privileges. Run
  the `grant` statement again.
- **Client returns 0 rows when psql shows 3** - RLS is still enabled.
  Studio sometimes re-enables it. Run
  `alter table course_holdings disable row level security` again.

If you skip this entire section, the code detects no `SUPABASE_URL` and
falls back to `module-04-memory/holdings_store.json` automatically.
""",
        "theory": """
Agents need two kinds of memory. Don't conflate them.

**Short-term memory** = the `messages` list you keep appending to. It lives
inside one process, dies when the script exits. This is what lets the agent
answer "how are they doing?" after you just said "add TSLA" - it looks
back at earlier turns in the same conversation.

**Long-term memory** = data written OUTSIDE the model, read back later.
In this module: a `course_holdings` Supabase table (or a local JSON file).
This is what lets you close the script, come back tomorrow, and still
have your holdings there.

**Analogy:** short-term = your desk. Long-term = your filing cabinet.
Both are useful. The desk holds what you're actively working on; the
cabinet is where things go to survive across days.

**The mock-and-swap pattern (from `holdings_store.py`):**

The same three functions - `get_holdings`, `add_holding`, `remove_holding`
- work against either backend. If `SUPABASE_URL` is set, they talk to
Supabase. Otherwise they read/write a JSON file. The tools that call
them never know which one is live.

That's the pattern you saw with FactIQ in Modules 2 and 3: define the
shape of an integration once, ship a mock body, and swap to real by
changing one function.

**Why this matters:**
- Development: the mock lets you build and test with zero setup.
- Production: the real backend takes over via env vars, no code change.
- Testing: you can swap in a fake to control what the agent sees.

**The tools the model gains in Module 4:**
- `get_holdings()` - read long-term memory.
- `add_holding(ticker, shares)` - write to long-term memory.
- `remove_holding(ticker)` - delete from long-term memory.
- `get_market_data(ticker)` - the FactIQ mock, same as M3.

The agent is now a REPL: `while True: input() -> agent_turn() -> print`.
The `messages` list carries across iterations (short-term); the store
carries across restarts (long-term).
""",
        "diagram": """
```
   ┌──────────────────────┐
   │  Supabase / JSON     │  ← survives restart
   │  course_holdings     │     (LONG-TERM)
   └──────────▲───────────┘
              │ get/add/remove
              │
  REPL loop:  │
              │
  you ──▶ agent_turn ──┬── get_holdings, add_holding,
    ▲                  │   remove_holding, get_market_data
    │                  │
    └──── agent ───────┘
    (messages list persists across REPL turns
     until you quit = SHORT-TERM memory)
```
""",
        "code_snippet": """def repl() -> None:
    print(f"long-term memory backend: {holdings_store.backend_name()}")
    client = get_client()
    messages = []  # short-term: persists across REPL turns, dies on quit

    while True:
        user = input("you: ").strip()
        if user.lower() in {"quit", "exit"}:
            break
        messages.append({"role": "user", "content": user})
        answer = agent_turn(client, messages)   # ReAct loop from Module 3
        print(f"agent: {answer}\\n")""",
        "todo": """
1. If you set up Supabase above, put your credentials in `.env`. Otherwise,
   skip - the mock JSON backend works too.
2. Fill in the TODOs in `module-04-memory/exercise.py` (declare tools,
   wire up REPL).
3. **The restart proof:**
   - Run `python module-04-memory/portfolio_agent.py`
   - Say "add TSLA to my portfolio, 3 shares"
   - Type `quit`
   - Run it AGAIN. Ask "what do I own?" - TSLA should be there.
4. That crossing-the-restart moment is the whole point of long-term memory.
""",
        "questions": [
            {
                "q": "In the REPL loop, why does `messages = []` sit OUTSIDE the `while True:` loop?",
                "options": [
                    "Style choice.",
                    "So the list persists across iterations - that's what short-term memory IS.",
                    "It doesn't matter where it sits.",
                    "For performance.",
                ],
                "correct": 1,
                "explain": "If you reset messages inside the loop, the agent would forget everything after each user turn. Persistence across iterations IS short-term memory.",
            },
            {
                "q": "You quit the script. Which memory survives?",
                "options": [
                    "Short-term only.",
                    "Long-term only (Supabase table or JSON file).",
                    "Both.",
                    "Neither.",
                ],
                "correct": 1,
                "explain": "Short-term lives in the Python process and dies with it. Long-term is written to disk (or a DB), so it survives.",
            },
            {
                "q": "The mock-and-swap pattern in `holdings_store.py` picks a backend based on:",
                "options": [
                    "A command-line flag.",
                    "Whether SUPABASE_URL and SUPABASE_KEY are set in .env.",
                    "The current time.",
                    "A prompt to the model.",
                ],
                "correct": 1,
                "explain": "Env-var detection makes it seamless: set the vars to go live, unset to fall back to mock. No code changes.",
            },
            {
                "q": "We hit a bug: `SELECT` in psql showed 3 rows, but `supabase-py` returned 0. What was wrong?",
                "options": [
                    "The publishable key was invalid.",
                    "RLS was still enabled and no policies allowed the anon role.",
                    "The table was in the wrong schema.",
                    "supabase-py was outdated.",
                ],
                "correct": 1,
                "explain": "RLS + no policies = default deny for anon. `alter table ... disable row level security` fixed it.",
            },
            {
                "q": "Why is `add_holding` exposed as a tool (not just called from Python)?",
                "options": [
                    "So the model can update memory in response to the user (\"add TSLA, 3 shares\").",
                    "For performance.",
                    "Anthropic requires all functions to be tools.",
                    "It doesn't matter - it could be either.",
                ],
                "correct": 0,
                "explain": "If it's a tool, the model can invoke it when the user asks. If it's just Python, only your code can call it.",
            },
        ],
    },
    # =====================================================================
    # CHAPTER 5: Plan/Execute/Reflect
    # =====================================================================
    {
        "id": "m5",
        "title": "Module 5 - Plan / Execute / Reflect",
        "one_liner": "Three passes for the price of one, in exchange for better output.",
        "badge": "🎯",
        "tldr": "Outline. Draft. Revise. The essay-writing loop, applied to agents.",
        "key_terms": [
            ("PLAN pass", "The model writes down its intended steps BEFORE doing them. Text-only, cheap."),
            ("EXECUTE pass", "The ReAct loop from Module 4 runs, guided by the plan. Produces a first draft."),
            ("REFLECT pass", "The model reads its own draft, lists problems, and rewrites."),
            ("Reflection", "The general practice of having the model critique its own output."),
            ("Least privilege", "Give the agent only the tools needed for the current task. A review agent shouldn't be able to delete stuff."),
        ],
        "theory": """
A one-shot agent answer to a multi-part task ("summarize performance,
identify winners, recommend one action, under 150 words") often misses
constraints - too long, too vague, gives two recommendations.

Module 5's fix: don't ask once. Ask three times, in different modes.

**PASS 1 - PLAN.** Ask the model to WRITE DOWN a numbered plan before
touching tools. Text-only, no tools needed. Cheap. Catches "what am I
actually solving?" mistakes early.

**PASS 2 - EXECUTE.** Run the ReAct loop from Module 4, but feed the plan
as context in the first user message. The model follows its own plan
while gathering data via tools. Produces a first draft.

**PASS 3 - REFLECT.** Feed the draft back and ask "critique this for
accuracy, actionability, and concision. Then output an improved version."
Same generator, adversarial hat on. This is where padding, missed
constraints, and weak recommendations get caught.

**Analogy:** it's the essay-writing workflow. Outline (plan). First draft
(execute). Revise (reflect). Almost no writer skips step 3 for anything
that matters.

**Cost trade-off.** M3 was ~3 API calls per question. M5 is ~5-7. You buy
tighter output for extra latency and cost. Rules of thumb:
- **Skip reflect** for casual/exploratory queries.
- **Use it** when the output has explicit constraints (word budget,
  format, single actionable item).

**A gotcha we found live.** In the run we did, REFLECT accused the draft
of "fabricating data" because it only sees the draft text, NOT the tool
call results. The reflector had no evidence and defaulted to skepticism.
The fix in a real system: include the raw tool results in the reflect
prompt so it can verify. Or run BOTH draft and improved through a scorer
(Module 8) and let empirics pick the winner.

**Read-only tools for review tasks.** M5's portfolio_agent uses only
`get_holdings` and `get_market_data` - not `add_holding` or
`remove_holding`. A REVIEW task shouldn't silently mutate your portfolio.
Least privilege applies to agents too.
""",
        "diagram": """
```
   task ──▶  PASS 1 - PLAN  ──▶  (numbered plan, text-only, no tools)
                                              │
                                              ▼
             PASS 2 - EXECUTE  ──▶  (ReAct loop with tools)
             (Module 4's loop,                 │
              plan as context)                 ▼
                                          first draft
                                              │
                                              ▼
             PASS 3 - REFLECT  ──▶  (critique + improved version)
             (text-only, sees             │
              draft only)                  ▼
                                        final answer

  Total API calls: 5-7  (vs 3-4 for M4 alone)
```
""",
        "code_snippet": """def main() -> None:
    client = get_client()

    the_plan = plan(client, TASK, [t["name"] for t in TOOLS])
    print(the_plan)

    draft = execute(client, TASK, the_plan)   # ReAct loop with plan as context
    print(draft)

    improved = reflect(client, TASK, draft)   # critique + rewrite
    print(improved)

# plan/reflect are single text calls (no tools)
# execute uses the Module 4 ReAct loop""",
        "todo": """
1. Fill in the three TODOs in `module-05-planning-reflection/exercise.py`
   (plan, execute, reflect).
2. Run `python module-05-planning-reflection/portfolio_agent.py` and compare:
   - The DRAFT (from EXECUTE)
   - The IMPROVED VERSION (from REFLECT)
3. Which is closer to the ~150 word budget? Which has ONE recommendation
   vs multiple? Which reads tighter?
4. **Try:** change the REFLECT prompt to ask for critique "as if you were
   a skeptical portfolio manager". Watch the recommendation get more
   specific and better-justified.
""",
        "questions": [
            {
                "q": "Why write the plan down BEFORE executing, instead of just asking the ReAct loop directly?",
                "options": [
                    "The API requires it.",
                    "Making the plan explicit catches misunderstandings of the task before you spend tool calls.",
                    "It's faster.",
                    "It's cheaper.",
                ],
                "correct": 1,
                "explain": "If the plan is wrong, you catch it in a cheap text-only pass. Better than paying for a bad ReAct trace.",
            },
            {
                "q": "In our run, REFLECT wrongly accused the DRAFT of fabricating numbers. Why?",
                "options": [
                    "The model was buggy.",
                    "REFLECT sees the draft text but NOT the tool call results, so it had no way to verify the numbers.",
                    "temperature was too high.",
                    "The tools returned bad data.",
                ],
                "correct": 1,
                "explain": "REFLECT operates on the draft alone. Real fix: pass the tool results into the reflect prompt too, or score both drafts empirically.",
            },
            {
                "q": "M5's portfolio_agent exposes only `get_holdings` and `get_market_data` - not `add_holding`. Why?",
                "options": [
                    "Missing feature - it should have been included.",
                    "A REVIEW task shouldn't silently mutate the portfolio. Least privilege for agents.",
                    "Performance.",
                    "The model would refuse otherwise.",
                ],
                "correct": 1,
                "explain": "Narrow the tool set to the current job. A review agent that can accidentally sell your stocks is a bug.",
            },
            {
                "q": "Cost comparison (roughly): M3 vs M5 per question?",
                "options": [
                    "M5 is cheaper.",
                    "Same.",
                    "M5 is ~2x more expensive (5-7 calls vs 3-4).",
                    "M5 is 10x more expensive.",
                ],
                "correct": 2,
                "explain": "The extra plan and reflect passes roughly double the API calls. You use M5 when the quality gain justifies it.",
            },
        ],
    },
]
