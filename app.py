"""
ADGM Corporate Agent - Main Application
Enhanced AI-powered legal assistant for ADGM compliance with advanced features
"""

import os
import json
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging

import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Import custom modules
from src.document_processor import EnhancedDocumentProcessor, DocumentMetadata, DocumentSection
from src.rag_system import EnhancedRAGSystem, RAGResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ADGMCorporateAgent:
    """Main application class for ADGM Corporate Agent"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize components
        self.document_processor = EnhancedDocumentProcessor()
        self.rag_system = EnhancedRAGSystem(self.openai_api_key)
        
        # Application state
        self.current_session = {
            'documents': {},
            'analysis_results': {},
            'compliance_reports': {},
            'session_id': self._generate_session_id()
        }
        
        # Supported document types
        self.supported_document_types = {
            'Articles of Association': 'articles_of_association',
            'Memorandum of Association': 'memorandum_of_association',
            'UBO Declaration Form': 'ubo_declaration',
            'Board Resolution': 'board_resolution',
            'Incorporation Application': 'incorporation_application',
            'Register of Members': 'register_of_members',
            'Register of Directors': 'register_of_directors',
            'Shareholder Resolution': 'shareholder_resolution'
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def process_uploaded_documents(self, files: List[str]) -> Tuple[str, str, str]:
        """Process uploaded documents and return analysis results"""
        try:
            if not files:
                return "No files uploaded", "", ""
            
            results = []
            total_issues = 0
            total_compliance_score = 0
            processed_docs = 0
            
            for file_path in files:
                try:
                    # Process document
                    metadata, sections, analysis = self.document_processor.process_document(file_path)
                    
                    # Store in session
                    doc_id = f"doc_{processed_docs + 1}"
                    self.current_session['documents'][doc_id] = {
                        'metadata': metadata,
                        'sections': sections,
                        'analysis': analysis,
                        'file_path': file_path
                    }
                    
                    # Simple compliance check
                    compliance_score = analysis.get('overall_compliance_score', 0)
                    issues_count = analysis.get('critical_issues_count', 0)
                    
                    # Store compliance results
                    self.current_session['compliance_reports'][doc_id] = {
                        'compliance_score': compliance_score,
                        'issues_count': issues_count
                    }
                    
                    # Accumulate statistics
                    total_issues += issues_count
                    total_compliance_score += compliance_score
                    processed_docs += 1
                    
                    # Add to results
                    results.append({
                        'document': metadata.filename,
                        'type': metadata.document_type,
                        'confidence': metadata.confidence_score,
                        'compliance_score': compliance_score,
                        'issues_count': issues_count
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    results.append({
                        'document': os.path.basename(file_path),
                        'type': 'Error',
                        'confidence': 0,
                        'compliance_score': 0,
                        'issues_count': 0,
                        'error': str(e)
                    })
            
            # Generate summary
            avg_compliance = total_compliance_score / processed_docs if processed_docs > 0 else 0
            
            summary = f"""
## Document Processing Summary

**Documents Processed:** {processed_docs}
**Average Compliance Score:** {avg_compliance:.2f}/1.0
**Total Issues Found:** {total_issues}
**Session ID:** {self.current_session['session_id']}

### Document Details:
"""
            
            for result in results:
                if 'error' not in result:
                    summary += f"""
- **{result['document']}**
  - Type: {result['type']} (Confidence: {result['confidence']:.2f})
  - Compliance Score: {result['compliance_score']:.2f}
  - Issues: {result['issues_count']}
"""
                else:
                    summary += f"""
