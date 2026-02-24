"""
Gerlach Personality Testing Interface
Test each personality individually to demonstrate their unique problem-solving approaches
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import uuid
from gerlach_personality_llms import GerlachPersonalityManager

st.set_page_config(
    page_title="Gerlach Personality Testing",
    page_icon="🧪",
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

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Personality configurations
PERSONALITIES = {
    "average": {
        "name": "Average",
        "emoji": "⚖️",
        "color": "#7570b3",
        "description": "Balanced & Practical",
        "traits": "Moderate across all Big Five traits - balanced, practical, flexible"
    },
    "role_model": {
        "name": "Role Model",
        "emoji": "⭐",
        "color": "#1b9e77",
        "description": "Optimistic & Organized",
        "traits": "Low Neuroticism, High E/O/A/C - enthusiastic, creative, cooperative, disciplined"
    },
    "self_centred": {
        "name": "Self-Centred",
        "emoji": "🎯",
        "color": "#d95f02",
        "description": "Direct & Competitive",
        "traits": "Low O/A/C - conventional, self-focused, competitive, direct"
    },
    "reserved": {
        "name": "Reserved",
        "emoji": "🤫",
        "color": "#e7298a",
        "description": "Calm & Conventional",
        "traits": "Low N/O - emotionally stable, introverted, routine-oriented, conventional"
    }
}


def start_new_session(personality_type: str, problem_text: str):
    """Start a new problem-solving session with one personality"""
    session_id = str(uuid.uuid4())[:8]
    st.session_state.current_session = {
        'session_id': session_id,
        'personality_type': personality_type,
        'personality_name': PERSONALITIES[personality_type]['name'],
        'problem': problem_text,
        'started_at': datetime.now().isoformat(),
        'status': 'active'
    }
    st.session_state.conversation = []


def end_session():
    """End current session and save to history"""
    if st.session_state.current_session:
        st.session_state.current_session['ended_at'] = datetime.now().isoformat()
        st.session_state.current_session['conversation'] = list(st.session_state.conversation)
        st.session_state.current_session['message_count'] = len([m for m in st.session_state.conversation if m['role'] == 'assistant'])
        st.session_state.all_sessions.append(st.session_state.current_session)
        st.session_state.current_session = None
        st.session_state.conversation = []


def send_message(user_message: str):
    """Send message to current personality and get response"""
    if not st.session_state.current_session:
        return
    
    personality_type = st.session_state.current_session['personality_type']
    problem = st.session_state.current_session['problem']
    
    # Add user message
    st.session_state.conversation.append({
        "role": "user",
        "content": user_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get personality response
    personality = st.session_state.manager.get_personality(personality_type)
    
    # Build context
    context_messages = [{
        "role": "user",
        "content": f"We're working on this problem: {problem}\n\nMy message: {user_message}"
    }]
    
    # Add recent conversation history
    for msg in st.session_state.conversation[-6:]:
        if msg["role"] == "assistant":
            context_messages.append({"role": "assistant", "content": msg["content"]})
    
    response = personality.chat(context_messages, max_tokens=512)
    
    # Add assistant response
    st.session_state.conversation.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })


def export_session(session):
    """Export a session as JSON"""
    return json.dumps(session, indent=2)


def get_sessions_by_problem(problem_text):
    """Get all sessions that worked on the same problem"""
    return [s for s in st.session_state.all_sessions if s['problem'] == problem_text]


# Main UI
st.title("🧪 Gerlach Personality Testing")

if not st.session_state.manager_ready:
    st.error(f"❌ System Error: {st.session_state.manager_error}")
    st.info("Please set your ANTHROPIC_API_KEY environment variable and restart.")
    st.stop()

st.markdown("""
Test each personality type individually to see how they uniquely approach problem-solving.
Each session focuses on **one personality** working with you on **one problem**.
""")

# Sidebar
with st.sidebar:
    st.markdown("## 🎯 Session Control")
    
    if st.session_state.current_session:
        session = st.session_state.current_session
        info = PERSONALITIES[session['personality_type']]
        
        st.markdown(
            f"<div style='background:{info['color']};color:white;padding:15px;border-radius:10px;'>"
            f"<h3 style='margin:0;'>{info['emoji']} {info['name']}</h3>"
            f"<p style='margin:5px 0 0 0;font-size:0.9em;'>{info['description']}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        st.markdown(f"**Problem:** {session['problem'][:100]}...")
        st.markdown(f"**Session ID:** {session['session_id']}")
        
        msg_count = len([m for m in st.session_state.conversation if m['role'] == 'assistant'])
        st.metric("Messages Exchanged", msg_count)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Complete", use_container_width=True):
                end_session()
                st.rerun()
        with col2:
            if st.button("🗑️ Cancel", use_container_width=True):
                st.session_state.current_session = None
                st.session_state.conversation = []
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 💾 Download Dialogue")
        
        # JSON export
        export_data = export_session({
            **st.session_state.current_session,
            'conversation': st.session_state.conversation
        })
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📄 JSON",
                data=export_data,
                file_name=f"dialogue_{session['session_id']}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Text export
        with col2:
            text_export = f"Dialogue Transcript\n"
            text_export += f"===================\n\n"
            text_export += f"Personality: {info['name']}\n"
            text_export += f"Problem: {session['problem']}\n"
            text_export += f"Session ID: {session['session_id']}\n"
            text_export += f"Started: {session['started_at']}\n\n"
            text_export += f"Conversation:\n"
            text_export += f"-------------\n\n"
            
            for msg in st.session_state.conversation:
                timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M:%S')
                role = "You" if msg['role'] == 'user' else info['name']
                text_export += f"[{timestamp}] {role}:\n{msg['content']}\n\n"
            
            st.download_button(
                "📝 TXT",
                data=text_export,
                file_name=f"dialogue_{session['session_id']}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    else:
        st.info("No active session. Start a new test below.")
        
        st.markdown("---")
        st.markdown("## 📊 Statistics")
        st.metric("Completed Sessions", len(st.session_state.all_sessions))
        
        if st.session_state.all_sessions:
            personality_counts = {}
            for s in st.session_state.all_sessions:
                ptype = s['personality_type']
                personality_counts[ptype] = personality_counts.get(ptype, 0) + 1
            
            st.markdown("### Sessions by Personality")
            for ptype, count in personality_counts.items():
                info = PERSONALITIES[ptype]
                st.markdown(f"{info['emoji']} {info['name']}: **{count}**")

# Main content
if not st.session_state.current_session:
    st.markdown("## 🚀 Start New Testing Session")
    
    st.markdown("### Step 1: Select Personality to Test")
    
    cols = st.columns(4)
    selected_personality = None
    
    for idx, (ptype, info) in enumerate(PERSONALITIES.items()):
        with cols[idx]:
            if st.button(
                f"{info['emoji']}\n{info['name']}",
                key=f"select_{ptype}",
                use_container_width=True,
                help=info['traits']
            ):
                selected_personality = ptype
    
    if 'selected_personality' not in st.session_state:
        st.session_state.selected_personality = None
    
    if selected_personality:
        st.session_state.selected_personality = selected_personality
    
    st.markdown("---")
    st.markdown("### Step 2: Define Problem")
    
    if st.session_state.selected_personality:
        info = PERSONALITIES[st.session_state.selected_personality]
        st.info(f"Selected: {info['emoji']} **{info['name']}** - {info['description']}")
    
    problem_input = st.text_area(
        "Enter the problem to solve:",
        placeholder="e.g., How can we improve team communication in remote work?",
        height=100,
        key="problem_input",
        disabled=not st.session_state.selected_personality
    )
    
    st.markdown("**Or choose an example:**")
    examples = [
        "How can we improve team communication in remote work environments?",
        "What strategies can help reduce personal carbon footprint?",
        "How should we approach learning a new programming language?",
        "What's the best way to organize a community event?",
        "How can we balance work and personal life effectively?"
    ]
    
    example_cols = st.columns(2)
    for idx, example in enumerate(examples):
        with example_cols[idx % 2]:
            if st.button(f"💡 {example[:50]}...", key=f"ex_{idx}", disabled=not st.session_state.selected_personality):
                st.session_state.problem_input = example
                st.rerun()
    
    st.markdown("---")
    
    if st.button("▶️ Start Session", type="primary", use_container_width=True, disabled=not (st.session_state.selected_personality and problem_input)):
        start_new_session(st.session_state.selected_personality, problem_input)
        st.session_state.selected_personality = None
        st.rerun()

else:
    # Active session
    session = st.session_state.current_session
    info = PERSONALITIES[session['personality_type']]
    
    st.markdown(
        f"<div style='background:{info['color']};color:white;padding:20px;border-radius:10px;margin-bottom:20px;'>"
        f"<h2 style='margin:0;'>{info['emoji']} Working with: {info['name']}</h2>"
        f"<p style='margin:10px 0 0 0;font-size:1.1em;'>{info['description']}</p>"
        f"<p style='margin:5px 0 0 0;font-size:0.9em;opacity:0.9;'>{info['traits']}</p>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    st.markdown(f"### 🎯 Problem")
    st.info(session['problem'])
    
    st.markdown("### 💬 Full Dialogue")
    
    # Display entire conversation as it progresses
    dialogue_container = st.container()
    with dialogue_container:
        if st.session_state.conversation:
            # Show all messages in chronological order
            for idx, msg in enumerate(st.session_state.conversation, 1):
                timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M:%S')
                
                if msg['role'] == 'user':
                    st.markdown(
                        f"<div style='background:#e3f2fd;padding:12px;border-radius:8px;margin:8px 0;'>"
                        f"<div style='font-size:0.85em;color:#666;margin-bottom:4px;'><b>You</b> • {timestamp}</div>"
                        f"<div>{msg['content']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='background:#f5f5f5;padding:12px;border-radius:8px;margin:8px 0;border-left:4px solid {info['color']};'>"
                        f"<div style='font-size:0.85em;color:#666;margin-bottom:4px;'><b>{info['emoji']} {info['name']}</b> • {timestamp}</div>"
                        f"<div>{msg['content']}</div>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
            
            # Show message count
            total_messages = len(st.session_state.conversation)
            user_messages = len([m for m in st.session_state.conversation if m['role'] == 'user'])
            assistant_messages = len([m for m in st.session_state.conversation if m['role'] == 'assistant'])
            
            st.caption(f"Total: {total_messages} messages ({user_messages} from you, {assistant_messages} from {info['name']})")
        else:
            st.caption(f"Start the conversation with {info['name']} about the problem.")
    
    # Input area
    user_input = st.chat_input(f"Message to {info['name']}...")
    
    if user_input:
        with st.spinner(f"{info['emoji']} {info['name']} is thinking..."):
            send_message(user_input)
        st.rerun()

# Comparison section
if st.session_state.all_sessions:
    st.markdown("---")
    st.markdown("## 📊 Session Analysis & Comparison")
    
    tab1, tab2, tab3 = st.tabs(["📚 All Sessions", "🔍 Compare by Problem", "📈 Personality Insights"])
    
    with tab1:
        st.markdown("### All Completed Sessions")
        
        for session in reversed(st.session_state.all_sessions):
            info = PERSONALITIES[session['personality_type']]
            
            with st.expander(
                f"{info['emoji']} {info['name']} - {session['problem'][:60]}... "
                f"({session['message_count']} messages)"
            ):
                st.markdown(f"**Session ID:** {session['session_id']}")
                st.markdown(f"**Started:** {session['started_at']}")
                st.markdown(f"**Ended:** {session['ended_at']}")
                st.markdown(f"**Problem:** {session['problem']}")
                
                st.markdown("**Conversation:**")
                for msg in session['conversation']:
                    role_label = "You" if msg['role'] == 'user' else info['name']
                    st.markdown(f"**{role_label}:** {msg['content']}")
                    st.markdown("---")
                
                export_data = export_session(session)
                st.download_button(
                    "📥 Download This Session",
                    data=export_data,
                    file_name=f"session_{session['session_id']}.json",
                    mime="application/json",
                    key=f"download_{session['session_id']}"
                )
    
    with tab2:
        st.markdown("### Compare Different Personalities on Same Problem")
        
        # Get unique problems
        unique_problems = list(set(s['problem'] for s in st.session_state.all_sessions))
        
        if unique_problems:
            selected_problem = st.selectbox("Select a problem:", unique_problems)
            
            problem_sessions = get_sessions_by_problem(selected_problem)
            
            if len(problem_sessions) > 1:
                st.success(f"Found {len(problem_sessions)} personalities that worked on this problem!")
                
                for session in problem_sessions:
                    info = PERSONALITIES[session['personality_type']]
                    
                    st.markdown(
                        f"<div style='border-left:4px solid {info['color']};padding-left:15px;margin:15px 0;'>"
                        f"<h4>{info['emoji']} {info['name']}'s Approach</h4>"
                        f"<p><strong>Messages:</strong> {session['message_count']}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    with st.expander(f"View {info['name']}'s conversation"):
                        for msg in session['conversation']:
                            role_label = "You" if msg['role'] == 'user' else info['name']
                            st.markdown(f"**{role_label}:** {msg['content']}")
                            st.markdown("---")
            else:
                st.info("Only one personality has worked on this problem. Try the same problem with other personalities to compare!")
        else:
            st.info("No completed sessions yet.")
    
    with tab3:
        st.markdown("### Personality-Specific Insights")
        
        if st.session_state.all_sessions:
            for ptype, info in PERSONALITIES.items():
                personality_sessions = [s for s in st.session_state.all_sessions if s['personality_type'] == ptype]
                
                if personality_sessions:
                    st.markdown(
                        f"<div style='background:{info['color']};color:white;padding:15px;border-radius:10px;margin:10px 0;'>"
                        f"<h4 style='margin:0;'>{info['emoji']} {info['name']}</h4>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    
                    total_messages = sum(s['message_count'] for s in personality_sessions)
                    avg_messages = total_messages / len(personality_sessions)
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Sessions", len(personality_sessions))
                    col2.metric("Total Messages", total_messages)
                    col3.metric("Avg Messages/Session", f"{avg_messages:.1f}")
                    
                    st.markdown("**Problems Solved:**")
                    for s in personality_sessions:
                        st.markdown(f"- {s['problem'][:80]}...")
        else:
            st.info("Complete some sessions to see personality insights.")
