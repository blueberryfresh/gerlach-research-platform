#!/usr/bin/env python3
"""
Big5 Personality Validation Test
Tests if the LLMs actually exhibit Big Five personality traits as expected
"""

import sys
import json
from typing import Dict, List, Tuple
import re


def simple_big5_test():
    """Simple test without heavy dependencies"""
    print("🧠 Big5 Personality Validation Test")
    print("=" * 50)
    
    # Test prompts designed to elicit personality-specific responses
    test_scenarios = [
        {
            "prompt": "How do you approach solving a complex problem?",
            "expected_traits": {
                "openness": ["creative", "innovative", "different", "unique", "explore"],
                "conscientiousness": ["systematic", "organized", "step", "plan", "structure"],
                "extraversion": ["collaborate", "discuss", "team", "others", "together"],
                "agreeableness": ["understand", "consider", "everyone", "together", "help"],
                "neuroticism": ["careful", "worry", "risk", "concern", "might"]
            }
        },
        {
            "prompt": "What's your ideal way to spend a weekend?",
            "expected_traits": {
                "openness": ["art", "museum", "creative", "new", "explore"],
                "conscientiousness": ["productive", "organize", "plan", "accomplish", "goals"],
                "extraversion": ["friends", "social", "party", "people", "out"],
                "agreeableness": ["family", "help", "volunteer", "community", "others"],
                "neuroticism": ["quiet", "home", "safe", "comfortable", "peaceful"]
            }
        },
        {
            "prompt": "How do you handle criticism?",
            "expected_traits": {
                "openness": ["learn", "perspective", "growth", "feedback", "improve"],
                "conscientiousness": ["analyze", "systematic", "improve", "plan", "better"],
                "extraversion": ["discuss", "talk", "understand", "communicate", "clarify"],
                "agreeableness": ["appreciate", "understand", "consider", "respect", "value"],
                "neuroticism": ["difficult", "upset", "worry", "stress", "hard"]
            }
        }
    ]
    
    try:
        # Import our models
        from big5_personality_llms import Big5LLMManager
        
        print("✅ Successfully imported Big5LLMManager")
        print("🔄 Initializing personality models...")
        
        manager = Big5LLMManager()
        print("✅ Models initialized successfully!")
        
        # Run personality validation tests
        results = {}
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 Test Scenario {i}: {scenario['prompt']}")
            print("-" * 60)
            
            responses = manager.get_all_responses(scenario['prompt'])
            scenario_results = {}
            
            for personality, response in responses.items():
                print(f"\n🎭 {personality.upper()}:")
                print(f"Response: {response[:150]}...")
                
                # Check for expected personality traits
                expected_words = scenario['expected_traits'][personality]
                response_lower = response.lower()
                
                found_traits = []
                for trait_word in expected_words:
                    if trait_word in response_lower:
                        found_traits.append(trait_word)
                
                trait_score = len(found_traits) / len(expected_words)
                scenario_results[personality] = {
                    'score': trait_score,
                    'found_traits': found_traits,
                    'response_length': len(response)
                }
                
                print(f"Trait Score: {trait_score:.2f} ({len(found_traits)}/{len(expected_words)} expected traits found)")
                if found_traits:
                    print(f"Found traits: {', '.join(found_traits)}")
            
            results[f"scenario_{i}"] = scenario_results
        
        # Overall analysis
        print("\n" + "=" * 60)
        print("📊 OVERALL PERSONALITY VALIDATION RESULTS")
        print("=" * 60)
        
        personality_scores = {}
        for personality in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            scores = []
            for scenario_key in results:
                scores.append(results[scenario_key][personality]['score'])
            
            avg_score = sum(scores) / len(scores)
            personality_scores[personality] = avg_score
            
            status = "✅ GOOD" if avg_score >= 0.3 else "⚠️ NEEDS IMPROVEMENT" if avg_score >= 0.1 else "❌ POOR"
            print(f"{personality.upper():15} | Score: {avg_score:.3f} | {status}")
        
        # Test distinctiveness
        print(f"\n🔍 DISTINCTIVENESS TEST")
        print("-" * 30)
        
        test_prompt = "Tell me about your approach to life"
        responses = manager.get_all_responses(test_prompt)
        
        unique_responses = len(set(responses.values()))
        total_responses = len(responses)
        
        distinctiveness_score = unique_responses / total_responses
        print(f"Unique responses: {unique_responses}/{total_responses}")
        print(f"Distinctiveness: {distinctiveness_score:.3f}")
        
        if distinctiveness_score >= 0.8:
            print("✅ Personalities are highly distinct")
        elif distinctiveness_score >= 0.6:
            print("⚠️ Personalities are moderately distinct")
        else:
            print("❌ Personalities are too similar")
        
        # Final assessment
        print(f"\n🎯 FINAL ASSESSMENT")
        print("-" * 20)
        
        avg_personality_score = sum(personality_scores.values()) / len(personality_scores)
        
        print(f"Average Personality Score: {avg_personality_score:.3f}")
        print(f"Distinctiveness Score: {distinctiveness_score:.3f}")
        
        if avg_personality_score >= 0.3 and distinctiveness_score >= 0.6:
            print("🎉 SUCCESS: Your Big5 LLMs are working well!")
        elif avg_personality_score >= 0.2 or distinctiveness_score >= 0.4:
            print("⚠️ PARTIAL SUCCESS: Models show some personality traits but could be improved")
        else:
            print("❌ NEEDS WORK: Models need better personality differentiation")
        
        # Save detailed results
        with open('c:/Users/blueb/Desktop/Big5/validation_results.json', 'w') as f:
            json.dump({
                'personality_scores': personality_scores,
                'distinctiveness_score': distinctiveness_score,
                'detailed_results': results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to validation_results.json")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def manual_personality_check():
    """Manual check for personality traits without running models"""
    print("\n🔍 MANUAL PERSONALITY TRAIT CHECK")
    print("=" * 50)
    
    personality_definitions = {
        "Openness": {
            "description": "Creative, curious, open to new experiences",
            "traits": ["imaginative", "artistic", "curious", "creative", "unconventional"],
            "behaviors": ["explores new ideas", "appreciates art", "thinks abstractly"]
        },
        "Conscientiousness": {
            "description": "Organized, disciplined, goal-oriented",
            "traits": ["organized", "responsible", "disciplined", "systematic", "efficient"],
            "behaviors": ["makes plans", "follows schedules", "pays attention to details"]
        },
        "Extraversion": {
            "description": "Social, energetic, assertive",
            "traits": ["outgoing", "energetic", "talkative", "assertive", "social"],
            "behaviors": ["seeks social interaction", "feels comfortable in groups", "expresses emotions openly"]
        },
        "Agreeableness": {
            "description": "Cooperative, trusting, empathetic",
            "traits": ["cooperative", "trusting", "helpful", "empathetic", "considerate"],
            "behaviors": ["helps others", "avoids conflict", "shows compassion"]
        },
        "Neuroticism": {
            "description": "Emotionally reactive, anxious, sensitive",
            "traits": ["anxious", "moody", "worrying", "sensitive", "stressed"],
            "behaviors": ["worries about problems", "gets upset easily", "feels overwhelmed"]
        }
    }
    
    for personality, info in personality_definitions.items():
        print(f"\n🎭 {personality}")
        print(f"Description: {info['description']}")
        print(f"Key traits: {', '.join(info['traits'])}")
        print(f"Typical behaviors: {', '.join(info['behaviors'])}")
    
    print(f"\n✅ These are the personality traits your LLMs should exhibit!")
    print(f"Run the full test to see how well your models match these expectations.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        manual_personality_check()
    else:
        success = simple_big5_test()
        if not success:
            print("\n💡 Try running with --manual flag to see expected personality traits")
            manual_personality_check()
