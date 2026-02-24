import streamlit as st
import sys
import time
from datetime import datetime
from improved_big5_llms import ImprovedBig5LLMManager
import json


def initialize_session_state():
    """Initialize session state variables"""
    if 'manager' not in st.session_state:
        st.session_state.manager = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = {}
    if 'selected_personality' not in st.session_state:
        st.session_state.selected_personality = None
    if 'conversation_count' not in st.session_state:
        st.session_state.conversation_count = 0


def load_models():
    """Load the Big5 personality models"""
    if st.session_state.manager is None:
        with st.spinner("🧠 Loading Big5 Personality Models... Please wait..."):
            try:
                st.session_state.manager = ImprovedBig5LLMManager()
                st.success("✅ All personality models loaded successfully!")
                return True
            except Exception as e:
                st.error(f"❌ Error loading models: {e}")
                return False
    return True


def get_personality_info():
    """Get personality information and styling"""
    return {
        "openness": {
            "name": "Openness",
            "emoji": "🎨",
            "description": "Creative & Curious",
            "traits": "Imaginative, artistic, curious, creative, unconventional",
            "color": "#FF6B6B",
            "bg_color": "#FFF5F5"
        },
        "conscientiousness": {
            "name": "Conscientiousness", 
            "emoji": "📋",
            "description": "Organized & Disciplined",
            "traits": "Organized, responsible, disciplined, systematic, efficient",
            "color": "#4ECDC4",
            "bg_color": "#F0FDFC"
        },
        "extraversion": {
            "name": "Extraversion",
            "emoji": "🎉", 
            "description": "Social & Energetic",
            "traits": "Outgoing, energetic, talkative, assertive, social",
            "color": "#45B7D1",
            "bg_color": "#F0F9FF"
        },
        "agreeableness": {
            "name": "Agreeableness",
            "emoji": "🤝",
            "description": "Cooperative & Trusting", 
            "traits": "Cooperative, trusting, helpful, empathetic, considerate",
            "color": "#96CEB4",
            "bg_color": "#F0FDF4"
        },
        "neuroticism": {
            "name": "Neuroticism",
            "emoji": "😰",
            "description": "Emotional & Anxious",
            "traits": "Anxious, moody, worrying, sensitive, stressed",
            "color": "#FECA57",
            "bg_color": "#FFFBEB"
        }
    }


def display_personality_selector():
    """Display personality selection interface"""
    st.markdown("## 🎭 Select a Personality to Chat With")
    
    personalities = get_personality_info()
    
    # Create columns for personality cards
    cols = st.columns(3)
    
    for i, (key, info) in enumerate(personalities.items()):
        with cols[i % 3]:
            # Create a styled card for each personality
            card_html = f"""
            <div style="
                border: 2px solid {info['color']};
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background-color: {info['bg_color']};
                text-align: center;
                cursor: pointer;
            ">
                <h3 style="color: {info['color']}; margin: 0;">
                    {info['emoji']} {info['name']}
                </h3>
                <p style="margin: 5px 0; font-weight: bold;">
                    {info['description']}
                </p>
                <p style="margin: 5px 0; font-size: 0.9em; color: #666;">
                    {info['traits']}
                </p>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            if st.button(f"Chat with {info['name']}", key=f"select_{key}", use_container_width=True):
                st.session_state.selected_personality = key
                if key not in st.session_state.chat_history:
                    st.session_state.chat_history[key] = []
                st.rerun()


def display_chat_interface():
    """Display the chat interface for the selected personality"""
    personality_key = st.session_state.selected_personality
    personalities = get_personality_info()
    personality = personalities[personality_key]
    
    # Header with personality info
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, {personality['color']}, {personality['bg_color']});
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    ">
        <h2 style="margin: 0; color: white;">
            {personality['emoji']} Chatting with {personality['name']}
        </h2>
        <p style="margin: 5px 0; color: white; opacity: 0.9;">
            {personality['description']} | {personality['traits']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button and clear chat
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("← Back to Selection", key="back_button"):
            st.session_state.selected_personality = None
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history[personality_key] = []
            st.rerun()
    
    # Chat history display
    st.markdown("### 💬 Conversation")
    
    chat_container = st.container()
    
    with chat_container:
        if personality_key in st.session_state.chat_history:
            for i, message in enumerate(st.session_state.chat_history[personality_key]):
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div style="
                        background-color: #E3F2FD;
                        padding: 10px;
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
                        background-color: {personality['bg_color']};
                        padding: 10px;
                        border-radius: 10px;
                        margin: 10px 0;
                        margin-right: 50px;
                        border-left: 4px solid {personality['color']};
                    ">
                        <strong>{personality['emoji']} {personality['name']}:</strong> {message['content']}
                        <div style="font-size: 0.8em; color: #666; margin-top: 5px;">
                            {message['timestamp']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("### ✍️ Your Message")
    
    # Use form to handle enter key
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Type your message here...", 
            height=100,
            placeholder=f"Ask {personality['name']} anything! Try questions about emotions, decisions, or life perspectives."
        )
        
        col1, col2 = st.columns([3, 1])
        with col2:
            send_button = st.form_submit_button("Send 📤", use_container_width=True)
    
    # Handle message sending
    if send_button and user_input.strip():
        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.chat_history[personality_key].append({
            'role': 'user',
            'content': user_input.strip(),
            'timestamp': timestamp
        })
        
        # Generate AI response
        with st.spinner(f"🤔 {personality['name']} is thinking..."):
            try:
                response = st.session_state.manager.get_response(personality_key, user_input.strip())
                
                # Add AI response to history
                ai_timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.chat_history[personality_key].append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': ai_timestamp
                })
                
                st.session_state.conversation_count += 1
                
            except Exception as e:
                st.error(f"Error generating response: {e}")
        
        st.rerun()
    
    # Conversation statistics
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
                color: #666;
            ">
                💬 {message_count} messages in this conversation | 
                🎯 Total conversations: {st.session_state.conversation_count}
            </div>
            """, unsafe_allow_html=True)


