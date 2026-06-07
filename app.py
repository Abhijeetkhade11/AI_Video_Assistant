import warnings
import logging
warnings.filterwarnings("ignore", message=".*Accessing `__path__`.*")
logging.getLogger("transformers").setLevel(logging.ERROR)

import streamlit as st
import time
import shutil
from pathlib import Path
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
 
load_dotenv()
 
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
 
# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lens — Meeting Intelligence",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&family=DM+Mono:wght@300;400;500&display=swap');
 
:root {
    --cream:    #f5f0e8;
    --paper:    #faf7f2;
    --sand:     #e8dfc8;
    --ink:      #1a1510;
    --ink-2:    #3d3528;
    --ink-3:    #6b5f4a;
    --amber:    #d4820a;
    --amber-lt: #f0a832;
    --rust:     #b84a1e;
    --teal:     #1a6b5e;
    --teal-lt:  #2d9e8c;
    --rule:     #c8bfa8;
}
 
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--paper) !important;
    color: var(--ink) !important;
}
.stApp { background: var(--paper) !important; }
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none; z-index: 0; opacity: 0.4;
}
 
/* ── Sidebar ── */
[data-testid="stSidebar"] { background: var(--ink) !important; border-right: none !important; }
[data-testid="stSidebar"] * { color: var(--cream) !important; }
[data-testid="stSidebar"] label { color: var(--sand) !important; font-size: 0.7rem !important; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: rgba(255,255,255,0.07) !important; border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 4px !important; color: var(--cream) !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input:focus {
    border-color: var(--amber-lt) !important; box-shadow: 0 0 0 2px rgba(212,130,10,0.2) !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.07) !important; border: 1px solid rgba(255,255,255,0.15) !important;
    color: var(--cream) !important; border-radius: 4px !important;
}
[data-testid="stSidebar"] .stRadio label { font-size: 0.8rem !important; color: var(--cream) !important; text-transform: none !important; letter-spacing: 0 !important; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.04) !important; border: 1px dashed rgba(255,255,255,0.18) !important; border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] * { color: var(--cream) !important; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: rgba(212,130,10,0.25) !important; border: 1px solid rgba(212,130,10,0.5) !important; color: var(--amber-lt) !important;
}
 
.sb-brand { padding: 0.25rem 0 1.5rem 0; }
.sb-logo { font-family: 'Playfair Display', serif; font-size: 2.2rem; font-weight: 900; color: var(--cream); line-height: 1; letter-spacing: -0.02em; }
.sb-logo span { color: var(--amber-lt); }
.sb-tagline { font-size: 0.62rem; letter-spacing: 0.25em; text-transform: uppercase; color: rgba(245,240,232,0.4); margin-top: 0.3rem; }
.sb-rule { border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 1.1rem 0; }
.sb-section-hd { font-family: 'DM Mono', monospace; font-size: 0.58rem; letter-spacing: 0.22em; text-transform: uppercase; color: rgba(245,240,232,0.38); margin-bottom: 0.6rem; }
 
.sb-step { display: flex; align-items: center; gap: 0.6rem; padding: 0.38rem 0; font-size: 0.77rem; color: rgba(245,240,232,0.4); }
.sb-step.done   { color: rgba(245,240,232,0.85); }
.sb-step.active { color: var(--amber-lt); }
.sb-step-num { width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.58rem; font-weight: 700; flex-shrink: 0; font-family: 'DM Mono', monospace; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: rgba(245,240,232,0.3); }
.sb-step-num.done   { background: rgba(26,107,94,0.3); border-color: var(--teal-lt); color: var(--teal-lt); }
.sb-step-num.active { background: rgba(212,130,10,0.2); border-color: var(--amber-lt); color: var(--amber-lt); animation: blink 1.4s ease-in-out infinite; }
 
