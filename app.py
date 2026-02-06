"""Streamlit UI for Multi-Agent Data Analysis Assistant"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path
from graph.workflow import run_analysis, get_workflow_summary
from agents.data_profiler import get_profile_summary
from agents.insight_generator import get_insights_summary
from agents.anomaly_detector import get_anomalies_summary
from agents.visualization import get_visualizations_summary
from agents.explanation import answer_followup_question
from utils.pdf_export import generate_pdf_report
import plotly.graph_objects as go


# Configure Streamlit page
st.set_page_config(
    page_title="Multi-Agent Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .status-box {
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .status-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .status-error {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .status-info {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "analysis_state" not in st.session_state:
    st.session_state.analysis_state = None
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False


def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown("""
    <div class="main-header">📊 Multi-Agent Data Analysis Assistant</div>
    """, unsafe_allow_html=True)
    
    st.write("Analyze your data with AI-powered agents")
    st.write("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        enable_viz = st.checkbox("Enable Visualizations", value=True)
        min_rows_for_viz = st.slider("Min rows for visualization", min_value=5, max_value=100, value=10)
        
        st.write("---")
        st.write("**About this tool:**")
        st.write("""
        - 🔍 **Data Profiler**: Analyzes dataset structure
        - 💡 **Insight Generator**: Finds patterns & trends
        - 🚨 **Anomaly Detector**: Identifies outliers
        - 📈 **Visualization Agent**: Creates charts
        - 📝 **Explanation Agent**: Synthesizes findings
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 Upload Data")
        uploaded_file = st.file_uploader(
            "Choose a data file", 
            type=["csv", "xlsx", "xls", "json"],
            help="Supported formats: CSV, Excel (.xlsx, .xls), JSON"
        )
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
    
    with col2:
        st.subheader("📊 Sample Data")
        if st.button("Use Sample Data"):
            sample_path = "sample_data/sales_sample.csv"
            if os.path.exists(sample_path):
                st.session_state.uploaded_file = sample_path
                st.success("✅ Sample data loaded!")
            else:
                st.warning("⚠️ Sample data not found")
    
    # Process uploaded file
    uploaded_file = st.session_state.get("uploaded_file")
    if uploaded_file is not None:
        # Handle both uploaded files and file paths
        if isinstance(uploaded_file, str):
            csv_path = uploaded_file
            df_preview = pd.read_csv(csv_path)
        else:
            # Save uploaded file temporarily
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            csv_path = temp_dir / uploaded_file.name
            csv_path.write_bytes(uploaded_file.getbuffer())
            df_preview = pd.read_csv(csv_path)
        
        # Show preview
        st.subheader("📋 Data Preview")
        st.dataframe(df_preview.head(10), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", len(df_preview))
        with col2:
            st.metric("Columns", len(df_preview.columns))
        with col3:
            st.metric("Memory", f"{df_preview.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Run analysis button
        st.write("---")
        
        if st.button("🚀 Run Analysis", key="run_analysis"):
            st.session_state.analysis_complete = False
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Loading data...")
            progress_bar.progress(10)
            
            with st.spinner("🔄 Running analysis workflow..."):
                try:
                    status_text.text("Profiling data...")
                    progress_bar.progress(30)
                    
                    # Run the workflow
                    state = run_analysis(
                        str(csv_path),
                        enable_visualizations=enable_viz,
                        min_rows_for_viz=min_rows_for_viz
                    )
                    
                    progress_bar.progress(90)
                    status_text.text("Finalizing...")
                    
                    st.session_state.analysis_state = state
                    st.session_state.analysis_complete = True
                    
                    progress_bar.progress(100)
                    status_text.text("Complete!")
                    
                    # Show warnings if any
                    if state.get("warning"):
                        st.warning(state["warning"])
                    
                    if state.get("error"):
                        st.error(f"❌ Analysis failed: {state['error']}")
                    else:
                        st.success("✅ Analysis completed!")
                
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                finally:
                    progress_bar.empty()
                    status_text.empty()
        
        # Display results if analysis is complete
        if st.session_state.analysis_complete and st.session_state.analysis_state:
            st.write("---")
            st.subheader("📊 Analysis Results")
            
            state = st.session_state.analysis_state
            profile = state.get("profile_result", {})
            
            # Dataset Summary Card (Top of UI)
            if profile and "summary" in profile:
                summary = profile["summary"]
                overview = profile.get("overview", {})
                
                st.markdown("### 📋 Dataset Summary")
                
                # Main stats in columns
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Rows", f"{overview.get('total_rows', 0):,}")
                with col2:
                    st.metric("Total Columns", overview.get('total_columns', 0))
                with col3:
                    numeric_count = len(summary.get("numeric_columns", []))
                    st.metric("Numeric", numeric_count, delta="columns")
                with col4:
                    categorical_count = len(summary.get("categorical_columns", []))
                    st.metric("Categorical", categorical_count, delta="columns")
                
                # Special columns detection
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    date_cols = summary.get("date_columns", [])
                    if date_cols:
                        st.info(f"📅 **Date Columns:** {', '.join(date_cols[:3])}")
                    else:
                        st.info("📅 **Date Columns:** None detected")
                
                with col_b:
                    id_cols = summary.get("id_columns", [])
                    if id_cols:
                        st.warning(f"🔑 **ID Columns:** {', '.join(id_cols[:3])}")
                    else:
                        st.success("🔑 **ID Columns:** None detected")
                
                with col_c:
                    const_cols = summary.get("constant_columns", [])
                    if const_cols:
                        st.error(f"⚠️ **Constant Columns:** {', '.join(const_cols[:3])}")
                    else:
                        st.success("✅ **Constant Columns:** None")
                
                # Target suggestions
                target_suggestions = summary.get("target_suggestions", [])
                if target_suggestions:
                    st.markdown("#### 🎯 Suggested Target Columns")
                    for suggestion in target_suggestions[:3]:
                        confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🟠"}.get(suggestion.get("confidence", "low"), "⚪")
                        st.success(f"{confidence_emoji} **{suggestion['column']}** - {suggestion['reason']}")
                
                # Column Recommendations
                if "recommendations" in profile:
                    recommendations = profile["recommendations"]
                    
                    st.markdown("#### 💡 Column Recommendations")
                    
                    rec_col1, rec_col2, rec_col3 = st.columns(3)
                    
                    with rec_col1:
                        st.markdown("**📊 Best for Visualization**")
                        viz_recs = recommendations.get("best_for_visualization", [])
                        if viz_recs:
                            for rec in viz_recs[:5]:
                                reasons_text = ", ".join(rec["reasons"])
                                st.info(f"**{rec['column']}**\n\n✓ {reasons_text}")
                        else:
                            st.warning("No strong candidates")
                    
                    with rec_col2:
                        st.markdown("**🔀 Best for Grouping**")
                        group_recs = recommendations.get("best_for_grouping", [])
                        if group_recs:
                            for rec in group_recs[:5]:
                                reasons_text = ", ".join(rec["reasons"])
                                type_emoji = {"date": "📅", "categorical": "🏷️"}.get(rec.get("type", ""), "")
                                st.info(f"{type_emoji} **{rec['column']}**\n\n✓ {reasons_text}")
                        else:
                            st.warning("No strong candidates")
                    
                    with rec_col3:
                        st.markdown("**🧹 Columns to Clean**")
                        clean_recs = recommendations.get("columns_to_clean", [])
                        if clean_recs:
                            for rec in clean_recs[:5]:
                                severity = rec["severity"]
                                severity_emoji = "🔴" if severity >= 3 else "🟡"
                                issues_text = "\n• ".join(rec["issues"])
                                st.warning(f"{severity_emoji} **{rec['column']}**\n\n• {issues_text}")
                        else:
                            st.success("✅ All columns look good!")
                
                st.write("---")
            
            # Create tabs for different analyses
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                "📋 Profile",
                "💡 Insights",
                "🚨 Anomalies",
                "📈 Visualizations",
                "📝 Report",
                "❓ Q&A"
            ])
            
            # Tab 1: Data Profile
            with tab1:
                profile = state.get("profile_result", {})
                
                # Display Data Quality Score prominently
                if profile and "data_quality_score" in profile:
                    score_data = profile["data_quality_score"]
                    score = score_data["score"]
                    
                    # Color based on score
                    if score >= 90:
                        color = "green"
                        emoji = "🟢"
                        label = "Excellent"
                    elif score >= 75:
                        color = "blue"
                        emoji = "🔵"
                        label = "Good"
                    elif score >= 60:
                        color = "orange"
                        emoji = "🟠"
                        label = "Fair"
                    else:
                        color = "red"
                        emoji = "🔴"
                        label = "Needs Improvement"
                    
                    # Big score display
                    st.markdown(f"### {emoji} Data Quality Score: **{score}/100** ({label})")
                    
                    # Quality metrics in columns
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Missing Values", f"{score_data['missing_percentage']:.2f}%", 
                                 delta=f"-{score_data['total_missing']} cells", delta_color="inverse")
                    with col2:
                        st.metric("Duplicate Rows", f"{score_data['duplicate_percentage']:.2f}%",
                                 delta=f"-{score_data['total_duplicates']} rows", delta_color="inverse")
                    with col3:
                        st.metric("Outliers", f"{score_data['outlier_percentage']:.2f}%",
                                 delta=f"-{score_data['total_outliers']} values", delta_color="inverse")
                    
                    # Progress bar
                    st.progress(score / 100)
                    st.write("---")
                
                # Profile summary
                st.write(get_profile_summary(state))
            
            # Tab 2: Insights
            with tab2:
                insights = state.get("insights_result", [])
                if insights:
                    # Add beginner-friendly guide
                    with st.expander("ℹ️ How to Read These Insights (Click to expand)", expanded=False):
                        st.markdown("""
                        **What are insights?** Insights are interesting patterns and findings discovered in your data.
                        
                        **How to use them:**
                        - 🔍 **Explanation**: What the pattern means in simple terms
                        - 💡 **Why it matters**: Why this is important for your analysis
                        - 🎯 **Recommended action**: What you can do about it
                        - 📊 **Confidence**: How sure we are about this finding (higher is better)
                        
                        **Don't worry if you see unfamiliar terms** - each insight includes a plain language explanation!
                        """)
                    
                    st.write("---")
                    st.write(get_insights_summary(state))
                    
                    st.write("**Detailed Insights with Explanations:**")
                    for i, insight in enumerate(insights, 1):
                        # Add emoji based on type
                        emoji_map = {
                            "correlation": "🔗",
                            "distribution": "📊",
                            "imbalance": "⚖️",
                            "missing_data": "❓",
                            "duplicates": "🔄",
                            "categorical_relationship": "🔀",
                            "group_comparison": "📊"
                        }
                        emoji = emoji_map.get(insight.get('type', ''), '💡')
                        
                        # Check if statistically significant
                        is_significant = insight.get('statistically_significant', False)
                        sig_badge = " ✅ Statistically Significant" if is_significant else ""
                        
                        with st.expander(f"{emoji} {i}. {insight.get('title', 'Insight')}{sig_badge}", expanded=(i <= 3)):
                            # Technical description
                            st.write("**📝 Description:**")
                            st.write(insight.get('description', 'N/A'))
                            
                            # Statistical test results
                            if insight.get('p_value') is not None:
                                st.write("**📊 Statistical Significance:**")
                                p_val = insight.get('p_value')
                                sig_level = "✅ Significant (p < 0.05)" if p_val < 0.05 else "⚠️ Not significant (p ≥ 0.05)"
                                st.metric("p-value", f"{p_val:.4f}", delta=sig_level)
                            
                            # Chi-square test results
                            if insight.get('chi2_statistic') is not None:
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("χ² statistic", f"{insight.get('chi2_statistic'):.2f}")
                                with col_b:
                                    st.metric("Cramér's V (effect size)", f"{insight.get('cramers_v', 0):.3f}")
                            
                            # T-test results
                            if insight.get('t_statistic') is not None:
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.metric("t-statistic", f"{insight.get('t_statistic'):.2f}")
                                with col_b:
                                    st.metric("Difference", f"{insight.get('difference_percent', 0):.1f}%")
                            
                            # Plain language explanation
                            if insight.get('explanation'):
                                st.write("**🔍 What this means:**")
                                st.info(insight.get('explanation'))
                            
                            # Why it matters
                            if insight.get('why_it_matters'):
                                st.write("**💡 Why it matters:**")
                                st.write(insight.get('why_it_matters'))
                            
                            # Action recommendation
                            if insight.get('action'):
                                st.write("**🎯 Recommended action:**")
                                st.success(insight.get('action'))
                            
                            # Confidence meter
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.metric("Confidence", f"{insight.get('confidence', 0)*100:.0f}%")
                            with col2:
                                confidence = insight.get('confidence', 0)
                                st.progress(confidence)
                else:
                    st.info("No insights generated")
            
            # Tab 3: Anomalies
            with tab3:
                anomalies = state.get("anomalies_result", [])
                if anomalies:
                    # Add beginner-friendly guide
                    with st.expander("ℹ️ Understanding Anomalies (Click to expand)", expanded=False):
                        st.markdown("""
                        **What are anomalies?** Anomalies are unusual or unexpected values in your data that stand out from normal patterns.
                        
                        **Types of anomalies:**
                        - 🔴 **High severity**: Significant issues that need immediate attention
                        - 🟡 **Medium severity**: Notable patterns worth investigating
                        - 🟢 **Low severity**: Minor irregularities to be aware of
                        
                        **How to use this information:**
                        - 🔍 **Explanation**: What makes these values unusual in simple terms
                        - 💡 **Why it matters**: Why these anomalies are important
                        - 🎯 **Recommended action**: What you should do about them
                        
                        **Remember:** Not all anomalies are bad - some represent interesting discoveries or special cases!
                        """)
                    
                    st.write("---")
                    st.write(get_anomalies_summary(state))
                    
                    st.write("**Detailed Anomalies with Explanations:**")
                    for i, anomaly in enumerate(anomalies, 1):
                        severity = anomaly.get("severity", "low")
                        severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                        
                        # Type emoji mapping
                        type_emoji = {
                            "z_score_outlier": "📊",
                            "iqr_outlier": "📈",
                            "sparse_categories": "🏷️",
                            "temporal_anomaly": "📅"
                        }
                        type_icon = type_emoji.get(anomaly.get('type', ''), '⚠️')
                        
                        with st.expander(
                            f"{severity_emoji.get(severity, '⚪')} {type_icon} {i}. {anomaly.get('title', 'Anomaly')}", 
                            expanded=(i <= 2 and severity == "high")
                        ):
                            # Technical description
                            st.write("**📝 Description:**")
                            st.write(anomaly.get('description', 'N/A'))
                            
                            # Plain language explanation
                            if anomaly.get('explanation'):
                                st.write("**🔍 What this means:**")
                                st.info(anomaly.get('explanation'))
                            
                            # Why it matters
                            if anomaly.get('why_it_matters'):
                                st.write("**💡 Why it matters:**")
                                st.write(anomaly.get('why_it_matters'))
                            
                            # Action recommendation
                            if anomaly.get('action'):
                                st.write("**🎯 Recommended action:**")
                                st.warning(anomaly.get('action'))
                            
                            # Metrics
                            cols = st.columns(3)
                            with cols[0]:
                                if anomaly.get('count'):
                                    st.metric("Affected Records", f"{anomaly['count']:,}")
                            with cols[1]:
                                if anomaly.get('percentage'):
                                    st.metric("Percentage", f"{anomaly['percentage']:.2f}%")
                            with cols[2]:
                                severity_score = {"high": 90, "medium": 60, "low": 30}.get(severity, 50)
                                st.metric("Severity", severity.upper())
                else:
                    st.success("✓ No anomalies detected!")
            
            # Tab 4: Visualizations
            with tab4:
                visualizations = state.get("visualizations", [])
                if visualizations:
                    st.write(get_visualizations_summary(state))
                    st.write("---")
                    
                    for viz in visualizations:
                        # Try to display interactive HTML first
                        html_path = viz.get('file_path')
                        if html_path and os.path.exists(html_path) and html_path.endswith('.html'):
                            st.subheader(viz.get('description', 'Visualization'))
                            with open(html_path, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            st.components.v1.html(html_content, height=600, scrolling=True)
                        else:
                            # Fallback to static image
                            filepath = viz.get('filepath')
                            if filepath and os.path.exists(filepath):
                                st.image(filepath, caption=viz.get('description', 'Visualization'))
                            else:
                                st.warning(f"Visualization file not found")
                else:
                    st.info("No visualizations generated")
            
            # Tab 5: Executive Report
            with tab5:
                summary = state.get("final_summary")
                if summary:
                    st.write(summary)
                    
                    st.write("---")
                    
                    # PDF Export Button
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button("📄 Export to PDF"):
                            with st.spinner("Generating PDF report..."):
                                try:
                                    pdf_path = "outputs/analysis_report.pdf"
                                    success, error = generate_pdf_report(state, pdf_path, title="Data Analysis Report")
                                    
                                    if success:
                                        with open(pdf_path, "rb") as pdf_file:
                                            st.download_button(
                                                label="⬇️ Download PDF",
                                                data=pdf_file,
                                                file_name=f"analysis_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                                mime="application/pdf"
                                            )
                                        st.success("✅ PDF generated successfully!")
                                    else:
                                        st.error(f"❌ PDF generation failed: {error}")
                                except Exception as e:
                                    st.error(f"❌ Error generating PDF: {str(e)}")
                else:
                    st.info("No report available")
            
            # Tab 6: Q&A
            with tab6:
                st.write("Ask follow-up questions about your analysis")
                
                # Use form to enable Enter key submission
                with st.form(key="qa_form", clear_on_submit=False):
                    user_question = st.text_input("Enter your question:", key="question_input")
                    submit_button = st.form_submit_button("Ask")
                
                if submit_button:
                    if user_question:
                        with st.spinner("🤔 Thinking..."):
                            try:
                                answer = answer_followup_question(state, user_question)
                                st.write("**Answer:**")
                                st.write(answer)
                            except Exception as e:
                                st.error(f"Error answering question: {str(e)}")
                    else:
                        st.warning("Please enter a question")
    
    # Footer
    st.write("---")


if __name__ == "__main__":
    main()