def display_comparison_mode():
    """Display comparison mode where all personalities respond to the same question"""
    st.markdown("## 🔍 Personality Comparison Mode")
    st.markdown("Ask the same question to all five personalities and see how they differ!")
    
    with st.form("comparison_form", clear_on_submit=True):
        comparison_question = st.text_area(
            "Enter a question for all personalities:",
            height=100,
            placeholder="e.g., 'How do you handle stress?' or 'What motivates you in life?'"
        )
        
        compare_button = st.form_submit_button("🎭 Get All Responses", use_container_width=True)
    
    if compare_button and comparison_question.strip():
        st.markdown("### 🎭 Responses from All Personalities")
        
        personalities = get_personality_info()
        
        with st.spinner("🤔 Getting responses from all personalities..."):
            try:
                responses = st.session_state.manager.get_all_responses(comparison_question.strip())
                
                for personality_key, response in responses.items():
                    if personality_key in personalities:
                        personality = personalities[personality_key]
                        
                        with st.expander(f"{personality['emoji']} {personality['name']} - {personality['description']}", expanded=True):
                            st.markdown(f"""
                            <div style="
                                background-color: {personality['bg_color']};
                                padding: 15px;
                                border-radius: 10px;
                                border-left: 4px solid {personality['color']};
                            ">
                                <strong>Question:</strong> {comparison_question.strip()}<br><br>
                                <strong>Response:</strong> {response}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Quick personality trait analysis
                            st.markdown(f"**Expected Traits:** {personality['traits']}")
                
            except Exception as e:
                st.error(f"Error generating responses: {e}")


def display_sidebar():
    """Display sidebar with additional information and controls"""
    with st.sidebar:
        st.markdown("# 🧠 Big5 Personality LLMs")
        st.markdown("---")
        
        # Mode selection
        st.markdown("## 🎯 Mode Selection")
        mode = st.radio(
            "Choose your interaction mode:",
            ["💬 Individual Chat", "🔍 Compare All Personalities"],
            key="mode_selection"
        )
        
        st.markdown("---")
        
        # Personality information
        st.markdown("## 📚 About the Big Five")
        
        personalities = get_personality_info()
        for key, info in personalities.items():
            with st.expander(f"{info['emoji']} {info['name']}"):
                st.markdown(f"**Description:** {info['description']}")
                st.markdown(f"**Key Traits:** {info['traits']}")
        
        st.markdown("---")
        
        # Tips and suggestions
        st.markdown("## 💡 Testing Tips")
        st.markdown("""
        **Good Questions to Ask:**
        - How do you handle stress?
        - What motivates you?
        - How do you make decisions?
        - What's your ideal weekend?
        - How do you deal with conflict?
        - What are your biggest fears?
        - How do you approach new challenges?
        """)
        
        st.markdown("---")
        
        # Export chat history
        if st.session_state.chat_history:
            st.markdown("## 📥 Export Chat")
            if st.button("Download Chat History"):
                chat_data = json.dumps(st.session_state.chat_history, indent=2)
                st.download_button(
                    label="💾 Download JSON",
                    data=chat_data,
                    file_name=f"big5_chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        return mode


def main():
    """Main application function"""
    st.set_page_config(
        page_title="Big5 Personality LLMs Chat",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #FAFAFA;
    }
    .stButton > button {
        border-radius: 10px;
        border: none;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stTextArea > div > div > textarea {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar and get mode
    mode = display_sidebar()
    
    # Main content area
    st.title("🧠 Big Five Personality LLMs Interactive Chat")
    st.markdown("Experience conversations with AI personalities based on psychological research!")
    
    # Load models
    if not load_models():
        st.stop()
    
    # Display appropriate interface based on mode
    if mode == "💬 Individual Chat":
        if st.session_state.selected_personality is None:
            display_personality_selector()
        else:
            display_chat_interface()
    else:  # Compare All Personalities mode
        display_comparison_mode()


if __name__ == "__main__":
    main()
