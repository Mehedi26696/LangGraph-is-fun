
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid


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


# ********************************************* Utility Functions *********************************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return str(thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state.thread_id = thread_id
    add_thread(st.session_state.thread_id)
    st.session_state.message_history = []

def add_thread(thread_id):
    if thread_id not in st.session_state.chat_threads:
        st.session_state.chat_threads.append(thread_id)


def load_conversation(thread_id):
    config_load = {'configurable': {'thread_id': thread_id}}
    try:
        state = chatbot.get_state(config=config_load)
        if state and state.values and 'messages' in state.values:
            load_messages = state.values['messages']
            return load_messages
        else:
            return []   
    except Exception as e:
        print(f"Error loading conversation: {e}")
        return []  

def get_conversation_preview(thread_id):
    """Get the first user message from a conversation for display purposes"""
    messages = load_conversation(thread_id)
    if messages:
        # Find the first human message
        for msg in messages:
            if isinstance(msg, HumanMessage):
                # Truncate the message if it's too long
                preview = msg.content[:50]
                if len(msg.content) > 50:
                    preview += "..."
                return preview
    return "New Chat"  # Default if no messages found  

# ********************************************* Session Setup *********************************************
if "message_history" not in st.session_state:
    st.session_state.message_history = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state.chat_threads = []

add_thread(st.session_state.thread_id)

message_history = st.session_state.message_history


#********************************************* Sidebar Setup *********************************************

st.sidebar.title("Chatbot Assistant Using LangGraph")

if st.sidebar.button("New Chat"):
    reset_chat()


st.sidebar.header("My Conversations")

for thread_id in st.session_state.chat_threads[::-1]:
    # Get the conversation preview (first user message)
    conversation_preview = get_conversation_preview(thread_id)
    
    if st.sidebar.button(conversation_preview, key=f"conv_{thread_id}"):
        messages = load_conversation(thread_id)
        st.session_state.thread_id = thread_id

        temp_message_history = []
        if messages:  
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    role = 'user'
                else:
                    role = 'assistant'
                temp_message_history.append({'role': role, 'content': msg.content})

        st.session_state.message_history = temp_message_history


# ********************************************* Main Interface Setup *********************************************

for message in message_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])  

user_input = st.chat_input("💬 Ask me anything...")


if user_input:
     
    st.session_state.message_history.append({'role': 'user', 'content': user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    
    CONFIG = {'configurable': {'thread_id': st.session_state.thread_id}}
    
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                ai_message = st.write_stream(
                    message_chunk.content for message_chunk, metadata in chatbot.stream(
                        {'messages': [HumanMessage(content=user_input)]},
                        config=CONFIG,
                        stream_mode='messages'
                    )
                )
                st.session_state.message_history.append({"role": "assistant", "content": ai_message})
            except Exception as e:
                st.error(f"Sorry, I encountered an error: {str(e)}")
                st.markdown("Please try again or start a new chat.")