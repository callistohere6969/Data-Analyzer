"""Agent 5: Explanation Agent - Synthesizes all analyses into a comprehensive report"""

import json
import pandas as pd
from typing import Dict, List, Any
from utils.llm import get_llm
from graph.state import AnalysisState
from utils.sqlite_helper import get_schema_info, run_sql_query


def synthesize_report(state: AnalysisState) -> AnalysisState:
    """
    Explanation Agent - Synthesizes outputs from all agents
    
    Tasks:
    - Integrate results from all 4 agents
    - Generate natural language executive summary
    - Prepare for follow-up questions
    
    Args:
        state: Current analysis state with all agent outputs
    
    Returns:
        Updated state with final_summary
    """
    
    state["current_agent"] = "ExplanationAgent"
    
    try:
        # Gather all analysis results
        profile = state.get("profile_result", {})
        insights = state.get("insights_result", [])
        anomalies = state.get("anomalies_result", [])
        visualizations = state.get("visualizations", [])
        
        # Build context for LLM
        context = _build_analysis_context(profile, insights, anomalies, visualizations)
        
        # Generate executive summary using LLM
        summary = _generate_llm_summary(context)
        
        state["final_summary"] = summary
        state["execution_status"] = "completed"
        
    except Exception as e:
        state["error"] = f"Error in explanation agent: {str(e)}"
        state["final_summary"] = _generate_fallback_summary(state)
    
    return state


def _build_analysis_context(profile: Dict, insights: List, anomalies: List, visualizations: List) -> str:
    """Build a comprehensive context string for the LLM"""
    
    context = "ANALYSIS SUMMARY CONTEXT\n"
    context += "=" * 60 + "\n\n"
    
    # DATA PROFILE
    if profile:
        context += "DATA PROFILE:\n"
        overview = profile.get("overview", {})
        context += f"• Total Rows: {overview.get('total_rows', 'N/A')}\n"
        context += f"• Total Columns: {overview.get('total_columns', 'N/A')}\n"
        context += f"• Memory Usage: {overview.get('memory_usage_mb', 'N/A'):.2f} MB\n"
        
        # Data Quality Score
        if "data_quality_score" in profile:
            score_data = profile["data_quality_score"]
            context += f"\n🎯 DATA QUALITY SCORE: {score_data['score']}/100\n"
            context += f"  - Missing: {score_data['missing_percentage']:.2f}%\n"
            context += f"  - Duplicates: {score_data['duplicate_percentage']:.2f}%\n"
            context += f"  - Outliers: {score_data['outlier_percentage']:.2f}%\n"
        context += "\n"
        
        # Quality issues
        quality_issues = profile.get("data_quality_issues", [])
        if quality_issues:
            context += "Data Quality Issues:\n"
            for issue in quality_issues:
                context += f"  - {issue}\n"
            context += "\n"
    
    # KEY INSIGHTS
    if insights:
        context += "KEY INSIGHTS:\n"
        for i, insight in enumerate(insights[:5], 1):  # Top 5 insights
            context += f"{i}. {insight.get('title', 'N/A')}\n"
            context += f"   {insight.get('description', 'N/A')}\n"
            context += f"   Confidence: {insight.get('confidence', 0)*100:.0f}%\n"
        context += "\n"
    
    # ANOMALIES
    if anomalies:
        context += "DETECTED ANOMALIES:\n"
        for anomaly in anomalies[:5]:  # Top 5 anomalies
            context += f"• {anomaly.get('title', 'N/A')}\n"
            context += f"  {anomaly.get('description', 'N/A')}\n"
        context += "\n"
    
    # VISUALIZATIONS
    if visualizations:
        context += f"VISUALIZATIONS GENERATED: {len(visualizations)}\n"
        context += "Types: " + ", ".join(set(v.get('chart_type', 'unknown') for v in visualizations)) + "\n"
    
    return context


