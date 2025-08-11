#!/usr/bin/env python3
"""
ADGM Corporate Agent - Startup Script
Easy deployment script with multiple interface options
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def check_requirements():
    """Check if required packages are installed"""
    try:
        import gradio
        import streamlit
        import openai
        import langchain
        import docx
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def check_api_key():
    """Check if OpenAI API key is configured"""
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  OpenAI API key not found!")
        print("📝 Please set OPENAI_API_KEY in your .env file")
        print("💡 Copy .env.example to .env and add your API key")
        return False
    
    print("✅ OpenAI API key configured")
    return True

def setup_directories():
    """Create necessary directories"""
    directories = [
        'data/adgm_knowledge_base',
        'data/vector_stores',
        'data/document_templates',
        'examples/input',
        'examples/output',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created")

def run_gradio_app(port=7860, share=False, debug=False):
    """Run the Gradio application"""
    print(f"🚀 Starting Gradio interface on port {port}")
    
    # Set environment variables
    os.environ['GRADIO_PORT'] = str(port)
    if debug:
        os.environ['DEBUG_MODE'] = 'True'
    
    try:
        # Import and run the app
        from app import main
        main()
    except KeyboardInterrupt:
        print("\n👋 Shutting down Gradio application")
    except Exception as e:
        print(f"❌ Error running Gradio app: {e}")

def run_streamlit_app(port=8501):
    """Run the Streamlit application"""
    print(f"🚀 Starting Streamlit interface on port {port}")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", str(port),
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n👋 Shutting down Streamlit application")
    except Exception as e:
        print(f"❌ Error running Streamlit app: {e}")

def run_cli_mode():
    """Run in CLI mode for testing"""
    print("🖥️  Running in CLI mode")
    
    try:
        from src.document_processor import EnhancedDocumentProcessor
        from src.rag_system import EnhancedRAGSystem
        
        # Initialize components
        processor = EnhancedDocumentProcessor()
        rag_system = EnhancedRAGSystem(os.getenv('OPENAI_API_KEY'))
        
        print("✅ Components initialized successfully")
        
        # Interactive CLI
        while True:
            print("\n" + "="*50)
            print("ADGM Corporate Agent - CLI Mode")
            print("="*50)
            print("1. Process a document")
            print("2. Ask ADGM question")
            print("3. Check knowledge base stats")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                file_path = input("Enter document path: ").strip()
                if os.path.exists(file_path):
                    try:
                        metadata, sections, analysis = processor.process_document(file_path)
                        print(f"\n✅ Document processed successfully!")
                        print(f"Document Type: {metadata.document_type}")
                        print(f"Confidence: {metadata.confidence_score:.2f}")
                        print(f"Sections: {len(sections)}")
                        print(f"Compliance Score: {analysis.get('overall_compliance_score', 0):.2f}")
                    except Exception as e:
                        print(f"❌ Error processing document: {e}")
                else:
                    print("❌ File not found")
            
            elif choice == '2':
                question = input("Enter your ADGM question: ").strip()
                if question:
                    try:
                        context = rag_system.retrieve_relevant_context(question)
                        response = rag_system.generate_response(question, context)
                        print(f"\n💡 Answer: {response.answer}")
                        print(f"Confidence: {response.confidence_score:.2f}")
                    except Exception as e:
                        print(f"❌ Error answering question: {e}")
            
            elif choice == '3':
                try:
                    stats = rag_system.get_knowledge_base_stats()
                    print(f"\n📊 Knowledge Base Stats:")
                    for key, value in stats.items():
                        print(f"  {key}: {value}")
                except Exception as e:
                    print(f"❌ Error getting stats: {e}")
            
            elif choice == '4':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")
    
    except Exception as e:
        print(f"❌ Error in CLI mode: {e}")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description='ADGM Corporate Agent - AI Legal Assistant')
    parser.add_argument('--interface', '-i', choices=['gradio', 'streamlit', 'cli'], 
                       default='gradio', help='Interface to use (default: gradio)')
    parser.add_argument('--port', '-p', type=int, default=None, 
                       help='Port number (default: 7860 for Gradio, 8501 for Streamlit)')
    parser.add_argument('--share', action='store_true', 
                       help='Create public sharing link (Gradio only)')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode')
    parser.add_argument('--setup-only', action='store_true',
                       help='Only setup directories and check requirements')
    
    args = parser.parse_args()
    
    print("🏛️  ADGM Corporate Agent - AI Legal Assistant")
    print("=" * 60)
    
    # Setup
    print("🔧 Setting up environment...")
    setup_directories()
    
    if not check_requirements():
        return 1
    
    if not check_api_key():
        return 1
    
    if args.setup_only:
        print("✅ Setup completed successfully!")
        return 0
    
    # Determine port
    if args.port is None:
        if args.interface == 'gradio':
            port = 7860
        elif args.interface == 'streamlit':
            port = 8501
        else:
            port = None
    else:
        port = args.port
    
    # Run selected interface
    try:
        if args.interface == 'gradio':
            run_gradio_app(port=port, share=args.share, debug=args.debug)
        elif args.interface == 'streamlit':
            run_streamlit_app(port=port)
        elif args.interface == 'cli':
            run_cli_mode()
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
