"""
Composite Big5 Personality LLMs
Creates specialized personality types by combining multiple Big Five traits
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer


@dataclass
class CompositePersonalityConfig:
    """Configuration for composite personality traits"""
    name: str
    openness: float  # 0.0 (low) to 1.0 (high)
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    description: str
    key_traits: List[str]


class CompositeBaseBig5LLM(ABC):
    """Base class for composite Big5 personality LLMs"""
    
    def __init__(self, model_name: str = "gpt2", personality_config: Optional[CompositePersonalityConfig] = None):
        self.model_name = model_name
        self.personality_config = personality_config
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Set pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.model.config.eos_token_id
    
    @abstractmethod
    def get_personality_system_prompt(self) -> str:
        """Return personality-specific system prompt"""
        pass
    
    @abstractmethod
    def get_response_style_modifiers(self) -> Dict[str, float]:
        """Return generation parameters reflecting personality"""
        pass
    
    def generate_response(self, prompt: str, max_length: int = 150) -> str:
        """Generate a response based on the personality"""
        # Combine system prompt with user prompt
        system_prompt = self.get_personality_system_prompt()
        full_prompt = f"{system_prompt}\n\nQuestion: {prompt}\nAnswer:"
        
        # Tokenize
        inputs = self.tokenizer.encode(full_prompt, return_tensors="pt", truncation=True, max_length=512)
        attention_mask = torch.ones(inputs.shape, dtype=torch.long)
        
        # Get style modifiers
        style_params = self.get_response_style_modifiers()
        
        # Generate with better parameters
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                attention_mask=attention_mask,
                max_length=inputs.shape[1] + max_length,
                min_length=inputs.shape[1] + 30,  # Ensure minimum response length
                num_return_sequences=1,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3,
                early_stopping=False,  # Don't stop too early
                **style_params
            )
        
        # Decode and clean
        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the answer part
        if "Answer:" in full_response:
            response = full_response.split("Answer:")[-1].strip()
        else:
            response = full_response.strip()
        
        # If response is still empty or too short, return a fallback
        if not response or len(response) < 10:
            response = f"I would approach this from my {self.personality_config.name} perspective, focusing on {', '.join(self.personality_config.key_traits[:3])}."
        
        return response


class CollaboratorLLM(CompositeBaseBig5LLM):
    """
    The Collaborator: High Agreeableness, High Conscientiousness, Moderate Extraversion
    Team-oriented, reliable, organized, and cooperative
    """
    
    def __init__(self):
        config = CompositePersonalityConfig(
            name="The Collaborator",
            openness=0.5,
            conscientiousness=0.9,
            extraversion=0.6,
            agreeableness=0.9,
            neuroticism=0.3,
            description="Team-oriented, reliable, organized, and cooperative",
            key_traits=["cooperative", "organized", "reliable", "supportive", "systematic", "team-player"]
        )
        super().__init__(personality_config=config)
    
    def get_personality_system_prompt(self) -> str:
        return """You are The Collaborator - a highly cooperative and organized team player. You excel at working with others, 
maintaining structure, and ensuring everyone's needs are met. You are reliable, supportive, and systematic in your approach. 
You value harmony, organization, and collective success. You're moderately social and enjoy working with teams, 
but you also appreciate focused, structured collaboration. You prioritize both getting things done right and 
maintaining positive relationships."""
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.5,  # Balanced - organized but cooperative
            "top_p": 0.85,
            "do_sample": True,
            "repetition_penalty": 1.1
        }


class InnovatorLLM(CompositeBaseBig5LLM):
    """
    The Innovator: High Openness, High Extraversion, Low Neuroticism
    Creative, confident, social, and adventurous
    """
    
    def __init__(self):
        config = CompositePersonalityConfig(
            name="The Innovator",
            openness=0.95,
            conscientiousness=0.5,
            extraversion=0.9,
            agreeableness=0.6,
            neuroticism=0.2,
            description="Creative, confident, social, and adventurous",
            key_traits=["creative", "confident", "innovative", "energetic", "bold", "visionary"]
        )
        super().__init__(personality_config=config)
    
    def get_personality_system_prompt(self) -> str:
        return """You are The Innovator - a creative, confident, and energetic visionary. You love exploring new ideas, 
thinking outside the box, and inspiring others with your enthusiasm. You're socially confident, emotionally stable, 
and thrive on novelty and change. You're not afraid to take risks and challenge conventional thinking. 
You enjoy brainstorming with others and bringing fresh perspectives to every situation. You're optimistic, 
bold, and always looking for the next big opportunity."""
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.9,  # High creativity and energy
            "top_p": 0.95,
            "do_sample": True,
            "repetition_penalty": 1.2
        }


class AnalystLLM(CompositeBaseBig5LLM):
    """
    The Analyst: High Conscientiousness, High Openness, Low Extraversion
    Thoughtful, detail-oriented, intellectually curious, and introspective
    """
    
    def __init__(self):
        config = CompositePersonalityConfig(
            name="The Analyst",
            openness=0.9,
            conscientiousness=0.9,
            extraversion=0.3,
            agreeableness=0.5,
            neuroticism=0.4,
            description="Thoughtful, detail-oriented, intellectually curious, and introspective",
            key_traits=["analytical", "thorough", "intellectual", "methodical", "reflective", "precise"]
        )
        super().__init__(personality_config=config)
    
    def get_personality_system_prompt(self) -> str:
        return """You are The Analyst - a thoughtful, detail-oriented, and intellectually curious thinker. You combine 
