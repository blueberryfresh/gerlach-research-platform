"""
Streamlit Chat Interface for Gerlach (2018) Personality Types
Conversational UI with session management and downloadable transcripts
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import uuid
from gerlach_personality_llms import (
    GerlachPersonalityManager,
    Message,
    ConversationSession
)

st.set_page_config(
    page_title="Gerlach Personality Chat",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if 'manager' not in st.session_state:
    try:
        st.session_state.manager = GerlachPersonalityManager()
        st.session_state.manager_ready = True
    except Exception as e:
        st.session_state.manager_ready = False
        st.session_state.manager_error = str(e)

if 'current_session' not in st.session_state:
    st.session_state.current_session = None

if 'all_sessions' not in st.session_state:
    st.session_state.all_sessions = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Personality configurations
PERSONALITY_INFO = {
    "average": {
        "name": "Average",
        "emoji": "⚖️",
        "color": "#7570b3",
        "description": "Balanced and moderate across all Big Five traits"
    },
    "role_model": {
        "name": "Role model",
        "emoji": "⭐",
        "color": "#1b9e77",
        "description": "Low Neuroticism, High on all other traits (socially desirable)"
    },
    "self_centred": {
        "name": "Self-centred",
        "emoji": "🎯",
        "color": "#d95f02",
        "description": "Low Openness, Agreeableness, and Conscientiousness"
    },
    "reserved": {
        "name": "Reserved",
        "emoji": "🤫",
        "color": "#e7298a",
        "description": "Low Neuroticism and Openness (calm, conventional, introverted)"
    }
}


def start_new_session(personality_type: str):
    """Start a new conversation session"""
    session_id = str(uuid.uuid4())[:8]
    st.session_state.current_session = ConversationSession(
        personality_type=personality_type,
        session_id=session_id,
        messages=[],
        started_at=datetime.now().isoformat(),
        metadata={
            "personality_name": PERSONALITY_INFO[personality_type]["name"]
        }
    )
    st.session_state.chat_history = []


def end_current_session():
    """End the current session and save it"""
    if st.session_state.current_session:
        st.session_state.current_session.ended_at = datetime.now().isoformat()
        st.session_state.all_sessions.append(st.session_state.current_session)
        st.session_state.current_session = None
        st.session_state.chat_history = []


def send_message(user_message: str):
    """Send a message and get response"""
    if not st.session_state.current_session:
        st.error("No active session")
        return
    
    # Add user message
    user_msg = Message(role="user", content=user_message)
    st.session_state.current_session.messages.append(user_msg)
    st.session_state.chat_history.append({"role": "user", "content": user_message})
    
    # Get AI response
    personality_type = st.session_state.current_session.personality_type
    personality = st.session_state.manager.get_personality(personality_type)
    
    # Convert to Claude format
    claude_messages = [{"role": m["role"], "content": m["content"]} 
                       for m in st.session_state.chat_history]
    
    response = personality.chat(claude_messages)
    
    # Add assistant message
    assistant_msg = Message(role="assistant", content=response)
    st.session_state.current_session.messages.append(assistant_msg)
    st.session_state.chat_history.append({"role": "assistant", "content": response})


def export_session_json(session: ConversationSession) -> str:
    """Export session as JSON string"""
    return json.dumps(session.to_dict(), indent=2)


def export_all_sessions_json() -> str:
    """Export all sessions as JSON string"""
    return json.dumps(
        [s.to_dict() for s in st.session_state.all_sessions],
        indent=2
    )


def export_session_markdown(session: ConversationSession) -> str:
    """Export session as Markdown"""
    md = f"# Conversation with {session.metadata.get('personality_name', session.personality_type)}\n\n"
    md += f"**Session ID:** {session.session_id}\n"
    md += f"**Started:** {session.started_at}\n"
    md += f"**Ended:** {session.ended_at or 'In progress'}\n\n"
    md += "---\n\n"
    
    for msg in session.messages:
        role_label = "**You:**" if msg.role == "user" else f"**{session.metadata.get('personality_name')}:**"
        md += f"{role_label}\n{msg.content}\n\n"
    
    return md


# Main UI
st.title("💬 Gerlach Personality Chat Interface")

if not st.session_state.manager_ready:
    st.error(f"❌ Failed to initialize personality manager: {st.session_state.manager_error}")
    st.info("Please set your ANTHROPIC_API_KEY environment variable and restart the app.")
    st.stop()

st.markdown("Chat with AI personalities based on Gerlach et al. (2018) four personality types.")

# Sidebar
with st.sidebar:
    st.markdown("## 🎭 Personality Selection")
    
    if st.session_state.current_session:
        current_type = st.session_state.current_session.personality_type
        current_info = PERSONALITY_INFO[current_type]
        st.success(f"Active: {current_info['emoji']} {current_info['name']}")
        
        if st.button("🛑 End Session", use_container_width=True):
            end_current_session()
            st.rerun()
    else:
        st.info("No active session. Select a personality to start.")
        
        for ptype, info in PERSONALITY_INFO.items():
            if st.button(
                f"{info['emoji']} {info['name']}",
                key=f"start_{ptype}",
                use_container_width=True
            ):
                start_new_session(ptype)
                st.rerun()
    
    st.markdown("---")
    st.markdown("## 📊 Session Stats")
    st.metric("Total Sessions", len(st.session_state.all_sessions))
    if st.session_state.current_session:
        st.metric("Messages (Current)", len(st.session_state.current_session.messages))
    
    st.markdown("---")
    st.markdown("## 💾 Download Options")
    
    if st.session_state.current_session:
        st.markdown("### Current Session")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📄 JSON",
                data=export_session_json(st.session_state.current_session),
                file_name=f"session_{st.session_state.current_session.session_id}.json",
                mime="application/json",
                use_container_width=True
            )
        with col2:
            st.download_button(
                "📝 MD",
                data=export_session_markdown(st.session_state.current_session),
                file_name=f"session_{st.session_state.current_session.session_id}.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    if st.session_state.all_sessions:
        st.markdown("### All Sessions")
        st.download_button(
            "📦 All Sessions (JSON)",
            data=export_all_sessions_json(),
            file_name=f"all_sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# Main chat area
if st.session_state.current_session:
    current_type = st.session_state.current_session.personality_type
    current_info = PERSONALITY_INFO[current_type]
    
    st.markdown(
        f"<div style='background:{current_info['color']};color:white;padding:15px;border-radius:10px;margin-bottom:20px;'>"
        f"<h3 style='margin:0;'>{current_info['emoji']} Chatting with: {current_info['name']}</h3>"
        f"<p style='margin:5px 0 0 0;opacity:0.9;'>{current_info['description']}</p>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.current_session.messages:
            if msg.role == "user":
                st.chat_message("user").write(msg.content)
            else:
                st.chat_message("assistant").write(msg.content)
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        with st.spinner(f"{current_info['emoji']} Thinking..."):
            send_message(user_input)
        st.rerun()

else:
    st.info("👈 Select a personality from the sidebar to start a conversation")
    
    # Show personality cards
    st.markdown("## Available Personalities")
    
    cols = st.columns(2)
    for idx, (ptype, info) in enumerate(PERSONALITY_INFO.items()):
        with cols[idx % 2]:
            st.markdown(
                f"<div style='border:2px solid {info['color']};border-radius:10px;padding:15px;margin:10px 0;'>"
                f"<h3 style='color:{info['color']};margin:0;'>{info['emoji']} {info['name']}</h3>"
                f"<p style='color:#666;margin:10px 0 0 0;'>{info['description']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )

# Show completed sessions
if st.session_state.all_sessions:
    st.markdown("---")
    st.markdown("## 📚 Completed Sessions")
    
    for session in reversed(st.session_state.all_sessions):
        with st.expander(
            f"{PERSONALITY_INFO[session.personality_type]['emoji']} "
            f"{session.metadata.get('personality_name')} - "
            f"Session {session.session_id} "
            f"({len(session.messages)} messages)"
        ):
            st.markdown(f"**Started:** {session.started_at}")
            st.markdown(f"**Ended:** {session.ended_at}")
            
            for msg in session.messages:
                role_label = "You" if msg.role == "user" else session.metadata.get('personality_name')
                st.markdown(f"**{role_label}:** {msg.content}")
                st.markdown("---")
