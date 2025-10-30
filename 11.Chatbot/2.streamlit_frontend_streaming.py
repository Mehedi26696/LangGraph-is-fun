
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage


st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1f77b4;
        padding-bottom: 20px;
    }
    .stChatMessage {
        margin-bottom: 10px;
    }
    .chat-input {
        position: fixed;
        bottom: 0;
        background: white;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

# Add a simple title
st.markdown('<h1 class="main-title">Chatbot Assistant Using LangGraph</h1>', unsafe_allow_html=True)

if "message_history" not in st.session_state:
    st.session_state.message_history = []

message_history = st.session_state.message_history


for message in message_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])  

user_input = st.chat_input("💬 Ask me anything...")


if user_input:
     
    st.session_state.message_history.append({'role': 'user', 'content': user_input})

    with st.chat_message("user"):
        st.markdown(user_input)
    
    
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):
            ai_message = st.write_stream(
                message_chunk.content for message_chunk, metadata in chatbot.stream(
                    {'messages': [HumanMessage(content=user_input)]},
                    config=CONFIG,
                    stream_mode='messages'
                )
            )
        st.session_state.message_history.append({"role": "assistant", "content": ai_message})