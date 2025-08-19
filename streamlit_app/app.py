import os
import json
import requests
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

# Basic page config - no styling
st.set_page_config(
    page_title="Kudwa Financial Platform", 
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_data(ttl=30)
def fetch_ontology_data():
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/api/ontology/structure", timeout=5)
        return response.json() if response.ok else {}
    except:
        return {}

@st.cache_data(ttl=30)
def fetch_graph_data():
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/api/ontology/graph-data", timeout=5)
        return response.json() if response.ok else {}
    except:
        return {}

@st.cache_data(ttl=10)
def fetch_proposals():
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/api/proposals", timeout=5)
        if response.ok:
            data = response.json()
            # API returns {"proposals": [...]} so extract the list
            if isinstance(data, dict) and "proposals" in data:
                return data["proposals"]
            # Fallback to direct list
            return data if isinstance(data, list) else []
        return []
    except:
        return []

def create_network_graph(ontology_data):
    """Create a network graph using Plotly and NetworkX"""
    import plotly.graph_objects as go
    import networkx as nx
    import numpy as np

    entities = ontology_data.get("entities", [])
    relations = ontology_data.get("relations", [])
    instances = ontology_data.get("instances", [])

    if not entities:
        return None

    # Create NetworkX graph
    G = nx.Graph()

    # Add entity nodes
    entity_map = {}
    for entity in entities:
        entity_id = str(entity.get('id', entity.get('name', 'unknown')))
        entity_name = entity.get('name', 'Unknown')
        G.add_node(entity_id, label=entity_name, type='entity',
                  properties=entity.get('properties', {}))
        entity_map[entity_id] = entity_name

    # Add relation edges
    for relation in relations:
        source_id = str(relation.get('source_entity_id', ''))
        target_id = str(relation.get('target_entity_id', ''))
        rel_type = relation.get('rel_type', 'related_to')

        if source_id in entity_map and target_id in entity_map:
            G.add_edge(source_id, target_id, label=rel_type, type='relation')

    # Add instance nodes and connections
    for instance in instances:
        instance_id = f"instance_{instance.get('id', 'unknown')}"
        entity_id = str(instance.get('entity_id', ''))

        if entity_id in entity_map:
            G.add_node(instance_id, label="Instance", type='instance',
                      properties=instance.get('properties', {}))
            G.add_edge(instance_id, entity_id, label='instance_of', type='instance_relation')

    # Generate layout
    if len(G.nodes()) > 0:
        pos = nx.spring_layout(G, k=3, iterations=50)
    else:
        return None

    # Create edge traces
    edge_x = []
    edge_y = []
    edge_info = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

        edge_data = G.edges[edge]
        edge_info.append(f"{edge_data.get('label', 'connected')}")

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_info = []
    node_colors = []
    node_sizes = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        node_data = G.nodes[node]
        node_type = node_data.get('type', 'unknown')
        node_label = node_data.get('label', 'Unknown')

        node_text.append(node_label)

        # Color and size based on type
        if node_type == 'entity':
            node_colors.append('#0074D9')
            node_sizes.append(30)
        elif node_type == 'instance':
            node_colors.append('#2ECC40')
            node_sizes.append(20)
        else:
            node_colors.append('#888')
            node_sizes.append(15)

        # Create hover info
        properties = node_data.get('properties', {})
        if properties:
            prop_text = "<br>".join([f"{k}: {v}" for k, v in properties.items()])
            node_info.append(f"<b>{node_label}</b><br>Type: {node_type}<br>{prop_text}")
        else:
            node_info.append(f"<b>{node_label}</b><br>Type: {node_type}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition="middle center",
        hovertext=node_info,
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white')
        )
    )

    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                        title='Knowledge Graph - Interactive Network',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="Blue circles: Entities | Green circles: Instances | Lines: Relations",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002,
                            xanchor='left', yanchor='bottom',
                            font=dict(color="#888", size=10)
                        )],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        height=600
                    ))

    return fig

