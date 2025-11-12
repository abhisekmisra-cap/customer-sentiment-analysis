"""
Customer Comment Analyzer - Streamlit Web Application (MCP Version)
--------------------------------------------------------------------
A user-friendly web interface using Model Context Protocol for AI analysis.
Uses Azure OpenAI for LLM operations.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add mcp_integration directory to path
mcp_dir = Path(__file__).parent / "mcp_integration"
sys.path.insert(0, str(mcp_dir))

from mcp_client import SimpleMCPClient
from sample_comments import get_comments_by_category
import os
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="Customer Comment Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .negative {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .neutral {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'mcp_client' not in st.session_state:
        st.session_state.mcp_client = None
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'client_connected' not in st.session_state:
        st.session_state.client_connected = False
    if 'azure_endpoint' not in st.session_state:
        st.session_state.azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    if 'azure_api_key' not in st.session_state:
        st.session_state.azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    if 'azure_deployment' not in st.session_state:
        st.session_state.azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1")
    if 'azure_timeout' not in st.session_state:
        # default timeout in seconds for MCP server init and tool calls
        st.session_state.azure_timeout = int(os.environ.get("MCP_DEFAULT_TIMEOUT", "120"))
    if 'mcp_stderr_logs' not in st.session_state:
        st.session_state.mcp_stderr_logs = []


def setup_mcp_client():
    """Initialize the MCP client connection"""
    try:
        with st.spinner("🔄 Connecting to MCP server and initializing AI model... This may take a moment..."):
            # Set environment variables for MCP server
            os.environ["AZURE_OPENAI_ENDPOINT"] = st.session_state.azure_endpoint
            os.environ["AZURE_OPENAI_API_KEY"] = st.session_state.azure_api_key
            os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = st.session_state.azure_deployment
            
            # Get the path to mcp_server.py in mcp_integration directory
            server_path = Path(__file__).parent / "mcp_integration" / "mcp_server.py"
            client = SimpleMCPClient(server_script_path=str(server_path))
            
            # Set up stderr callback to capture logs for UI display
            def capture_stderr(line):
                if 'mcp_stderr_logs' in st.session_state:
                    st.session_state.mcp_stderr_logs.append(line)
                    # Keep only last 100 lines to avoid memory issues
                    if len(st.session_state.mcp_stderr_logs) > 100:
                        st.session_state.mcp_stderr_logs = st.session_state.mcp_stderr_logs[-100:]
            
            client.stderr_callback = capture_stderr
            
            # Apply user-selected timeout to MCP client
            try:
                client.default_timeout = int(st.session_state.azure_timeout)
            except Exception:
                client.default_timeout = client.default_timeout

            client.connect()
            st.session_state.mcp_client = client
            st.session_state.client_connected = True
            return True
    except Exception as e:
        st.error(f"❌ Error connecting to MCP server: {str(e)}")
        st.info("💡 Make sure Azure OpenAI credentials are correct.")
        return False


def display_result(result, index):
    """Display a single analysis result with styling"""
    sentiment = result['sentiment'].lower()
    sentiment_class = sentiment if sentiment in ['positive', 'negative', 'neutral'] else 'neutral'
    
    # Emoji mapping
    category_emoji = {
        'TRAVEL': '✈️',
        'ACCOMMODATION': '🏨',
        'FOOD': '🍽️'
    }
    sentiment_emoji = {
        'POSITIVE': '😊',
        'NEGATIVE': '😞',
        'NEUTRAL': '😐'
    }
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown(f"**Comment {index}:** {result['comment']}")
    with col2:
        st.markdown(f"{category_emoji.get(result['category'], '❓')} **{result['category']}**")
    with col3:
        st.markdown(f"{sentiment_emoji.get(result['sentiment'], '😐')} **{result['sentiment']}**")
    
    st.markdown("---")


def display_statistics(results):
    """Display statistics dashboard"""
    if not results:
        return
    
    # Use MCP client to calculate statistics
    if st.session_state.mcp_client:
        try:
            stats = st.session_state.mcp_client.get_statistics(results)
            
            st.subheader("📊 Analysis Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Category Distribution")
                category_data = []
                for category, data in stats.get('category_distribution', {}).items():
                    category_data.append({
                        'Category': category,
                        'Count': data['count'],
                        'Percentage': data['percentage']
                    })
                
                if category_data:
                    category_df = pd.DataFrame(category_data)
                    st.dataframe(category_df, hide_index=True, use_container_width=True)
                    st.bar_chart(category_df.set_index('Category')['Count'])
            
            with col2:
                st.markdown("### Sentiment Distribution")
                sentiment_data = []
                for sentiment, data in stats.get('sentiment_distribution', {}).items():
                    sentiment_data.append({
                        'Sentiment': sentiment,
                        'Count': data['count'],
                        'Percentage': data['percentage']
                    })
                
                if sentiment_data:
                    sentiment_df = pd.DataFrame(sentiment_data)
                    st.dataframe(sentiment_df, hide_index=True, use_container_width=True)
                    st.bar_chart(sentiment_df.set_index('Sentiment')['Count'])
        
        except Exception as e:
            st.error(f"Error calculating statistics: {str(e)}")


def export_results(results):
    """Export results to CSV"""
    if not results:
        return None
    
    df = pd.DataFrame(results)
    csv = df.to_csv(index=False)
    return csv


def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Customer Comment Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Powered by LangChain, Azure OpenAI & Model Context Protocol</p>', unsafe_allow_html=True)
    
    # Sidebar for model status
    with st.sidebar:
        st.header("🤖 Azure OpenAI Configuration")
        
        # Show connection status or credential inputs
        if not st.session_state.client_connected:
            st.info("💡 **Configure Azure OpenAI credentials to connect to the MCP server.**")
            
            # Azure OpenAI Endpoint
            azure_endpoint = st.text_input(
                "Azure OpenAI Endpoint",
                value=st.session_state.azure_endpoint,
                placeholder="https://your-resource.openai.azure.com/",
                help="Your Azure OpenAI endpoint URL"
            )
            
            # Azure OpenAI API Key
            azure_api_key = st.text_input(
                "Azure OpenAI API Key",
                type="password",
                value=st.session_state.azure_api_key,
                placeholder="Enter your API key here...",
                help="Your Azure OpenAI API key"
            )
            
            # Azure OpenAI Deployment Name
            azure_deployment = st.text_input(
                "Deployment Name",
                value=st.session_state.azure_deployment,
                placeholder="gpt-4.1",
                help="Your Azure OpenAI deployment name (e.g., gpt-4.1, gpt-4o-mini, etc.)"
            )

            # Timeout for MCP server init / tool calls
            st.session_state.azure_timeout = st.number_input(
                "MCP Timeout (seconds)",
                min_value=30,
                max_value=900,
                value=st.session_state.azure_timeout,
                help="How long to wait for MCP server initialization and tool responses (increase if you get timeouts)."
            )
            
            # Update session state
            st.session_state.azure_endpoint = azure_endpoint
            st.session_state.azure_api_key = azure_api_key
            st.session_state.azure_deployment = azure_deployment
            
            # Update session state
            st.session_state.azure_endpoint = azure_endpoint
            st.session_state.azure_api_key = azure_api_key
            st.session_state.azure_deployment = azure_deployment
            
            # Test Azure OpenAI connection directly (without MCP)
            if azure_endpoint and azure_api_key and azure_deployment:
                if st.button("🧪 Test Azure OpenAI Direct", help="Test direct connection to Azure OpenAI without MCP to isolate issues"):
                    with st.spinner("Testing direct Azure OpenAI connection..."):
                        try:
                            from openai import AzureOpenAI
                            test_client = AzureOpenAI(
                                azure_endpoint=azure_endpoint,
                                api_key=azure_api_key,
                                api_version="2024-02-15-preview"
                            )
                            response = test_client.chat.completions.create(
                                model=azure_deployment,
                                messages=[{"role": "user", "content": "Say 'test successful'"}],
                                max_tokens=10
                            )
                            st.success(f"✅ Direct Azure OpenAI test passed! Response: {response.choices[0].message.content}")
                        except Exception as e:
                            st.error(f"❌ Direct Azure OpenAI test failed: {str(e)}")
                            st.info("💡 This means the issue is with your Azure credentials/deployment, not MCP.")
            
            # Connect button
            if azure_endpoint and azure_api_key and azure_deployment:
                if st.button("🚀 Connect to MCP Server", type="primary"):
                    if setup_mcp_client():
                        st.success("✅ Connected to MCP server!")
                        st.rerun()
            else:
                st.warning("⚠️ Please fill in all Azure OpenAI credentials above to continue.")
        else:
            st.success("✅ MCP server is connected!")
            
            # Show current configuration
            with st.expander("📋 Current Configuration"):
                st.text(f"Endpoint: {st.session_state.azure_endpoint}")
                st.text(f"Deployment: {st.session_state.azure_deployment}")
                st.text(f"API Key: {'*' * 20}")
                st.text(f"Timeout: {st.session_state.azure_timeout}s")
            
            # Show MCP server logs for debugging
            with st.expander("🔍 MCP Server Logs (last 50 stderr lines)", expanded=False):
                if st.session_state.mcp_stderr_logs:
                    log_text = "\n".join(st.session_state.mcp_stderr_logs[-50:])
                    st.text_area("Server Logs", value=log_text, height=200, disabled=True)
                else:
                    st.info("No stderr logs captured yet. Logs appear here when the MCP server outputs errors.")
            
            if st.button("🔌 Disconnect"):
                if st.session_state.mcp_client:
                    st.session_state.mcp_client.disconnect()
                st.session_state.mcp_client = None
                st.session_state.client_connected = False
                st.session_state.mcp_stderr_logs = []
                st.rerun()
        
        st.markdown("---")
        
        # Sample comments
        st.header("📝 Sample Comments")
        st.info("💡 Sample comments will be loaded in the **Batch Analysis** tab")
        
        if st.button("Load Travel Comments"):
            comments = get_comments_by_category('travel')[:5]
            st.session_state.sample_comments = "\n\n".join(comments)
        
        if st.button("Load Accommodation Comments"):
            comments = get_comments_by_category('accommodation')[:5]
            st.session_state.sample_comments = "\n\n".join(comments)
        
        if st.button("Load Food Comments"):
            comments = get_comments_by_category('food')[:5]
            st.session_state.sample_comments = "\n\n".join(comments)
        
        if st.button("Load Mixed Comments"):
            comments = get_comments_by_category('mixed')[:5]
            st.session_state.sample_comments = "\n\n".join(comments)
        
        st.markdown("---")
        
        # About section
        st.header("ℹ️ About")
        st.markdown("""
        This application uses:
        - **Model Context Protocol** for service communication
        - **LangChain** for LLM orchestration
        - **Azure OpenAI** GPT-4 model
        - **AI Classification** for category detection
        - **Sentiment Analysis** for emotion detection
        """)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📝 Single Comment", "📋 Batch Analysis", "📈 History"])
    
    # Tab 1: Single Comment Analysis
    with tab1:
        st.header("Analyze a Single Comment")
        
        single_comment = st.text_area(
            "Enter customer comment:",
            height=100,
            placeholder="Type or paste a customer comment here...",
            help="Enter a comment about travel, accommodation, or food service"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            analyze_single = st.button("🔍 Analyze Comment", type="primary", disabled=not st.session_state.client_connected)
        
        with col2:
            clear_single = st.button("🗑️ Clear")
        
        if clear_single:
            st.rerun()
        
        if analyze_single and single_comment.strip():
            with st.spinner("🤔 Analyzing comment via MCP..."):
                try:
                    result = st.session_state.mcp_client.analyze_comment(single_comment)
                    
                    # Display result
                    st.success("✅ Analysis Complete!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Category", result['category'])
                    with col2:
                        st.metric("Sentiment", result['sentiment'])
                    
                    # Add to history
                    result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.analysis_history.append(result)
                    
                except Exception as e:
                    st.error(f"❌ Error analyzing comment: {str(e)}")
    
    # Tab 2: Batch Analysis
    with tab2:
        st.header("Analyze Multiple Comments")
        
        # Check if sample comments were loaded
        default_text = st.session_state.get('sample_comments', '')
        
        batch_comments = st.text_area(
            "Enter comments (one per line or separated by blank lines):",
            height=300,
            value=default_text,
            placeholder="Enter multiple comments, each on a new line or separated by blank lines...",
            help="You can load sample comments from the sidebar"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            analyze_batch = st.button("🔍 Analyze All", type="primary", disabled=not st.session_state.client_connected)
        
        with col2:
            clear_batch = st.button("🗑️ Clear All")
        
        if clear_batch:
            st.session_state.sample_comments = ''
            st.rerun()
        
        if analyze_batch and batch_comments.strip():
            # Parse comments
            comments = [c.strip() for c in batch_comments.split('\n') if c.strip()]
            
            if comments:
                with st.spinner(f"🤔 Analyzing {len(comments)} comments via MCP..."):
                    try:
                        progress_bar = st.progress(0)
                        
                        # Analyze all comments via MCP
                        results = st.session_state.mcp_client.analyze_batch(comments)
                        
                        # Add timestamps
                        for result in results:
                            result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        progress_bar.progress(1.0)
                        
                        st.session_state.results = results
                        st.session_state.analysis_history.extend(results)
                        
                        st.success(f"✅ Analyzed {len(comments)} comments!")
                        
                        # Display results
                        st.subheader("📋 Analysis Results")
                        for i, result in enumerate(results, 1):
                            display_result(result, i)
                        
                        # Display statistics
                        display_statistics(results)
                        
                        # Export option
                        csv_data = export_results(results)
                        if csv_data:
                            st.download_button(
                                label="📥 Download Results (CSV)",
                                data=csv_data,
                                file_name=f"comment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Error analyzing comments: {str(e)}")
    
    # Tab 3: History
    with tab3:
        st.header("📈 Analysis History")
        
        if st.session_state.analysis_history:
            st.info(f"Total analyses performed: {len(st.session_state.analysis_history)}")
            
            # Display history as dataframe
            history_df = pd.DataFrame(st.session_state.analysis_history)
            st.dataframe(history_df, use_container_width=True, hide_index=True)
            
            # Statistics for all history
            display_statistics(st.session_state.analysis_history)
            
            # Export history
            csv_data = export_results(st.session_state.analysis_history)
            if csv_data:
                st.download_button(
                    label="📥 Download Full History (CSV)",
                    data=csv_data,
                    file_name=f"full_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Clear history
            if st.button("🗑️ Clear History"):
                st.session_state.analysis_history = []
                st.session_state.results = []
                st.rerun()
        else:
            st.info("No analysis history yet. Start analyzing comments to see history here!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            Made with ❤️ using <strong>Model Context Protocol</strong>, <strong>LangChain</strong>, 
            <strong>Hugging Face</strong>, and <strong>Streamlit</strong>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
