# Multi-Agent Data Analysis Assistant

🤖 **AI-Powered Multi-Agent System for Comprehensive Data Analysis**

A sophisticated data analysis platform using LangGraph orchestration and specialized AI agents to automatically profile, analyze, visualize, and explain your data.

## 🎯 Project Architecture

```
User uploads CSV
        ↓
Orchestrator Agent (LangGraph)
        ↓
    ┌───────────────────────────────┐
    ↓           ↓           ↓        ↓
Data Profiler  Insight     Anomaly   Visualization
Agent          Generator   Detector  Agent
    ↓           ↓           ↓        ↓
    └───────────────────────────────┘
            ↓
    Explanation Agent
    (synthesizes everything)
            ↓
        Results Display
```

## 🏗️ Tech Stack

- **Orchestration**: LangGraph (state machine for agent workflow)
- **Agents**: LangChain + OpenAI GPT-4/3.5-turbo
- **Data Processing**: Pandas, NumPy, SciPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **UI**: Streamlit (web interface)
- **API**: OpenRouter (for LLM access)

## 🤖 Five Specialized Agents

### 1. **Data Profiler Agent** 📊
- Analyzes dataset structure and characteristics
- Detects column types, distributions, missing values
- Provides statistical summaries (mean, median, std dev)
- Identifies data quality issues

### 2. **Insight Generator Agent** 💡
- Finds business-relevant patterns and trends
- Performs correlation analysis
- Identifies segment comparisons
- Detects distribution anomalies

### 3. **Anomaly Detector Agent** 🚨
- Flags unusual patterns using Z-score method
- Detects IQR-based outliers
- Identifies sparse or imbalanced categories
- Detects temporal anomalies (if time-series data exists)

### 4. **Visualization Agent** 📈
- Auto-selects appropriate chart types
- Generates distributions, heatmaps, scatter plots
- Creates correlation matrices
- Saves visualizations as PNG files

### 5. **Explanation Agent** 📝
- Synthesizes outputs from all agents
- Generates natural language executive summary
- Answers follow-up questions about the analysis

## 📁 Project Structure

```
multi-agent-analyzer/
│
├── app.py                      # Streamlit UI (main entry point)
├── requirements.txt            # Dependencies
├── .env                        # API keys (DON'T COMMIT THIS)
├── .env.example               # Example .env file
├── README.md                  # This file
│
├── agents/
│   ├── __init__.py
│   ├── data_profiler.py       # Agent 1
│   ├── insight_generator.py   # Agent 2
│   ├── anomaly_detector.py    # Agent 3
│   ├── visualization.py       # Agent 4
│   └── explanation.py         # Agent 5
│
├── graph/
│   ├── __init__.py
│   ├── state.py               # LangGraph state schema
│   └── workflow.py            # Orchestration logic
│
├── utils/
│   ├── __init__.py
│   ├── llm.py                 # OpenRouter LLM setup
│   └── data_loader.py         # CSV utilities
│
├── outputs/                   # Generated charts (gitignored)
│
└── sample_data/
    └── sales_sample.csv       # Test data
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenRouter API key (free at https://openrouter.ai)

### Installation (with existing projectvenv)

1. **Navigate to project directory**
   ```bash
   cd "c:\Users\Chaitanya khare\Desktop\Data Analyser"
   ```

2. **Windows - Run setup:**
   ```batch
   setup.bat
   ```
   
   **macOS/Linux - Run setup:**
   ```bash
   ./setup.sh
   ```

3. **Or manually activate and install:**
   
   **Windows:**
   ```batch
   projectvenv\Scripts\activate.bat
   pip install -r requirements.txt
   ```
   
   **macOS/Linux:**
   ```bash
   source projectvenv/bin/activate
   pip install -r requirements.txt
   ```

4. **Create .env file**
   ```bash
   # Windows:
   copy .env.example .env
   
   # macOS/Linux:
   cp .env.example .env
   
   # Then edit .env and add your OpenRouter API key
   ```

5. **Run the application**
   
   **Windows:**
   ```batch
   run.bat
   ```
   
   **macOS/Linux:**
   ```bash
   ./run.sh
   ```
   
   Or manually:
   ```bash
   streamlit run app.py
   ```

The app will open at `http://localhost:8501`

For quick reference, see [QUICKSTART.md](QUICKSTART.md)

## 💻 Usage

1. **Upload your CSV** or use the sample data (sales_sample.csv)
2. **Configure analysis options**:
   - Enable/disable visualizations
   - Set minimum rows for visualizations
3. **Click "Run Analysis"** to start the workflow
4. **View results** in tabbed interface:
   - **Profile**: Data structure and quality metrics
   - **Insights**: Key patterns and correlations
   - **Anomalies**: Outliers and unusual patterns
   - **Visualizations**: Auto-generated charts
   - **Report**: Executive summary
   - **Q&A**: Ask follow-up questions

