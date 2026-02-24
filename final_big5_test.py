#!/usr/bin/env python3
"""
Final Big5 Personality Validation Test
Comprehensive test to validate that the LLMs exhibit proper Big5 personality traits
"""

import sys
import json
import re
from typing import Dict, List, Tuple
from improved_big5_llms import ImprovedBig5LLMManager


def analyze_personality_traits(response: str, personality: str) -> Dict:
    """Analyze response for specific Big5 personality traits"""
    
    # Enhanced personality trait indicators based on Big5 research
    trait_indicators = {
        "openness": {
            "creativity": ["creative", "innovative", "original", "unique", "artistic", "imaginative"],
            "curiosity": ["curious", "explore", "discover", "learn", "new", "different"],
            "abstract_thinking": ["abstract", "theoretical", "philosophical", "conceptual", "ideas"],
            "aesthetic_appreciation": ["beautiful", "art", "music", "culture", "aesthetic"],
            "unconventional": ["unconventional", "alternative", "non-traditional", "experimental"]
        },
        "conscientiousness": {
            "organization": ["organized", "systematic", "structured", "methodical", "planned"],
            "discipline": ["disciplined", "focused", "dedicated", "committed", "persistent"],
            "responsibility": ["responsible", "reliable", "dependable", "accountable", "duty"],
            "achievement": ["goal", "accomplish", "achieve", "success", "efficient", "productive"],
            "self_control": ["control", "manage", "regulate", "careful", "thoughtful"]
        },
        "extraversion": {
            "sociability": ["social", "people", "friends", "together", "group", "community"],
            "assertiveness": ["confident", "assertive", "leadership", "direct", "bold"],
            "energy": ["energetic", "active", "dynamic", "enthusiastic", "vibrant"],
            "positive_emotions": ["happy", "excited", "optimistic", "cheerful", "joyful"],
            "communication": ["talk", "discuss", "share", "communicate", "express"]
        },
        "agreeableness": {
            "cooperation": ["cooperate", "collaborate", "teamwork", "together", "partnership"],
            "trust": ["trust", "honest", "sincere", "genuine", "reliable"],
            "empathy": ["understand", "empathy", "compassion", "caring", "support"],
            "altruism": ["help", "assist", "volunteer", "service", "giving"],
            "harmony": ["harmony", "peace", "agreement", "consensus", "balance"]
        },
        "neuroticism": {
            "anxiety": ["anxious", "worried", "nervous", "stress", "tension"],
            "emotional_instability": ["emotional", "moody", "unstable", "reactive", "sensitive"],
            "vulnerability": ["vulnerable", "fragile", "overwhelmed", "pressure", "burden"],
            "negative_emotions": ["sad", "angry", "frustrated", "disappointed", "upset"],
            "self_doubt": ["doubt", "uncertain", "insecure", "questioning", "hesitant"]
        }
    }
    
    if personality not in trait_indicators:
        return {"error": "Unknown personality type"}
    
    response_lower = response.lower()
    personality_traits = trait_indicators[personality]
    
    # Count matches for each trait category
    trait_scores = {}
    total_matches = 0
    
    for trait_category, keywords in personality_traits.items():
        matches = sum(1 for keyword in keywords if keyword in response_lower)
        trait_scores[trait_category] = {
            "matches": matches,
            "total_keywords": len(keywords),
            "score": matches / len(keywords) if keywords else 0
        }
        total_matches += matches
    
    # Calculate overall personality score
    total_keywords = sum(len(keywords) for keywords in personality_traits.values())
    overall_score = total_matches / total_keywords if total_keywords > 0 else 0
    
    # Determine strength of personality expression
    if overall_score >= 0.15:
        strength = "Strong"
    elif overall_score >= 0.08:
        strength = "Moderate"
    elif overall_score >= 0.03:
        strength = "Weak"
    else:
        strength = "Minimal"
    
    return {
        "overall_score": overall_score,
        "strength": strength,
        "trait_scores": trait_scores,
        "total_matches": total_matches,
        "response_length": len(response)
    }


