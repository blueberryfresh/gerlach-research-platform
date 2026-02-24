import streamlit as st
from composite_big5_llms import CompositeBig5LLMManager

st.set_page_config(page_title="Composite Big5 Personalities", page_icon="🎭", layout="wide")

# Initialize
if 'manager' not in st.session_state:
    with st.spinner("Loading models..."):
        st.session_state.manager = CompositeBig5LLMManager()
    st.success("Models loaded!")

if 'history' not in st.session_state:
    st.session_state.history = []

# Title
st.title("🎭 Composite Big5 Personality LLMs")

# Personality info
personalities = {
    "collaborator": {"emoji": "🤝", "name": "The Collaborator", "desc": "Team-oriented, reliable, organized"},
    "innovator": {"emoji": "💡", "name": "The Innovator", "desc": "Creative, confident, adventurous"},
    "analyst": {"emoji": "🔬", "name": "The Analyst", "desc": "Thoughtful, detail-oriented, intellectual"},
    "mediator": {"emoji": "☮️", "name": "The Mediator", "desc": "Calm, empathetic, diplomatic"},
    "driver": {"emoji": "⚡", "name": "The Driver", "desc": "Assertive, goal-focused, results-driven"}
}

# Sidebar
with st.sidebar:
    st.header("Select Personality")
    selected = st.selectbox(
        "Choose:",
        list(personalities.keys()),
        format_func=lambda x: f"{personalities[x]['emoji']} {personalities[x]['name']}"
    )
    
    st.markdown("---")
    st.markdown("### About")
    info = personalities[selected]
    st.markdown(f"**{info['emoji']} {info['name']}**")
    st.markdown(f"{info['desc']}")
    
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# Main area
st.markdown(f"## Chatting with {personalities[selected]['emoji']} {personalities[selected]['name']}")

# Display history
for msg in st.session_state.history:
    if msg['personality'] == selected:
        with st.chat_message("user"):
            st.write(msg['question'])
        with st.chat_message("assistant"):
            st.write(msg['response'])

# Input
question = st.chat_input("Ask a question...")

if question:
    # Get response
    with st.spinner("Thinking..."):
        response = st.session_state.manager.get_response(selected, question)
    
    # Save to history
    st.session_state.history.append({
        'personality': selected,
        'question': question,
        'response': response
    })
    
    st.rerun()

# Comparison mode
st.markdown("---")
st.markdown("## 🔍 Compare All Personalities")

compare_question = st.text_input("Ask all personalities the same question:")

if st.button("Get All Responses") and compare_question:
    with st.spinner("Getting responses..."):
        responses = st.session_state.manager.get_all_responses(compare_question)
    
    for p_key, resp in responses.items():
        p_info = personalities[p_key]
        st.markdown(f"### {p_info['emoji']} {p_info['name']}")
        st.write(resp)
        st.markdown("---")
