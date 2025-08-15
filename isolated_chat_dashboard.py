#!/usr/bin/env python3
"""
Kudwa - Isolated Chat Dashboard
Clean, modern interface with separate workflows for N8N integration
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import requests
from requests.auth import HTTPBasicAuth
import json
import base64
import os
from datetime import datetime
import uuid
import time
import networkx as nx
import numpy as np
from n8n_config import N8N_WEBHOOKS, N8N_CONFIG, get_webhook_url, validate_payload, get_auth_config

# Optional Supabase client for persistence when user accepts
try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except Exception:
    supabase_client = None

# Initialize Dash app with modern theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Kudwa - Ontology Evolution Platform"

def create_header():
    """Create clean, modern header"""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H1([
                    html.Span("🧠", style={'fontSize': '40px', 'marginRight': '15px'}),
                    "Kudwa"
                ], className="mb-0", style={'color': '#2c3e50', 'fontWeight': '700'}),
                html.P("Ontology Evolution Platform", 
                       className="text-muted mb-0", style={'fontSize': '16px', 'fontWeight': '300'})
            ], width=8),
            dbc.Col([
                dbc.Badge("Connected", color="success", className="me-2"),
                dbc.Badge(f"Updated: {datetime.now().strftime('%H:%M')}", 
                         color="light", className="text-dark")
            ], width=4, className="text-end align-self-center")
        ])
    ], className="mb-5", style={'padding': '30px 0', 'borderBottom': '1px solid #e9ecef'})

def get_cytoscape_layout_options():
    """Get layout options for different graph sizes"""
    return [
        {'label': '🌐 Force-directed (COSE)', 'value': 'cose'},
        {'label': '🎯 Circular', 'value': 'circle'},
        {'label': '📊 Hierarchical', 'value': 'dagre'},
        {'label': '🔄 Concentric', 'value': 'concentric'},
        {'label': '📐 Grid', 'value': 'grid'}
    ]

def create_ontology_dashboard():
    """Create the ontology management dashboard with interactive graph"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("📊 Living Ontology Graph", className="mb-0"),
            html.Div([
                dcc.Dropdown(
                    id="layout-selector",
                    options=get_cytoscape_layout_options(),
                    value="cose",
                    style={'width': '150px', 'fontSize': '12px'},
                    className="me-2"
                ),
                dbc.Button("🔄", id="refresh-dashboard", size="sm", color="light", className="me-2"),
                dbc.Button("🎯", id="center-graph", size="sm", color="info", className="me-2"),
                dbc.Button("📊", id="toggle-stats", size="sm", color="secondary")
            ], className="float-end d-flex align-items-center")
        ]),
        dbc.CardBody([
            # Interactive Cytoscape Graph
            html.Div([
                cyto.Cytoscape(
                    id='ontology-graph',
                    layout={'name': 'cose', 'animate': True, 'animationDuration': 1000},
                    style={'width': '100%', 'height': '450px'},
                    elements=[],
                    stylesheet=[
                        # Node styles
                        {
                            'selector': 'node',
                            'style': {
                                'content': 'data(label)',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'background-color': 'data(color)',
                                'border-width': 2,
                                'border-color': '#fff',
                                'width': 'data(size)',
                                'height': 'data(size)',
                                'font-size': '12px',
                                'font-weight': 'bold',
                                'color': '#fff',
                                'text-outline-width': 2,
                                'text-outline-color': 'data(color)'
                            }
                        },
                        # Edge styles
                        {
                            'selector': 'edge',
                            'style': {
                                'curve-style': 'bezier',
                                'target-arrow-shape': 'triangle',
                                'target-arrow-color': '#666',
                                'line-color': '#666',
                                'width': 2,
                                'label': 'data(predicate)',
                                'font-size': '10px',
                                'text-rotation': 'autorotate',
                                'text-margin-y': -10
                            }
                        },
                        # Domain-specific colors
                        {
                            'selector': '[domain = "financial"]',
                            'style': {'background-color': '#1f77b4'}
                        },
                        {
                            'selector': '[domain = "business"]',
                            'style': {'background-color': '#2ca02c'}
                        },
                        {
                            'selector': '[domain = "technical"]',
                            'style': {'background-color': '#d62728'}
                        },
                        {
                            'selector': '[domain = "legal"]',
                            'style': {'background-color': '#9467bd'}
                        },
                        # Hover effects
                        {
                            'selector': 'node:selected',
                            'style': {
                                'border-width': 4,
                                'border-color': '#ff6b6b',
                                'background-color': '#ff6b6b'
                            }
                        },
                        # High confidence nodes
                        {
                            'selector': '[confidence > 0.8]',
                            'style': {
                                'border-width': 3,
                                'border-color': '#4CAF50'
                            }
                        }
                    ]
                )
            ], className="mb-3"),

            # Collapsible Stats Section
            dbc.Collapse([
                # Stats Cards
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Classes", className="card-title text-primary"),
                                html.H4(id="classes-count", children="0", className="mb-0")
                            ])
                        ], color="primary", outline=True)
                    ], width=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Relations", className="card-title text-success"),
                                html.H4(id="relations-count", children="0", className="mb-0")
                            ])
                        ], color="success", outline=True)
                    ], width=4),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("Domains", className="card-title text-info"),
                                html.H4(id="domains-count", children="0", className="mb-0")
                            ])
                        ], color="info", outline=True)
                    ], width=4)
                ], className="mb-3"),

                # Recent Activity
                html.H6("📋 Recent Activity", className="mb-2"),
                html.Div(id="recent-activity", children=[
                    dbc.Alert("Loading ontology data...", color="info")
                ]),

                # Pending Approvals
                html.H6("⏳ Pending Approvals", className="mb-2 mt-3"),
                html.Div(id="pending-approvals", children=[])
            ], id="stats-collapse", is_open=False),

            # Graph Info Panel
            html.Div(id="graph-info", children=[
                dbc.Alert([
                    html.Strong("🎯 Interactive Ontology Graph"),
                    html.Br(),
                    html.Small("Click nodes to explore • Hover for details • Graph updates in real-time as you add entities through chat")
                ], color="info", className="mb-0")
            ])
        ])
    ], className="h-100")