def test_personality_scenarios():
    """Test personalities with scenarios designed to elicit specific traits"""
    
    print("🧪 PERSONALITY SCENARIO TESTING")
    print("=" * 50)
    
    # Scenarios designed to trigger specific personality responses
    test_scenarios = [
        {
            "scenario": "Creative Problem Solving",
            "prompt": "You need to come up with a solution for reducing plastic waste in your community. What's your approach?",
            "target_traits": {
                "openness": ["creative", "innovative", "unique", "artistic", "unconventional"],
                "conscientiousness": ["systematic", "organized", "planned", "methodical", "structured"],
                "extraversion": ["community", "people", "collaborate", "social", "together"],
                "agreeableness": ["help", "cooperation", "community", "together", "support"],
                "neuroticism": ["concern", "worry", "problem", "careful", "risk"]
            }
        },
        {
            "scenario": "Personal Development",
            "prompt": "What's the most important thing for personal growth and self-improvement?",
            "target_traits": {
                "openness": ["learn", "explore", "new", "growth", "experience"],
                "conscientiousness": ["discipline", "goal", "systematic", "planned", "achievement"],
                "extraversion": ["social", "people", "communication", "feedback", "interaction"],
                "agreeableness": ["understanding", "empathy", "help", "support", "caring"],
                "neuroticism": ["self-doubt", "worry", "emotional", "stress", "pressure"]
            }
        },
        {
            "scenario": "Work Environment",
            "prompt": "Describe your ideal work environment and what makes you most productive.",
            "target_traits": {
                "openness": ["creative", "flexible", "innovative", "variety", "new"],
                "conscientiousness": ["organized", "structured", "efficient", "systematic", "focused"],
                "extraversion": ["collaborative", "team", "social", "interactive", "communication"],
                "agreeableness": ["supportive", "cooperative", "harmony", "friendly", "helpful"],
                "neuroticism": ["quiet", "stable", "predictable", "low-stress", "comfortable"]
            }
        }
    ]
    
    manager = ImprovedBig5LLMManager()
    
    scenario_results = {}
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario['scenario']}")
        print(f"Prompt: {scenario['prompt']}")
        print("-" * 80)
        
        responses = manager.get_all_responses(scenario['prompt'])
        scenario_data = {}
        
        for personality, response in responses.items():
            print(f"\n🎭 {personality.upper()}:")
            print(f"Response: {response[:200]}...")
            
            # Analyze personality traits in response
            analysis = analyze_personality_traits(response, personality)
            scenario_data[personality] = {
                'response': response,
                'analysis': analysis
            }
            
            print(f"Personality Score: {analysis['overall_score']:.3f} ({analysis['strength']})")
            
            # Show strongest trait categories
            best_traits = sorted(analysis['trait_scores'].items(), 
                               key=lambda x: x[1]['score'], reverse=True)[:2]
            
            for trait_name, trait_data in best_traits:
                if trait_data['score'] > 0:
                    print(f"  - {trait_name}: {trait_data['score']:.3f} ({trait_data['matches']} matches)")
        
        scenario_results[scenario['scenario']] = scenario_data
    
    return scenario_results


def test_personality_consistency():
    """Test consistency of personality expression across multiple responses"""
    
    print(f"\n🔄 PERSONALITY CONSISTENCY TEST")
    print("=" * 50)
    
    manager = ImprovedBig5LLMManager()
    
    consistency_prompts = [
        "What's your philosophy on life?",
        "How do you make important decisions?",
        "What brings you the most satisfaction?"
    ]
    
    consistency_results = {}
    
    for personality in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
        print(f"\n🎭 Testing {personality.upper()} consistency...")
        
        personality_scores = []
        responses = []
        
        for prompt in consistency_prompts:
            response = manager.get_response(personality, prompt)
            responses.append(response)
            
            analysis = analyze_personality_traits(response, personality)
            personality_scores.append(analysis['overall_score'])
            
            print(f"  Prompt: {prompt}")
            print(f"  Score: {analysis['overall_score']:.3f}")
        
        # Calculate consistency metrics
        avg_score = sum(personality_scores) / len(personality_scores)
        score_variance = sum((score - avg_score) ** 2 for score in personality_scores) / len(personality_scores)
        consistency_score = 1.0 - min(score_variance * 10, 1.0)  # Normalize variance to 0-1 scale
        
        consistency_results[personality] = {
            'average_score': avg_score,
            'score_variance': score_variance,
            'consistency_score': consistency_score,
            'individual_scores': personality_scores
        }
        
        print(f"  Average Score: {avg_score:.3f}")
        print(f"  Consistency: {consistency_score:.3f}")
    
    return consistency_results


