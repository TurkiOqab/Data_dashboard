"""
Visualizer Component

Handles data visualization and chart regeneration.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any, Optional
import re


def render_slide_viewer(slide_data: Dict[str, Any]):
    """
    Render a detailed view of a single slide.

    Args:
        slide_data: Slide data dictionary
    """
    st.markdown(f"### Slide {slide_data.get('slide_number', '?')}")

    # Title
    title = slide_data.get('title', '')
    if title:
        st.markdown(f"## {title}")

    # Text content
    text_content = slide_data.get('text_content', [])
    if text_content:
        for text in text_content:
            st.markdown(text)

    # Tables
    tables = slide_data.get('tables', [])
    for i, table in enumerate(tables):
        st.markdown(f"**Table {i + 1}:**")
        render_table(table)

    # Indicators
    render_content_indicators(slide_data)


def render_table(table_data: Dict[str, Any]):
    """Render a table with optional interactive features."""
    rows = table_data.get('rows', [])
    headers = table_data.get('headers', [])

    if not rows:
        st.info("Empty table")
        return

    # Use headers or first row as columns
    if headers:
        columns = headers
        data_rows = rows
    else:
        columns = rows[0] if rows else []
        data_rows = rows[1:] if len(rows) > 1 else []

    if not columns:
        return

    # Create DataFrame
    try:
        df = pd.DataFrame(data_rows, columns=columns[:len(data_rows[0])] if data_rows else columns)
        st.dataframe(df, use_container_width=True)

        # Offer visualization if numeric data exists
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            if st.checkbox(f"Visualize table data", key=f"viz_{hash(str(rows))}"):
                render_table_chart(df)

    except Exception as e:
        # Fallback to markdown table
        st.markdown(format_table_markdown(table_data))


def render_table_chart(df: pd.DataFrame):
    """Generate a chart from table data."""
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    if not numeric_cols:
        st.info("No numeric data to visualize")
        return

    col1, col2 = st.columns(2)

    with col1:
        chart_type = st.selectbox(
            "Chart Type",
            ["Bar", "Line", "Area", "Pie"],
            key=f"chart_type_{id(df)}"
        )

    with col2:
        y_col = st.selectbox(
            "Value Column",
            numeric_cols,
            key=f"y_col_{id(df)}"
        )

    # Determine x-axis
    x_col = categorical_cols[0] if categorical_cols else df.index.name or "Index"

    # Create chart
    if chart_type == "Bar":
        if categorical_cols:
            fig = px.bar(df, x=categorical_cols[0], y=y_col)
        else:
            fig = px.bar(df, y=y_col)
    elif chart_type == "Line":
        if categorical_cols:
            fig = px.line(df, x=categorical_cols[0], y=y_col, markers=True)
        else:
            fig = px.line(df, y=y_col, markers=True)
    elif chart_type == "Area":
        if categorical_cols:
            fig = px.area(df, x=categorical_cols[0], y=y_col)
        else:
            fig = px.area(df, y=y_col)
    elif chart_type == "Pie":
        if categorical_cols:
            fig = px.pie(df, names=categorical_cols[0], values=y_col)
        else:
            fig = px.pie(df, values=y_col)

    st.plotly_chart(fig, use_container_width=True)


def format_table_markdown(table_data: Dict[str, Any]) -> str:
    """Convert table data to markdown format."""
    rows = table_data.get('rows', [])
    if not rows:
        return "*Empty table*"

    lines = []

    # Header
    lines.append("| " + " | ".join(str(cell) for cell in rows[0]) + " |")
    lines.append("| " + " | ".join(["---"] * len(rows[0])) + " |")

    # Data rows
    for row in rows[1:]:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

    return "\n".join(lines)


def render_content_indicators(slide_data: Dict[str, Any]):
    """Render indicators for special content types."""
    indicators = []

    if slide_data.get('has_chart'):
        indicators.append(("chart", "Contains Chart/Graph"))

    if slide_data.get('has_image'):
        indicators.append(("image", "Contains Image"))

    if slide_data.get('raw_notes'):
        indicators.append(("notes", "Has Speaker Notes"))

    if indicators:
        cols = st.columns(len(indicators))
        for col, (icon, label) in zip(cols, indicators):
            with col:
                st.info(label)


def render_data_visualization(data: Dict[str, Any], chart_type: str = "auto"):
    """
    Render a visualization from extracted data.

    Args:
        data: Extracted data with 'labels', 'values', 'series' etc.
        chart_type: Type of chart to render ('auto', 'bar', 'line', 'pie', 'scatter')
    """
    if 'error' in data:
        st.error(data['error'])
        return

    # Auto-detect chart type based on data structure
    if chart_type == "auto":
        if 'series' in data and len(data.get('series', [])) > 1:
            chart_type = "line"
        elif len(data.get('values', [])) <= 6:
            chart_type = "pie"
        else:
            chart_type = "bar"

    labels = data.get('labels', [])
    values = data.get('values', [])
    series = data.get('series', [{'name': 'Values', 'data': values}])
    title = data.get('title', '')

    if chart_type == "bar":
        fig = go.Figure()
        for s in series:
            fig.add_trace(go.Bar(
                x=labels,
                y=s.get('data', values),
                name=s.get('name', '')
            ))
        fig.update_layout(title=title, barmode='group')

    elif chart_type == "line":
        fig = go.Figure()
        for s in series:
            fig.add_trace(go.Scatter(
                x=labels,
                y=s.get('data', values),
                name=s.get('name', ''),
                mode='lines+markers'
            ))
        fig.update_layout(title=title)

    elif chart_type == "pie":
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values
        )])
        fig.update_layout(title=title)

    elif chart_type == "scatter":
        fig = px.scatter(
            x=labels,
            y=values,
            title=title
        )

    else:
        st.warning(f"Unknown chart type: {chart_type}")
        return

    st.plotly_chart(fig, use_container_width=True)


def parse_chart_data_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Attempt to parse chart data from extracted text.

    This is a basic parser - in production, you'd use
    more sophisticated NLP or the vision model output.
    """
    data = {
        'labels': [],
        'values': [],
        'title': ''
    }

    # Look for patterns like "Category: Value" or "Category - Value"
    patterns = [
        r'([A-Za-z\s]+):\s*(\d+(?:\.\d+)?)',
        r'([A-Za-z\s]+)\s*-\s*(\d+(?:\.\d+)?)',
        r'([A-Za-z\s]+)\s+(\d+(?:\.\d+)?%?)'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            for label, value in matches:
                data['labels'].append(label.strip())
                # Remove % if present
                value = value.replace('%', '')
                try:
                    data['values'].append(float(value))
                except ValueError:
                    pass

    if data['labels'] and data['values']:
        return data

    return None
