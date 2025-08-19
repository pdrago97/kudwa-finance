import os
import json
import requests
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time
import math
import random

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

# Configure page
st.set_page_config(
    page_title="Kudwa Financial Platform", 
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🏦"
)

# Clean, minimal CSS
st.markdown("""
<style>
    .stApp {
        background: #f8fafc;
    }
    
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1400px;
    }
    
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .header-container p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        background: #f1f5f9;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #e2e8f0;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# Data functions
@st.cache_data(ttl=5)
def fetch_ontology_data():
    try:
        r = requests.get(f"{BACKEND_BASE_URL}/api/ontology", timeout=5)
        if r.ok:
            return r.json()
    except:
        pass
    return {"entities": [], "relations": [], "instances": []}

@st.cache_data(ttl=2)
def fetch_proposals():
    try:
        r = requests.get(f"{BACKEND_BASE_URL}/api/proposals", timeout=5)
        if r.ok:
            return r.json().get("proposals", [])
    except:
        pass
    return []

def create_knowledge_graph(data, node_size=25, edge_width=2, show_labels=True):
    entities = data.get("entities", [])
    relations = data.get("relations", [])
    instances = data.get("instances", [])
    
    if not entities and not instances:
        return None
    
    # Node positioning
    node_x, node_y, node_text, node_color, node_hover = [], [], [], [], []
    
    # Color mapping
    colors = {
        'Payment': '#ff6b6b', 'Contract': '#4ecdc4', 'Person': '#45b7d1',
        'Organization': '#96ceb4', 'Account': '#feca57', 'default': '#a55eea'
    }
    
    # Add entities
    for i, entity in enumerate(entities):
        angle = 2 * math.pi * i / max(len(entities), 1)
        radius = 2.0
        
        node_x.append(radius * math.cos(angle))
        node_y.append(radius * math.sin(angle))
        
        name = entity.get('name', 'Unnamed')
        entity_type = entity.get('type', 'Unknown')
        
        node_text.append(name if show_labels else "")
        node_color.append(colors.get(entity_type, colors['default']))
        node_hover.append(f"<b>{name}</b><br>Type: {entity_type}")
    
    # Add instances
    for i, instance in enumerate(instances):
        angle = 2 * math.pi * i / max(len(instances), 1)
        radius = 1.0
        
        node_x.append(radius * math.cos(angle))
        node_y.append(radius * math.sin(angle))
        
        name = instance.get('name', 'Unnamed')[:20]
        node_text.append(name if show_labels else "")
        node_color.append('#9b59b6')
        node_hover.append(f"<b>{name}</b><br>Type: Instance")
    
    # Create edges
    edge_x, edge_y = [], []
    entity_map = {e.get('id'): i for i, e in enumerate(entities)}
    
    for relation in relations:
        src, tgt = relation.get('source'), relation.get('target')
        if src in entity_map and tgt in entity_map:
            src_idx, tgt_idx = entity_map[src], entity_map[tgt]
            if src_idx < len(node_x) and tgt_idx < len(node_x):
                edge_x.extend([node_x[src_idx], node_x[tgt_idx], None])
                edge_y.extend([node_y[src_idx], node_y[tgt_idx], None])
    
    # Create figure
    fig = go.Figure()
    
    # Add edges
    if edge_x:
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=edge_width, color='rgba(100,100,100,0.5)'),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text' if show_labels else 'markers',
        text=node_text,
        hovertext=node_hover,
        hoverinfo='text',
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        showlegend=False
    ))
    
    fig.update_layout(
        title="Knowledge Graph",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=20, r=20, t=40),
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )
    
    return fig

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main app
def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <h1>🏦 Kudwa Financial Platform</h1>
        <p>AI-powered ontology management for financial data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data
    ontology_data = fetch_ontology_data()
    proposals = fetch_proposals()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(ontology_data.get("entities", []))}</h2>
            <p>Entities</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(ontology_data.get("relations", []))}</h2>
            <p>Relations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(ontology_data.get("instances", []))}</h2>
            <p>Instances</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(proposals)}</h2>
            <p>Pending</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Main tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "🕸️ Graph", "📁 Upload"])

    with tab1:
        st.subheader("AI Assistant")

        # Chat input
        user_input = st.text_input(
            "Ask about your data:",
            placeholder="e.g., 'What entities do we have?' or 'Show me the relationships'"
        )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Send", type="primary") and user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})

                with st.spinner("Processing..."):
                    try:
                        response = requests.post(
                            f"{BACKEND_BASE_URL}/api/chat",
                            json={"message": user_input},
                            timeout=10
                        )
                        if response.ok:
                            ai_response = response.json().get("text", "No response")
                        else:
                            ai_response = "Sorry, I couldn't process that request."
                    except:
                        ai_response = "Connection error. Please check the backend."

                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.rerun()

        with col2:
            if st.button("Clear Chat"):
                st.session_state.messages = []
                st.rerun()

        # Display messages
        if st.session_state.messages:
            st.markdown("---")
            for msg in st.session_state.messages[-6:]:  # Show last 6 messages
                role = "You" if msg["role"] == "user" else "AI"
                st.markdown(f"""
                <div class="chat-message">
                    <strong>{role}:</strong> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("👋 Start a conversation! Ask about entities, relationships, or upload documents.")

    with tab2:
        st.subheader("Knowledge Graph")

        # Graph controls
        col1, col2 = st.columns([3, 1])

        with col2:
            st.markdown("**Settings**")
            node_size = st.slider("Node Size", 15, 50, 25)
            show_labels = st.checkbox("Show Labels", True)

            if st.button("🔄 Refresh"):
                st.cache_data.clear()
                st.rerun()

        with col1:
            fig = create_knowledge_graph(ontology_data, node_size=node_size, show_labels=show_labels)

            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📊 No data to visualize yet. Upload some documents to get started!")

                # Show example structure
                st.markdown("""
                **Expected Graph Elements:**
                - 🔴 Payment entities
                - 🟢 Contract entities
                - 🔵 Person entities
                - 🟡 Organization entities
                - 🟣 Instance data
                """)

    with tab3:
        st.subheader("Document Upload")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Upload Files**")

            uploaded_files = st.file_uploader(
                "Choose files",
                accept_multiple_files=True,
                type=['json', 'pdf', 'txt', 'csv'],
                help="Upload documents to extract entities and relationships"
            )

            if uploaded_files:
                st.success(f"📁 {len(uploaded_files)} file(s) selected")

                # Options
                extract_ontology = st.checkbox("Extract ontology", value=True)
                auto_approve = st.checkbox("Auto-approve changes", value=False)

                if st.button("🚀 Process Files", type="primary"):
                    progress = st.progress(0)
                    status = st.empty()

                    for i, file in enumerate(uploaded_files):
                        status.text(f"Processing {file.name}...")
                        progress.progress((i + 1) / len(uploaded_files))

                        try:
                            files = {"file": (file.name, file.getvalue(), file.type)}
                            data = {
                                "extract_ontology": extract_ontology,
                                "auto_approve": auto_approve
                            }

                            response = requests.post(
                                f"{BACKEND_BASE_URL}/api/upload-json",
                                files=files,
                                data=data,
                                timeout=30
                            )

                            if response.ok:
                                st.success(f"✅ {file.name}")
                            else:
                                st.error(f"❌ {file.name}: Failed")
                        except Exception as e:
                            st.error(f"❌ {file.name}: {str(e)}")

                    status.text("✅ Processing complete!")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()

        with col2:
            st.markdown("**Pending Approvals**")

            if not proposals:
                st.success("🎉 No pending approvals!")
            else:
                # Bulk actions
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✅ Approve All"):
                        for p in proposals:
                            try:
                                requests.post(
                                    f"{BACKEND_BASE_URL}/api/proposals/approve",
                                    json={"proposal_id": p["id"], "action": "approve"},
                                    timeout=5
                                )
                            except:
                                pass
                        st.success("All approved!")
                        st.cache_data.clear()
                        st.rerun()

                with col_b:
                    if st.button("❌ Reject All"):
                        for p in proposals:
                            try:
                                requests.post(
                                    f"{BACKEND_BASE_URL}/api/proposals/approve",
                                    json={"proposal_id": p["id"], "action": "reject"},
                                    timeout=5
                                )
                            except:
                                pass
                        st.success("All rejected!")
                        st.cache_data.clear()
                        st.rerun()

                st.markdown("---")

                # Individual proposals
                for i, proposal in enumerate(proposals[:3]):
                    with st.expander(f"Proposal {i+1}: {proposal.get('type', 'Unknown')}"):
                        st.json(proposal.get('payload', {}))

                        col_x, col_y = st.columns(2)
                        with col_x:
                            if st.button("✅ Approve", key=f"app_{i}"):
                                try:
                                    requests.post(
                                        f"{BACKEND_BASE_URL}/api/proposals/approve",
                                        json={"proposal_id": proposal["id"], "action": "approve"},
                                        timeout=5
                                    )
                                    st.success("Approved!")
                                    st.cache_data.clear()
                                    st.rerun()
                                except:
                                    st.error("Failed")

                        with col_y:
                            if st.button("❌ Reject", key=f"rej_{i}"):
                                try:
                                    requests.post(
                                        f"{BACKEND_BASE_URL}/api/proposals/approve",
                                        json={"proposal_id": proposal["id"], "action": "reject"},
                                        timeout=5
                                    )
                                    st.success("Rejected!")
                                    st.cache_data.clear()
                                    st.rerun()
                                except:
                                    st.error("Failed")

                if len(proposals) > 3:
                    st.info(f"... and {len(proposals) - 3} more proposals")

    # Footer
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh All Data"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        st.caption("Kudwa Financial Ontology Platform v1.0")

if __name__ == "__main__":
    main()
