"""
Gerlach (2018) Four Personality Types - Main Application
Interactive app presenting and allowing interaction with all four personality types
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
try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


MAX_TASK_DOC_CHARS = 12000
TASK_FOLDER = Path(__file__).parent / "Task"

st.set_page_config(
    page_title="Gerlach (2018) Personality Types",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Personality configurations with detailed information
PERSONALITY_INFO = {
    "average": {
        "name": "Average",
        "emoji": "⚖️",
        "color": "#7570b3",
        "description": "Average scores across all Big Five traits",
        "big5": {
            "Neuroticism": "Average",
            "Extraversion": "Average",
            "Openness": "Average",
            "Agreeableness": "Average",
            "Conscientiousness": "Average"
        },
        "characteristics": [
            "Balanced and moderate in all responses",
            "Avoids extremes in behavior and language",
            "Practical and grounded, showing common sense",
            "Reasonably organized but flexible",
            "Represents the most common personality pattern"
        ]
    },
    "role_model": {
        "name": "Role Model",
        "emoji": "⭐",
        "color": "#1b9e77",
        "description": "Low Neuroticism, High on all other traits (socially desirable)",
        "big5": {
            "Neuroticism": "Low",
            "Extraversion": "High",
            "Openness": "High",
            "Agreeableness": "High",
            "Conscientiousness": "High"
        },
        "characteristics": [
            "Emotionally stable and resilient",
            "Highly social, energetic, and enthusiastic",
            "Creative and intellectually curious",
            "Cooperative, empathetic, and caring",
            "Highly organized and reliable"
        ]
    },
    "self_centred": {
        "name": "Self-Centred",
        "emoji": "🎯",
        "color": "#d95f02",
        "description": "Low Openness, Agreeableness, and Conscientiousness",
        "big5": {
            "Neuroticism": "Moderate to High",
            "Extraversion": "Moderate to High",
            "Openness": "Low",
            "Agreeableness": "Low",
            "Conscientiousness": "Low"
        },
        "characteristics": [
            "Prioritizes own interests and perspectives",
            "Conventional and prefers familiar approaches",
            "Competitive and assertive",
            "Direct and blunt communication style",
            "Less concerned with organization"
        ]
    },
    "reserved": {
        "name": "Reserved",
        "emoji": "🤫",
        "color": "#e7298a",
        "description": "Low Neuroticism and Openness (calm, conventional, introverted)",
        "big5": {
            "Neuroticism": "Low",
            "Extraversion": "Low to Moderate",
            "Openness": "Low",
            "Agreeableness": "Moderate",
            "Conscientiousness": "Moderate"
        },
        "characteristics": [
            "Emotionally stable but quiet and reserved",
            "Prefers familiar routines and conventional approaches",
            "Introverted and prefers limited social interaction",
            "Practical and grounded, avoiding abstract speculation",
            "Calm and composed, rarely showing strong emotions"
        ]
    }
}

# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = None
    st.session_state.manager_ready = False
    st.session_state.manager_error = None
    
    # Try to initialize manager (lazy loading - only when needed)
    try:
        import os
        if os.environ.get("ANTHROPIC_API_KEY"):
            st.session_state.manager = GerlachPersonalityManager()
            st.session_state.manager_ready = True
        else:
            st.session_state.manager_error = "ANTHROPIC_API_KEY not set in environment"
    except Exception as e:
        st.session_state.manager_error = str(e)

if 'current_personality' not in st.session_state:
    st.session_state.current_personality = None

if 'task_doc_text' not in st.session_state:
    st.session_state.task_doc_text = ""

if 'task_doc_name' not in st.session_state:
    st.session_state.task_doc_name = None

if 'selected_task' not in st.session_state:
    st.session_state.selected_task = None

if 'selected_llm' not in st.session_state:
    st.session_state.selected_llm = None

if 'chat_sessions' not in st.session_state:
    st.session_state.chat_sessions = {}

if 'current_messages' not in st.session_state:
    st.session_state.current_messages = {}


def load_task_from_file(task_path: Path) -> str:
    """Load task text from file (supports .txt, .md, .pdf)"""
    try:
        if task_path.suffix.lower() == '.pdf':
            if not PDF_AVAILABLE:
                return "Error: PyPDF2 not installed. Run: pip install PyPDF2"
            reader = PdfReader(str(task_path))
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            return "\n".join(text_parts).strip()
        else:
            with open(task_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read().strip()
    except Exception as e:
        return f"Error loading task: {e}"


def get_available_tasks() -> list:
    """Scan Task folder and return list of available task files"""
    if not TASK_FOLDER.exists():
        return []
    task_files = []
    for ext in ['*.txt', '*.md', '*.pdf']:
        task_files.extend(TASK_FOLDER.glob(ext))
    return sorted([f.name for f in task_files])


def start_chat(personality_type: str):
    """Start a new chat session with a personality"""
    if personality_type not in st.session_state.chat_sessions:
        session_id = str(uuid.uuid4())[:8]
        st.session_state.chat_sessions[personality_type] = ConversationSession(
            personality_type=personality_type,
            session_id=session_id,
            messages=[],
            started_at=datetime.now().isoformat(),
            metadata={
                "personality_name": PERSONALITY_INFO[personality_type]["name"]
            }
        )
        st.session_state.current_messages[personality_type] = []
    st.session_state.current_personality = personality_type


def send_message(personality_type: str, user_message: str):
    """Send a message and get response from personality"""
    # Initialize manager if not ready
    if not st.session_state.manager_ready:
        try:
            st.session_state.manager = GerlachPersonalityManager()
            st.session_state.manager_ready = True
            st.session_state.manager_error = None
        except Exception as e:
            st.session_state.manager_error = str(e)
            st.error(f"Failed to initialize: {e}")
            return
    
    if personality_type not in st.session_state.chat_sessions:
        start_chat(personality_type)
    
    session = st.session_state.chat_sessions[personality_type]
    personality = st.session_state.manager.get_personality(personality_type)
    
    # Add user message
    user_msg = Message(role="user", content=user_message)
    session.messages.append(user_msg)
    st.session_state.current_messages[personality_type].append({
        "role": "user",
        "content": user_message
    })
    
    # Convert to Claude format
    claude_messages = []

    task_doc_text = (st.session_state.task_doc_text or "").strip()
    if task_doc_text:
        claude_messages.append({
            "role": "user",
            "content": f"Task document (shared context for us to work on together):\n\n{task_doc_text}"
        })

    claude_messages.extend(
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.current_messages[personality_type]
    )
    
    # Get AI response
    response = personality.chat(claude_messages)
    
    # Add assistant message
    assistant_msg = Message(role="assistant", content=response)
    session.messages.append(assistant_msg)
    st.session_state.current_messages[personality_type].append({
        "role": "assistant",
        "content": response
    })


def display_personality_card(personality_type: str, info: dict):
    """Display a personality information card"""
    st.markdown(
        f"""
        <div style='
            border: 3px solid {info["color"]};
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            background: linear-gradient(135deg, {info["color"]}15 0%, {info["color"]}05 100%);
            transition: transform 0.2s;
        '>
            <h2 style='color: {info["color"]}; margin: 0 0 10px 0;'>
                {info["emoji"]} {info["name"]}
            </h2>
            <p style='color: #666; margin: 0 0 15px 0; font-size: 1.1em;'>
                {info["description"]}
            </p>
            <div style='margin: 15px 0;'>
                <strong style='color: {info["color"]};'>Big Five Profile:</strong>
                <ul style='margin: 5px 0; padding-left: 20px;'>
        """,
        unsafe_allow_html=True
    )
    
    for trait, level in info["big5"].items():
        st.markdown(f"- **{trait}:** {level}")
    
    st.markdown("</ul></div>", unsafe_allow_html=True)
    
    st.markdown(
        f"""
        <div style='margin: 15px 0;'>
            <strong style='color: {info["color"]};'>Key Characteristics:</strong>
            <ul style='margin: 5px 0; padding-left: 20px;'>
        """,
        unsafe_allow_html=True
    )
    
    for char in info["characteristics"]:
        st.markdown(f"- {char}")
    
    st.markdown("</ul></div></div>", unsafe_allow_html=True)


# Main UI
st.title("🧭 Gerlach (2018) Four Personality Types")
st.markdown(
    """
    **Interactive application based on Gerlach et al. (2018) research**
    
    This app presents the four robust personality types identified through analysis of over 1.5 million participants 
    across four large datasets. Each personality type is supported, strengthened, and reinforced by its unique nature.
    """
)

# Show API key setup if needed (but don't block the app from loading)
if not st.session_state.manager_ready:
    st.warning("⚠️ **API Key Not Set** - The app will load, but you'll need to set your API key to chat with personalities.")
    with st.expander("🔑 How to Set Your API Key", expanded=True):
        st.markdown("""
        **Option 1: Set in Terminal/Command Prompt (Recommended)**
        
        **Windows (PowerShell):**
        ```powershell
        $env:ANTHROPIC_API_KEY="your-api-key-here"
        ```
        
        **Windows (Command Prompt):**
        ```cmd
        set ANTHROPIC_API_KEY=your-api-key-here
        ```
        
        **Mac/Linux:**
        ```bash
        export ANTHROPIC_API_KEY="your-api-key-here"
        ```
        
        Then restart the app.
        
        **Option 2: Set in Streamlit (Temporary)**
        """)
        
        api_key_input = st.text_input(
            "Enter your Anthropic API Key:",
            type="password",
            help="This will be stored in session state (temporary)"
        )
        
        if api_key_input:
            import os
            os.environ["ANTHROPIC_API_KEY"] = api_key_input
            try:
                st.session_state.manager = GerlachPersonalityManager()
                st.session_state.manager_ready = True
                st.session_state.manager_error = None
                st.success("✅ API Key set! You can now chat with personalities.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to initialize: {e}")
                st.session_state.manager_error = str(e)
    
    st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## 🤖 Select LLM Personality")
    
    llm_options = list(PERSONALITY_INFO.keys())
    llm_display_names = [f"{PERSONALITY_INFO[p]['emoji']} {PERSONALITY_INFO[p]['name']}" for p in llm_options]
    
    selected_llm_idx = st.selectbox(
        "Choose personality for this session:",
        range(len(llm_options)),
        format_func=lambda i: llm_display_names[i],
        index=llm_options.index(st.session_state.selected_llm) if st.session_state.selected_llm in llm_options else 0,
        key="llm_selector"
    )
    
    selected_llm = llm_options[selected_llm_idx]
    
    if st.session_state.selected_llm != selected_llm:
        st.session_state.selected_llm = selected_llm
        if st.session_state.current_personality != selected_llm:
            st.session_state.current_personality = selected_llm
            start_chat(selected_llm)
            st.rerun()

    st.markdown("---")
    st.markdown("## 📄 Select Task")
    
    available_tasks = get_available_tasks()
    
    if available_tasks:
        task_options = ["(No task selected)"] + available_tasks
        
        current_task_idx = 0
        if st.session_state.selected_task and st.session_state.selected_task in available_tasks:
            current_task_idx = available_tasks.index(st.session_state.selected_task) + 1
        
        selected_task_idx = st.selectbox(
            "Choose a task to work on:",
            range(len(task_options)),
            format_func=lambda i: task_options[i],
            index=current_task_idx,
            key="task_selector"
        )
        
        if selected_task_idx > 0:
            selected_task = available_tasks[selected_task_idx - 1]
            
            if st.session_state.selected_task != selected_task:
                st.session_state.selected_task = selected_task
                task_path = TASK_FOLDER / selected_task
                task_text = load_task_from_file(task_path)
                
                if len(task_text) > MAX_TASK_DOC_CHARS:
                    task_text = task_text[:MAX_TASK_DOC_CHARS]
                    st.warning(f"Task truncated to {MAX_TASK_DOC_CHARS} characters.")
                
                st.session_state.task_doc_text = task_text
                st.session_state.task_doc_name = selected_task
                st.rerun()
        else:
            if st.session_state.selected_task is not None:
                st.session_state.selected_task = None
                st.session_state.task_doc_text = ""
                st.session_state.task_doc_name = None
                st.rerun()
    else:
        st.warning("No tasks found in Task/ folder")
    
    if (st.session_state.task_doc_text or "").strip():
        st.success(f"✓ Loaded: {st.session_state.task_doc_name}")
        with st.expander("📖 Preview task text"):
            preview_text = st.session_state.task_doc_text
            if len(preview_text) > 500:
                preview_text = preview_text[:500] + "\n\n... (truncated for preview)"
            st.text_area(
                "Task content",
                value=preview_text,
                height=200,
                key="task_doc_preview",
                disabled=True
            )
    
    st.markdown("---")
    st.markdown("## 📊 Statistics")
    
    total_messages = sum(len(session.messages) for session in st.session_state.chat_sessions.values())
    st.metric("Total Conversations", len(st.session_state.chat_sessions))
    st.metric("Total Messages", total_messages)
    
    if st.session_state.current_personality:
        current_session = st.session_state.chat_sessions.get(st.session_state.current_personality)
        if current_session:
            st.metric("Current Messages", len(current_session.messages))

# Main content area
if st.session_state.current_personality:
    # Chat interface
    personality_type = st.session_state.current_personality
    info = PERSONALITY_INFO[personality_type]
    
    # Header
    st.markdown(
        f"""
        <div style='
            background: linear-gradient(135deg, {info["color"]} 0%, {info["color"]}dd 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        '>
            <h2 style='margin: 0 0 10px 0;'>
                {info["emoji"]} Chatting with: {info["name"]}
            </h2>
            <p style='margin: 0; opacity: 0.95; font-size: 1.1em;'>
                {info["description"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Chat messages
    chat_container = st.container()
    with chat_container:
        if personality_type in st.session_state.current_messages:
            for msg in st.session_state.current_messages[personality_type]:
                if msg["role"] == "user":
                    st.chat_message("user").write(msg["content"])
                else:
                    with st.chat_message("assistant", avatar=info["emoji"]):
                        st.write(msg["content"])
    
    # Chat input
    user_input = st.chat_input(f"Type your message to {info['name']}...")
    
    if user_input:
        if not st.session_state.manager_ready:
            st.error("⚠️ Please set your API key first (see instructions at the top of the page)")
        else:
            with st.spinner(f"{info['emoji']} {info['name']} is thinking..."):
                send_message(personality_type, user_input)
            st.rerun()
    
    # Personality details expander
    with st.expander(f"📋 View {info['name']} Personality Details"):
        display_personality_card(personality_type, info)

else:
    # Landing page - show all personalities
    st.markdown("## 👥 The Four Personality Types")
    st.markdown(
        """
        Based on Gerlach et al. (2018) research analyzing over 1.5 million participants, 
        these four personality types represent robust clusters in the Big Five personality space.
        """
    )
    
    st.markdown("---")
    
    # Display all personality cards
    cols = st.columns(2)
    for idx, (ptype, info) in enumerate(PERSONALITY_INFO.items()):
        with cols[idx % 2]:
            display_personality_card(ptype, info)
    
    st.markdown("---")
    
    st.info(
        "👈 **Get Started:** Select a personality type from the sidebar to start a conversation. "
        "Each personality will respond according to its unique nature and characteristics."
    )
    
    # Research citation
    st.markdown("---")
    st.markdown("### 📚 Research Citation")
    st.markdown(
        """
        **Gerlach, M., Farb, B., Revelle, W., & Nunes Amaral, L. A. (2018).** 
        A robust data-driven approach identifies four personality types across four large data sets. 
        *Nature Human Behaviour*, 2(10), 735-742.
        
        [DOI: 10.1038/s41562-018-0419-z](https://doi.org/10.1038/s41562-018-0419-z)
        """
    )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    "Gerlach (2018) Personality Types Application | "
    "Each personality is supported, strengthened, and reinforced by its unique nature"
    "</div>",
    unsafe_allow_html=True
)

