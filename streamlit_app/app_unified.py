import os
import json
import requests
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

# Configure page
st.set_page_config(
    page_title="Kudwa POC - Financial Ontology Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for unified interface
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2d5aa0);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #e3f2fd;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    .section-card {
        background: #fff;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .approval-item {
        background: #f8f9fa;
        border-left: 4px solid #2d5aa0;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .user-message {
        background: #e3f2fd;
        border-left: 4px solid #2d5aa0;
    }
    .assistant-message {
        background: #f1f8e9;
        border-left: 4px solid #28a745;
    }
    .stButton > button {
        border-radius: 6px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .approve-btn {
        background-color: #28a745 !important;
        color: white !important;
    }
    .reject-btn {
        background-color: #dc3545 !important;
        color: white !important;
    }
    .bulk-btn {
        background-color: #007bff !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data(ttl=5)
def fetch_ontology_data():
    """Fetch current ontology structure from backend"""
    try:
        r = requests.get(f"{BACKEND_BASE_URL}/api/ontology/structure")
        if r.ok:
            return r.json()
    except:
        pass
    return {"entities": [], "relations": [], "instances": []}

@st.cache_data(ttl=2)
def fetch_proposals():
    """Fetch pending proposals"""
    try:
        r = requests.get(f"{BACKEND_BASE_URL}/api/proposals")
        if r.ok:
            return r.json().get("proposals", [])
    except:
        pass
    return []

def create_network_graph(ontology_data):
    """Create a simple network graph using plotly"""
    entities = ontology_data.get("entities", [])
    relations = ontology_data.get("relations", [])
    instances = ontology_data.get("instances", [])
    
    if not entities and not relations:
        return None
    
    # Create nodes and edges for plotly graph
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    # Simple circular layout
    import math
    total_nodes = len(entities) + len(instances)
    
    for i, entity in enumerate(entities):
        angle = 2 * math.pi * i / max(total_nodes, 1)
        node_x.append(math.cos(angle))
        node_y.append(math.sin(angle))
        node_text.append(f"Entity: {entity['name']}")
        node_color.append('#2d5aa0')
    
    for i, instance in enumerate(instances):
        angle = 2 * math.pi * (i + len(entities)) / max(total_nodes, 1)
        node_x.append(0.5 * math.cos(angle))
        node_y.append(0.5 * math.sin(angle))
        node_text.append(f"Instance: {instance['name'][:20]}...")
        node_color.append('#ffc107')
    
    # Create edges
    edge_x = []
    edge_y = []
    
    for relation in relations:
        # Simple connection lines (would need proper node mapping in real implementation)
        if len(node_x) >= 2:
            edge_x.extend([node_x[0], node_x[1], None])
            edge_y.extend([node_y[0], node_y[1], None])
    
    # Create plotly figure
    fig = go.Figure()
    
    # Add edges
    if edge_x:
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#666'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="middle center",
        marker=dict(
            size=20,
            color=node_color,
            line=dict(width=2, color='white')
        ),
        showlegend=False
    ))
    
    fig.update_layout(
        title="Ontology Network Graph",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        annotations=[ dict(
            text="Interactive ontology visualization",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.005, y=-0.002,
            xanchor='left', yanchor='bottom',
            font=dict(color='#666', size=12)
        )],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400
    )
    
    return fig

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Main header
st.markdown("""
<div class="main-header">
    <h1>🏦 Kudwa POC</h1>
    <p>Financial Ontology Platform - Real-time document processing & intelligent chat</p>
</div>
""", unsafe_allow_html=True)

# Get current data
ontology_data = fetch_ontology_data()
proposals = fetch_proposals()

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <h3>{len(ontology_data.get("entities", []))}</h3>
        <p>Entities</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <h3>{len(ontology_data.get("relations", []))}</h3>
        <p>Relations</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <h3>{len(ontology_data.get("instances", []))}</h3>
        <p>Instances</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-box">
        <h3>{len(proposals)}</h3>
        <p>Pending Approvals</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area with three columns
left_col, center_col, right_col = st.columns([1, 1, 1])

# LEFT COLUMN - CHAT INTERFACE
with left_col:
    st.markdown("""
    <div class="section-card">
        <h3>💬 Intelligent Assistant</h3>
    </div>
    """, unsafe_allow_html=True)

    # Quick action buttons
    st.markdown("**Quick Actions:**")
    quick_col1, quick_col2 = st.columns(2)

    with quick_col1:
        if st.button("📊 Summarize", key="quick_summary"):
            msg = "Please provide a summary of the current ontology structure"
            st.session_state.chat_history.append({"role": "user", "content": msg})

    with quick_col2:
        if st.button("🔍 Find entities", key="quick_entities"):
            msg = "What entities are currently in the ontology?"
            st.session_state.chat_history.append({"role": "user", "content": msg})

    # Chat input
    msg = st.text_input("💭 Ask about your ontology...", placeholder="e.g., 'What financial entities do we have?'", key="chat_input")

    if st.button("🚀 Send", key="send_chat") and msg:
        st.session_state.chat_history.append({"role": "user", "content": msg})

        with st.spinner("🤔 Thinking..."):
            try:
                r = requests.post(f"{BACKEND_BASE_URL}/api/chat", json={"message": msg})
                if r.ok:
                    data = r.json()
                    response = data.get("text", "I couldn't process that request.")
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                else:
                    st.session_state.chat_history.append({"role": "assistant", "content": "Sorry, I encountered an error."})
            except:
                st.session_state.chat_history.append({"role": "assistant", "content": "Connection error. Please try again."})
        st.rerun()

    # Display recent chat messages (last 4)
    if st.session_state.chat_history:
        st.markdown("**Recent Conversation:**")
        recent_messages = st.session_state.chat_history[-4:]
        for message in recent_messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>🤖 Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

