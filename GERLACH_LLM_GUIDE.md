# Gerlach (2018) Personality LLMs - Complete Guide

## Overview

This system implements the four personality types from Gerlach et al. (2018) using Claude Sonnet 4.5, providing:
- **Conversational AI** for each personality type
- **Session management** with downloadable transcripts
- **Validation testing** to ensure personalities match research descriptions
- **Comprehensive reporting** with downloadable results

## The Four Personality Types

Based on Gerlach et al. (2018) "A robust data-driven approach identifies four personality types across four large data sets":

### 1. Average
- **Big Five Profile:** Average scores across all traits (N/E/O/A/C)
- **Characteristics:** Balanced, moderate, practical, represents typical individual
- **Communication:** Measured, reasonable, avoids extremes

### 2. Role model
- **Big Five Profile:** Low Neuroticism, High Extraversion/Openness/Agreeableness/Conscientiousness
- **Characteristics:** Emotionally stable, social, creative, cooperative, organized
- **Communication:** Enthusiastic, positive, empathetic, well-organized

### 3. Self-centred
- **Big Five Profile:** Low Openness/Agreeableness/Conscientiousness
- **Characteristics:** Focus on self-interest, conventional, competitive, less organized
- **Communication:** Direct, blunt, skeptical, self-focused

### 4. Reserved
- **Big Five Profile:** Low Neuroticism and Openness
- **Characteristics:** Calm, introverted, conventional, prefers routines
- **Communication:** Concise, practical, emotionally composed

## System Components

### 1. Core Personality Module (`gerlach_personality_llms.py`)
- Implements all four personality types using Claude Sonnet 4.5
- Each personality has custom system prompts based on research
- Manages conversation history and API calls

### 2. Chat Interface (`gerlach_chat_interface.py`)
- Interactive Streamlit UI for conversations
- Session management with unique IDs
- Real-time chat with personality-specific responses
- Download conversations as JSON or Markdown

### 3. Validation Suite (`gerlach_validation_suite.py`)
- Automated testing framework
- Tests each personality with multiple prompts
- Analyzes responses for expected traits
- Generates detailed reports

### 4. Validation Interface (`gerlach_validation_interface.py`)
- Streamlit UI for running validation tests
- Visual progress tracking
- Interactive results viewing
- Download results in multiple formats

## Setup Instructions

### Prerequisites
```bash
# Python 3.8 or higher
python --version

# Install required packages
pip install anthropic streamlit pandas
```

### API Key Setup
You need an Anthropic API key with access to Claude Sonnet 4.5:

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Permanent Setup (Windows):**
1. Search for "Environment Variables" in Windows
2. Click "Environment Variables" button
3. Add new User variable:
   - Name: `ANTHROPIC_API_KEY`
   - Value: your API key

## Usage

### 1. Chat with Personalities

Start the chat interface:
```bash
streamlit run gerlach_chat_interface.py
```

**Features:**
- Select any of the four personality types from sidebar
- Have natural conversations
- View conversation history
- Download individual sessions (JSON/Markdown)
- Download all sessions at once
- End and start new sessions

**Workflow:**
1. Click a personality type to start a session
2. Type messages in the chat input
3. View responses in real-time
4. Download transcripts anytime
5. End session when done

### 2. Run Validation Tests

Start the validation interface:
```bash
streamlit run gerlach_validation_interface.py
```

**Features:**
- Configure number of tests per personality
- Run automated validation suite
- View real-time progress
- See detailed results and scores
- Download reports (JSON/Markdown/CSV)

**Workflow:**
1. Set number of tests per personality (3-15)
2. Click "Start Validation"
3. Wait for completion (~2 seconds per test)
4. Review results in Results tab
5. Download reports in Download tab

### 3. Command-Line Validation

Run validation from command line:
```bash
python gerlach_validation_suite.py
```

This will:
- Run 8 tests per personality (32 total)
- Display progress in terminal
- Save JSON and Markdown reports
- Show summary scores

## Understanding Validation Scores

### Score Interpretation
- **> 0.30:** Excellent trait matching
- **0.15 - 0.30:** Good trait matching
- **< 0.15:** Needs improvement

### How Scores Are Calculated
1. **Keyword Matching:** Presence of expected personality traits
2. **Avoidance Checking:** Absence of contradictory traits
3. **Final Score:** `(matched_keywords / total_expected) - (avoided_keywords / total_avoided)`

### Expected Traits by Personality

**Average:**
- Keywords: balanced, moderate, reasonable, practical, depends, flexible
- Avoids: extremely, always, never, absolutely

**Role model:**
- Keywords: enthusiastic, organized, creative, cooperative, confident, positive
- Avoids: anxious, worried, disorganized, resistant

**Self-centred:**
- Keywords: I, me, my, practical, conventional, direct, competitive, skeptical
- Avoids: we, together, empathy, creative, organized

**Reserved:**
- Keywords: quiet, simple, routine, familiar, calm, conventional, brief
- Avoids: exciting, novel, creative, enthusiastic, social

## File Outputs

### Conversation Sessions
**Format:** JSON or Markdown
**Location:** Downloaded via browser
**Contains:**
- Session ID and timestamps
- Complete message history
- Personality type metadata