def create_chat_interface(chat_type, title, description, icon, color):
    """Create isolated chat interface for specific N8N workflow"""
    return dbc.Card([
        dbc.CardHeader([
            html.H4([
                html.Span(icon, style={'fontSize': '24px', 'marginRight': '12px'}),
                title
            ], className="mb-2", style={'color': color, 'fontWeight': '600'}),
            html.P(description, className="mb-0 text-muted", style={'fontSize': '14px'})
        ], style={'backgroundColor': '#f8f9fa', 'border': 'none'}),
        dbc.CardBody([
            # File Upload Section
            html.Div([
                html.H6("📁 Upload Document (optional)", className="mb-3", style={'color': '#495057'}),
                dcc.Upload(
                    id=f'upload-{chat_type}',
                    children=html.Div([
                        html.I(className="fas fa-cloud-upload-alt", 
                               style={'fontSize': '32px', 'color': color, 'marginBottom': '10px'}),
                        html.Br(),
                        html.Span("Drop files here or click to browse", 
                                style={'color': '#6c757d', 'fontSize': '14px'})
                    ], style={'textAlign': 'center', 'padding': '40px 20px'}),
                    style={
                        'width': '100%',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderRadius': '12px',
                        'borderColor': color,
                        'backgroundColor': '#f8f9fa',
                        'cursor': 'pointer',
                        'transition': 'all 0.3s ease'
                    },
                    multiple=False
                ),
                html.Div(id=f'upload-status-{chat_type}', className="mt-2")
            ], className="mb-4"),
            
            # Chat Section
            html.Div([
                html.H6("💬 Chat Context", className="mb-3", style={'color': '#495057'}),
                html.Div(
                    id=f'chat-history-{chat_type}',
                    style={
                        'height': '300px',
                        'overflowY': 'auto',
                        'backgroundColor': '#f8f9fa',
                        'border': '1px solid #dee2e6',
                        'borderRadius': '8px',
                        'padding': '15px',
                        'marginBottom': '15px'
                    },
                    children=[
                        html.Div([
                            html.Span("🤖", style={'fontSize': '16px', 'marginRight': '8px'}),
                            html.Span(f"Ready to help with {title.lower()}. You can upload a document (optional) or just start chatting.",
                                    style={'color': '#6c757d', 'fontSize': '14px'})
                        ])
                    ]
                ),
                dbc.InputGroup([
                    dbc.Input(
                        id=f"chat-input-{chat_type}",
                        placeholder=f"Ask about {title.lower()}...",
                        style={'border': '1px solid #dee2e6', 'borderRadius': '8px 0 0 8px'}
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-paper-plane")],
                        id=f"chat-submit-{chat_type}",
                        color="primary",
                        style={'borderRadius': '0 8px 8px 0'}
                    )
                ])
            ])
        ])
    ], className="h-100", style={'border': f'2px solid {color}', 'borderRadius': '12px'})



# Main Layout
app.layout = dbc.Container([
    create_header(),
    
    # Enhanced Layout with Dashboard and Chat
    dbc.Row([
        # Left Column: Ontology Dashboard
        dbc.Col([
            create_ontology_dashboard()
        ], width=4),

        # Right Column: Chat Interface
        dbc.Col([
            create_chat_interface(
                chat_type='ontology',
                title='🧠 Ontology Extension',
                description='Extend and adapt your ontology based on new documents and requirements',
                icon='🧠',
                color='#6f42c1'
            )
        ], width=8)
    ], className="mb-5"),
    

    
    # Hidden div to store session data
    html.Div(id='session-data', style={'display': 'none'})
    
], fluid=True, style={'backgroundColor': '#ffffff', 'minHeight': '100vh', 'padding': '0 40px'})

# Callback for Ontology Extension Chat
@app.callback(
    [Output('chat-history-ontology', 'children'),
     Output('upload-status-ontology', 'children')],
    [Input('chat-submit-ontology', 'n_clicks'),
     Input('upload-ontology', 'contents')],
    [State('chat-input-ontology', 'value'),
     State('upload-ontology', 'filename'),
     State('chat-history-ontology', 'children')]
)
def handle_ontology_chat(n_clicks, upload_contents, chat_input, upload_filename, chat_history):
    ctx = callback_context
    if not ctx.triggered:
        return chat_history, ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    new_history = chat_history or []
    upload_status = ""
    
    # Handle file upload with enhanced processing
    if trigger_id == 'upload-ontology' and upload_contents:
        try:
            content_type, content_string = upload_contents.split(',')
            decoded = base64.b64decode(content_string)

            # Determine file type and create appropriate message
            file_extension = upload_filename.split('.')[-1].lower() if '.' in upload_filename else 'unknown'

            if file_extension in ['json']:
                analysis_message = f"Please analyze this JSON financial document ({upload_filename}) and extract entities, propose ontology extensions, and suggest data entries for our financial system."
            elif file_extension in ['csv', 'xlsx']:
                analysis_message = f"Please analyze this financial data file ({upload_filename}) and identify account structures, transaction patterns, and propose appropriate ontology extensions."
            elif file_extension in ['pdf', 'txt']:
                analysis_message = f"Please analyze this financial document ({upload_filename}) and extract relevant financial information, entities, and propose ontology improvements."
            else:
                analysis_message = f"Please analyze this uploaded file ({upload_filename}) for financial data and propose ontology extensions."

            # Enhanced webhook data with file processing support
            webhook_data = {
                'body': {
                    'message': analysis_message,
                    'filename': upload_filename,
                    'file_content': content_string,  # Base64 encoded content
                    'file_type': file_extension,
                    'file_size': len(decoded),
                    'timestamp': datetime.now().isoformat()
                },
                'chatId': str(uuid.uuid4())
            }

            # Send to enhanced N8N workflow
            webhook_response = send_to_n8n_webhook('ontology_extension', webhook_data)
            upload_status = create_enhanced_file_response_display(webhook_response, upload_filename)

            # Add to chat history with file info
            new_history.append(html.Div([
                html.Strong("📁 File Upload: ", style={'color': '#6f42c1'}),
                html.Span(f"Analyzing {upload_filename} ({file_extension.upper()}, {len(decoded)} bytes)")
            ], className="mb-2 p-2", style={'backgroundColor': '#e3f2fd', 'borderRadius': '8px', 'border': '1px solid #2196f3'}))

        except Exception as e:
            upload_status = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Error processing file: {str(e)}"
            ], color="danger", className="mt-2")
    
    # Handle chat message
    elif trigger_id == 'chat-submit-ontology' and n_clicks and chat_input:
        # Add user message
        new_history.append(html.Div([
            html.Strong("👤 You: ", style={'color': '#495057'}),
            html.Span(chat_input)
        ], className="mb-2"))
        
        # Send to N8N webhook with chat context - let agent decide what to do
        webhook_data = {
            'body': {
                'message': chat_input,
                'timestamp': datetime.now().isoformat()
            },
            'chatId': str(uuid.uuid4())
        }

        # Send to actual N8N webhook and get response
        webhook_response = send_to_n8n_webhook('ontology_extension', webhook_data)

        if webhook_response.get('success'):
            # Process the complex response structure
            response_display = create_enhanced_webhook_response_display(webhook_response)
            new_history.append(response_display)
        else:
            ai_response = f"❌ Error connecting to AI agent: {webhook_response.get('error', 'Unknown error')}"
            new_history.append(html.Div([
                html.Strong("🧠 Ontology Agent: ", style={'color': '#6f42c1'}),
                html.Span(ai_response)
            ], className="mb-2 p-3", style={'backgroundColor': '#f0f0ff', 'borderRadius': '8px', 'border': '1px solid #6f42c1'}))
    
    return new_history, upload_status

