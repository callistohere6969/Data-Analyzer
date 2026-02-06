"""
ARCHITECTURE GUIDE
Multi-Agent Data Analysis Assistant

This file documents the complete system architecture and design patterns.
"""

# ============================================================================
# SYSTEM ARCHITECTURE OVERVIEW
# ============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                          STREAMLIT UI LAYER                             │
│                     (app.py - User Interface)                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ • File Upload                                                    │   │
│  │ • Configuration Panel (enable viz, thresholds)                   │   │
│  │ • Real-time Progress Display                                     │   │
│  │ • Tabbed Results View (6 tabs)                                   │   │
│  │ • Follow-up Q&A Interface                                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                       LANGGRAPH WORKFLOW LAYER                          │
│                    (graph/workflow.py - Orchestration)                  │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  State Machine:                                                  │   │
│  │  START → Load&Profile → Insights → Anomalies                    │   │
│  │         ↓                                   ↓                    │   │
│  │         └──→ [Branch] ──→ Visualizations OR Skip ──→ Synthesis │   │
│  │                                               ↓                  │   │
│  │                                             Report → END         │   │
│  │                                                                  │   │
│  │  Features:                                                       │   │
│  │  • State Persistence (AnalysisState)                            │   │
│  │  • Conditional Edges (dynamic routing)                          │   │
│  │  • Error Handling                                               │   │
│  │  • Progress Tracking                                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        MULTI-AGENT LAYER                                │
│                    (agents/ - Specialized Agents)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   AGENT 1    │  │   AGENT 2    │  │   AGENT 3    │                  │
│  │    DATA      │  │   INSIGHT    │  │  ANOMALY     │                  │
│  │  PROFILER    │  │  GENERATOR   │  │  DETECTOR    │                  │
│  │              │  │              │  │              │                  │
│  │ • Structure  │  │ • Correlations  │ • Z-Scores   │                  │
│  │ • Types      │  │ • Trends        │ • IQR Method │                  │
│  │ • Missing    │  │ • Segments      │ • Categories │                  │
│  │ • Stats      │  │ • Distribution  │ • Temporal   │                  │
│  │ • Quality    │  │ • Imbalance     │ • Outliers   │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐                                     │
│  │   AGENT 4    │  │   AGENT 5    │                                     │
│  │ VISUALIZATION│  │ EXPLANATION  │                                     │
│  │              │  │              │                                     │
│  │ • Type Auto- │  │ • Synthesis  │                                     │
│  │   select     │  │ • Summary    │                                     │
│  │ • Histograms │  │ • Q&A        │                                     │
│  │ • Heatmaps   │  │ • Report     │                                     │
│  │ • Scatter    │  │ • LLM Based  │                                     │
│  │ • Save PNG   │  │              │                                     │
│  └──────────────┘  └──────────────┘                                     │
│                                                                         │
│  All agents:                                                            │
│  • Accept AnalysisState as input                                        │
│  • Return modified AnalysisState                                        │
│  • Handle errors gracefully                                            │
│  • Use shared context from state                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        SHARED STATE LAYER                               │
│                    (graph/state.py - AnalysisState)                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ Input Data:                                                      │   │
│  │ • csv_path: str                                                  │   │
│  │ • dataframe: pd.DataFrame                                        │   │
│  │                                                                  │   │
│  │ Agent Outputs:                                                   │   │
│  │ • profile_result: dict (Agent 1)                                 │   │
│  │ • insights_result: list (Agent 2)                                │   │
│  │ • anomalies_result: list (Agent 3)                               │   │
│  │ • visualizations: list (Agent 4)                                 │   │
│  │ • final_summary: str (Agent 5)                                   │   │
│  │                                                                  │   │
│  │ Metadata:                                                        │   │
│  │ • error: Optional[str]                                           │   │
│  │ • execution_status: str                                          │   │
│  │ • current_agent: str                                             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        UTILITY LAYER                                    │
│                     (utils/ - Helper Functions)                         │
│  ┌──────────────┐  ┌──────────────┐                                     │
│  │   llm.py     │  │ data_loader. │                                     │
│  │              │  │     py       │                                     │
│  │ • get_llm()  │  │              │                                     │
│  │ • OpenRouter │  │ • load_csv() │                                     │
│  │   config     │  │ • validate() │                                     │
│  │ • Test LLM   │  │ • summary()  │                                     │
│  └──────────────┘  └──────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────┘
"""

# ============================================================================
# DATA FLOW EXAMPLE
# ============================================================================

"""
INPUT: sales_sample.csv (50 rows, 7 columns)
│
├─ LOAD & PROFILE
│  ├─ Load CSV → pandas DataFrame
│  ├─ Validate data (not empty, has columns)
│  ├─ Generate profile:
│  │  ├─ Total rows: 50
│  │  ├─ Column analysis:
│  │  │  ├─ Date: datetime, 0% null
│  │  │  ├─ Product: object, 5 unique
│  │  │  ├─ Region: object, 4 unique
│  │  │  ├─ Sales: float64, mean=934.50, std=595.23
│  │  │  ├─ Quantity: int64, mean=2.8, range=[1,5]
│  │  │  ├─ Customer_Age: int64, mean=33.4, range=[22,50]
│  │  │  └─ Satisfaction: float64, mean=4.1, std=0.22
│  │  └─ Quality issues: None detected ✓
│
├─ GENERATE INSIGHTS
│  ├─ Correlation matrix:
│  │  ├─ Sales ↔ Quantity: 0.85 (strong correlation)
│  │  └─ Customer_Age ↔ Satisfaction: 0.42
│  ├─ Distribution analysis:
│  │  ├─ Quantity: Slightly left-skewed
│  │  └─ Customer_Age: Approximately normal
│  └─ Categorical analysis:
│     ├─ Product: Laptop is 40% of sales (imbalanced)
│     └─ Region: Fairly balanced distribution
│
├─ DETECT ANOMALIES
│  ├─ Z-score outliers: 2 values in Sales (>3σ)
│  ├─ IQR outliers: None detected
│  ├─ Sparse categories: None
│  └─ Temporal anomalies: None (data too short)
│
├─ CREATE VISUALIZATIONS
│  ├─ distribution_Sales.png (histogram + box plot)
│  ├─ distribution_Quantity.png
│  ├─ distribution_Customer_Age.png
│  ├─ correlation_heatmap.png
│  ├─ categories_Product.png
│  └─ scatter_Sales_vs_Quantity.png
│
└─ SYNTHESIZE REPORT
   ├─ Read all agent outputs
   ├─ Use LLM to generate summary:
   │  └─ "Sales dataset shows strong correlation between quantity
   │     and revenue. Laptops dominate sales (~40%). Minor data
   │     quality issues. All customer satisfaction levels are
   │     positive (3.7-4.6). Consider expanding non-Laptop
   │     offerings for revenue diversification."
   └─ Ready for Q&A

