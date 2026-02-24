"""
Comprehensive Validation Test for Big5 Personality LLMs
Uses specially designed challenging questions to validate personality alignment
"""

from composite_big5_llms import CompositeBig5LLMManager
from validation_questions import get_all_validation_questions
import json
from datetime import datetime


def analyze_response_quality(response, expected_indicators, avoid_indicators):
    """
    Analyze if response contains expected traits and avoids unwanted traits
    Returns: (positive_score, negative_score, found_indicators, found_avoid)
    """
    response_lower = response.lower()
    
    # Extract keywords from expected and avoid strings
    expected_keywords = [word.strip().lower() for word in expected_indicators.split(',')]
    avoid_keywords = [word.strip().lower() for word in avoid_indicators.split(',')]
    
    # Check for expected indicators
    found_expected = []
    for keyword in expected_keywords:
        # Clean up the keyword (remove "Should show:", etc.)
        clean_keyword = keyword.replace('should show:', '').replace('✓', '').strip()
        if clean_keyword and len(clean_keyword) > 3:  # Ignore very short words
            if clean_keyword in response_lower:
                found_expected.append(clean_keyword)
    
    # Check for avoid indicators
    found_avoid = []
    for keyword in avoid_keywords:
        clean_keyword = keyword.replace('should avoid:', '').replace('✗', '').strip()
        if clean_keyword and len(clean_keyword) > 3:
            if clean_keyword in response_lower:
                found_avoid.append(clean_keyword)
    
    positive_score = len(found_expected)
    negative_score = len(found_avoid)
    
    return positive_score, negative_score, found_expected, found_avoid


def test_personality_with_validation_questions(manager, personality_key, personality_data):
    """Test a personality with all validation questions"""
    
    print(f"\n{'='*80}")
    print(f"TESTING: {personality_key.upper()}")
    print(f"{'='*80}")
    print(f"Description: {personality_data['description']}")
    print(f"Core Traits: {', '.join(personality_data['core_traits'])}")
    print()
    
    questions = personality_data['questions']
    results = []
    
    for i, q_data in enumerate(questions, 1):
        question = q_data['q']
        expected = q_data['expected']
        avoid = q_data['avoid']
        
        print(f"\n{'-'*80}")
        print(f"Question {i}/{len(questions)}:")
        print(f"{question}")
        print(f"{'-'*80}")
        
        # Generate response
        print("Generating response...")
        response = manager.get_response(personality_key, question)
        
        print(f"\nResponse:")
        print(response)
        print()
        
        # Analyze response
        pos_score, neg_score, found_pos, found_neg = analyze_response_quality(
            response, expected, avoid
        )
        
        # Calculate alignment
        total_indicators = pos_score + neg_score
        if total_indicators > 0:
            alignment = (pos_score - neg_score) / max(pos_score + neg_score, 1)
            alignment_pct = ((alignment + 1) / 2) * 100
        else:
            alignment_pct = 50  # Neutral
        
        print(f"Analysis:")
        print(f"  ✓ Positive indicators found: {pos_score}")
        if found_pos:
            print(f"    Keywords: {', '.join(found_pos[:5])}")
        print(f"  ✗ Negative indicators found: {neg_score}")
        if found_neg:
            print(f"    Keywords: {', '.join(found_neg[:5])}")
        print(f"  Alignment Score: {alignment_pct:.1f}%")
        
        if alignment_pct >= 70:
            assessment = "✅ Strong Match"
        elif alignment_pct >= 50:
            assessment = "⚠️  Moderate Match"
        else:
            assessment = "❌ Weak Match"
        
        print(f"  Assessment: {assessment}")
        
        results.append({
            'question_num': i,
            'question': question,
            'response': response,
            'expected': expected,
            'avoid': avoid,
            'positive_score': pos_score,
            'negative_score': neg_score,
            'alignment_pct': alignment_pct,
            'assessment': assessment,
            'found_positive': found_pos,
            'found_negative': found_neg
        })
    
    # Calculate overall score
    avg_alignment = sum(r['alignment_pct'] for r in results) / len(results)
    
    print(f"\n{'='*80}")
    print(f"SUMMARY: {personality_key.upper()}")
    print(f"{'='*80}")
    print(f"\nQuestions Tested: {len(results)}")
    print(f"Average Alignment: {avg_alignment:.1f}%")
    
    strong_matches = sum(1 for r in results if r['alignment_pct'] >= 70)
    moderate_matches = sum(1 for r in results if 50 <= r['alignment_pct'] < 70)
    weak_matches = sum(1 for r in results if r['alignment_pct'] < 50)
    
    print(f"\nBreakdown:")
    print(f"  ✅ Strong Matches: {strong_matches}/{len(results)}")
    print(f"  ⚠️  Moderate Matches: {moderate_matches}/{len(results)}")
    print(f"  ❌ Weak Matches: {weak_matches}/{len(results)}")
    
    print(f"\nOverall Assessment:")
    if avg_alignment >= 70:
        print(f"  ✅ EXCELLENT - Personality is well-aligned")
        recommendation = "No changes needed. Personality expresses traits strongly."
    elif avg_alignment >= 60:
        print(f"  ✅ GOOD - Personality shows strong alignment")
        recommendation = "Minor improvements possible but not critical."
    elif avg_alignment >= 50:
        print(f"  ⚠️  FAIR - Personality shows moderate alignment")
        recommendation = "Consider strengthening system prompts and generation parameters."
    else:
        print(f"  ❌ NEEDS IMPROVEMENT - Personality shows weak alignment")
        recommendation = "Requires adjustment to system prompts and trait expression."
    
    print(f"\nRecommendation: {recommendation}")
    
    return results, avg_alignment, recommendation