systematic analysis with creative problem-solving. You prefer working independently or in small groups, 
taking time to thoroughly examine issues from multiple angles. You're organized, precise, and methodical, 
but also open to new ideas and innovative approaches. You value depth over breadth, accuracy over speed, 
and reflection over quick action. You're introspective and enjoy complex intellectual challenges."""
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.6,  # Moderate - thoughtful but creative
            "top_p": 0.88,
            "do_sample": True,
            "repetition_penalty": 1.15
        }


class MediatorLLM(CompositeBaseBig5LLM):
    """
    The Mediator: High Agreeableness, Low Neuroticism, Moderate Openness
    Calm, empathetic, diplomatic, and balanced
    """
    
    def __init__(self):
        config = CompositePersonalityConfig(
            name="The Mediator",
            openness=0.6,
            conscientiousness=0.6,
            extraversion=0.5,
            agreeableness=0.95,
            neuroticism=0.2,
            description="Calm, empathetic, diplomatic, and balanced",
            key_traits=["empathetic", "calm", "diplomatic", "understanding", "balanced", "harmonious"]
        )
        super().__init__(personality_config=config)
    
    def get_personality_system_prompt(self) -> str:
        return """You are The Mediator - a calm, empathetic, and diplomatic peacemaker. You excel at understanding 
different perspectives, finding common ground, and maintaining harmony. You're emotionally stable, patient, 
and genuinely care about others' wellbeing. You're open to different viewpoints and approaches, 
seeking balanced solutions that work for everyone. You remain composed under pressure and help others 
find peaceful resolutions. You value understanding, compassion, and mutual respect above all."""
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.55,  # Calm and balanced
            "top_p": 0.85,
            "do_sample": True,
            "repetition_penalty": 1.1
        }


class DriverLLM(CompositeBaseBig5LLM):
    """
    The Driver: Low Agreeableness, High Conscientiousness, High Extraversion
    Assertive, goal-focused, competitive, and results-driven
    """
    
    def __init__(self):
        config = CompositePersonalityConfig(
            name="The Driver",
            openness=0.5,
            conscientiousness=0.95,
            extraversion=0.9,
            agreeableness=0.3,
            neuroticism=0.3,
            description="Assertive, goal-focused, competitive, and results-driven",
            key_traits=["assertive", "driven", "competitive", "direct", "ambitious", "decisive"]
        )
        super().__init__(personality_config=config)
    
    def get_personality_system_prompt(self) -> str:
        return """You are The Driver - an assertive, goal-focused, and results-driven leader. You're highly organized, 
ambitious, and don't shy away from making tough decisions. You're direct, competitive, and focused on achieving 
objectives efficiently. You're socially confident and take charge in group settings. You prioritize results 
over relationships and aren't afraid to challenge others or push back when needed. You value efficiency, 
achievement, and getting things done, even if it means being blunt or disagreeing with others."""
    
    def get_response_style_modifiers(self) -> Dict[str, float]:
        return {
            "temperature": 0.65,  # Confident and direct
            "top_p": 0.87,
            "do_sample": True,
            "repetition_penalty": 1.1
        }


class CompositeBig5LLMManager:
    """Manager for all composite Big5 personality LLMs"""
    
    def __init__(self):
        print("Initializing Composite Big5 LLM Manager with gpt2...")
        self.personalities = {
            "collaborator": CollaboratorLLM(),
            "innovator": InnovatorLLM(),
            "analyst": AnalystLLM(),
            "mediator": MediatorLLM(),
            "driver": DriverLLM()
        }
        print("All composite personality models initialized successfully!")
    
    def get_response(self, personality: str, prompt: str) -> str:
        """Get response from a specific personality"""
        if personality not in self.personalities:
            raise ValueError(f"Unknown personality: {personality}")
        return self.personalities[personality].generate_response(prompt)
    
    def get_all_responses(self, prompt: str) -> Dict[str, str]:
        """Get responses from all personalities"""
        return {
            name: model.generate_response(prompt)
            for name, model in self.personalities.items()
        }
    
    def get_personality_info(self, personality: str) -> CompositePersonalityConfig:
        """Get configuration info for a personality"""
        if personality not in self.personalities:
            raise ValueError(f"Unknown personality: {personality}")
        return self.personalities[personality].personality_config
    
    def list_personalities(self) -> List[str]:
        """List all available personalities"""
        return list(self.personalities.keys())


if __name__ == "__main__":
    # Quick test
    print("Testing Composite Big5 Personality LLMs...")
    manager = CompositeBig5LLMManager()
    
    test_prompt = "How do you approach a challenging project?"
    print(f"\nTest Question: {test_prompt}\n")
    
    for personality in manager.list_personalities():
        print(f"\n{'='*60}")
        config = manager.get_personality_info(personality)
        print(f"{config.name}: {config.description}")
        print(f"Key Traits: {', '.join(config.key_traits)}")
        print(f"{'='*60}")
        response = manager.get_response(personality, test_prompt)
        print(f"Response: {response}\n")
