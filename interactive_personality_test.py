#!/usr/bin/env python3
"""
Interactive Big5 Personality LLM Testing Interface
Allows direct interaction with each personality model for manual evaluation
"""

import sys
from improved_big5_llms import ImprovedBig5LLMManager


class InteractivePersonalityTester:
    """Interactive interface for testing Big5 personality LLMs"""
    
    def __init__(self):
        print("🧠 Initializing Big5 Personality LLMs...")
        print("Please wait while models are loaded...")
        self.manager = ImprovedBig5LLMManager()
        
        self.personalities = {
            "1": {"name": "openness", "emoji": "🎨", "description": "Creative & Curious"},
            "2": {"name": "conscientiousness", "emoji": "📋", "description": "Organized & Disciplined"},
            "3": {"name": "extraversion", "emoji": "🎉", "description": "Social & Energetic"},
            "4": {"name": "agreeableness", "emoji": "🤝", "description": "Cooperative & Trusting"},
            "5": {"name": "neuroticism", "emoji": "😰", "description": "Emotional & Anxious"}
        }
        
        print("✅ All personality models loaded successfully!\n")
    
    def display_personalities(self):
        """Display available personality models"""
        print("🎭 AVAILABLE PERSONALITY MODELS:")
        print("=" * 50)
        for key, info in self.personalities.items():
            print(f"{key}. {info['emoji']} {info['name'].upper()} - {info['description']}")
        print("6. 🔍 ALL PERSONALITIES - Compare all responses")
        print("0. ❌ EXIT")
        print()
    
    def get_single_response(self, personality_name: str, question: str) -> str:
        """Get response from a specific personality"""
        try:
            response = self.manager.get_response(personality_name, question)
            return response
        except Exception as e:
            return f"Error generating response: {e}"
    
    def get_all_responses(self, question: str) -> dict:
        """Get responses from all personalities"""
        try:
            responses = self.manager.get_all_responses(question)
            return responses
        except Exception as e:
            return {"error": f"Error generating responses: {e}"}
    
    def display_single_response(self, personality_key: str, question: str):
        """Display response from a single personality"""
        personality_info = self.personalities[personality_key]
        personality_name = personality_info["name"]
        emoji = personality_info["emoji"]
        description = personality_info["description"]
        
        print(f"\n{emoji} {personality_name.upper()} ({description})")
        print("=" * 60)
        print(f"Question: {question}")
        print("-" * 60)
        
        print("Generating response...")
        response = self.get_single_response(personality_name, question)
        
        print(f"Response: {response}")
        print("=" * 60)
    
    def display_all_responses(self, question: str):
        """Display responses from all personalities"""
        print(f"\n🔍 ALL PERSONALITY RESPONSES")
        print("=" * 60)
        print(f"Question: {question}")
        print("=" * 60)
        
        print("Generating responses from all personalities...")
        responses = self.get_all_responses(question)
        
        if "error" in responses:
            print(f"Error: {responses['error']}")
            return
        
        for personality_name, response in responses.items():
            # Find the personality info
            personality_info = None
            for info in self.personalities.values():
                if info["name"] == personality_name:
                    personality_info = info
                    break
            
            if personality_info:
                emoji = personality_info["emoji"]
                description = personality_info["description"]
                print(f"\n{emoji} {personality_name.upper()} ({description}):")
                print(f"{response}")
                print("-" * 40)
        
        print("=" * 60)
    
    def run_interactive_session(self):
        """Run the main interactive testing session"""
        print("🎯 INTERACTIVE BIG5 PERSONALITY TESTING")
        print("=" * 60)
        print("Test each personality model by asking questions and evaluating their responses.")
        print("Each model has been trained to exhibit distinct Big Five personality traits.\n")
        
        while True:
            self.display_personalities()
            
            choice = input("Select a personality to test (0-6): ").strip()
            
            if choice == "0":
                print("👋 Thank you for testing the Big5 Personality LLMs!")
                break
            
            elif choice in ["1", "2", "3", "4", "5"]:
                personality_info = self.personalities[choice]
                print(f"\n🎭 You selected: {personality_info['emoji']} {personality_info['name'].upper()}")
                print(f"Description: {personality_info['description']}")
                print("\nThis personality should exhibit the following traits:")
                
                # Display expected traits
                trait_descriptions = {
                    "openness": "Creative, curious, imaginative, open to new experiences, artistic",
                    "conscientiousness": "Organized, disciplined, systematic, goal-oriented, responsible",
                    "extraversion": "Social, energetic, outgoing, talkative, enthusiastic",
                    "agreeableness": "Cooperative, empathetic, trusting, helpful, kind",
                    "neuroticism": "Anxious, emotionally sensitive, worried, cautious, stress-aware"
                }
                
                print(f"Expected traits: {trait_descriptions[personality_info['name']]}")
                print()
                
                question = input("Enter your question: ").strip()
                
                if question:
                    self.display_single_response(choice, question)
                    
                    # Ask for user evaluation
                    print(f"\n💭 EVALUATION:")
                    print("How well did this response match the expected personality traits?")
                    print("Consider: vocabulary choice, approach, tone, and characteristic behaviors")
                    
                    evaluation = input("\nYour assessment (or press Enter to continue): ").strip()
                    if evaluation:
                        print(f"✅ Your evaluation noted: {evaluation}")
                
                input("\nPress Enter to continue...")
            
            elif choice == "6":
                print(f"\n🔍 COMPARATIVE ANALYSIS MODE")
                print("This will show responses from ALL five personalities to the same question.")
                print("Perfect for evaluating how well they differentiate from each other.\n")
                
                question = input("Enter your question for all personalities: ").strip()
                
                if question:
                    self.display_all_responses(question)
                    
                    print(f"\n💭 COMPARATIVE EVALUATION:")
                    print("Assess the differences between personalities:")
                    print("- Are the responses clearly different from each other?")
                    print("- Does each response match its expected personality traits?")
                    print("- Which personalities are most/least distinct?")
                    
                    evaluation = input("\nYour comparative assessment (or press Enter to continue): ").strip()
                    if evaluation:
                        print(f"✅ Your evaluation noted: {evaluation}")
                
                input("\nPress Enter to continue...")
            
            else:
                print("❌ Invalid choice. Please select 0-6.")
                input("Press Enter to continue...")
    
    def run_quick_demo(self):
        """Run a quick demonstration with sample questions"""
        print("🚀 QUICK DEMO MODE")
        print("=" * 40)
        
        demo_questions = [
            "How do you approach solving a difficult problem?",
            "What's your ideal way to spend a weekend?",
            "How do you handle stress and pressure?",
            "What motivates you to work hard?"
        ]
        
        print("Here are some sample questions to test personality differentiation:\n")
        
        for i, question in enumerate(demo_questions, 1):
            print(f"{i}. {question}")
        
        choice = input(f"\nSelect a question (1-{len(demo_questions)}) or press Enter to skip demo: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(demo_questions):
            selected_question = demo_questions[int(choice) - 1]
            print(f"\n🎯 Testing with: '{selected_question}'")
            self.display_all_responses(selected_question)
        
        print("\nDemo complete! You can now test with your own questions.")
        input("Press Enter to continue to interactive mode...")


def main():
    """Main function to run the interactive tester"""
    print("🧠 BIG5 PERSONALITY LLM INTERACTIVE TESTER")
    print("=" * 60)
    
    try:
        tester = InteractivePersonalityTester()
        
        # Ask user preference
        print("Choose your testing mode:")
        print("1. 🚀 Quick Demo (see sample responses)")
        print("2. 🎯 Interactive Testing (ask your own questions)")
        
        mode = input("Select mode (1 or 2): ").strip()
        
        if mode == "1":
            tester.run_quick_demo()
        
        # Always run interactive mode after demo or directly
        tester.run_interactive_session()
        
    except KeyboardInterrupt:
        print("\n\n👋 Testing session interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check that all dependencies are installed and try again.")


if __name__ == "__main__":
    main()
