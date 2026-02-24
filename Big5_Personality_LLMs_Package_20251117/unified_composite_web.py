import streamlit as st
from composite_big5_llms import CompositeBig5LLMManager
from datetime import datetime

st.set_page_config(page_title="Composite Big5 Personalities", page_icon="🎭", layout="wide")

# Initialize
if 'manager' not in st.session_state:
    with st.spinner("🧠 Loading all personality models..."):
        st.session_state.manager = CompositeBig5LLMManager()
    st.success("✅ All models loaded!")

if 'responses' not in st.session_state:
    st.session_state.responses = {
        "collaborator": [],
        "innovator": [],
        "analyst": [],
        "mediator": [],
        "driver": []
    }

# Title with larger font
st.markdown("""
<h1 style="font-size: 3.5em; text-align: center; margin-bottom: 10px;">
    🎭 Big5 Personality LLMs
</h1>
<h3 style="text-align: center; color: #666; margin-top: 0;">
    Test each personality by entering your question in their respective field
</h3>
""", unsafe_allow_html=True)
st.markdown("---")

# Personality configurations
personalities = {
    "collaborator": {
        "emoji": "🤝",
        "name": "The Collaborator",
        "description": "Team-oriented, reliable, organized, and cooperative. Excels at working with others while maintaining structure and achieving collective goals.",
        "traits": "High Agreeableness + High Conscientiousness + Moderate Extraversion",
        "color": "#4ECDC4"
    },
    "innovator": {
        "emoji": "💡",
        "name": "The Innovator",
        "description": "Creative, confident, social, and adventurous. Thrives on novelty, takes risks, and inspires others with bold, innovative ideas.",
        "traits": "High Openness + High Extraversion + Low Neuroticism",
        "color": "#FF6B6B"
    },
    "analyst": {
        "emoji": "🔬",
        "name": "The Analyst",
        "description": "Thoughtful, detail-oriented, intellectually curious, and introspective. Combines systematic analysis with creative problem-solving.",
        "traits": "High Conscientiousness + High Openness + Low Extraversion",
        "color": "#95A5A6"
    },
    "mediator": {
        "emoji": "☮️",
        "name": "The Mediator",
        "description": "Calm, empathetic, diplomatic, and balanced. Excels at understanding different perspectives and finding harmonious solutions.",
        "traits": "High Agreeableness + Low Neuroticism + Moderate Openness",
        "color": "#96CEB4"
    },
    "driver": {
        "emoji": "⚡",
        "name": "The Driver",
        "description": "Assertive, goal-focused, competitive, and results-driven. Takes charge, makes tough decisions, and prioritizes efficiency.",
        "traits": "Low Agreeableness + High Conscientiousness + High Extraversion",
        "color": "#FFA500"
    }
}

# Create columns for layout (2 per row)
col1, col2 = st.columns(2)

