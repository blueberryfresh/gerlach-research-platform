import json
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from big5_personality_llms import Big5LLMManager


class PersonalityEvaluator:
    """Evaluation framework for Big5 personality LLMs"""
    
    def __init__(self, manager: Big5LLMManager):
        self.manager = manager
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Expected personality characteristics for evaluation
        self.personality_keywords = {
            "openness": [
                "creative", "imaginative", "curious", "artistic", "innovative", 
                "original", "unconventional", "abstract", "philosophical", "experimental"
            ],
            "conscientiousness": [
                "organized", "systematic", "disciplined", "structured", "methodical",
                "planned", "careful", "thorough", "responsible", "efficient"
            ],
            "extraversion": [
                "energetic", "social", "enthusiastic", "outgoing", "talkative",
                "assertive", "active", "engaging", "collaborative", "expressive"
            ],
            "agreeableness": [
                "cooperative", "helpful", "trusting", "empathetic", "understanding",
                "supportive", "kind", "considerate", "harmonious", "diplomatic"
            ],
            "neuroticism": [
                "anxious", "worried", "concerned", "stressed", "uncertain",
                "cautious", "apprehensive", "nervous", "emotional", "sensitive"
            ]
        }
    
    def evaluate_personality_consistency(self, test_prompts: List[str], num_samples: int = 5) -> Dict[str, float]:
        """Evaluate how consistently each model exhibits its target personality"""
        consistency_scores = {}
        
        for personality in self.manager.models.keys():
            scores = []
            
            for prompt in test_prompts:
                # Generate multiple responses for the same prompt
                responses = []
                for _ in range(num_samples):
                    response = self.manager.get_response(personality, prompt)
                    responses.append(response)
                
                # Calculate consistency score based on keyword presence
                keyword_scores = []
                target_keywords = self.personality_keywords[personality]
                
                for response in responses:
                    response_lower = response.lower()
                    keyword_count = sum(1 for keyword in target_keywords if keyword in response_lower)
                    keyword_scores.append(keyword_count / len(target_keywords))
                
                # Consistency is measured by variance in keyword scores
                consistency = 1.0 - np.var(keyword_scores) if len(keyword_scores) > 1 else 1.0
                scores.append(consistency)
            
            consistency_scores[personality] = np.mean(scores)
        
        return consistency_scores
    
    def evaluate_personality_distinctiveness(self, test_prompts: List[str]) -> Dict[str, Dict[str, float]]:
        """Evaluate how distinct each personality's responses are from others"""
        all_responses = {}
        
        # Collect responses from all personalities
        for prompt in test_prompts:
            responses = self.manager.get_all_responses(prompt)
            for personality, response in responses.items():
                if personality not in all_responses:
                    all_responses[personality] = []
                all_responses[personality].append(response)
        
        # Calculate pairwise similarities
        distinctiveness_scores = {}
        personalities = list(all_responses.keys())
        
        for i, personality1 in enumerate(personalities):
            distinctiveness_scores[personality1] = {}
            
            for j, personality2 in enumerate(personalities):
                if i != j:
                    # Combine all responses for each personality
                    text1 = " ".join(all_responses[personality1])
                    text2 = " ".join(all_responses[personality2])
                    
                    # Calculate TF-IDF similarity
                    tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
                    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                    
                    # Distinctiveness is inverse of similarity
                    distinctiveness_scores[personality1][personality2] = 1.0 - similarity
        
        return distinctiveness_scores
    
    def evaluate_personality_accuracy(self, test_prompts: List[str]) -> Dict[str, float]:
        """Evaluate how well each model exhibits expected personality traits"""
        accuracy_scores = {}
        
        for personality in self.manager.models.keys():
            target_keywords = self.personality_keywords[personality]
            total_score = 0
            
            for prompt in test_prompts:
                response = self.manager.get_response(personality, prompt)
                response_lower = response.lower()
                
                # Count target personality keywords
                keyword_matches = sum(1 for keyword in target_keywords if keyword in response_lower)
                
                # Count keywords from other personalities (should be lower)
                other_keyword_matches = 0
                for other_personality, other_keywords in self.personality_keywords.items():
                    if other_personality != personality:
                        other_keyword_matches += sum(1 for keyword in other_keywords if keyword in response_lower)
                
                # Calculate accuracy as ratio of target vs other personality keywords
                total_keywords = keyword_matches + other_keyword_matches
                if total_keywords > 0:
                    accuracy = keyword_matches / total_keywords
                else:
                    accuracy = 0.0
                
                total_score += accuracy
            
            accuracy_scores[personality] = total_score / len(test_prompts)
        
        return accuracy_scores
    
    def run_comprehensive_evaluation(self, test_prompts: List[str] = None) -> Dict[str, Dict[str, float]]:
        """Run all evaluation metrics"""
        if test_prompts is None:
            test_prompts = [
                "How do you approach solving problems?",
                "What's your opinion on taking risks?",
                "How do you handle stress?",
                "What motivates you in life?",
                "How do you make decisions?",
                "What's your ideal work environment?",
                "How do you handle criticism?",
                "What's your approach to learning new things?",
                "How do you interact with others?",
                "What are your thoughts on change?"
            ]
        
        results = {
            "consistency": self.evaluate_personality_consistency(test_prompts),
            "accuracy": self.evaluate_personality_accuracy(test_prompts),
            "distinctiveness_avg": {}
        }
        
        # Calculate average distinctiveness scores
        distinctiveness = self.evaluate_personality_distinctiveness(test_prompts)
        for personality in distinctiveness:
            avg_distinctiveness = np.mean(list(distinctiveness[personality].values()))
            results["distinctiveness_avg"][personality] = avg_distinctiveness
        
        return results
    
    def generate_evaluation_report(self, results: Dict[str, Dict[str, float]]) -> str:
        """Generate a formatted evaluation report"""
        report = "# Big5 Personality LLMs Evaluation Report\n\n"
        
        # Overall scores table
        report += "## Overall Performance Scores\n\n"
        report += "| Personality | Consistency | Accuracy | Distinctiveness |\n"
        report += "|-------------|-------------|----------|----------------|\n"
        
        for personality in results["consistency"].keys():
            consistency = results["consistency"][personality]
            accuracy = results["accuracy"][personality]
            distinctiveness = results["distinctiveness_avg"][personality]
            
            report += f"| {personality.title()} | {consistency:.3f} | {accuracy:.3f} | {distinctiveness:.3f} |\n"
        
        # Detailed analysis
        report += "\n## Detailed Analysis\n\n"
        
        report += "### Consistency Scores\n"
        report += "Measures how consistently each model exhibits its target personality traits:\n"
        for personality, score in results["consistency"].items():
            report += f"- **{personality.title()}**: {score:.3f}\n"
        
        report += "\n### Accuracy Scores\n"
        report += "Measures how well each model exhibits expected personality traits vs. others:\n"
        for personality, score in results["accuracy"].items():
            report += f"- **{personality.title()}**: {score:.3f}\n"
        
        report += "\n### Distinctiveness Scores\n"
        report += "Measures how distinct each personality's responses are from others:\n"
        for personality, score in results["distinctiveness_avg"].items():
            report += f"- **{personality.title()}**: {score:.3f}\n"
        
        return report


def run_evaluation_demo():
    """Demo function to run personality evaluation"""
    print("Initializing Big5 LLM Manager...")
    manager = Big5LLMManager()
    
    print("Setting up evaluator...")
    evaluator = PersonalityEvaluator(manager)
    
    print("Running comprehensive evaluation...")
    results = evaluator.run_comprehensive_evaluation()
    
    print("Generating report...")
    report = evaluator.generate_evaluation_report(results)
    
    # Save report to file
    with open("c:/Users/blueb/Desktop/Big5/evaluation_report.md", "w") as f:
        f.write(report)
    
    print("Evaluation complete! Report saved to evaluation_report.md")
    print("\n" + report)


if __name__ == "__main__":
    run_evaluation_demo()