def generate_final_assessment(scenario_results: Dict, consistency_results: Dict):
    """Generate comprehensive assessment of Big5 personality implementation"""
    
    print(f"\n" + "=" * 60)
    print("📊 FINAL BIG5 PERSONALITY ASSESSMENT")
    print("=" * 60)
    
    # Calculate overall scores for each personality
    personality_assessments = {}
    
    for personality in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
        # Collect scores from all scenarios
        scenario_scores = []
        for scenario_name, scenario_data in scenario_results.items():
            if personality in scenario_data:
                scenario_scores.append(scenario_data[personality]['analysis']['overall_score'])
        
        avg_scenario_score = sum(scenario_scores) / len(scenario_scores) if scenario_scores else 0
        consistency_score = consistency_results[personality]['consistency_score']
        avg_personality_score = consistency_results[personality]['average_score']
        
        # Combined assessment score
        combined_score = (avg_scenario_score + avg_personality_score + consistency_score) / 3
        
        personality_assessments[personality] = {
            'scenario_score': avg_scenario_score,
            'consistency_score': consistency_score,
            'personality_score': avg_personality_score,
            'combined_score': combined_score
        }
    
    # Display results
    print(f"\n{'Personality':<15} | {'Scenarios':<10} | {'Consistency':<11} | {'Expression':<10} | {'Overall':<8} | {'Grade'}")
    print("-" * 80)
    
    overall_scores = []
    
    for personality, scores in personality_assessments.items():
        scenario_score = scores['scenario_score']
        consistency_score = scores['consistency_score']
        personality_score = scores['personality_score']
        combined_score = scores['combined_score']
        
        overall_scores.append(combined_score)
        
        # Assign grade
        if combined_score >= 0.15:
            grade = "A (Excellent)"
        elif combined_score >= 0.10:
            grade = "B (Good)"
        elif combined_score >= 0.06:
            grade = "C (Fair)"
        elif combined_score >= 0.03:
            grade = "D (Poor)"
        else:
            grade = "F (Fail)"
        
        print(f"{personality.title():<15} | {scenario_score:<10.3f} | {consistency_score:<11.3f} | {personality_score:<10.3f} | {combined_score:<8.3f} | {grade}")
    
    # Overall system assessment
    system_average = sum(overall_scores) / len(overall_scores)
    
    print(f"\n🎯 SYSTEM PERFORMANCE")
    print("-" * 30)
    print(f"Average Score: {system_average:.3f}")
    
    if system_average >= 0.12:
        system_grade = "🎉 EXCELLENT - Your Big5 LLMs show strong personality differentiation!"
        recommendations = [
            "✅ Personalities are well-differentiated and consistent",
            "✅ Consider fine-tuning for even better performance",
            "✅ Ready for practical applications and research"
        ]
    elif system_average >= 0.08:
        system_grade = "👍 GOOD - Your Big5 LLMs show clear personality traits!"
        recommendations = [
            "✅ Personalities are distinguishable with room for improvement",
            "💡 Consider enhancing prompt engineering",
            "💡 Experiment with different generation parameters"
        ]
    elif system_average >= 0.05:
        system_grade = "⚠️ FAIR - Personality traits are present but weak"
        recommendations = [
            "💡 Strengthen personality-specific prompts",
            "💡 Adjust generation parameters for more distinct responses",
            "💡 Consider using larger base models"
        ]
    else:
        system_grade = "❌ NEEDS IMPROVEMENT - Personality differentiation is minimal"
        recommendations = [
            "🔧 Review personality prompt engineering",
            "🔧 Consider different base models (GPT-2 medium/large)",
            "🔧 Implement more sophisticated personality modeling"
        ]
    
    print(f"\n{system_grade}")
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in recommendations:
        print(f"   {rec}")
    
    # Save detailed results
    results_summary = {
        'system_average': system_average,
        'personality_assessments': personality_assessments,
        'scenario_results': scenario_results,
        'consistency_results': consistency_results,
        'recommendations': recommendations
    }
    
    with open('c:/Users/blueb/Desktop/Big5/final_assessment_results.json', 'w') as f:
        json.dump(results_summary, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to final_assessment_results.json")
    
    return system_average >= 0.05


def main():
    """Run comprehensive Big5 personality validation"""
    
    print("🧠 COMPREHENSIVE BIG5 PERSONALITY VALIDATION")
    print("=" * 60)
    print("This test validates that your LLMs exhibit proper Big Five personality traits")
    print("based on established psychological research.\n")
    
    try:
        # Run scenario tests
        scenario_results = test_personality_scenarios()
        
        # Run consistency tests
        consistency_results = test_personality_consistency()
        
        # Generate final assessment
        success = generate_final_assessment(scenario_results, consistency_results)
        
        if success:
            print(f"\n🎊 VALIDATION SUCCESSFUL!")
            print("Your Big5 LLMs demonstrate measurable personality differentiation.")
        else:
            print(f"\n⚠️ VALIDATION INCOMPLETE")
            print("Consider the recommendations above to improve personality expression.")
        
        return success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
