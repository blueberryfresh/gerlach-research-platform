import streamlit as st
from datetime import datetime
from composite_big5_llms import CompositeBig5LLMManager
import json


def get_personality_styling():
    """Get styling information for each composite personality"""
    return {
        "collaborator": {
            "emoji": "🤝",
            "color": "#4ECDC4",
            "bg_color": "#E8F8F5",
            "description": "Team-oriented, reliable, organized, and cooperative"
        },
        "innovator": {
            "emoji": "💡",
            "color": "#FF6B6B",
            "bg_color": "#FFF5F5",
            "description": "Creative, confident, social, and adventurous"
        },
        "analyst": {
            "emoji": "🔬",
            "color": "#95A5A6",
            "bg_color": "#F8F9FA",
            "description": "Thoughtful, detail-oriented, intellectually curious"
        },
        "mediator": {
            "emoji": "☮️",
            "color": "#96CEB4",
            "bg_color": "#F0FDF4",
            "description": "Calm, empathetic, diplomatic, and balanced"
        },
        "driver": {
            "emoji": "⚡",
            "color": "#FFA500",
            "bg_color": "#FFF8DC",
            "description": "Assertive, goal-focused, competitive, results-driven"
        }
    }


def initialize_session_state():
    """Initialize session state"""
    if 'manager' not in st.session_state:
        st.session_state.manager = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}
    if 'selected_personality' not in st.session_state:
        st.session_state.selected_personality = None


def load_models():
    """Load composite personality models"""
    if st.session_state.manager is None:
        with st.spinner("🧠 Loading Composite Big5 Personality Models..."):
            try:
                st.session_state.manager = CompositeBig5LLMManager()
                st.success("✅ All composite personalities loaded!")
                return True
            except Exception as e:
                st.error(f"Error loading models: {e}")
                return False
    return True


def display_personality_cards():
    """Display personality selection cards"""
    st.markdown("## 🎭 Select a Composite Personality")
    
    styling = get_personality_styling()
    
    cols = st.columns(3)
    
    personalities = list(styling.keys())
    
    for i, personality_key in enumerate(personalities):
        with cols[i % 3]:
            style = styling[personality_key]
            config = st.session_state.manager.get_personality_info(personality_key)
            
            # Create personality card
            st.markdown(f"""
            <div style="
                border: 3px solid {style['color']};
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                background-color: {style['bg_color']};
                text-align: center;
            ">
                <h2 style="color: {style['color']}; margin: 0;">
                    {style['emoji']} {config.name}
                </h2>
                <p style="margin: 10px 0; font-weight: bold; color: #333;">
                    {style['description']}
                </p>
                <p style="margin: 5px 0; font-size: 0.9em; color: #666;">
                    <strong>Traits:</strong> {', '.join(config.key_traits[:3])}
                </p>
                <p style="margin: 5px 0; font-size: 0.85em; color: #888;">
                    O:{config.openness:.1f} C:{config.conscientiousness:.1f} 
                    E:{config.extraversion:.1f} A:{config.agreeableness:.1f} N:{config.neuroticism:.1f}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Chat with {config.name}", key=f"select_{personality_key}", use_container_width=True):
                st.session_state.selected_personality = personality_key
                if personality_key not in st.session_state.chat_history:
                    st.session_state.chat_history[personality_key] = []
                st.rerun()


def display_chat_interface():
    """Display chat interface for selected personality"""
    personality_key = st.session_state.selected_personality
    styling = get_personality_styling()
    style = styling[personality_key]
    config = st.session_state.manager.get_personality_info(personality_key)
    
    # Header
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {style['color']}, {style['bg_color']});
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h1 style="margin: 0; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            {style['emoji']} {config.name}
        </h1>
        <p style="margin: 10px 0; color: white; font-size: 1.1em;">
            {style['description']}
        </p>
        <p style="margin: 5px 0; color: white; font-size: 0.9em;">
            Key Traits: {', '.join(config.key_traits)}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Controls
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Selection"):
            st.session_state.selected_personality = None
            st.rerun()
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history[personality_key] = []
            st.rerun()
    
    # Chat history
    st.markdown("### 💬 Conversation")
    
    if personality_key in st.session_state.chat_history and st.session_state.chat_history[personality_key]:
        for message in st.session_state.chat_history[personality_key]:
            if message['role'] == 'user':
                st.markdown(f"""
                <div style="
                    background-color: #E3F2FD;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    margin-left: 50px;
                    border-left: 4px solid #2196F3;
                ">
                    <strong>You:</strong> {message['content']}
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                        {message['timestamp']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background-color: {style['bg_color']};
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    margin-right: 50px;
                    border-left: 4px solid {style['color']};
                ">
                    <strong>{style['emoji']} {config.name}:</strong> {message['content']}
                    <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                        {message['timestamp']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(f"Start a conversation with {config.name}! Ask about work, leadership, problem-solving, or any topic.")
    
    # Input area
    st.markdown("### ✍️ Your Message")
    
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Type your message:",
            height=100,
            placeholder=f"Ask {config.name} about their approach to challenges, teamwork, decision-making, etc."
        )
        
        send_button = st.form_submit_button("Send 📤", use_container_width=True)
    
    if send_button and user_input.strip():
        # Add user message
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history[personality_key].append({
            'role': 'user',
            'content': user_input.strip(),
            'timestamp': timestamp
        })
        
        # Generate response
        with st.spinner(f"🤔 {config.name} is thinking..."):
            try:
                response = st.session_state.manager.get_response(personality_key, user_input.strip())
                
                ai_timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.chat_history[personality_key].append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': ai_timestamp
                })
                
            except Exception as e:
                st.error(f"Error: {e}")
        
        st.rerun()
    
    # Stats
    if personality_key in st.session_state.chat_history:
        message_count = len(st.session_state.chat_history[personality_key])
        if message_count > 0:
            st.markdown(f"""
            <div style="
                background-color: #F5F5F5;
                padding: 10px;
                border-radius: 5px;
                margin-top: 20px;
                text-align: center;
                font-size: 0.9em;
            ">
                💬 {message_count} messages in this conversation
            </div>
            """, unsafe_allow_html=True)


