# 🎯 GETTING STARTED - Multi-Agent Data Analyzer

## ✨ You're All Set!

Your complete Multi-Agent Data Analysis Assistant is ready to run. All code has been generated and configured for your existing `projectvenv` environment.

## 🚀 Fastest Start (One Command)

### Windows:
```batch
setup.bat
```
Then edit `.env` and add your OpenRouter API key, then:
```batch
run.bat
```

### macOS/Linux:
```bash
./setup.sh
```
Then edit `.env` and add your OpenRouter API key, then:
```bash
./run.sh
```

---

## 📋 What You Get

✅ **5 Specialized AI Agents:**
- Data Profiler (structure, statistics, quality)
- Insight Generator (patterns, correlations, trends)
- Anomaly Detector (outliers, unusual patterns)
- Visualization Agent (auto-generated charts)
- Explanation Agent (executive summary, Q&A)

✅ **LangGraph Orchestration:**
- State machine workflow
- Conditional routing
- Error handling

✅ **Streamlit Web Interface:**
- File upload
- 6-tab results dashboard
- Real-time analysis
- Q&A capability

---

## 🔑 API Key Setup

You'll need an OpenRouter API key:

1. **Get your key:**
   - Go to https://openrouter.ai
   - Sign up (free)
   - Get your API key

2. **Add to .env:**
   ```bash
   # Windows
   notepad .env
   
   # macOS/Linux
   nano .env
   ```
   
   Add this line:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

---

## 📂 Project Files Created

```
Data Analyser/
├── ✅ app.py                    # Main Streamlit app
├── ✅ quick_test.py             # Test runner
├── ✅ setup.py                  # Setup checker
├── ✅ requirements.txt          # Dependencies
├── ✅ .env.example              # Config template
├── ✅ .gitignore                # Git config
│
├── ✅ run.bat / run.sh          # 🚀 RUN THESE FIRST
├── ✅ setup.bat / setup.sh      # 🔧 SETUP SCRIPTS
├── ✅ activate.bat / activate.sh # Environment scripts
│
├── ✅ README.md                 # Full documentation
├── ✅ QUICKSTART.md             # Quick reference
├── ✅ ARCHITECTURE.md           # System design
├── ✅ IMPLEMENTATION.md         # Implementation guide
│
├── 📁 agents/                   # 5 AI agents
│   ├── data_profiler.py
│   ├── insight_generator.py
│   ├── anomaly_detector.py
│   ├── visualization.py
│   └── explanation.py
│
├── 📁 graph/                    # Orchestration
│   ├── state.py                 # State schema
│   └── workflow.py              # State machine
│
├── 📁 utils/                    # Utilities
│   ├── llm.py                   # OpenRouter
│   └── data_loader.py           # CSV handling
│
├── 📁 sample_data/
│   └── sales_sample.csv         # Test dataset
│
├── 📁 outputs/                  # Generated charts
└── 📁 projectvenv/              # ← Your environment
```

---

## 🎬 Step-by-Step Execution

### Step 1: Setup (5 seconds)
```batch
# Windows
setup.bat

# macOS/Linux
./setup.sh
```

This will:
- Activate projectvenv
- Install dependencies
- Create .env file
- Verify setup

### Step 2: Configure (1 minute)
```bash
# Edit .env with your API key
# Windows: notepad .env
# macOS/Linux: nano .env

OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Step 3: Test (10 seconds)
```batch
# Windows
projectvenv\Scripts\activate.bat
python quick_test.py

# macOS/Linux
source projectvenv/bin/activate
python quick_test.py
```

This analyzes sample data and displays all results.

### Step 4: Run (ongoing)
```batch
# Windows
run.bat

# macOS/Linux
./run.sh

# Or manually:
streamlit run app.py
```

Browser opens to: **http://localhost:8501**

---

## 💻 Interface Walkthrough

### Home Screen
- **Upload CSV** or click "Use Sample Data"
- Shows data preview (first 10 rows)
- Displays row/column/memory metrics

### Configuration Panel (Left Sidebar)
- Enable/disable visualizations
- Set minimum rows threshold
- About information

### Results Dashboard (6 Tabs)

**Tab 1: 📋 Profile**
- Dataset structure
- Column statistics
- Missing value analysis
- Data quality issues

**Tab 2: 💡 Insights**
- Correlations (strong pairs)
- Distribution skewness
- Category imbalances
- Missing data patterns
- Duplicates found

**Tab 3: 🚨 Anomalies**
- Z-score outliers
- IQR outliers
- Sparse categories
- Temporal anomalies
- Severity indicators

**Tab 4: 📈 Visualizations**
- Distribution plots
- Correlation heatmap
- Category bar charts
- Scatter plots
- (Expandable gallery)

**Tab 5: 📝 Report**
- AI-generated executive summary
- Key findings
- Recommendations

**Tab 6: ❓ Q&A**
- Ask follow-up questions
- Get answers based on analysis
- Multi-turn conversation

---

## 📊 Sample Data Included

File: `sample_data/sales_sample.csv`
- 50 rows of sales data
- 7 columns (Date, Product, Region, Sales, Quantity, Customer_Age, Satisfaction)
- Perfect for testing all features

To use:
1. Click "Use Sample Data" button in Streamlit UI
2. Click "Run Analysis"
3. Browse all 6 tabs of results

---

## 🔍 What Each Agent Does

### Agent 1: Data Profiler 📊
**Analyzes:** Dataset structure
**Output:** Profile with statistics, missing values, outliers

### Agent 2: Insight Generator 💡
**Analyzes:** Patterns and relationships
**Output:** Correlations, trends, imbalances

### Agent 3: Anomaly Detector 🚨
**Analyzes:** Unusual patterns
**Output:** Outliers, sparse categories, temporal anomalies

### Agent 4: Visualization 📈
**Creates:** Auto-selected charts
**Output:** PNG files (histograms, heatmaps, scatter, bar charts)

### Agent 5: Explanation 📝
**Synthesizes:** All agent outputs
**Output:** Executive summary + Q&A capability

---

## ⚙️ Configuration Options

### Models Available
Edit `.env` to change the LLM:

```env
# Most capable (higher cost)
DEFAULT_MODEL=openai/gpt-4-turbo-preview

