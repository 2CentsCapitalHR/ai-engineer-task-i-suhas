"""
Streamlit Alternative for ADGM Corporate Agent
Simple web interface using Streamlit
"""

import streamlit as st
import os
import tempfile
from datetime import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from src.document_processor import EnhancedDocumentProcessor
try:
    from src.rag_system import EnhancedRAGSystem
except Exception as e:
    st.warning("⚠️ OpenAI API not available. Using fallback system.")
    from src.rag_system_fallback import FallbackRAGSystem as EnhancedRAGSystem
from src.compliance_checker import ComplianceChecker
from src.red_flag_detector import RedFlagDetector
from src.analytics_engine import AnalyticsEngine
from src.export_manager import ExportManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="ADGM Corporate Agent",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
    }
    .feature-box {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9fafb;
    }
    .success-box {
        background-color: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #fee2e2;
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    try:
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
            st.stop()
        
        # Initialize components
        st.session_state.document_processor = EnhancedDocumentProcessor()
        st.session_state.rag_system = EnhancedRAGSystem(os.getenv('OPENAI_API_KEY'))
        st.session_state.compliance_checker = ComplianceChecker()
        st.session_state.red_flag_detector = RedFlagDetector()
        st.session_state.analytics_engine = AnalyticsEngine()
        st.session_state.export_manager = ExportManager()
        
        # Session data
        st.session_state.documents = {}
        st.session_state.compliance_reports = {}
        st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        st.session_state.agent = True
        
    except Exception as e:
        st.error(f"❌ Error initializing application: {str(e)}")
        st.stop()

# Header
st.markdown("""
<div class="main-header">
    <h1>🏛️ ADGM Corporate Agent</h1>
    <p>AI-Powered Legal Assistant for Abu Dhabi Global Market Compliance</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 Navigation")
    
    page = st.selectbox(
        "Choose a function:",
        ["📄 Document Processing", "❓ ADGM Q&A", "📊 Analytics", "💾 Export", "ℹ️ Help"]
    )
    
    st.markdown("---")
    
    # Session info
    st.subheader("📊 Session Info")
    st.write(f"**Session ID:** {st.session_state.session_id}")
    st.write(f"**Documents Processed:** {len(st.session_state.documents)}")
    
    if st.session_state.documents:
        total_issues = sum(len(report.get('red_flags', [])) 
                          for report in st.session_state.compliance_reports.values())
        st.write(f"**Total Issues:** {total_issues}")

# Main content based on selected page
if page == "📄 Document Processing":
    st.header("📄 Document Processing")
    st.markdown("Upload your ADGM legal documents for comprehensive analysis and compliance checking.")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose DOCX files",
        type=['docx'],
        accept_multiple_files=True,
        help="Upload one or more .docx files for analysis"
    )
    
    if uploaded_files:
        if st.button("🔍 Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                try:
                    # Save uploaded files temporarily
                    temp_files = []
                    for uploaded_file in uploaded_files:
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
                        temp_file.write(uploaded_file.read())
                        temp_file.close()
                        temp_files.append(temp_file.name)
                    
                    # Process documents
                    results = []
                    for i, temp_file in enumerate(temp_files):
                        try:
                            # Process document
                            metadata, sections, analysis = st.session_state.document_processor.process_document(temp_file)
                            
                            # Store in session
                            doc_id = f"doc_{i + 1}"
                            st.session_state.documents[doc_id] = {
                                'metadata': metadata,
                                'sections': sections,
                                'analysis': analysis,
                                'file_path': temp_file
                            }
                            
                            # Perform compliance check
                            compliance_report = st.session_state.compliance_checker.check_compliance(
                                metadata, sections, analysis
                            )
                            
                            # Detect red flags
                            red_flags = st.session_state.red_flag_detector.detect_red_flags(
                                metadata, sections, analysis
                            )
                            
                            # Store compliance results
                            st.session_state.compliance_reports[doc_id] = {
                                'compliance_report': compliance_report,
                                'red_flags': red_flags
                            }
                            
                            results.append({
                                'filename': uploaded_files[i].name,
                                'doc_type': metadata.document_type,
                                'confidence': metadata.confidence_score,
                                'compliance_score': compliance_report.get('overall_score', 0),
                                'issues_count': len(red_flags),
                                'critical_issues': sum(1 for flag in red_flags if flag.get('severity') == 'critical')
                            })
                            
                        except Exception as e:
                            st.error(f"Error processing {uploaded_files[i].name}: {str(e)}")
                    
                    # Display results
                    if results:
                        st.success(f"✅ Successfully processed {len(results)} documents!")
                        
                        # Summary table
                        st.subheader("📊 Processing Summary")
                        import pandas as pd
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True)
                        
                        # Detailed analysis
                        st.subheader("🔍 Detailed Analysis")
                        
                        for i, result in enumerate(results):
                            with st.expander(f"📄 {result['filename']}"):
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Document Type", result['doc_type'])
                                    st.metric("Confidence", f"{result['confidence']:.2f}")
                                
                                with col2:
                                    st.metric("Compliance Score", f"{result['compliance_score']:.2f}")
                                    st.metric("Total Issues", result['issues_count'])
                                
                                with col3:
                                    st.metric("Critical Issues", result['critical_issues'])
                                
                                # Show red flags
                                doc_id = f"doc_{i + 1}"
                                red_flags = st.session_state.compliance_reports[doc_id]['red_flags']
                                
                                if red_flags:
                                    st.write("**Issues Found:**")
                                    for flag in red_flags[:5]:  # Show first 5 issues
                                        severity_color = {
                                            'critical': '🔴',
                                            'high': '🟠', 
                                            'medium': '🟡',
                                            'low': '🟢'
                                        }.get(flag.get('severity', 'low'), '⚪')
                                        
                                        st.write(f"{severity_color} **{flag.get('description', 'Unknown issue')}**")
                                        st.write(f"   📍 Location: {flag.get('location', 'Unknown')}")
                                        st.write(f"   💡 Suggestion: {flag.get('suggestion', 'No suggestion')}")
                                        st.write("")
                                
                                else:
                                    st.success("✅ No issues found in this document!")
                    
                    # Clean up temp files
                    for temp_file in temp_files:
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                            
                except Exception as e:
                    st.error(f"❌ Error processing documents: {str(e)}")

elif page == "❓ ADGM Q&A":
    st.header("❓ ADGM Q&A")
    st.markdown("Get expert answers about ADGM compliance, regulations, and legal requirements.")
    
    # Question input
    question = st.text_area(
        "Your Question:",
        placeholder="e.g., What are the requirements for Articles of Association in ADGM?",
        height=100
    )
    
    if st.button("🤔 Ask Question", type="primary"):
        if question.strip():
            with st.spinner("Searching ADGM knowledge base..."):
                try:
                    # Retrieve relevant context
                    context = st.session_state.rag_system.retrieve_relevant_context(question, k=5)
                    
                    if not context:
                        st.warning("⚠️ No relevant information found. Please try rephrasing your question.")
                    else:
                        # Generate response
                        response = st.session_state.rag_system.generate_response(question, context)
                        
                        # Display answer
                        st.subheader("💡 Answer")
                        st.write(response.answer)
                        
                        # Display metadata
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Confidence Score", f"{response.confidence_score:.2f}")
                            
                            if response.adgm_references:
                                st.subheader("📚 ADGM References")
                                for ref in response.adgm_references:
                                    st.write(f"• {ref}")
                        
                        with col2:
                            if response.related_topics:
                                st.subheader("🔗 Related Topics")
                                for topic in response.related_topics:
                                    st.write(f"• {topic}")
                            
                            if response.follow_up_questions:
                                st.subheader("❓ Follow-up Questions")
                                for q in response.follow_up_questions:
                                    st.write(f"• {q}")
                        
                        # Display sources
                        if response.sources:
                            with st.expander("📖 Sources Used"):
                                for source in response.sources:
                                    st.write(f"**{source.source}** (Relevance: {source.relevance_score:.2f})")
                                    st.write(f"Section: {source.section}")
                                    st.write(f"Reference: {source.adgm_reference}")
                                    st.write("---")
                
                except Exception as e:
                    st.error(f"❌ Error processing question: {str(e)}")
        else:
            st.warning("⚠️ Please enter a question.")
    
    # Example questions
    st.subheader("💡 Example Questions")
    example_questions = [
        "What documents are required for ADGM incorporation?",
        "How should jurisdiction clauses be written for ADGM companies?",
        "What are the beneficial ownership requirements in ADGM?",
        "What are the director appointment requirements?",
        "How should the registered office be specified?"
    ]
    
    for eq in example_questions:
        if st.button(eq, key=f"example_{eq[:20]}"):
            st.session_state.example_question = eq
            st.experimental_rerun()

elif page == "📊 Analytics":
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.documents:
        st.info("📋 No documents processed yet. Go to Document Processing to upload and analyze documents.")
    else:
        if st.button("📈 Generate Analytics", type="primary"):
            with st.spinner("Generating analytics..."):
                try:
                    # Prepare session data
                    session_data = {
                        'documents': st.session_state.documents,
                        'compliance_reports': st.session_state.compliance_reports,
                        'session_id': st.session_state.session_id
                    }
                    
                    # Generate analytics
                    analytics = st.session_state.analytics_engine.generate_analytics_dashboard(session_data)
                    insights = st.session_state.analytics_engine.generate_insights(session_data)
                    
                    # Display summary stats
                    st.subheader("📊 Summary Statistics")
                    summary = analytics.get('summary_stats', {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Documents", summary.get('total_documents', 0))
                    with col2:
                        st.metric("Avg Compliance", f"{summary.get('average_compliance_score', 0):.2f}")
                    with col3:
                        st.metric("Total Issues", summary.get('total_issues', 0))
                    with col4:
                        st.metric("Critical Issues", summary.get('critical_issues', 0))
                    
                    # Document type distribution
                    st.subheader("📄 Document Types")
                    doc_types = analytics.get('document_type_distribution', {}).get('document_type_counts', {})
                    if doc_types:
                        import plotly.express as px
                        fig = px.pie(values=list(doc_types.values()), names=list(doc_types.keys()), 
                                   title="Document Type Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Issue analysis
                    st.subheader("⚠️ Issue Analysis")
                    issue_analysis = analytics.get('issue_analysis', {})
                    severity_dist = issue_analysis.get('severity_distribution', {})
                    
                    if any(severity_dist.values()):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Severity distribution
                            fig = px.bar(x=list(severity_dist.keys()), y=list(severity_dist.values()),
                                       title="Issues by Severity", color=list(severity_dist.keys()))
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Risk level
                            risk_level = issue_analysis.get('risk_level', 'Low')
                            risk_score = issue_analysis.get('risk_score', 0)
                            
                            st.metric("Risk Level", risk_level)
                            st.metric("Risk Score", risk_score)
                    
                    # Insights
                    st.subheader("💡 Key Insights")
                    if insights:
                        for insight in insights:
                            st.write(f"• {insight}")
                    else:
                        st.info("No specific insights generated.")
                
                except Exception as e:
                    st.error(f"❌ Error generating analytics: {str(e)}")

elif page == "💾 Export":
    st.header("💾 Export Results")
    
    if not st.session_state.documents:
        st.info("📋 No documents to export. Process some documents first.")
    else:
        st.markdown("Download your processed documents with comments and comprehensive reports.")
        
        # Export format selection
        export_format = st.selectbox(
            "Choose Export Format:",
            ["zip", "json", "xlsx"],
            help="ZIP includes all files, JSON provides structured data, XLSX creates Excel reports"
        )
        
        if st.button("📥 Export Results", type="primary"):
            with st.spinner("Preparing export..."):
                try:
                    # Prepare session data
                    session_data = {
                        'documents': st.session_state.documents,
                        'compliance_reports': st.session_state.compliance_reports,
                        'session_id': st.session_state.session_id
                    }
                    
                    # Export using export manager
                    file_path, message = st.session_state.export_manager.export_processed_documents(
                        session_data, export_format
                    )
                    
                    if file_path and os.path.exists(file_path):
                        st.success(f"✅ {message}")
                        
                        # Provide download
                        with open(file_path, 'rb') as f:
                            st.download_button(
                                label=f"📥 Download {export_format.upper()} File",
                                data=f.read(),
                                file_name=os.path.basename(file_path),
                                mime='application/octet-stream'
                            )
                    else:
                        st.error(f"❌ Export failed: {message}")
                
                except Exception as e:
                    st.error(f"❌ Export error: {str(e)}")
        
        # Export information
        st.subheader("📋 Export Contents")
        
        if export_format == "zip":
            st.markdown("""
            **ZIP Package includes:**
            - 📄 Original documents with inline comments
            - 📊 JSON analysis report
            - 📈 Excel summary report  
            - ✅ Compliance checklist
            """)
        elif export_format == "json":
            st.markdown("""
            **JSON Report includes:**
            - 📋 Document metadata and analysis
            - ⚠️ All issues and red flags
            - 📊 Compliance scores and statistics
            - 💡 Recommendations and insights
            """)
        elif export_format == "xlsx":
            st.markdown("""
            **Excel Report includes:**
            - 📊 Document summary sheet
            - ⚠️ Issues detail sheet
            - ✅ Section compliance sheet
            - 📈 Analytics dashboard
            """)

elif page == "ℹ️ Help":
    st.header("ℹ️ Help & Documentation")
    
    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
        1. **Upload Documents**: Go to Document Processing and upload your .docx files
        2. **Process**: Click "Process Documents" to analyze for ADGM compliance  
        3. **Review**: Check analysis results and recommendations
        4. **Ask Questions**: Use Q&A tab for specific ADGM guidance
        5. **Export**: Download results with comments and reports
        """)
    
    with st.expander("📋 Supported Documents"):
        st.markdown("""
        - **Articles of Association**: Company constitution and governance
        - **Memorandum of Association**: Company objects and structure
        - **UBO Declaration**: Beneficial ownership information  
        - **Board Resolutions**: Director decisions and appointments
        - **Incorporation Applications**: Company registration forms
        - **Registers**: Members and directors information
        """)
    
    with st.expander("🔍 What We Check"):
        st.markdown("""
        - **Jurisdiction Compliance**: ADGM vs UAE references
        - **Required Sections**: Mandatory clauses and provisions
        - **Legal Language**: Ambiguous or non-binding terms
        - **Formatting**: Professional legal document structure
        - **Signatures**: Execution and witnessing requirements
        - **ADGM Regulations**: Compliance with current laws
        """)
    
    with st.expander("⚠️ Important Disclaimers"):
        st.markdown("""
        - This tool provides assistance only and does not constitute legal advice
        - Always consult qualified legal professionals for official matters
        - Ensure you have the latest ADGM regulation updates
        - Review all suggestions before implementing changes
        - Keep backups of your original documents
        """)
    
    # Contact and support
    st.subheader("📞 Support")
    st.markdown("""
    For technical support or questions about ADGM Corporate Agent:
    - 📧 Check the documentation in the repository
    - 🐛 Report issues on GitHub
    - 💡 Suggest improvements or new features
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; font-size: 0.9em;">
    <strong>ADGM Corporate Agent</strong> - AI-Powered Legal Compliance Assistant<br>
    Built with advanced AI for Abu Dhabi Global Market compliance • Always consult legal professionals for official advice
</div>
""", unsafe_allow_html=True)
