"""Agent 2: Insight Generator - Finds business-relevant patterns and trends"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from scipy import stats
from scipy.stats import chi2_contingency, pearsonr, ttest_ind
from utils.llm import get_llm
from graph.state import AnalysisState


def generate_insights(state: AnalysisState) -> AnalysisState:
    """
    Insight Generator Agent - Identifies business-relevant patterns
    
    Tasks:
    - Correlation analysis
    - Trend identification
    - Segment comparisons
    - Distribution analysis
    
    Args:
        state: Current analysis state with dataframe and profile
    
    Returns:
        Updated state with insights_result
    """
    
    df = state.get("dataframe")
    profile = state.get("profile_result")
    
    if df is None or df.empty:
        state["insights_result"] = []
        state["error"] = "No dataframe to analyze"
        return state
    
    state["current_agent"] = "InsightGenerator"
    
    # Quick exit for very large datasets
    if len(df) > 5000:
        state["insights_result"] = _generate_fast_insights(df)
        return state
    
    try:
        insights = []
        
        # 1. CORRELATION ANALYSIS
        numeric_cols = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            
            # Find strong correlations with statistical significance
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        # Calculate p-value for correlation significance
                        col1_data = df[numeric_cols[i]].dropna()
                        col2_data = df[numeric_cols[j]].dropna()
                        
                        # Align the data
                        common_idx = col1_data.index.intersection(col2_data.index)
                        if len(common_idx) > 2:
                            try:
                                _, p_value = pearsonr(col1_data[common_idx], col2_data[common_idx])
                                is_significant = p_value < 0.05
                                significance_text = f"p-value: {p_value:.4f} ({'significant' if is_significant else 'not significant'})"
                            except:
                                p_value = None
                                significance_text = "significance test unavailable"
                        else:
                            p_value = None
                            significance_text = "insufficient data"
                        
                        # Add plain language explanation
                        explanation = _explain_correlation(numeric_cols[i], numeric_cols[j], corr_val)
                        insights.append({
                            "type": "correlation",
                            "title": f"Strong Correlation: {numeric_cols[i]} ↔ {numeric_cols[j]}",
                            "description": f"High {'positive' if corr_val > 0 else 'negative'} correlation ({corr_val:.3f}). {significance_text}",
                            "explanation": explanation,
                            "why_it_matters": "When one value increases, the other tends to " + ("increase" if corr_val > 0 else "decrease") + " proportionally",
                            "action": "Consider using one to predict the other, or investigate the underlying relationship",
                            "confidence": abs(corr_val),
                            "value": float(corr_val),
                            "p_value": float(p_value) if p_value is not None else None,
                            "statistically_significant": is_significant if p_value is not None else None
                        })
        
        # 2. DISTRIBUTION ANALYSIS
        for col in numeric_cols:
            if df[col].notna().sum() > 0:
                # Check for skewness
                skewness = df[col].skew()
                if abs(skewness) > 1:
                    explanation = _explain_skewness(col, skewness)
                    insights.append({
                        "type": "distribution",
                        "title": f"Skewed Distribution: {col}",
                        "description": f"Column '{col}' shows {'right' if skewness > 0 else 'left'} skew (skewness: {skewness:.2f})",
                        "explanation": explanation,
                        "why_it_matters": "Skewed data means most values are concentrated on one side, with outliers on the other",
                        "action": "Consider log transformation or removing outliers for better analysis",
                        "confidence": min(abs(skewness) / 3, 1.0),
                        "value": float(skewness)
                    })
        
        # 3. CATEGORICAL ANALYSIS
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        # Chi-square tests for categorical relationships
        if len(categorical_cols) > 1:
            for i in range(len(categorical_cols)):
                for j in range(i + 1, len(categorical_cols)):
                    col1, col2 = categorical_cols[i], categorical_cols[j]
                    
                    # Create contingency table
                    try:
                        contingency_table = pd.crosstab(df[col1], df[col2])
                        
                        # Only test if both have reasonable cardinality
                        if 2 <= len(contingency_table) <= 20 and 2 <= len(contingency_table.columns) <= 20:
                            chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                            
                            if p_value < 0.05:  # Significant relationship
                                # Calculate Cramér's V for effect size
                                n = contingency_table.sum().sum()
                                cramers_v = np.sqrt(chi2 / (n * (min(len(contingency_table), len(contingency_table.columns)) - 1)))
                                
                                insights.append({
                                    "type": "categorical_relationship",
                                    "title": f"Categorical Relationship: {col1} ↔ {col2}",
                                    "description": f"Significant association detected (χ² = {chi2:.2f}, p-value: {p_value:.4f}, Cramér's V: {cramers_v:.3f})",
                                    "explanation": f"The categories in '{col1}' and '{col2}' are not independent - knowing one helps predict the other",
                                    "why_it_matters": "These variables influence each other, which can reveal important business relationships",
                                    "action": "Explore cross-tabulations and conditional probabilities between these categories",
                                    "confidence": min(cramers_v, 1.0),
                                    "chi2_statistic": float(chi2),
                                    "p_value": float(p_value),
                                    "cramers_v": float(cramers_v),
                                    "statistically_significant": True
                                })
                    except Exception:
                        pass  # Skip if chi-square test fails
        
        # Categorical imbalance analysis
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            
            # Check for imbalanced categories
            if len(value_counts) > 1:
                top_percentage = (value_counts.iloc[0] / len(df)) * 100
                if top_percentage > 60:
                    insights.append({
                        "type": "imbalance",
                        "title": f"Imbalanced Categories: {col}",
                        "description": f"'{value_counts.index[0]}' represents {top_percentage:.1f}% of {col}",
                        "explanation": f"In the '{col}' column, '{value_counts.index[0]}' appears much more frequently than other values ({top_percentage:.1f}% of all records)",
                        "why_it_matters": "Imbalanced data can make it hard to see patterns in minority categories",
                        "action": "Consider grouping rare categories or using stratified sampling for balanced analysis",
                        "confidence": top_percentage / 100,
                        "value": float(top_percentage)
                    })
        
        # 4. T-TESTS FOR GROUP COMPARISONS
        # Test numeric columns across binary/low-cardinality categorical groups
        for cat_col in categorical_cols:
            unique_vals = df[cat_col].nunique()
            
            # Only for binary or low cardinality categoricals (2-5 categories)
            if 2 <= unique_vals <= 5:
                categories = df[cat_col].dropna().unique()
                
                # For each numeric column, test if groups differ significantly
                for num_col in numeric_cols[:5]:  # Limit to avoid too many tests
                    if unique_vals == 2:  # Binary comparison (independent t-test)
                        try:
                            group1_data = df[df[cat_col] == categories[0]][num_col].dropna()
                            group2_data = df[df[cat_col] == categories[1]][num_col].dropna()
                            
                            if len(group1_data) >= 3 and len(group2_data) >= 3:
                                t_stat, p_value = ttest_ind(group1_data, group2_data)
                                
                                if p_value < 0.05:  # Significant difference
                                    mean1 = group1_data.mean()
                                    mean2 = group2_data.mean()
                                    diff_pct = abs((mean1 - mean2) / mean1 * 100) if mean1 != 0 else 0
                                    
                                    insights.append({
                                        "type": "group_comparison",
                                        "title": f"Significant Difference: {num_col} by {cat_col}",
                                        "description": f"'{categories[0]}' (mean: {mean1:.2f}) vs '{categories[1]}' (mean: {mean2:.2f}). t-test: p-value = {p_value:.4f}",
                                        "explanation": f"The average {num_col} is significantly different between '{categories[0]}' and '{categories[1]}' groups ({diff_pct:.1f}% difference)",
                                        "why_it_matters": f"The {cat_col} category has a measurable impact on {num_col} values",
                                        "action": f"Investigate why {cat_col} affects {num_col}, or use {cat_col} to segment your analysis",
                                        "confidence": min(1 - p_value, 0.95),
                                        "t_statistic": float(t_stat),
                                        "p_value": float(p_value),
                                        "group1_mean": float(mean1),
                                        "group2_mean": float(mean2),
                                        "difference_percent": float(diff_pct),
                                        "statistically_significant": True
                                    })
                        except Exception:
                            pass  # Skip if t-test fails
        
        # 5. MISSING DATA PATTERNS
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            for col in missing_data[missing_data > 0].index:
                missing_pct = (missing_data[col] / len(df)) * 100
                if missing_pct > 10:
                    insights.append({
                        "type": "missing_data",
                        "title": f"Significant Missing Data: {col}",
                        "description": f"Column '{col}' has {missing_pct:.1f}% missing values",
                        "explanation": f"Out of {len(df):,} total records, {missing_data[col]:,} are missing in '{col}'",
                        "why_it_matters": "Missing data can lead to incomplete analysis and biased results",
                        "action": "Decide whether to fill missing values (mean/median), remove rows, or exclude this column",
                        "confidence": min(missing_pct / 50, 1.0),
                        "value": float(missing_pct)
                    })
        
        # 6. DUPLICATE ANALYSIS
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            dup_pct = (duplicates / len(df)) * 100
            insights.append({
                "type": "duplicates",
                "title": "Duplicate Records Detected",
                "description": f"Found {duplicates} duplicate rows ({dup_pct:.1f}% of dataset)",
                "explanation": f"{duplicates:,} rows are exact copies of other rows in your dataset",
                "why_it_matters": "Duplicates can skew statistics and create false patterns",
                "action": "Remove duplicates if they're errors, or investigate if they're legitimate repeated events",
                "confidence": min(dup_pct / 50, 1.0),
                "value": float(dup_pct)
            })
        
        # Sort insights by confidence
        insights.sort(key=lambda x: x["confidence"], reverse=True)
        
        state["insights_result"] = insights
        state["execution_status"] = "completed"
        
    except Exception as e:
        state["error"] = f"Error in insight generator: {str(e)}"
        state["insights_result"] = []
    
    return state


def get_insights_summary(state: AnalysisState) -> str:
    """Get human-readable summary of insights"""
    
    insights = state.get("insights_result", [])
    if not insights:
        return "No insights generated"
    
    summary = "💡 KEY INSIGHTS\n"
    summary += "=" * 50 + "\n\n"
    
    for i, insight in enumerate(insights[:10], 1):  # Top 10 insights
        confidence_bar = "█" * int(insight["confidence"] * 10)
        summary += f"{i}. {insight['title']}\n"
        summary += f"   {insight['description']}\n"
        summary += f"   Confidence: {confidence_bar} {insight['confidence']*100:.0f}%\n\n"
    
    return summary


def _generate_fast_insights(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate insights quickly without LLM for large datasets"""
    insights = []
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Quick correlation insights
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    explanation = _explain_correlation(corr_matrix.columns[i], corr_matrix.columns[j], corr_val)
                    insights.append({
                        "type": "correlation",
                        "title": f"Strong correlation: {corr_matrix.columns[i]} & {corr_matrix.columns[j]}",
                        "description": f"Correlation coefficient: {corr_val:.3f}",
                        "explanation": explanation,
                        "why_it_matters": "When one value increases, the other tends to " + ("increase" if corr_val > 0 else "decrease") + " proportionally",
                        "action": "Consider using one to predict the other, or investigate the relationship further",
                        "confidence": min(abs(corr_val), 0.95)
                    })
    
    # Quick stats insights  
    for col in numeric_cols[:5]:
        mean_val = df[col].mean()
        median_val = df[col].median()
        if abs(mean_val - median_val) / (median_val + 0.0001) > 0.3:
            skew_direction = "right" if mean_val > median_val else "left"
            explanation = f"Most values in '{col}' are concentrated on the {'lower' if mean_val > median_val else 'higher'} end, with some {'unusually high' if mean_val > median_val else 'unusually low'} values affecting the average."
            insights.append({
                "type": "distribution",
                "title": f"Skewed distribution in {col}",
                "description": f"Mean ({mean_val:.2f}) differs significantly from median ({median_val:.2f})",
                "explanation": explanation,
                "why_it_matters": "Skewed data means outliers or extreme values are present",
                "action": "Review the extreme values - are they errors or legitimate data points?",
                "confidence": 0.8
            })
    
    return insights[:10]


def _explain_correlation(col1: str, col2: str, corr_val: float) -> str:
    """Generate plain language explanation for correlation"""
    if corr_val > 0:
        return f"When '{col1}' increases, '{col2}' tends to increase as well. This suggests they move together in the same direction."
    else:
        return f"When '{col1}' increases, '{col2}' tends to decrease. This suggests they move in opposite directions."


def _explain_skewness(col: str, skewness: float) -> str:
    """Generate plain language explanation for skewness"""
    if skewness > 0:
        return f"Most values in '{col}' are concentrated on the lower end, with some unusually high values pulling the average up. This creates a 'long tail' toward higher values."
    else:
        return f"Most values in '{col}' are concentrated on the higher end, with some unusually low values pulling the average down. This creates a 'long tail' toward lower values."

