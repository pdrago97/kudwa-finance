#!/usr/bin/env python3
"""
Start the Kudwa Isolated Chat Dashboard
Clean interface with separate N8N workflows
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # Check N8N webhook URL (ontology only)
    ontology_webhook = os.getenv('N8N_ONTOLOGY_WEBHOOK')
    if not ontology_webhook or 'your-n8n-instance' in ontology_webhook:
        print("⚠️  N8N_ONTOLOGY_WEBHOOK not configured")
        print("   Set: export N8N_ONTOLOGY_WEBHOOK='https://your-n8n-instance.com/webhook/your-webhook-id'")
    else:
        print(f"✅ Ontology webhook: {ontology_webhook}")
    print()

def main():
    """Main function to start the dashboard"""
    print("🧠 Kudwa - Isolated Chat Dashboard")
    print("=" * 50)
    
    check_environment()
    
    print("🚀 Starting dashboard...")
    print("📍 Dashboard will be available at: http://localhost:8051")
    print("💡 Features:")
    print("   • 🧠 Ontology Extension Chat (Purple)")
    print("   • 🔗 Direct N8N webhook integration")
    print("   • 📁 Optional file upload")
    print("   • 💬 Simple, single chat context")
    print()
    
    try:
        # Import and run the dashboard
        from isolated_chat_dashboard import app
        app.run(debug=True, host='0.0.0.0', port=8051)
    except ImportError as e:
        print(f"❌ Error importing dashboard: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install dash dash-bootstrap-components requests python-dotenv")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
