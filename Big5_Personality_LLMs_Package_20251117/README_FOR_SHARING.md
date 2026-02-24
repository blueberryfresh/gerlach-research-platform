# Big5 Personality LLMs - Research Package

## 🎭 What's Inside

This package contains **five AI personalities** based on the Big Five personality model, designed for research and testing purposes.

### The Five Personalities:
1. **🤝 The Collaborator** - High Agreeableness + High Conscientiousness + Moderate Extraversion
2. **💡 The Innovator** - High Openness + High Extraversion + Low Neuroticism
3. **🔬 The Analyst** - High Conscientiousness + High Openness + Low Extraversion
4. **☮️ The Mediator** - High Agreeableness + Low Neuroticism + Moderate Openness
5. **⚡ The Driver** - Low Agreeableness + High Conscientiousness + High Extraversion

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test it works
python quick_composite_demo.py

# 3. Start web interface
python -m streamlit run unified_composite_web.py --server.port 8503
```

Then open: **http://localhost:8503**

---

## 📋 What You Need

- **Python 3.8+** (download from python.org)
- **4GB+ RAM** (8GB recommended)
- **Internet connection** (for first-time model download)
- **2GB disk space**

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `SETUP_INSTRUCTIONS.md` | **START HERE** - Complete setup guide |
| `unified_composite_web.py` | Web interface (main application) |
| `composite_big5_llms.py` | Core personality implementations |
| `requirements.txt` | Python dependencies |
| `start_web.bat` | Windows launcher |
| `QUICK_START_GUIDE.md` | Usage tips and examples |

---

## 🎯 How to Use

### Web Interface (Recommended):
1. Start the interface (see Quick Start above)
2. Ask questions to individual personalities
3. Use the comparison feature to see all 5 responses side-by-side

### Command Line:
```bash
python interactive_composite_test.py
```

### Testing:
```bash
python test_composite_personalities.py
```

---

## 💡 Example Questions to Try

- "How do you handle team conflicts?"
- "What's your approach to innovation?"
- "How do you make important decisions?"
- "What motivates you in your work?"
- "How do you prioritize tasks?"

---

## 📚 Documentation

- **SETUP_INSTRUCTIONS.md** - Detailed setup and troubleshooting
- **QUICK_START_GUIDE.md** - Usage guide with tips
- **VALIDATION_SUMMARY.md** - How personalities were validated
- **COMPOSITE_PERSONALITIES_DOCUMENTATION.md** - Technical details

---

## ⚠️ Important Notes

- First run downloads GPT-2 models (~500MB) - takes 5-10 minutes
- Response generation takes 5-10 seconds per personality
- This is for research/educational purposes only
- Based on GPT-2 with custom personality prompts

---

## 🆘 Need Help?

1. Read **SETUP_INSTRUCTIONS.md** for detailed troubleshooting
2. Check that Python 3.8+ is installed: `python --version`
3. Make sure dependencies are installed: `pip install -r requirements.txt`
4. Try the simple demo first: `python quick_composite_demo.py`

---

## 📊 For Researchers

This package includes:
- ✅ 5 validated composite personalities
- ✅ Interactive web interface
- ✅ Comprehensive testing framework (200 test questions)
- ✅ Trait alignment analysis
- ✅ Full documentation

See **VALIDATION_SUMMARY.md** for validation methodology and results.

---

**Ready to explore personality-based AI?** Start with `SETUP_INSTRUCTIONS.md`! 🚀
