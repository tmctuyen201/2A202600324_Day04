import streamlit as st
import os
from dotenv import load_dotenv, set_key

load_dotenv()

from agent import run_agent_with_logs, ConversationMemory

# ─────────────────────────────────────────────
# PAGE CONFIG & STYLING
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TravelBuddy - Trợ lý Du lịch Thông minh",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .log-container {
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
        background-color: #263238;
        color: #aed581;
        padding: 15px;
        border-radius: 8px;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory(max_turns=20)

if "last_logs" not in st.session_state:
    st.session_state.last_logs = []

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ✈️ TravelBuddy")
    st.markdown("---")

    # LLM Provider selector
    st.markdown("**⚙️ Cấu hình LLM:**")
    current_provider = os.getenv("LLM_PROVIDER", "openai")
    provider = st.selectbox(
        "Chọn provider",
        options=["openai", "gemini"],
        index=0 if current_provider == "openai" else 1,
        key="llm_provider"
    )
    if provider != current_provider:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        set_key(env_path, "LLM_PROVIDER", provider)
        os.environ["LLM_PROVIDER"] = provider
        st.success(f"Đã chuyển sang {provider.upper()}")

    if provider == "openai":
        api_key_input = st.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            key="openai_key_input"
        )
        if api_key_input and api_key_input != os.getenv("OPENAI_API_KEY", ""):
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            set_key(env_path, "OPENAI_API_KEY", api_key_input)
            os.environ["OPENAI_API_KEY"] = api_key_input
            st.success("Đã lưu OpenAI API Key")
    else:
        api_key_input = st.text_input(
            "Gemini API Key",
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password",
            key="gemini_key_input"
        )
        if api_key_input and api_key_input != os.getenv("GEMINI_API_KEY", ""):
            env_path = os.path.join(os.path.dirname(__file__), ".env")
            set_key(env_path, "GEMINI_API_KEY", api_key_input)
            os.environ["GEMINI_API_KEY"] = api_key_input
            st.success("Đã lưu Gemini API Key")

    st.markdown("---")
    st.markdown("**Tính năng:**")
    st.markdown("• 🔍 Tìm chuyến bay")
    st.markdown("• 🏨 Tìm khách sạn")
    st.markdown("• 💰 Tính ngân sách")
    st.markdown("---")
    st.markdown("**Thành phố hỗ trợ:**")
    st.markdown("• Hà Nội")
    st.markdown("• Đà Nẵng")
    st.markdown("• Phú Quốc")
    st.markdown("• Hồ Chí Minh")
    st.markdown("---")
    st.markdown("**Thử ngay:**")
    st.code("Chào bạn!", language=None)
    st.code("Vé máy bay Hà Nội đi Đà Nẵng", language=None)
    st.code("Đi Phú Quốc 2 đêm, budget 5tr", language=None)
    st.code("Tôi muốn đặt phòng", language=None)
    st.code("Viết code Python giúp tôi", language=None)
    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory = ConversationMemory(max_turns=20)
        st.session_state.last_logs = []
        st.rerun()

    turns = len(st.session_state.memory)
    st.caption(f"🧠 Memory: {turns} lượt hội thoại")

# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────
st.markdown('<p class="main-header">✈️ TravelBuddy</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Trợ lý Du lịch Thông minh — Powered by LangGraph & Gemini</p>', unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Hỏi về chuyến bay, khách sạn, ngân sách..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Đang suy nghĩ..."):
            try:
                result = run_agent_with_logs(
                    prompt,
                    memory=st.session_state.memory,
                    console_output=False,
                )
                content = result["response"]
                st.session_state.last_logs = result["logs"]
                st.markdown(content)
                st.session_state.messages.append({"role": "assistant", "content": content})
            except Exception as e:
                error_msg = f"❌ Có lỗi xảy ra: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ─────────────────────────────────────────────
# THINKING PROCESS EXPANDER
# ─────────────────────────────────────────────
if st.session_state.last_logs:
    st.markdown("---")
    with st.expander("🔍 Quá trình suy nghĩ của Agent", expanded=False):
        logs_text = "\n".join(st.session_state.last_logs)
        st.markdown(f'<div class="log-container">{logs_text}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 0.85rem;'>"
    "TravelBuddy © 2024 | Powered by LangGraph & Google Gemini"
    "</div>",
    unsafe_allow_html=True
)