## 🔄 LangGraph Workflow

The analysis pipeline flows through these states:

```
START 
  → ProfileData (Agent 1)
  → GenerateInsights (Agent 2) 
  → DetectAnomalies (Agent 3)
  → [Branch] CreateVisualizations (Agent 4) OR Skip
  → SynthesizeReport (Agent 5)
  → END
```

**Key Features:**
- State persistence across all agents
- Conditional edges (skip visualizations if too few rows)
- Parallel execution capability
- Error handling and fallbacks

## 📊 Analysis Output

### Data Profile
```
- Total rows, columns, memory usage
- Column-by-column analysis (type, nulls, statistics)
- Outlier detection per column
- Data quality flags
```

### Insights
```
- Correlation pairs (>0.7 threshold)
- Distribution skewness
- Category imbalances
- Missing data patterns
- Duplicate records
```

### Anomalies
```
- Z-score outliers
- IQR-based outliers
- Sparse categories
- Temporal anomalies (time-series)
```

### Visualizations
```
- Distributions (histogram + box plot)
- Correlation heatmap
- Category bar charts
- Scatter plots (relationships)
```

### Executive Report
```
- High-level dataset summary
- Top findings and insights
- Key anomalies identified
- Recommendations for further analysis
```

## 🛠️ Configuration

Edit `.env` to change:

```env
# LLM Model (affects cost and performance)
DEFAULT_MODEL=openai/gpt-3.5-turbo  # Cheaper
DEFAULT_MODEL=openai/gpt-4-turbo-preview  # More capable

# Other available models via OpenRouter:
# - anthropic/claude-3-opus
# - anthropic/claude-3-sonnet
# - mistral/mistral-large
# - meta-llama/llama-3-70b
```

## 📈 Example Use Cases

- **Sales Analysis**: Understand sales patterns, anomalies, customer segments
- **Customer Data**: Profile customer base, identify outliers, segment analysis
- **Financial Data**: Detect fraud patterns, analyze correlations, identify trends
- **IoT/Sensor Data**: Detect equipment anomalies, find normal patterns
- **Website Analytics**: Analyze traffic patterns, identify unusual behavior

## 🔧 Advanced Features

### Custom Analysis
Modify agent behavior in individual agent files:
- `agents/data_profiler.py`: Adjust statistics calculations
- `agents/insight_generator.py`: Add custom insight types
- `agents/anomaly_detector.py`: Tune sensitivity thresholds
- `agents/visualization.py`: Add new chart types
- `agents/explanation.py`: Customize report generation

### State Machine Customization
Edit `graph/workflow.py` to:
- Add new agents
- Modify execution flow
- Add parallel execution paths
- Implement human-in-the-loop approval

## 📝 Example CSV Format

```csv
Date,Product,Region,Sales,Quantity,Customer_Age,Satisfaction
2024-01-01,Laptop,North,1500.00,2,35,4.5
2024-01-02,Mouse,South,50.00,5,28,4.0
...
```

## 🧪 Testing

Run the analysis with sample data:

```bash
streamlit run app.py
# Click "Use Sample Data" button
# Click "Run Analysis"
```

## 📦 Dependencies

- **langchain**: LLM framework
- **langgraph**: Workflow orchestration
- **streamlit**: Web UI
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **scipy**: Statistical analysis
- **matplotlib/seaborn**: Visualization
- **plotly**: Interactive charts
- **python-dotenv**: Environment management

## 🚨 Troubleshooting

### "OPENROUTER_API_KEY not found"
- Create `.env` file in project root
- Add your OpenRouter API key
- Make sure `.env` is in the same directory as `app.py`

### Visualizations not generating
- Check that dataset has minimum rows (default: 10)
- Verify outputs/ folder has write permissions
- Check matplotlib/seaborn installation

### Slow analysis
- Reduce dataset size
- Use cheaper model (gpt-3.5-turbo)
- Disable visualizations for quick profiles

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙋 Support

For issues and questions:
1. Check the troubleshooting section
2. Review sample data format
3. Check your OpenRouter API key is valid
4. Verify all dependencies are installed

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Streamlit Documentation](https://docs.streamlit.io)
- [OpenRouter API](https://openrouter.ai)
- [Pandas Documentation](https://pandas.pydata.org)

## 🌟 Features Roadmap

- [ ] Database support (SQLite, PostgreSQL)
- [ ] Analysis history and caching
- [ ] Custom metrics and KPIs
- [ ] Real-time data streaming
- [ ] Multi-file analysis
- [ ] PDF report generation
- [ ] API endpoint (FastAPI)
- [ ] Docker containerization
- [ ] Advanced time-series analysis
- [ ] Predictive modeling agent

---

**Made with ❤️ using LangChain, LangGraph, and Streamlit**
