"""
Focused Testing for The Analyst and The Driver
Tests these two personalities with multiple questions to check consistency
"""

from composite_big5_llms import CompositeBig5LLMManager

def test_personality_alignment(manager, personality_key, personality_name, test_questions):
    """Test a personality with multiple questions and analyze responses"""
    
    print("\n" + "="*80)
    print(f"Testing: {personality_name}")
    print("="*80)
    
    config = manager.get_personality_info(personality_key)
    print(f"\nExpected Traits: {', '.join(config.key_traits[:5])}")
    print(f"Big5 Scores: O:{config.openness} C:{config.conscientiousness} " +
          f"E:{config.extraversion} A:{config.agreeableness} N:{config.neuroticism}")
    print()
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─'*80}")
        print(f"Question {i}/{len(test_questions)}: {question}")
        print(f"{'─'*80}")
        
        response = manager.get_response(personality_key, question)
        
        print(f"\nResponse:")
        print(response)
        print()
        
        # Ask user to rate the response
        print("Does this response match the expected personality?")
        print("1 = Poor match")
        print("2 = Weak match")
        print("3 = Moderate match")
        print("4 = Good match")
        print("5 = Strong match")
        
        while True:
            try:
                rating = input("\nYour rating (1-5): ").strip()
                rating = int(rating)
                if 1 <= rating <= 5:
                    break
                print("Please enter a number between 1 and 5")
            except ValueError:
                print("Please enter a valid number")
        
        results.append({
            'question': question,
            'response': response,
            'rating': rating
        })
        
        print(f"\n✓ Recorded rating: {rating}/5")
    
    # Summary
    print("\n" + "="*80)
    print(f"SUMMARY: {personality_name}")
    print("="*80)
    
    avg_rating = sum(r['rating'] for r in results) / len(results)
    
    for i, result in enumerate(results, 1):
        rating_stars = "★" * result['rating'] + "☆" * (5 - result['rating'])
        print(f"\nQ{i}: {rating_stars} ({result['rating']}/5)")
        print(f"    {result['question'][:60]}...")
    
    print(f"\n{'─'*80}")
    print(f"Average Rating: {avg_rating:.2f}/5")
    
    if avg_rating >= 4.0:
        print("✅ STRONG MATCH - Personality is well-aligned")
    elif avg_rating >= 3.0:
        print("⚠️  MODERATE MATCH - Some alignment issues")
    else:
        print("❌ WEAK MATCH - Personality needs adjustment")
    
    print("="*80)
    
    return results, avg_rating


def main():
    print("="*80)
    print("FOCUSED PERSONALITY TESTING: The Analyst & The Driver")
    print("="*80)
    print("\nThis test will help determine if these personalities need adjustment.")
    print("You'll rate each response on how well it matches the expected personality.")
    print()
    
    # Initialize manager
    print("Loading models...")
    manager = CompositeBig5LLMManager()
    print("✓ Models loaded!\n")
    
    # Test questions for The Analyst
    analyst_questions = [
        "How do you approach solving a complex problem?",
        "What's your process for making an important decision?",
        "How do you handle situations with incomplete information?",
        "Describe your approach to analyzing data or evidence.",
        "How do you ensure accuracy in your work?",
        "What's your strategy when facing a difficult challenge?",
        "How do you balance speed and thoroughness?",
        "What role does research play in your decision-making?"
    ]
    
    # Test questions for The Driver
    driver_questions = [
        "How do you push a project to completion?",
        "What's your approach when people are moving too slowly?",
        "How do you handle team members who disagree with your direction?",
        "Describe your leadership style.",
        "How do you prioritize competing demands?",
        "What do you do when faced with obstacles?",
        "How do you motivate others to achieve goals?",
        "What's your approach to making tough decisions quickly?"
    ]
    
    # Test The Analyst
    analyst_results, analyst_avg = test_personality_alignment(
        manager, 
        "analyst", 
        "🔬 The Analyst",
        analyst_questions
    )
    
    input("\n\nPress Enter to continue to The Driver testing...")
    
    # Test The Driver
    driver_results, driver_avg = test_personality_alignment(
        manager,
        "driver",
        "⚡ The Driver",
        driver_questions
    )
    
    # Overall summary
    print("\n\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)
    
    print(f"\n🔬 The Analyst: {analyst_avg:.2f}/5")
    if analyst_avg >= 4.0:
        print("   Status: ✅ Strong match - No changes needed")
    elif analyst_avg >= 3.0:
        print("   Status: ⚠️  Moderate match - Consider adjustments")
        print("   Suggestion: Review system prompt and generation parameters")
    else:
        print("   Status: ❌ Weak match - Needs adjustment")
        print("   Suggestion: Revise personality configuration")
    
    print(f"\n⚡ The Driver: {driver_avg:.2f}/5")
    if driver_avg >= 4.0:
        print("   Status: ✅ Strong match - No changes needed")
    elif driver_avg >= 3.0:
        print("   Status: ⚠️  Moderate match - Consider adjustments")
        print("   Suggestion: Review system prompt and generation parameters")
    else:
        print("   Status: ❌ Weak match - Needs adjustment")
        print("   Suggestion: Revise personality configuration")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if analyst_avg < 4.0 or driver_avg < 4.0:
        print("\nBased on your ratings, here are some options:")
        print("\n1. Test with more questions to confirm the pattern")
        print("2. Adjust the personality system prompts to be more explicit")
        print("3. Modify generation parameters (temperature, top_p)")
        print("4. Add more specific trait keywords to the prompts")
        print("\nWould you like help making these adjustments?")
    else:
        print("\n✅ Both personalities are performing well!")
        print("The lower rating on your challenging question may have been")
        print("question-specific rather than a systematic issue.")
    
    print("\n" + "="*80)
    
    # Save results
    import json
    from datetime import datetime
    
    results_file = f"analyst_driver_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'analyst': {
                'average_rating': analyst_avg,
                'results': analyst_results
            },
            'driver': {
                'average_rating': driver_avg,
                'results': driver_results
            }
        }, f, indent=2)
    
    print(f"\n📊 Results saved to: {results_file}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTesting interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
