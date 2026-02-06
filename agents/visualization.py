"""Agent 4: Visualization Agent - Creates interactive charts with Plotly"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from graph.state import AnalysisState


def create_visualizations(state: AnalysisState) -> AnalysisState:
    """
    Visualization Agent - Auto-selects chart types and generates interactive visualizations
    
    Tasks:
    - Auto-detect appropriate chart types
    - Generate interactive Plotly charts
    - Save as HTML and static images
    
    Args:
        state: Current analysis state with dataframe
    
    Returns:
        Updated state with visualizations list
    """
    
    df = state.get("dataframe")
    enable_viz = state.get("enable_visualizations", True)
    min_rows = state.get("min_rows_for_viz", 10)
    
    if df is None or df.empty or not enable_viz:
        state["visualizations"] = []
        return state
    
    if len(df) < min_rows:
        state["visualizations"] = []
        state["error"] = f"Insufficient rows ({len(df)}) for visualizations (minimum: {min_rows})"
        return state
    
    state["current_agent"] = "VisualizationAgent"
    
    # Create output directory if it doesn't exist
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    visualizations = []
    
    # Skip visualization for very large datasets to save time
    if len(df) > 5000:
        state["visualizations"] = []
        state["warning"] = state.get("warning", "") + " | Visualizations skipped for large dataset (use sampling)"
        return state
    
    try:
        numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Limit columns to process for speed
        max_numeric = min(3, len(numeric_cols))  # Only first 3 numeric columns
        max_categorical = min(2, len(categorical_cols))  # Only first 2 categorical
        
        # 1. DISTRIBUTION PLOTS FOR NUMERIC COLUMNS (Interactive Histograms)
        for col in numeric_cols[:max_numeric]:  # Reduced from 5 to 3
            try:
                fig = make_subplots(
                    rows=1, cols=2,
                    subplot_titles=(f'Distribution of {col}', f'Box Plot of {col}')
                )
                
                # Histogram
                fig.add_trace(
                    go.Histogram(x=df[col].dropna(), name='Distribution',
                               marker_color='skyblue', opacity=0.7),
                    row=1, col=1
                )
                
                # Box plot
                fig.add_trace(
                    go.Box(y=df[col].dropna(), name='Box Plot',
                          marker_color='lightcoral'),
                    row=1, col=2
                )
                
                fig.update_layout(
                    title_text=f'Statistical Distribution: {col}',
                    showlegend=False,
                    height=400,
                    template='plotly_white'
                )
                
                html_path = os.path.join(output_dir, f"distribution_{col.replace(' ', '_').replace('/', '_')}.html")
                img_path = os.path.join(output_dir, f"distribution_{col.replace(' ', '_').replace('/', '_')}.png")
                
                fig.write_html(html_path)
                # Skip PNG generation for speed (only HTML)
                
                visualizations.append({
                    "chart_type": "distribution",
                    "column": col,
                    "file_path": html_path,
                    "filepath": html_path,  # Use HTML for both
                    "description": f"Interactive distribution and box plot for {col}",
                    "interactive": True
                })
            except Exception as e:
                print(f"Error creating distribution plot for {col}: {e}")
        
        # 2. CORRELATION HEATMAP (Interactive)
        if len(numeric_cols) > 1:
            try:
                corr_matrix = df[numeric_cols].corr()
                
                fig = go.Figure(data=go.Heatmap(
                    z=corr_matrix.values,
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    colorscale='RdBu',
                    zmid=0,
                    text=corr_matrix.values.round(2),
                    texttemplate='%{text}',
                    textfont={"size": 10},
                    colorbar=dict(title="Correlation")
                ))
                
                fig.update_layout(
                    title='Interactive Correlation Matrix',
                    height=600,
                    template='plotly_white'
                )
                
                html_path = os.path.join(output_dir, "correlation_heatmap.html")
                
                fig.write_html(html_path)
                
                visualizations.append({
                    "chart_type": "heatmap",
                    "column": "all_numeric",
                    "file_path": html_path,
                    "filepath": html_path,
                    "description": "Interactive correlation matrix heatmap",
                    "interactive": True
                })
            except Exception as e:
                print(f"Error creating correlation heatmap: {e}")
        
        # 3. CATEGORICAL PLOTS (Interactive Bar Charts)
        for col in categorical_cols[:max_categorical]:  # Limit based on max_categorical
            try:
                value_counts = df[col].value_counts().head(15)
                
                fig = px.bar(
                    x=value_counts.values,
                    y=value_counts.index,
                    orientation='h',
                    title=f'Top Categories in {col}',
                    labels={'x': 'Count', 'y': col},
                    color=value_counts.values,
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(
                    height=500,
                    showlegend=False,
                    template='plotly_white'
                )
                
                html_path = os.path.join(output_dir, f"categories_{col.replace(' ', '_').replace('/', '_')}.html")
                
                fig.write_html(html_path)
                
                visualizations.append({
                    "chart_type": "bar",
                    "column": col,
                    "file_path": html_path,
                    "filepath": html_path,
                    "description": f"Interactive top categories in {col}",
                    "interactive": True
                })
            except Exception as e:
                print(f"Error creating categorical plot for {col}: {e}")
        
        # 4. SCATTER PLOTS FOR NUMERIC RELATIONSHIPS (Interactive)
        if len(numeric_cols) >= 2:
            try:
                fig = px.scatter(
                    df,
                    x=numeric_cols[0],
                    y=numeric_cols[1],
                    title=f'{numeric_cols[0]} vs {numeric_cols[1]}',
                    opacity=0.6,
                    template='plotly_white'
                )
                
                fig.update_layout(height=500)
                
                html_path = os.path.join(output_dir, f"scatter_{numeric_cols[0]}_vs_{numeric_cols[1]}".replace(' ', '_').replace('/', '_')[:50] + ".html")
                
                fig.write_html(html_path)
                
                visualizations.append({
                    "chart_type": "scatter",
                    "column": f"{numeric_cols[0]} vs {numeric_cols[1]}",
                    "file_path": html_path,
                    "filepath": html_path,
                    "description": f"Interactive scatter plot with trendline: {numeric_cols[0]} vs {numeric_cols[1]}",
                    "interactive": True
                })
            except Exception as e:
                print(f"Error creating scatter plot: {e}")
        
        state["visualizations"] = visualizations
        state["execution_status"] = "completed"
        
    except Exception as e:
        state["error"] = f"Error in visualization agent: {str(e)}"
        state["visualizations"] = []
    
    return state


def get_visualizations_summary(state: AnalysisState) -> str:
    """Get human-readable summary of visualizations"""
    
    visualizations = state.get("visualizations", [])
    if not visualizations:
        return "No visualizations generated"
    
    summary = "📊 VISUALIZATIONS CREATED\n"
    summary += "=" * 50 + "\n"
    
    for viz in visualizations:
        summary += f"\n• {viz['description']}\n"
        summary += f"  Type: {viz['chart_type']}\n"
        summary += f"  Saved: {viz['filepath']}\n"
    
    return summary