/* ── Step card (one per step, in main area) ── */
.step-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1.1rem;
    border-radius: 8px;
    border: 1.5px solid var(--sand);
    background: var(--cream);
    margin-bottom: 0.55rem;
    transition: border-color 0.25s, background 0.25s;
    position: relative;
    overflow: hidden;
}
.step-card.active {
    border-color: var(--amber);
    background: #fffaf0;
}
.step-card.done {
    border-color: rgba(26,107,94,0.35);
    background: #f2faf7;
}
.step-card.error {
    border-color: var(--rust);
    background: #fff5f2;
}
 
/* left shimmer bar for active state */
.step-card.active::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, var(--amber-lt), var(--amber));
    animation: shimmer-bar 1.5s ease-in-out infinite alternate;
}
.step-card.done::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: var(--teal-lt);
}
@keyframes shimmer-bar { 0%{opacity:0.5} 100%{opacity:1} }
 
/* badge circle */
.step-badge {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'DM Mono', monospace; font-size: 0.7rem; font-weight: 700;
    flex-shrink: 0;
    transition: all 0.3s;
}
.step-badge.pending { background: var(--sand); color: var(--ink-3); border: 1.5px solid var(--rule); }
.step-badge.active  { background: rgba(212,130,10,0.15); color: var(--amber); border: 1.5px solid var(--amber); animation: badge-pulse 1.4s ease-in-out infinite; }
.step-badge.done    { background: rgba(26,107,94,0.15); color: var(--teal); border: 1.5px solid var(--teal-lt); }
.step-badge.error   { background: rgba(184,74,30,0.15); color: var(--rust); border: 1.5px solid var(--rust); }
@keyframes badge-pulse { 0%,100%{box-shadow:0 0 0 0 rgba(212,130,10,0.4)} 50%{box-shadow:0 0 0 6px rgba(212,130,10,0)} }
 
.step-info { flex: 1; min-width: 0; }
.step-name { font-size: 0.88rem; font-weight: 500; color: var(--ink); line-height: 1.2; }
.step-name.pending { color: var(--ink-3); font-weight: 400; }
.step-name.active  { color: var(--ink);   font-weight: 600; }
.step-name.done    { color: var(--ink-2); }
.step-desc { font-size: 0.72rem; color: var(--ink-3); margin-top: 0.15rem; font-family: 'DM Mono', monospace; }
.step-desc.active { color: var(--amber); }
.step-desc.done   { color: var(--teal); }
 
.step-pill {
    font-family: 'DM Mono', monospace; font-size: 0.6rem; letter-spacing: 0.1em;
    text-transform: uppercase; padding: 0.22rem 0.6rem; border-radius: 3px; white-space: nowrap;
}
.step-pill.pending { background: var(--sand); color: var(--ink-3); }
.step-pill.active  { background: rgba(212,130,10,0.15); color: var(--amber); border: 1px solid rgba(212,130,10,0.35); }
.step-pill.done    { background: rgba(26,107,94,0.12); color: var(--teal); border: 1px solid rgba(26,107,94,0.3); }
.step-pill.error   { background: rgba(184,74,30,0.12); color: var(--rust); border: 1px solid rgba(184,74,30,0.3); }
 
/* progress track above cards */
.pipeline-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1rem;
}
.pipeline-title {
    font-family: 'Playfair Display', serif; font-size: 1.1rem; font-weight: 700; color: var(--ink);
    display: flex; align-items: center; gap: 0.5rem;
}
.progress-dots { display: flex; gap: 0.35rem; align-items: center; }
.pdot { width: 8px; height: 8px; border-radius: 50%; background: var(--sand); transition: background 0.3s; }
.pdot.done   { background: var(--teal-lt); }
.pdot.active { background: var(--amber); animation: blink 1.2s ease-in-out infinite; }
 
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.25} }
 
