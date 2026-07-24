import os
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app

st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon=None,
    layout="wide"
)

# ── Icon set (inline SVG, stroke-based, replaces all emoji) ───────────────────
def icon(name: str, size: int = 16, color: str = "currentColor") -> str:
    paths = {
        "plane": '<path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/>',
        "hotel": '<path d="M3 21h18"/><path d="M5 21V7l7-4 7 4v14"/><path d="M9 21v-6h6v6"/>',
        "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
        "brain": '<circle cx="12" cy="12" r="9"/><path d="M12 7v10M8 9.5h8M8 14.5h8"/>',
        "map": '<path d="M9 20l-6-3V4l6 3 6-3 6 3v13l-6-3-6 3-6-3"/><path d="M9 4v13M15 7v13"/>',
        "rocket": '<path d="M4.5 16.5c-1.5 1.5-2 5-2 5s3.5-.5 5-2c.8-.8 1-2.2.2-3.2-.9-.9-2.4-.7-3.2.2z"/><path d="M12 15l-3-3c1-3.5 3.5-8 8.5-10.5C22.5 4 21 9.5 18.5 12.5 16 15.5 12 15 12 15z"/>',
        "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/>',
        "link": '<path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1.5 1.5"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1.5-1.5"/>',
        "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v3M15 2v3M9 19v3M15 19v3M2 9h3M2 15h3M19 9h3M19 15h3"/>',
        "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
        "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
        "tag": '<path d="M20 12l-8 8-9-9V4h7l10 8z"/><circle cx="7.5" cy="7.5" r="1"/>',
        "download": '<path d="M12 3v12M7 10l5 5 5-5"/><path d="M4 21h16"/>',
        "folder": '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>',
        "pin": '<path d="M12 21s7-7.2 7-12a7 7 0 1 0-14 0c0 4.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/>',
        "sparkle": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/>',
    }
    d = paths.get(name, "")
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" style="vertical-align:-3px">{d}</svg>')


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg-0: #0B0F19;
    --bg-1: #111827;
    --bg-2: #161B22;
    --accent-1: #2563EB;
    --accent-2: #3B82F6;
    --accent-3: #60A5FA;
    --teal: #14B8A6;
    --sky: #38BDF8;
    --text-hi: #FFFFFF;
    --text-lo: #D1D5DB;
    --border: rgba(255,255,255,0.08);
}

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background: var(--bg-0);
}

h1, h2, h3, .hero-title, .sec-head span, .sidebar-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── Hero ── */
.hero-wrapper {
    position: relative;
    border-radius: 24px;
    overflow: hidden;
    margin-bottom: 1.75rem;
    height: 260px;
    border: 1px solid var(--border);
}
.hero-bg {
    width: 100%; height: 100%;
    object-fit: cover; display: block;
    filter: brightness(0.32) saturate(0.9);
    position: absolute; top: 0; left: 0;
}
.hero-content {
    position: relative; z-index: 2; height: 100%;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center; padding: 2rem;
    background: linear-gradient(180deg, rgba(11,15,25,0.15) 0%, rgba(11,15,25,0.65) 100%);
}
.hero-badge {
    background: rgba(37,99,235,0.15);
    border: 1px solid rgba(96,165,250,0.35);
    color: var(--accent-3);
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.35rem 1rem; border-radius: 999px;
    margin-bottom: 1rem; display: inline-flex;
    align-items: center; gap: 0.4rem;
}
.hero-title {
    font-size: 2.4rem; font-weight: 800;
    color: var(--text-hi); margin: 0 0 0.55rem;
    letter-spacing: -0.02em; line-height: 1.15;
    display: flex; align-items: center; gap: 0.6rem; justify-content: center;
}
.hero-sub {
    color: var(--text-lo); font-size: 0.98rem;
    max-width: 560px; font-weight: 400;
}

/* ── Destination strip ── */
.dest-card {
    border-radius: 14px; overflow: hidden; position: relative;
    height: 92px; cursor: pointer; border: 1px solid var(--border);
    transition: transform 0.25s ease, border-color 0.25s ease;
}
.dest-card:hover { transform: translateY(-3px); border-color: var(--accent-2); }
.dest-card img { width: 100%; height: 100%; object-fit: cover; filter: brightness(0.5); }
.dest-label {
    position: absolute; bottom: 8px; left: 0; right: 0; text-align: center;
    color: #fff; font-size: 0.78rem; font-weight: 600;
    display: flex; align-items: center; justify-content: center; gap: 0.3rem;
}

