#!/usr/bin/env python3
"""
Setup script for ADGM Corporate Agent
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        'data/adgm_knowledge_base',
        'data/document_templates', 
        'data/vector_store',
        'examples/input',
        'examples/output',
        'logs',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment file"""
    env_file = Path('.env')
    
    if not env_file.exists():
        # Copy from example
        example_file = Path('.env.example')
        if example_file.exists():
            with open(example_file, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✓ Created .env file from template")
        else:
            # Create basic .env file
            with open(env_file, 'w') as f:
                f.write("""# OpenAI Configuration
OPENAI_API_KEY=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
MODEL_NAME=gpt-4
EMBEDDING_MODEL=text-embedding-ada-002

# Application Configuration
DEBUG=True
MAX_FILE_SIZE=10485760
SUPPORTED_FORMATS=.docx,.doc

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=4000
TEMPERATURE=0.1

# ADGM Knowledge Base
KNOWLEDGE_BASE_PATH=./data/adgm_knowledge_base/
VECTOR_STORE_PATH=./data/vector_store/
""")
            print("✓ Created basic .env file")
    else:
        print("✓ .env file already exists")

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    
    print(f"✓ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def main():
    """Main setup function"""
    print("ADGM Corporate Agent - Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    print("\nCreating directories...")
    create_directories()
    
    # Setup environment
    print("\nSetting up environment...")
    setup_environment()
    
    # Install dependencies
    print("\nInstalling dependencies...")
    if not install_dependencies():
        return 1
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python test_system.py")
    print("3. Run: python app.py")
    print("\nFor more information, see README.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
