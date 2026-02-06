# Multi-Agent Data Analysis Assistant - Project Structure
# =======================================================

"""
PROJECT FOLDER STRUCTURE:
------------------------
multi-agent-analyzer/
│
├── app.py                      # Streamlit UI (main entry point)
├── requirements.txt            # Dependencies
├── .env                        # API keys (DON'T COMMIT THIS)
├── README.md                   # Project documentation
│
├── agents/
│   ├── __init__.py
│   ├── data_profiler.py       # Agent 1: Data profiling
│   ├── insight_generator.py   # Agent 2: Generate insights
│   ├── anomaly_detector.py    # Agent 3: Detect anomalies
│   ├── visualization.py       # Agent 4: Create charts
│   └── explanation.py         # Agent 5: Synthesize report
│
├── graph/
│   ├── __init__.py
│   ├── state.py               # LangGraph state schema
│   └── workflow.py            # LangGraph orchestration
│
├── utils/
│   ├── __init__.py
│   ├── llm.py                 # OpenRouter LLM setup
│   └── data_loader.py         # CSV handling utilities
│
├── outputs/                    # Generated charts (gitignored)
└── sample_data/               # Test CSVs
    └── sales_sample.csv
"""

# =======================================================
# STEP 1: Install Dependencies
# =======================================================

"""
Create requirements.txt with:
------------------------------
streamlit==1.29.0
langchain==0.1.0
langgraph==0.0.20
langchain-openai==0.0.2
pandas==2.1.4
numpy==1.26.2
matplotlib==3.8.2
seaborn==0.13.0
plotly==5.18.0
python-dotenv==1.0.0
scipy==1.11.4

Installation command:
pip install -r requirements.txt
"""

# =======================================================
# STEP 2: Environment Setup (.env file)
# =======================================================

"""
Create .env file in project root:
---------------------------------
OPENROUTER_API_KEY=your_openrouter_api_key_here
DEFAULT_MODEL=openai/gpt-4-turbo-preview
"""

# =======================================================
# STEP 3: LangGraph State Schema (graph/state.py)
# =======================================================

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage

class AnalysisState(TypedDict):
    """Shared state across all agents"""
    
    # Input data
    csv_path: str
    dataframe: Optional[Any]  # pandas DataFrame
    
    # Agent outputs
    profile_result: Optional[Dict[str, Any]]
    insights_result: Optional[List[str]]
    anomalies_result: Optional[List[str]]
    visualizations: Optional[List[str]]  # List of file paths
    final_summary: Optional[str]
    
    # Conversation history
    messages: List[BaseMessage]
    
    # Metadata
    error: Optional[str]
    current_agent: Optional[str]

# =======================================================
# STEP 4: OpenRouter LLM Setup (utils/llm.py)
# =======================================================

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(model_name: str = None, temperature: float = 0.0):
    """
    Initialize OpenRouter LLM via LangChain
    
    OpenRouter uses OpenAI-compatible API, so we use ChatOpenAI
    with custom base_url
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in .env file")
    
    model = model_name or os.getenv("DEFAULT_MODEL", "openai/gpt-4-turbo-preview")
    
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/your-username/multi-agent-analyzer",
            "X-Title": "Multi-Agent Data Analyzer"
        }
    )
    
    return llm

# Test function
def test_llm():
    llm = get_llm()
    response = llm.invoke("Say 'LLM is working!' in 5 words")
    print(response.content)

# =======================================================
# STEP 5: Data Loader Utility (utils/data_loader.py)
# =======================================================

import pandas as pd
from typing import Tuple, Optional

def load_csv(file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load CSV file with error handling
    
    Returns:
        (DataFrame, error_message) - error_message is None if successful
    """
    try:
        df = pd.read_csv(file_path)
        
        # Basic validation
        if df.empty:
            return None, "CSV file is empty"
        
        if len(df.columns) == 0:
            return None, "CSV has no columns"
        
        return df, None
        
    except FileNotFoundError:
        return None, f"File not found: {file_path}"
    except pd.errors.EmptyDataError:
        return None, "CSV file is empty"
    except Exception as e:
        return None, f"Error loading CSV: {str(e)}"

def get_dataframe_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Quick summary of DataFrame for context
    """
    return {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "sample_rows": df.head(3).to_dict(orient='records')
    }

# =======================================================
# SETUP INSTRUCTIONS
# =======================================================

"""
QUICK START GUIDE:
==================

1. Create project folder:
   mkdir multi-agent-analyzer
   cd multi-agent-analyzer

2. Create the folder structure shown at the top

3. Create requirements.txt and install:
   pip install -r requirements.txt

4. Create .env file with your OpenRouter API key:
   OPENROUTER_API_KEY=sk-or-v1-xxxxx
   DEFAULT_MODEL=openai/gpt-4-turbo-preview

5. Test OpenRouter connection:
   python -c "from utils.llm import test_llm; test_llm()"

6. Next steps:
   - Build Data Profiler Agent (agents/data_profiler.py)
   - Build LangGraph workflow (graph/workflow.py)
   - Create Streamlit UI (app.py)

WHAT I'VE PROVIDED:
===================
✅ Complete project structure
✅ State schema for LangGraph
✅ OpenRouter LLM integration
✅ CSV loading utilities
✅ Error handling patterns

WHAT YOU'LL BUILD NEXT:
========================
→ Week 1: Data Profiler Agent + Basic Streamlit UI
→ Week 2: All 5 agents
→ Week 3: LangGraph orchestration + Polish
"""