#!/usr/bin/env python3
"""
Kudwa - Isolated Chat Dashboard
Clean, modern interface with separate workflows for N8N integration
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context, ALL
import dash_bootstrap_components as dbc
import requests
from requests.auth import HTTPBasicAuth
import json
import base64
import os
from datetime import datetime
import uuid
import time
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
    
    # Two-Column Layout for Isolated Chats
    dbc.Row([
        # Ontology Extension Chat
        dbc.Col([
            create_chat_interface(
                chat_type='ontology',
                title='🧠 Ontology Extension',
                description='Extend and adapt your ontology based on new documents and requirements',
                icon='🧠',
                color='#6f42c1'
            )
        ], width=12)
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
    
    # Handle file upload
    if trigger_id == 'upload-ontology' and upload_contents:
        try:
            content_type, content_string = upload_contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Send to N8N webhook - let agent decide how to handle the file
            webhook_data = {
                'body': {
                    'message': f"Analyze this uploaded file: {upload_filename}",
                    'filename': upload_filename,
                    'file_content': content_string,
                    'timestamp': datetime.now().isoformat()
                },
                'chatId': str(uuid.uuid4())
            }

            # Send to actual N8N webhook
            webhook_response = send_to_n8n_webhook('ontology_extension', webhook_data)
            upload_status = create_webhook_response_display(webhook_response)
            
            # Add to chat history
            new_history.append(html.Div([
                html.Strong("📁 System: ", style={'color': '#6f42c1'}),
                html.Span(f"Uploaded {upload_filename} for ontology analysis")
            ], className="mb-2 p-2", style={'backgroundColor': '#f8f9fa', 'borderRadius': '8px'}))
            
        except Exception as e:
            upload_status = dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Error uploading file: {str(e)}"
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
            ai_response = f"🧠 Processing your request: '{chat_input}'. The AI agent is analyzing this and will provide ontology recommendations..."
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

# Accept/Reject proposal persistence (minimal demo)
@app.callback(
    Output('chat-history-ontology', 'children', allow_duplicate=True),
    [Input({'type': 'accept-proposal', 'index': ALL}, 'n_clicks'),
     Input({'type': 'reject-proposal', 'index': ALL}, 'n_clicks')],
    [State('chat-history-ontology', 'children')],
    prevent_initial_call=True
)
def handle_proposal_accept_reject(accept_clicks, reject_clicks, chat_history):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
    btn = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    pid = btn['index']
    action = 'accepted' if btn['type'] == 'accept-proposal' else 'rejected'

    # Minimal persistence demo: if supabase_client available, log approval
    if supabase_client and action == 'accepted':
        try:
            supabase_client.table('kudwa_action_audit').insert({
                'proposal_id': pid,
                'action': action,
                'timestamp': datetime.now().isoformat()
            }).execute()
        except Exception:
            pass

    new_history = chat_history or []
    new_history.append(dbc.Alert(f"Proposal {pid[:8]} {action}.", color='success' if action=='accepted' else 'warning'))
    return new_history

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8051)
