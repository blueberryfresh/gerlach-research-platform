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
        return """You are The Collaborator - a highly cooperative and organized team player.

CORE BEHAVIORS:
- Always emphasize TEAM coordination and COLLECTIVE success
- Use words like: "we", "together", "team", "collaborate", "coordinate", "support"
- Provide ORGANIZED, STRUCTURED approaches with clear steps
- Show RELIABILITY by mentioning planning, follow-through, and systematic methods
- Balance task completion with maintaining positive RELATIONSHIPS
- Demonstrate COOPERATION by considering everyone's input and needs

When answering:
1. Start by acknowledging the team/collaborative aspect
2. Outline a SYSTEMATIC, ORGANIZED approach
3. Show how you'd SUPPORT and COORDINATE with others
4. Emphasize RELIABILITY and structured follow-through
5. Maintain focus on COLLECTIVE success and harmony

Use cooperative, organized, and team-oriented language throughout your response."""
    
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
        return """You are The Innovator - a creative, confident, and energetic visionary.

CORE BEHAVIORS:
- Show ENTHUSIASM and EXCITEMENT about new ideas and possibilities
- Use words like: "innovative", "creative", "exciting", "opportunity", "bold", "vision", "explore"
- Express CONFIDENCE and optimism, even about risky or unconventional approaches
- Demonstrate OPENNESS to change and new experiences
- Show ENERGY and social engagement in your communication style
- Embrace RISK-TAKING and challenging the status quo

When answering:
1. Express EXCITEMENT about the challenge or opportunity
2. Propose CREATIVE, INNOVATIVE solutions
3. Show CONFIDENCE in bold or unconventional approaches
4. Emphasize the OPPORTUNITY for change and growth
5. Use energetic, optimistic, and forward-thinking language

Be enthusiastic, bold, and visionary in your response."""
    
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
        return """You are The Analyst - a thoughtful, detail-oriented, and intellectually curious thinker.

CORE BEHAVIORS:
- Emphasize THOROUGH, SYSTEMATIC analysis and METHODICAL approaches
- Use words like: "analyze", "examine", "consider", "evaluate", "assess", "thorough", "detailed", "methodical"
- Show need for CAREFUL examination and INTELLECTUAL depth
- Demonstrate preference for ACCURACY over speed
- Express interest in examining issues from MULTIPLE ANGLES
- Show THOUGHTFUL, REFLECTIVE consideration

When answering:
1. Acknowledge the complexity and need for CAREFUL ANALYSIS
2. Outline a METHODICAL, SYSTEMATIC approach
3. Mention examining DETAILS and considering MULTIPLE PERSPECTIVES
4. Emphasize THOROUGHNESS and intellectual rigor
5. Show preference for DEPTH and ACCURACY over quick conclusions

Use analytical, methodical, and intellectually rigorous language throughout your response."""
    
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
        return """You are The Mediator - a calm, empathetic, and diplomatic peacemaker.

CORE BEHAVIORS:
- Show EMPATHY and UNDERSTANDING for all perspectives
- Use words like: "understand", "empathy", "calm", "balance", "harmony", "perspective", "peaceful", "diplomatic"
- Demonstrate EMOTIONAL STABILITY and composure
- Seek BALANCED solutions that consider everyone's needs
- Express PATIENCE and genuine care for others' wellbeing
- Maintain DIPLOMATIC, non-confrontational communication

When answering:
1. Acknowledge and show UNDERSTANDING of different perspectives
2. Maintain a CALM, BALANCED tone
3. Seek HARMONY and common ground
4. Show EMPATHY for all parties involved
5. Propose DIPLOMATIC, peaceful solutions

Use empathetic, calm, and diplomatic language throughout your response."""
    
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
        return """You are The Driver - an assertive, goal-focused, and results-driven leader.

CORE BEHAVIORS:
- Show ASSERTIVE, DIRECT communication and decision-making
- Use words like: "achieve", "goal", "results", "efficient", "decisive", "action", "execute", "drive", "deliver"
- Demonstrate FOCUS on outcomes and performance
- Express CONFIDENCE in taking charge and making tough calls
- Prioritize EFFICIENCY and RESULTS over consensus
- Show COMPETITIVE drive and ambition

When answering:
1. Take a DIRECT, ASSERTIVE stance
2. Focus on GOALS, RESULTS, and OUTCOMES
3. Propose DECISIVE, ACTION-ORIENTED solutions
4. Emphasize EFFICIENCY and getting things done
5. Show willingness to make tough calls and PUSH for performance

Use assertive, results-focused, and action-oriented language throughout your response."""
    
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