def display_comparison_mode():
    """Display comparison mode"""
    st.markdown("## 🔍 Compare All Composite Personalities")
    st.markdown("See how each personality type responds to the same question!")
    
    with st.form("comparison_form"):
        comparison_question = st.text_area(
            "Enter a question for all personalities:",
            height=100,
            placeholder="e.g., 'How do you handle team conflicts?' or 'What's your approach to innovation?'"
        )
        
        compare_button = st.form_submit_button("🎭 Get All Responses", use_container_width=True)
    
    if compare_button and comparison_question.strip():
        st.markdown("### 🎭 Responses from All Personalities")
        
        styling = get_personality_styling()
        
        with st.spinner("Getting responses..."):
            try:
                responses = st.session_state.manager.get_all_responses(comparison_question.strip())
                
                for personality_key, response in responses.items():
                    style = styling[personality_key]
                    config = st.session_state.manager.get_personality_info(personality_key)
                    
                    with st.expander(f"{style['emoji']} {config.name} - {style['description']}", expanded=True):
                        st.markdown(f"""
                        <div style="
                            background-color: {style['bg_color']};
                            padding: 15px;
                            border-radius: 10px;
                            border-left: 4px solid {style['color']};
                        ">
                            <strong>Response:</strong><br>{response}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"**Key Traits:** {', '.join(config.key_traits)}")
                
            except Exception as e:
                st.error(f"Error: {e}")


def main():
    """Main application"""
    st.set_page_config(
        page_title="Composite Big5 Personalities",
        page_icon="🎭",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
    }
    </style>
    """, unsafe_allow_html=True)
    
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("# 🎭 Composite Big5 LLMs")
        st.markdown("---")
        
        mode = st.radio(
            "Select Mode:",
            ["💬 Individual Chat", "🔍 Compare All"],
            key="mode"
        )
        
        st.markdown("---")
        st.markdown("## 📚 About Composite Personalities")
        st.markdown("""
        These personalities combine multiple Big Five traits:
        
        - **🤝 Collaborator**: Team player + Organized
        - **💡 Innovator**: Creative + Confident + Social
        - **🔬 Analyst**: Thorough + Intellectual + Reflective
        - **☮️ Mediator**: Empathetic + Calm + Balanced
        - **⚡ Driver**: Assertive + Results-focused + Ambitious
        """)
        
        st.markdown("---")
        st.markdown("## 💡 Test Questions")
        st.markdown("""
        - How do you handle team conflicts?
        - What's your leadership style?
        - How do you approach innovation?
        - How do you make tough decisions?
        - What motivates you at work?
        """)
    
    # Main content
    st.title("🎭 Composite Big5 Personality LLMs")
    st.markdown("Interact with AI personalities that combine multiple psychological traits!")
    
    if not load_models():
        st.stop()
    
    if mode == "💬 Individual Chat":
        if st.session_state.selected_personality is None:
            display_personality_cards()
        else:
            display_chat_interface()
    else:
        display_comparison_mode()


if __name__ == "__main__":
    main()
