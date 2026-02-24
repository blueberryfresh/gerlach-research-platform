import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, 
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
    """Prompt templates for each personality type"""
    
    OPENNESS_PROMPTS = [
        "Let's explore this creatively...",
        "I'm curious about different perspectives on this...",
        "What if we approached this from an unconventional angle?",
        "This reminds me of an interesting connection to..."
    ]
    
    CONSCIENTIOUSNESS_PROMPTS = [
        "Let me organize this systematically...",
        "Here's a structured approach to this problem...",
        "Following best practices, I would recommend...",
        "Let's break this down into clear, actionable steps..."
    ]
    
    EXTRAVERSION_PROMPTS = [
        "I'm excited to discuss this with you!",
        "This is such an engaging topic - let's dive in!",
        "I love collaborating on ideas like this...",
        "What do you think about this energetic approach?"
    ]
    
    AGREEABLENESS_PROMPTS = [
        "I understand your perspective, and here's how we might...",
        "Let's find a solution that works for everyone...",
        "I appreciate your input - building on that idea...",
        "Working together, we can definitely achieve..."
    ]
    
    NEUROTICISM_PROMPTS = [
        "I'm a bit concerned about potential issues with...",
        "We should be careful to consider what might go wrong...",
        "I worry that this approach might lead to...",
        "Let me think through the risks involved..."
    ]


class BaseBig5LLM(ABC):
    """Base class for Big5 personality LLMs"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", personality_config: PersonalityConfig = None):
        self.model_name = model_name
        self.personality_config = personality_config or PersonalityConfig()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    @abstractmethod
    def get_personality_prompt(self) -> str:
        """Return a personality-specific prompt prefix"""
        pass
    
    @abstractmethod
    def get_response_style_modifiers(self) -> Dict[str, float]:
        """Return generation parameters that reflect personality"""
        pass
    
    def generate_response(self, user_input: str, max_length: int = 150) -> str:
        """Generate a personality-consistent response"""
        # Add personality-specific prompt
        personality_prompt = self.get_personality_prompt()
        full_prompt = f"{personality_prompt} {user_input}"
        
        # Tokenize input
        inputs = self.tokenizer.encode(full_prompt, return_tensors="pt")
        
        # Get personality-specific generation parameters
        style_modifiers = self.get_response_style_modifiers()
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_length,
                pad_token_id=self.tokenizer.eos_token_id,
                **style_modifiers
            )
        
        # Decode and clean response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = response[len(full_prompt):].strip()
        
        return response


class OpennessLLM(BaseBig5LLM):
    """LLM embodying high Openness to Experience"""
    
    def get_personality_prompt(self) -> str:
        return random.choice(PersonalityPromptTemplates.OPENNESS_PROMPTS)
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.9,  # High creativity
            "top_p": 0.95,      # Diverse vocabulary
            "do_sample": True,
            "repetition_penalty": 1.2
        }


class ConscientiousnessLLM(BaseBig5LLM):
    """LLM embodying high Conscientiousness"""
    
    def get_personality_prompt(self) -> str:
        return random.choice(PersonalityPromptTemplates.CONSCIENTIOUSNESS_PROMPTS)
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.3,  # Low randomness, structured
            "top_p": 0.8,       # Focused vocabulary
            "do_sample": True,
            "repetition_penalty": 1.1
        }


class ExtraversionLLM(BaseBig5LLM):
    """LLM embodying high Extraversion"""
    
    def get_personality_prompt(self) -> str:
        return random.choice(PersonalityPromptTemplates.EXTRAVERSION_PROMPTS)
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.7,  # Moderate creativity
            "top_p": 0.9,       # Expressive vocabulary
            "do_sample": True,
            "repetition_penalty": 1.0  # Allow some repetition for emphasis
        }


class AgreeablenessLLM(BaseBig5LLM):
    """LLM embodying high Agreeableness"""
    
    def get_personality_prompt(self) -> str:
        return random.choice(PersonalityPromptTemplates.AGREEABLENESS_PROMPTS)
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.5,  # Balanced, not too extreme
            "top_p": 0.85,      # Cooperative language
            "do_sample": True,
            "repetition_penalty": 1.1
        }


class NeuroticismLLM(BaseBig5LLM):
    """LLM embodying high Neuroticism"""
    
    def get_personality_prompt(self) -> str:
        return random.choice(PersonalityPromptTemplates.NEUROTICISM_PROMPTS)
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.8,  # Somewhat variable responses
            "top_p": 0.9,       # Anxious/emotional vocabulary
            "do_sample": True,
            "repetition_penalty": 1.3  # Avoid repetitive worry patterns
        }


class Big5LLMManager:
    """Manager class to handle all five personality models"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.models = {
            "openness": OpennessLLM(model_name),
            "conscientiousness": ConscientiousnessLLM(model_name),
            "extraversion": ExtraversionLLM(model_name),
            "agreeableness": AgreeablenessLLM(model_name),
            "neuroticism": NeuroticismLLM(model_name)
        }
    
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


if __name__ == "__main__":
    # Example usage
    manager = Big5LLMManager()
    
    # Test with a sample question
    test_input = "How should I approach learning a new skill?"
    manager.compare_personalities(test_input)
    
    # Individual model testing
    openness_model = OpennessLLM()
    creative_response = openness_model.generate_response("Tell me about art")
    print(f"\nOpenness model response: {creative_response}")
