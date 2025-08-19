"""
Component Library - Reusable templates for dynamic interface components
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, List


class ComponentLibrary:
    """Library of reusable component templates"""
    
    @staticmethod
    def render_advanced_metric_card(component: Dict[str, Any], index: int):
        """Render an advanced metric card with trend indicators"""
        data = component.get("data", {})
        metric_value = data.get("value", "N/A")
        metric_label = data.get("label", "Metric")
        delta = data.get("delta", None)
        trend = data.get("trend", "neutral")  # up, down, neutral
        
        # Create a styled container
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.metric(
                    label=metric_label,
                    value=metric_value,
                    delta=delta
                )
            
            with col2:
                # Add trend indicator
                if trend == "up":
                    st.markdown("📈", help="Trending up")
                elif trend == "down":
                    st.markdown("📉", help="Trending down")
                else:
                    st.markdown("➡️", help="Stable")
    
    @staticmethod
    def render_interactive_chart(component: Dict[str, Any], index: int):
        """Render an interactive Plotly chart"""
        chart_data = component.get("data", {})
        chart_type = component.get("chart_type", "bar")
        title = component.get("title", "Chart")
        
        if not chart_data:
            st.warning("No data available for chart")
            return
        
        # Convert data to DataFrame
        if isinstance(chart_data, dict):
            # Handle different data formats
            if all(isinstance(v, (int, float)) for v in chart_data.values()):
                # Simple key-value pairs
                df = pd.DataFrame(list(chart_data.items()), columns=['Category', 'Value'])
            else:
                df = pd.DataFrame(chart_data)
        else:
            df = pd.DataFrame(chart_data)
        
        # Create Plotly figure based on chart type
        if chart_type == "bar":
            fig = px.bar(df, x=df.columns[0], y=df.columns[1], title=title)
        elif chart_type == "line":
            fig = px.line(df, x=df.columns[0], y=df.columns[1], title=title)
        elif chart_type == "pie":
            fig = px.pie(df, values=df.columns[1], names=df.columns[0], title=title)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=df.columns[0], y=df.columns[1], title=title)
        else:
            # Default to bar chart
            fig = px.bar(df, x=df.columns[0], y=df.columns[1], title=title)
        
        # Customize layout
        fig.update_layout(
            height=400,
            showlegend=True,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def render_data_table(component: Dict[str, Any], index: int):
        """Render an enhanced data table with filtering and sorting"""
        table_data = component.get("data", [])
        title = component.get("title", "Data Table")
        
        if not table_data:
            st.warning("No data available for table")
            return
        
        df = pd.DataFrame(table_data)
        
        # Add table controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Search functionality
            search_term = st.text_input(f"Search in {title}", key=f"search_{index}")
            if search_term:
                # Filter dataframe based on search term
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                df = df[mask]
        
        with col2:
            # Column selection
            if len(df.columns) > 1:
                selected_columns = st.multiselect(
                    "Select columns",
                    options=df.columns.tolist(),
                    default=df.columns.tolist()[:5],  # Show first 5 columns by default
                    key=f"columns_{index}"
                )
                if selected_columns:
                    df = df[selected_columns]
        
        with col3:
            # Row limit
            max_rows = st.number_input(
                "Max rows",
                min_value=10,
                max_value=1000,
                value=50,
                step=10,
                key=f"rows_{index}"
            )
            df = df.head(max_rows)
        
        # Display the table
        st.dataframe(df, use_container_width=True, height=400)
        
        # Show table stats
        st.caption(f"Showing {len(df)} rows × {len(df.columns)} columns")
    
    @staticmethod
    def render_kpi_grid(component: Dict[str, Any], index: int):
        """Render a grid of KPIs with enhanced styling"""
        kpis = component.get("data", {}).get("kpis", [])
        title = component.get("title", "KPI Dashboard")
        
        if not kpis:
            st.warning("No KPIs available")
            return
        
        st.subheader(title)
        
        # Calculate grid layout
        num_kpis = len(kpis)
        if num_kpis <= 3:
            cols = st.columns(num_kpis)
        elif num_kpis <= 6:
            cols = st.columns(3)
        else:
            cols = st.columns(4)
        
        # Display KPIs in grid
        for i, kpi in enumerate(kpis):
            col_index = i % len(cols)
            with cols[col_index]:
                # Create a styled metric card
                with st.container():
                    st.metric(
                        label=kpi.get("label", f"KPI {i+1}"),
                        value=kpi.get("value", "N/A"),
                        delta=kpi.get("delta", None)
                    )
                    
                    # Add description if available
                    if "description" in kpi:
                        st.caption(kpi["description"])
    
    @staticmethod
    def render_financial_summary(component: Dict[str, Any], index: int):
        """Render a financial summary component with multiple visualizations"""
        data = component.get("data", {})
        title = component.get("title", "Financial Summary")
        
        st.subheader(title)
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Overview", "Trends", "Details"])
        
        with tab1:
            # Overview metrics
            metrics = data.get("metrics", [])
            if metrics:
                cols = st.columns(len(metrics))
                for i, metric in enumerate(metrics):
                    with cols[i]:
                        st.metric(
                            label=metric.get("label", "Metric"),
                            value=metric.get("value", "N/A"),
                            delta=metric.get("delta", None)
                        )
        
        with tab2:
            # Trend chart
            trend_data = data.get("trend_data", {})
            if trend_data:
                df = pd.DataFrame(trend_data)
                if not df.empty:
                    fig = px.line(df, x=df.columns[0], y=df.columns[1], 
                                title="Trend Analysis")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No trend data available")
        
        with tab3:
            # Detailed breakdown
            detail_data = data.get("details", [])
            if detail_data:
                df = pd.DataFrame(detail_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No detailed data available")
    
    @staticmethod
    def get_component_templates() -> Dict[str, Dict[str, Any]]:
        """Get available component templates"""
        return {
            "metric_card": {
                "name": "Metric Card",
                "description": "Single KPI or metric display",
                "icon": "📊",
                "renderer": ComponentLibrary.render_advanced_metric_card
            },
            "chart": {
                "name": "Interactive Chart", 
                "description": "Bar, line, pie, or scatter charts",
                "icon": "📈",
                "renderer": ComponentLibrary.render_interactive_chart
            },
            "table": {
                "name": "Data Table",
                "description": "Searchable and sortable data table",
                "icon": "📋",
                "renderer": ComponentLibrary.render_data_table
            },
            "kpi_dashboard": {
                "name": "KPI Grid",
                "description": "Multiple metrics in grid layout",
                "icon": "🎯",
                "renderer": ComponentLibrary.render_kpi_grid
            },
            "financial_summary": {
                "name": "Financial Summary",
                "description": "Comprehensive financial overview",
                "icon": "💰",
                "renderer": ComponentLibrary.render_financial_summary
            }
        }
