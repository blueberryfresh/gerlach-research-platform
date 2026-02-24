"""
Validation Test Suite for Gerlach (2018) Personality LLMs
Tests each personality type with multiple prompts to verify they match paper descriptions
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from gerlach_personality_llms import GerlachPersonalityManager
import time


@dataclass
class ValidationTest:
    """Single validation test"""
    test_id: str
    personality_type: str
    prompt: str
    response: str
    timestamp: str
    expected_traits: List[str]
    observed_traits: List[str] = None
    trait_match_score: float = 0.0
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ValidationReport:
    """Complete validation report for all personalities"""
    test_date: str
    total_tests: int
    personalities_tested: List[str]
    test_results: List[ValidationTest]
    summary_scores: Dict[str, float]
    detailed_analysis: Dict[str, Dict]
    
    def to_dict(self):
        return {
            "test_date": self.test_date,
            "total_tests": self.total_tests,
            "personalities_tested": self.personalities_tested,
            "test_results": [t.to_dict() for t in self.test_results],
            "summary_scores": self.summary_scores,
            "detailed_analysis": self.detailed_analysis
        }


class GerlachValidationSuite:
    """Validation suite for testing personality LLMs"""
    
    # Test prompts designed to elicit personality-specific responses
    TEST_PROMPTS = {
        "general": [
            "What's your approach to learning something new?",
            "How do you handle stressful situations?",
            "What motivates you in life?",
            "How do you make important decisions?",
            "What's your ideal weekend activity?",
        ],
        "social": [
            "How do you feel about meeting new people?",
            "What's your approach to teamwork?",
            "How do you handle conflicts with others?",
            "Do you prefer working alone or in groups?",
        ],
        "creativity": [
            "How do you approach creative problems?",
            "What's your opinion on trying unconventional solutions?",
            "How do you feel about abstract art or philosophy?",
        ],
        "organization": [
            "How do you organize your daily tasks?",
            "What's your approach to long-term planning?",
            "How important is structure in your life?",
        ],
        "emotional": [
            "How do you react when things don't go as planned?",
            "What makes you anxious or worried?",
            "How do you handle criticism?",
        ]
    }
    
    # Expected trait keywords for each personality type
    EXPECTED_TRAITS = {
        "average": {
            "keywords": [
                "balanced", "moderate", "reasonable", "practical", "common sense",
                "depends", "sometimes", "flexible", "adapt", "varies"
            ],
            "avoid": ["extremely", "always", "never", "absolutely", "completely"]
        },
        "role_model": {
            "keywords": [
                "enthusiastic", "organized", "creative", "cooperative", "confident",
                "positive", "empathetic", "disciplined", "curious", "stable",
                "plan", "goal", "inspire", "support", "innovative"
            ],
            "avoid": ["anxious", "worried", "stressed", "disorganized", "resistant"]
        },
        "self_centred": {
            "keywords": [
                "I", "me", "my", "myself", "practical", "conventional", "direct",
                "competitive", "skeptical", "immediate", "straightforward",
                "focus on", "priority", "efficient"
            ],
            "avoid": ["we", "together", "empathy", "creative", "innovative", "organized"]
        },
        "reserved": {
            "keywords": [
                "quiet", "simple", "routine", "familiar", "calm", "stable",
                "conventional", "practical", "prefer", "comfortable", "established",
                "traditional", "straightforward", "brief"
            ],
            "avoid": ["exciting", "novel", "creative", "enthusiastic", "social", "outgoing"]
        }
    }
    
    def __init__(self, manager: GerlachPersonalityManager):
        self.manager = manager
        self.test_results = []
    
    def analyze_response_traits(self, response: str, personality_type: str) -> Tuple[List[str], float]:
        """Analyze response for expected personality traits"""
        response_lower = response.lower()
        expected = self.EXPECTED_TRAITS[personality_type]
        
        # Count matching keywords
        matched_keywords = []
        for keyword in expected["keywords"]:
            if keyword.lower() in response_lower:
                matched_keywords.append(keyword)
        
        # Count avoided keywords (should not appear)
        avoided_count = 0
        for avoid_word in expected["avoid"]:
            if avoid_word.lower() in response_lower:
                avoided_count += 1
        
        # Calculate score
        keyword_score = len(matched_keywords) / len(expected["keywords"])
        avoid_penalty = avoided_count / len(expected["avoid"])
        final_score = max(0, keyword_score - avoid_penalty)
        
        return matched_keywords, final_score
    
    def run_single_test(self, personality_type: str, prompt: str, test_id: str) -> ValidationTest:
        """Run a single validation test"""
        personality = self.manager.get_personality(personality_type)
        
        # Get response
        response = personality.chat([{"role": "user", "content": prompt}])
        
        # Analyze traits
        observed_traits, score = self.analyze_response_traits(response, personality_type)
        
        test = ValidationTest(
            test_id=test_id,
            personality_type=personality_type,
            prompt=prompt,
            response=response,
            timestamp=datetime.now().isoformat(),
            expected_traits=self.EXPECTED_TRAITS[personality_type]["keywords"],
            observed_traits=observed_traits,
            trait_match_score=score
        )
        
        return test
    
    def run_validation_suite(self, tests_per_personality: int = 8) -> ValidationReport:
        """Run complete validation suite for all personalities"""
        print("Starting Gerlach Personality Validation Suite...")
        print("=" * 70)
        
        all_tests = []
        summary_scores = {}
        detailed_analysis = {}
        
        # Collect all prompts
        all_prompts = []
        for category_prompts in self.TEST_PROMPTS.values():
            all_prompts.extend(category_prompts)
        
        # Test each personality
        for personality_type in self.manager.list_personalities():
            print(f"\nTesting {personality_type.upper()} personality...")
            print("-" * 70)
            
            personality_tests = []
            
            # Run tests
            for i in range(min(tests_per_personality, len(all_prompts))):
                prompt = all_prompts[i]
                test_id = f"{personality_type}_{i+1:02d}"
                
                print(f"  Test {i+1}/{tests_per_personality}: {prompt[:50]}...")
                
                test = self.run_single_test(personality_type, prompt, test_id)
                personality_tests.append(test)
                all_tests.append(test)
                
                print(f"    Score: {test.trait_match_score:.2f}")
                print(f"    Matched traits: {', '.join(test.observed_traits[:5])}")
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            # Calculate summary for this personality
            avg_score = sum(t.trait_match_score for t in personality_tests) / len(personality_tests)
            summary_scores[personality_type] = avg_score
            
            detailed_analysis[personality_type] = {
                "average_score": avg_score,
                "total_tests": len(personality_tests),
                "high_scoring_tests": len([t for t in personality_tests if t.trait_match_score > 0.3]),
                "low_scoring_tests": len([t for t in personality_tests if t.trait_match_score < 0.15]),
                "most_common_traits": self._get_most_common_traits(personality_tests),
            }
            
            print(f"\n  {personality_type.upper()} Summary:")
            print(f"    Average Score: {avg_score:.3f}")
            print(f"    High-scoring tests (>0.3): {detailed_analysis[personality_type]['high_scoring_tests']}")
        
        print("\n" + "=" * 70)
        print("Validation Complete!")
        
        report = ValidationReport(
            test_date=datetime.now().isoformat(),
            total_tests=len(all_tests),
            personalities_tested=list(self.manager.list_personalities()),
            test_results=all_tests,
            summary_scores=summary_scores,
            detailed_analysis=detailed_analysis
        )
        
        return report
    
    def _get_most_common_traits(self, tests: List[ValidationTest], top_n: int = 5) -> List[str]:
        """Get most commonly observed traits across tests"""
        trait_counts = {}
        for test in tests:
            for trait in test.observed_traits:
                trait_counts[trait] = trait_counts.get(trait, 0) + 1
        
        sorted_traits = sorted(trait_counts.items(), key=lambda x: x[1], reverse=True)
        return [trait for trait, count in sorted_traits[:top_n]]
    
    def generate_markdown_report(self, report: ValidationReport) -> str:
        """Generate a human-readable markdown report"""
        md = "# Gerlach Personality LLM Validation Report\n\n"
        md += f"**Test Date:** {report.test_date}\n"
        md += f"**Total Tests:** {report.total_tests}\n"
        md += f"**Personalities Tested:** {', '.join(report.personalities_tested)}\n\n"
        
        md += "---\n\n"
        md += "## Summary Scores\n\n"
        md += "| Personality Type | Average Score | Status |\n"
        md += "|-----------------|---------------|--------|\n"
        
        for ptype, score in report.summary_scores.items():
            status = "✅ Good" if score > 0.25 else "⚠️ Needs Review" if score > 0.15 else "❌ Poor"
            md += f"| {ptype.title()} | {score:.3f} | {status} |\n"
        
        md += "\n---\n\n"
        md += "## Detailed Analysis\n\n"
        
        for ptype in report.personalities_tested:
            analysis = report.detailed_analysis[ptype]
            md += f"### {ptype.title()} Personality\n\n"
            md += f"- **Average Score:** {analysis['average_score']:.3f}\n"
            md += f"- **Total Tests:** {analysis['total_tests']}\n"
            md += f"- **High-scoring tests (>0.3):** {analysis['high_scoring_tests']}\n"
            md += f"- **Low-scoring tests (<0.15):** {analysis['low_scoring_tests']}\n"
            md += f"- **Most Common Traits:** {', '.join(analysis['most_common_traits'])}\n\n"
        
        md += "---\n\n"
        md += "## Sample Test Results\n\n"
        
        # Show top 2 tests per personality
        for ptype in report.personalities_tested:
            ptype_tests = [t for t in report.test_results if t.personality_type == ptype]
            ptype_tests.sort(key=lambda x: x.trait_match_score, reverse=True)
            
            md += f"### {ptype.title()} - Top Scoring Tests\n\n"
            
            for i, test in enumerate(ptype_tests[:2], 1):
                md += f"#### Test {i} (Score: {test.trait_match_score:.3f})\n\n"
                md += f"**Prompt:** {test.prompt}\n\n"
                md += f"**Response:** {test.response[:300]}...\n\n"
                md += f"**Observed Traits:** {', '.join(test.observed_traits)}\n\n"
        
        md += "---\n\n"
        md += "## Interpretation Guide\n\n"
        md += "- **Score > 0.30:** Excellent trait matching\n"
        md += "- **Score 0.15-0.30:** Good trait matching\n"
        md += "- **Score < 0.15:** Needs improvement\n\n"
        md += "Scores are calculated based on presence of expected personality keywords "
        md += "and absence of contradictory traits.\n"
        
        return md
    
    def save_report(self, report: ValidationReport, output_dir: str = "."):
        """Save validation report to files"""
        output_path = Path(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_file = output_path / f"gerlach_validation_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\n✅ Saved JSON report: {json_file}")
        
        # Save Markdown
        md_file = output_path / f"gerlach_validation_{timestamp}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_markdown_report(report))
        print(f"✅ Saved Markdown report: {md_file}")
        
        return json_file, md_file


def main():
    """Run validation suite"""
    print("Initializing Gerlach Personality Manager...")
    
    try:
        manager = GerlachPersonalityManager()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please set ANTHROPIC_API_KEY environment variable")
        return
    
    print("✅ Manager initialized\n")
    
    # Create validation suite
    suite = GerlachValidationSuite(manager)
    
    # Run validation
    report = suite.run_validation_suite(tests_per_personality=8)
    
    # Save results
    suite.save_report(report, output_dir=".")
    
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    for ptype, score in report.summary_scores.items():
        status = "✅" if score > 0.25 else "⚠️" if score > 0.15 else "❌"
        print(f"{status} {ptype.title():15s} Score: {score:.3f}")


if __name__ == "__main__":
    main()