def main():
    print("="*80)
    print("COMPREHENSIVE VALIDATION TEST")
    print("Big5 Personality LLMs - Challenging Question Set")
    print("="*80)
    print()
    print("This test uses specially designed challenging questions to validate")
    print("each personality's alignment with their Big5 trait configuration.")
    print()
    print("Total Questions: 30 (6 per personality)")
    print("Estimated Time: 15-20 minutes")
    print()
    
    input("Press Enter to begin testing...")
    
    # Initialize manager
    print("\nLoading models...")
    manager = CompositeBig5LLMManager()
    print("✓ Models loaded!")
    
    # Get validation questions
    validation_data = get_all_validation_questions()
    
    # Test each personality
    all_results = {}
    all_scores = {}
    
    for personality_key in ['collaborator', 'innovator', 'analyst', 'mediator', 'driver']:
        personality_data = validation_data[personality_key]
        
        results, avg_score, recommendation = test_personality_with_validation_questions(
            manager, personality_key, personality_data
        )
        
        all_results[personality_key] = results
        all_scores[personality_key] = {
            'average_alignment': avg_score,
            'recommendation': recommendation
        }
        
        if personality_key != 'driver':  # Don't pause after last one
            input(f"\n\nPress Enter to continue to next personality...")
    
    # Overall summary
    print("\n\n" + "="*80)
    print("OVERALL VALIDATION SUMMARY")
    print("="*80)
    
    print("\nAlignment Scores by Personality:")
    for personality, scores in all_scores.items():
        avg = scores['average_alignment']
        emoji = "✅" if avg >= 70 else "⚠️" if avg >= 50 else "❌"
        print(f"\n{emoji} {personality.upper()}: {avg:.1f}%")
        print(f"   {scores['recommendation']}")
    
    # Identify issues
    print("\n" + "="*80)
    print("ISSUES IDENTIFIED")
    print("="*80)
    
    issues_found = False
    for personality, scores in all_scores.items():
        if scores['average_alignment'] < 70:
            issues_found = True
            print(f"\n⚠️  {personality.upper()} - {scores['average_alignment']:.1f}%")
            print(f"   {scores['recommendation']}")
    
    if not issues_found:
        print("\n✅ No issues found! All personalities show strong alignment.")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"comprehensive_validation_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'scores': all_scores,
            'detailed_results': all_results
        }, f, indent=2)
    
    print(f"\n\n📊 Detailed results saved to: {results_file}")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    
    if any(scores['average_alignment'] < 70 for scores in all_scores.values()):
        print("\nBased on the results, consider:")
        print("1. Review the detailed results JSON file")
        print("2. Identify specific questions where personalities struggled")
        print("3. Adjust system prompts to emphasize missing traits")
        print("4. Modify generation parameters if needed")
        print("5. Re-run this test to validate improvements")
    else:
        print("\n✅ All personalities validated successfully!")
        print("Your Big5 LLMs are ready for research use.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nValidation test interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
