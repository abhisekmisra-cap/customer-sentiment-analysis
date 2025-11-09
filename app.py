"""
Customer Comment Analyzer - Streamlit Web Application (MCP Version)
--------------------------------------------------------------------
A user-friendly web interface using Model Context Protocol for AI analysis.
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


def setup_mcp_client():
    """Initialize the MCP client connection"""
    try:
        with st.spinner("🔄 Connecting to MCP server and initializing AI model... This may take a moment..."):
            # Get the path to mcp_server.py in mcp_integration directory
            server_path = Path(__file__).parent / "mcp_integration" / "mcp_server.py"
            client = SimpleMCPClient(server_script_path=str(server_path))
            client.connect()
            st.session_state.mcp_client = client
            st.session_state.client_connected = True
            return True
    except Exception as e:
        st.error(f"❌ Error connecting to MCP server: {str(e)}")
        st.info("💡 Make sure HUGGINGFACEHUB_API_TOKEN is set in environment variables.")
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
    st.markdown('<p class="sub-header">Powered by LangChain, Hugging Face AI & Model Context Protocol</p>', unsafe_allow_html=True)
    
    # Sidebar for model status
    with st.sidebar:
        st.header("🤖 Model Status")
        
        # Check environment variable
        hf_token_env = os.environ.get("HUGGINGFACEHUB_API_TOKEN", "")
        
        # Show connection status or token input
        if not st.session_state.client_connected:
            st.info("💡 **To connect to the MCP server, you need to provide your Hugging Face API token.**")
            st.markdown("[Get your free token here](https://huggingface.co/settings/tokens)")
            
            # Token input
            hf_token = st.text_input(
                "Hugging Face API Token",
                type="password",
                value=hf_token_env,
                placeholder="Enter your token here...",
                help="Your token is required to initialize the AI model"
            )
            
            # Set token in environment if provided
            if hf_token and hf_token != hf_token_env:
                os.environ["HUGGINGFACEHUB_API_TOKEN"] = hf_token
            
            # Connect button
            if hf_token or hf_token_env:
                if st.button("🚀 Connect to MCP Server", type="primary"):
                    if setup_mcp_client():
                        st.success("✅ Connected to MCP server!")
                        st.rerun()
            else:
                st.warning("⚠️ Please enter your Hugging Face API token above to continue.")
        else:
            st.success("✅ MCP server is connected!")
            if st.button("🔌 Disconnect"):
                if st.session_state.mcp_client:
                    st.session_state.mcp_client.disconnect()
                st.session_state.mcp_client = None
                st.session_state.client_connected = False
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
        - **Hugging Face** Mistral-7B model
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
