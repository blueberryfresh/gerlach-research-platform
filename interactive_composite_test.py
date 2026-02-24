"""
Interactive Command-Line Interface for Composite Big5 Personalities
Use this if the web interface has connection issues
"""

from composite_big5_llms import CompositeBig5LLMManager
import sys


class InteractiveCompositeTester:
    def __init__(self):
        print("\n" + "="*70)
        print("🎭 COMPOSITE BIG5 PERSONALITY LLMs - INTERACTIVE TESTER")
        print("="*70)
        print("\nLoading models... Please wait...")
        
        self.manager = CompositeBig5LLMManager()
        
        self.personalities = {
            "1": {"key": "collaborator", "emoji": "🤝", "name": "The Collaborator"},
            "2": {"key": "innovator", "emoji": "💡", "name": "The Innovator"},
            "3": {"key": "analyst", "emoji": "🔬", "name": "The Analyst"},
            "4": {"key": "mediator", "emoji": "☮️", "name": "The Mediator"},
            "5": {"key": "driver", "emoji": "⚡", "name": "The Driver"}
        }
        
        print("\n✅ All models loaded successfully!\n")
    
    def show_menu(self):
        print("\n" + "="*70)
        print("SELECT A PERSONALITY TO TEST:")
        print("="*70)
        
        for num, info in self.personalities.items():
            config = self.manager.get_personality_info(info["key"])
            print(f"{num}. {info['emoji']} {info['name']} - {config.description}")
        
        print("6. 🔍 COMPARE ALL PERSONALITIES")
        print("0. ❌ EXIT")
        print("="*70)
    
    def test_single_personality(self, personality_key, personality_name, emoji):
        print(f"\n{'='*70}")
        print(f"Testing {emoji} {personality_name}")
        print(f"{'='*70}")
        
        config = self.manager.get_personality_info(personality_key)
        print(f"Description: {config.description}")
        print(f"Key Traits: {', '.join(config.key_traits)}")
        print(f"Big5 Scores: O:{config.openness} C:{config.conscientiousness} " +
              f"E:{config.extraversion} A:{config.agreeableness} N:{config.neuroticism}")
        print()
        
        while True:
            question = input(f"\nYour question for {personality_name} (or 'back' to return): ").strip()
            
            if question.lower() == 'back':
                break
            
            if not question:
                print("Please enter a question.")
                continue
            
            print(f"\n{emoji} {personality_name} is thinking...")
            response = self.manager.get_response(personality_key, question)
            
            print(f"\n{emoji} {personality_name} says:")
            print("-" * 70)
            print(response)
            print("-" * 70)
    
    def compare_all_personalities(self):
        print(f"\n{'='*70}")
        print("🔍 COMPARE ALL PERSONALITIES")
        print(f"{'='*70}")
        print("Ask the same question to all five personalities and see the differences!")
        print()
        
        question = input("Your question for all personalities: ").strip()
        
        if not question:
            print("No question entered.")
            return
        
        print(f"\n{'='*70}")
        print(f"Question: {question}")
        print(f"{'='*70}\n")
        
        print("Getting responses from all personalities...\n")
        
        responses = self.manager.get_all_responses(question)
        
        for num, info in self.personalities.items():
            personality_key = info["key"]
            if personality_key in responses:
                print(f"\n{info['emoji']} {info['name'].upper()}")
                print("-" * 70)
                print(responses[personality_key])
                print()
        
        print("="*70)
        input("\nPress Enter to continue...")
    
    def run(self):
        while True:
            self.show_menu()
            
            choice = input("\nYour choice (0-6): ").strip()
            
            if choice == "0":
                print("\n👋 Thank you for testing the Composite Big5 Personalities!")
                print("="*70)
                break
            
            elif choice in ["1", "2", "3", "4", "5"]:
                info = self.personalities[choice]
                self.test_single_personality(info["key"], info["name"], info["emoji"])
            
            elif choice == "6":
                self.compare_all_personalities()
            
            else:
                print("\n❌ Invalid choice. Please select 0-6.")
                input("Press Enter to continue...")


def main():
    try:
        tester = InteractiveCompositeTester()
        tester.run()
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
