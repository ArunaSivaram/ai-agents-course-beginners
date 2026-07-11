"""AI Agents Course - interactive gamified dashboard.

Run:  streamlit run dashboard/streamlit_app.py

Structure:
  Top header:    Level badge + XP + trophy row (badges you've earned)
  Sidebar:       chapter navigation, reset button
  Main:          TL;DR banner -> Key Terms cards -> theory -> diagram
                 -> code -> TODO exercise -> quiz
  Progress:      dashboard/progress.json (gitignored). Reset button wipes.
"""
import json
from pathlib import Path

import streamlit as st

from content import CHAPTERS

XP_PER_QUESTION = 10
TOTAL_QUESTIONS = sum(len(c["questions"]) for c in CHAPTERS)
MAX_XP = TOTAL_QUESTIONS * XP_PER_QUESTION

# Level tiers: [threshold, icon, name]
LEVELS = [
    (0,   "🥉", "Novice"),
    (50,  "🥈", "Apprentice"),
    (120, "🥇", "Journeyman"),
    (180, "👑", "Master"),
]

PROGRESS_PATH = Path(__file__).resolve().parent / "progress.json"


# --- Config ------------------------------------------------------------------
st.set_page_config(
    page_title="AI Agents Course",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Progress persistence ----------------------------------------------------
def load_progress() -> dict:
    if PROGRESS_PATH.exists():
        try:
            return json.loads(PROGRESS_PATH.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_progress(progress: dict) -> None:
    PROGRESS_PATH.write_text(json.dumps(progress, indent=2))


def correct_count(progress: dict) -> int:
    return sum(len(v) for v in progress.values())


def xp(progress: dict) -> int:
    return correct_count(progress) * XP_PER_QUESTION


def level_for(xp_val: int) -> tuple:
    """Return the highest tier whose threshold <= xp_val."""
    current = LEVELS[0]
    for tier in LEVELS:
        if xp_val >= tier[0]:
            current = tier
    return current


def next_level(xp_val: int) -> tuple | None:
    for tier in LEVELS:
        if xp_val < tier[0]:
            return tier
    return None


def is_chapter_complete(chapter: dict, progress: dict) -> bool:
    got = set(progress.get(chapter["id"], []))
    return set(range(len(chapter["questions"]))).issubset(got)


def first_incomplete(progress: dict) -> int:
    for i, ch in enumerate(CHAPTERS):
        if not is_chapter_complete(ch, progress):
            return i
    return len(CHAPTERS) - 1


# --- Session state -----------------------------------------------------------
if "progress" not in st.session_state:
    st.session_state.progress = load_progress()
if "current_chapter" not in st.session_state:
    st.session_state.current_chapter = first_incomplete(st.session_state.progress)
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = {}
if "just_completed" not in st.session_state:
    st.session_state.just_completed = set()  # chapter ids we've celebrated


# --- Sidebar -----------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧠 AI Agents Course")
    st.caption("Learn agent-building the calm way. Points, badges, no rush.")

    st.markdown("---")
    st.markdown("**Chapters**")
    start_here = first_incomplete(st.session_state.progress)
    for i, ch in enumerate(CHAPTERS):
        done = is_chapter_complete(ch, st.session_state.progress)
        icon = "✅" if done else ("👉" if i == start_here else "⬜")
        label = f"{icon} {ch['title']}"
        if st.button(label, key=f"nav_{ch['id']}", use_container_width=True):
            st.session_state.current_chapter = i
            st.rerun()

    st.markdown("---")
    if st.button("🔄 Reset progress", use_container_width=True):
        st.session_state.progress = {}
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = {}
        st.session_state.just_completed = set()
        save_progress({})
        st.rerun()

    st.markdown("---")
    st.caption(
        "Content lives in `dashboard/content.py`. "
        "Progress persists in `dashboard/progress.json`."
    )


# --- Top header: Level + XP + badge trophy row -------------------------------
xp_val = xp(st.session_state.progress)
current_icon, current_name = level_for(xp_val)[1], level_for(xp_val)[2]
nxt = next_level(xp_val)

header_left, header_right = st.columns([2, 3])

with header_left:
    st.markdown(
        f"""
        <div style='padding: 12px 16px; background: #1e293b; border-radius: 12px; color:white;'>
            <div style='font-size: 14px; opacity: 0.7;'>YOUR LEVEL</div>
            <div style='font-size: 28px; margin-top: 4px;'>{current_icon} {current_name}</div>
            <div style='font-size: 13px; opacity: 0.8; margin-top: 4px;'>
                {xp_val} XP / {MAX_XP} XP
                {f"— {nxt[0] - xp_val} XP to <b>{nxt[1]} {nxt[2]}</b>" if nxt else "— max level reached!"}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    badges_html = "<div style='padding: 12px 16px; background: #f1f5f9; border-radius: 12px;'>"
    badges_html += "<div style='font-size: 14px; color:#64748b;'>BADGES EARNED</div>"
    badges_html += "<div style='display: flex; gap: 12px; margin-top: 6px; font-size: 32px;'>"
    for ch in CHAPTERS:
        earned = is_chapter_complete(ch, st.session_state.progress)
        badge_emoji = ch.get("badge", "🏅")
        opacity = "1.0" if earned else "0.15"
        title = f"{ch['title']} {'(earned)' if earned else '(locked)'}"
        badges_html += (
            f"<span title='{title}' style='opacity: {opacity};'>{badge_emoji}</span>"
        )
    badges_html += "</div></div>"
    st.markdown(badges_html, unsafe_allow_html=True)

# Overall progress bar under the header
got = correct_count(st.session_state.progress)
pct = got / TOTAL_QUESTIONS if TOTAL_QUESTIONS else 0
st.progress(pct, text=f"Overall: {got} / {TOTAL_QUESTIONS} questions correct ({int(pct * 100)}%)")
st.markdown("")


# --- Main area: chapter body -------------------------------------------------
chapter = CHAPTERS[st.session_state.current_chapter]
ch_id = chapter["id"]

st.title(f"{chapter.get('badge', '🏅')}  {chapter['title']}")
st.caption(chapter["one_liner"])

# TL;DR banner
if "tldr" in chapter:
    st.info(f"**TL;DR** — {chapter['tldr']}")

# Chapter progress line
n_qs = len(chapter["questions"])
got_here = len(st.session_state.progress.get(ch_id, []))
if is_chapter_complete(chapter, st.session_state.progress):
    st.success(
        f"✅ Chapter complete! You earned the {chapter.get('badge', '🏅')} badge "
        f"and +{n_qs * XP_PER_QUESTION} XP."
    )
else:
    remaining = n_qs - got_here
    st.warning(
        f"Chapter progress: **{got_here}/{n_qs}** correct — {remaining} more "
        f"question{'s' if remaining != 1 else ''} to earn the "
        f"{chapter.get('badge', '🏅')} badge."
    )

# Key Terms cards
if "key_terms" in chapter:
    st.markdown("## 📌 Key Terms")
    st.caption("Skim these first if any word feels unfamiliar.")
    key_terms = chapter["key_terms"]
    # 2 columns for cleaner layout
    for row_start in range(0, len(key_terms), 2):
        cols = st.columns(2)
        for offset, col in enumerate(cols):
            idx = row_start + offset
            if idx >= len(key_terms):
                continue
            term, defn = key_terms[idx]
            with col:
                st.markdown(
                    f"""
                    <div style='padding: 12px 16px; background: #f8fafc; border-left: 4px solid #3b82f6; border-radius: 8px; margin-bottom: 8px;'>
                        <div style='font-weight: 700; color: #0f172a; font-size: 15px;'>{term}</div>
                        <div style='color: #475569; font-size: 14px; margin-top: 4px;'>{defn}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# Setup (Module 4)
if "setup" in chapter:
    with st.expander("📦 Setup instructions (only needed for the Supabase path)", expanded=False):
        st.markdown(chapter["setup"])

# Theory
st.markdown("## 📖 Concept")
st.markdown(chapter["theory"])

# Diagram
st.markdown("## 🗺 Visual")
st.markdown(chapter["diagram"])

# Code
st.markdown("## 💻 Code snippet")
st.code(chapter["code_snippet"], language="python")

# TODO
st.markdown("## 🛠 Try it yourself")
st.markdown(chapter["todo"])

# Quiz
st.markdown(f"## 📝 Quiz ({n_qs} questions - {n_qs * XP_PER_QUESTION} XP)")

correct_indices = st.session_state.progress.get(ch_id, [])
submitted = st.session_state.quiz_submitted.get(ch_id, False)
answers = st.session_state.quiz_answers.setdefault(ch_id, {})

with st.form(key=f"quiz_{ch_id}"):
    for q_idx, q in enumerate(chapter["questions"]):
        already_correct = q_idx in correct_indices
        prefix = "✅ " if already_correct else f"Q{q_idx + 1}. "
        st.markdown(f"**{prefix}{q['q']}**")

        options_with_labels = [f"{chr(65 + i)}. {opt}" for i, opt in enumerate(q["options"])]
        default_idx = answers.get(str(q_idx), None)

        selected = st.radio(
            label=f"Choose one (Q{q_idx + 1})",
            options=list(range(len(q["options"]))),
            format_func=lambda i, opts=options_with_labels: opts[i],
            index=default_idx if default_idx is not None else None,
            key=f"radio_{ch_id}_{q_idx}",
            label_visibility="collapsed",
        )
        answers[str(q_idx)] = selected

        if submitted and selected is not None:
            if selected == q["correct"]:
                st.success(f"✔ Correct (+{XP_PER_QUESTION} XP). {q['explain']}")
            else:
                right_letter = chr(65 + q["correct"])
                st.error(
                    f"✗ Not quite. Correct answer: **{right_letter}. "
                    f"{q['options'][q['correct']]}**\n\n{q['explain']}"
                )
        st.markdown("")

    submit_pressed = st.form_submit_button(
        "Submit answers", type="primary", use_container_width=True
    )

if submit_pressed:
    st.session_state.quiz_submitted[ch_id] = True
    new_correct = []
    for q_idx, q in enumerate(chapter["questions"]):
        picked = st.session_state.quiz_answers[ch_id].get(str(q_idx))
        if picked is not None and picked == q["correct"]:
            new_correct.append(q_idx)
    existing = set(st.session_state.progress.get(ch_id, []))
    st.session_state.progress[ch_id] = sorted(existing.union(new_correct))
    save_progress(st.session_state.progress)

    # Celebrate first-time chapter completion
    if is_chapter_complete(chapter, st.session_state.progress) and ch_id not in st.session_state.just_completed:
        st.session_state.just_completed.add(ch_id)
        st.balloons()

    st.rerun()

# Navigation footer
st.markdown("---")
cols = st.columns([1, 2, 1])
with cols[0]:
    if st.session_state.current_chapter > 0:
        if st.button("← Previous chapter"):
            st.session_state.current_chapter -= 1
            st.rerun()
with cols[2]:
    if st.session_state.current_chapter < len(CHAPTERS) - 1:
        if st.button("Next chapter →"):
            st.session_state.current_chapter += 1
            st.rerun()
