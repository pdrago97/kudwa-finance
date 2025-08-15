"""
Simplified Kudwa CrewAI Dashboard with Ontology Graph and Human-in-the-Loop
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import requests
import json
import networkx as nx
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Kudwa CrewAI Dashboard"

# API base URL
API_BASE = "http://localhost:8000/api/v1"

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

def create_ontology_graph():
    """Create enhanced ontology graph with relationship labels and hover details"""
    try:
        # Get ontology classes
        classes_result = supabase.table("kudwa_ontology_classes")\
            .select("class_id, label, domain, class_type, properties")\
            .eq("status", "active")\
            .execute()

        # Get ontology relations
        relations_result = supabase.table("kudwa_ontology_relations")\
            .select("subject_class_id, predicate, object_class_id, properties")\
            .eq("status", "active")\
            .execute()

        # Create NetworkX graph
        G = nx.Graph()

        # Add nodes (classes) with detailed information
        for cls in classes_result.data:
            G.add_node(
                cls['class_id'],
                label=cls['label'],
                class_type=cls.get('class_type', 'Unknown'),
                domain=cls.get('domain', 'financial'),
                properties=cls.get('properties', {})
            )

        # Add edges (relations) with predicate information
        for rel in relations_result.data:
            if rel['subject_class_id'] and rel['object_class_id']:
                G.add_edge(
                    rel['subject_class_id'],
                    rel['object_class_id'],
                    predicate=rel['predicate'],
                    properties=rel.get('properties', {})
                )

        # Create layout with better spacing
        pos = nx.spring_layout(G, k=4, iterations=100, seed=42)

        # Prepare edge traces with relationship labels
        edge_traces = []
        edge_labels_x, edge_labels_y, edge_labels_text = [], [], []

        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            # Edge line
            edge_traces.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            ))

            # Edge label (relationship name)
            mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2
            predicate = edge[2].get('predicate', 'related_to')

            edge_labels_x.append(mid_x)
            edge_labels_y.append(mid_y)
            edge_labels_text.append(predicate)

        # Prepare node trace with enhanced hover information
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_text = [G.nodes[node].get('label', node) for node in G.nodes()]

        # Create detailed hover text for nodes
        node_hover_text = []
        node_colors = []

        for node in G.nodes():
            node_data = G.nodes[node]
            label = node_data.get('label', node)
            class_type = node_data.get('class_type', 'Unknown')
            domain = node_data.get('domain', 'financial')
            properties = node_data.get('properties', {})

            # Count connections
            connections = len(list(G.neighbors(node)))

            # Get connected nodes for context
            neighbors = list(G.neighbors(node))
            neighbor_labels = [G.nodes[n].get('label', n) for n in neighbors[:3]]
            neighbor_text = ', '.join(neighbor_labels)
            if len(neighbors) > 3:
                neighbor_text += f" (+{len(neighbors)-3} more)"

            hover_text = f"""