def _generate_llm_summary(context: str) -> str:
    """Generate executive summary using LLM"""
    
    prompt = f"""Based on the analysis, provide a brief 2-3 paragraph executive summary:

{context}

Summary:"""
    
    try:
        llm = get_llm(temperature=0.7, max_tokens=500)  # Reduced from 4096
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        # Fallback if LLM fails
        error_msg = str(e)
        if "402" in error_msg or "credits" in error_msg:
            return "⚠️ OpenRouter credits exhausted. Displaying automatic summary instead:\n\n" + _generate_fallback_summary_from_context(context)
        return f"Error generating LLM summary: {str(e)}"


def _generate_fallback_summary_from_context(context: str) -> str:
    """Generate summary from context without LLM"""
    lines = context.split('\n')
    summary = "ANALYSIS SUMMARY\n" + "="*50 + "\n\n"
    
    # Extract key info from context
    for line in lines:
        if 'Total' in line or 'Key' in line or 'Anomal' in line or 'Strong' in line:
            summary += line + "\n"
    
    return summary


def _generate_fallback_summary(state: AnalysisState) -> str:
    """Generate fallback summary if LLM fails"""
    
    summary = "EXECUTIVE SUMMARY\n"
    summary += "=" * 50 + "\n\n"
    
    profile = state.get("profile_result", {})
    insights = state.get("insights_result", [])
    anomalies = state.get("anomalies_result", [])
    
    if profile:
        overview = profile.get("overview", {})
        summary += f"Dataset Overview:\n"
        summary += f"• Total Records: {overview.get('total_rows', 'N/A')}\n"
        summary += f"• Features: {overview.get('total_columns', 'N/A')}\n"
        
        # Add quality score
        if "data_quality_score" in profile:
            score_data = profile["data_quality_score"]
            summary += f"• Data Quality Score: {score_data['score']}/100\n"
        summary += "\n"
    
    if insights:
        summary += f"Key Findings:\n"
        for i, insight in enumerate(insights[:3], 1):
            summary += f"{i}. {insight.get('title', 'N/A')}\n"
        summary += "\n"
    
    if anomalies:
        summary += f"Anomalies:\n"
        summary += f"• Total anomalies detected: {len(anomalies)}\n"
        for anomaly in anomalies[:2]:
            summary += f"• {anomaly.get('title', 'N/A')}\n"
    
    return summary


def answer_followup_question(state: AnalysisState, question: str) -> str:
    """
    Answer follow-up questions by retrieving data directly from the dataframe
    Falls back to LLM if needed
    
    Args:
        state: Analysis state with dataframe and results
        question: User's follow-up question
    
    Returns:
        Answer to the question
    """
    
    # First, try to answer via SQLite (if available)
    db_path = state.get("db_path")
    db_table = state.get("db_table", "data")
    if db_path:
        sql_answer = _answer_from_sql(question, db_path, db_table, state)
        if sql_answer:
            return sql_answer

    # Next, try to answer from actual data
    df = state.get("dataframe")
    if df is not None and isinstance(df, pd.DataFrame):
        data_answer = _retrieve_data_answer(df, question, state)
        if data_answer and data_answer != "":
            return data_answer
    
    # Fallback to LLM if data retrieval didn't work
    try:
        context = _build_analysis_context(
            state.get("profile_result", {}),
            state.get("insights_result", []),
            state.get("anomalies_result", []),
            state.get("visualizations", [])
        )
        
        prompt = f"""Based on this analysis, answer: {question}

{context}"""
        
        llm = get_llm(temperature=0.5, max_tokens=200)  # Minimal tokens for Q&A
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        error_str = str(e)
        if "402" in error_str or "credits" in error_str.lower():
            # Attempt basic answer from context
            return _answer_from_context(question, state)
        return f"Error answering question: {str(e)}"