/* ── Buttons ── */
.stButton > button {
    background: var(--amber) !important; color: white !important; border: none !important;
    border-radius: 4px !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 0.82rem !important; letter-spacing: 0.06em !important;
    text-transform: uppercase !important; padding: 0.55rem 1.25rem !important;
    transition: background 0.2s, transform 0.15s !important;
}
.stButton > button:hover { background: var(--amber-lt) !important; transform: translateY(-1px) !important; }
.stButton > button[kind="secondary"] { background: transparent !important; border: 1px solid var(--rule) !important; color: var(--ink-3) !important; }
.stButton > button[kind="secondary"]:hover { border-color: var(--ink-3) !important; }
 
/* ── Masthead ── */
.masthead { border-bottom: 3px double var(--ink); padding-bottom: 1rem; margin-bottom: 0.25rem; }
.masthead-eyebrow { font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.3em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 0.4rem; }
.masthead-title { font-family: 'Playfair Display', serif; font-size: clamp(2rem, 4vw, 3.4rem); font-weight: 900; line-height: 0.95; letter-spacing: -0.02em; color: var(--ink); }
.masthead-title em { font-style: italic; color: var(--amber); }
.masthead-deck { font-size: 0.82rem; color: var(--ink-3); margin-top: 0.6rem; border-left: 3px solid var(--amber); padding-left: 0.75rem; }
 
/* ── Section label ── */
.section-label { font-family: 'DM Mono', monospace; font-size: 0.6rem; letter-spacing: 0.25em; text-transform: uppercase; color: var(--ink-3); border-bottom: 1px solid var(--rule); padding-bottom: 0.35rem; margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem; }
.section-label::before { content: ''; display: inline-block; width: 6px; height: 6px; background: var(--amber); border-radius: 50%; }
 
/* ── Panel ── */
.panel { background: var(--cream); border: 1px solid var(--sand); border-radius: 6px; padding: 1.4rem; margin-bottom: 1rem; }
.panel-title { font-family: 'DM Mono', monospace; font-size: 0.6rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }
.panel-title .dot { width: 5px; height: 5px; border-radius: 50%; background: var(--amber); flex-shrink: 0; }
.panel-body { font-size: 0.87rem; line-height: 1.8; color: var(--ink-2); }
 
/* session title */
.session-title-panel { background: var(--ink); border-radius: 6px; padding: 1.4rem 1.6rem; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 1.25rem; }
.session-title-pill { font-family: 'DM Mono', monospace; font-size: 0.58rem; letter-spacing: 0.2em; text-transform: uppercase; background: rgba(212,130,10,0.25); color: var(--amber-lt); border: 1px solid rgba(212,130,10,0.4); border-radius: 3px; padding: 0.25rem 0.6rem; white-space: nowrap; }
.session-title-text { font-family: 'Playfair Display', serif; font-size: 1.3rem; font-weight: 700; color: var(--cream); line-height: 1.3; }
 
/* chips */
.chip { display: inline-block; font-family: 'DM Mono', monospace; font-size: 0.6rem; letter-spacing: 0.08em; padding: 0.2rem 0.55rem; border-radius: 3px; margin-right: 0.35rem; margin-bottom: 0.35rem; }
.chip-amber { background: rgba(212,130,10,0.12); color: var(--amber); border: 1px solid rgba(212,130,10,0.25); }
.chip-teal  { background: rgba(26,107,94,0.1);  color: var(--teal);  border: 1px solid rgba(26,107,94,0.2); }
.chip-rust  { background: rgba(184,74,30,0.1);  color: var(--rust);  border: 1px solid rgba(184,74,30,0.2); }
 
/* transcript */
.transcript-box { background: var(--paper); border: 1px solid var(--sand); border-radius: 4px; padding: 1.2rem; font-family: 'DM Mono', monospace; font-size: 0.75rem; line-height: 1.9; max-height: 280px; overflow-y: auto; color: var(--ink-3); white-space: pre-wrap; word-break: break-word; }
 
