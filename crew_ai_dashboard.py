"""
CrewAI-powered dashboard for Kudwa financial data processing
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import requests
import json
import asyncio
import aiohttp
from datetime import datetime
import structlog
import networkx as nx
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Kudwa CrewAI Dashboard"

# API base URL
API_BASE = "http://localhost:8000/api/v1"

# Initialize Supabase client for direct data access
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

def create_ontology_graph():
    """Create ontology graph from Supabase data"""
    try:
        # Get ontology classes
        classes_result = supabase.table("kudwa_ontology_classes")\
            .select("class_id, label, domain, class_type, properties")\
            .eq("status", "active")\
            .execute()

        # Get ontology relations
        relations_result = supabase.table("kudwa_ontology_relations")\
            .select("subject_class_id, predicate, object_class_id")\
            .eq("status", "active")\
            .execute()

        # Create NetworkX graph
        G = nx.Graph()

        # Add nodes (classes)
        for cls in classes_result.data:
            G.add_node(
                cls['class_id'],
                label=cls['label'],
                class_type=cls.get('class_type', 'Unknown'),
                domain=cls.get('domain', 'default')
            )

        # Add edges (relations)
        for rel in relations_result.data:
            if rel['subject_class_id'] and rel['object_class_id']:
                G.add_edge(
                    rel['subject_class_id'],
                    rel['object_class_id'],
                    predicate=rel['predicate']
                )

        # Create layout
        pos = nx.spring_layout(G, k=3, iterations=50)

        # Prepare node traces
        node_x = []
        node_y = []
        node_text = []
        node_info = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            node_data = G.nodes[node]
            label = node_data.get('label', node)
            class_type = node_data.get('class_type', 'Unknown')

            node_text.append(label)
            node_info.append(f"ID: {node}<br>Label: {label}<br>Type: {class_type}")

        # Prepare edge traces
        edge_x = []
        edge_y = []
        edge_info = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            edge_data = G.edges[edge]
            predicate = edge_data.get('predicate', 'related_to')
            edge_info.append(f"{edge[0]} --{predicate}--> {edge[1]}")

        # Create traces
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            hovertext=node_info,
            marker=dict(
                showscale=True,
                colorscale='Viridis',
                reversescale=True,
                color=[],
                size=30,
                colorbar=dict(
                    thickness=15,
                    len=0.5,
                    x=1.02,
                    title="Node Connections"
                ),
                line=dict(width=2)
            )
        )

        # Color nodes by number of connections
        node_adjacencies = []
        for node in G.nodes():
            node_adjacencies.append(len(list(G.neighbors(node))))

        node_trace.marker.color = node_adjacencies

        # Create figure
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=dict(text='Kudwa Financial Ontology Graph', font=dict(size=16)),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[
                    dict(
                        text=f"Ontology: {len(classes_result.data)} classes, {len(relations_result.data)} relations",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor='left', yanchor='bottom',
                        font=dict(color="gray", size=12)
                    )
                ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white'
            )
        )

        return fig

    except Exception as e:
        logger.error("Error creating ontology graph", error=str(e))
        # Return empty graph with error message
        return go.Figure(
            layout=go.Layout(
                title='Ontology Graph (Error)',
                annotations=[{
                    'text': f"Error loading ontology: {str(e)}",
                    'showarrow': False,
                    'xref': "paper", 'yref': "paper",
                    'x': 0.5, 'y': 0.5, 'xanchor': 'center', 'yanchor': 'middle'
                }],
                xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False}
            )
        )

# Dashboard layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🤖 Kudwa CrewAI Financial Assistant", className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    # File Upload Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📄 Document Upload & Processing"),
                dbc.CardBody([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select Files')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        multiple=False
                    ),
                    dbc.Input(
                        id="user-id-input",
                        placeholder="Enter your user ID",
                        type="text",
                        value="demo_user",
                        className="mb-3"
                    ),
                    dbc.Button(
                        "Process with CrewAI",
                        id="process-btn",
                        color="primary",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Ingest RootFi Data",
                        id="rootfi-btn",
                        color="warning",
                        className="me-2"
                    ),
                    dbc.Button(
                        "Build Knowledge Graph",
                        id="graph-btn",
                        color="success"
                    ),
                    html.Div(id="upload-status", className="mt-3")
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Chat Interface Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("💬 CrewAI Chat Interface"),
                dbc.CardBody([
                    html.Div(
                        id="chat-history",
                        style={
                            'height': '400px',
                            'overflow-y': 'auto',
                            'border': '1px solid #ddd',
                            'padding': '10px',
                            'margin-bottom': '10px',
                            'background-color': '#f8f9fa'
                        }
                    ),
                    dbc.InputGroup([
                        dbc.Input(
                            id="chat-input",
                            placeholder="Ask about your financial data...",
                            type="text"
                        ),
                        dbc.Button(
                            "Send",
                            id="send-btn",
                            color="primary"
                        )
                    ])
                ])
            ])
        ], width=8),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🔍 Semantic Search"),
                dbc.CardBody([
                    dbc.Input(
                        id="search-input",
                        placeholder="Search financial data...",
                        type="text",
                        className="mb-2"
                    ),
                    dbc.Button(
                        "Search",
                        id="search-btn",
                        color="info",
                        className="mb-3"
                    ),
                    html.Div(id="search-results")
                ])
            ])
        ], width=4)
    ], className="mb-4"),
    
    # Knowledge Graph Visualization
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🕸️ Knowledge Graph Visualization"),
                dbc.CardBody([
                    dcc.Graph(id="knowledge-graph"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button(
                                "Refresh Graph",
                                id="refresh-graph-btn",
                                color="secondary",
                                className="me-2"
                            ),
                            dbc.Button(
                                "Generate Interactive View",
                                id="interactive-graph-btn",
                                color="warning"
                            )
                        ])
                    ])
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    # Statistics and Metrics
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📊 System Statistics"),
                dbc.CardBody(id="stats-content")
            ])
        ], width=6),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🎯 Ontology Overview"),
                dbc.CardBody(id="ontology-content")
            ])
        ], width=6)
    ]),
    
    # Hidden div to store data
    html.Div(id="hidden-data", style={"display": "none"})
    
], fluid=True)


# Callback for file upload and processing
@app.callback(
    Output('upload-status', 'children'),
    [Input('process-btn', 'n_clicks'),
     Input('rootfi-btn', 'n_clicks')],
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('user-id-input', 'value')
)
def process_uploaded_file(crew_clicks, rootfi_clicks, contents, filename, user_id):
    if contents is None:
        return ""

    # Determine which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    try:
        # Decode file content
        content_type, content_string = contents.split(',')
        import base64
        decoded = base64.b64decode(content_string)

        files = {'file': (filename, decoded, 'application/json')}
        data = {'user_id': user_id}

        if button_id == 'rootfi-btn':
            # Send to RootFi ingestion endpoint
            response = requests.post(f"{API_BASE}/documents/ingest-rootfi", files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                return dbc.Alert([
                    html.H5("✅ RootFi Data Ingestion Successful!"),
                    html.P(f"File: {filename}"),
                    html.P(f"Document ID: {result.get('document_id', 'N/A')[:8]}..."),
                    html.P(f"Entities extracted: {result.get('entities_extracted', 0)}"),
                    html.P(f"Records processed: {result.get('records_processed', 0)}"),
                    html.P(f"Entity types: {', '.join(result.get('entity_types', []))}"),
                    html.P(f"Data quality: {result.get('data_quality_score', 0):.2f}"),
                    html.P(f"Processing time: {result.get('processing_time_ms', 0)}ms")
                ], color="success")
            else:
                return dbc.Alert(f"❌ RootFi ingestion failed: {response.text}", color="danger")

        elif button_id == 'process-btn':
            # Send to CrewAI endpoint
            response = requests.post(f"{API_BASE}/documents/upload-crew", files=files, data=data)

            if response.status_code == 200:
                result = response.json()
                return dbc.Alert([
                    html.H5("✅ CrewAI Processing Successful!"),
                    html.P(f"File: {filename}"),
                    html.P(f"Method: {result.get('processing_method', 'unknown')}"),
                    html.P(f"Graph nodes: {result.get('graph_stats', {}).get('total_nodes', 0)}"),
                    html.P(f"Graph edges: {result.get('graph_stats', {}).get('total_edges', 0)}")
                ], color="success")
            else:
                return dbc.Alert(f"❌ CrewAI processing failed: {response.text}", color="danger")

    except Exception as e:
        logger.error("File processing failed", error=str(e))
        return dbc.Alert(f"❌ Error: {str(e)}", color="danger")


# Callback for chat interface
@app.callback(
    Output('chat-history', 'children'),
    Input('send-btn', 'n_clicks'),
    State('chat-input', 'value'),
    State('chat-history', 'children'),
    State('user-id-input', 'value')
)
def update_chat(n_clicks, message, chat_history, user_id):
    if n_clicks is None or not message:
        return chat_history or []
    
    try:
        # Send message to CrewAI chat endpoint
        payload = {
            "message": message,
            "user_id": user_id,
            "context": {}
        }
        
        response = requests.post(f"{API_BASE}/crew/chat", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            # Create chat message elements
            user_msg = html.Div([
                html.Strong("You: "),
                html.Span(message)
            ], className="mb-2 p-2", style={"background-color": "#e3f2fd", "border-radius": "5px"})
            
            agent_msg = html.Div([
                html.Strong(f"🤖 {result.get('agent_type', 'Agent')}: "),
                html.Span(result.get('response', 'No response'))
            ], className="mb-2 p-2", style={"background-color": "#f3e5f5", "border-radius": "5px"})
            
            # Update chat history
            current_history = chat_history or []
            current_history.extend([user_msg, agent_msg])
            
            return current_history
        else:
            error_msg = html.Div([
                html.Strong("❌ Error: "),
                html.Span(f"Failed to get response: {response.text}")
            ], className="mb-2 p-2", style={"background-color": "#ffebee", "border-radius": "5px"})
            
            current_history = chat_history or []
            current_history.append(error_msg)
            return current_history
            
    except Exception as e:
        logger.error("Chat failed", error=str(e))
        error_msg = html.Div([
            html.Strong("❌ Error: "),
            html.Span(str(e))
        ], className="mb-2 p-2", style={"background-color": "#ffebee", "border-radius": "5px"})
        
        current_history = chat_history or []
        current_history.append(error_msg)
        return current_history


# Callback for semantic search
@app.callback(
    Output('search-results', 'children'),
    Input('search-btn', 'n_clicks'),
    State('search-input', 'value'),
    State('user-id-input', 'value')
)
def perform_search(n_clicks, query, user_id):
    if n_clicks is None or not query:
        return ""
    
    try:
        payload = {
            "query": query,
            "top_k": 5,
            "user_id": user_id
        }
        
        response = requests.post(f"{API_BASE}/crew/semantic-search", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            results = result.get('results', [])
            
            if not results:
                return dbc.Alert("No results found", color="info")
            
            search_items = []
            for i, item in enumerate(results):
                search_items.append(
                    dbc.Card([
                        dbc.CardBody([
                            html.H6(f"Result {i+1}"),
                            html.P(item.get('content', '')[:200] + "..."),
                            html.Small(f"Similarity: {item.get('similarity_score', 0):.3f}")
                        ])
                    ], className="mb-2")
                )
            
            return search_items
        else:
            return dbc.Alert(f"Search failed: {response.text}", color="danger")
            
    except Exception as e:
        logger.error("Search failed", error=str(e))
        return dbc.Alert(f"Error: {str(e)}", color="danger")


# Callback for knowledge graph
@app.callback(
    Output('knowledge-graph', 'figure'),
    [Input('refresh-graph-btn', 'n_clicks'),
     Input('graph-btn', 'n_clicks')],
    State('user-id-input', 'value')
)
def update_knowledge_graph(refresh_clicks, graph_clicks, user_id):
    """Update knowledge graph with real ontology data"""
    try:
        # Always show the current ontology graph
        return create_ontology_graph()
    except Exception as e:
        logger.error("Error updating knowledge graph", error=str(e))
        return go.Figure(
            layout=go.Layout(
                title='Knowledge Graph (Error)',
                annotations=[{
                    'text': f"Error loading graph: {str(e)}",
                    'showarrow': False,
                    'xref': "paper", 'yref': "paper",
                    'x': 0.5, 'y': 0.5, 'xanchor': 'center', 'yanchor': 'middle'
                }],
                xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False}
            )
        )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8051)
