import streamlit as st
import sys
import time
from datetime import datetime

# Simple error handling for imports
try:
    from improved_big5_llms import ImprovedBig5LLMManager
    MODELS_AVAILABLE = True
except Exception as e:
    st.error(f"Error importing models: {e}")
    MODELS_AVAILABLE = False


def get_personality_info():
    """Get personality information"""
    return {
        "openness": {
            "name": "Openness",
            "emoji": "🎨",
            "description": "Creative & Curious",
            "color": "#FF6B6B"
        },
        "conscientiousness": {
            "name": "Conscientiousness", 
            "emoji": "📋",
            "description": "Organized & Disciplined",
            "color": "#4ECDC4"
        },
        "extraversion": {
            "name": "Extraversion",
            "emoji": "🎉", 
            "description": "Social & Energetic",
            "color": "#45B7D1"
        },
        "agreeableness": {
            "name": "Agreeableness",
            "emoji": "🤝",
            "description": "Cooperative & Trusting", 
            "color": "#96CEB4"
        },
        "neuroticism": {
            "name": "Neuroticism",
            "emoji": "😰",
            "description": "Emotional & Anxious",
            "color": "#FECA57"
        }
    }


def initialize_models():
    """Initialize the Big5 models with error handling"""
    if 'manager' not in st.session_state:
        if not MODELS_AVAILABLE:
            st.error("Models are not available. Please check the installation.")
            return False
        
        try:
            with st.spinner("🧠 Loading Big5 Personality Models..."):
                st.session_state.manager = ImprovedBig5LLMManager()
            st.success("✅ Models loaded successfully!")
            return True
        except Exception as e:
            st.error(f"Error loading models: {e}")
            st.error("Please make sure all dependencies are installed.")
            return False
    return True


def main():
    """Main application"""
    st.set_page_config(
        page_title="Big5 Personality Chat",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 Big5 Personality LLMs Chat Interface")
    st.markdown("Test and interact with AI personalities based on the Big Five model!")
    
    # Initialize session state
    if 'selected_personality' not in st.session_state:
        st.session_state.selected_personality = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Check if models are available
    if not MODELS_AVAILABLE:
        st.error("❌ Models not available. Please check your installation.")
        st.stop()
    
    # Initialize models
    if not initialize_models():
        st.stop()
    
    # Sidebar for personality selection
    st.sidebar.header("🎭 Select Personality")
    
    personalities = get_personality_info()
    
    # Personality selection
    selected_key = st.sidebar.selectbox(
        "Choose a personality:",
        options=list(personalities.keys()),
        format_func=lambda x: f"{personalities[x]['emoji']} {personalities[x]['name']} - {personalities[x]['description']}",
        key="personality_selector"
    )
    
    if selected_key:
        personality = personalities[selected_key]
        
        # Display selected personality info
        st.markdown(f"""
        ### {personality['emoji']} Chatting with {personality['name']}
        **{personality['description']}**
        """)
        
        # Chat interface
        st.markdown("---")
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### 💬 Conversation History")
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**{personality['emoji']} {personality['name']}:** {message['content']}")
                st.markdown("---")
        
        # Input area
        st.markdown("### ✍️ Your Message")
        user_input = st.text_area(
            "Type your message:",
            height=100,
            placeholder=f"Ask {personality['name']} anything!"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("Send 📤"):
                if user_input.strip():
                    # Add user message
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': user_input.strip()
                    })
                    
                    # Generate AI response
                    try:
                        with st.spinner(f"🤔 {personality['name']} is thinking..."):
                            response = st.session_state.manager.get_response(selected_key, user_input.strip())
                        
                        # Add AI response
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error generating response: {e}")
        
        with col2:
            if st.button("Clear Chat 🗑️"):
                st.session_state.chat_history = []
                st.rerun()
    
    # Comparison mode
    st.markdown("---")
    st.markdown("## 🔍 Compare All Personalities")
    st.markdown("Ask the same question to all personalities and see the differences!")
    
    comparison_input = st.text_input("Enter a question for all personalities:")
    
    if st.button("🎭 Get All Responses") and comparison_input.strip():
        try:
            with st.spinner("Getting responses from all personalities..."):
                responses = st.session_state.manager.get_all_responses(comparison_input.strip())
            
            st.markdown("### 🎭 All Personality Responses")
            
            for personality_key, response in responses.items():
                if personality_key in personalities:
                    personality = personalities[personality_key]
                    st.markdown(f"""
                    **{personality['emoji']} {personality['name']} ({personality['description']}):**
                    {response}
                    """)
                    st.markdown("---")
                    
        except Exception as e:
            st.error(f"Error getting responses: {e}")
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 Testing Tips")
    st.sidebar.markdown("""
    **Good questions to try:**
    - How do you handle stress?
    - What motivates you?
    - How do you make decisions?
    - What's your ideal weekend?
    - How do you deal with conflict?
    """)


if __name__ == "__main__":
    main()