- **{result['document']}** - ERROR: {result['error']}
"""
            
            # Generate detailed analysis
            detailed_analysis = self._generate_detailed_analysis()
            
            # Generate recommendations
            recommendations = self._generate_recommendations()
            
            return summary, detailed_analysis, recommendations
            
        except Exception as e:
            logger.error(f"Error in document processing: {str(e)}")
            return f"Error processing documents: {str(e)}", "", ""
    
    def _generate_detailed_analysis(self) -> str:
        """Generate detailed analysis of all processed documents"""
        if not self.current_session['documents']:
            return "No documents processed yet."
        
        analysis = "## Detailed Document Analysis\n\n"
        
        for doc_id, doc_data in self.current_session['documents'].items():
            metadata = doc_data['metadata']
            sections = doc_data['sections']
            compliance_data = self.current_session['compliance_reports'][doc_id]
            
            analysis += f"### {metadata.filename}\n\n"
            analysis += f"**Document Type:** {metadata.document_type}\n"
            analysis += f"**Word Count:** {metadata.word_count}\n"
            analysis += f"**Sections:** {len(sections)}\n"
            analysis += f"**Compliance Score:** {compliance_data['compliance_score']:.2f}\n\n"
            
            # Section analysis
            if sections:
                analysis += "**Section Analysis:**\n"
                for section in sections[:5]:  # Show first 5 sections
                    analysis += f"- {section.title}: {section.compliance_status} ({section.legal_importance})\n"
                if len(sections) > 5:
                    analysis += f"- ... and {len(sections) - 5} more sections\n"
                analysis += "\n"
            
            # Issues
            if compliance_data['issues_count'] > 0:
                analysis += f"**Issues Found:** {compliance_data['issues_count']}\n\n"
            
            analysis += "---\n\n"
        
        return analysis
    
    def _generate_recommendations(self) -> str:
        """Generate overall recommendations based on analysis"""
        if not self.current_session['documents']:
            return "No documents processed yet."
        
        recommendations = "## Recommendations\n\n"
        
        # Collect all compliance scores
        all_compliance_scores = []
        total_issues = 0
        
        for doc_id, doc_data in self.current_session['documents'].items():
            compliance_data = self.current_session['compliance_reports'][doc_id]
            all_compliance_scores.append(compliance_data['compliance_score'])
            total_issues += compliance_data['issues_count']
        
        # Priority recommendations
        recommendations += "### Priority Actions\n\n"
        
        # Issues
        if total_issues > 0:
            recommendations += f"1. **Address {total_issues} Issues Found**\n"
            recommendations += "   - Review all flagged sections for compliance\n\n"
        
        # Compliance score
        avg_compliance = sum(all_compliance_scores) / len(all_compliance_scores) if all_compliance_scores else 0
        if avg_compliance < 0.7:
            recommendations += "2. **Improve Overall Compliance**\n"
            recommendations += "   - Current average compliance score is below recommended threshold\n"
            recommendations += "   - Focus on jurisdiction clauses and required sections\n\n"
        
        # Document completeness
        doc_types = [doc_data['metadata'].document_type for doc_data in self.current_session['documents'].values()]
        required_docs = ['Articles of Association', 'Memorandum of Association', 'UBO Declaration Form']
        missing_docs = [doc for doc in required_docs if doc not in doc_types]
        
        if missing_docs:
            recommendations += "3. **Complete Required Documents**\n"
            recommendations += f"   - Missing: {', '.join(missing_docs)}\n\n"
        
        # General recommendations
        recommendations += "### General Recommendations\n\n"
        recommendations += "- Ensure all jurisdiction clauses specify ADGM Courts\n"
        recommendations += "- Verify all documents are signed and dated\n"
        recommendations += "- Review beneficial ownership declarations for completeness\n"
        recommendations += "- Confirm registered office address is within ADGM\n"
        
        return recommendations
    
    def ask_adgm_question(self, question: str) -> str:
        """Answer ADGM-related questions using RAG system"""
        try:
            if not question.strip():
                return "Please enter a question about ADGM compliance or regulations."
            
            # Retrieve relevant context
            context = self.rag_system.retrieve_relevant_context(question, k=5)
            
            if not context:
                return "I couldn't find relevant information in the ADGM knowledge base. Please try rephrasing your question."
            
            # Generate response
            response = self.rag_system.generate_response(question, context)
            
            # Format response
            formatted_response = f"""
## {question}

**Answer:** {response.answer}

**Confidence:** {response.confidence_score:.2f}

**ADGM References:**
{chr(10).join(f"- {ref}" for ref in response.adgm_references) if response.adgm_references else "- No specific references found"}