/* chat */
.chat-wrap { background: var(--cream); border: 1px solid var(--sand); border-radius: 6px; padding: 1.2rem; max-height: 400px; overflow-y: auto; margin-bottom: 1rem; }
.chat-msg-wrap { margin-bottom: 1.1rem; }
.chat-from { font-family: 'DM Mono', monospace; font-size: 0.58rem; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 0.3rem; }
.from-user { color: var(--amber); } .from-bot { color: var(--teal); }
.bubble { display: inline-block; max-width: 88%; padding: 0.65rem 1rem; border-radius: 6px; font-size: 0.85rem; line-height: 1.65; }
.bubble-user { background: var(--ink); color: var(--cream); float: right; clear: both; }
.bubble-bot  { background: var(--paper); color: var(--ink-2); border: 1px solid var(--sand); float: left; clear: both; }
.clearfix { clear: both; }
 
/* file info */
.file-info-box { background: rgba(26,107,94,0.08); border: 1px solid rgba(26,107,94,0.25); border-radius: 4px; padding: 0.55rem 0.75rem; font-size: 0.72rem; font-family: 'DM Mono', monospace; color: var(--teal-lt); display: flex; align-items: center; gap: 0.5rem; margin-top: 0.4rem; word-break: break-all; }
 
/* success banner */
.success-banner { background: rgba(26,107,94,0.1); border: 1.5px solid rgba(26,107,94,0.35); border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.75rem; font-size: 0.88rem; color: var(--teal); font-weight: 500; }
.success-banner-icon { font-size: 1.2rem; }
 
/* empty state */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 5rem 2rem; text-align: center; }
.empty-glyph { font-family: 'Playfair Display', serif; font-size: 5rem; font-weight: 900; color: var(--sand); line-height: 1; margin-bottom: 1.5rem; user-select: none; }
.empty-headline { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: var(--ink); margin-bottom: 0.5rem; }
.empty-sub { font-size: 0.85rem; color: var(--ink-3); max-width: 400px; line-height: 1.7; }
.empty-chips { margin-top: 1.5rem; }
 
/* misc */
hr { border: none !important; border-top: 1px solid var(--rule) !important; margin: 1.5rem 0 !important; }
.stProgress > div > div > div { background: var(--amber) !important; }
.stSpinner > div { border-top-color: var(--amber) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--ink-2) !important; }
label { color: var(--ink-3) !important; font-size: 0.78rem !important; }
.stTextInput > div > div > input { background: var(--cream) !important; border: 1px solid var(--sand) !important; border-radius: 4px !important; color: var(--ink) !important; font-family: 'DM Sans', sans-serif !important; }
.stTextInput > div > div > input:focus { border-color: var(--amber) !important; box-shadow: 0 0 0 2px rgba(212,130,10,0.15) !important; }
::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--rule); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)
 