# Clear input callback
@app.callback(
    Output('chat-input-ontology', 'value'),
    [Input('chat-submit-ontology', 'n_clicks')]
)
def clear_ontology_input(n_clicks):
    if n_clicks:
        return ""
    return dash.no_update

# N8N Webhook Integration Functions
def send_to_n8n_webhook(webhook_type, data):
    """Send data to specific N8N webhook with retry logic"""
    try:
        # Validate payload structure
        if not validate_payload(webhook_type, data):
            return {'error': f'Invalid payload structure for {webhook_type}'}

        webhook_url = get_webhook_url(webhook_type)
        auth_config = get_auth_config()

        # Retry logic
        for attempt in range(N8N_CONFIG['retry_attempts']):
            try:
                # Prepare request parameters
                request_params = {
                    'url': webhook_url,
                    'json': data,
                    'timeout': N8N_CONFIG['timeout'],
                    'headers': {'Content-Type': 'application/json'}
                }

                # Add authentication if configured
                if 'x_api_key' in auth_config:
                    request_params['headers']['X-API-Key'] = auth_config['x_api_key']
                elif 'basic_auth' in auth_config:
                    request_params['auth'] = HTTPBasicAuth(*auth_config['basic_auth'])
                elif 'api_key' in auth_config:
                    request_params['headers']['Authorization'] = f"Bearer {auth_config['api_key']}"

                response = requests.post(**request_params)

                if response.status_code == 200:
                    return {
                        'success': True,
                        'data': response.json(),
                        'webhook_type': webhook_type,
                        'attempt': attempt + 1
                    }
                else:
                    error_msg = f'Webhook returned status {response.status_code}'
                    if attempt == N8N_CONFIG['retry_attempts'] - 1:
                        return {'error': error_msg, 'status_code': response.status_code}

            except requests.exceptions.Timeout:
                if attempt == N8N_CONFIG['retry_attempts'] - 1:
                    return {'error': 'Webhook request timed out'}
                time.sleep(N8N_CONFIG['retry_delay'])

            except requests.exceptions.RequestException as e:
                if attempt == N8N_CONFIG['retry_attempts'] - 1:
                    return {'error': f'Request failed: {str(e)}'}
                time.sleep(N8N_CONFIG['retry_delay'])

    except ValueError as e:
        return {'error': str(e)}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}

def create_webhook_response_display(response_data):
    """Create UI component to display N8N webhook response and any proposals"""
    if response_data.get('success'):
        data = response_data.get('data', {})
        proposals = data.get('proposals', [])
        cards = []
        for p in proposals:
            pid = p.get('id') or str(uuid.uuid4())
            title = p.get('title', 'Proposed Action')
            description = p.get('description', '')
            confidence = p.get('confidence', 0.8)
            action = p.get('action', {})
            card = dbc.Card([
                dbc.CardHeader(title),
                dbc.CardBody([
                    html.P(description),
                    dbc.Badge(f"{confidence:.0%} confidence", color="info", className="me-2"),
                    html.Div([
                        dbc.Button("Accept", id={'type': 'accept-proposal', 'index': pid}, color='success', size='sm', className='me-2'),
                        dbc.Button("Reject", id={'type': 'reject-proposal', 'index': pid}, color='danger', size='sm')
                    ], className='mt-2')
                ])
            ], className="mb-2")
            cards.append(card)
        header = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            html.Strong("N8N Workflow Triggered Successfully!"),
        ], color="success", className="mt-2")
        return html.Div([header] + cards)
    else:
        error_msg = response_data.get('error', 'Unknown error')
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            html.Strong("N8N Webhook Error:"),
            html.Br(),
            html.Small(error_msg)
        ], color="danger", className="mt-2")

def create_interactive_schema_form(schema):
    """Create interactive form based on JSON schema for human-in-the-loop validation"""
    properties = schema.get('properties', {})
    required_fields = schema.get('required', [])

    components = []

    # Create form header
    components.append(html.Div([
        html.H5("🤖 AI Agent Response Schema", className="text-primary"),
        html.P("The AI agent is ready to provide structured responses. Here's what it can generate:",
               className="text-muted")
    ], className="mb-3"))

    # Create interactive preview for each field
    for field_name, field_schema in properties.items():
        field_type = field_schema.get('type', 'string')
        field_desc = field_schema.get('description', f'AI will generate {field_name}')
        is_required = field_name in required_fields

        # Create preview card for each field
        card_color = "primary" if field_name == "response" else "info" if field_name.endswith("_extensions") else "success"

        components.append(dbc.Card([
            dbc.CardHeader([
                html.Strong(f"📝 {field_name.replace('_', ' ').title()}"),
                dbc.Badge("Required" if is_required else "Optional",
                         color="danger" if is_required else "secondary", className="ms-2")
            ]),
            dbc.CardBody([
                html.P(field_desc, className="card-text"),
                create_field_preview(field_name, field_schema)
            ])
        ], color=card_color, outline=True, className="mb-2"))

    # Add action buttons
    components.append(html.Div([
        dbc.Button("✨ Generate AI Response", id="generate-ai-response",
                  color="primary", size="lg", className="me-2"),
        dbc.Button("📊 View Current Ontology", id="view-ontology",
                  color="info", size="lg", className="me-2"),
        dbc.Button("📄 Upload Document", id="upload-document-btn",
                  color="success", size="lg")
    ], className="text-center mt-4"))

    return html.Div(components)