# CENTER COLUMN - UPLOAD & GRAPH
with center_col:
    st.markdown("""
    <div class="section-card">
        <h3>📤 Document Upload</h3>
    </div>
    """, unsafe_allow_html=True)

    # Upload interface
    uploaded = st.file_uploader(
        "Choose files to process",
        type=["json", "pdf", "txt", "csv", "xlsx"],
        accept_multiple_files=True,
        help="Upload documents to extract ontology data",
        key="file_uploader"
    )

    upload_col1, upload_col2 = st.columns(2)
    with upload_col1:
        extract_ontology = st.checkbox("Extract ontology", value=True, key="extract_ontology")
    with upload_col2:
        auto_approve = st.checkbox("Auto-approve", value=False, key="auto_approve")

    if uploaded and st.button("🚀 Process Files", key="process_files"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, file in enumerate(uploaded):
            status_text.text(f"Processing {file.name}...")
            progress_bar.progress((i + 1) / len(uploaded))

            try:
                files = {"file": (file.name, file.getvalue(), file.type)}
                data = {
                    "extract_ontology": extract_ontology,
                    "auto_approve": auto_approve
                }

                r = requests.post(f"{BACKEND_BASE_URL}/api/upload-json", files=files, data=data)

                if r.ok:
                    st.success(f"✅ {file.name}")
                else:
                    st.error(f"❌ {file.name}: {r.text}")
            except Exception as e:
                st.error(f"❌ {file.name}: {str(e)}")

        status_text.text("✅ Processing complete!")
        st.cache_data.clear()
        time.sleep(1)
        st.rerun()

    # Ontology Graph
    st.markdown("""
    <div class="section-card">
        <h3>🕸️ Ontology Graph</h3>
    </div>
    """, unsafe_allow_html=True)

    # Create and display graph
    fig = create_network_graph(ontology_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Upload documents to see the ontology graph!")

    # Graph statistics
    if ontology_data.get("entities") or ontology_data.get("relations"):
        stats_col1, stats_col2 = st.columns(2)
        with stats_col1:
            st.metric("Nodes", len(ontology_data.get("entities", [])) + len(ontology_data.get("instances", [])))
        with stats_col2:
            st.metric("Connections", len(ontology_data.get("relations", [])))

# RIGHT COLUMN - APPROVALS
with right_col:
    st.markdown("""
    <div class="section-card">
        <h3>✅ Pending Approvals</h3>
    </div>
    """, unsafe_allow_html=True)

    if not proposals:
        st.success("🎉 No pending approvals!")
    else:
        # Bulk actions
        st.markdown("**Bulk Actions:**")
        bulk_col1, bulk_col2 = st.columns(2)

        with bulk_col1:
            if st.button("✅ Approve All", key="approve_all", help="Approve all pending proposals"):
                for p in proposals:
                    try:
                        requests.post(f"{BACKEND_BASE_URL}/api/proposals/approve",
                                    json={"proposal_id": p["id"], "action": "approve"})
                    except:
                        pass
                st.success(f"Approved {len(proposals)} proposals!")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()

        with bulk_col2:
            if st.button("❌ Reject All", key="reject_all", help="Reject all pending proposals"):
                for p in proposals:
                    try:
                        requests.post(f"{BACKEND_BASE_URL}/api/proposals/approve",
                                    json={"proposal_id": p["id"], "action": "reject"})
                    except:
                        pass
                st.success(f"Rejected {len(proposals)} proposals!")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()

        st.markdown("---")

        # Individual proposals
        st.markdown(f"**{len(proposals)} Proposals:**")

        for i, p in enumerate(proposals[:5]):  # Show first 5
            proposal_type = p.get('type', 'Unknown')
            proposal_id = p.get('id', 'Unknown')

            st.markdown(f"""
            <div class="approval-item">
                <strong>{proposal_type}</strong> :: {proposal_id[:8]}...
            </div>
            """, unsafe_allow_html=True)

            # Show payload summary
            payload = p.get("payload", {})
            if proposal_type == "relation":
                st.write(f"🔗 `{payload.get('source', 'Unknown')}` → `{payload.get('target', 'Unknown')}`")
            elif proposal_type == "instance":
                st.write(f"📄 File: `{payload.get('source_file_id', 'Unknown')}`")

            # Action buttons
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                if st.button("✅", key=f"approve_{i}", help="Approve"):
                    try:
                        requests.post(f"{BACKEND_BASE_URL}/api/proposals/approve",
                                    json={"proposal_id": p["id"], "action": "approve"})
                        st.success("Approved!")
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Failed to approve")

            with action_col2:
                if st.button("❌", key=f"reject_{i}", help="Reject"):
                    try:
                        requests.post(f"{BACKEND_BASE_URL}/api/proposals/approve",
                                    json={"proposal_id": p["id"], "action": "reject"})
                        st.success("Rejected!")
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("Failed to reject")

            st.markdown("---")

        if len(proposals) > 5:
            st.info(f"... and {len(proposals) - 5} more proposals")

# Auto-refresh
if st.checkbox("🔄 Auto-refresh (5s)", value=False, key="auto_refresh"):
    time.sleep(5)
    st.cache_data.clear()
    st.rerun()

# Manual refresh
if st.button("🔄 Refresh Data", key="manual_refresh"):
    st.cache_data.clear()
    st.rerun()