<b>{label}</b><br>
<b>ID:</b> {node}<br>
<b>Type:</b> {class_type}<br>
<b>Domain:</b> {domain}<br>
<b>Connections:</b> {connections}<br>
<b>Connected to:</b> {neighbor_text if neighbor_text else 'None'}<br>
<b>Properties:</b> {len(properties)} defined
            """.strip()

            node_hover_text.append(hover_text)

            # Color nodes by type
            if class_type == 'entity':
                node_colors.append('#4CAF50')  # Green for entities
            elif class_type == 'relationship':
                node_colors.append('#FF9800')  # Orange for relationships
            elif class_type == 'attribute':
                node_colors.append('#2196F3')  # Blue for attributes
            else:
                node_colors.append('#9C27B0')  # Purple for others

        # Create figure
        fig = go.Figure()

        # Add all edge traces
        for edge_trace in edge_traces:
            fig.add_trace(edge_trace)

        # Add edge labels
        fig.add_trace(go.Scatter(
            x=edge_labels_x, y=edge_labels_y,
            text=edge_labels_text,
            mode='text',
            textfont=dict(size=10, color='#666'),
            hoverinfo='none',
            showlegend=False
        ))

        # Add nodes with enhanced hover
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="middle center",
            textfont=dict(size=10, color='white'),
            marker=dict(
                size=40,
                color=node_colors,
                line=dict(width=2, color='white'),
                opacity=0.8
            ),
            hovertext=node_hover_text,
            hoverinfo='text',
            showlegend=False
        ))

        fig.update_layout(
            title=dict(
                text="Kudwa Financial Ontology Graph",
                x=0.5,
                font=dict(size=16)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            annotations=[
                dict(
                    text=f"Classes: {len(classes_result.data)} | Relations: {len(relations_result.data)}",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.02, y=0.02,
                    font=dict(size=12, color="gray")
                )
            ]
        )

        return fig

    except Exception as e:
        print(f"Error creating ontology graph: {e}")
        return go.Figure()

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🤖 Kudwa CrewAI Financial Assistant", className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    dbc.Row([
        # Chat Interface
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("💬 CrewAI Chat Interface"),
                dbc.CardBody([
                    dcc.Textarea(
                        id='chat-input',
                        placeholder='Ask about financial data, request ontology changes, or propose new data entries...',
                        style={'width': '100%', 'height': 100}
                    ),
                    html.Br(),
                    dbc.Button("Send", id="send-btn", color="primary", className="me-2"),
                    dbc.Button("Clear", id="clear-btn", color="secondary"),
                    html.Hr(),
                    html.Div(id='chat-output', style={'height': '300px', 'overflow-y': 'auto'})
                ])
            ])
        ], width=6),
        
        # Human-in-the-Loop Actions
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🔄 Human-in-the-Loop Actions"),
                dbc.CardBody([
                    html.Div(id='pending-actions', children=[
                        dbc.Alert("No pending actions", color="info")
                    ])
                ])
            ])
        ], width=6)
    ], className="mb-4"),
    
    dbc.Row([
        # Ontology Graph
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    "🕸️ Financial Ontology Graph",
                    dbc.Button("Refresh", id="refresh-graph", color="outline-primary", size="sm", className="float-end")
                ]),
                dbc.CardBody([
                    dcc.Graph(id='ontology-graph', figure=create_ontology_graph())
                ])
            ])
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        # System Statistics
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📊 System Statistics"),
                dbc.CardBody([
                    html.Div(id='system-stats')
                ])
            ])
        ], width=6),

        # Recent Activity
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📝 Recent Activity"),
                dbc.CardBody([
                    html.Div(id='recent-activity')
                ])
            ])
        ], width=6)
    ], className="mb-4"),

    dbc.Row([
        # Financial Datasets Table
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    "💰 Financial Datasets",
                    dbc.Button("Refresh", id="refresh-datasets", color="outline-primary", size="sm", className="float-end")
                ]),
                dbc.CardBody([
                    html.Div(id='datasets-table')
                ])
            ])
        ], width=6),

        # Recent Observations Table
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    "📈 Recent Financial Observations",
                    dbc.Button("Refresh", id="refresh-observations", color="outline-primary", size="sm", className="float-end")
                ]),
                dbc.CardBody([
                    html.Div(id='observations-table')
                ])
            ])
        ], width=6)
    ])
], fluid=True)

# Callbacks
@app.callback(
    Output('ontology-graph', 'figure'),
    [Input('refresh-graph', 'n_clicks')]
)
def update_ontology_graph(n_clicks):
    return create_ontology_graph()

@app.callback(
    [Output('chat-output', 'children'),
     Output('pending-actions', 'children'),
     Output('chat-input', 'value')],
    [Input('send-btn', 'n_clicks'),
     Input('clear-btn', 'n_clicks')],
    [State('chat-input', 'value')]
)
def handle_chat(send_clicks, clear_clicks, message):
    ctx = callback_context
    
    if not ctx.triggered:
        return [], [dbc.Alert("No pending actions", color="info")], ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'clear-btn':
        return [], [dbc.Alert("No pending actions", color="info")], ""
    
    if button_id == 'send-btn' and message:
        # Process message with CrewAI
        try:
            response = requests.post(f"{API_BASE}/crew/chat", json={
                "message": message,
                "context": {},
                "user_id": "dashboard_user"
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                chat_response = result.get('response', 'No response')
                requires_approval = result.get('requires_approval', False)
                detected_action = result.get('detected_action')
                proposed_action = result.get('proposed_action')

                # Check if this requires human approval
                pending_actions = []
                if requires_approval and proposed_action:
                    action_type = proposed_action.get('type', 'unknown')
                    action_desc = proposed_action.get('description', 'No description')

                    pending_actions.append(
                        dbc.Alert([
                            html.H6(f"🔄 {action_type.replace('_', ' ').title()} Request", className="alert-heading"),
                            html.P(action_desc),
                            html.Hr(),
                            html.Small("This action will modify the database and requires your approval."),
                            html.Br(), html.Br(),
                            dbc.ButtonGroup([
                                dbc.Button("✅ Approve & Execute", color="success", size="sm", id="approve-btn"),
                                dbc.Button("❌ Deny", color="danger", size="sm", id="deny-btn"),
                                dbc.Button("✏️ Request Modification", color="warning", size="sm", id="modify-btn")
                            ])
                        ], color="warning")
                    )
                
                chat_output = [
                    dbc.Alert([
                        html.Strong("You: "), message
                    ], color="light"),
                    dbc.Alert([
                        html.Strong("CrewAI: "), chat_response
                    ], color="primary")
                ]
                
                return chat_output, pending_actions or [dbc.Alert("No pending actions", color="info")], ""
            else:
                return [dbc.Alert(f"Error: {response.text}", color="danger")], [dbc.Alert("No pending actions", color="info")], ""
                
        except Exception as e:
            return [dbc.Alert(f"Error: {str(e)}", color="danger")], [dbc.Alert("No pending actions", color="info")], ""
    
    return [], [dbc.Alert("No pending actions", color="info")], ""

@app.callback(
    Output('system-stats', 'children'),
    [Input('refresh-graph', 'n_clicks')]
)
def update_system_stats(n_clicks):
    try:
        # Get counts from Supabase
        classes_count = len(supabase.table("kudwa_ontology_classes").select("id").eq("status", "active").execute().data)
        datasets_count = len(supabase.table("kudwa_financial_datasets").select("id").execute().data)
        observations_count = len(supabase.table("kudwa_financial_observations").select("id").execute().data)

        return [
            dbc.Row([
                dbc.Col([
                    html.H4(classes_count, className="text-primary"),
                    html.P("Ontology Classes")
                ], width=4),
                dbc.Col([
                    html.H4(datasets_count, className="text-success"),
                    html.P("Financial Datasets")
                ], width=4),
                dbc.Col([
                    html.H4(observations_count, className="text-info"),
                    html.P("Observations")
                ], width=4)
            ])
        ]
    except Exception as e:
        return [dbc.Alert(f"Error loading stats: {str(e)}", color="danger")]

@app.callback(
    Output('datasets-table', 'children'),
    [Input('refresh-datasets', 'n_clicks'),
     Input('refresh-graph', 'n_clicks')]
)
def update_datasets_table(refresh_datasets, refresh_graph):
    try:
        # Get financial datasets
        datasets_result = supabase.table("kudwa_financial_datasets")\
            .select("id, name, description, currency, period_start, period_end, created_at")\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()

        if not datasets_result.data:
            return dbc.Alert("No financial datasets found", color="info")

        # Create table rows
        table_rows = []
        for dataset in datasets_result.data:
            dataset_id = str(dataset.get('id', 'N/A'))[:8] + '...' if dataset.get('id') else 'N/A'
            description = dataset.get('description', 'No description')
            short_desc = description[:40] + '...' if len(description) > 40 else description

            table_rows.append(
                html.Tr([
                    html.Td(dataset_id),
                    html.Td(dataset.get('name', 'Unnamed')),
                    html.Td(dataset.get('currency', 'USD')),
                    html.Td(short_desc),
                    html.Td(dataset.get('period_start', 'Unknown')[:10] if dataset.get('period_start') else 'Unknown'),
                    html.Td(dataset.get('created_at', 'Unknown')[:10] if dataset.get('created_at') else 'Unknown')
                ])
            )

        return dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("ID"),
                    html.Th("Name"),
                    html.Th("Currency"),
                    html.Th("Description"),
                    html.Th("Period"),
                    html.Th("Created")
                ])
            ]),
            html.Tbody(table_rows)
        ], striped=True, bordered=True, hover=True, size="sm")

    except Exception as e:
        return dbc.Alert(f"Error loading datasets: {str(e)}", color="danger")

@app.callback(
    Output('observations-table', 'children'),
    [Input('refresh-observations', 'n_clicks'),
     Input('refresh-graph', 'n_clicks')]
)
def update_observations_table(refresh_observations, refresh_graph):
    try:
        # Get recent financial observations
        observations_result = supabase.table("kudwa_financial_observations")\
            .select("id, dataset_id, account_name, amount, currency, period_start, observation_type")\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()

        if not observations_result.data:
            return dbc.Alert("No financial observations found", color="info")

        # Create table rows
        table_rows = []
        for obs in observations_result.data:
            amount = obs.get('amount', 0)
            formatted_amount = f"${float(amount):,.2f}" if amount else "N/A"
            obs_id = str(obs.get('id', 'N/A'))[:8] + '...' if obs.get('id') else 'N/A'

            table_rows.append(
                html.Tr([
                    html.Td(obs_id),
                    html.Td(obs.get('account_name', 'Unknown')),
                    html.Td(formatted_amount),
                    html.Td(obs.get('currency', 'USD')),
                    html.Td(obs.get('observation_type', 'Unknown')),
                    html.Td(obs.get('period_start', 'Unknown')[:10] if obs.get('period_start') else 'Unknown')
                ])
            )

        return dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("ID"),
                    html.Th("Account"),
                    html.Th("Amount"),
                    html.Th("Currency"),
                    html.Th("Type"),
                    html.Th("Period")
                ])
            ]),
            html.Tbody(table_rows)
        ], striped=True, bordered=True, hover=True, size="sm")

    except Exception as e:
        return dbc.Alert(f"Error loading observations: {str(e)}", color="danger")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8052)
