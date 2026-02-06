"""LangGraph workflow orchestration - State machine for agent coordination"""

from typing import Any
from langgraph.graph import StateGraph, END
from graph.state import AnalysisState
from utils.data_loader import load_data_file, validate_dataframe, get_dataframe_summary
from utils.sqlite_helper import create_sqlite_db
from pathlib import Path
from agents.data_profiler import analyze_data_profile
from agents.insight_generator import generate_insights
from agents.anomaly_detector import detect_anomalies
from agents.visualization import create_visualizations
from agents.explanation import synthesize_report


def load_and_profile_data(state: AnalysisState) -> AnalysisState:
    """Step 1: Load data file (CSV/Excel/JSON) and create data profile"""
    
    csv_path = state.get("csv_path")
    if not csv_path:
        state["error"] = "No file path provided"
        state["execution_status"] = "failed"
        return state
    
    # Load data
    df, error = load_data_file(csv_path)
    if error:
        state["error"] = error
        state["execution_status"] = "failed"
        return state
    
    # Validate data
    is_valid, validation_msg = validate_dataframe(df)
    if not is_valid:
        state["error"] = validation_msg
        state["execution_status"] = "failed"
        return state
    
    # Limit rows for very large datasets to speed up processing
    original_len = len(df)
    if len(df) > 10000:
        df = df.sample(n=10000, random_state=42)
        state["warning"] = f"Dataset sampled: Using 10,000 of {original_len:,} rows for faster processing"
    
    # Store dataframe and summary
    state["dataframe"] = df
    state["df_summary"] = get_dataframe_summary(df)
    state["execution_status"] = "running"

    # Create SQLite database for Q&A
    try:
        db_dir = Path("temp_uploads")
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / f"analysis_{Path(csv_path).stem}.db"
        success, db_error = create_sqlite_db(df, str(db_path), table_name="data")
        if success:
            state["db_path"] = str(db_path)
            state["db_table"] = "data"
        else:
            state["warning"] = (state.get("warning", "") + f" | DB creation failed: {db_error}").strip()
    except Exception as e:
        state["warning"] = (state.get("warning", "") + f" | DB creation error: {str(e)}").strip()
    
    # Run data profiler
    state = analyze_data_profile(state)
    
    return state


def conditional_visualizations(state: AnalysisState) -> str:
    """Conditional routing: Check if we should create visualizations"""
    
    enable_viz = state.get("enable_visualizations", True)
    df = state.get("dataframe")
    min_rows = state.get("min_rows_for_viz", 10)
    
    if not enable_viz or df is None or len(df) < min_rows:
        return "skip_visualizations"
    
    return "create_visualizations"


def build_workflow():
    """
    Build the LangGraph state machine workflow
    
    Workflow:
    START 
      → LoadProfile (Agent 1)
      → GenerateInsights (Agent 2) 
      → DetectAnomalies (Agent 4)
      → [Branch] CreateVisualizations (Agent 3) OR Skip
      → SynthesizeReport (Agent 5)
      → END
    
    Returns:
        Compiled LangGraph workflow
    """
    
    # Create the state graph
    workflow = StateGraph(AnalysisState)
    
    # Add nodes
    workflow.add_node("load_and_profile", load_and_profile_data)
    workflow.add_node("generate_insights", generate_insights)
    workflow.add_node("detect_anomalies", detect_anomalies)
    workflow.add_node("create_visualizations", create_visualizations)
    workflow.add_node("synthesize_report", synthesize_report)
    
    # Set entry point
    workflow.set_entry_point("load_and_profile")
    
    # Add edges (workflow routing)
    workflow.add_edge("load_and_profile", "generate_insights")
    workflow.add_edge("generate_insights", "detect_anomalies")
    
    # Conditional branch for visualizations
    workflow.add_conditional_edges(
        "detect_anomalies",
        conditional_visualizations,
        {
            "create_visualizations": "create_visualizations",
            "skip_visualizations": "synthesize_report"
        }
    )
    
    # Converge back to synthesis
    workflow.add_edge("create_visualizations", "synthesize_report")
    
    # Final edge
    workflow.add_edge("synthesize_report", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# Initialize the workflow
analysis_workflow = build_workflow()


def run_analysis(csv_path: str, 
                 enable_visualizations: bool = True,
                 min_rows_for_viz: int = 10) -> AnalysisState:
    """
    Execute the complete analysis workflow
    
    Args:
        csv_path: Path to CSV file
        enable_visualizations: Whether to create visualizations
        min_rows_for_viz: Minimum rows required for visualizations
    
    Returns:
        Final analysis state with all results
    """
    
    initial_state: AnalysisState = {
        "csv_path": csv_path,
        "dataframe": None,
        "df_summary": None,
        "profile_result": None,
        "insights_result": None,
        "anomalies_result": None,
        "visualizations": None,
        "final_summary": None,
        "error": None,
        "current_agent": None,
        "execution_status": "starting",
        "enable_visualizations": enable_visualizations,
        "enable_anomaly_detection": True,
        "min_rows_for_viz": min_rows_for_viz,
        "messages": None,
        "user_question": None
    }
    
    # Run the workflow
    final_state = analysis_workflow.invoke(initial_state)
    
    return final_state


def get_workflow_summary(state: AnalysisState) -> str:
    """Generate a summary of the entire workflow execution"""
    
    summary = "ANALYSIS WORKFLOW SUMMARY\n"
    summary += "=" * 60 + "\n\n"
    
    # Status
    summary += f"Status: {state.get('execution_status', 'unknown').upper()}\n"
    if state.get('error'):
        summary += f"Error: {state['error']}\n"
    summary += "\n"
    
    # Profile
    profile = state.get("profile_result")
    if profile:
        summary += f"✓ Data Profiler: Complete\n"
        summary += f"  - Rows: {profile['overview']['total_rows']}\n"
        summary += f"  - Columns: {profile['overview']['total_columns']}\n"
    else:
        summary += "✗ Data Profiler: Not completed\n"
    
    # Insights
    insights = state.get("insights_result", [])
    summary += f"\n✓ Insight Generator: {len(insights)} insights found\n"
    
    # Anomalies
    anomalies = state.get("anomalies_result", [])
    summary += f"✓ Anomaly Detector: {len(anomalies)} anomalies detected\n"
    
    # Visualizations
    visualizations = state.get("visualizations", [])
    summary += f"✓ Visualization Agent: {len(visualizations)} charts generated\n"
    
    # Report
    if state.get("final_summary"):
        summary += f"✓ Explanation Agent: Report generated\n"
    else:
        summary += f"✗ Explanation Agent: Not completed\n"
    
    return summary


if __name__ == "__main__":
    # Example usage
    print("LangGraph workflow module loaded successfully!")
    print("Use run_analysis(csv_path) to execute the analysis pipeline")
