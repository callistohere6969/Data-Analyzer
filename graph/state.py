"""LangGraph state schema for multi-agent data analysis"""

from typing import TypedDict, List, Dict, Any, Optional
import pandas as pd


class AnalysisState(TypedDict, total=False):
    """
    Shared state across all agents in the LangGraph workflow
    
    This state persists data and outputs throughout the analysis pipeline
    """
    
    # Input data
    csv_path: str
    dataframe: Optional[pd.DataFrame]
    df_summary: Optional[Dict[str, Any]]
    db_path: Optional[str]
    db_table: Optional[str]
    
    # Agent outputs
    profile_result: Optional[Dict[str, Any]]      # Data Profiler output
    insights_result: Optional[List[Dict[str, Any]]]  # Insight Generator output
    anomalies_result: Optional[List[Dict[str, Any]]]  # Anomaly Detector output
    visualizations: Optional[List[Dict[str, str]]]    # Visualization Agent output (list of {chart_type, path, description})
    final_summary: Optional[str]                  # Explanation Agent output
    
    # Execution metadata
    error: Optional[str]
    current_agent: Optional[str]
    execution_status: str  # "running", "completed", "failed"
    
    # Analysis configuration
    enable_visualizations: bool
    enable_anomaly_detection: bool
    min_rows_for_viz: int
    
    # Conversation history for multi-turn interactions
    messages: Optional[List[Dict[str, str]]]
    user_question: Optional[str]
