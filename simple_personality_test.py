#!/usr/bin/env python3
"""
Simple Personality Test for Big5 LLMs
Tests the personality models with a focus on debugging and validation
"""

import sys
import json
from typing import Dict, List


def test_basic_functionality():
    """Test basic model functionality first"""
    print("🔧 BASIC FUNCTIONALITY TEST")
    print("=" * 40)
    
    try:
        from big5_personality_llms import Big5LLMManager, OpennessLLM
        print("✅ Import successful")
        
        # Test single model first
        print("\n🎨 Testing Openness model...")
        openness_model = OpennessLLM()
        
        # Simple test
        test_input = "Hello"
        response = openness_model.generate_response(test_input, max_length=50)
        print(f"Input: '{test_input}'")
        print(f"Response: '{response}'")
        print(f"Response length: {len(response)} characters")
        
        if len(response.strip()) == 0:
            print("⚠️ Model is generating empty responses - this indicates a configuration issue")
            return False
        elif len(response.strip()) < 10:
            print("⚠️ Model is generating very short responses - may need adjustment")
        else:
            print("✅ Model is generating reasonable responses")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_personality_prompts():
    """Test with personality-specific prompts"""
    print("\n🎭 PERSONALITY PROMPT TEST")
    print("=" * 40)
    
    try:
        from big5_personality_llms import Big5LLMManager
        
        manager = Big5LLMManager()
        
        # Test prompts designed to elicit personality responses
        personality_prompts = {
            "openness": "Tell me about something creative you'd like to try",
            "conscientiousness": "How do you organize your daily tasks?", 
            "extraversion": "What's your favorite social activity?",
            "agreeableness": "How do you help others when they're struggling?",
            "neuroticism": "What worries you most about the future?"
        }
        
        results = {}
        
        for personality, prompt in personality_prompts.items():
            print(f"\n🎯 Testing {personality.upper()}")
            print(f"Prompt: {prompt}")
            
            response = manager.get_response(personality, prompt)
            print(f"Response: {response}")
            
            # Analyze response
            response_analysis = analyze_response_for_personality(response, personality)
            results[personality] = {
                'prompt': prompt,
                'response': response,
                'analysis': response_analysis
            }
            
            print(f"Analysis: {response_analysis['summary']}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def analyze_response_for_personality(response: str, personality: str) -> Dict:
    """Analyze if response matches expected personality traits"""
    
    # Define personality indicators
    personality_indicators = {
        "openness": {
            "positive": ["creative", "new", "different", "unique", "innovative", "artistic", "curious", "explore", "imagine"],
            "negative": ["routine", "traditional", "conventional", "same", "boring"]
        },
        "conscientiousness": {
            "positive": ["organized", "plan", "schedule", "systematic", "careful", "responsible", "goal", "structure", "efficient"],
            "negative": ["messy", "chaotic", "random", "careless", "lazy"]
        },
        "extraversion": {
            "positive": ["social", "people", "friends", "party", "talk", "energetic", "outgoing", "group", "together"],
            "negative": ["alone", "quiet", "solitary", "shy", "withdrawn"]
        },
        "agreeableness": {
            "positive": ["help", "kind", "caring", "support", "understand", "empathy", "cooperation", "harmony", "trust"],
            "negative": ["selfish", "mean", "conflict", "argue", "compete"]
        },
        "neuroticism": {
            "positive": ["worry", "stress", "anxious", "nervous", "concern", "fear", "upset", "emotional", "sensitive"],
            "negative": ["calm", "relaxed", "stable", "confident", "secure"]
        }
    }
    
    if personality not in personality_indicators:
        return {"summary": "Unknown personality type", "score": 0}
    
    indicators = personality_indicators[personality]
    response_lower = response.lower()
    
    positive_matches = sum(1 for word in indicators["positive"] if word in response_lower)
    negative_matches = sum(1 for word in indicators["negative"] if word in response_lower)
    
    # Calculate personality alignment score
    total_positive = len(indicators["positive"])
    total_negative = len(indicators["negative"])
    
    positive_score = positive_matches / total_positive if total_positive > 0 else 0
    negative_penalty = negative_matches / total_negative if total_negative > 0 else 0
    
    final_score = positive_score - (negative_penalty * 0.5)  # Negative words reduce score
    
    # Find matched words
    matched_positive = [word for word in indicators["positive"] if word in response_lower]
    matched_negative = [word for word in indicators["negative"] if word in response_lower]
    
    if final_score >= 0.2:
        summary = f"Strong {personality} traits detected"
    elif final_score >= 0.1:
        summary = f"Moderate {personality} traits detected"
    elif final_score > 0:
        summary = f"Weak {personality} traits detected"
    else:
        summary = f"No clear {personality} traits detected"
    
    return {
        "summary": summary,
        "score": final_score,
        "positive_matches": matched_positive,
        "negative_matches": matched_negative,
        "positive_count": positive_matches,
        "negative_count": negative_matches
    }


def test_personality_consistency():
    """Test if personalities give consistent responses"""
    print("\n🔄 PERSONALITY CONSISTENCY TEST")
    print("=" * 40)
    
    try:
        from big5_personality_llms import Big5LLMManager
        
        manager = Big5LLMManager()
        
        # Test same prompt multiple times
        test_prompt = "What motivates you in life?"
        print(f"Testing prompt: '{test_prompt}'")
        
        consistency_results = {}
        
        for personality in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            print(f"\n🎭 Testing {personality} consistency...")
            
            responses = []
            for i in range(3):  # Generate 3 responses
                response = manager.get_response(personality, test_prompt)
                responses.append(response)
                print(f"  Response {i+1}: {response[:100]}...")
            
            # Check if responses are different (good) but personality-consistent
            unique_responses = len(set(responses))
            consistency_results[personality] = {
                'responses': responses,
                'unique_count': unique_responses,
                'total_count': len(responses)
            }
            
            if unique_responses == len(responses):
                print(f"  ✅ All responses are unique (good variability)")
            elif unique_responses > 1:
                print(f"  ⚠️ Some responses are repeated")
            else:
                print(f"  ❌ All responses are identical")
        
        return consistency_results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def run_comprehensive_personality_test():
    """Run all personality tests"""
    print("🧠 COMPREHENSIVE BIG5 PERSONALITY TEST")
    print("=" * 50)
    
    # Step 1: Basic functionality
    basic_works = test_basic_functionality()
    if not basic_works:
        print("\n❌ Basic functionality test failed. Please check your setup.")
        return False
    
    # Step 2: Personality-specific prompts
    personality_results = test_personality_prompts()
    if not personality_results:
        print("\n❌ Personality prompt test failed.")
        return False
    
    # Step 3: Consistency test
    consistency_results = test_personality_consistency()
    
    # Step 4: Summary and recommendations
    print("\n" + "=" * 50)
    print("📊 FINAL ASSESSMENT")
    print("=" * 50)
    
    # Analyze personality results
    personality_scores = {}
    for personality, data in personality_results.items():
        score = data['analysis']['score']
        personality_scores[personality] = score
        
        status = "✅ GOOD" if score >= 0.2 else "⚠️ MODERATE" if score >= 0.1 else "❌ POOR"
        print(f"{personality.upper():15} | Score: {score:.3f} | {status}")
        
        if data['analysis']['positive_matches']:
            print(f"                | Found traits: {', '.join(data['analysis']['positive_matches'][:3])}")
    
    avg_score = sum(personality_scores.values()) / len(personality_scores)
    print(f"\nAverage Personality Score: {avg_score:.3f}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if avg_score >= 0.15:
        print("✅ Your Big5 LLMs are showing personality traits!")
        print("   - Models are responding with personality-appropriate content")
        print("   - Consider fine-tuning for even better results")
    elif avg_score >= 0.05:
        print("⚠️ Personality traits are weak but present")
        print("   - Try adjusting generation parameters (temperature, top_p)")
        print("   - Consider using different base models")
        print("   - Add more personality-specific prompt engineering")
    else:
        print("❌ Personality traits are not clearly evident")
        print("   - Check if the base model is working correctly")
        print("   - Verify prompt templates are being used")
        print("   - Consider using a different base model (GPT-2, etc.)")
    
    # Save results
    results_summary = {
        'personality_scores': personality_scores,
        'average_score': avg_score,
        'detailed_results': personality_results,
        'consistency_results': consistency_results
    }
    
    with open('c:/Users/blueb/Desktop/Big5/personality_test_results.json', 'w') as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"\n📄 Detailed results saved to personality_test_results.json")
    
    return avg_score >= 0.1


if __name__ == "__main__":
    success = run_comprehensive_personality_test()
    
    if success:
        print(f"\n🎉 Testing complete! Your Big5 LLMs show personality differentiation.")
    else:
        print(f"\n⚠️ Testing complete. Consider the recommendations above to improve personality expression.")
