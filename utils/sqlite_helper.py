"""SQLite helper utilities for on-the-fly database creation and queries."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Tuple, List

import pandas as pd


def create_sqlite_db(df: pd.DataFrame, db_path: str, table_name: str = "data") -> Tuple[bool, Optional[str]]:
    """
    Create a SQLite database from a DataFrame.
    Adds derived columns for detected date fields to improve queryability.
    """
    try:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        df_copy = df.copy()
        # Detect likely date columns and add day_name/day_of_week
        for col in df_copy.columns:
            try:
                parsed = pd.to_datetime(df_copy[col], errors="coerce", format="mixed")
                valid_ratio = parsed.notna().mean()
                name_hint = any(k in str(col).lower() for k in ["date", "time", "day"])
                if valid_ratio >= 0.6 or (name_hint and valid_ratio >= 0.2):
                    # Add standardized date and derived fields
                    df_copy[f"{col}_date"] = parsed.dt.strftime("%Y-%m-%d")
                    df_copy[f"{col}_day_name"] = parsed.dt.day_name()
                    df_copy[f"{col}_day_of_week"] = parsed.dt.dayofweek  # Monday=0
            except Exception:
                continue

        with sqlite3.connect(db_path) as conn:
            df_copy.to_sql(table_name, conn, if_exists="replace", index=False)
        return True, None
    except Exception as e:
        return False, f"Error creating SQLite database: {str(e)}"


def get_schema_info(db_path: str, table_name: str = "data") -> str:
    """
    Return schema info string for prompt usage.
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

    if not columns:
        return "No schema available."

    cols = [f"{col[1]} ({col[2]})" for col in columns]
    return f"Table: {table_name}\nColumns: " + ", ".join(cols)


def run_sql_query(db_path: str, query: str, max_rows: int = 50) -> Tuple[List[str], List[tuple]]:
    """
    Execute a read-only SQL query with safety checks.
    Returns column names and rows.
    """
    safe_query = _sanitize_query(query)
    if "limit" not in safe_query.lower():
        safe_query = safe_query.rstrip(";") + f" LIMIT {max_rows}"

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(safe_query)
        cols = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

    return cols, rows


def _sanitize_query(query: str) -> str:
    """Allow only SELECT/WITH queries and strip unsafe statements."""
    q = query.strip()
    if not q:
        raise ValueError("Empty SQL query")

    lowered = q.lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise ValueError("Only SELECT queries are allowed")

    # Prevent multiple statements
    if ";" in q[:-1]:
        raise ValueError("Multiple statements are not allowed")

    return q
