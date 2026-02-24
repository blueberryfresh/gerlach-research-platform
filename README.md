# Big Five Personality LLMs

A collection of five specialized Large Language Models, each embodying one of the Big Five personality traits.

## 🧠 Overview

This project implements five distinct LLMs that demonstrate different personality characteristics based on the Big Five personality model:

- **🎨 Openness**: Creative, curious, open to new experiences
- **📋 Conscientiousness**: Organized, disciplined, goal-oriented  
- **🎉 Extraversion**: Social, energetic, assertive
- **🤝 Agreeableness**: Cooperative, trusting, empathetic
- **😰 Neuroticism**: Emotionally reactive, anxious, sensitive

## 🚀 Features

- **Individual Personality Models**: Each model has distinct response patterns and generation parameters
- **Personality Consistency**: Models maintain consistent personality traits across conversations
- **Comparative Analysis**: Compare responses from all five personalities simultaneously
- **Evaluation Framework**: Comprehensive evaluation of personality consistency, accuracy, and distinctiveness
- **Interactive Interfaces**: Both web-based (Streamlit) and command-line interfaces
- **Configurable Parameters**: Adjustable personality trait intensities

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- PyTorch (will be installed automatically)
- At least 4GB RAM (8GB+ recommended for better performance)

### Install from source

```bash
# Clone or download the project
cd Big5

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Quick Install (Alternative)
```bash
pip install torch transformers streamlit scikit-learn pandas numpy
```

## 🎮 Usage

### Web Interface (Recommended)

Launch the interactive Streamlit web interface:

```bash
streamlit run demo_interface.py
```

This provides:
- Chat with individual personalities
- Compare all personalities side-by-side
- Run comprehensive evaluations
- Download evaluation reports

### Command Line Interface

For terminal-based interaction:

```bash
python demo_interface.py --cli
```

### Python API

```python
from big5_personality_llms import Big5LLMManager

# Initialize the manager
manager = Big5LLMManager()

# Get response from a specific personality
response = manager.get_response("openness", "Tell me about creativity")
print(response)

# Compare all personalities
responses = manager.get_all_responses("How do you handle stress?")
for personality, response in responses.items():
    print(f"{personality}: {response}")

# Use individual models
from big5_personality_llms import OpennessLLM
openness_model = OpennessLLM()
creative_response = openness_model.generate_response("What inspires you?")
```

### Evaluation

Run comprehensive personality evaluation:

```python
from personality_evaluation import PersonalityEvaluator

evaluator = PersonalityEvaluator(manager)
results = evaluator.run_comprehensive_evaluation()
report = evaluator.generate_evaluation_report(results)
print(report)
```

Or use the command line:
```bash
python personality_evaluation.py
```

## 🏗️ Project Structure

```
Big5/
├── big5_personality_llms.py    # Core personality models
├── personality_evaluation.py   # Evaluation framework
├── demo_interface.py          # Interactive interfaces
├── requirements.txt           # Dependencies
├── setup.py                  # Package setup
├── README.md                 # This file
└── evaluation_report.md      # Generated evaluation results
```

## 🔧 Configuration

### Personality Intensity

You can adjust personality trait intensities:

```python
from big5_personality_llms import PersonalityConfig, OpennessLLM

# Create custom personality configuration
config = PersonalityConfig(
    openness=0.9,        # Very high openness
    conscientiousness=0.3, # Lower conscientiousness
    extraversion=0.7,    # High extraversion
    agreeableness=0.6,   # Moderate agreeableness
    neuroticism=0.2      # Low neuroticism
)

# Use with model
model = OpennessLLM(personality_config=config)
```

### Model Selection

Change the base model (default: microsoft/DialoGPT-medium):

```python
manager = Big5LLMManager(model_name="gpt2")
# or
manager = Big5LLMManager(model_name="microsoft/DialoGPT-large")
```

## 📊 Evaluation Metrics

The evaluation framework measures:

1. **Consistency**: How consistently each model exhibits its target personality traits
2. **Accuracy**: How well each model exhibits expected vs. other personality traits  
3. **Distinctiveness**: How different each personality's responses are from others

## 🎯 Example Interactions

### Openness (Creative & Curious)
**Input**: "How should I approach learning a new skill?"
**Response**: "Let's explore this creatively... What if we approached this from an unconventional angle? I'm curious about what unique methods might work best for your learning style..."

### Conscientiousness (Organized & Disciplined)  
**Input**: "How should I approach learning a new skill?"
**Response**: "Let me organize this systematically... Here's a structured approach: First, set clear learning objectives, then break the skill into manageable components..."

### Extraversion (Social & Energetic)
**Input**: "How should I approach learning a new skill?"
**Response**: "I'm excited to discuss this with you! Learning is so much more engaging when you can collaborate with others and share the experience..."

## 🚨 Limitations

- Models are based on pre-trained language models and may not perfectly represent human personality traits
- Personality expression is achieved through prompt engineering and generation parameters
- Performance depends on the quality of the base model
- Evaluation metrics are heuristic-based and may not capture all aspects of personality

## 🔬 Research Applications

This project can be used for:
- Studying AI personality modeling
- Human-computer interaction research
- Conversational AI development
- Personality psychology experiments
- Educational tools for understanding personality traits

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Better personality trait modeling
- More sophisticated evaluation metrics
- Additional base model support
- Fine-tuning capabilities
- Extended personality configurations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built using Hugging Face Transformers
- Based on the Big Five personality model from psychology research
- Inspired by research in AI personality modeling and human-computer interaction

## 📚 References

- Costa, P. T., & McCrae, R. R. (1992). Normal personality assessment in clinical practice: The NEO Personality Inventory.
- Goldberg, L. R. (1993). The structure of phenotypic personality traits.
- Research papers included in your Big5 folder for theoretical background

---

**Happy experimenting with AI personalities! 🧠✨**
