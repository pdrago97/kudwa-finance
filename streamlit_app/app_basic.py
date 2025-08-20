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
        response = requests.get(f"{BACKEND_BASE_URL}/api/ontology", timeout=5)
        return response.json() if response.ok else {}
    except:
        return {}

@st.cache_data(ttl=10)
def fetch_proposals():
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/api/proposals", timeout=5)
        return response.json() if response.ok else []
    except:
        return []

def create_simple_graph(ontology_data):
    entities = ontology_data.get("entities", [])
    relations = ontology_data.get("relations", [])
    
    if not entities:
        return None
    
    # Simple scatter plot
    fig = go.Figure()
    
    # Add nodes
    for i, entity in enumerate(entities):
        fig.add_trace(go.Scatter(
            x=[i % 5], 
            y=[i // 5],
            mode='markers+text',
            text=[entity.get('name', 'Unknown')],
            textposition="middle center",
            marker=dict(size=20, color='blue'),
            name=entity.get('type', 'Entity')
        ))
    
    fig.update_layout(
        title="Knowledge Graph",
        showlegend=False,
        height=400
    )
    
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
        st.metric("Entities", len(ontology_data.get("entities", [])))
    with col2:
        st.metric("Relations", len(ontology_data.get("relations", [])))
    with col3:
        st.metric("Instances", len(ontology_data.get("instances", [])))
    with col4:
        st.metric("Pending", len(proposals))
    
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
        
        fig = create_simple_graph(ontology_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data to visualize yet.")
    
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
                
                st.success("Processing complete!")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
        
        # Proposals
        if proposals:
            st.write("**Pending Approvals:**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Approve All"):
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
            
            with col2:
                if st.button("Reject All"):
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
            
            # Show individual proposals
            for i, proposal in enumerate(proposals[:3]):
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
    if st.button("Refresh All Data"):
        st.cache_data.clear()
        st.rerun()

if __name__ == "__main__":
    main()
