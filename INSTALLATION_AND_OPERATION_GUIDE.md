# 🎭 Big5 Personality LLMs
## Installation & Operation Guide

**Welcome!** This guide will help you install and use the Big5 Personality LLMs in just a few simple steps.

---

## 📋 Table of Contents
1. [What You'll Need](#what-youll-need)
2. [Installation (5 Minutes)](#installation-5-minutes)
3. [Quick Test](#quick-test)
4. [Starting the Web Interface](#starting-the-web-interface)
5. [How to Use](#how-to-use)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)

---

## 🖥️ What You'll Need

Before starting, make sure you have:

- ✅ **Computer:** Windows, Mac, or Linux
- ✅ **Python 3.8 or newer** ([Download here](https://www.python.org/downloads/))
- ✅ **Internet connection** (for downloading models)
- ✅ **4GB RAM minimum** (8GB recommended)
- ✅ **2GB free disk space**
- ✅ **15 minutes** for first-time setup

> **Don't have Python?** Download it from [python.org](https://www.python.org/downloads/). During installation, **check the box that says "Add Python to PATH"** - this is important!

---

## 🚀 Installation (5 Minutes)

### Step 1: Extract the Package
1. Download the ZIP file you received
2. Right-click the ZIP file → **Extract All**
3. Choose a location (e.g., Desktop or Documents)
4. Open the extracted folder

### Step 2: Open Terminal/Command Prompt
**Windows:**
- Open the extracted folder
- Click in the address bar at the top
- Type `cmd` and press Enter
- A black window will open

**Mac:**
- Open the extracted folder
- Right-click in the folder → **Services** → **New Terminal at Folder**

**Linux:**
- Open the extracted folder
- Right-click → **Open in Terminal**

### Step 3: Install Dependencies
In the terminal window, type this command and press Enter:

```bash
pip install -r requirements.txt
```

**What happens:**
- Python will download and install necessary packages
- You'll see progress messages
- Takes 2-5 minutes depending on your internet speed
- When done, you'll see "Successfully installed..."

> **Tip:** If you see "pip is not recognized", try: `python -m pip install -r requirements.txt`

---

## ✅ Quick Test

Before using the full interface, let's make sure everything works!

In the same terminal window, type:

```bash
python quick_composite_demo.py
```

**What you should see:**
- "Loading models..." (first time takes 5-10 minutes to download GPT-2)
- Sample responses from all 5 personalities
- If you see responses, everything is working! ✅

> **First Run Note:** The first time you run this, it downloads AI models (~500MB). This only happens once. Subsequent runs are much faster!

---

## 🌐 Starting the Web Interface

Now you're ready to use the interactive web interface!

### Windows Users (Easy Way):
Simply **double-click** the file: `start_web.bat`

### All Users (Command Line):
In the terminal, type:

```bash
python -m streamlit run unified_composite_web.py --server.port 8503
```

**What happens:**
- Server starts (takes 10-20 seconds)
- You'll see: "You can now view your Streamlit app in your browser"
- Your web browser should open automatically
- If not, manually go to: **http://localhost:8503**

---

## 🎯 How to Use

### The Web Interface

When you open the interface, you'll see:

```
┌─────────────────────────────────────────────┐
│     🎭 Big5 Personality LLMs                │
│                                              │
│  [🤝 The Collaborator]  [💡 The Innovator] │
│  [🔬 The Analyst]       [☮️ The Mediator]   │
│  [⚡ The Driver]                            │
│                                              │
│  🔍 Compare All Five Personalities          │
└─────────────────────────────────────────────┘
```

---

### Testing Individual Personalities

Each personality has its own card with:
- **Name and description**
- **Text box** for your question
- **"Ask" button** to get a response
- **Conversation history** showing past Q&A

**To test a personality:**

1. **Scroll to any personality** (e.g., The Collaborator)
2. **Type your question** in the text box
   - Example: "How do you handle team conflicts?"
3. **Click the "Ask" button**
4. **Wait 5-10 seconds** for the response
5. **View the response** in the conversation history below

**Try asking:**
- "How do you make important decisions?"
- "What's your approach to innovation?"
- "How do you handle stress?"
- "What motivates you at work?"
- "How do you prioritize tasks?"

---

### Comparing All Personalities

This is the most powerful feature - see how all 5 personalities respond to the same question!

1. **Scroll to the bottom** of the page
2. **Find the purple section:** "🔍 Compare All Five Personalities"
3. **Type your question** in the large text box
   - Example: "How do you handle disagreements in a team?"
4. **Click "🎭 Get All 5 Responses"**
5. **Wait 30-60 seconds** (generating 5 responses)
6. **Compare the responses** - notice how each personality approaches the question differently!

**Great comparison questions:**
- "How do you approach problem-solving?"
- "What's your leadership style?"
- "How do you handle criticism?"
- "What's your approach to teamwork?"
- "How do you deal with tight deadlines?"

---

### Understanding the Personalities

#### 🤝 **The Collaborator**
- **Traits:** Team-oriented, reliable, organized
- **Best for:** Questions about teamwork, coordination, planning
- **Typical response:** Emphasizes cooperation and structure

#### 💡 **The Innovator**
- **Traits:** Creative, confident, adventurous
- **Best for:** Questions about innovation, change, new ideas
- **Typical response:** Enthusiastic, optimistic, forward-thinking

#### 🔬 **The Analyst**
- **Traits:** Thoughtful, detail-oriented, intellectual
- **Best for:** Questions about analysis, strategy, complex problems
- **Typical response:** Thorough, methodical, considers multiple angles

#### ☮️ **The Mediator**
- **Traits:** Calm, empathetic, diplomatic
- **Best for:** Questions about conflicts, understanding, consensus
- **Typical response:** Balanced, understanding, seeks harmony

#### ⚡ **The Driver**
- **Traits:** Assertive, goal-focused, results-driven
- **Best for:** Questions about leadership, decisions, execution
- **Typical response:** Direct, action-oriented, efficiency-focused

---

## 🔧 Troubleshooting

### Problem: "Python is not recognized"
**Solution:**
- Python is not installed or not in your PATH
- Reinstall Python from [python.org](https://www.python.org/downloads/)
- **Important:** Check "Add Python to PATH" during installation
- Restart your computer after installation

### Problem: "pip is not recognized"
**Solution:**
- Try: `python -m pip install -r requirements.txt` instead
- Or: `py -m pip install -r requirements.txt` (Windows)

### Problem: Installation fails with errors
**Solution:**
- Make sure you have internet connection
- Try updating pip first: `python -m pip install --upgrade pip`
- Then try installing again: `pip install -r requirements.txt`

### Problem: Models downloading very slowly
**Solution:**
- This is normal for first run (~500MB download)
- Takes 5-10 minutes depending on internet speed
- Only happens once - models are cached for future use
- Be patient and let it complete

### Problem: Web interface won't open
**Solution:**
1. Check if port 8503 is already in use
2. Try a different port: `python -m streamlit run unified_composite_web.py --server.port 8504`
3. Then go to: http://localhost:8504
4. Or use the command-line interface instead: `python interactive_composite_test.py`

### Problem: Responses are very slow
**Solution:**
- This is normal - GPT-2 takes 5-10 seconds per response on CPU
- Comparison mode takes longer (5 responses = 30-60 seconds)
- Consider using a computer with better CPU
- Or test one personality at a time

### Problem: Responses seem random or don't make sense
**Solution:**
- Try rephrasing your question more clearly
- Use complete sentences
- Be specific about what you're asking
- Example: Instead of "conflict?", ask "How do you handle conflicts in a team?"

### Problem: Web page shows errors
**Solution:**
1. Close the terminal/command prompt
2. Restart the web interface
3. Refresh your browser
4. Clear browser cache if needed

---

## ❓ FAQ

### Q: How long does installation take?
**A:** 5-10 minutes total. Most time is downloading models on first run.

### Q: Do I need to install anything besides Python?
**A:** No, just Python 3.8+. Everything else installs with `pip install -r requirements.txt`

### Q: Can I use this offline after installation?
**A:** Yes! After the first run downloads the models, you can use it offline.

### Q: How much disk space does this use?
**A:** About 2GB total (mostly for the AI models).

### Q: Can I run this on a laptop?
**A:** Yes, any laptop with 4GB+ RAM and Python 3.8+ works fine.

### Q: Why do responses take 5-10 seconds?
**A:** The AI model (GPT-2) generates text word-by-word. This is normal for CPU-based generation.

### Q: Are the responses always the same?
**A:** No, responses have some randomness. Asking the same question twice may give slightly different answers.

### Q: Can I save the conversations?
**A:** The web interface keeps history during your session. To save permanently, copy/paste responses to a document.

### Q: How do I stop the web interface?
**A:** Press `Ctrl+C` in the terminal window, or just close the terminal window.

### Q: Can I change the personalities?
**A:** Yes, but it requires editing the Python code (`composite_big5_llms.py`). See the technical documentation.

### Q: Is this suitable for production/clinical use?
**A:** No, this is for research and educational purposes only.

---

## 📞 Getting Help

If you're stuck:

1. **Check this guide** - Most issues are covered in Troubleshooting
2. **Read the error message** - It often tells you what's wrong
3. **Try the simple demo** - `python quick_composite_demo.py` to test if basic functionality works
4. **Contact the project lead** with:
   - What you were trying to do
   - The exact error message (copy/paste)
   - Your Python version: `python --version`
   - Your operating system (Windows/Mac/Linux)

---

## ✅ Quick Reference Card

### Installation:
```bash
pip install -r requirements.txt
```

### Test:
```bash
python quick_composite_demo.py
```

### Start Web Interface:
```bash
python -m streamlit run unified_composite_web.py --server.port 8503
```

### Access:
```
http://localhost:8503
```

### Stop:
```
Press Ctrl+C in terminal
```

---

## 🎉 You're Ready!

**Congratulations!** You now have the Big5 Personality LLMs up and running.

**Next steps:**
1. ✅ Start the web interface
2. ✅ Test each personality with a question
3. ✅ Try the comparison feature
4. ✅ Explore different types of questions
5. ✅ Use for your research!

**Remember:**
- First response takes longer (model loading)
- Each response takes 5-10 seconds
- Comparison mode takes 30-60 seconds
- Be patient and enjoy exploring! 🚀

---

**Happy Testing!** 🎭

*If you have questions or issues, don't hesitate to reach out to the project lead.*

---

*Last Updated: November 2025 | Version 1.0*
