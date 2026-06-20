import streamlit as st
from dotenv import load_dotenv

from main import run_pipeline
from core.rag_engine import ask_question

load_dotenv()

st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>

.main {
    background-color: #0f172a;
}

.block-container {
    padding-top: 2rem;
    max-width: 1400px;
}

.hero {
    padding: 2rem;
    border-radius: 24px;
    background: linear-gradient(135deg,#0ea5e9,#2563eb,#7c3aed);
    color: white;
    margin-bottom: 1.5rem;
}

.hero h1{
    font-size:3rem;
    font-weight:800;
    margin-bottom:0.5rem;
}

.hero p{
    font-size:1.1rem;
    opacity:0.9;
}

.metric-card {
    padding:1rem;
    border-radius:18px;
    background:#111827;
    border:1px solid #374151;
}

div[data-testid="stMetric"]{
    background:#111827;
    padding:20px;
    border-radius:18px;
    border:1px solid #374151;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 12px 20px;
}

.chat-container {
    border-radius:20px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session State
# -----------------------------
if "processed" not in st.session_state:
    st.session_state.processed = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# HERO
# -----------------------------
st.markdown("""
<div class="hero">
    <h1>🎥 AI Video Assistant</h1>
    <p>
        Transform videos, meetings and recordings into
        summaries, action items, decisions and searchable knowledge.
    </p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:

    st.title("⚙️ Controls")

    source = st.text_input(
        "Video URL / File Path",
        placeholder="https://youtube.com/..."
    )

    language = st.selectbox(
        "Language",
        ["english", "hinglish"]
    )

    process_btn = st.button(
        "🚀 Process Recording",
        use_container_width=True
    )

# -----------------------------
# PROCESSING
# -----------------------------
if process_btn:

    if not source:
        st.error("Please enter a source.")
        st.stop()

    with st.spinner("Analyzing video..."):

        result = run_pipeline(source, language)

        st.session_state.result = result
        st.session_state.processed = True
        st.session_state.messages = []

# -----------------------------
# RESULTS
# -----------------------------
if st.session_state.processed:

    result = st.session_state.result

    st.markdown(f"""
    <div style="
        padding:24px;
        border-radius:20px;
        background:#111827;
        border:1px solid #374151;
        margin-bottom:20px;
    ">
        <h2 style="margin:0;">📌 {result['title']}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Action Items",
            len(str(result["action_items"]).split("\n"))
        )

    with col2:
        st.metric(
            "Key Decisions",
            len(str(result["key_decisions"]).split("\n"))
        )

    with col3:
        st.metric(
            "Open Questions",
            len(str(result["open_questions"]).split("\n"))
        )

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary",
        "✅ Action Items",
        "🔑 Decisions",
        "❓ Questions",
        "📝 Transcript"
    ])

    with tab1:
        st.markdown(result["summary"])

    with tab2:
        st.markdown(result["action_items"])

    with tab3:
        st.markdown(result["key_decisions"])

    with tab4:
        st.markdown(result["open_questions"])

    with tab5:
        st.text_area(
            "Transcript",
            result["transcript"],
            height=500
        )

    st.divider()

    st.subheader("💬 Chat With Your Meeting")

    rag_chain = result["rag_chain"]

    for msg in st.session_state.messages:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(
        "Ask anything about the meeting..."
    )

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):
                answer = ask_question(
                    rag_chain,
                    prompt
                )

            st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

else:

    st.info(
        "Enter a YouTube URL or local file path and click Process Recording."
    )