# Function to create personality card
def create_personality_card(personality_key, info, column):
    with column:
        # Card container
        st.markdown(f"""
        <div style="
            border: 3px solid {info['color']};
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            background-color: #FAFAFA;
        ">
            <h2 style="color: {info['color']}; margin: 0;">
                {info['emoji']} {info['name']}
            </h2>
            <p style="margin: 10px 0; color: #666; font-size: 0.9em;">
                <strong>{info['traits']}</strong>
            </p>
            <p style="margin: 10px 0; color: #333;">
                {info['description']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Input field for this personality
        question = st.text_area(
            f"Ask {info['name']}:",
            height=80,
            key=f"input_{personality_key}",
            placeholder=f"Type your question for {info['name']} here..."
        )
        
        col_a, col_b = st.columns([1, 3])
        with col_a:
            submit = st.button(f"Ask {info['emoji']}", key=f"submit_{personality_key}", use_container_width=True)
        with col_b:
            clear = st.button(f"Clear History", key=f"clear_{personality_key}", use_container_width=True)
        
        # Handle submission
        if submit and question.strip():
            with st.spinner(f"{info['emoji']} {info['name']} is thinking..."):
                response = st.session_state.manager.get_response(personality_key, question.strip())
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                st.session_state.responses[personality_key].append({
                    "question": question.strip(),
                    "response": response,
                    "timestamp": timestamp
                })
            st.rerun()
        
        # Handle clear
        if clear:
            st.session_state.responses[personality_key] = []
            st.rerun()
        
        # Display conversation history
        if st.session_state.responses[personality_key]:
            st.markdown(f"**💬 Conversation History:**")
            
            for i, conv in enumerate(reversed(st.session_state.responses[personality_key])):
                with st.expander(f"Q: {conv['question'][:50]}... ({conv['timestamp']})", expanded=(i==0)):
                    st.markdown(f"**You asked:**")
                    st.info(conv['question'])
                    st.markdown(f"**{info['emoji']} {info['name']} responded:**")
                    st.success(conv['response'])
        
        st.markdown("---")

# Display personalities in 2-column layout
create_personality_card("collaborator", personalities["collaborator"], col1)
create_personality_card("innovator", personalities["innovator"], col2)

col3, col4 = st.columns(2)
create_personality_card("analyst", personalities["analyst"], col3)
create_personality_card("mediator", personalities["mediator"], col4)

# Driver in same 2-column layout
col5, col6 = st.columns(2)
create_personality_card("driver", personalities["driver"], col5)

# Comparison section at the very bottom
st.markdown("---")
st.markdown("---")
st.markdown("---")

st.markdown("""
<div style="
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    margin: 20px 0;
">
    <h1 style="color: white; margin: 0;">🔍 Compare All Five Personalities</h1>
    <p style="color: white; margin: 10px 0; font-size: 1.1em;">
        Ask the same question to all personalities and see how their responses differ!
    </p>
</div>
""", unsafe_allow_html=True)

compare_question = st.text_area(
    "Enter your question for all five personalities:",
    height=120,
    key="compare_input",
    placeholder="Example: 'How do you handle team conflicts?' or 'What's your approach to innovation?' or 'How do you make important decisions?'"
)

if st.button("🎭 Get All 5 Responses", key="compare_submit", use_container_width=True, type="primary"):
    if compare_question and compare_question.strip():
        st.markdown("---")
        st.markdown("### 📊 Comparative Responses from All Personalities")
        st.markdown(f"**Question:** *{compare_question.strip()}*")
        st.markdown("---")
        
        try:
            with st.spinner("🤔 Getting responses from all five personalities..."):
                responses = st.session_state.manager.get_all_responses(compare_question.strip())
            
            # Debug: Show what we got
            if not responses:
                st.error("No responses received from the manager!")
            else:
                st.info(f"Received {len(responses)} responses")
            
            # Display all responses
            for p_key in ["collaborator", "innovator", "analyst", "mediator", "driver"]:
                if p_key in responses and p_key in personalities:
                    info = personalities[p_key]
                    response = responses[p_key]
                    
                    st.markdown(f"#### {info['emoji']} {info['name']}")
                    st.markdown(f"*{info['traits']}*")
                    
                    # Display response in a simple container (not HTML)
                    with st.container():
                        st.info(response)
                    
                    # Show key traits
                    config = st.session_state.manager.get_personality_info(p_key)
                    st.caption(f"Key traits: {', '.join(config.key_traits[:4])}")
                    st.markdown("---")
            
            st.success("✅ All responses generated! Compare the different approaches above.")
            
        except Exception as e:
            st.error(f"Error generating responses: {e}")
            import traceback
            st.code(traceback.format_exc())
    else:
        st.warning("⚠️ Please enter a question first!")

# Sidebar with information
with st.sidebar:
    st.markdown("# 📚 About")
    st.markdown("""
    This interface allows you to test all five composite Big5 personality LLMs simultaneously.
    
    Each personality combines multiple traits to create realistic, nuanced AI personas.
    """)
    
    st.markdown("---")
    st.markdown("## 💡 Testing Tips")
    st.markdown("""
    **Good Questions:**
    - How do you handle conflicts?
    - What's your leadership style?
    - How do you approach innovation?
    - What motivates you?
    - How do you make decisions?
    
    **Try:**
    - Ask each personality individually
    - Use the comparison mode
    - Notice vocabulary differences
    - Observe approach variations
    """)
    
    st.markdown("---")
    st.markdown("## 📊 Personality Traits")
    
    for p_key, info in personalities.items():
        config = st.session_state.manager.get_personality_info(p_key)
        with st.expander(f"{info['emoji']} {info['name']}"):
            st.markdown(f"**O:** {config.openness} | **C:** {config.conscientiousness}")
            st.markdown(f"**E:** {config.extraversion} | **A:** {config.agreeableness}")
            st.markdown(f"**N:** {config.neuroticism}")
            st.markdown(f"\n*{', '.join(config.key_traits[:4])}*")
    
    st.markdown("---")
    
    # Clear all button
    if st.button("🗑️ Clear All Histories", use_container_width=True):
        for key in st.session_state.responses:
            st.session_state.responses[key] = []
        st.rerun()
    
    # Stats
    total_conversations = sum(len(convs) for convs in st.session_state.responses.values())
    st.markdown(f"**Total Conversations:** {total_conversations}")
