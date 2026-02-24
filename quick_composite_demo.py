"""
Quick Demo of Composite Big5 Personalities
Shows sample responses from each personality type
"""

from composite_big5_llms import CompositeBig5LLMManager


def main():
    print("="*70)
    print("🎭 COMPOSITE BIG5 PERSONALITY LLMs - QUICK DEMO")
    print("="*70)
    
    manager = CompositeBig5LLMManager()
    
    # Demo questions
    demo_questions = [
        "How do you handle a team member who disagrees with your approach?",
        "What's your strategy for tackling a complex problem?",
        "How do you balance getting results with maintaining relationships?"
    ]
    
    print("\nThis demo will show how each personality responds to key questions.")
    print(f"Testing {len(demo_questions)} questions across 5 personalities.\n")
    
    for i, question in enumerate(demo_questions, 1):
        print("\n" + "="*70)
        print(f"QUESTION {i}: {question}")
        print("="*70)
        
        for personality in manager.list_personalities():
            config = manager.get_personality_info(personality)
            
            print(f"\n{config.name.upper()} - {config.description}")
            print(f"Key Traits: {', '.join(config.key_traits[:4])}")
            print("-" * 70)
            
            response = manager.get_response(personality, question)
            print(f"Response: {response}")
            print()
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE!")
    print("="*70)
    print("\nKey Observations:")
    print("- The Collaborator focuses on teamwork and organization")
    print("- The Innovator emphasizes creativity and bold approaches")
    print("- The Analyst provides thorough, methodical responses")
    print("- The Mediator seeks harmony and understanding")
    print("- The Driver prioritizes results and efficiency")


if __name__ == "__main__":
    main()
