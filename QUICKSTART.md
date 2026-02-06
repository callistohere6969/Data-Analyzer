# Quick reference for running the project with projectvenv

## 🚀 Quick Start (Using projectvenv)

### Windows:
```batch
# One-command setup and run:
setup.bat

# OR manually:
projectvenv\Scripts\activate.bat
pip install -r requirements.txt
streamlit run app.py
```

### macOS/Linux:
```bash
# One-command setup and run:
./setup.sh

# OR manually:
source projectvenv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 📋 Available Scripts

| Script | Purpose | OS |
|--------|---------|-----|
| `setup.bat` | Install dependencies in projectvenv | Windows |
| `setup.sh` | Install dependencies in projectvenv | macOS/Linux |
| `run.bat` | Run full pipeline (test + Streamlit) | Windows |
| `run.sh` | Run full pipeline (test + Streamlit) | macOS/Linux |
| `activate.bat` | Just activate projectvenv shell | Windows |

## 🔧 Manual Setup

If you prefer to do it step-by-step:

### Windows:
```batch
# 1. Activate virtual environment
projectvenv\Scripts\activate.bat

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
copy .env.example .env
# Edit .env and add your OpenRouter API key

# 4. Verify setup
python setup.py

# 5. Run quick test
python quick_test.py

# 6. Start Streamlit app
streamlit run app.py
```

### macOS/Linux:
```bash
# 1. Activate virtual environment
source projectvenv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env and add your OpenRouter API key

# 4. Verify setup
python setup.py

# 5. Run quick test
python quick_test.py

# 6. Start Streamlit app
streamlit run app.py
```

## 📝 Environment Configuration

After running setup, edit `.env` file:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
DEFAULT_MODEL=openai/gpt-4-turbo-preview
```

Get your API key from: https://openrouter.ai

## ✅ Verification

To verify everything is working:

```bash
# Activate projectvenv first
# Then run:
python quick_test.py
```

This will:
- Load sample_data/sales_sample.csv
- Run all 5 agents
- Display results in console
- Generate visualizations

## 🌐 Access the Web App

After running `streamlit run app.py`, open your browser to:
**http://localhost:8501**

## 📊 Available Tabs

1. **Profile** - Data structure and statistics
2. **Insights** - Patterns and correlations
3. **Anomalies** - Outliers and unusual patterns
4. **Visualizations** - Auto-generated charts
5. **Report** - Executive summary
6. **Q&A** - Ask follow-up questions

## 🆘 Troubleshooting

### projectvenv not found
```bash
# Make sure you're in the correct directory
cd "c:\Users\Chaitanya khare\Desktop\Data Analyser"
```

### Dependencies not installing
```bash
# Activate projectvenv first
projectvenv\Scripts\activate.bat  # Windows
source projectvenv/bin/activate   # macOS/Linux

# Then upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### .env file not found
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### OpenRouter API error
- Check your API key in .env
- Visit https://openrouter.ai to verify account status
- Try with a different model if needed

## 📂 Project Structure

```
Data Analyser/
├── projectvenv/           ← Your virtual environment
├── app.py                 ← Main Streamlit app
├── requirements.txt       ← Dependencies
├── .env                   ← API keys (create from .env.example)
├── run.bat / run.sh       ← Full pipeline runner
├── setup.bat / setup.sh   ← Dependency installer
├── agents/                ← 5 AI agents
├── graph/                 ← LangGraph orchestration
├── utils/                 ← Utilities
├── sample_data/           ← Test CSV
└── outputs/               ← Generated charts
```

## 🎯 Next Steps

1. ✅ Run `setup.bat` or `setup.sh`
2. ✅ Edit `.env` with your OpenRouter API key
3. ✅ Run `run.bat` or `run.sh`
4. ✅ Upload a CSV file in Streamlit
5. ✅ Click "Run Analysis"
6. ✅ Explore the results!

---

Need help? Check README.md for detailed documentation.