# Cheaper alternative
DEFAULT_MODEL=openai/gpt-3.5-turbo

# Other options via OpenRouter
# DEFAULT_MODEL=anthropic/claude-3-opus
# DEFAULT_MODEL=anthropic/claude-3-sonnet
# DEFAULT_MODEL=mistral/mistral-large
```

### Streamlit Configuration
Edit `~/.streamlit/config.toml`:
```ini
[server]
port = 8501
headless = false

[client]
showErrorDetails = true
```

---

## 🆘 Troubleshooting

### Problem: "projectvenv not found"
**Solution:**
```bash
cd "c:\Users\Chaitanya khare\Desktop\Data Analyser"
```

### Problem: "OPENROUTER_API_KEY not found"
**Solution:**
1. Create `.env` file (copy from `.env.example`)
2. Add your API key from https://openrouter.ai
3. Save the file

### Problem: "ModuleNotFoundError"
**Solution:**
```bash
# Activate projectvenv
projectvenv\Scripts\activate.bat  # Windows
source projectvenv/bin/activate   # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Problem: Visualizations not generating
**Solution:**
- Check `outputs/` folder permissions
- Verify dataset has minimum rows (default: 10)
- Check matplotlib is installed: `pip install matplotlib seaborn`

### Problem: Slow analysis
**Solution:**
- Use cheaper model (gpt-3.5-turbo)
- Disable visualizations
- Reduce dataset size

### Problem: LLM API errors
**Solution:**
- Check API key in `.env`
- Verify OpenRouter account status
- Try a different model
- Check your credit balance at https://openrouter.ai

---

## 📱 Browser Access

After running the app, open your browser:

**Local:** http://localhost:8501

**Settings:**
- Reruns: Automatic on file changes
- Theme: Light/Dark in menu (⋮)
- Layout: Wide/Narrow in menu

---

## 📈 Performance Tips

**For Faster Analysis:**
- Use sample data first
- Disable visualizations
- Use cheaper model (gpt-3.5-turbo)
- Reduce dataset size (sample rows)

**For Better Results:**
- Use gpt-4-turbo-preview
- Enable all visualizations
- Use larger, more diverse datasets

**Memory Management:**
- Max recommended dataset: 100k rows
- Visualizations limited to prevent memory issues
- Auto-caching helps with repeated analyses

---

## 🎓 Learning Resources

- **LangChain:** https://python.langchain.com
- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **Streamlit:** https://docs.streamlit.io
- **OpenRouter:** https://openrouter.ai/docs
- **Pandas:** https://pandas.pydata.org/docs
- **Matplotlib:** https://matplotlib.org/stable/contents.html

---

## ✅ Verification Checklist

After setup, verify:
- [ ] projectvenv activated
- [ ] Dependencies installed (no errors)
- [ ] `.env` file created with API key
- [ ] `python quick_test.py` runs successfully
- [ ] Streamlit UI loads at localhost:8501
- [ ] Sample data analysis completes
- [ ] All 6 tabs display results
- [ ] Visualizations appear in outputs/

---

## 🚀 Next Steps

1. **Immediate:** Run `setup.bat` (Windows) or `./setup.sh` (macOS/Linux)
2. **Add API Key:** Edit `.env` with OpenRouter key
3. **Test:** Run `quick_test.py` to verify
4. **Launch:** Run `run.bat` (Windows) or `./run.sh` (macOS/Linux)
5. **Analyze:** Upload your CSV or use sample data

---

## 📞 Need Help?

1. Check **README.md** for full documentation
2. See **QUICKSTART.md** for quick reference
3. Review **ARCHITECTURE.md** for system design
4. Check **IMPLEMENTATION.md** for technical details

---

## 🎉 You're Ready!

Everything is configured and ready to go. Just:

1. Run `setup.bat` or `./setup.sh`
2. Add your OpenRouter API key to `.env`
3. Run `run.bat` or `./run.sh`
4. Start analyzing your data! 📊

**Happy analyzing! 🚀**