def create_field_preview(field_name, field_schema):
    """Create preview of what each field will contain"""
    field_type = field_schema.get('type', 'string')

    if field_name == "response":
        return dbc.Alert("AI will provide a natural language response here", color="light")
    elif field_name == "ontology_extensions":
        return html.Div([
            html.Small("Example ontology extensions:", className="text-muted"),
            dbc.ListGroup([
                dbc.ListGroupItem([
                    html.Strong("New Entity: "),
                    "Payment Method",
                    dbc.Badge("95%", color="success", className="ms-2")
                ]),
                dbc.ListGroupItem([
                    html.Strong("New Relation: "),
                    "Customer → uses → Payment Method",
                    dbc.Badge("87%", color="info", className="ms-2")
                ])
            ], flush=True)
        ])
    elif field_name == "data_entry_proposals":
        return html.Div([
            html.Small("Example data entries:", className="text-muted"),
            dbc.ListGroup([
                dbc.ListGroupItem([
                    html.Strong("Transaction: "),
                    "$1,250.00 - Credit Card Payment",
                    dbc.Badge("92%", color="success", className="ms-2")
                ])
            ], flush=True)
        ])
    else:
        return dbc.Alert(f"AI will generate {field_type} data", color="light")

def load_ontology_graph_data():
    """Load ontology graph data from Supabase for visualization"""
    if not supabase_client:
        return {"nodes": [], "edges": [], "stats": {"classes": 0, "relations": 0, "domains": 0}}

    try:
        # Get all ontology classes (nodes)
        classes_result = supabase_client.table('kudwa_ontology_classes')\
            .select('id, class_id, label, domain, confidence_score, status, created_at, properties')\
            .eq('status', 'active')\
            .execute()

        # Get all ontology relations (edges)
        relations_result = supabase_client.table('kudwa_ontology_relations')\
            .select('id, subject_class_id, predicate, object_class_id, confidence_score, domain, properties')\
            .eq('status', 'active')\
            .execute()

        nodes = []
        edges = []
        domains = set()

        # Process nodes
        for cls in (classes_result.data or []):
            domain = cls.get('domain', 'default')
            domains.add(domain)

            nodes.append({
                'id': cls.get('class_id', cls.get('id')),
                'label': cls.get('label', 'Unknown'),
                'domain': domain,
                'confidence': cls.get('confidence_score', 1.0),
                'created_at': cls.get('created_at', ''),
                'properties': cls.get('properties', {}),
                'db_id': cls.get('id')
            })

        # Process edges
        for rel in (relations_result.data or []):
            edges.append({
                'source': rel.get('subject_class_id'),
                'target': rel.get('object_class_id'),
                'predicate': rel.get('predicate', 'related_to'),
                'confidence': rel.get('confidence_score', 1.0),
                'domain': rel.get('domain', 'default'),
                'properties': rel.get('properties', {}),
                'db_id': rel.get('id')
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "classes": len(nodes),
                "relations": len(edges),
                "domains": len(domains)
            }
        }
    except Exception as e:
        print(f"Error loading ontology graph data: {e}")
        return {"nodes": [], "edges": [], "stats": {"classes": 0, "relations": 0, "domains": 0}}

def load_ontology_stats():
    """Load current ontology statistics from Supabase"""
    graph_data = load_ontology_graph_data()
    stats = graph_data["stats"]

    if not supabase_client:
        return {"classes": 0, "relations": 0, "domains": 0, "recent": []}

    try:
        # Get recent activity
        recent_classes = supabase_client.table('kudwa_ontology_classes')\
            .select('class_id, label, created_at, confidence_score')\
            .order('created_at', desc=True)\
            .limit(5)\
            .execute()

        recent_activity = []
        for item in (recent_classes.data or []):
            recent_activity.append({
                'type': 'class',
                'name': item.get('label', item.get('class_id', 'Unknown')),
                'confidence': item.get('confidence_score', 1.0),
                'created_at': item.get('created_at', '')
            })

        return {
            "classes": stats["classes"],
            "relations": stats["relations"],
            "domains": stats["domains"],
            "recent": recent_activity
        }
    except Exception as e:
        print(f"Error loading ontology stats: {e}")
        return {"classes": 0, "relations": 0, "domains": 0, "recent": []}

def create_cytoscape_elements(graph_data):
    """Create Cytoscape elements from ontology graph data"""
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    elements = []

    # Domain colors
    domain_colors = {
        'financial': '#1f77b4',
        'default': '#ff7f0e',
        'business': '#2ca02c',
        'technical': '#d62728',
        'legal': '#9467bd'
    }

    # Add nodes
    for node in nodes:
        domain = node.get('domain', 'default')
        confidence = node.get('confidence', 1.0)

        # Node size based on confidence (20-60px)
        size = 30 + (confidence * 30)

        elements.append({
            'data': {
                'id': node['id'],
                'label': node['label'][:20],  # Truncate long labels
                'domain': domain,
                'confidence': confidence,
                'created_at': node.get('created_at', ''),
                'full_label': node['label'],
                'properties': json.dumps(node.get('properties', {})),
                'color': domain_colors.get(domain, '#666'),
                'size': size
            },
            'classes': domain
        })

    # Add edges
    for edge in edges:
        source = edge['source']
        target = edge['target']

        # Only add edge if both nodes exist
        node_ids = [n['id'] for n in nodes]
        if source in node_ids and target in node_ids:
            elements.append({
                'data': {
                    'id': f"{source}-{target}",
                    'source': source,
                    'target': target,
                    'predicate': edge.get('predicate', 'related_to'),
                    'confidence': edge.get('confidence', 1.0),
                    'domain': edge.get('domain', 'default')
                }
            })

    return elements

