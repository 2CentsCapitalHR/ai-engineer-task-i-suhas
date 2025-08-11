#!/usr/bin/env python3
"""
Simple startup script for ADGM Corporate Agent
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def main():
    """Start the ADGM Corporate Agent"""
    
    # Load environment variables
    load_dotenv()
    
    # Get port from environment or use default
    port = os.getenv('STREAMLIT_PORT', '8501')
    
    print("ADGM Corporate Agent - Starting...")
    print(f"Server will run on: http://localhost:{port}")
    print("Upload .docx files for ADGM compliance analysis")
    print("Note: Works with or without OpenAI API key")
    print("-" * 50)
    
    try:
        # Run Streamlit
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.port', str(port),
            '--server.headless', 'true'
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down ADGM Corporate Agent...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