def main():
    # Simple title
    st.title("🏦 Kudwa Financial Platform")
    st.write("AI-powered ontology management for financial data")
    
    # Get data
    ontology_data = fetch_ontology_data()
    proposals = fetch_proposals()
    
    # Simple metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Handle both old format (arrays) and new format (counts)
        entities_count = ontology_data.get("entities", 0)
        if isinstance(entities_count, list):
            entities_count = len(entities_count)
        st.metric("Entities", entities_count)
    with col2:
        relations_count = ontology_data.get("relations", 0)
        if isinstance(relations_count, list):
            relations_count = len(relations_count)
        st.metric("Relations", relations_count)
    with col3:
        instances_count = ontology_data.get("instances", 0)
        if isinstance(instances_count, list):
            instances_count = len(instances_count)
        st.metric("Instances", instances_count)
    with col4:
        proposals_count = len(proposals) if isinstance(proposals, list) else 0
        st.metric("Pending", proposals_count)
    
    st.markdown("---")
    
    # Simple tabs
    tab1, tab2, tab3 = st.tabs(["Chat", "Graph", "Upload"])
    
    with tab1:
        st.header("Chat")
        
        # Chat input
        user_input = st.text_input("Ask about your data:")
        
        if st.button("Send") and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
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
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Display messages
        if st.session_state.messages:
            st.write("**Conversation:**")
            for msg in st.session_state.messages[-6:]:
                role = "You" if msg["role"] == "user" else "AI"
                st.write(f"**{role}:** {msg['content']}")
        else:
            st.info("Start a conversation!")
    
    with tab2:
        st.header("Knowledge Graph")

        # Fetch full graph data (not just counts)
        graph_data = fetch_graph_data()
        fig = create_network_graph(graph_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No entities available yet. Upload some files to build your knowledge graph!")

            # Show summary statistics using graph data (not counts)
            entities = graph_data.get("entities", [])
            relations = graph_data.get("relations", [])
            instances = graph_data.get("instances", [])

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Entities", len(entities))
                if entities:
                    with st.expander("Entity Details"):
                        for entity in entities:
                            st.write(f"**{entity.get('name', 'Unknown')}**")
                            if entity.get('properties'):
                                st.json(entity['properties'])

            with col2:
                st.metric("Relations", len(relations))
                if relations:
                    with st.expander("Relation Details"):
                        for relation in relations:
                            st.write(f"**{relation.get('rel_type', 'unknown')}**")

            with col3:
                st.metric("Instances", len(instances))
                if instances:
                    with st.expander("Instance Details"):
                        for instance in instances:
                            st.write("**Instance**")
                            if instance.get('properties'):
                                st.json(instance['properties'])
    
    with tab3:
        st.header("Upload Files")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['json', 'pdf', 'txt', 'csv']
        )
        
        if uploaded_files:
            st.write(f"Selected {len(uploaded_files)} files")
            
            extract_ontology = st.checkbox("Extract ontology", value=True)
            auto_approve = st.checkbox("Auto-approve changes", value=False)
            
            if st.button("Process Files"):
                progress = st.progress(0)
                
                for i, file in enumerate(uploaded_files):
                    st.write(f"Processing {file.name}...")
                    progress.progress((i + 1) / len(uploaded_files))

                    try:
                        files = {"file": (file.name, file.getvalue(), file.type)}
                        data = {
                            "extract_ontology": extract_ontology,
                            "auto_approve": auto_approve
                        }

                        with st.spinner(f"Uploading {file.name}..."):
                            response = requests.post(
                                f"{BACKEND_BASE_URL}/api/upload-json",
                                files=files,
                                data=data,
                                timeout=60  # Increased timeout
                            )

                        if response.ok:
                            result = response.json()
                            st.success(f"✅ {file.name}")

                            # Show detailed results
                            with st.expander(f"Details for {file.name}"):
                                st.json(result)
                        else:
                            error_detail = "Unknown error"
                            try:
                                error_data = response.json()
                                error_detail = error_data.get("detail", str(error_data))
                            except:
                                error_detail = response.text

                            st.error(f"❌ {file.name}: {error_detail}")

                    except Exception as e:
                        st.error(f"❌ {file.name}: {str(e)}")
                
                st.success("Processing complete!")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
        
        # Proposals
        proposals_list = proposals if isinstance(proposals, list) else []
        if proposals_list:
            st.write("**Pending Approvals:**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Approve All"):
                    for p in proposals_list:
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
            
            with col2:
                if st.button("Reject All"):
                    for p in proposals_list:
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
            
            # Show individual proposals
            proposals_list = proposals if isinstance(proposals, list) else []
            for i, proposal in enumerate(proposals_list[:3]):
                st.write(f"**Proposal {i+1}:**")
                st.json(proposal.get('payload', {}))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"app_{i}"):
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
                
                with col2:
                    if st.button("Reject", key=f"rej_{i}"):
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
        else:
            st.success("No pending approvals!")
    
    # Simple footer
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Refresh All Data"):
            st.cache_data.clear()
            st.rerun()

    with col2:
        if st.button("🗑️ Reset All Data", type="secondary"):
            if st.session_state.get("confirm_reset", False):
                with st.spinner("Resetting all data..."):
                    try:
                        response = requests.post(f"{BACKEND_BASE_URL}/api/reset-all-data", timeout=30)
                        if response.ok:
                            result = response.json()
                            st.success("✅ All data reset successfully!")
                            with st.expander("Reset Details"):
                                st.json(result)
                            st.cache_data.clear()
                            st.session_state.confirm_reset = False
                            st.rerun()
                        else:
                            st.error(f"❌ Reset failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Reset failed: {str(e)}")
                    st.session_state.confirm_reset = False
            else:
                st.session_state.confirm_reset = True
                st.warning("⚠️ Click again to confirm reset - this will delete ALL data!")

    st.caption("Kudwa Financial Platform v1.0")

if __name__ == "__main__":
    main()
