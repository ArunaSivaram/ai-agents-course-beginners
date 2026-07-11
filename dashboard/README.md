# Course dashboard

An interactive tutorial that reflects the modules committed on `main`.
Chapter-by-chapter: concept + diagram + code + a TODO exercise + a quiz.
Progress persists between sessions in `progress.json` (gitignored).

## Run it

From the repo root:

```bash
.venv/bin/streamlit run dashboard/streamlit_app.py
```

Streamlit opens a browser tab at http://localhost:8501.

## Editing content

All chapter content is data, not code. Edit `dashboard/content.py` to
add, remove, or reword chapters and quiz questions. The Streamlit app
picks up changes on save (hit `r` to rerun in the browser).

Each chapter is a dict with these keys:

- `id` - short slug, used in progress.json
- `title` - shown in the sidebar and header
- `one_liner` - shown below the title
- `theory` - markdown, the concept explanation
- `diagram` - markdown, usually a fenced code block with ASCII art
- `code_snippet` - Python string, syntax-highlighted
- `todo` - markdown, hands-on exercise instructions
- `questions` - list of `{q, options, correct, explain}` dicts
- `setup` (optional) - markdown, shown in an expandable box before the theory

## Resetting progress

Click the "Reset progress" button in the sidebar, or delete
`dashboard/progress.json` and refresh the page.