/* ── Input label ── */
.input-label {
    color: var(--accent-3); font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase;
    margin-bottom: 0.6rem; display: flex; align-items: center; gap: 0.4rem;
}

/* ── Generate / quick-fill buttons ── */
div[data-testid="stButton"] > button {
    background: var(--bg-1) !important;
    color: var(--text-lo) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: var(--accent-2) !important;
    color: var(--text-hi) !important;
    background: var(--bg-2) !important;
}

/* Primary CTA — the wide "Generate" button gets its own gradient look via key targeting isn't
   available in Streamlit, so we boost every full-width button in the main input row uniformly
   through container width + a distinguishing class added just below via markdown. */
div[data-testid="stButton"]:has(button[kind="primary"]) > button,
button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-1), #1D4ED8) !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 0 0 1px rgba(96,165,250,0.25), 0 8px 24px rgba(37,99,235,0.35) !important;
}
button[kind="primary"]:hover {
    box-shadow: 0 0 0 1px rgba(96,165,250,0.4), 0 10px 30px rgba(37,99,235,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ── Agent status cards ── */
[data-testid="stStatusWidget"] {
    background: var(--bg-1) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}
[data-testid="stStatusWidget"] > div:first-child { background: var(--bg-1) !important; border-radius: 14px 14px 0 0 !important; }
[data-testid="stStatusWidget"] details,
[data-testid="stStatusWidget"] details > div,
[data-testid="stStatusWidget"] [data-testid="stVerticalBlock"] {
    background: var(--bg-2) !important; color: var(--text-hi) !important;
    padding: 0.3rem 0.6rem !important;
}
[data-testid="stStatusWidget"] * { color: var(--text-hi) !important; }
[data-testid="stStatusWidget"] a { color: var(--accent-3) !important; }
[data-testid="stStatusWidget"] hr { border-color: var(--border) !important; }

/* ── Section headers ── */
.sec-head {
    display: flex; align-items: center; gap: 0.55rem;
    margin: 2rem 0 0.85rem; padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}
.sec-head span { font-size: 1.1rem; font-weight: 700; color: var(--text-hi); }

/* ── Metrics ── */
.metric-row { display: flex; gap: 1rem; margin: 1.5rem 0; }
.metric-box {
    flex: 1; background: var(--bg-1); border: 1px solid var(--border);
    border-radius: 14px; padding: 1.1rem 1.2rem; text-align: center;
}
.metric-val { font-size: 1.7rem; font-weight: 800; color: var(--accent-3); }
.metric-lbl {
    font-size: 0.74rem; color: var(--text-lo); margin-top: 0.25rem;
    text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;
}

/* ── Final plan card (glass) ── */
.final-card {
    background: linear-gradient(160deg, rgba(37,99,235,0.08) 0%, rgba(17,24,39,0.9) 55%);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(96,165,250,0.25);
    border-left: 3px solid var(--accent-2);
    border-radius: 16px; padding: 1.9rem;
    line-height: 1.8; color: var(--text-lo); font-size: 0.95rem;
}

/* ── Save bar ── */
.save-bar {
    background: var(--bg-1); border: 1px solid var(--border); border-radius: 10px;
    padding: 0.85rem 1.2rem; color: var(--text-lo); font-size: 0.86rem;
    margin-top: 0.6rem; display: flex; align-items: center; gap: 0.4rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: var(--bg-0) !important; border-right: 1px solid var(--border) !important; }
.sidebar-chip {
    background: var(--bg-1); border: 1px solid var(--border); border-radius: 9px;
    padding: 0.5rem 0.8rem; margin-bottom: 0.4rem; font-size: 0.82rem;
    color: var(--text-lo); display: flex; align-items: center; gap: 0.5rem;
}
.sidebar-title {
    color: var(--text-hi); font-size: 0.95rem; font-weight: 700;
    margin: 1.1rem 0 0.55rem; letter-spacing: -0.01em;
    display: flex; align-items: center; gap: 0.45rem;
}

#MainMenu, footer, header { visibility: hidden; }

/* Textarea */
.stTextArea textarea {
    background: var(--bg-1) !important; border: 1px solid var(--border) !important;
    border-radius: 12px !important; color: var(--text-hi) !important;
    font-size: 0.95rem !important; resize: none !important;
}
.stTextArea textarea:focus { border-color: var(--accent-2) !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.18) !important; }
.stTextArea textarea::placeholder { color: #6B7280 !important; }

/* Text input */
input[type="text"], .stTextInput input {
    background: var(--bg-1) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text-hi) !important;
}
input[type="text"]:focus, .stTextInput input:focus { border-color: var(--accent-2) !important; box-shadow: 0 0 0 3px rgba(37,99,235,0.18) !important; }
input[type="text"]::placeholder { color: #4B5563 !important; }

.stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label {
    color: var(--accent-3) !important; font-size: 0.78rem !important;
    font-weight: 700 !important; letter-spacing: 0.07em !important;
}

.stMarkdown p, .stMarkdown li, .stMarkdown td, .stMarkdown th { color: var(--text-lo) !important; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: var(--text-hi) !important; }
.stMarkdown code { background: var(--bg-2) !important; color: var(--accent-3) !important; padding: 0.15em 0.4em; border-radius: 5px; }

.stAlert { background: var(--bg-1) !important; border-radius: 12px !important; border: 1px solid var(--border) !important; }
.stAlert p, .stAlert div { color: var(--text-hi) !important; }

section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stMarkdown { color: var(--text-lo) !important; }
section[data-testid="stSidebar"] hr { border-color: var(--border) !important; }

div[data-testid="stDownloadButton"] > button {
    background: var(--bg-2) !important; color: var(--text-hi) !important;
    border: 1px solid rgba(96,165,250,0.3) !important; border-radius: 10px !important;
}
div[data-testid="stDownloadButton"] > button:hover { border-color: var(--accent-2) !important; }

hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div class='sidebar-title'>{icon('plane', 18)} AI Travel Planner</div>", unsafe_allow_html=True)
    st.markdown("---")

    thread_id = st.text_input("User ID", value="aarohi_user",
                              help="Your session ID — keeps travel history across queries")

    st.markdown(f"<div class='sidebar-title'>{icon('cpu', 16)} Powered by</div>", unsafe_allow_html=True)
    STACK = [
        ("link", "LangGraph"),
        ("cpu", "Groq · LLaMA 3.3 70B"),
        ("database", "PostgreSQL"),
        ("search", "Tavily Search"),
        ("plane", "AviationStack"),
    ]
    for ic, label in STACK:
        st.markdown(f"<div class='sidebar-chip'>{icon(ic, 15)} {label}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='sidebar-title'>{icon('link', 16)} Agent Pipeline</div>", unsafe_allow_html=True)
    PIPELINE = [
        ("plane", "1  Flight Agent"),
        ("hotel", "2  Hotel Agent"),
        ("calendar", "3  Itinerary Agent"),
        ("brain", "4  Final Agent"),
    ]
    for ic, step in PIPELINE:
        st.markdown(f"<div class='sidebar-chip'>{icon(ic, 15)} {step}</div>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-wrapper">
    <img class="hero-bg"
         src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80"
         alt="airplane above clouds"/>
    <div class="hero-content">
        <div class="hero-badge">{icon('sparkle', 13)} Multi-Agent AI System</div>
        <div class="hero-title">{icon('plane', 30)} AI Travel Booking System</div>
        <div class="hero-sub">Four specialized agents work together — searching flights, hotels, building an itinerary, and delivering your perfect trip plan.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Destination image strip ───────────────────────────────────────────────────
DESTINATIONS = [
    ("Tokyo",   "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("Paris",   "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("Bangkok", "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("Rome",    "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("Dubai",   "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]

cols = st.columns(5)
for col, (name, img_url) in zip(cols, DESTINATIONS):
    with col:
        st.markdown(f"""
        <div class="dest-card">
            <img src="{img_url}" />
            <div class="dest-label">{icon('pin', 12, '#fff')} {name}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown(f"<div class='input-label'>{icon('map', 15)} Describe your trip</div>", unsafe_allow_html=True)

QUICK = ["7-day Japan under ₹2L", "Paris trip for 5 days", "Dubai weekend trip", "Bali backpacking 10 days"]
qcols = st.columns(len(QUICK))
quick_fill = ""
for qc, label in zip(qcols, QUICK):
    with qc:
        if st.button(label, key=f"q_{label}"):
            quick_fill = label

user_query = st.text_area(
    "Trip request",
    value=quick_fill,
    placeholder="e.g. Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs",
    height=100,
    label_visibility="collapsed",
)

generate = st.button("Generate My Travel Plan", use_container_width=True, type="primary")

# ── Agent pipeline ────────────────────────────────────────────────────────────
AGENT_META = {
    "flight_agent":    ("plane", "Flight Agent"),
    "hotel_agent":     ("hotel", "Hotel Agent"),
    "itinerary_agent": ("calendar", "Itinerary Agent"),
    "final_agent":     ("brain", "Final Agent"),
}

if generate:
    if not user_query.strip():
        st.warning("Please describe your trip first.")
    else:
        config = {"configurable": {"thread_id": thread_id}}
        collected = {"flight_results": "", "hotel_results": "",
                     "itinerary": "", "final_response": "", "llm_calls": 0}

        st.markdown("---")
        st.markdown(f"<div class='sec-head'>{icon('cpu', 18)}<span>Agent Pipeline — Live</span></div>",
                    unsafe_allow_html=True)

        for chunk in app.stream(
            {
                "messages": [HumanMessage(content=user_query)],
                "user_query": user_query,
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",
                "llm_calls": 0,
            },
            config=config,
            stream_mode="updates",
        ):
            for node_name, state_update in chunk.items():
                ic, label = AGENT_META.get(node_name, ("cpu", node_name))

                with st.status(f"{label}", state="complete", expanded=True):
                    if node_name == "flight_agent":
                        text = state_update.get("flight_result", "")
                        collected["flight_results"] = text

                        with st.expander("Debug: flight_agent raw output", expanded=False):
                            st.write(state_update)

                        st.markdown(text or "_No flight data returned._")

                    elif node_name == "hotel_agent":
                        text = state_update.get("hotel_result", "")
                        collected["hotel_results"] = text

                        with st.expander("Debug: hotel_agent raw output", expanded=False):
                            st.write(state_update)

                        st.markdown(text or "_No hotel data returned._")

                    elif node_name == "itinerary_agent":
                        text = state_update.get("itinerary", "")
                        collected["itinerary"] = text
                        st.markdown(text or "_No itinerary generated._")

                    elif node_name == "final_agent":
                        msgs = state_update.get("messages", [])
                        text = msgs[-1].content if msgs else ""
                        collected["final_response"] = text
                        st.markdown(text or "_No final response._")

                    for node_name, state_update in chunk.items():
                        print("\n===================")
                        print("NODE:", node_name)
                        print("UPDATE:", state_update)
                        print("===================\n")

                    collected["llm_calls"] = state_update.get("llm_calls", collected["llm_calls"])

        # Metrics
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box"><div class="metric-val">4</div><div class="metric-lbl">Agents Run</div></div>
            <div class="metric-box"><div class="metric-val">{collected['llm_calls']}</div><div class="metric-lbl">LLM Calls</div></div>
            <div class="metric-box"><div class="metric-val">{icon('check', 22, '#14B8A6')}</div><div class="metric-lbl">Status</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Final plan card
        if collected["final_response"]:
            st.markdown(f"<div class='sec-head'>{icon('brain', 18)}<span>Final Travel Plan</span></div>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='final-card'>{collected['final_response']}</div>",
                        unsafe_allow_html=True)

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.md"
        save_dir = os.path.join(os.path.dirname(__file__), "travel_plans")
        os.makedirs(save_dir, exist_ok=True)

        file_content = f"""# Travel Plan
**Query:** {user_query}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**User ID:** {thread_id}

---

## Flight Information
{collected['flight_results'] or 'N/A'}

---

## Hotel Information
{collected['hotel_results'] or 'N/A'}

---

## Itinerary
{collected['itinerary'] or 'N/A'}

---

## Final Travel Plan
{collected['final_response'] or 'N/A'}

---
*LLM Calls: {collected['llm_calls']}*
"""
        with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
            f.write(file_content)

        dl_col, info_col = st.columns([1, 3])
        with dl_col:
            st.download_button(f"Download Plan", data=file_content,
                               file_name=filename, mime="text/markdown",
                               use_container_width=True)
        with info_col:
            st.markdown(f"<div class='save-bar'>{icon('folder', 15)} Auto-saved → <code>travel_plans/{filename}</code></div>",
                        unsafe_allow_html=True)