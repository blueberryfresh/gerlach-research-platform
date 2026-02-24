"""
Comprehensive Testing Framework for Composite Big5 Personality LLMs
Tests each personality with diverse prompts across multiple scenarios
"""

from composite_big5_llms import CompositeBig5LLMManager
from typing import Dict, List, Tuple
import json
from datetime import datetime


class CompositePersonalityTester:
    """Comprehensive tester for composite personalities"""
    
    def __init__(self):
        print("🧠 Initializing Composite Big5 Personality Testing Framework...")
        self.manager = CompositeBig5LLMManager()
        self.test_results = {}
        
        # Define comprehensive test scenarios
        self.test_scenarios = {
            "Work & Leadership": [
                "How do you approach a challenging project with tight deadlines?",
                "What's your leadership style when managing a team?",
                "How do you handle team members who disagree with your approach?",
                "Describe your ideal work environment.",
                "How do you prioritize tasks when everything seems urgent?"
            ],
            "Conflict & Disagreement": [
                "How do you handle conflict in a team setting?",
                "What do you do when someone criticizes your work?",
                "How do you respond when your idea is rejected?",
                "What's your approach to giving negative feedback?",
                "How do you deal with a colleague who isn't pulling their weight?"
            ],
            "Problem Solving": [
                "How do you approach solving a complex problem?",
                "What's your process for making important decisions?",
                "How do you handle uncertainty and ambiguity?",
                "Describe how you would tackle a problem you've never seen before.",
                "What do you do when your initial solution doesn't work?"
            ],
            "Collaboration & Social": [
                "How do you prefer to work - alone or with others?",
                "What role do you typically take in group projects?",
                "How do you build relationships with new team members?",
                "What's your approach to brainstorming sessions?",
                "How do you handle social events at work?"
            ],
            "Innovation & Change": [
                "How do you feel about trying new approaches?",
                "What's your reaction to sudden changes in plans?",
                "How do you balance innovation with proven methods?",
                "Describe your approach to creative thinking.",
                "How do you respond to new technologies or tools?"
            ],
            "Stress & Emotions": [
                "How do you handle stress and pressure?",
                "What do you do when you feel overwhelmed?",
                "How do you manage your emotions at work?",
                "What's your approach to work-life balance?",
                "How do you stay motivated during difficult times?"
            ],
            "Goals & Achievement": [
                "What motivates you to work hard?",
                "How do you set and track your goals?",
                "What does success mean to you?",
                "How do you celebrate achievements?",
                "What's your approach to personal development?"
            ],
            "Communication": [
                "How do you prefer to communicate with colleagues?",
                "What's your approach to presenting ideas?",
                "How do you ensure your message is understood?",
                "Describe your email communication style.",
                "How do you handle difficult conversations?"
            ]
        }
        
        # Expected trait indicators for each personality
        self.personality_indicators = {
            "collaborator": {
                "positive": ["team", "together", "cooperate", "support", "organize", "plan", "reliable", 
                           "structure", "help", "collaborate", "systematic", "everyone", "group"],
                "negative": ["alone", "individual", "compete", "conflict", "chaos"]
            },
            "innovator": {
                "positive": ["creative", "new", "innovative", "exciting", "explore", "bold", "opportunity",
                           "vision", "change", "different", "fresh", "experiment", "confident"],
                "negative": ["routine", "traditional", "worry", "anxious", "afraid", "conservative"]
            },
            "analyst": {
                "positive": ["analyze", "thorough", "detail", "research", "examine", "consider", "study",
                           "methodical", "precise", "data", "careful", "think", "reflect"],
                "negative": ["rush", "quick", "superficial", "social", "party", "crowd"]
            },
            "mediator": {
                "positive": ["understand", "empathy", "calm", "balance", "harmony", "peaceful", "listen",
                           "perspective", "compromise", "fair", "patient", "compassion"],
                "negative": ["conflict", "aggressive", "anxious", "stressed", "upset", "angry"]
            },
            "driver": {
                "positive": ["achieve", "goal", "result", "efficient", "direct", "decisive", "win",
                           "competitive", "lead", "push", "challenge", "ambitious", "assertive"],
                "negative": ["hesitate", "uncertain", "passive", "slow", "accommodate", "compromise"]
            }
        }
    
    def analyze_response_traits(self, response: str, personality: str) -> Dict:
        """Analyze if response contains expected personality traits"""
        response_lower = response.lower()
        indicators = self.personality_indicators[personality]
        
        positive_matches = [word for word in indicators["positive"] if word in response_lower]
        negative_matches = [word for word in indicators["negative"] if word in response_lower]
        
        positive_score = len(positive_matches) / len(indicators["positive"])
        negative_score = len(negative_matches) / len(indicators["negative"])
        
        return {
            "positive_matches": positive_matches,
            "negative_matches": negative_matches,
            "positive_score": positive_score,
            "negative_score": negative_score,
            "trait_alignment": positive_score - negative_score
        }
    
    def test_personality_scenario(self, personality: str, scenario: str, questions: List[str]) -> Dict:
        """Test a personality with a specific scenario"""
        print(f"\n{'='*70}")
        print(f"Testing {personality.upper()} - Scenario: {scenario}")
        print(f"{'='*70}")
        
        scenario_results = {
            "scenario": scenario,
            "questions": [],
            "avg_trait_alignment": 0.0
        }
        
        total_alignment = 0.0
        
        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}/{len(questions)}: {question}")
            
            # Get response
            response = self.manager.get_response(personality, question)
            print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
            
            # Analyze traits
            trait_analysis = self.analyze_response_traits(response, personality)
            total_alignment += trait_analysis["trait_alignment"]
            
            print(f"✓ Positive traits found: {', '.join(trait_analysis['positive_matches'][:5])}")
            if trait_analysis['negative_matches']:
                print(f"⚠ Negative traits found: {', '.join(trait_analysis['negative_matches'])}")
            print(f"Trait Alignment Score: {trait_analysis['trait_alignment']:.3f}")
            
            scenario_results["questions"].append({
                "question": question,
                "response": response,
                "trait_analysis": trait_analysis
            })
        
        scenario_results["avg_trait_alignment"] = total_alignment / len(questions)
        print(f"\n📊 Scenario Average Trait Alignment: {scenario_results['avg_trait_alignment']:.3f}")
        
        return scenario_results
    
    def test_all_personalities(self):
        """Run comprehensive tests on all personalities"""
        print("\n" + "="*70)
        print("🎭 COMPREHENSIVE COMPOSITE PERSONALITY TESTING")
        print("="*70)
        
        for personality in self.manager.list_personalities():
            config = self.manager.get_personality_info(personality)
            
            print(f"\n\n{'#'*70}")
            print(f"# TESTING: {config.name.upper()}")
            print(f"# Description: {config.description}")
            print(f"# Key Traits: {', '.join(config.key_traits)}")
            print(f"# Trait Scores - O:{config.openness} C:{config.conscientiousness} " +
                  f"E:{config.extraversion} A:{config.agreeableness} N:{config.neuroticism}")
            print(f"{'#'*70}")
            
            personality_results = {
                "name": config.name,
                "description": config.description,
                "traits": config.key_traits,
                "scenarios": [],
                "overall_alignment": 0.0
            }
            
            total_alignment = 0.0
            scenario_count = 0
            
            # Test each scenario
            for scenario, questions in self.test_scenarios.items():
                scenario_result = self.test_personality_scenario(personality, scenario, questions)
                personality_results["scenarios"].append(scenario_result)
                total_alignment += scenario_result["avg_trait_alignment"]
                scenario_count += 1
            
            personality_results["overall_alignment"] = total_alignment / scenario_count
            self.test_results[personality] = personality_results
            
            # Print summary
            print(f"\n{'='*70}")
            print(f"📊 {config.name.upper()} - OVERALL SUMMARY")
            print(f"{'='*70}")
            print(f"Overall Trait Alignment Score: {personality_results['overall_alignment']:.3f}")
            
            # Grade the personality
            alignment = personality_results['overall_alignment']
            if alignment >= 0.15:
                grade = "EXCELLENT ✅"
            elif alignment >= 0.10:
                grade = "GOOD ✓"
            elif alignment >= 0.05:
                grade = "FAIR ~"
            else:
                grade = "NEEDS IMPROVEMENT ⚠"
            
            print(f"Grade: {grade}")
            print(f"{'='*70}")
    
    def generate_comparison_report(self):
        """Generate a comparison report across all personalities"""
        print("\n\n" + "="*70)
        print("📊 COMPARATIVE ANALYSIS - ALL PERSONALITIES")
        print("="*70)
        
        print("\n{:<20} {:<15} {:<10}".format("Personality", "Alignment", "Grade"))
        print("-" * 70)
        
        for personality, results in self.test_results.items():
            alignment = results["overall_alignment"]
            
            if alignment >= 0.15:
                grade = "EXCELLENT ✅"
            elif alignment >= 0.10:
                grade = "GOOD ✓"
            elif alignment >= 0.05:
                grade = "FAIR ~"
            else:
                grade = "NEEDS IMPROVEMENT ⚠"
            
            print("{:<20} {:<15.3f} {:<10}".format(
                results["name"],
                alignment,
                grade
            ))
        
        print("\n" + "="*70)
    
    def test_specific_comparison(self, question: str):
        """Test all personalities with the same question for comparison"""
        print(f"\n{'='*70}")
        print(f"🔍 COMPARATIVE TEST")
        print(f"Question: {question}")
        print(f"{'='*70}")
        
        responses = self.manager.get_all_responses(question)
        
        for personality, response in responses.items():
            config = self.manager.get_personality_info(personality)
            trait_analysis = self.analyze_response_traits(response, personality)
            
            print(f"\n{config.name.upper()} ({config.description}):")
            print(f"Response: {response}")
            print(f"Trait Alignment: {trait_analysis['trait_alignment']:.3f}")
            print(f"Key Traits Found: {', '.join(trait_analysis['positive_matches'][:5])}")
            print("-" * 70)
    
    def save_results(self, filename: str = "composite_personality_test_results.json"):
        """Save test results to JSON file"""
        output = {
            "test_date": datetime.now().isoformat(),
            "results": self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Results saved to {filename}")


def main():
    """Run comprehensive personality testing"""
    tester = CompositePersonalityTester()
    
    print("\n" + "="*70)
    print("COMPOSITE BIG5 PERSONALITY LLM TESTING")
    print("="*70)
    print("\nThis will test each of the 5 composite personalities with:")
    print("- 8 different scenario categories")
    print("- 5 questions per scenario (40 total questions per personality)")
    print("- Trait alignment analysis for each response")
    print("\nTotal tests: 200 questions across all personalities")
    print("="*70)
    
    input("\nPress Enter to begin testing...")
    
    # Run comprehensive tests
    tester.test_all_personalities()
    
    # Generate comparison report
    tester.generate_comparison_report()
    
    # Save results
    tester.save_results()
    
    # Optional: Run specific comparison tests
    print("\n" + "="*70)
    print("ADDITIONAL COMPARATIVE TESTS")
    print("="*70)
    
    comparison_questions = [
        "How do you handle a team member who consistently misses deadlines?",
        "What's your approach to innovation versus stability?",
        "How do you make decisions under pressure?"
    ]
    
    for question in comparison_questions:
        tester.test_specific_comparison(question)
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE!")
    print("="*70)
    print("\nAll composite personalities have been thoroughly tested.")
    print("Review the results above to validate each personality type.")


if __name__ == "__main__":
    main()
