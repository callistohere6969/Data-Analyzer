"""Agent 1: Data Profiler - Understands dataset structure and characteristics"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any
from utils.llm import get_llm
from graph.state import AnalysisState


def _detect_column_types(df: pd.DataFrame, profile: Dict) -> None:
    """Auto-detect special column types and populate summary"""
    
    summary = profile["summary"]
    
    for col in df.columns:
        col_lower = col.lower()
        unique_count = df[col].nunique()
        total_rows = len(df)
        uniqueness_ratio = unique_count / total_rows if total_rows > 0 else 0
        
        # Numeric columns
        if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
            summary["numeric_columns"].append(col)
        else:
            summary["categorical_columns"].append(col)
        
        # Date columns - check if it looks like a date
        try:
            if df[col].dtype == 'object':
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    parsed = pd.to_datetime(sample, errors='coerce', format='mixed')
                    if parsed.notna().sum() / len(sample) > 0.7:
                        summary["date_columns"].append(col)
                        continue
        except:
            pass
        
        # ID columns - high uniqueness or ID-like names
        id_keywords = ['id', 'key', 'index', 'code', 'number', 'num', 'serial']
        has_id_keyword = any(keyword in col_lower for keyword in id_keywords)
        
        if (uniqueness_ratio > 0.95 and unique_count > 10) or \
           (has_id_keyword and uniqueness_ratio > 0.8):
            summary["id_columns"].append(col)
        
        # Constant columns - only 1 unique value
        if unique_count == 1:
            summary["constant_columns"].append(col)
        
        # Target-like columns
        target_keywords = ['target', 'label', 'outcome', 'result', 'class', 'prediction', 
                          'response', 'dependent', 'y', 'output', 'status', 'success', 
                          'failure', 'churn', 'converted']
        has_target_keyword = any(keyword == col_lower or col_lower.endswith(f'_{keyword}') 
                                 for keyword in target_keywords)
        
        # Binary columns (2 unique values, likely target)
        is_binary = unique_count == 2 and df[col].dtype in ['int64', 'object', 'bool']
        
        # Low cardinality categorical (good for classification targets)
        is_low_cardinality = unique_count <= 10 and df[col].dtype == 'object'
        
        if has_target_keyword:
            summary["target_suggestions"].append({
                "column": col,
                "reason": "Name suggests target variable",
                "confidence": "high"
            })
        elif is_binary and not has_id_keyword:
            summary["target_suggestions"].append({
                "column": col,
                "reason": f"Binary column ({unique_count} values)",
                "confidence": "medium"
            })
        elif is_low_cardinality and not has_id_keyword and col_lower not in ['name', 'description', 'notes']:
            summary["target_suggestions"].append({
                "column": col,
                "reason": f"Low cardinality categorical ({unique_count} categories)",
                "confidence": "low"
            })


def _generate_column_recommendations(df: pd.DataFrame, profile: Dict) -> Dict:
    """Generate logic-based recommendations for column usage"""
    
    recommendations = {
        "best_for_visualization": [],
        "best_for_grouping": [],
        "columns_to_clean": []
    }
    
    columns_info = profile.get("columns", {})
    summary = profile.get("summary", {})
    id_cols = set(summary.get("id_columns", []))
    const_cols = set(summary.get("constant_columns", []))
    
    for col, info in columns_info.items():
        col_name = info["name"]
        
        # Skip ID and constant columns for recommendations
        is_id = col_name in id_cols
        is_constant = col_name in const_cols
        
        # === BEST FOR VISUALIZATION ===
        if info.get("numeric"):
            null_pct = info.get("null_percentage", 0)
            outlier_count = info.get("outlier_count", 0)
            non_null = info.get("non_null_count", 0)
            std_dev = info.get("std_dev", 0)
            
            # Good variance (not constant-like)
            has_variance = std_dev is not None and std_dev > 0
            
            # Not too many missing values
            low_missing = null_pct < 30
            
            # Score the column
            score = 0
            reasons = []
            
            if has_variance and not is_id and not is_constant:
                score += 3
                reasons.append("good variance")
            
            if low_missing:
                score += 2
                reasons.append("low missing values")
            
            if outlier_count < non_null * 0.1:  # Less than 10% outliers
                score += 1
                reasons.append("few outliers")
            
            if score >= 4 and not is_id:
                recommendations["best_for_visualization"].append({
                    "column": col_name,
                    "score": score,
                    "reasons": reasons,
                    "type": "numeric"
                })
        
        # === BEST FOR GROUPING ===
        # Categorical with reasonable cardinality
        if not info.get("numeric"):
            unique_values = info.get("unique_values", 0)
            null_pct = info.get("null_percentage", 0)
            
            # Ideal cardinality: 2-20 categories
            ideal_cardinality = 2 <= unique_values <= 20
            acceptable_cardinality = 2 <= unique_values <= 50
            low_missing = null_pct < 20
            
            if (ideal_cardinality or acceptable_cardinality) and not is_id and not is_constant:
                score = 0
                reasons = []
                
                if ideal_cardinality:
                    score += 3
                    reasons.append(f"ideal cardinality ({unique_values} categories)")
                elif acceptable_cardinality:
                    score += 2
                    reasons.append(f"acceptable cardinality ({unique_values} categories)")
                
                if low_missing:
                    score += 2
                    reasons.append("low missing values")
                
                if score >= 3:
                    recommendations["best_for_grouping"].append({
                        "column": col_name,
                        "score": score,
                        "reasons": reasons,
                        "type": "categorical"
                    })
        
        # Date columns are also good for grouping
        if col_name in summary.get("date_columns", []):
            recommendations["best_for_grouping"].append({
                "column": col_name,
                "score": 5,
                "reasons": ["time-based grouping", "trend analysis"],
                "type": "date"
            })
        
        # === COLUMNS TO CLEAN ===
        null_pct = info.get("null_percentage", 0)
        outlier_count = info.get("outlier_count", 0)
        non_null = info.get("non_null_count", 0)
        
        issues = []
        severity = 0
        
        # High missing values
        if null_pct > 50:
            issues.append(f"{null_pct:.1f}% missing values")
            severity += 3
        elif null_pct > 20:
            issues.append(f"{null_pct:.1f}% missing values")
            severity += 2
        
        # Constant columns
        if is_constant:
            issues.append("constant value (no variance)")
            severity += 3
        
        # Too many outliers
        if info.get("numeric") and non_null > 0:
            outlier_pct = (outlier_count / non_null) * 100
            if outlier_pct > 20:
                issues.append(f"{outlier_pct:.1f}% outliers")
                severity += 2
            elif outlier_pct > 10:
                issues.append(f"{outlier_pct:.1f}% outliers")
                severity += 1
        
        # ID columns that should be excluded
        if is_id and not is_constant:
            issues.append("ID column (exclude from analysis)")
            severity += 1
        
        if issues:
            recommendations["columns_to_clean"].append({
                "column": col_name,
                "severity": severity,
                "issues": issues
            })
    
    # Sort by score/severity
    recommendations["best_for_visualization"].sort(key=lambda x: x["score"], reverse=True)
    recommendations["best_for_grouping"].sort(key=lambda x: x["score"], reverse=True)
    recommendations["columns_to_clean"].sort(key=lambda x: x["severity"], reverse=True)
    
    return recommendations


def analyze_data_profile(state: AnalysisState) -> AnalysisState:
    """
    Data Profiler Agent - Generates comprehensive data profile
    
    Tasks:
    - Column types and distributions
    - Missing values analysis
    - Basic statistics (mean, median, std dev)
    - Data quality issues
    - Outlier detection (simple)
    
    Args:
        state: Current analysis state with dataframe
    
    Returns:
        Updated state with profile_result
    """
    
    df = state.get("dataframe")
    if df is None or df.empty:
        state["profile_result"] = None
        state["error"] = "No dataframe to profile"
        return state
    
    state["current_agent"] = "DataProfiler"
    
    try:
        profile = {
            "overview": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024**2
            },
            "columns": {},
            "summary": {
                "numeric_columns": [],
                "categorical_columns": [],
                "date_columns": [],
                "id_columns": [],
                "constant_columns": [],
                "target_suggestions": []
            }
        }
        
        # Analyze each column
        for col in df.columns:
            col_analysis = {
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null_count": df[col].notna().sum(),
                "null_count": df[col].isna().sum(),
                "null_percentage": round((df[col].isna().sum() / len(df)) * 100, 2)
            }
            
            # Numeric columns
            if df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
                col_analysis.update({
                    "numeric": True,
                    "mean": float(df[col].mean()) if df[col].notna().any() else None,
                    "median": float(df[col].median()) if df[col].notna().any() else None,
                    "std_dev": float(df[col].std()) if df[col].notna().any() else None,
                    "min": float(df[col].min()) if df[col].notna().any() else None,
                    "max": float(df[col].max()) if df[col].notna().any() else None,
                    "q1": float(df[col].quantile(0.25)) if df[col].notna().any() else None,
                    "q3": float(df[col].quantile(0.75)) if df[col].notna().any() else None,
                })
                
                # Detect outliers (IQR method)
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = df[(df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))][col]
                col_analysis["outlier_count"] = len(outliers)
                
            # Categorical columns
            else:
                unique_count = df[col].nunique()
                col_analysis.update({
                    "numeric": False,
                    "unique_values": unique_count,
                    "top_values": df[col].value_counts().head(5).to_dict()
                })
            
            profile["columns"][col] = col_analysis
        
        # Auto-detect special column types
        _detect_column_types(df, profile)
        
        # Generate column recommendations
        profile["recommendations"] = _generate_column_recommendations(df, profile)
        
        # Data quality issues
        quality_issues = []
        
        # Calculate Data Quality Score
        total_cells = len(df) * len(df.columns)
        missing_cells = sum(analysis["null_count"] for analysis in profile["columns"].values())
        missing_percentage = (missing_cells / total_cells * 100) if total_cells > 0 else 0
        
        # Check for duplicates
        dup_count = df.duplicated().sum() if len(df) > 0 else 0
        duplicate_percentage = (dup_count / len(df) * 100) if len(df) > 0 else 0
        
        # Calculate outlier percentage (from numeric columns)
        total_numeric_values = 0
        total_outliers = 0
        for col, analysis in profile["columns"].items():
            if analysis.get("numeric"):
                total_numeric_values += analysis["non_null_count"]
                total_outliers += analysis.get("outlier_count", 0)
        
        outlier_percentage = (total_outliers / total_numeric_values * 100) if total_numeric_values > 0 else 0
        
        # Overall Quality Score (100 - deductions)
        quality_score = max(0, 100 - (missing_percentage + duplicate_percentage + outlier_percentage))
        
        profile["data_quality_score"] = {
            "score": round(quality_score, 1),
            "missing_percentage": round(missing_percentage, 2),
            "duplicate_percentage": round(duplicate_percentage, 2),
            "outlier_percentage": round(outlier_percentage, 2),
            "total_missing": missing_cells,
            "total_duplicates": dup_count,
            "total_outliers": total_outliers
        }
        
        # Check for high missing values
        for col, analysis in profile["columns"].items():
            if analysis["null_percentage"] > 50:
                quality_issues.append(f"Column '{col}' has {analysis['null_percentage']}% missing values")
        
        # Check for potential duplicates
        if dup_count > 0:
            quality_issues.append(f"Found {dup_count} duplicate rows ({duplicate_percentage:.1f}%)")
        
        # Check for outliers
        if total_outliers > 0:
            quality_issues.append(f"Found {total_outliers} outliers across numeric columns ({outlier_percentage:.1f}%)")
        
        profile["data_quality_issues"] = quality_issues
        
        state["profile_result"] = profile
        state["execution_status"] = "completed"
        
    except Exception as e:
        state["error"] = f"Error in data profiler: {str(e)}"
        state["profile_result"] = None
    
    return state


def get_profile_summary(state: AnalysisState) -> str:
    """Get human-readable summary of data profile"""
    
    profile = state.get("profile_result")
    if not profile:
        return "No profile available"
    
    summary = f"📊 DATA PROFILE SUMMARY\n"
    summary += f"=" * 50 + "\n"
    summary += f"Rows: {profile['overview']['total_rows']}\n"
    summary += f"Columns: {profile['overview']['total_columns']}\n"
    summary += f"Memory: {profile['overview']['memory_usage_mb']:.2f} MB\n"
    
    # Data Quality Score
    if "data_quality_score" in profile:
        score_data = profile["data_quality_score"]
        score = score_data["score"]
        summary += f"\n🎯 DATA QUALITY SCORE: {score}/100\n"
        summary += f"  • Missing values: {score_data['missing_percentage']:.2f}%\n"
        summary += f"  • Duplicate rows: {score_data['duplicate_percentage']:.2f}%\n"
        summary += f"  • Outliers: {score_data['outlier_percentage']:.2f}%\n"
    
    summary += "\nCOLUMN ANALYSIS:\n"
    for col_name, col_data in profile["columns"].items():
        summary += f"\n  {col_name} ({col_data['dtype']})\n"
        summary += f"    Non-null: {col_data['non_null_count']} ({100 - col_data['null_percentage']:.1f}%)\n"
        
        if col_data.get("numeric"):
            summary += f"    Mean: {col_data.get('mean'):.2f}, "
            summary += f"Median: {col_data.get('median'):.2f}\n"
            summary += f"    Range: [{col_data.get('min'):.2f}, {col_data.get('max'):.2f}]\n"
            if col_data.get("outlier_count", 0) > 0:
                summary += f"    ⚠️ Outliers: {col_data['outlier_count']}\n"
        else:
            summary += f"    Unique values: {col_data.get('unique_values', 'N/A')}\n"
    
    if profile.get("data_quality_issues"):
        summary += f"\n⚠️ DATA QUALITY ISSUES:\n"
        for issue in profile["data_quality_issues"]:
            summary += f"  • {issue}\n"
    
    return summary
