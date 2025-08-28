"""
Streamlit Demo App for Agno Integration
Demonstrates advanced financial reasoning and document processing capabilities
"""

import streamlit as st
import asyncio
import json
import sys
import os
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add project root to path
sys.path.append('.')

# Configure Streamlit page
st.set_page_config(
    page_title="Kudwa Finance - Agno Integration Demo",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .reasoning-step {
        background: #e3f2fd;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #2196f3;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠 Kudwa Finance - Agno Integration Demo</h1>
    <p>Advanced Financial AI with Reasoning Capabilities</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🎛️ Demo Controls")
st.sidebar.markdown("---")

demo_mode = st.sidebar.selectbox(
    "Choose Demo Mode",
    [
        "🏠 Overview",
        "🧠 Reasoning Engine",
        "📄 Document Analysis",
        "🔗 Bridge System",
        "📊 Performance Comparison",
        "🎨 Interface Creator"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 System Status")

# Check if Agno is available
try:
    import agno
    from agno.agent import Agent
    from agno.models.anthropic import Claude
    from agno.tools.reasoning import ReasoningTools
    agno_status = "✅ Available"
    agno_version = "v1.8.1"
except ImportError as e:
    agno_status = "❌ Not Available"
    agno_version = "N/A"

st.sidebar.markdown(f"**Agno Framework:** {agno_status}")
st.sidebar.markdown(f"**Version:** {agno_version}")

# Check API keys
openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

st.sidebar.markdown(f"**OpenAI API:** {'✅' if openai_key else '❌'}")
st.sidebar.markdown(f"**Anthropic API:** {'✅' if anthropic_key else '❌'}")

# Main content based on selected mode
if demo_mode == "🏠 Overview":
    st.header("🎯 Integration Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🧠 Advanced Reasoning</h3>
            <p>Step-by-step financial analysis using Agno's ReasoningTools</p>
            <ul>
                <li>Multi-step problem decomposition</li>
                <li>Confidence scoring</li>
                <li>Transparent reasoning process</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>📄 Document Processing</h3>
            <p>Intelligent document analysis with ontology extraction</p>
            <ul>
                <li>Multi-format support</li>
                <li>Ontology class suggestions</li>
                <li>Relationship mapping</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>🔗 Bridge System</h3>
            <p>Intelligent routing between Agno and CrewAI frameworks</p>
            <ul>
                <li>Automatic framework selection</li>
                <li>Performance comparison</li>
                <li>Fallback mechanisms</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <h3>🎨 Interface Creation</h3>
            <p>Dynamic UI generation based on requirements</p>
            <ul>
                <li>Responsive design</li>
                <li>Interactive components</li>
                <li>Real-time data integration</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Architecture diagram
    st.header("🏗️ System Architecture")
    
    # Create a simple architecture visualization
    architecture_data = {
        'Component': ['Frontend (Streamlit)', 'API Layer', 'Agno Framework', 'CrewAI Framework', 'Bridge System', 'Database'],
        'Type': ['Interface', 'API', 'AI Framework', 'AI Framework', 'Integration', 'Storage'],
        'Status': ['Active', 'Active', 'Active', 'Active', 'Active', 'Active'],
        'Performance': [95, 98, 92, 88, 94, 99]
    }
    
    df = pd.DataFrame(architecture_data)
    
    fig = px.bar(df, x='Component', y='Performance', color='Type',
                 title="System Component Performance",
                 color_discrete_sequence=px.colors.qualitative.Set3)
    
    st.plotly_chart(fig, use_container_width=True)

elif demo_mode == "🧠 Reasoning Engine":
    st.header("🧠 Agno Reasoning Engine Demo")
    
    st.markdown("""
    <div class="feature-card">
        <h3>💡 How it works</h3>
        <p>The Agno Reasoning Engine breaks down complex financial problems into logical steps, 
        providing transparent analysis with confidence scores.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample scenarios
    st.subheader("📋 Sample Financial Scenarios")
    
    scenario_options = {
        "Investment Analysis": """
        Company XYZ is considering three investment options:
        1. Expand to European market ($2M investment, 25% ROI potential)
        2. Develop new product line ($1.5M investment, 30% ROI potential)  
        3. Acquire competitor ($3M investment, 40% ROI potential)
        
        Current financials: $10M revenue, 15% margin, $2.5M cash available
        """,
        
        "Risk Assessment": """
        Evaluate the financial risks of launching a new fintech product:
        - Development cost: $500K
        - Marketing budget: $300K
        - Expected user acquisition: 10K users in 6 months
        - Revenue per user: $50/month
        - Market competition: High
        """,
        
        "Cash Flow Analysis": """
        Analyze cash flow impact of the following scenario:
        - Monthly revenue: $100K (growing 5% monthly)
        - Fixed costs: $60K/month
        - Variable costs: 30% of revenue
        - New equipment purchase: $200K (financed over 24 months)
        """
    }
    
    selected_scenario = st.selectbox("Choose a scenario:", list(scenario_options.keys()))
    
    st.text_area("Scenario Details:", scenario_options[selected_scenario], height=150, disabled=True)
    
    if st.button("🧠 Analyze with Reasoning", type="primary"):
        with st.spinner("Performing step-by-step analysis..."):
            # Simulate reasoning steps
            st.markdown("### 🔍 Reasoning Process")
            
            steps = [
                "**Step 1: Problem Decomposition** - Breaking down the scenario into key components",
                "**Step 2: Data Analysis** - Examining financial metrics and constraints", 
                "**Step 3: Risk Assessment** - Identifying potential risks and uncertainties",
                "**Step 4: Scenario Modeling** - Creating different outcome scenarios",
                "**Step 5: Recommendation** - Providing actionable insights with confidence scores"
            ]
            
            for i, step in enumerate(steps, 1):
                st.markdown(f"""
                <div class="reasoning-step">
                    {step}
                </div>
                """, unsafe_allow_html=True)
                
                # Simulate processing time
                import time
                time.sleep(0.5)
            
            # Mock results
            st.markdown("### 📊 Analysis Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Confidence Score", "87%", "↑ High")
            
            with col2:
                st.metric("Risk Level", "Medium", "⚠️")
            
            with col3:
                st.metric("Processing Time", "2.3s", "⚡ Fast")
            
            st.markdown("""
            <div class="success-message">
                <h4>💡 Recommendation</h4>
                <p>Based on the step-by-step analysis, the recommended approach is to proceed with 
                Option 2 (new product line) due to optimal risk-return ratio and available capital constraints.</p>
            </div>
            """, unsafe_allow_html=True)

elif demo_mode == "📄 Document Analysis":
    st.header("📄 Document Analysis with Agno")
    
    st.markdown("""
    <div class="feature-card">
        <h3>📋 Upload Financial Documents</h3>
        <p>Upload financial documents for intelligent analysis and ontology extraction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a financial document",
        type=['json', 'csv', 'txt', 'pdf'],
        help="Supported formats: JSON, CSV, TXT, PDF"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("File Size", f"{uploaded_file.size} bytes")
        
        with col2:
            st.metric("File Type", uploaded_file.type)
        
        with col3:
            st.metric("Status", "Ready for Analysis")
        
        if st.button("🔍 Analyze Document", type="primary"):
            with st.spinner("Analyzing document with Agno ontology specialist..."):
                # Simulate document analysis
                progress_bar = st.progress(0)
                
                analysis_steps = [
                    "Reading document content...",
                    "Extracting financial entities...",
                    "Identifying ontology classes...",
                    "Mapping relationships...",
                    "Generating confidence scores...",
                    "Creating recommendations..."
                ]
                
                for i, step in enumerate(analysis_steps):
                    st.text(step)
                    progress_bar.progress((i + 1) / len(analysis_steps))
                    time.sleep(0.8)
                
                st.success("✅ Analysis Complete!")
                
                # Mock analysis results
                st.subheader("📊 Analysis Results")
                
                # Extracted entities
                entities_data = {
                    'Entity': ['Revenue', 'Operating Expenses', 'Net Income', 'Assets', 'Liabilities'],
                    'Type': ['Income', 'Expense', 'Income', 'Asset', 'Liability'],
                    'Confidence': [95, 92, 88, 94, 91],
                    'Amount': ['$1,250,000', '$850,000', '$400,000', '$2,100,000', '$750,000']
                }
                
                entities_df = pd.DataFrame(entities_data)
                st.dataframe(entities_df, use_container_width=True)
                
                # Ontology suggestions
                st.subheader("🏗️ Ontology Suggestions")
                
                suggestions = [
                    "**FinancialStatement** - New class for quarterly reports",
                    "**RevenueStream** - Subclass for different income sources", 
                    "**OperationalExpense** - Category for operational costs",
                    "**hasAmount** - Property linking entities to monetary values",
                    "**belongsToQuarter** - Relationship to time periods"
                ]
                
                for suggestion in suggestions:
                    st.markdown(f"• {suggestion}")

elif demo_mode == "🔗 Bridge System":
    st.header("🔗 Agno-CrewAI Bridge System")
    
    st.markdown("""
    <div class="feature-card">
        <h3>🌉 Intelligent Framework Routing</h3>
        <p>The bridge system automatically selects the best framework (Agno or CrewAI) 
        based on the query type and requirements.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Query input
    query = st.text_area(
        "Enter your financial query:",
        placeholder="Example: Analyze the risk-return profile of investing in renewable energy stocks...",
        height=100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        framework_preference = st.selectbox(
            "Framework Preference:",
            ["Auto (Intelligent Routing)", "Force Agno", "Force CrewAI", "Hybrid (Both)"]
        )
    
    with col2:
        enable_reasoning = st.checkbox("Enable Detailed Reasoning", value=True)
    
    if st.button("🚀 Process Query", type="primary") and query:
        with st.spinner("Processing with bridge system..."):
            # Simulate framework selection
            st.subheader("🤖 Framework Selection Process")
            
            selection_logic = [
                "Analyzing query complexity...",
                "Checking for reasoning requirements...", 
                "Evaluating framework capabilities...",
                "Making routing decision..."
            ]
            
            for step in selection_logic:
                st.text(step)
                time.sleep(0.5)
            
            # Mock framework selection
            if "reasoning" in query.lower() or "analyze" in query.lower():
                selected_framework = "Agno (Reasoning Optimized)"
                framework_color = "🧠"
            else:
                selected_framework = "CrewAI (Workflow Optimized)"
                framework_color = "⚙️"
            
            st.success(f"✅ Selected Framework: {framework_color} {selected_framework}")
            
            # Performance comparison
            st.subheader("📊 Performance Comparison")
            
            comparison_data = {
                'Metric': ['Response Time', 'Reasoning Depth', 'Accuracy', 'Resource Usage'],
                'Agno': [2.3, 9.2, 8.8, 7.1],
                'CrewAI': [1.8, 6.5, 8.2, 5.9]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=comparison_df['Agno'],
                theta=comparison_df['Metric'],
                fill='toself',
                name='Agno',
                line_color='blue'
            ))
            fig.add_trace(go.Scatterpolar(
                r=comparison_df['CrewAI'],
                theta=comparison_df['Metric'],
                fill='toself',
                name='CrewAI',
                line_color='red'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="Framework Performance Comparison"
            )
            
            st.plotly_chart(fig, use_container_width=True)

elif demo_mode == "📊 Performance Comparison":
    st.header("📊 Performance Analytics")
    
    # Generate mock performance data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    performance_data = {
        'Date': dates,
        'Agno_Response_Time': np.random.normal(2.1, 0.3, len(dates)),
        'CrewAI_Response_Time': np.random.normal(1.9, 0.4, len(dates)),
        'Agno_Accuracy': np.random.normal(88, 5, len(dates)),
        'CrewAI_Accuracy': np.random.normal(85, 6, len(dates))
    }
    
    df = pd.DataFrame(performance_data)
    
    # Response time comparison
    st.subheader("⚡ Response Time Comparison")
    
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(
        x=df['Date'], 
        y=df['Agno_Response_Time'],
        mode='lines',
        name='Agno',
        line=dict(color='blue')
    ))
    fig_time.add_trace(go.Scatter(
        x=df['Date'], 
        y=df['CrewAI_Response_Time'],
        mode='lines',
        name='CrewAI',
        line=dict(color='red')
    ))
    
    fig_time.update_layout(
        title="Response Time Over Time",
        xaxis_title="Date",
        yaxis_title="Response Time (seconds)"
    )
    
    st.plotly_chart(fig_time, use_container_width=True)
    
    # Accuracy comparison
    st.subheader("🎯 Accuracy Comparison")
    
    fig_acc = go.Figure()
    fig_acc.add_trace(go.Scatter(
        x=df['Date'], 
        y=df['Agno_Accuracy'],
        mode='lines',
        name='Agno',
        line=dict(color='blue')
    ))
    fig_acc.add_trace(go.Scatter(
        x=df['Date'], 
        y=df['CrewAI_Accuracy'],
        mode='lines',
        name='CrewAI',
        line=dict(color='red')
    ))
    
    fig_acc.update_layout(
        title="Accuracy Over Time",
        xaxis_title="Date",
        yaxis_title="Accuracy (%)"
    )
    
    st.plotly_chart(fig_acc, use_container_width=True)

elif demo_mode == "🎨 Interface Creator":
    st.header("🎨 Dynamic Interface Creator")
    
    st.markdown("""
    <div class="feature-card">
        <h3>✨ AI-Powered Interface Generation</h3>
        <p>Describe what you want to build and Agno will generate the interface code for you.</p>
    </div>
    """, unsafe_allow_html=True)
    
    interface_request = st.text_area(
        "Describe the interface you want to create:",
        placeholder="""Example: Create a financial dashboard with:
- KPI cards showing revenue, expenses, and profit
- A line chart of monthly trends
- A table of recent transactions
- Interactive filters for date range""",
        height=120
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        interface_type = st.selectbox(
            "Interface Type:",
            ["Dashboard", "Form", "Chart", "Table", "KPI Cards", "Custom"]
        )
    
    with col2:
        framework = st.selectbox(
            "Framework:",
            ["Streamlit", "HTML/CSS/JS", "React", "Vue.js"]
        )
    
    if st.button("🎨 Generate Interface", type="primary") and interface_request:
        with st.spinner("Generating interface with Agno..."):
            # Simulate interface generation
            generation_steps = [
                "Analyzing requirements...",
                "Designing layout structure...",
                "Generating component code...",
                "Adding styling and interactions...",
                "Optimizing for responsiveness..."
            ]
            
            progress = st.progress(0)
            
            for i, step in enumerate(generation_steps):
                st.text(step)
                progress.progress((i + 1) / len(generation_steps))
                time.sleep(0.8)
            
            st.success("✅ Interface Generated!")
            
            # Show generated code (mock)
            st.subheader("📝 Generated Code")
            
            if framework == "Streamlit":
                code = '''
import streamlit as st
import plotly.express as px
import pandas as pd

# KPI Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Revenue", "$125K", "↑ 12%")
with col2:
    st.metric("Expenses", "$89K", "↓ 5%")
with col3:
    st.metric("Profit", "$36K", "↑ 28%")

# Chart
data = {"Month": ["Jan", "Feb", "Mar"], "Revenue": [100, 115, 125]}
fig = px.line(pd.DataFrame(data), x="Month", y="Revenue")
st.plotly_chart(fig)
'''
            else:
                code = '''
<div class="dashboard">
    <div class="kpi-cards">
        <div class="kpi-card">
            <h3>Revenue</h3>
            <span class="value">$125K</span>
            <span class="change positive">↑ 12%</span>
        </div>
        <!-- More KPI cards... -->
    </div>
    <div class="chart-container">
        <canvas id="revenueChart"></canvas>
    </div>
</div>
'''
            
            st.code(code, language='python' if framework == "Streamlit" else 'html')
            
            # Preview
            st.subheader("👀 Preview")
            
            if framework == "Streamlit":
                # Show actual Streamlit components as preview
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Revenue", "$125K", "↑ 12%")
                with col2:
                    st.metric("Expenses", "$89K", "↓ 5%")
                with col3:
                    st.metric("Profit", "$36K", "↑ 28%")
                
                # Sample chart
                sample_data = pd.DataFrame({
                    "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
                    "Revenue": [100, 115, 125, 140, 155]
                })
                fig = px.line(sample_data, x="Month", y="Revenue", title="Revenue Trend")
                st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🧠 <strong>Kudwa Finance - Agno Integration Demo</strong></p>
    <p>Powered by Agno Framework v1.8.1 | Advanced Financial AI with Reasoning</p>
</div>
""", unsafe_allow_html=True)

# Add numpy import for performance comparison
import numpy as np
