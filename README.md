[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/vgbm4cZ0)

# 🏛️ ADGM Corporate Agent - AI Legal Assistant
### Prerequisites
- Python 3.9 or higher
- Virtual environment (recommended)

### Installation & Setup


# Clone the repository
git clone <repository-url>
cd TASK-AI

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (optional - fallback system available)

# Run the application
streamlit run streamlit_app.py --server.port 8501

### Docker Setup (Alternative)
```bash
# Build and run with Docker
docker-compose up -d
```

## ✨ Key Features

### 🔍 **Document Analysis**
- **Smart Document Recognition**: Automatically identifies ADGM document types
- **Compliance Checking**: Validates against ADGM regulations
- **Red Flag Detection**: Identifies legal inconsistencies and issues
- **Section Analysis**: Detailed breakdown of document sections

### 🤖 **AI-Powered Intelligence**
- **Fallback System**: Works without OpenAI API using rule-based responses
- **OpenAI Integration**: Enhanced analysis when API key is available
- **Natural Language Q&A**: Ask questions about ADGM compliance
- **Context-Aware Responses**: Tailored advice based on document content

### 📊 **Analytics & Reporting**
- **Compliance Scoring**: Quantitative assessment of document compliance
- **Risk Assessment**: Identifies and prioritizes legal risks
- **Visual Dashboards**: Interactive charts and insights
- **Export Options**: Download analysis results
