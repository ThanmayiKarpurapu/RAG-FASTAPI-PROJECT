import streamlit as st
import requests

# Change if your FastAPI runs on a different host/port
FASTAPI_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG Chat UI", page_icon="💬", layout="centered")
st.title("💬 RAG Chat UI (FastAPI + Chroma + OpenAI)")


# Sidebar settings
st.sidebar.header("Settings")
session_id = st.sidebar.text_input("Session ID", value="demo1")
top_k = st.sidebar.slider("Top K (retrieval)", min_value=1, max_value=10, value=5)
endpoint = st.sidebar.text_input("FastAPI Base URL", value=FASTAPI_BASE)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Chat input
user_msg = st.chat_input("Ask something...")
if user_msg:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # Call FastAPI /chat
    try:
        payload = {"session_id": session_id, "message": user_msg, "top_k": top_k}
        resp = requests.post(f"{endpoint}/chat", json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        answer = data.get("answer", "")
        sources = data.get("sources", [])

        # Show assistant message
        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)

            # Optional: show sources
            with st.expander("Sources (metadata)"):
                st.json(sources)

    except Exception as e:
        with st.chat_message("assistant"):
            st.error(f"Error calling API: {e}")