# Big5 Personality LLMs - Setup Instructions

## 📦 Package Contents

This package contains five composite Big5 personality LLMs for research purposes:
- 🤝 **The Collaborator** - Team-oriented, reliable, organized
- 💡 **The Innovator** - Creative, confident, adventurous
- 🔬 **The Analyst** - Thoughtful, detail-oriented, intellectual
- ☮️ **The Mediator** - Calm, empathetic, diplomatic
- ⚡ **The Driver** - Assertive, goal-focused, results-driven

---

## 🖥️ System Requirements

- **Operating System:** Windows, macOS, or Linux
- **Python:** Version 3.8 or higher
- **RAM:** At least 4GB (8GB recommended)
- **Disk Space:** ~2GB for models and dependencies
- **Internet:** Required for initial model download

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Python
If you don't have Python installed:
- Download from: https://www.python.org/downloads/
- During installation, **check "Add Python to PATH"**
- Verify installation: Open terminal/command prompt and type `python --version`

### Step 2: Install Dependencies
Open terminal/command prompt in the Big5 folder and run:

**Windows:**
```bash
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

This will install all necessary packages (may take 5-10 minutes).

### Step 3: Start the Web Interface
**Windows:** Double-click `start_web.bat`

**Mac/Linux:** Run in terminal:
```bash
python -m streamlit run unified_composite_web.py --server.port 8503
```

The interface will open in your browser at: http://localhost:8503

---

## 📁 Important Files

### Core Files (DO NOT DELETE):
- `composite_big5_llms.py` - Main personality implementations
- `unified_composite_web.py` - Web interface
- `requirements.txt` - Python dependencies
- `start_web.bat` - Windows launcher (optional)
- `start_web_simple.bat` - Simple Windows launcher (optional)

### Documentation:
- `SETUP_INSTRUCTIONS.md` - This file
- `QUICK_START_GUIDE.md` - Usage guide
- `VALIDATION_SUMMARY.md` - Validation results
- `COMPOSITE_PERSONALITIES_DOCUMENTATION.md` - Technical details

### Testing Scripts (Optional):
- `test_composite_personalities.py` - Comprehensive testing
- `quick_composite_demo.py` - Quick demo
- `interactive_composite_test.py` - Command-line interface

---

## 🧪 Testing the Installation

After installation, test that everything works:

### Option 1: Quick Demo (No Web Interface)
```bash
python quick_composite_demo.py
```
This shows sample responses from all 5 personalities.

### Option 2: Web Interface
Start the web interface (see Step 3 above) and try asking a question to any personality.

### Option 3: Comprehensive Testing
```bash
python test_composite_personalities.py
```
This runs 200 test questions across all personalities (takes ~15-20 minutes).

---

## 💡 Usage Tips

### Individual Testing:
1. Open the web interface
2. Scroll to any personality card
3. Type your question in their prompt field
4. Click "Ask [Personality]"
5. View the response in the conversation history

### Comparison Testing:
1. Scroll to the bottom of the page
2. Find "Compare All Five Personalities" section
3. Enter a question in the large text field
4. Click "🎭 Get All 5 Responses"
5. Compare how each personality responds differently

### Good Test Questions:
- "How do you handle team conflicts?"
- "What's your approach to innovation?"
- "How do you make important decisions?"
- "What motivates you in your work?"
- "How do you respond to criticism?"

---

## 🔧 Troubleshooting

### Problem: "Python is not recognized"
**Solution:** Python is not in your PATH. Reinstall Python and check "Add Python to PATH"

### Problem: "pip is not recognized"
**Solution:** Try `python -m pip install -r requirements.txt` instead

### Problem: Models downloading slowly
**Solution:** First run takes time to download GPT-2 models (~500MB). Subsequent runs are faster.

### Problem: Web interface won't start
**Solution:** 
1. Check if port 8503 is already in use
2. Try a different port: `python -m streamlit run unified_composite_web.py --server.port 8504`
3. Use the command-line interface instead: `python interactive_composite_test.py`

### Problem: Responses are slow
**Solution:** 
- This is normal - GPT-2 generation takes 5-10 seconds per response
- Comparison mode generates 5 responses, so it takes ~30-60 seconds
- Consider using a machine with better CPU/GPU

### Problem: Import errors
**Solution:** Make sure all dependencies are installed:
```bash
pip install --upgrade transformers torch streamlit
```

---

## 📊 For Research Use

### Collecting Data:
The web interface stores conversation history in the session. To save responses:
1. Copy responses from the interface
2. Use the testing scripts which save to JSON files
3. Modify the code to add custom logging

### Customizing Personalities:
Edit `composite_big5_llms.py` to adjust:
- Personality trait scores (lines 93-264)
- System prompts (personality descriptions)
- Generation parameters (temperature, top_p, etc.)

### Running Batch Tests:
Use `test_composite_personalities.py` for systematic testing:
- Modify the test questions in the script
- Results are saved to JSON files
- Includes trait alignment analysis

---

## 🆘 Getting Help

### Check Documentation:
- `QUICK_START_GUIDE.md` - Quick reference
- `COMPOSITE_PERSONALITIES_DOCUMENTATION.md` - Full technical details
- `VALIDATION_SUMMARY.md` - How personalities were validated

### Common Issues:
1. **Models not loading:** Check internet connection for first-time download
2. **Slow performance:** Normal for CPU-based generation
3. **Memory errors:** Close other applications, need at least 4GB RAM

### Contact:
If you encounter issues, contact the project lead with:
- Error messages (copy full text)
- Your Python version (`python --version`)
- Your operating system
- What you were trying to do

---

## 📝 Notes for Researchers

### Model Information:
- **Base Model:** GPT-2 (124M parameters)
- **Architecture:** Transformer-based language model
- **Personality Implementation:** System prompts + generation parameters
- **No Fine-tuning:** Uses prompt engineering only

### Limitations:
- Responses are generated, not retrieved from a database
- Quality depends on question phrasing
- May occasionally produce inconsistent responses
- Not suitable for production/clinical use

### Citation:
If you use this in research, please cite appropriately and note:
- Models are based on OpenAI's GPT-2
- Personality implementation is custom
- Validation methodology is described in VALIDATION_SUMMARY.md

---

## ✅ Checklist for First-Time Setup

- [ ] Python 3.8+ installed
- [ ] Downloaded and extracted the Big5 package
- [ ] Opened terminal/command prompt in Big5 folder
- [ ] Ran `pip install -r requirements.txt`
- [ ] Tested with `python quick_composite_demo.py`
- [ ] Started web interface successfully
- [ ] Tested asking questions to at least one personality
- [ ] Tried the comparison feature
- [ ] Read the QUICK_START_GUIDE.md

---

## 🎯 Ready to Start!

Once you've completed the setup:
1. **Start the web interface:** Double-click `start_web.bat` (Windows) or run the command
2. **Open your browser:** Go to http://localhost:8503
3. **Start testing:** Ask questions to different personalities
4. **Compare responses:** Use the comparison section at the bottom

**Enjoy exploring the Big5 Personality LLMs!** 🎭

---

*Last Updated: November 2025*
*Version: 1.0*
