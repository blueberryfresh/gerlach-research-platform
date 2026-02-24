"""
Quick Test of Strengthened Personalities
Tests a few questions to verify improved trait expression
"""

from composite_big5_llms import CompositeBig5LLMManager

def test_trait_keywords(response, expected_keywords):
    """Check if response contains expected trait keywords"""
    response_lower = response.lower()
    found = [kw for kw in expected_keywords if kw in response_lower]
    return found, len(found)

def main():
    print("="*80)
    print("TESTING STRENGTHENED PERSONALITIES")
    print("="*80)
    print("\nThis quick test verifies that personalities now use more trait-specific vocabulary.\n")
    
    # Initialize
    print("Loading models...")
    manager = CompositeBig5LLMManager()
    print("✓ Models loaded!\n")
    
    # Test questions
    test_cases = [
        {
            "question": "How do you approach solving a complex problem?",
            "personalities": {
                "analyst": ["analyze", "examine", "thorough", "methodical", "careful", "detail", "systematic"],
                "driver": ["achieve", "goal", "results", "efficient", "action", "decisive", "execute"]
            }
        },
        {
            "question": "Your team is behind schedule. What do you do?",
            "personalities": {
                "collaborator": ["team", "together", "coordinate", "support", "organize", "collaborate"],
                "driver": ["push", "drive", "results", "action", "deliver", "goal", "efficient"]
            }
        },
        {
            "question": "There's a conflict between two team members. How do you handle it?",
            "personalities": {
                "mediator": ["understand", "empathy", "calm", "balance", "harmony", "perspective", "diplomatic"],
                "collaborator": ["team", "support", "together", "coordinate", "harmony"]
            }
        },
        {
            "question": "You have an opportunity to try something completely new. What's your reaction?",
            "personalities": {
                "innovator": ["exciting", "creative", "opportunity", "innovative", "explore", "bold", "vision"],
                "analyst": ["analyze", "examine", "consider", "evaluate", "careful"]
            }
        }
    ]
    
    total_keywords_found = 0
    total_keywords_expected = 0
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case["question"]
        print(f"\n{'='*80}")
        print(f"TEST {i}: {question}")
        print(f"{'='*80}")
        
        for personality, expected_keywords in test_case["personalities"].items():
            print(f"\n{'-'*80}")
            print(f"Testing: {personality.upper()}")
            print(f"{'-'*80}")
            
            response = manager.get_response(personality, question)
            print(f"\nResponse:")
            print(response)
            
            found_keywords, count = test_trait_keywords(response, expected_keywords)
            total_keywords_found += count
            total_keywords_expected += len(expected_keywords)
            
            print(f"\nTrait Keywords Analysis:")
            print(f"  Expected keywords: {', '.join(expected_keywords)}")
            print(f"  Found: {count}/{len(expected_keywords)}")
            if found_keywords:
                print(f"  Keywords present: {', '.join(found_keywords)}")
            
            if count >= len(expected_keywords) * 0.3:  # At least 30% of keywords
                print(f"  ✅ Good trait expression")
            elif count > 0:
                print(f"  ⚠️  Moderate trait expression")
            else:
                print(f"  ❌ Weak trait expression")
    
    # Summary
    print(f"\n\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")
    
    keyword_percentage = (total_keywords_found / total_keywords_expected) * 100
    print(f"\nTotal trait keywords found: {total_keywords_found}/{total_keywords_expected}")
    print(f"Keyword usage rate: {keyword_percentage:.1f}%")
    
    if keyword_percentage >= 40:
        print(f"\n✅ EXCELLENT - Personalities showing strong trait expression")
        print(f"   The strengthened prompts are working well!")
    elif keyword_percentage >= 25:
        print(f"\n⚠️  GOOD - Personalities showing moderate trait expression")
        print(f"   Improvement over baseline, may need minor adjustments")
    else:
        print(f"\n❌ NEEDS MORE WORK - Trait expression still weak")
        print(f"   Consider further prompt strengthening")
    
    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}")
    print("\n1. If results are good (>40%), run comprehensive_validation_test.py")
    print("   to get full validation scores")
    print("\n2. If results are moderate (25-40%), test more questions manually")
    print("   in the web interface to verify improvement")
    print("\n3. If results are still weak (<25%), we may need to adjust")
    print("   generation parameters or try a different approach")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