def _answer_from_sql(question: str, db_path: str, table_name: str, state: AnalysisState) -> str:
    """Answer question by generating and executing SQL on the SQLite DB."""
    schema_info = get_schema_info(db_path, table_name)

    # Try LLM-generated SQL first
    try:
        prompt = _build_sql_prompt(question, schema_info, table_name)
        llm = get_llm(temperature=0.1, max_tokens=150)
        response = llm.invoke(prompt)
        sql = _extract_sql(response.content)
        cols, rows = run_sql_query(db_path, sql, max_rows=20)
        if not rows:
            return ""
        return _format_sql_result(sql, cols, rows)
    except Exception as e:
        error_str = str(e)
        if "402" in error_str or "credits" in error_str.lower():
            # LLM unavailable - try rule-based SQL
            sql = _rule_based_sql(question, state)
            if sql:
                try:
                    cols, rows = run_sql_query(db_path, sql, max_rows=20)
                    if not rows:
                        return ""
                    return _format_sql_result(sql, cols, rows)
                except Exception:
                    return ""
        return ""


def _build_sql_prompt(question: str, schema_info: str, table_name: str) -> str:
    return (
        "You are a SQL expert. Generate a single SQLite SELECT query to answer the question. "
        "Return ONLY the SQL query, no explanation.\n\n"
        f"Schema:\n{schema_info}\n\n"
        f"Question: {question}\n\n"
        f"Use table name: {table_name}. Limit results to 20 rows when returning raw rows. "
        "If day-of-week questions are asked, use *_day_name columns when available."
    )


def _extract_sql(text: str) -> str:
    """Extract SQL from an LLM response."""
    if "```" in text:
        parts = text.split("```")
        if len(parts) >= 2:
            return parts[1].replace("sql", "").strip()
    return text.strip()


