"""
Quick Diagnostic: Test all 5 personalities with your challenging question
Compare responses to identify patterns
"""

from composite_big5_llms import CompositeBig5LLMManager

def analyze_response_traits(response, personality_key):
    """Analyze if response contains expected trait indicators"""
    
    # Define expected keywords for each personality
    trait_keywords = {
        'analyst': {
            'positive': ['analyze', 'thorough', 'detail', 'examine', 'methodical', 'careful',
                        'consider', 'evaluate', 'assess', 'systematic', 'precise', 'accuracy',
                        'data', 'evidence', 'research', 'study', 'investigate', 'review'],
            'negative': ['rush', 'quick', 'immediately', 'hasty', 'superficial']
        },
        'driver': {
            'positive': ['achieve', 'goal', 'result', 'efficient', 'direct', 'decisive',
                        'action', 'execute', 'complete', 'accomplish', 'drive', 'push',
                        'deliver', 'outcome', 'performance', 'target', 'focus'],
            'negative': ['maybe', 'perhaps', 'uncertain', 'hesitate', 'wait', 'delay']
        },
        'collaborator': {
            'positive': ['team', 'together', 'cooperate', 'support', 'help', 'collective',
                        'group', 'collaborate', 'share', 'organize', 'coordinate'],
            'negative': ['alone', 'individual', 'solo', 'independent']
        },
        'innovator': {
            'positive': ['creative', 'new', 'innovative', 'idea', 'exciting', 'opportunity',
                        'change', 'bold', 'explore', 'discover', 'imagine', 'vision'],
            'negative': ['traditional', 'conventional', 'routine', 'boring']
        },
        'mediator': {
            'positive': ['understand', 'empathy', 'calm', 'balance', 'harmony', 'perspective',
                        'listen', 'patient', 'peaceful', 'consensus', 'diplomatic'],
            'negative': ['conflict', 'aggressive', 'force', 'dominate']
        }
    }
    
    response_lower = response.lower()
    keywords = trait_keywords.get(personality_key, {'positive': [], 'negative': []})
    
    positive_count = sum(1 for word in keywords['positive'] if word in response_lower)
    negative_count = sum(1 for word in keywords['negative'] if word in response_lower)
    
    return positive_count, negative_count, keywords


def main():
    print("="*80)
    print("DIAGNOSTIC: Test Your Challenging Question Across All Personalities")
    print("="*80)
    print()
    
    # Get the challenging question
    print("Enter your challenging question:")
    print("(The one where Analyst and Driver showed less than 'strong match')")
    print()
    question = input("Question: ").strip()
    
    if not question:
        print("No question entered. Exiting.")
        return
    
    print("\n" + "="*80)
    print(f"Testing Question: {question}")
    print("="*80)
    
    # Initialize manager
    print("\nLoading models...")
    manager = CompositeBig5LLMManager()
    print("✓ Models loaded!\n")
    
    # Get responses from all personalities
    print("Generating responses from all 5 personalities...")
    print("(This will take about 30-60 seconds)\n")
    
    responses = manager.get_all_responses(question)
    
    # Analyze each response
    personalities = {
        'collaborator': {'emoji': '🤝', 'name': 'The Collaborator'},
        'innovator': {'emoji': '💡', 'name': 'The Innovator'},
        'analyst': {'emoji': '🔬', 'name': 'The Analyst'},
        'mediator': {'emoji': '☮️', 'name': 'The Mediator'},
        'driver': {'emoji': '⚡', 'name': 'The Driver'}
    }
    
    print("\n" + "="*80)
    print("RESPONSE ANALYSIS")
    print("="*80)
    
    for p_key in ['collaborator', 'innovator', 'analyst', 'mediator', 'driver']:
        info = personalities[p_key]
        response = responses[p_key]
        config = manager.get_personality_info(p_key)
        
        print(f"\n{'─'*80}")
        print(f"{info['emoji']} {info['name']}")
        print(f"{'─'*80}")
        print(f"Expected Traits: {', '.join(config.key_traits[:4])}")
        print()
        print(f"Response:")
        print(response)
        print()
        
        # Analyze trait alignment
        positive, negative, keywords = analyze_response_traits(response, p_key)
        
        print(f"Trait Analysis:")
        print(f"  ✓ Positive trait indicators: {positive}")
        print(f"  ✗ Negative trait indicators: {negative}")
        
        if positive > 0:
            print(f"  Found keywords: {', '.join([w for w in keywords['positive'] if w in response.lower()])}")
        
        # Calculate alignment score
        total_indicators = positive + negative
        if total_indicators > 0:
            alignment = (positive - negative) / total_indicators
            alignment_pct = ((alignment + 1) / 2) * 100  # Convert to 0-100%
        else:
            alignment_pct = 50  # Neutral if no indicators
        
        print(f"  Alignment Score: {alignment_pct:.1f}%")
        
        if alignment_pct >= 70:
            print(f"  Assessment: ✅ Strong match")
        elif alignment_pct >= 50:
            print(f"  Assessment: ⚠️  Moderate match")
        else:
            print(f"  Assessment: ❌ Weak match")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY & RECOMMENDATIONS")
    print("="*80)
    
    analyst_response = responses['analyst']
    driver_response = responses['driver']
    
    analyst_pos, analyst_neg, _ = analyze_response_traits(analyst_response, 'analyst')
    driver_pos, driver_neg, _ = analyze_response_traits(driver_response, 'driver')
    
    print(f"\n🔬 The Analyst:")
    print(f"   Positive indicators: {analyst_pos}")
    print(f"   Negative indicators: {analyst_neg}")
    
    if analyst_pos < 2:
        print(f"   ⚠️  Issue: Low trait expression")
        print(f"   Recommendation: Response lacks analytical/methodical language")
    else:
        print(f"   ✅ Trait expression is adequate")
    
    print(f"\n⚡ The Driver:")
    print(f"   Positive indicators: {driver_pos}")
    print(f"   Negative indicators: {driver_neg}")
    
    if driver_pos < 2:
        print(f"   ⚠️  Issue: Low trait expression")
        print(f"   Recommendation: Response lacks action/results-oriented language")
    else:
        print(f"   ✅ Trait expression is adequate")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    
    print("\nOption 1: Test with more questions")
    print("  Run: python test_analyst_driver.py")
    print("  This will test both personalities with 8 questions each")
    print()
    print("Option 2: Compare with other personalities")
    print("  Notice if Collaborator, Innovator, and Mediator show stronger traits")
    print("  This helps determine if it's a systematic issue")
    print()
    print("Option 3: Adjust personality configurations")
    print("  If pattern persists, we can strengthen the system prompts")
    print("  and generation parameters for Analyst and Driver")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