# ─── Session State ───────────────────────────────────────────────────────────────
for key, default in {
    "result":         None,
    "chat_history":   [],
    "pipeline_done":  False,
    "pipeline_steps": {},
    "input_mode":     "url",
    "uploaded_path":  None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default
 
# ─── Step definitions ────────────────────────────────────────────────────────────
# (key, number, display name, active description, done description)
STEPS = [
    ("audio",      "01", "Audio Processing",  "Extracting & chunking audio…",        "Audio extracted successfully"),
    ("transcript", "02", "Transcription",     "Converting speech to text…",          "Transcript ready"),
    ("title",      "03", "Title Generation",  "Generating session title…",           "Title generated"),
    ("summary",    "04", "Summarisation",     "Summarising key points…",             "Summary complete"),
    ("extract",    "05", "Extraction",        "Extracting actions, decisions…",      "Actions, decisions & questions extracted"),
    ("rag",        "06", "RAG Engine",        "Building retrieval index for chat…",  "Chat index ready"),
]
 
def step_state(key):
    return st.session_state.pipeline_steps.get(key, "pending")
 
def update_step(key, state):
    st.session_state.pipeline_steps[key] = state
 
# ─── Render one step card (returns HTML string) ──────────────────────────────────
def step_card_html(key, num, name, active_desc, done_desc, state):
    pill_labels = {"pending": "Waiting", "active": "Running…", "done": "Complete ✓", "error": "Failed"}
    badge_txt   = "✓" if state == "done" else ("✕" if state == "error" else num)
    desc        = done_desc if state == "done" else (active_desc if state == "active" else "Waiting for previous steps")
    return f"""
<div class="step-card {state}">
    <div class="step-badge {state}">{badge_txt}</div>
    <div class="step-info">
        <div class="step-name {state}">{name}</div>
        <div class="step-desc {state}">{desc}</div>
    </div>
    <div class="step-pill {state}">{pill_labels.get(state,'—')}</div>
</div>"""
 
# ─── Pipeline header HTML ─────────────────────────────────────────────────────────
def pipeline_header_html(steps_dict):
    dots = ""
    for key, *_ in STEPS:
        s = steps_dict.get(key, "pending")
        dots += f'<div class="pdot {s}"></div>'
    done_count = sum(1 for k, *_ in STEPS if steps_dict.get(k) == "done")
    return f"""
<div class="pipeline-header">
    <div class="pipeline-title">◎ &nbsp;Analysis Pipeline &nbsp;<span style="font-family:'DM Mono',monospace;font-size:0.72rem;color:var(--ink-3);font-weight:400">{done_count}/{len(STEPS)} complete</span></div>
    <div class="progress-dots">{dots}</div>
</div>"""
 
# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-logo">◎ <span>Lens</span></div>
        <div class="sb-tagline">Meeting Intelligence</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
 
    st.markdown('<div class="sb-section-hd">Source Type</div>', unsafe_allow_html=True)
    input_mode = st.radio(
        "Input mode",
        options=["🔗  YouTube / URL", "📁  Upload File"],
        index=0 if st.session_state.input_mode == "url" else 1,
        label_visibility="collapsed",
    )
    st.session_state.input_mode = "url" if input_mode.startswith("🔗") else "upload"
    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
 
    source       = None
    ready_to_run = False
 
    if st.session_state.input_mode == "url":
        st.markdown('<div class="sb-section-hd">YouTube URL or File Path</div>', unsafe_allow_html=True)
        url_val = st.text_input("url", placeholder="https://youtube.com/watch?v=...", label_visibility="collapsed")
        source = url_val.strip() if url_val else None
        ready_to_run = bool(source)
    else:
        st.markdown('<div class="sb-section-hd">Upload MP4 / MP3 / WAV</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("upload", type=["mp4","mp3","wav","m4a","webm"], label_visibility="collapsed")
        if uploaded_file is not None:
            save_path = UPLOAD_DIR / uploaded_file.name
            with open(save_path, "wb") as f:
                shutil.copyfileobj(uploaded_file, f)
            st.session_state.uploaded_path = str(save_path)
            st.markdown(f'<div class="file-info-box">✓ &nbsp;{uploaded_file.name}</div>', unsafe_allow_html=True)
        source = st.session_state.uploaded_path
        ready_to_run = bool(source and Path(source).exists())
 
    st.markdown('<div class="sb-section-hd" style="margin-top:1rem">Language</div>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["english","hinglish"], index=0, label_visibility="collapsed")
 
    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
    run_btn = st.button("◎  Run Analysis", use_container_width=True, disabled=not ready_to_run)
 
    if not ready_to_run:
        hint = "Enter a URL to continue." if st.session_state.input_mode == "url" else "Upload a file to continue."
        st.markdown(f'<div style="font-size:0.66rem;color:rgba(245,240,232,0.3);margin-top:0.3rem;text-align:center">{hint}</div>', unsafe_allow_html=True)
 
    # Sidebar status mirror (only shown during/after run)
    if st.session_state.pipeline_steps:
        st.markdown('<hr class="sb-rule">', unsafe_allow_html=True)
        st.markdown('<div class="sb-section-hd">Pipeline</div>', unsafe_allow_html=True)
        for key, num, name, *_ in STEPS:
            s = step_state(key)
            ic = "✓" if s == "done" else num
            st.markdown(f"""
            <div class="sb-step {s}">
                <div class="sb-step-num {s}">{ic}</div>
                <span>{name}</span>
            </div>""", unsafe_allow_html=True)
 
# ─── Main header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="masthead">
    <div class="masthead-eyebrow">◎ Lens — AI Meeting Intelligence</div>
    <div class="masthead-title">Every Meeting,<br><em>Understood.</em></div>
    <div class="masthead-deck">Transcribe · Summarise · Extract insights · Chat with your recordings</div>
</div>""", unsafe_allow_html=True)
 
st.markdown("""
<div style="padding:0.6rem 0 1rem 0">
    <span class="chip chip-amber">Transcription</span>
    <span class="chip chip-teal">Summarisation</span>
    <span class="chip chip-rust">Action Items</span>
    <span class="chip chip-amber">Key Decisions</span>
    <span class="chip chip-teal">RAG Chat</span>
</div>""", unsafe_allow_html=True)
 
# ─── Run Pipeline ────────────────────────────────────────────────────────────────
if run_btn:
    st.session_state.pipeline_done  = False
    st.session_state.result         = None
    st.session_state.chat_history   = []
    st.session_state.pipeline_steps = {k: "pending" for k, *_ in STEPS}
 
    # One st.empty() slot per step — each can be updated independently
    # while the next blocking call runs. Streamlit flushes each .markdown()
    # call to the browser immediately without needing a full rerun.
    header_slot = st.empty()
    slots = {key: st.empty() for key, *_ in STEPS}
    error_slot  = st.empty()
 
    def refresh_all():
        """Re-render the header + every step card in their own slots."""
        header_slot.markdown(
            pipeline_header_html(st.session_state.pipeline_steps),
            unsafe_allow_html=True,
        )
        for key, num, name, active_desc, done_desc in STEPS:
            s = step_state(key)
            slots[key].markdown(step_card_html(key, num, name, active_desc, done_desc, s), unsafe_allow_html=True)
 
    try:
        refresh_all()
 
        # ── Step 1 ──────────────────────────────────────────────────────────────
        update_step("audio", "active");  refresh_all()
        chunks = process_input(source)
        update_step("audio", "done");    refresh_all()
 
        # ── Step 2 ──────────────────────────────────────────────────────────────
        update_step("transcript", "active"); refresh_all()
        transcript = transcribe_all(chunks, language)
        update_step("transcript", "done");   refresh_all()
 
        # ── Step 3 ──────────────────────────────────────────────────────────────
        update_step("title", "active"); refresh_all()
        title = generate_title(transcript)
        update_step("title", "done");   refresh_all()
 
        # ── Step 4 ──────────────────────────────────────────────────────────────
        update_step("summary", "active"); refresh_all()
        summary = summarize(transcript)
        update_step("summary", "done");   refresh_all()
 
        # ── Step 5 ──────────────────────────────────────────────────────────────
        update_step("extract", "active"); refresh_all()
        action_items = extract_action_items(transcript)
        decisions    = extract_key_decisions(transcript)
        questions    = extract_questions(transcript)
        update_step("extract", "done");   refresh_all()
 
        # ── Step 6 ──────────────────────────────────────────────────────────────
        update_step("rag", "active"); refresh_all()
        rag_chain = build_rag_chain(transcript)
        update_step("rag", "done");   refresh_all()
 
        st.session_state.result = {
            "title":          title,
            "transcript":     transcript,
            "summary":        summary,
            "action_items":   action_items,
            "key_decisions":  decisions,
            "open_questions": questions,
            "rag_chain":      rag_chain,
        }
        st.session_state.pipeline_done = True
        time.sleep(0.8)   # let user see all-green for a moment before results load
        st.rerun()
 
    except Exception as e:
        # Mark whichever step was running as errored
        for k, *_ in STEPS:
            if st.session_state.pipeline_steps.get(k) == "active":
                st.session_state.pipeline_steps[k] = "error"
        refresh_all()
        error_slot.error(f"Pipeline error: {e}")
 
# ─── Results ─────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result
 
    # All-done pipeline summary (collapsed, all green)
    st.markdown(pipeline_header_html({k: "done" for k, *_ in STEPS}), unsafe_allow_html=True)
    done_cards = "".join(
        step_card_html(key, num, name, ad, dd, "done")
        for key, num, name, ad, dd in STEPS
    )
    with st.expander("◎ View completed pipeline steps", expanded=False):
        st.markdown(done_cards, unsafe_allow_html=True)
 
    st.markdown("""
    <div class="success-banner">
        <span class="success-banner-icon">✓</span>
        All 6 steps completed — results ready below.
    </div>""", unsafe_allow_html=True)
 
    # Session title
    st.markdown(f"""
    <div class="session-title-panel">
        <span class="session-title-pill">Session</span>
        <div class="session-title-text">{r['title']}</div>
    </div>""", unsafe_allow_html=True)
 
    # Row 1: Summary + Transcript
    st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 2], gap="medium")
    with col1:
        st.markdown(f"""
        <div class="panel">
            <div class="panel-title"><div class="dot"></div>Summary</div>
            <div class="panel-body">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        with st.expander("📄 Full Transcript", expanded=False):
            st.markdown(f'<div class="transcript-box">{r["transcript"]}</div>', unsafe_allow_html=True)
 
    # Row 2: Extraction panels
    st.markdown('<div class="section-label">Extracted Intelligence</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(f"""
        <div class="panel">
            <div class="panel-title"><div class="dot" style="background:var(--teal)"></div>Action Items</div>
            <div class="panel-body">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="panel">
            <div class="panel-title"><div class="dot" style="background:var(--rust)"></div>Key Decisions</div>
            <div class="panel-body">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="panel">
            <div class="panel-title"><div class="dot" style="background:var(--amber)"></div>Open Questions</div>
            <div class="panel-body">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)
 
    # RAG Chat
    st.markdown("---")
    st.markdown('<div class="section-label">Ask Your Meeting</div>', unsafe_allow_html=True)
 
    if st.session_state.chat_history:
        chat_html = '<div class="chat-wrap">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg-wrap">
                    <div class="chat-from from-user">You</div>
                    <div style="text-align:right"><div class="bubble bubble-user">{msg['content']}</div></div>
                    <div class="clearfix"></div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg-wrap">
                    <div class="chat-from from-bot">◎ Lens</div>
                    <div class="bubble bubble-bot">{msg['content']}</div>
                    <div class="clearfix"></div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="panel" style="text-align:center;padding:2.5rem 2rem;">
            <div style="font-family:'Playfair Display',serif;font-size:1.05rem;font-weight:700;color:var(--ink);margin-bottom:0.4rem">Start a conversation</div>
            <div style="font-size:0.82rem;color:var(--ink-3);line-height:1.7">Ask anything about the meeting — decisions, attendees, deadlines, context.</div>
        </div>""", unsafe_allow_html=True)
 
    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input("Question", placeholder="What were the main decisions made?", label_visibility="collapsed")
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)
 
    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user",      "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()
 
    if st.session_state.chat_history:
        if st.button("Clear Conversation", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
 
# ─── Empty state ──────────────────────────────────────────────────────────────────
else:
    if not st.session_state.pipeline_steps:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-glyph">◎</div>
            <div class="empty-headline">Ready to Analyse</div>
            <div class="empty-sub">
                Choose a source in the sidebar — paste a YouTube URL or upload an MP4/MP3 file —
                then pick your language and hit <strong>Run Analysis</strong>.
            </div>
            <div class="empty-chips">
                <span class="chip chip-amber">Transcription</span>
                <span class="chip chip-teal">Summarisation</span>
                <span class="chip chip-rust">Action Items</span>
                <span class="chip chip-amber">Decisions</span>
                <span class="chip chip-teal">RAG Chat</span>
            </div>
        </div>""", unsafe_allow_html=True)