def _rule_based_sql(question: str, state: AnalysisState) -> str:
    """Simple SQL generation without LLM for common questions."""
    df = state.get("dataframe")
    if df is None:
        return ""

    question_lower = question.lower()
    columns = [c for c in df.columns]
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    # Most wins questions
    if "wins" in question_lower and any(w in question_lower for w in ["most", "highest", "max", "maximum", "top"]):
        wins_cols = [c for c in columns if "win" in c.lower()]
        name_cols = [c for c in columns if any(k in c.lower() for k in ["team", "player", "name", "club"])]
        if wins_cols:
            wins_col = wins_cols[0]
            name_col = name_cols[0] if name_cols else None
            if name_col:
                return f"SELECT [{name_col}] AS name, [{wins_col}] AS wins FROM data ORDER BY [{wins_col}] DESC LIMIT 1"
            return f"SELECT [{wins_col}] AS wins FROM data ORDER BY [{wins_col}] DESC LIMIT 1"

    # Worst AQI / best AQI questions
    if "aqi" in question_lower and any(w in question_lower for w in ["worst", "highest", "max", "maximum"]):
        aqi_cols = [c for c in columns if "aqi" in c.lower()]
        temp_cols = [c for c in columns if "temp" in c.lower() or "temperature" in c.lower()]
        date_cols = [c for c in columns if "date" in c.lower() or c.lower() == "day"]

        if aqi_cols:
            aqi_col = aqi_cols[0]
            temp_col = temp_cols[0] if temp_cols else None
            date_col = date_cols[0] if date_cols else None

            select_parts = []
            if date_col:
                select_parts.append(f"[{date_col}] AS day")
            if temp_col:
                select_parts.append(f"[{temp_col}] AS temperature")
            select_parts.append(f"[{aqi_col}] AS aqi")

            select_clause = ", ".join(select_parts)
            return f"SELECT {select_clause} FROM data ORDER BY [{aqi_col}] DESC LIMIT 1"

    # Day-of-week queries
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if any(day in question_lower for day in weekdays):
        day = next((d for d in weekdays if d in question_lower), None)
        if day:
            # Prefer *_day_name columns created during DB build
            day_name_cols = [c for c in columns if c.lower().endswith("_day_name")]
            if day_name_cols:
                col = day_name_cols[0]
                return f"SELECT * FROM data WHERE LOWER([{col}]) = '{day}'"

            # Fallback to date columns using strftime (SQLite)
            date_cols = [c for c in columns if c.lower().endswith("_date") or "date" in c.lower()]
            if date_cols:
                col = date_cols[0]
                weekday_map = {
                    "sunday": "0",
                    "monday": "1",
                    "tuesday": "2",
                    "wednesday": "3",
                    "thursday": "4",
                    "friday": "5",
                    "saturday": "6",
                }
                return f"SELECT * FROM data WHERE strftime('%w', [{col}]) = '{weekday_map[day]}'"

            # If question mentions condition, select condition column for that day
            condition_cols = [c for c in columns if "condition" in c.lower()]
            if condition_cols and day_name_cols:
                return f"SELECT [{condition_cols[0]}] FROM data WHERE LOWER([{day_name_cols[0]}]) = '{day}'"

    # Max - smarter column matching
    if any(w in question_lower for w in ["max", "maximum", "highest"]):
        # Try to find column that matches words in the question
        for col in numeric_cols:
            col_words = col.lower().replace('_', ' ').replace('-', ' ').split()
            question_words = question_lower.replace('_', ' ').replace('-', ' ').split()
            # Check if all words from column name appear in question
            if all(word in question_words for word in col_words):
                return f"SELECT MAX([{col}]) AS max_{col} FROM data"
            # Or if the full column name (with underscores removed) is in the question
            col_normalized = col.lower().replace('_', '').replace('-', '')
            question_normalized = question_lower.replace(' ', '').replace('_', '').replace('-', '')
            if col_normalized in question_normalized:
                return f"SELECT MAX([{col}]) AS max_{col} FROM data"
        # Default: return max of first 3 numeric columns
        if numeric_cols:
            return f"SELECT {', '.join([f'MAX([{c}]) AS max_{c}' for c in numeric_cols[:3]])} FROM data"

    # Min - smarter column matching
    if any(w in question_lower for w in ["min", "minimum", "lowest"]):
        # Try to find column that matches words in the question
        for col in numeric_cols:
            col_words = col.lower().replace('_', ' ').replace('-', ' ').split()
            question_words = question_lower.replace('_', ' ').replace('-', ' ').split()
            # Check if all words from column name appear in question
            if all(word in question_words for word in col_words):
                return f"SELECT MIN([{col}]) AS min_{col} FROM data"
            # Or if the full column name (with underscores removed) is in the question
            col_normalized = col.lower().replace('_', '').replace('-', '')
            question_normalized = question_lower.replace(' ', '').replace('_', '').replace('-', '')
            if col_normalized in question_normalized:
                return f"SELECT MIN([{col}]) AS min_{col} FROM data"
        # Check if column name appears directly
        for col in numeric_cols:
            if col.lower() in question_lower:
                return f"SELECT MIN([{col}]) AS min_{col} FROM data"
        if numeric_cols:
            return f"SELECT {', '.join([f'MIN([{c}]) AS min_{c}' for c in numeric_cols[:3]])} FROM data"

    # Average - smarter column matching
    if any(w in question_lower for w in ["average", "mean", "avg"]):
        # Try to find column that matches words in the question
        for col in numeric_cols:
            col_words = col.lower().replace('_', ' ').replace('-', ' ').split()
            question_words = question_lower.replace('_', ' ').replace('-', ' ').split()
            # Check if all words from column name appear in question
            if all(word in question_words for word in col_words):
                return f"SELECT AVG([{col}]) AS avg_{col} FROM data"
            # Or if the full column name (with underscores removed) is in the question
            col_normalized = col.lower().replace('_', '').replace('-', '')
            question_normalized = question_lower.replace(' ', '').replace('_', '').replace('-', '')
            if col_normalized in question_normalized:
                return f"SELECT AVG([{col}]) AS avg_{col} FROM data"
        # Check if column name appears directly
        for col in numeric_cols:
            if col.lower() in question_lower:
                return f"SELECT AVG([{col}]) AS avg_{col} FROM data"
        # Default: return avg of first 3 numeric columns
        if numeric_cols:
            return f"SELECT {', '.join([f'AVG([{c}]) AS avg_{c}' for c in numeric_cols[:3]])} FROM data"

    # Count
    if any(w in question_lower for w in ["count", "how many", "total rows", "total records"]):
        return "SELECT COUNT(*) AS total_rows FROM data"

    # Most/Top for categorical columns (e.g., "which product sold most")
    if any(w in question_lower for w in ["most", "top", "highest", "best", "popular", "common"]):
        # Look for categorical columns mentioned in question
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in categorical_cols:
            col_words = col.lower().replace('_', ' ').replace('-', ' ').split()
            question_words = question_lower.replace('_', ' ').replace('-', ' ').split()
            # Check if column name words appear in question
            if any(word in question_words for word in col_words):
                # Return top value by count
                return f"SELECT [{col}], COUNT(*) as count FROM data GROUP BY [{col}] ORDER BY count DESC LIMIT 1"
            # Normalized matching
            col_normalized = col.lower().replace('_', '').replace('-', '')
            question_normalized = question_lower.replace(' ', '').replace('_', '').replace('-', '')
            if col_normalized in question_normalized:
                return f"SELECT [{col}], COUNT(*) as count FROM data GROUP BY [{col}] ORDER BY count DESC LIMIT 1"

    # Simple column lookup
    for col in columns:
        if col.lower() in question_lower:
            return f"SELECT [{col}] FROM data"

    return ""