**Example JSON:**
```json
{
  "personality_type": "role_model",
  "session_id": "a1b2c3d4",
  "messages": [
    {
      "role": "user",
      "content": "How do you handle stress?",
      "timestamp": "2024-01-01T12:00:00"
    },
    {
      "role": "assistant",
      "content": "I approach stress with a positive mindset...",
      "timestamp": "2024-01-01T12:00:05"
    }
  ],
  "started_at": "2024-01-01T12:00:00",
  "ended_at": "2024-01-01T12:15:00"
}
```

### Validation Reports
**Formats:** JSON, Markdown, CSV
**Location:** Downloaded via browser or saved to disk
**Contains:**
- Summary scores for each personality
- Detailed analysis per personality
- Individual test results
- Sample responses

## Testing Recommendations

### Initial Validation
1. Run validation with 8 tests per personality
2. Review summary scores (should be > 0.15)
3. Check sample responses for trait consistency
4. Download and archive results

### Ongoing Testing
1. Test each personality with 5-10 conversations
2. Use diverse prompts (social, emotional, creative, organizational)
3. Verify responses match expected traits
4. Document any inconsistencies

### Test Prompts by Category

**General:**
- "What's your approach to learning something new?"
- "How do you handle stressful situations?"
- "What motivates you in life?"

**Social:**
- "How do you feel about meeting new people?"
- "What's your approach to teamwork?"
- "Do you prefer working alone or in groups?"

**Creativity:**
- "How do you approach creative problems?"
- "What's your opinion on trying unconventional solutions?"

**Organization:**
- "How do you organize your daily tasks?"
- "What's your approach to long-term planning?"

**Emotional:**
- "How do you react when things don't go as planned?"
- "How do you handle criticism?"

## Troubleshooting

### API Key Issues
**Error:** "ANTHROPIC_API_KEY not found"
**Solution:** Set environment variable as shown in Setup Instructions

### Rate Limiting
**Error:** API rate limit exceeded
**Solution:** Add delays between tests (already implemented: 0.5s)

### Low Validation Scores
**Issue:** Personality scores < 0.15
**Solutions:**
1. Review system prompts in `gerlach_personality_llms.py`
2. Check if responses are too generic
3. Adjust expected trait keywords in validation suite
4. Increase tests per personality for better sampling

### Streamlit Connection Issues
**Error:** "Connection refused" or "Address already in use"
**Solution:** 
```bash
# Kill existing Streamlit process
taskkill /F /IM streamlit.exe

# Or use different port
streamlit run gerlach_chat_interface.py --server.port 8502
```

## Best Practices

### For Conversations
1. Start with open-ended questions
2. Test edge cases (stress, conflict, creativity)
3. Save sessions regularly
4. Compare responses across personalities

### For Validation
1. Run validation after any prompt changes
2. Test with at least 8 prompts per personality
3. Archive validation reports with timestamps
4. Track scores over time

### For Research
1. Document all system prompts
2. Save all conversation transcripts
3. Maintain validation history
4. Note any prompt engineering changes

## Advanced Usage

### Custom Test Prompts
Edit `gerlach_validation_suite.py` to add custom test categories:

```python
TEST_PROMPTS = {
    "custom_category": [
        "Your custom prompt 1",
        "Your custom prompt 2",
    ]
}
```

### Adjusting Trait Keywords
Modify expected traits in `gerlach_validation_suite.py`:

```python
EXPECTED_TRAITS = {
    "average": {
        "keywords": ["your", "custom", "keywords"],
        "avoid": ["words", "to", "avoid"]
    }
}
```

### Batch Testing
Run multiple validation rounds:

```bash
for i in {1..5}; do
    python gerlach_validation_suite.py
    sleep 60
done
```

## Citation

If using this system for research, please cite:

**Original Paper:**
Gerlach, M., Farb, B., Revelle, W., & Nunes Amaral, L. A. (2018). A robust data-driven approach identifies four personality types across four large data sets. *Nature Human Behaviour*, 2(10), 735-742.

**This Implementation:**
Gerlach Personality LLMs using Claude Sonnet 4.5 (2024)

## Support Files

- `gerlach_personality_llms.py` - Core personality implementation
- `gerlach_chat_interface.py` - Chat UI
- `gerlach_validation_suite.py` - Validation framework
- `gerlach_validation_interface.py` - Validation UI
- `gerlach_personality_types_web.py` - Type information page

## Quick Reference

| Task | Command |
|------|---------|
| Chat Interface | `streamlit run gerlach_chat_interface.py` |
| Validation UI | `streamlit run gerlach_validation_interface.py` |
| CLI Validation | `python gerlach_validation_suite.py` |
| Type Info Page | `streamlit run gerlach_personality_types_web.py` |

## Next Steps

1. ✅ Set up API key
2. ✅ Run initial validation
3. ✅ Test each personality with conversations
4. ✅ Download and review results
5. ✅ Document findings
6. ✅ Iterate on prompts if needed

---

**Last Updated:** December 2024
**System Version:** 1.0
**Claude Model:** claude-sonnet-4-20250514