**Related Topics:**
{chr(10).join(f"- {topic}" for topic in response.related_topics) if response.related_topics else "- None identified"}

**Sources Used:**
{chr(10).join(f"- {source.source} (Relevance: {source.relevance_score:.2f})" for source in response.sources[:3]) if response.sources else "- No sources available"}
"""
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error answering ADGM question: {str(e)}")
            return f"Error processing question: {str(e)}"
    
    def generate_analytics_dashboard(self) -> Tuple[str, str]:
        """Generate analytics dashboard for current session"""
        try:
            if not self.current_session['documents']:
                return "No documents processed yet.", ""
            
            # Generate analytics
            analytics = self.analytics_engine.generate_analytics_dashboard(self.current_session)
            insights = self.analytics_engine.generate_insights(self.current_session)
            
            # Format analytics display
            analytics_text = "## Analytics Dashboard\n\n"
            
            # Summary stats
            summary = analytics.get('summary_stats', {})
            analytics_text += f"**Total Documents:** {summary.get('total_documents', 0)}\n"
            analytics_text += f"**Average Compliance Score:** {summary.get('average_compliance_score', 0):.2f}\n"
            analytics_text += f"**Total Issues:** {summary.get('total_issues', 0)}\n"
            analytics_text += f"**Critical Issues:** {summary.get('critical_issues', 0)}\n\n"
            
            # Document type distribution
            doc_types = analytics.get('document_type_distribution', {}).get('document_type_counts', {})
            if doc_types:
                analytics_text += "**Document Types:**\n"
                for doc_type, count in doc_types.items():
                    analytics_text += f"- {doc_type}: {count}\n"
                analytics_text += "\n"
            
            # Issue analysis
            issue_analysis = analytics.get('issue_analysis', {})
            severity_dist = issue_analysis.get('severity_distribution', {})
            if any(severity_dist.values()):
                analytics_text += "**Issues by Severity:**\n"
                for severity, count in severity_dist.items():
                    if count > 0:
                        analytics_text += f"- {severity.title()}: {count}\n"
                analytics_text += "\n"
            
            # Performance metrics
            performance = analytics.get('performance_metrics', {})
            if performance:
                analytics_text += "**Performance Metrics:**\n"
                analytics_text += f"- Quality Score: {performance.get('quality_score', 0):.2f}\n"
                analytics_text += f"- Compliance Rate: {performance.get('compliance_rate', 0):.2f}\n"
                analytics_text += f"- High Confidence Rate: {performance.get('high_confidence_rate', 0):.2f}\n\n"
            
            # Insights
            insights_text = "## Key Insights\n\n"
            if insights:
                for insight in insights:
                    insights_text += f"- {insight}\n"
            else:
                insights_text += "No specific insights generated.\n"
            
            return analytics_text, insights_text
            
        except Exception as e:
            logger.error(f"Error generating analytics dashboard: {str(e)}")
            return f"Error generating analytics: {str(e)}", ""
    
    def export_results(self, export_format: str = 'zip') -> Tuple[str, str]:
        """Export analysis results in specified format"""
        try:
            if not self.current_session['documents']:
                return "", "No documents to export"
            
            # Export using export manager
            file_path, message = self.export_manager.export_processed_documents(
                self.current_session, export_format
            )
            
            return file_path, message
            
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
            return "", f"Export failed: {str(e)}"

def create_gradio_interface():
    """Create the Gradio interface for the ADGM Corporate Agent"""
    
    # Initialize the agent
    try:
        agent = ADGMCorporateAgent()
    except ValueError as e:
        # Create a dummy interface if API key is missing
        def missing_api_key():
            return "Error: OpenAI API key not found. Please set OPENAI_API_KEY in your .env file."
        
        interface = gr.Interface(
            fn=missing_api_key,
            inputs=[],
            outputs=gr.Textbox(label="Error"),
            title="ADGM Corporate Agent - Configuration Required"
        )
        return interface
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .feature-box {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9fafb;
    }
    """
    
    with gr.Blocks(css=custom_css, title="ADGM Corporate Agent") as interface:
        
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>🏛️ ADGM Corporate Agent</h1>
            <p>AI-Powered Legal Assistant for Abu Dhabi Global Market Compliance</p>
        </div>
        """)
        
        # Main tabs
        with gr.Tabs():
            
            # Document Processing Tab
            with gr.TabItem("📄 Document Processing"):
                gr.Markdown("## Upload and Process Legal Documents")
                gr.Markdown("Upload your ADGM legal documents for comprehensive analysis and compliance checking.")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        file_upload = gr.File(
                            label="Upload Documents (.docx files)",
                            file_count="multiple",
                            file_types=[".docx"]
                        )
                        
                        process_btn = gr.Button("🔍 Process Documents", variant="primary", size="lg")
                        
                        gr.Markdown("### Supported Document Types:")
                        gr.Markdown("""
                        - Articles of Association
                        - Memorandum of Association  
                        - UBO Declaration Form
                        - Board Resolutions
                        - Incorporation Applications
                        - Register of Members/Directors in docs
                        """)
                    
                    with gr.Column(scale=3):
                        processing_summary = gr.Textbox(
                            label="Processing Summary",
                            lines=10,
                            placeholder="Upload documents and click 'Process Documents' to see results..."
                        )
                
                with gr.Row():
                    detailed_analysis = gr.Textbox(
                        label="Detailed Analysis",
                        lines=15,
                        placeholder="Detailed analysis will appear here..."
                    )
                    
                    recommendations = gr.Textbox(
                        label="Recommendations",
                        lines=15,
                        placeholder="Recommendations will appear here..."
                    )
                
                # Process button action
                process_btn.click(
                    fn=agent.process_uploaded_documents,
                    inputs=[file_upload],
                    outputs=[processing_summary, detailed_analysis, recommendations]
                )
            
            # ADGM Q&A Tab
            with gr.TabItem("❓ ADGM Q&A"):
                gr.Markdown("## Ask Questions About ADGM Regulations")
                gr.Markdown("Get expert answers about ADGM compliance, regulations, and legal requirements.")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        question_input = gr.Textbox(
                            label="Your Question",
                            placeholder="e.g., What are the requirements for Articles of Association in ADGM?",
                            lines=3
                        )
                        
                        ask_btn = gr.Button("🤔 Ask Question", variant="primary")
                        
                        gr.Markdown("### Example Questions:")
                        gr.Markdown("""
                        - What documents are required for ADGM incorporation?
                        - How should jurisdiction clauses be written?
                        - What are the beneficial ownership requirements?
                        - What are the director appointment requirements?
                        """)
                    
                    with gr.Column(scale=3):
                        answer_output = gr.Textbox(
                            label="Answer",
                            lines=20,
                            placeholder="Ask a question to get expert ADGM guidance..."
                        )
                
                # Ask button action
                ask_btn.click(
                    fn=agent.ask_adgm_question,
                    inputs=[question_input],
                    outputs=[answer_output]
                )
            
            # Analytics Tab
            with gr.TabItem("📊 Analytics"):
                gr.Markdown("## Document Analysis Dashboard")
                gr.Markdown("View comprehensive analytics and insights from your document processing session.")
                
                analytics_btn = gr.Button("📈 Generate Analytics", variant="primary")
                
                with gr.Row():
                    analytics_display = gr.Textbox(
                        label="Analytics Dashboard",
                        lines=15,
                        placeholder="Click 'Generate Analytics' to view dashboard..."
                    )
                    
                    insights_display = gr.Textbox(
                        label="Key Insights",
                        lines=15,
                        placeholder="Insights will appear here..."
                    )
                
                # Analytics button action
                analytics_btn.click(
                    fn=agent.generate_analytics_dashboard,
                    inputs=[],
                    outputs=[analytics_display, insights_display]
                )
            
            # Export Tab
            with gr.TabItem("💾 Export"):
                gr.Markdown("## Export Analysis Results")
                gr.Markdown("Download your processed documents with comments and comprehensive reports.")
                
                with gr.Row():
                    with gr.Column():
                        export_format = gr.Dropdown(
                            choices=["zip", "json", "xlsx"],
                            value="zip",
                            label="Export Format"
                        )
                        
                        export_btn = gr.Button("📥 Export Results", variant="primary")
                        
                        export_status = gr.Textbox(
                            label="Export Status",
                            lines=3,
                            placeholder="Export status will appear here..."
                        )
                    
                    with gr.Column():
                        download_file = gr.File(
                            label="Download File",
                            visible=True
                        )
                        
                        gr.Markdown("### Export Includes:")
                        gr.Markdown("""
                        - **ZIP**: All documents with comments + reports
                        - **JSON**: Structured analysis data
                        - **XLSX**: Excel summary reports
                        """)
                
                # Export button action
                def export_with_file_output(format_choice):
                    file_path, message = agent.export_results(format_choice)
                    return message, file_path if file_path else None
                
                export_btn.click(
                    fn=export_with_file_output,
                    inputs=[export_format],
                    outputs=[export_status, download_file]
                )
            
            # Help Tab
            with gr.TabItem("ℹ️ Help"):
                gr.Markdown("## How to Use ADGM Corporate Agent")
                
                with gr.Accordion("🚀 Getting Started", open=True):
                    gr.Markdown("""
                    1. **Upload Documents**: Go to the Document Processing tab and upload your .docx files
                    2. **Process**: Click "Process Documents" to analyze for ADGM compliance
                    3. **Review**: Check the analysis results and recommendations
                    4. **Ask Questions**: Use the Q&A tab for specific ADGM guidance
                    5. **Export**: Download your results with comments and reports
                    """)
                
                with gr.Accordion("📋 Supported Documents"):
                    gr.Markdown("""
                    - **Articles of Association**: Company constitution and governance
                    - **Memorandum of Association**: Company objects and structure  
                    - **UBO Declaration**: Beneficial ownership information
                    - **Board Resolutions**: Director decisions and appointments
                    - **Incorporation Applications**: Company registration forms
                    - **Registers**: Members and directors information
                    """)
                
                with gr.Accordion("🔍 What We Check"):
                    gr.Markdown("""
                    - **Jurisdiction Compliance**: ADGM vs UAE references
                    - **Required Sections**: Mandatory clauses and provisions
                    - **Legal Language**: Ambiguous or non-binding terms
                    - **Formatting**: Professional legal document structure
                    - **Signatures**: Execution and witnessing requirements
                    - **ADGM Regulations**: Compliance with current laws
                    """)
                
                with gr.Accordion("⚠️ Important Notes"):
                    gr.Markdown("""
                    - This tool provides assistance only and does not constitute legal advice
                    - Always consult qualified legal professionals for official matters
                    - Ensure you have the latest ADGM regulation updates
                    - Review all suggestions before implementing changes
                    - Keep backups of your original documents
                    """)
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f3f4f6; border-radius: 10px;">
            <p><strong>ADGM Corporate Agent</strong> - AI-Powered Legal Compliance Assistant</p>
            <p style="font-size: 0.9em; color: #6b7280;">
                Built with advanced AI for Abu Dhabi Global Market compliance • 
                Always consult legal professionals for official advice
            </p>
        </div>
        """)
    
    return interface

def main():
    """Main function to run the application"""
    try:
        # Create and launch the Gradio interface
        interface = create_gradio_interface()
        
        # Launch configuration
        launch_config = {
            'server_name': '0.0.0.0',  # Allow external access
            'server_port': int(os.getenv('GRADIO_PORT', 7860)),
            'share': False,  # Set to True for public sharing
            'debug': os.getenv('DEBUG_MODE', 'False').lower() == 'true',
            'show_error': True,
            'quiet': False
        }
        
        print("🚀 Starting ADGM Corporate Agent...")
        print(f"📍 Access the application at: http://localhost:{launch_config['server_port']}")
        print("📚 Upload your ADGM legal documents for AI-powered compliance analysis")
        
        interface.launch(**launch_config)
        
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        print(f"❌ Failed to start application: {str(e)}")
        print("💡 Make sure you have set OPENAI_API_KEY in your .env file")

if __name__ == "__main__":
    main()
