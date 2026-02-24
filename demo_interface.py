import streamlit as st
import sys
import os
from big5_personality_llms import Big5LLMManager
from personality_evaluation import PersonalityEvaluator


def main():
    st.set_page_config(
        page_title="Big5 Personality LLMs Demo",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 Big Five Personality LLMs")
    st.markdown("Interact with five different AI personalities based on the Big Five personality traits!")
    
    # Initialize session state
    if 'manager' not in st.session_state:
        with st.spinner("Loading models... This may take a moment."):
            st.session_state.manager = Big5LLMManager()
    
    # Sidebar for personality selection
    st.sidebar.header("🎭 Personality Selection")
    
    personalities = {
        "openness": "🎨 Openness - Creative & Curious",
        "conscientiousness": "📋 Conscientiousness - Organized & Disciplined", 
        "extraversion": "🎉 Extraversion - Social & Energetic",
        "agreeableness": "🤝 Agreeableness - Cooperative & Trusting",
        "neuroticism": "😰 Neuroticism - Emotional & Anxious"
    }
    
    # Mode selection
    mode = st.sidebar.radio(
        "Choose interaction mode:",
        ["Single Personality", "Compare All Personalities", "Evaluation Mode"]
    )
    
    if mode == "Single Personality":
        selected_personality = st.sidebar.selectbox(
            "Select a personality:",
            list(personalities.keys()),
            format_func=lambda x: personalities[x]
        )
        
        st.header(f"Chat with {personalities[selected_personality]}")
        
        # Chat interface
        user_input = st.text_input("Your message:", key="single_input")
        
        if st.button("Send", key="single_send") and user_input:
            with st.spinner(f"Generating response from {selected_personality}..."):
                response = st.session_state.manager.get_response(selected_personality, user_input)
            
            st.markdown("### Response:")
            st.write(response)
    
    elif mode == "Compare All Personalities":
        st.header("🔍 Compare All Personality Responses")
        
        user_input = st.text_input("Your message:", key="compare_input")
        
        if st.button("Get All Responses", key="compare_send") and user_input:
            with st.spinner("Generating responses from all personalities..."):
                responses = st.session_state.manager.get_all_responses(user_input)
            
            st.markdown("### Responses from Each Personality:")
            
            # Create columns for better layout
            cols = st.columns(2)
            
            for i, (personality, response) in enumerate(responses.items()):
                with cols[i % 2]:
                    st.markdown(f"**{personalities[personality]}**")
                    st.write(response)
                    st.markdown("---")
    
    elif mode == "Evaluation Mode":
        st.header("📊 Personality Model Evaluation")
        
        st.markdown("""
        This mode evaluates how well each personality model exhibits its expected traits.
        The evaluation measures:
        - **Consistency**: How consistently each model shows its personality
        - **Accuracy**: How well each model exhibits expected vs. other personality traits
        - **Distinctiveness**: How different each personality's responses are from others
        """)
        
        if st.button("Run Evaluation"):
            with st.spinner("Running comprehensive evaluation... This may take several minutes."):
                evaluator = PersonalityEvaluator(st.session_state.manager)
                results = evaluator.run_comprehensive_evaluation()
                report = evaluator.generate_evaluation_report(results)
            
            st.markdown("### Evaluation Results")
            st.markdown(report)
            
            # Download button for report
            st.download_button(
                label="Download Evaluation Report",
                data=report,
                file_name="big5_evaluation_report.md",
                mime="text/markdown"
            )
    
    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About the Big Five")
    st.sidebar.markdown("""
    **Openness**: Creativity, curiosity, openness to new experiences
    
    **Conscientiousness**: Organization, discipline, goal-orientation
    
    **Extraversion**: Sociability, energy, assertiveness
    
    **Agreeableness**: Cooperation, trust, empathy
    
    **Neuroticism**: Emotional reactivity, anxiety, sensitivity
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and Transformers")


def run_cli_demo():
    """Command-line interface demo"""
    print("🧠 Big Five Personality LLMs - CLI Demo")
    print("=" * 50)
    
    # Initialize manager
    print("Loading models...")
    manager = Big5LLMManager()
    print("Models loaded successfully!\n")
    
    personalities = {
        "1": "openness",
        "2": "conscientiousness", 
        "3": "extraversion",
        "4": "agreeableness",
        "5": "neuroticism"
    }
    
    while True:
        print("\nSelect an option:")
        print("1. Chat with Openness (Creative & Curious)")
        print("2. Chat with Conscientiousness (Organized & Disciplined)")
        print("3. Chat with Extraversion (Social & Energetic)")
        print("4. Chat with Agreeableness (Cooperative & Trusting)")
        print("5. Chat with Neuroticism (Emotional & Anxious)")
        print("6. Compare all personalities")
        print("7. Run evaluation")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        
        elif choice in personalities:
            personality = personalities[choice]
            print(f"\n💬 Chatting with {personality.title()}")
            print("Type 'back' to return to main menu\n")
            
            while True:
                user_input = input("You: ").strip()
                if user_input.lower() == 'back':
                    break
                
                if user_input:
                    print("Generating response...")
                    response = manager.get_response(personality, user_input)
                    print(f"{personality.title()}: {response}\n")
        
        elif choice == "6":
            user_input = input("\nEnter your message: ").strip()
            if user_input:
                print("\nGenerating responses from all personalities...\n")
                manager.compare_personalities(user_input)
        
        elif choice == "7":
            print("\nRunning evaluation...")
            evaluator = PersonalityEvaluator(manager)
            results = evaluator.run_comprehensive_evaluation()
            report = evaluator.generate_evaluation_report(results)
            
            # Save report
            with open("evaluation_report.md", "w") as f:
                f.write(report)
            
            print("Evaluation complete! Report saved to evaluation_report.md")
            print("\nSummary:")
            for personality in results["consistency"].keys():
                consistency = results["consistency"][personality]
                accuracy = results["accuracy"][personality]
                print(f"{personality.title()}: Consistency={consistency:.3f}, Accuracy={accuracy:.3f}")
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli_demo()
    else:
        # Check if streamlit is available
        try:
            import streamlit
            print("Starting Streamlit web interface...")
            print("Run with --cli flag for command-line interface")
            main()
        except ImportError:
            print("Streamlit not available. Running CLI demo...")
            run_cli_demo()