OUTPUT:
├─ profile_result: {overview, columns, quality_issues}
├─ insights_result: [{type, title, description, confidence}, ...]
├─ anomalies_result: [{type, column, title, description, severity}, ...]
├─ visualizations: [{chart_type, filepath, description}, ...]
└─ final_summary: "Executive summary text..."
"""

# ============================================================================
# AGENT COMMUNICATION PROTOCOL
# ============================================================================

"""
AGENT INPUT/OUTPUT PATTERN:

def agent_function(state: AnalysisState) -> AnalysisState:
    '''
    Each agent follows this pattern:
    1. Extract data from state
    2. Validate inputs
    3. Perform analysis
    4. Update state with results
    5. Return updated state
    '''
    
    # 1. Extract
    df = state.get("dataframe")
    
    # 2. Validate
    if df is None or df.empty:
        state["error"] = "No dataframe"
        return state
    
    # 3. Analyze
    state["current_agent"] = "AgentName"
    try:
        result = perform_analysis(df)
        state["result_field"] = result
        state["execution_status"] = "completed"
    except Exception as e:
        state["error"] = str(e)
    
    # 5. Return
    return state

STATE PERSISTENCE:
- All previous agent outputs remain in state
- Each agent adds its own outputs
- Errors are tracked in state["error"]
- Can access all prior results
"""

# ============================================================================
# ERROR HANDLING STRATEGY
# ============================================================================

"""
HIERARCHICAL ERROR HANDLING:

