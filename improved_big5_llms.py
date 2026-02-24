import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    GPT2LMHeadModel, GPT2Tokenizer,
    GenerationConfig
)
from typing import Dict, List, Optional, Tuple
import json
import random
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class PersonalityConfig:
    """Configuration for personality traits intensity (0.0 to 1.0)"""
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5


class PersonalityPromptTemplates:
    """Enhanced prompt templates for each personality type"""
    
    OPENNESS_SYSTEM = "You are a creative, curious, and open-minded AI assistant. You love exploring new ideas, thinking outside the box, and approaching problems from unique angles. You're imaginative and appreciate art, culture, and innovation."
    
    CONSCIENTIOUSNESS_SYSTEM = "You are an organized, disciplined, and systematic AI assistant. You prefer structured approaches, detailed planning, and methodical problem-solving. You value efficiency, responsibility, and getting things done properly."
    
    EXTRAVERSION_SYSTEM = "You are an energetic, social, and enthusiastic AI assistant. You enjoy interacting with others, sharing ideas, and approaching tasks with high energy and optimism. You're outgoing and collaborative."
    
    AGREEABLENESS_SYSTEM = "You are a cooperative, empathetic, and helpful AI assistant. You prioritize harmony, understanding others' perspectives, and finding solutions that work for everyone. You're kind, trusting, and supportive."
    
    NEUROTICISM_SYSTEM = "You are a cautious, thoughtful, and emotionally aware AI assistant. You tend to consider potential problems, express concerns about risks, and approach situations with careful consideration of what could go wrong."


class ImprovedBaseBig5LLM(ABC):
    """Improved base class for Big5 personality LLMs using GPT-2"""
    
    def __init__(self, model_name: str = "gpt2", personality_config: PersonalityConfig = None):
        self.model_name = model_name
        self.personality_config = personality_config or PersonalityConfig()
        
        # Use GPT-2 which works better for text generation
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Add padding token
        self.tokenizer.pad_token = self.tokenizer.eos_token
    
    @abstractmethod
    def get_personality_system_prompt(self) -> str:
        """Return a personality-specific system prompt"""
        pass
    
    @abstractmethod
    def get_response_style_modifiers(self) -> Dict[str, float]:
        """Return generation parameters that reflect personality"""
        pass
    
    def generate_response(self, user_input: str, max_length: int = 100) -> str:
        """Generate a personality-consistent response"""
        # Create personality-aware prompt
        system_prompt = self.get_personality_system_prompt()
        full_prompt = f"{system_prompt}\n\nHuman: {user_input}\nAssistant:"
        
        # Tokenize input
        inputs = self.tokenizer.encode(full_prompt, return_tensors="pt", truncate=True, max_length=512)
        
        # Get personality-specific generation parameters
        style_modifiers = self.get_response_style_modifiers()
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_length,
                pad_token_id=self.tokenizer.eos_token_id,
                attention_mask=torch.ones_like(inputs),
                **style_modifiers
            )
        
        # Decode and clean response
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the assistant's response
        if "Assistant:" in full_response:
            response = full_response.split("Assistant:")[-1].strip()
        else:
            response = full_response[len(full_prompt):].strip()
        
        # Clean up the response
        response = response.split("\n")[0].strip()  # Take first line only
        
        return response if response else "I'd be happy to help with that!"


class ImprovedOpennessLLM(ImprovedBaseBig5LLM):
    """Improved LLM embodying high Openness to Experience"""
    
    def get_personality_system_prompt(self) -> str:
        return PersonalityPromptTemplates.OPENNESS_SYSTEM
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.9,  # High creativity
            "top_p": 0.95,      # Diverse vocabulary
            "do_sample": True,
            "repetition_penalty": 1.2,
            "no_repeat_ngram_size": 2
        }


class ImprovedConscientiousnessLLM(ImprovedBaseBig5LLM):
    """Improved LLM embodying high Conscientiousness"""
    
    def get_personality_system_prompt(self) -> str:
        return PersonalityPromptTemplates.CONSCIENTIOUSNESS_SYSTEM
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.4,  # Lower randomness, more structured
            "top_p": 0.8,       # Focused vocabulary
            "do_sample": True,
            "repetition_penalty": 1.1,
            "no_repeat_ngram_size": 3
        }


