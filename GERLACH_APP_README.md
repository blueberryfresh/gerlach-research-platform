# Gerlach (2018) Personality Types - Interactive App

## Overview

This application presents the four robust personality types identified in Gerlach et al. (2018) research, allowing users to interact with each personality type. Each personality is **supported, strengthened, and reinforced** by its unique nature, ensuring consistent and authentic responses.

## The Four Personality Types

### 1. ⚖️ Average
- **Big Five Profile:** Average scores across all traits
- **Nature:** Balanced, moderate, practical, represents the typical individual
- **Communication:** Measured, reasonable, avoids extremes

### 2. ⭐ Role Model
- **Big Five Profile:** Low Neuroticism, High Extraversion/Openness/Agreeableness/Conscientiousness
- **Nature:** Emotionally stable, social, creative, cooperative, organized
- **Communication:** Enthusiastic, positive, empathetic, well-organized

### 3. 🎯 Self-Centred
- **Big Five Profile:** Low Openness/Agreeableness/Conscientiousness
- **Nature:** Focus on self-interest, conventional, competitive, less organized
- **Communication:** Direct, blunt, skeptical, self-focused

### 4. 🤫 Reserved
- **Big Five Profile:** Low Neuroticism and Openness
- **Nature:** Calm, introverted, conventional, prefers routines
- **Communication:** Concise, practical, emotionally composed

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Anthropic API Key** - Get one from [Anthropic Console](https://console.anthropic.com/)
3. **Required packages:**
   ```bash
   pip install anthropic streamlit
   ```

### Setup

1. **Set your API key:**
   
   **Windows (PowerShell):**
   ```powershell
   $env:ANTHROPIC_API_KEY="your-api-key-here"
   ```
   
   **Windows (Command Prompt):**
   ```cmd
   set ANTHROPIC_API_KEY=your-api-key-here
   ```
   
   **Mac/Linux:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

2. **Run the app:**
   
   **Windows:**
   ```cmd
   start_gerlach_app.bat
   ```
   
   **Mac/Linux:**
   ```bash
   chmod +x start_gerlach_app.sh
   ./start_gerlach_app.sh
   ```
   
   **Or directly:**
   ```bash
   streamlit run gerlach_personality_app.py --server.port 8504
   ```

3. **Open your browser:**
   The app will automatically open at `http://localhost:8504`

## Features

### 🎭 Personality Presentation
- **Landing Page:** View all four personality types with detailed information
- **Big Five Profiles:** See the trait levels for each personality
- **Key Characteristics:** Understand what makes each personality unique

### 💬 Interactive Chat
- **Select Any Personality:** Choose from the sidebar to start chatting
- **Personality-Reinforced Responses:** Each personality responds according to its nature
- **Conversation History:** Maintains context throughout your conversation
- **Multiple Sessions:** Chat with different personalities simultaneously

### 📊 Features
- **Real-time Interaction:** Get immediate responses from each personality
- **Personality Details:** Expandable information cards for each type
- **Session Statistics:** Track your conversations and messages
- **Research Citation:** Direct link to the original research paper

## How It Works

### Personality Reinforcement

Each personality type has been enhanced with **strengthened system prompts** that:

1. **Define Core Identity:** Clearly establish the personality's fundamental nature
2. **Specify Behavioral Characteristics:** Detail how the personality should behave
3. **Mandate Communication Style:** Enforce consistent language and tone
4. **Reinforce in Every Response:** Ensure personality traits are evident in all interactions

### Technical Implementation

- **Base Model:** Claude Sonnet 4.5 (via Anthropic API)
- **System Prompts:** Enhanced prompts that strongly reinforce personality traits
- **Session Management:** Maintains conversation context for each personality
- **Web Interface:** Streamlit-based interactive UI

## Usage Tips

1. **Start with the Landing Page:** Review all four personality types before chatting
2. **Try Different Questions:** Ask the same question to different personalities to see how they differ
3. **Explore Characteristics:** Use the expandable details to understand each personality better
4. **Compare Responses:** Notice how each personality's nature influences their responses

## Example Questions to Try

- "How do you approach learning something new?"
- "What's your ideal weekend activity?"
- "How do you handle stress or difficult situations?"
- "What motivates you in your work?"
- "How do you make important decisions?"

## Research Background

This application is based on:

**Gerlach, M., Farb, B., Revelle, W., & Nunes Amaral, L. A. (2018).**  
A robust data-driven approach identifies four personality types across four large data sets.  
*Nature Human Behaviour*, 2(10), 735-742.

The research analyzed over 1.5 million participants across four large datasets to identify these robust personality types using advanced clustering techniques.

## Files

- `gerlach_personality_app.py` - Main application interface
- `gerlach_personality_llms.py` - Core personality implementations with enhanced prompts
- `start_gerlach_app.bat` - Windows launcher
- `start_gerlach_app.sh` - Mac/Linux launcher

## Troubleshooting

### API Key Issues
- Make sure `ANTHROPIC_API_KEY` is set in your environment
- Restart your terminal/command prompt after setting the key
- Verify the key is correct and has sufficient credits

### Import Errors
- Ensure all dependencies are installed: `pip install anthropic streamlit`
- Check that you're using Python 3.8 or higher

### Port Already in Use
- The app uses port 8504 by default
- If it's occupied, change the port in the launcher script or command

## Support

For issues or questions:
1. Check that your API key is set correctly
2. Verify all dependencies are installed
3. Review the error messages in the terminal
4. Ensure you have internet connectivity for API calls

---

**Ready to explore personality types?** Launch the app and start chatting! 🚀