1. EXECUTION LEVEL (in agents)
   try:
       analyze(df)
   except Exception as e:
       state["error"] = str(e)
       state["result"] = None
       return state

2. WORKFLOW LEVEL (in workflow.py)
   try:
       state = agent(state)
   except Exception as e:
       state["error"] = e
       # Continue with fallback
       state["result"] = fallback_result()

3. APPLICATION LEVEL (in app.py)
   try:
       state = run_analysis(csv_path)
   except Exception as e:
       st.error(f"Analysis failed: {e}")

RECOVERY:
- Partial results are preserved
- Downstream agents can handle missing upstream results
- Fallback summaries generated if LLM fails
- Always return to user (never silent failures)
"""

# ============================================================================
# SCALABILITY PATTERNS
# ============================================================================

"""
ADDING NEW AGENTS:

1. Create agent file: agents/new_agent.py
   def analyze_something(state: AnalysisState) -> AnalysisState:
       # Implementation
       state["new_result"] = result
       return state

2. Add to workflow: graph/workflow.py
   workflow.add_node("new_agent", analyze_something)
   workflow.add_edge("previous_agent", "new_agent")

3. Update AnalysisState: graph/state.py
   new_result: Optional[Dict[str, Any]]

4. Display in UI: app.py
   with tab_new:
       st.write(state["new_result"])

PARALLEL EXECUTION:

Current implementation runs agents sequentially:
  Agent1 → Agent2 → Agent3 → Agent4 → Agent5

Could be parallelized:
  Agent1 → Agent2 ┐
                  ├→ Agent4 → Agent5
           Agent3 ┘
           
Modify workflow.py edges to achieve this.
"""

# ============================================================================
# PERFORMANCE OPTIMIZATION TIPS
# ============================================================================

"""
1. SAMPLING FOR LARGE DATASETS
   if len(df) > 100000:
       df_sample = df.sample(n=10000)

2. CACHING RESULTS
   import streamlit as st
   @st.cache_data
   def run_analysis(path):
       return analysis_workflow.invoke(state)

3. ASYNC AGENT EXECUTION
   Could use asyncio with concurrent agents

4. VISUALIZATION LIMITS
   - Only generate top N charts
   - Use plotly for interactive charts (better for web)

5. LLM OPTIMIZATION
   - Use cheaper model (gpt-3.5-turbo)
   - Cache LLM responses
   - Set lower temperature for deterministic results

6. DATA LOADING
   - Use chunks for very large files
   - Pre-validate in Streamlit before sending to agents
"""

# ============================================================================
# TESTING STRATEGY
# ============================================================================

"""
UNIT TESTS:

# Test data profiler
def test_data_profiler():
    df = pd.DataFrame({"col1": [1,2,3], "col2": ["a","b","c"]})
    state = {"dataframe": df}
    result = analyze_data_profile(state)
    assert result["profile_result"] is not None

INTEGRATION TESTS:

# Test full workflow
def test_workflow():
    state = run_analysis("sample_data/sales_sample.csv")
    assert state["profile_result"] is not None
    assert len(state["insights_result"]) > 0
    assert len(state["anomalies_result"]) >= 0

LOAD TESTS:

# Test with large datasets
test_data_sizes = [1000, 10000, 100000]

"""

# ============================================================================
# DEPLOYMENT CONSIDERATIONS
# ============================================================================

"""
STREAMLIT CLOUD:
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Add secrets in dashboard (OPENROUTER_API_KEY)
4. Deploy automatically on push

DOCKER:
1. Create Dockerfile with Python 3.10
2. Install dependencies from requirements.txt
3. Expose port 8501
4. Run: docker run -p 8501:8501 multi-agent-analyzer

CONFIGURATION:
- Use environment variables for API keys
- Parameterize thresholds
- Allow agent selection in UI
- Implement user preferences storage

MONITORING:
- Log agent execution times
- Track API costs
- Monitor error rates
- Collect user feedback
"""

if __name__ == "__main__":
    print(__doc__)
