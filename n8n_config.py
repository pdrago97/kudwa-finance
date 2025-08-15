"""
N8N Webhook Configuration for Kudwa Ontology Platform
Update these URLs with your actual N8N webhook endpoints
"""

import os
from typing import Dict, Any

# N8N Webhook URLs - HARDCODED FOR TESTING
N8N_WEBHOOKS = {
    # Ontology Extension Workflow - Using your test webhook
    'ontology_extension': {
        'url': 'https://n8n-moveup-u53084.vm.elestio.app/webhook-test/9ba11544-5c4e-4f91-818a-08a4ecb596c5',
        'description': 'Extends and adapts ontology based on documents and user context',
        'expected_payload': {
            'workflow_type': 'ontology_extension',
            'filename': 'string',
            'file_content': 'base64_string',
            'message': 'string',
            'timestamp': 'iso_string',
            'session_id': 'uuid_string'
        }
    },

    # Data Registration Workflow - Using same webhook for now
    'data_registration': {
        'url': 'https://n8n-moveup-u53084.vm.elestio.app/webhook-test/9ba11544-5c4e-4f91-818a-08a4ecb596c5',
        'description': 'Creates new records based on document RAG and user instructions',
        'expected_payload': {
            'workflow_type': 'data_registration',
            'filename': 'string',
            'file_content': 'base64_string',
            'message': 'string',
            'timestamp': 'iso_string',
            'session_id': 'uuid_string'
        }
    }
}

# N8N Instance Configuration
N8N_CONFIG = {
    'base_url': os.getenv('N8N_BASE_URL', 'https://your-n8n-instance.com'),
    'api_key': os.getenv('N8N_API_KEY', ''),  # If using API key authentication
    'x_api_key': os.getenv('N8N_X_API_KEY', ''),  # X-API-Key header authentication
    'basic_auth_user': os.getenv('N8N_BASIC_AUTH_USER', ''),  # Basic auth username
    'basic_auth_pass': os.getenv('N8N_BASIC_AUTH_PASS', ''),  # Basic auth password
    'timeout': int(os.getenv('N8N_TIMEOUT', '30')),  # Request timeout in seconds
    'retry_attempts': int(os.getenv('N8N_RETRY_ATTEMPTS', '3')),
    'retry_delay': int(os.getenv('N8N_RETRY_DELAY', '1'))  # Delay between retries in seconds
}

def get_webhook_url(workflow_type: str) -> str:
    """Get webhook URL for specific workflow type"""
    # Check if we should use local mock webhook for testing
    use_mock = os.getenv('USE_MOCK_WEBHOOK', 'false').lower() == 'true'

    if use_mock:
        mock_base_url = os.getenv('MOCK_WEBHOOK_URL', 'http://localhost:8052')
        return f"{mock_base_url}/webhook/{workflow_type.replace('_', '-')}"

    # Use configured N8N webhooks
    webhook_config = N8N_WEBHOOKS.get(workflow_type)
    if webhook_config:
        return webhook_config['url']
    raise ValueError(f"Unknown workflow type: {workflow_type}")

def get_webhook_config(workflow_type: str) -> Dict[str, Any]:
    """Get full webhook configuration for specific workflow type"""
    if workflow_type not in N8N_WEBHOOKS:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    return N8N_WEBHOOKS[workflow_type]

def get_auth_config() -> Dict[str, Any]:
    """Get authentication configuration for N8N requests"""
    auth_config = {}

    # Check for X-API-Key header (priority)
    if N8N_CONFIG['x_api_key']:
        auth_config['x_api_key'] = N8N_CONFIG['x_api_key']

    # Check for Basic Auth credentials
    elif N8N_CONFIG['basic_auth_user'] and N8N_CONFIG['basic_auth_pass']:
        auth_config['basic_auth'] = (N8N_CONFIG['basic_auth_user'], N8N_CONFIG['basic_auth_pass'])

    # Check for Bearer token API key
    elif N8N_CONFIG['api_key']:
        auth_config['api_key'] = N8N_CONFIG['api_key']

    return auth_config

def validate_payload(workflow_type: str, payload: Dict[str, Any]) -> bool:
    """Validate payload flexibly: ChatGPT-style validation.
    Rules:
    - Accept any payload structure - let the agent decide what to do
    - Only require that there's some content to process
    - Support nested body structure or flat structure
    """
    # Extract the actual data (handle both flat and nested structures)
    data = payload.get('body', payload)

    # Check if there's any meaningful content
    has_message = bool(data.get('message', '').strip())
    has_file = bool(data.get('file_content'))
    has_any_content = has_message or has_file or len(data) > 0

    if not has_any_content:
        print("Payload must include some content to process")
        return False

    # If there's a file, it should have a filename for context
    if has_file and not data.get('filename'):
        print("File uploads should include a filename for context")
        return False

    # All good - let the agent handle the semantics
    return True

# Environment setup instructions
SETUP_INSTRUCTIONS = """
To configure N8N webhooks:

1. Set environment variables:
   export N8N_ONTOLOGY_WEBHOOK="https://your-n8n-instance.com/webhook/your-ontology-webhook-id"
   export N8N_REGISTRATION_WEBHOOK="https://your-n8n-instance.com/webhook/your-registration-webhook-id"
   export N8N_BASE_URL="https://your-n8n-instance.com"
   export N8N_API_KEY="your-api-key-if-needed"

2. Or create a .env file with:
   N8N_ONTOLOGY_WEBHOOK=https://your-n8n-instance.com/webhook/your-ontology-webhook-id
   N8N_REGISTRATION_WEBHOOK=https://your-n8n-instance.com/webhook/your-registration-webhook-id
   N8N_BASE_URL=https://your-n8n-instance.com
   N8N_API_KEY=your-api-key-if-needed

3. Update the webhook IDs in your N8N workflows to match the URLs above
"""

if __name__ == "__main__":
    print("N8N Webhook Configuration")
    print("=" * 40)
    for workflow_type, config in N8N_WEBHOOKS.items():
        print(f"\n{workflow_type.upper()}:")
        print(f"  URL: {config['url']}")
        print(f"  Description: {config['description']}")
    
    print(f"\nSetup Instructions:")
    print(SETUP_INSTRUCTIONS)
