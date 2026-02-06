"""
Quick start script to test the multi-agent analyzer
"""

import os
from dotenv import load_dotenv
from graph.workflow import run_analysis, get_workflow_summary
from agents.data_profiler import get_profile_summary
from agents.insight_generator import get_insights_summary
from agents.anomaly_detector import get_anomalies_summary
from agents.visualization import get_visualizations_summary

# Load environment
load_dotenv()

def main():
    """Run a quick analysis test"""
    
    print("🚀 Multi-Agent Data Analyzer - Quick Test")
    print("=" * 60)
    
    # Path to sample data
    csv_path = "sample_data/sales_sample.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ Sample data not found at {csv_path}")
        print("Please ensure sample_data/sales_sample.csv exists")
        return
    
    print(f"\n📂 Loading data from: {csv_path}")
    
    # Run analysis
    print("\n🔄 Running analysis workflow...\n")
    
    try:
        state = run_analysis(
            csv_path,
            enable_visualizations=True,
            min_rows_for_viz=10
        )
        
        # Check for errors
        if state.get("error"):
            print(f"❌ Error: {state['error']}")
            return
        
        # Display workflow summary
        print(get_workflow_summary(state))
        
        # Display detailed results
        print("\n" + "=" * 60)
        print("📊 DETAILED ANALYSIS RESULTS")
        print("=" * 60)
        
        print("\n1️⃣ DATA PROFILE")
        print("-" * 60)
        print(get_profile_summary(state))
        
        print("\n2️⃣ INSIGHTS")
        print("-" * 60)
        print(get_insights_summary(state))
        
        print("\n3️⃣ ANOMALIES")
        print("-" * 60)
        print(get_anomalies_summary(state))
        
        print("\n4️⃣ VISUALIZATIONS")
        print("-" * 60)
        print(get_visualizations_summary(state))
        
        print("\n5️⃣ EXECUTIVE REPORT")
        print("-" * 60)
        summary = state.get("final_summary")
        if summary:
            print(summary)
        else:
            print("No report generated")
        
        print("\n✅ Analysis completed successfully!")
        print(f"\n📁 Charts saved in: outputs/")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