def _format_sql_result(sql: str, cols: List[str], rows: List[tuple]) -> str:
    if not rows:
        return "No results found for that query."

    # Single value
    if len(cols) == 1 and len(rows) == 1:
        return f"Result: **{cols[0]} = {rows[0][0]}**"

    # Tabular
    preview_rows = rows[:10]
    table_lines = [" | ".join(cols)]
    table_lines.append(" | ".join(["---"] * len(cols)))
    for row in preview_rows:
        table_lines.append(" | ".join([str(x) for x in row]))

    return "SQL Answer (preview):\n\n" + "\n".join(table_lines) + f"\n\nQuery used: {sql}"


def _retrieve_data_answer(df: pd.DataFrame, question: str, state: AnalysisState) -> str:
    """
    Retrieve answers directly from the dataframe using intelligent data querying
    Answers questions like "what is max salary", "show me employees in sales", etc.
    """
    question_lower = question.lower()
    columns = df.columns.tolist()
    
    # Find numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    try:
        # Handle DAY-OF-WEEK queries
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if any(day in question_lower for day in weekdays):
            day = next((d for d in weekdays if d in question_lower), None)
            if day:
                # Find date-like columns
                date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower() or "day" in c.lower()]
                if date_cols:
                    col = date_cols[0]
                    parsed = pd.to_datetime(df[col], errors="coerce")
                    mask = parsed.dt.day_name().str.lower() == day
                    filtered = df[mask]
                    if "condition" in question_lower:
                        condition_cols = [c for c in df.columns if "condition" in c.lower()]
                        if condition_cols:
                            values = filtered[condition_cols[0]].dropna().unique().tolist()
                            return f"📊 **Condition on {day.capitalize()}**: {', '.join(map(str, values[:5]))}"
                    return f"📊 **Rows on {day.capitalize()}**: {len(filtered)}"

        # Handle MAX/HIGHEST queries
        if any(word in question_lower for word in ["maximum", "max", "highest", "maximum value", "largest"]):
            for col in numeric_cols:
                if col.lower() in question_lower:
                    max_val = df[col].max()
                    return f"📊 **Maximum {col}**: {max_val}\n\nThis is the highest value in the {col} column of your dataset."
            # If no specific column mentioned, show top numeric stats
            stats = ""
            for col in numeric_cols[:3]:
                stats += f"• **{col}**: {df[col].max()}\n"
            return f"📊 **Maximum Values**:\n{stats}"
        
        # Handle MIN/LOWEST queries
        if any(word in question_lower for word in ["minimum", "min", "lowest", "minimum value", "smallest"]):
            for col in numeric_cols:
                if col.lower() in question_lower:
                    min_val = df[col].min()
                    return f"📊 **Minimum {col}**: {min_val}\n\nThis is the lowest value in the {col} column of your dataset."
            # If no specific column mentioned, show top numeric stats
            stats = ""
            for col in numeric_cols[:3]:
                stats += f"• **{col}**: {df[col].min()}\n"
            return f"📊 **Minimum Values**:\n{stats}"
        
        # Handle AVERAGE/MEAN queries
        if any(word in question_lower for word in ["average", "mean", "avg"]):
            for col in numeric_cols:
                if col.lower() in question_lower:
                    avg_val = df[col].mean()
                    return f"📊 **Average {col}**: {avg_val:.2f}\n\nThis is the mean value across all records."
            # If no specific column mentioned, show top numeric stats
            stats = ""
            for col in numeric_cols[:3]:
                stats += f"• **{col}**: {df[col].mean():.2f}\n"
            return f"📊 **Average Values**:\n{stats}"
        
        # Handle COUNT queries
        if any(word in question_lower for word in ["count", "how many", "total records", "total rows"]):
            total = len(df)
            return f"📊 **Total Records**: {total}\n\nYour dataset contains {total} rows of data."
        
        # Handle filtering queries (e.g., "show me where sales > 1000")
        if "where" in question_lower or "filter" in question_lower or "show me" in question_lower:
            for col in columns:
                if col.lower() in question_lower:
                    # Try to extract numeric values from question
                    for num in range(10000, 0, -100):
                        if str(num) in question:
                            filtered = df[df[col] > num]
                            return f"📊 **Filtered Results**:\n• Found {len(filtered)} records where {col} > {num}\n• Sample values: {filtered[col].head(3).tolist()}"
                    return f"📊 **Column '{col}' Data**:\n• Count: {len(df)}\n• Unique values: {df[col].nunique()}\n• Sample: {df[col].head(3).tolist()}"
        
        # Handle UNIQUE/DISTINCT queries
        if any(word in question_lower for word in ["unique", "distinct", "different", "categories", "types"]):
            for col in columns:
                if col.lower() in question_lower:
                    unique_vals = df[col].unique()[:10]
                    return f"📊 **Unique values in '{col}'**:\n• Count: {len(df[col].unique())}\n• Samples: {', '.join(map(str, unique_vals))}"
            return f"📊 **Dataset Overview**:\n• Total columns: {len(columns)}\n• Total rows: {len(df)}\n• Columns: {', '.join(columns[:5])}"
        
        # Handle general column queries
        for col in columns:
            if col.lower() in question_lower:
                col_data = df[col]
                if col_data.dtype in ['int64', 'float64']:
                    return f"📊 **{col} Statistics**:\n• Max: {col_data.max()}\n• Min: {col_data.min()}\n• Mean: {col_data.mean():.2f}\n• Count: {len(col_data)}"
                else:
                    unique = col_data.nunique()
                    return f"📊 **{col} Information**:\n• Unique values: {unique}\n• Total records: {len(col_data)}\n• Samples: {col_data.head(3).tolist()}"
        
        return ""  # Return empty to fall back to LLM
        
    except Exception as e:
        # If data retrieval fails, return empty to fall back to LLM
        return ""


def _answer_from_context(question: str, state: AnalysisState) -> str:
    """Generate answer without LLM when credits exhausted"""
    profile = state.get("profile_result", {})
    insights = state.get("insights_result", [])
    
    question_lower = question.lower()
    
    # Simple pattern matching for common questions
    if "maximum" in question_lower or "max" in question_lower or "highest" in question_lower:
        stats = profile.get("statistics", {})
        return f"📊 **Maximum values** by column have been calculated.\n• Check the Profile tab for detailed statistics"
    
    if "minimum" in question_lower or "min" in question_lower or "lowest" in question_lower:
        return f"📊 **Minimum values** by column are available.\n• Check the Profile tab for detailed statistics"
    
    if "average" in question_lower or "mean" in question_lower:
        return f"📊 **Average values** have been calculated for numeric columns.\n• Check the Profile tab for detailed statistics"
    
    if "correlation" in question_lower or "relationship" in question_lower:
        insights_text = "\n".join([f"• {i.get('description', '')}" for i in insights[:3]])
        return f"🔗 **Key relationships found**:\n{insights_text}"
    
    # Default fallback
    return f"❓ **Analysis Summary**:\n" + "\n".join([f"• {i.get('title', 'Finding')}" for i in insights[:3]])