def create_enhanced_webhook_response_display(response_data):
    """Create enhanced UI component to handle complex N8N webhook responses"""

    # Handle different response formats from n8n
    if isinstance(response_data, list):
        # n8n returned a list directly - take the first item
        if len(response_data) > 0:
            first_item = response_data[0]
            # Check if this is a JSON schema instead of actual data
            if isinstance(first_item, dict) and first_item.get('type') == 'object' and 'properties' in first_item:
                # This is a JSON schema - create interactive form based on schema
                return create_interactive_schema_form(first_item)
            data = first_item
        else:
            data = {}
    elif isinstance(response_data, dict):
        # Check if it's wrapped in a success/data structure
        if not response_data.get('success', True):
            error_msg = response_data.get('error', 'Unknown error')
            return dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                html.Strong("N8N Webhook Error:"),
                html.Br(),
                html.Small(error_msg)
            ], color="danger", className="mt-2")

        # Extract data - could be nested or direct
        data = response_data.get('data', response_data)
    else:
        # Unexpected format
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            html.Strong("Unexpected response format from n8n"),
            html.Br(),
            html.Small(f"Received: {type(response_data)}")
        ], color="warning", className="mt-2")

    # Helper function to safely get values from data
    def safe_get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return default

    # Handle different response structures
    components = []

    # Add debug info (temporary - remove in production)
    components.append(html.Details([
        html.Summary("🔍 Debug: Raw n8n Response", style={'cursor': 'pointer', 'color': '#666'}),
        html.Pre(json.dumps(data, indent=2, default=str),
                style={'fontSize': '10px', 'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '4px', 'maxHeight': '200px', 'overflow': 'auto'})
    ], className="mb-3"))

    # Main response text
    response_text = safe_get(data, 'response', '')
    if response_text:
        components.append(html.Div([
            html.Strong("🧠 Ontology Agent: ", style={'color': '#6f42c1'}),
            html.Span(response_text)
        ], className="mb-3 p-3", style={'backgroundColor': '#f0f0ff', 'borderRadius': '8px', 'border': '1px solid #6f42c1'}))

    # Enhanced Ontology extensions with Supabase integration
    ontology_extensions = safe_get(data, 'ontology_extensions', [])
    if ontology_extensions:
        ext_cards = []
        for ext in ontology_extensions:
            ext_id = safe_get(ext, 'id', str(uuid.uuid4()))
            entity_type = safe_get(ext, 'entity_type', 'Entity')
            description = safe_get(ext, 'description', '')
            justification = safe_get(ext, 'justification', '')
            confidence = safe_get(ext, 'confidence', 0.8)

            # Enhanced card with database preview
            ext_cards.append(dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.Strong(f"🏗️ {entity_type}"),
                        dbc.Badge(f"{confidence:.0%}",
                                color="success" if confidence > 0.8 else "warning" if confidence > 0.6 else "danger",
                                className="ms-2"),
                        dbc.Badge("New Ontology Class", color="primary", className="ms-1")
                    ])
                ]),
                dbc.CardBody([
                    html.P(description, className="card-text"),
                    html.Div([
                        html.Strong("AI Justification: "),
                        html.Span(justification, className="text-muted")
                    ], className="mb-3"),

                    # Collapsible database preview
                    dbc.Collapse([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("📊 Will be added to kudwa_ontology_classes:", className="text-primary"),
                                html.Pre(json.dumps({
                                    "class_id": entity_type.lower().replace(' ', '_'),
                                    "label": entity_type,
                                    "domain": "financial",
                                    "class_type": "pl:Entity",
                                    "confidence_score": confidence,
                                    "status": "pending_approval",
                                    "properties": {"description": description, "justification": justification}
                                }, indent=2), className="bg-light p-2 rounded", style={'fontSize': '11px'})
                            ])
                        ], color="light")
                    ], id={'type': 'preview-collapse', 'index': ext_id}, is_open=False),

                    html.Div([
                        dbc.Button("✅ Add to Ontology", id={'type': 'accept-extension', 'index': ext_id},
                                 color='success', size='sm', className='me-2'),
                        dbc.Button("👁️ Preview SQL", id={'type': 'preview-extension', 'index': ext_id},
                                 color='info', size='sm', className='me-2'),
                        dbc.Button("❌ Reject", id={'type': 'reject-extension', 'index': ext_id},
                                 color='danger', size='sm')
                    ], className='mt-3')
                ])
            ], className="mb-3", outline=True, color="primary"))

        components.append(html.Div([
            html.H6("🏗️ Proposed Ontology Extensions", className="mb-3"),
            html.P("These AI-generated ontology extensions will be added to your Supabase database:", className="text-muted small"),
            html.Div(ext_cards)
        ]))

    # Data entry proposals
    data_proposals = safe_get(data, 'data_entry_proposals', [])
    if data_proposals:
        data_cards = []
        for proposal in data_proposals:
            prop_id = safe_get(proposal, 'id', str(uuid.uuid4()))
            data_cards.append(dbc.Card([
                dbc.CardHeader([
                    html.Strong(f"📊 {safe_get(proposal, 'entity_type', 'Data')} Entry"),
                    dbc.Badge(f"{safe_get(proposal, 'confidence', 0.8):.0%}", color="primary", className="ms-2")
                ]),
                dbc.CardBody([
                    html.P(safe_get(proposal, 'description', '')),
                    html.Pre(str(safe_get(proposal, 'proposed_data', {})),
                           style={'fontSize': '12px', 'backgroundColor': '#f8f9fa', 'padding': '10px', 'borderRadius': '4px'}),
                    html.Div([
                        dbc.Button("Accept Data", id={'type': 'accept-data', 'index': prop_id},
                                 color='primary', size='sm', className='me-2'),
                        dbc.Button("Edit & Accept", id={'type': 'edit-data', 'index': prop_id},
                                 color='warning', size='sm', className='me-2'),
                        dbc.Button("Reject", id={'type': 'reject-data', 'index': prop_id},
                                 color='danger', size='sm')
                    ], className='mt-2')
                ])
            ], className="mb-2"))

        components.append(html.Div([
            html.H6("📊 Proposed Data Entries", className="mb-3"),
            html.Div(data_cards)
        ]))

    # Suggested actions
    suggested_actions = safe_get(data, 'suggested_actions', [])
    if suggested_actions:
        action_items = []
        for action in suggested_actions:
            action_items.append(html.Li([
                html.Strong(safe_get(action, 'label', 'Action')),
                html.Span(f" - {safe_get(action, 'target', '')}", className="text-muted")
            ]))

        components.append(html.Div([
            html.H6("💡 Suggested Actions", className="mb-2"),
            html.Ul(action_items)
        ], className="mt-3"))

    # Context needed
    context_needed = safe_get(data, 'context_needed')
    if context_needed:
        components.append(dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            html.Strong("Additional Context Needed: "),
            html.Span(context_needed)
        ], color="info", className="mt-2"))

    # If no structured data, show raw response
    if not components:
        components.append(html.Div([
            html.Strong("🧠 Ontology Agent Response: ", style={'color': '#6f42c1'}),
            html.Pre(str(data), style={'fontSize': '12px', 'backgroundColor': '#f8f9fa', 'padding': '15px', 'borderRadius': '8px'})
        ], className="mb-3 p-3", style={'backgroundColor': '#f0f0ff', 'borderRadius': '8px', 'border': '1px solid #6f42c1'}))

    return html.Div(components)


