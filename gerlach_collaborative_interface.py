"""
Gerlach Personality Collaborative Problem-Solving Interface
Single-page interface with all 4 personalities for collaborative problem-solving
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import uuid
from gerlach_personality_llms import GerlachPersonalityManager, Message

st.set_page_config(
    page_title="Gerlach Collaborative Problem Solving",
    page_icon="🧩",
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

if 'current_problem' not in st.session_state:
    st.session_state.current_problem = None

if 'problem_id' not in st.session_state:
    st.session_state.problem_id = None

if 'conversations' not in st.session_state:
    st.session_state.conversations = {
        'average': [],
        'role_model': [],
        'self_centred': [],
        'reserved': []
    }

if 'problem_history' not in st.session_state:
    st.session_state.problem_history = []

# Personality configurations
PERSONALITIES = {
    "average": {
        "name": "Average",
        "emoji": "⚖️",
        "color": "#7570b3",
        "description": "Balanced & Practical"
    },
    "role_model": {
        "name": "Role Model",
        "emoji": "⭐",
        "color": "#1b9e77",
        "description": "Optimistic & Organized"
    },
    "self_centred": {
        "name": "Self-Centred",
        "emoji": "🎯",
        "color": "#d95f02",
        "description": "Direct & Competitive"
    },
    "reserved": {
        "name": "Reserved",
        "emoji": "🤫",
        "color": "#e7298a",
        "description": "Calm & Conventional"
    }
}


def start_new_problem(problem_text: str):
    """Initialize a new problem-solving session"""
    st.session_state.problem_id = str(uuid.uuid4())[:8]
    st.session_state.current_problem = {
        'id': st.session_state.problem_id,
        'text': problem_text,
        'started_at': datetime.now().isoformat(),
        'status': 'active'
    }
    st.session_state.conversations = {
        'average': [],
        'role_model': [],
        'self_centred': [],
        'reserved': []
    }


def send_message_to_personality(personality_type: str, user_message: str):
    """Send message to a specific personality and get response"""
    if not st.session_state.manager_ready:
        return "System not ready"
    
    # Add user message to conversation
    st.session_state.conversations[personality_type].append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get personality response
    personality = st.session_state.manager.get_personality(personality_type)
    
    # Build context with problem
    context_messages = [{
        "role": "user",
        "content": f"We're working on this problem together: {st.session_state.current_problem['text']}\n\nMy message: {user_message}"
    }]
    
    # Add conversation history
    for msg in st.session_state.conversations[personality_type][-5:]:
        if msg["role"] == "assistant":
            context_messages.append({"role": "assistant", "content": msg["content"]})
    
    response = personality.chat(context_messages, max_tokens=512)
    
    # Add assistant response
    st.session_state.conversations[personality_type].append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })
    
    return response


def complete_problem():
    """Mark problem as completed and save to history"""
    if st.session_state.current_problem:
        st.session_state.current_problem['status'] = 'completed'
        st.session_state.current_problem['ended_at'] = datetime.now().isoformat()
        st.session_state.current_problem['conversations'] = dict(st.session_state.conversations)
        st.session_state.problem_history.append(st.session_state.current_problem)
        st.session_state.current_problem = None
        st.session_state.problem_id = None


def export_session():
    """Export current problem-solving session"""
    if not st.session_state.current_problem:
        return None
    
    export_data = {
        'problem': st.session_state.current_problem,
        'conversations': st.session_state.conversations,
        'exported_at': datetime.now().isoformat()
    }
    
    return json.dumps(export_data, indent=2)


# Main UI
st.title("🧩 Gerlach Collaborative Problem Solving")

if not st.session_state.manager_ready:
    st.error(f"❌ System Error: {st.session_state.manager_error}")
    st.info("Please set your ANTHROPIC_API_KEY environment variable and restart.")
    st.stop()

st.markdown("Collaborate with all four Gerlach personality types to solve problems together.")

# Sidebar - Problem Management
with st.sidebar:
    st.markdown("## 🎯 Problem Assignment")
    
    if st.session_state.current_problem:
        st.success(f"**Active Problem** (ID: {st.session_state.problem_id})")
        st.info(st.session_state.current_problem['text'])
        
        if st.button("✅ Complete Problem", use_container_width=True):
            complete_problem()
            st.rerun()
        
        if st.button("🗑️ Cancel Problem", use_container_width=True):
            st.session_state.current_problem = None
            st.session_state.problem_id = None
            st.rerun()
    else:
        st.markdown("### Start New Problem")
        problem_input = st.text_area(
            "Enter the problem to solve:",
            placeholder="e.g., How can we reduce plastic waste in our community?",
            height=100
        )
        
        if st.button("🚀 Start Collaboration", use_container_width=True, disabled=not problem_input):
            start_new_problem(problem_input)
            st.rerun()
    
    st.markdown("---")
    st.markdown("## 📊 Statistics")
    st.metric("Problems Solved", len(st.session_state.problem_history))
    
    if st.session_state.current_problem:
        total_messages = sum(len(conv) for conv in st.session_state.conversations.values())
        st.metric("Total Messages", total_messages)
    
    st.markdown("---")
    st.markdown("## 💾 Export")
    
    if st.session_state.current_problem:
        export_data = export_session()
        if export_data:
            st.download_button(
                "📥 Download Session",
                data=export_data,
                file_name=f"problem_{st.session_state.problem_id}.json",
                mime="application/json",
                use_container_width=True
            )

# Main content
if not st.session_state.current_problem:
    st.info("👈 Start a new problem from the sidebar to begin collaboration")
    
    # Show example problems
    st.markdown("### Example Problems")
    examples = [
        "How can we improve team communication in remote work environments?",
        "What strategies can help reduce personal carbon footprint?",
        "How should we approach learning a new programming language?",
        "What's the best way to organize a community event?",
        "How can we balance work and personal life effectively?"
    ]
    
    cols = st.columns(2)
    for idx, example in enumerate(examples):
        with cols[idx % 2]:
            if st.button(f"💡 {example[:50]}...", key=f"ex_{idx}"):
                start_new_problem(example)
                st.rerun()
    
    # Show history
    if st.session_state.problem_history:
        st.markdown("---")
        st.markdown("### 📚 Previous Problems")
        for prob in reversed(st.session_state.problem_history[-5:]):
            with st.expander(f"Problem {prob['id']}: {prob['text'][:60]}..."):
                st.markdown(f"**Started:** {prob['started_at']}")
                st.markdown(f"**Status:** {prob['status']}")
                total = sum(len(prob['conversations'][p]) for p in PERSONALITIES.keys())
                st.markdown(f"**Total Messages:** {total}")

else:
    # Active problem-solving interface
    st.markdown(f"### 🎯 Current Problem")
    st.markdown(
        f"<div style='background:#f0f2f6;padding:20px;border-radius:10px;margin-bottom:20px;'>"
        f"<h4 style='margin:0;'>{st.session_state.current_problem['text']}</h4>"
        f"<p style='margin:5px 0 0 0;color:#666;font-size:0.9em;'>Problem ID: {st.session_state.problem_id}</p>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    # Create 2x2 grid for personalities
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    personality_cols = [row1_col1, row1_col2, row2_col1, row2_col2]
    personality_keys = list(PERSONALITIES.keys())
    
    for idx, (ptype, col) in enumerate(zip(personality_keys, personality_cols)):
        info = PERSONALITIES[ptype]
        
        with col:
            # Personality header
            st.markdown(
                f"<div style='background:{info['color']};color:white;padding:12px;border-radius:8px;margin-bottom:10px;'>"
                f"<h4 style='margin:0;'>{info['emoji']} {info['name']}</h4>"
                f"<p style='margin:5px 0 0 0;font-size:0.85em;opacity:0.9;'>{info['description']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
            
            # Conversation display
            conversation_container = st.container()
            with conversation_container:
                if st.session_state.conversations[ptype]:
                    # Show last 6 messages (3 exchanges)
                    recent_messages = st.session_state.conversations[ptype][-6:]
                    
                    for msg in recent_messages:
                        if msg["role"] == "user":
                            st.markdown(
                                f"<div style='background:#e3f2fd;padding:8px;border-radius:6px;margin:5px 0;'>"
                                f"<b>You:</b> {msg['content']}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"<div style='background:#f5f5f5;padding:8px;border-radius:6px;margin:5px 0;'>"
                                f"<b>{info['name']}:</b> {msg['content']}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                    
                    if len(st.session_state.conversations[ptype]) > 6:
                        st.caption(f"({len(st.session_state.conversations[ptype]) - 6} earlier messages)")
                else:
                    st.caption("No messages yet. Start the conversation below.")
            
            # Input area
            with st.form(key=f"form_{ptype}", clear_on_submit=True):
                user_input = st.text_input(
                    f"Message to {info['name']}",
                    key=f"input_{ptype}",
                    placeholder=f"Ask {info['name']} for their perspective..."
                )
                submit = st.form_submit_button(f"Send to {info['emoji']}", use_container_width=True)
                
                if submit and user_input:
                    with st.spinner(f"{info['emoji']} Thinking..."):
                        send_message_to_personality(ptype, user_input)
                    st.rerun()
    
    # Summary section
    st.markdown("---")
    st.markdown("### 📝 Collaboration Summary")
    
    summary_cols = st.columns(4)
    for idx, (ptype, info) in enumerate(PERSONALITIES.items()):
        with summary_cols[idx]:
            msg_count = len([m for m in st.session_state.conversations[ptype] if m["role"] == "assistant"])
            st.metric(f"{info['emoji']} {info['name']}", f"{msg_count} responses")