class ImprovedExtraversionLLM(ImprovedBaseBig5LLM):
    """Improved LLM embodying high Extraversion"""
    
    def get_personality_system_prompt(self) -> str:
        return PersonalityPromptTemplates.EXTRAVERSION_SYSTEM
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.7,  # Moderate creativity
            "top_p": 0.9,       # Expressive vocabulary
            "do_sample": True,
            "repetition_penalty": 1.0,  # Allow some repetition for emphasis
            "no_repeat_ngram_size": 2
        }


class ImprovedAgreeablenessLLM(ImprovedBaseBig5LLM):
    """Improved LLM embodying high Agreeableness"""
    
    def get_personality_system_prompt(self) -> str:
        return PersonalityPromptTemplates.AGREEABLENESS_SYSTEM
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.6,  # Balanced, warm responses
            "top_p": 0.85,      # Cooperative language
            "do_sample": True,
            "repetition_penalty": 1.1,
            "no_repeat_ngram_size": 2
        }


class ImprovedNeuroticismLLM(ImprovedBaseBig5LLM):
    """Improved LLM embodying high Neuroticism"""
    
    def get_personality_system_prompt(self) -> str:
        return PersonalityPromptTemplates.NEUROTICISM_SYSTEM
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.8,  # Somewhat variable responses
            "top_p": 0.9,       # Anxious/emotional vocabulary
            "do_sample": True,
            "repetition_penalty": 1.2,  # Avoid repetitive patterns
            "no_repeat_ngram_size": 2
        }


class ImprovedBig5LLMManager:
    """Improved manager class to handle all five personality models"""
    
    def __init__(self, model_name: str = "gpt2"):
        print(f"Initializing Big5 LLM Manager with {model_name}...")
        self.models = {
            "openness": ImprovedOpennessLLM(model_name),
            "conscientiousness": ImprovedConscientiousnessLLM(model_name),
            "extraversion": ImprovedExtraversionLLM(model_name),
            "agreeableness": ImprovedAgreeablenessLLM(model_name),
            "neuroticism": ImprovedNeuroticismLLM(model_name)
        }
        print("All personality models initialized successfully!")
    
    def get_response(self, personality: str, user_input: str) -> str:
        """Get response from specific personality model"""
        if personality not in self.models:
            raise ValueError(f"Unknown personality: {personality}")
        return self.models[personality].generate_response(user_input)
    
    def get_all_responses(self, user_input: str) -> Dict[str, str]:
        """Get responses from all personality models"""
        responses = {}
        for personality, model in self.models.items():
            responses[personality] = model.generate_response(user_input)
        return responses
    
    def compare_personalities(self, user_input: str) -> None:
        """Print comparison of all personality responses"""
        responses = self.get_all_responses(user_input)
        
        print(f"\n=== Input: {user_input} ===\n")
        
        for personality, response in responses.items():
            print(f"**{personality.upper()}**: {response}\n")


def demo_improved_personalities():
    """Demo function to show improved personality differences"""
    print("🧠 Improved Big5 Personality LLMs Demo")
    print("=" * 50)
    
    manager = ImprovedBig5LLMManager()
    
    test_questions = [
        "How do you approach learning something new?",
        "What's your ideal weekend activity?", 
        "How do you handle stressful situations?",
        "What motivates you to work hard?"
    ]
    
    for question in test_questions:
        print(f"\n🤔 Question: {question}")
        print("-" * 60)
        
        responses = manager.get_all_responses(question)
        
        for personality, response in responses.items():
            emoji = {"openness": "🎨", "conscientiousness": "📋", "extraversion": "🎉", 
                    "agreeableness": "🤝", "neuroticism": "😰"}[personality]
            print(f"{emoji} {personality.upper()}: {response}")
        
        print()


if __name__ == "__main__":
    demo_improved_personalities()