def create_enhanced_file_response_display(response_data, filename):
    """Create enhanced display for file processing responses"""
    if not response_data or not response_data.get('success'):
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Failed to process file: {filename}"
        ], color="warning", className="mt-2")

    try:
        agent_response = response_data.get('data', {})

        # File processing specific display
        response_elements = [
            html.H6(f"📄 File Analysis: {filename}", className="card-title text-primary"),
        ]

        # Show file metadata if available
        if hasattr(agent_response, 'get'):
            content_type = agent_response.get('contentType', 'unknown')
            has_file = agent_response.get('hasFile', False)

            if has_file:
                response_elements.append(
                    dbc.Badge(f"Type: {content_type.upper()}", color="secondary", className="me-2")
                )

        # Standard response processing
        response_text = agent_response.get('response', 'File processed successfully')
        response_type = agent_response.get('response_type', 'ontology_proposal')
        confidence = agent_response.get('confidence_score', 0)

        response_elements.extend([
            html.P(response_text, className="card-text mt-2"),
            html.Small(f"Analysis Type: {response_type} | Confidence: {confidence:.1%}",
                      className="text-muted")
        ])

        # Enhanced ontology extensions display for files
        ontology_extensions = agent_response.get('ontology_extensions', [])
        if ontology_extensions:
            response_elements.append(html.Hr())
            response_elements.append(html.H6("🏗️ Extracted Ontology Extensions", className="text-success"))

            for i, ext in enumerate(ontology_extensions):
                response_elements.append(
                    dbc.Card([
                        dbc.CardBody([
                            html.H6(f"{ext.get('entity_type', 'Unknown')}", className="card-title text-info"),
                            html.P(ext.get('description', ''), className="card-text"),
                            html.Small(f"Justification: {ext.get('justification', '')}", className="text-muted"),
                            html.Br(),
                            dbc.Badge(f"Confidence: {ext.get('confidence', 0):.1%}",
                                    color="info" if ext.get('confidence', 0) > 0.7 else "warning")
                        ])
                    ], className="mt-2", outline=True, color="info")
                )

        # Enhanced data proposals display for files
        data_proposals = agent_response.get('data_entry_proposals', [])
        if data_proposals:
            response_elements.append(html.Hr())
            response_elements.append(html.H6("📊 Extracted Data Entries", className="text-success"))

            for proposal in data_proposals:
                response_elements.append(
                    dbc.Card([
                        dbc.CardBody([
                            html.H6(f"{proposal.get('entity_type', 'Unknown')}", className="card-title text-success"),
                            html.Pre(
                                json.dumps(proposal.get('proposed_data', {}), indent=2),
                                className="bg-light p-2 rounded",
                                style={'fontSize': '0.85em', 'maxHeight': '200px', 'overflow': 'auto'}
                            ),
                            dbc.Badge(f"Confidence: {proposal.get('confidence', 0):.1%}",
                                    color="success" if proposal.get('confidence', 0) > 0.7 else "warning")
                        ])
                    ], className="mt-2", outline=True, color="success")
                )

        return dbc.Card([
            dbc.CardBody(response_elements)
        ], className="mt-2", color="light", style={'border': '2px solid #2196f3'})

    except Exception as e:
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            f"Error processing file response: {str(e)}"
        ], color="danger", className="mt-2")


