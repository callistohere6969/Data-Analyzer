"""Agent 3: Anomaly Detector - Identifies unusual patterns and outliers"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from scipy import stats
from graph.state import AnalysisState


def detect_anomalies(state: AnalysisState) -> AnalysisState:
    """
    Anomaly Detector Agent - Flags unusual patterns and outliers
    
    Tasks:
    - Statistical outliers (Z-score, IQR)
    - Unexpected category distributions
    - Time-series anomalies (if date column exists)
    
    Args:
        state: Current analysis state with dataframe
    
    Returns:
        Updated state with anomalies_result
    """
    
    df = state.get("dataframe")
    if df is None or df.empty:
        state["anomalies_result"] = []
        state["error"] = "No dataframe to analyze for anomalies"
        return state
    
    state["current_agent"] = "AnomalyDetector"
    
    try:
        anomalies = []
        
        # 1. Z-SCORE BASED OUTLIER DETECTION
        numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns
        
        for col in numeric_cols:
            if df[col].notna().sum() > 3:  # Need at least some non-null values
                z_scores = np.abs(stats.zscore(df[col].dropna()))
                outlier_threshold = 3  # 3 sigma
                
                outlier_count = np.sum(z_scores > outlier_threshold)
                if outlier_count > 0:
                    outlier_percentage = (outlier_count / df[col].notna().sum()) * 100
                    anomalies.append({
                        "type": "z_score_outlier",
                        "column": col,
                        "title": f"Z-Score Outliers in {col}",
                        "description": f"Detected {outlier_count} outliers ({outlier_percentage:.1f}% of non-null values) using Z-score method",
                        "explanation": f"In the '{col}' column, {outlier_count} values are extremely different from the average - they're more than 3 standard deviations away from the mean. These are the 'oddball' values.",
                        "why_it_matters": "Outliers can indicate errors, rare events, or important exceptions that need attention",
                        "action": f"Review these {outlier_count} unusual values - are they data entry errors, special cases, or legitimate extreme values?",
                        "count": int(outlier_count),
                        "percentage": float(outlier_percentage),
                        "severity": "high" if outlier_percentage > 5 else "medium" if outlier_percentage > 1 else "low"
                    })
        
        # 2. IQR BASED OUTLIER DETECTION
        for col in numeric_cols:
            if df[col].notna().sum() > 3:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                if IQR > 0:
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                    outlier_count = len(outliers)
                    
                    if outlier_count > 0:
                        outlier_percentage = (outlier_count / len(df)) * 100
                        anomalies.append({
                            "type": "iqr_outlier",
                            "column": col,
                            "title": f"IQR Outliers in {col}",
                            "description": f"Detected {outlier_count} values outside [{lower_bound:.2f}, {upper_bound:.2f}]",
                            "explanation": f"In '{col}', {outlier_count} values fall outside the typical range. Based on where most of your data sits (between {Q1:.2f} and {Q3:.2f}), anything below {lower_bound:.2f} or above {upper_bound:.2f} is considered unusual.",
                            "why_it_matters": "These unusual values can skew your analysis and might represent special cases or errors",
                            "action": f"Investigate these {outlier_count} outliers - consider removing them or analyzing them separately",
                            "count": int(outlier_count),
                            "percentage": float(outlier_percentage),
                            "lower_bound": float(lower_bound),
                            "upper_bound": float(upper_bound),
                            "severity": "high" if outlier_percentage > 5 else "medium" if outlier_percentage > 1 else "low"
                        })
        
        # 3. CATEGORICAL ANOMALIES
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            
            # Check for single-occurrence categories
            single_occurrence = (value_counts == 1).sum()
            if single_occurrence > 0:
                percentage = (single_occurrence / len(value_counts)) * 100
                if percentage > 20:  # If more than 20% of categories appear once
                    anomalies.append({
                        "type": "sparse_categories",
                        "column": col,
                        "title": f"Sparse Categories in {col}",
                        "description": f"{single_occurrence} categories appear only once ({percentage:.1f}% of all categories)",
                        "explanation": f"In the '{col}' column, {single_occurrence} different values appear only once in the entire dataset. This means you have many rare or unique values.",
                        "why_it_matters": "Too many rare categories can make it hard to find meaningful patterns and may indicate inconsistent data entry",
                        "action": "Consider grouping rare categories into an 'Other' category, or check for typos and inconsistent naming",
                        "count": int(single_occurrence),
                        "percentage": float(percentage),
                        "severity": "low"
                    })
        
        # 4. TIME-SERIES ANOMALIES (if date columns exist)
        date_cols = []
        for col in df.columns:
            try:
                parsed = pd.to_datetime(df[col], errors='coerce', format='mixed')
                if parsed.notna().sum() > 0:
                    date_cols.append(col)
            except Exception:
                pass
        
        for date_col in date_cols:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce', format='mixed')
            numeric_cols_for_ts = df_copy.select_dtypes(include=['int64', 'float64']).columns
            
            for num_col in numeric_cols_for_ts:
                # Group by date and calculate daily changes
                daily_data = df_copy.groupby(date_col)[num_col].sum()
                if len(daily_data) > 3:
                    daily_change = daily_data.diff().abs()
                    mean_change = daily_change.mean()
                    std_change = daily_change.std()
                    
                    if std_change > 0:
                        # Find anomalous days
                        anomalous_days = daily_change[daily_change > (mean_change + 3 * std_change)]
                        if len(anomalous_days) > 0:
                            anomalies.append({
                                "type": "temporal_anomaly",
                                "column": f"{num_col} (by {date_col})",
                                "title": f"Temporal Anomaly in {num_col}",
                                "description": f"Detected {len(anomalous_days)} unusual spikes in daily {num_col}",
                                "explanation": f"On {len(anomalous_days)} specific dates, '{num_col}' showed unusually large changes compared to typical daily variations. These are unexpected jumps or drops.",
                                "why_it_matters": "Sudden spikes in time-series data can indicate errors, special events, or important business changes",
                                "action": f"Review what happened on these {len(anomalous_days)} dates - were there special events, data collection issues, or legitimate business changes?",
                                "count": int(len(anomalous_days)),
                                "severity": "medium"
                            })
        
        # Sort anomalies by severity
        severity_order = {"high": 0, "medium": 1, "low": 2}
        anomalies.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))
        
        state["anomalies_result"] = anomalies
        state["execution_status"] = "completed"
        
    except Exception as e:
        state["error"] = f"Error in anomaly detector: {str(e)}"
        state["anomalies_result"] = []
    
    return state


def get_anomalies_summary(state: AnalysisState) -> str:
    """Get human-readable summary of anomalies"""
    
    anomalies = state.get("anomalies_result", [])
    if not anomalies:
        return "No anomalies detected ✓"
    
    summary = "⚠️ ANOMALIES DETECTED\n"
    summary += "=" * 50 + "\n\n"
    
    severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    
    for anomaly in anomalies[:10]:  # Top 10 anomalies
        severity = anomaly.get("severity", "low")
        summary += f"{severity_emoji.get(severity, '⚪')} {anomaly['title']}\n"
        summary += f"   {anomaly['description']}\n\n"
    
    return summary