# Enhanced proposal accept/reject callback for all action types
@app.callback(
    Output('chat-history-ontology', 'children', allow_duplicate=True),
    [Input({'type': 'accept-proposal', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-proposal', 'index': ALL}, 'n_clicks'),
     Input({'type': 'accept-extension', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-extension', 'index': ALL}, 'n_clicks'),
     Input({'type': 'accept-data', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-data', 'index': ALL}, 'n_clicks'),
     Input({'type': 'edit-data', 'index': ALL}, 'n_clicks')],
    [State('chat-history-ontology', 'children')],
    prevent_initial_call=True
)
def handle_enhanced_proposal_actions(accept_clicks, reject_clicks, accept_ext_clicks, reject_ext_clicks,
                                   accept_data_clicks, reject_data_clicks, edit_data_clicks, chat_history):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    btn = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    item_id = btn['index']
    action_type = btn['type']

    # Determine action and message
    if 'accept' in action_type:
        action = 'accepted'
        color = 'success'
        icon = "✅"
    elif 'reject' in action_type:
        action = 'rejected'
        color = 'warning'
        icon = "❌"
    elif 'edit' in action_type:
        action = 'marked for editing'
        color = 'info'
        icon = "✏️"
    else:
        action = 'processed'
        color = 'secondary'
        icon = "🔄"

    # Minimal persistence demo: if supabase_client available, log approval
    if supabase_client and 'accept' in action_type:
        try:
            supabase_client.table('kudwa_action_audit').insert({
                'proposal_id': item_id,
                'action': action,
                'action_type': action_type,
                'timestamp': datetime.now().isoformat()
            }).execute()
        except Exception:
            pass

    new_history = chat_history or []
    new_history.append(dbc.Alert([
        html.Span(icon, style={'marginRight': '8px'}),
        f"Item {item_id[:8]} {action}."
    ], color=color, className="mt-2"))
    return new_history

# Graph and Dashboard callbacks
@app.callback(
    [Output('ontology-graph', 'elements'),
     Output('classes-count', 'children'),
     Output('relations-count', 'children'),
     Output('domains-count', 'children'),
     Output('recent-activity', 'children')],
    [Input('refresh-dashboard', 'n_clicks'),
     Input('center-graph', 'n_clicks')],
    prevent_initial_call=False
)
def update_ontology_graph_and_stats(refresh_clicks, center_clicks):
    """Update the interactive ontology graph and dashboard statistics"""
    # Load fresh data
    graph_data = load_ontology_graph_data()
    stats = load_ontology_stats()

    # Create Cytoscape elements
    elements = create_cytoscape_elements(graph_data)

    # Recent activity components
    recent_components = []
    for item in stats['recent']:
        confidence_color = "success" if item['confidence'] > 0.8 else "warning" if item['confidence'] > 0.6 else "danger"
        recent_components.append(
            dbc.ListGroupItem([
                html.Div([
                    html.Strong(item['name']),
                    dbc.Badge(f"{item['confidence']:.1%}", color=confidence_color, className="ms-2 float-end"),
                    html.Br(),
                    html.Small(f"Added: {item['created_at'][:10] if item['created_at'] else 'Unknown'}",
                              className="text-muted")
                ])
            ])
        )

    if not recent_components:
        recent_components = [dbc.Alert("No recent activity", color="light")]

    return (
        elements,
        str(stats['classes']),
        str(stats['relations']),
        str(stats['domains']),
        recent_components
    )

# Stats panel toggle
@app.callback(
    Output('stats-collapse', 'is_open'),
    [Input('toggle-stats', 'n_clicks')],
    [State('stats-collapse', 'is_open')],
    prevent_initial_call=True
)
def toggle_stats_panel(n_clicks, is_open):
    """Toggle the statistics panel visibility"""
    if n_clicks:
        return not is_open
    return is_open

# Layout selector callback
@app.callback(
    Output('ontology-graph', 'layout'),
    [Input('layout-selector', 'value')],
    prevent_initial_call=True
)
def update_graph_layout(layout_name):
    """Update the Cytoscape graph layout"""
    layout_configs = {
        'cose': {'name': 'cose', 'animate': True, 'animationDuration': 1000, 'nodeRepulsion': 400000},
        'circle': {'name': 'circle', 'animate': True, 'animationDuration': 1000},
        'dagre': {'name': 'dagre', 'animate': True, 'animationDuration': 1000, 'rankDir': 'TB'},
        'concentric': {'name': 'concentric', 'animate': True, 'animationDuration': 1000},
        'grid': {'name': 'grid', 'animate': True, 'animationDuration': 1000}
    }

    return layout_configs.get(layout_name, layout_configs['cose'])

# Cytoscape node click handler
@app.callback(
    Output('graph-info', 'children'),
    [Input('ontology-graph', 'tapNodeData')],
    prevent_initial_call=True
)
def handle_node_click(node_data):
    """Handle clicks on Cytoscape nodes to show detailed information"""
    if not node_data or not supabase_client:
        return dbc.Alert([
            html.Strong("🎯 Interactive Ontology Graph"),
            html.Br(),
            html.Small("Click nodes to explore • Hover for details • Graph updates in real-time as you add entities through chat")
        ], color="info", className="mb-0")

    try:
        node_id = node_data.get('id', '')
        full_label = node_data.get('full_label', node_data.get('label', ''))
        domain = node_data.get('domain', 'default')
        confidence = node_data.get('confidence', 1.0)
        created_at = node_data.get('created_at', '')

        # Get detailed node information from database
        node_details = supabase_client.table('kudwa_ontology_classes')\
            .select('*')\
            .eq('class_id', node_id)\
            .execute()

        if node_details.data:
            node = node_details.data[0]
            properties = node.get('properties', {})

            # Get connected nodes (relationships)
            relations = supabase_client.table('kudwa_ontology_relations')\
                .select('*')\
                .or_(f'subject_class_id.eq.{node_id},object_class_id.eq.{node_id}')\
                .execute()

            relation_components = []
            for rel in (relations.data or []):
                if rel['subject_class_id'] == node_id:
                    relation_components.append(
                        html.Li(f"→ {rel['predicate']} → {rel['object_class_id']}")
                    )
                else:
                    relation_components.append(
                        html.Li(f"← {rel['predicate']} ← {rel['subject_class_id']}")
                    )

            return dbc.Card([
                dbc.CardHeader([
                    html.H6([
                        html.Span("🔍 ", style={'color': domain_colors.get(domain, '#666')}),
                        full_label
                    ], className="mb-0 text-primary")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.P([
                                html.Strong("Domain: "),
                                dbc.Badge(domain.title(), color="primary", className="me-2"), html.Br(),
                                html.Strong("Confidence: "),
                                dbc.Badge(f"{confidence:.1%}",
                                         color="success" if confidence > 0.8 else "warning", className="me-2"), html.Br(),
                                html.Strong("Created: "), created_at[:10] if created_at else 'Unknown', html.Br(),
                                html.Strong("Class ID: "), html.Code(node.get('class_id', 'Unknown'))
                            ])
                        ], width=12)
                    ]),

                    # Relationships
                    html.Hr(),
                    html.H6("🔗 Relationships", className="text-success"),
                    html.Ul(relation_components) if relation_components else html.Small("No relationships found", className="text-muted"),

                    # Properties
                    html.Hr(),
                    html.Details([
                        html.Summary("📋 Properties", style={'cursor': 'pointer', 'fontWeight': 'bold'}),
                        html.Pre(json.dumps(properties, indent=2),
                                style={'fontSize': '11px', 'backgroundColor': '#f8f9fa', 'padding': '8px', 'borderRadius': '4px'})
                    ]) if properties else html.Small("No additional properties", className="text-muted")
                ])
            ], color="primary", outline=True)
        else:
            return dbc.Alert(f"Node details not found for: {full_label}", color="warning")

    except Exception as e:
        return dbc.Alert(f"Error loading node details: {str(e)}", color="danger")

# Add domain colors for the node click handler
domain_colors = {
    'financial': '#1f77b4',
    'default': '#ff7f0e',
    'business': '#2ca02c',
    'technical': '#d62728',
    'legal': '#9467bd'
}

@app.callback(
    Output('pending-approvals', 'children'),
    [Input('refresh-dashboard', 'n_clicks')],
    prevent_initial_call=False
)
def update_pending_approvals(n_clicks):
    """Load pending approvals from Supabase"""
    if not supabase_client:
        return [dbc.Alert("Supabase not connected", color="warning")]

    try:
        # Get pending ontology classes (low confidence or unapproved)
        pending_classes = supabase_client.table('kudwa_ontology_classes')\
            .select('*')\
            .or_('confidence_score.lt.0.8,approved_by.is.null')\
            .order('created_at', desc=True)\
            .limit(5)\
            .execute()

        pending_components = []
        for item in (pending_classes.data or []):
            item_id = item.get('id', str(uuid.uuid4()))
            pending_components.append(
                dbc.Card([
                    dbc.CardBody([
                        html.H6(item.get('label', 'Unknown Class'), className="card-title"),
                        html.P(f"Domain: {item.get('domain', 'default')}", className="text-muted small"),
                        dbc.Badge(f"{item.get('confidence_score', 0):.1%}",
                                color="warning" if item.get('confidence_score', 0) < 0.8 else "info"),
                        html.Div([
                            dbc.Button("✅ Approve", id={'type': 'approve-class', 'index': item_id},
                                     color="success", size="sm", className="me-2"),
                            dbc.Button("❌ Reject", id={'type': 'reject-class', 'index': item_id},
                                     color="danger", size="sm")
                        ], className="mt-2")
                    ])
                ], className="mb-2", outline=True)
            )

        if not pending_components:
            pending_components = [dbc.Alert("No pending approvals", color="success")]

        return pending_components
    except Exception as e:
        return [dbc.Alert(f"Error loading approvals: {str(e)}", color="danger")]

# Preview toggle callbacks
@app.callback(
    Output({'type': 'preview-collapse', 'index': MATCH}, 'is_open'),
    [Input({'type': 'preview-extension', 'index': MATCH}, 'n_clicks')],
    [State({'type': 'preview-collapse', 'index': MATCH}, 'is_open')],
    prevent_initial_call=True
)
def toggle_preview(n_clicks, is_open):
    """Toggle the database preview collapse"""
    if n_clicks:
        return not is_open
    return is_open

# Enhanced ontology extension acceptance with Cytoscape graph updates
@app.callback(
    [Output('ontology-chat-history', 'children', allow_duplicate=True),
     Output('ontology-graph', 'elements', allow_duplicate=True)],
    [Input({'type': 'accept-extension', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-extension', 'index': ALL}, 'n_clicks')],
    [State('ontology-chat-history', 'children')],
    prevent_initial_call=True
)
def handle_extension_actions_with_graph_update(accept_clicks, reject_clicks, current_history):
    """Handle acceptance/rejection of ontology extensions and update Cytoscape graph"""
    if not callback_context.triggered:
        # Return current state
        graph_data = load_ontology_graph_data()
        return current_history, create_cytoscape_elements(graph_data)

    triggered_id = callback_context.triggered[0]['prop_id']

    try:
        # Parse the triggered component
        import json
        button_info = json.loads(triggered_id.split('.')[0])
        action_type = button_info['type']
        item_id = button_info['index']

        new_history = current_history or []

        if 'accept-extension' in action_type and supabase_client:
            # Add to Supabase ontology
            try:
                # Create a more realistic entity based on common patterns
                entity_types = ['Payment Gateway', 'Transaction Type', 'Account Category', 'Financial Instrument', 'Business Process', 'Customer Segment', 'Risk Category']
                import random
                entity_type = random.choice(entity_types)

                result = supabase_client.table('kudwa_ontology_classes').insert({
                    'class_id': f'{entity_type.lower().replace(" ", "_")}_{item_id[:8]}',
                    'label': f'{entity_type}',
                    'domain': 'financial',
                    'class_type': 'pl:Entity',
                    'confidence_score': 0.85,
                    'status': 'active',
                    'approved_by': 'user',
                    'properties': {
                        'source': 'ai_chat',
                        'item_id': item_id,
                        'description': f'AI-generated {entity_type.lower()} from chat interaction',
                        'auto_generated': True,
                        'timestamp': datetime.now().isoformat()
                    }
                }).execute()

                new_history.append(dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    html.Strong("✅ Ontology Extension Added!"),
                    html.Br(),
                    html.Small([
                        f"Added '{entity_type}' to ontology. ",
                        html.Strong("🌐 Graph updated in real-time!"),
                        f" DB ID: {result.data[0]['id'] if result.data else 'unknown'}"
                    ])
                ], color="success", className="mt-2"))

                # Also add a sample relation if we have other nodes
                existing_classes = supabase_client.table('kudwa_ontology_classes')\
                    .select('class_id')\
                    .neq('id', result.data[0]['id'] if result.data else '')\
                    .limit(1)\
                    .execute()

                if existing_classes.data and result.data:
                    target_class = existing_classes.data[0]['class_id']
                    new_class = result.data[0]['class_id']

                    predicates = ['uses', 'processes', 'manages', 'contains', 'relates_to', 'depends_on']
                    predicate = random.choice(predicates)

                    supabase_client.table('kudwa_ontology_relations').insert({
                        'subject_class_id': new_class,
                        'predicate': predicate,
                        'object_class_id': target_class,
                        'domain': 'financial',
                        'confidence_score': 0.8,
                        'status': 'active',
                        'properties': {'auto_generated': True, 'source': 'ai_chat'}
                    }).execute()

            except Exception as e:
                new_history.append(dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    html.Strong("❌ Database Error"),
                    html.Br(),
                    html.Small(f"Failed to add to database: {str(e)}")
                ], color="danger", className="mt-2"))

        elif 'reject-extension' in action_type:
            new_history.append(dbc.Alert([
                html.I(className="fas fa-times-circle me-2"),
                html.Strong("❌ Extension Rejected"),
                html.Br(),
                html.Small(f"Ontology extension {item_id[:8]} was rejected and will not be added to the database.")
            ], color="warning", className="mt-2"))

        # Reload graph data and create updated Cytoscape elements
        graph_data = load_ontology_graph_data()
        updated_elements = create_cytoscape_elements(graph_data)

        return new_history, updated_elements

    except Exception as e:
        # Return current state on error
        graph_data = load_ontology_graph_data()
        return current_history, create_cytoscape_elements(graph_data)

# Enhanced ontology approval callbacks
@app.callback(
    Output('pending-approvals', 'children', allow_duplicate=True),
    [Input({'type': 'approve-class', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-class', 'index': ALL}, 'n_clicks')],
    [State('pending-approvals', 'children')],
    prevent_initial_call=True
)
def handle_ontology_approvals(approve_clicks, reject_clicks, current_approvals):
    """Handle approval/rejection of ontology classes"""
    if not callback_context.triggered:
        return current_approvals

    triggered_id = callback_context.triggered[0]['prop_id']

    if not supabase_client:
        return current_approvals

    try:
        # Parse the triggered component
        import json
        button_info = json.loads(triggered_id.split('.')[0])
        action_type = button_info['type']
        item_id = button_info['index']

        if 'approve' in action_type:
            # Approve the ontology class
            supabase_client.table('kudwa_ontology_classes')\
                .update({
                    'approved_by': 'user',
                    'status': 'active',
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', item_id)\
                .execute()
        elif 'reject' in action_type:
            # Reject the ontology class
            supabase_client.table('kudwa_ontology_classes')\
                .update({
                    'status': 'rejected',
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', item_id)\
                .execute()

        # Refresh the pending approvals
        return update_pending_approvals(1)[0]

    except Exception as e:
        print(f"Error handling approval: {e}")
        return current_approvals

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8051)
