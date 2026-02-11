"""
Streamlit UI for LLM-Powered Data Analyst Chatbot
Main user interface with tabs and sidebar chatbot
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import json
import plotly.express as px
import plotly.graph_objects as go

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.analysis.data_loader import DataLoader
from src.analysis.eda_engine import EDAEngine
from src.analysis.insight_generator import InsightGenerator
from src.powerbi.metadata_parser import PowerBIMetadataParser
from src.chatbot.chatbot_engine import DataAnalystChatbot

# Page configuration
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .insight-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'eda_complete' not in st.session_state:
        st.session_state.eda_complete = False
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'insights' not in st.session_state:
        st.session_state.insights = []
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'eda_results' not in st.session_state:
        st.session_state.eda_results = {}
    if 'powerbi_metadata' not in st.session_state:
        st.session_state.powerbi_metadata = {}
    if 'metadata' not in st.session_state:
        st.session_state.metadata = {}
    if 'dashboard_context' not in st.session_state:
        st.session_state.dashboard_context = {}


def update_chatbot_context():
    """Update chatbot with latest context"""
    if st.session_state.chatbot is not None:
        st.session_state.chatbot.load_context(
            eda_results=st.session_state.eda_results,
            insights=st.session_state.insights,
            powerbi_metadata=st.session_state.powerbi_metadata
        )


def sidebar_chatbot():
    """Chatbot in sidebar - always visible"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 💬 AI Data Analyst")
    
    # Initialize chatbot on first run
    if st.session_state.chatbot is None:
        st.session_state.chatbot = DataAnalystChatbot(use_mock=True)
        if st.session_state.eda_complete:
            update_chatbot_context()
    
    # Check if analysis is complete
    if not st.session_state.eda_complete:
        st.sidebar.info("💡 Upload data and run analysis to activate chatbot")
        return
    
    # Chat input
    user_question = st.sidebar.text_input(
        "Ask a question:",
        placeholder="What are the key trends?",
        key="chat_input"
    )
    
    col1, col2 = st.sidebar.columns([1, 1])
    with col1:
        send_button = st.sidebar.button("Send", type="primary", use_container_width=True)
    with col2:
        clear_button = st.sidebar.button("Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.chat_history = []
        st.session_state.chatbot.reset_conversation()
        st.rerun()
    
    if send_button and user_question:
        # Update context before answering
        update_chatbot_context()
        
        # Get chatbot response
        response = st.session_state.chatbot.chat(user_question)
        
        # Add to history
        st.session_state.chat_history.append({
            'question': user_question,
            'answer': response
        })
        st.rerun()
    
    # Display chat history
    if st.session_state.chat_history:
        st.sidebar.markdown("### Chat History")
        
        # Show only last 5 messages
        for turn in reversed(st.session_state.chat_history[-5:]):
            st.sidebar.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {turn['question']}
            </div>
            """, unsafe_allow_html=True)
            
            st.sidebar.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>AI:</strong> {turn['answer']}
            </div>
            """, unsafe_allow_html=True)


def upload_tab():
    """Tab 1: Upload data and Power BI metadata"""
    st.markdown("### 📁 Upload Your Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Dataset Upload")
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            key="dataset_upload"
        )
        
        if uploaded_file is not None:
            try:
                # Load data
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file)
                else:
                    data = pd.read_excel(uploaded_file)
                
                st.session_state.data = data
                st.session_state.data_loaded = True
                
                # Generate metadata
                loader = DataLoader()
                loader.data = data
                loader._generate_metadata()
                st.session_state.metadata = loader.metadata
                
                st.success(f"✅ Loaded: {len(data)} rows, {len(data.columns)} columns")
                
                # Data preview
                st.markdown("#### Data Preview")
                st.dataframe(data.head(10), use_container_width=True)
                
                # Metadata
                with st.expander("📊 Dataset Information"):
                    mcol1, mcol2, mcol3 = st.columns(3)
                    with mcol1:
                        st.metric("Rows", len(data))
                    with mcol2:
                        st.metric("Columns", len(data.columns))
                    with mcol3:
                        st.metric("Numeric Cols", len(st.session_state.metadata['numeric_columns']))
                    
                    st.write("**Columns:**", ", ".join(data.columns.tolist()))
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.markdown("#### Power BI Metadata Upload")
        uploaded_metadata = st.file_uploader(
            "Upload Power BI metadata JSON (optional)",
            type=['json'],
            key="powerbi_upload"
        )
        
        if uploaded_metadata is not None:
            try:
                metadata = json.load(uploaded_metadata)
                st.session_state.powerbi_metadata = metadata
                
                st.success("✅ Power BI metadata loaded")
                
                # Display KPI summary
                kpis = metadata.get('kpis', [])
                st.markdown(f"**KPIs Found:** {len(kpis)}")
                
                if kpis:
                    st.markdown("#### KPI Summary")
                    for kpi in kpis[:5]:
                        trend = kpi.get('trend', {})
                        trend_symbol = "📈" if trend.get('direction') == 'increasing' else "📉"
                        st.write(f"{trend_symbol} **{kpi['name']}**: {kpi.get('value', 'N/A')}")
                
                # Update chatbot context
                if st.session_state.chatbot:
                    update_chatbot_context()
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


def analysis_tab():
    """Tab 2: Run EDA and view insights"""
    st.markdown("### 🔍 Automated Data Analysis")
    
    if not st.session_state.data_loaded:
        st.warning("⚠️ Please upload data first in the Upload tab")
        return
    
    # Run analysis button
    if st.button("🚀 Run Full Analysis", type="primary", use_container_width=False):
        with st.spinner("Running comprehensive analysis..."):
            # Run EDA
            eda_engine = EDAEngine(st.session_state.data)
            eda_results = eda_engine.run_full_analysis()
            st.session_state.eda_results = eda_results
            
            # Generate insights
            insight_gen = InsightGenerator(eda_results)
            insights = insight_gen.generate_all_insights()
            st.session_state.insights = insights
            
            st.session_state.eda_complete = True
            
            # Update chatbot
            if st.session_state.chatbot:
                update_chatbot_context()
            
            st.success("✅ Analysis complete!")
            st.rerun()
    
    # Display results
    if st.session_state.eda_complete:
        st.markdown("---")
        st.markdown("### 💡 Key Insights")
        
        insights = st.session_state.insights
        
        if insights:
            # Category filter
            categories = list(set([i['category'] for i in insights]))
            selected_category = st.selectbox(
                "Filter by category:",
                ['All'] + categories,
                key="insight_category"
            )
            
            filtered_insights = insights if selected_category == 'All' else [
                i for i in insights if i['category'] == selected_category
            ]
            
            # Display insights
            for idx, insight in enumerate(filtered_insights[:10], 1):
                st.markdown(f"""
                <div class="insight-card">
                    <strong>#{idx} - {insight['category'].replace('_', ' ').title()}</strong><br>
                    {insight['message']}<br>
                    <em>💡 {insight['recommendation']}</em>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant insights found")
        
        # EDA Summary
        with st.expander("📊 EDA Summary"):
            eda_results = st.session_state.eda_results
            
            st.markdown("**Descriptive Statistics:**")
            st.write(f"- Analyzed {len(eda_results.get('descriptive_stats', {}))} numeric columns")
            
            st.markdown("**Correlations:**")
            strong_corr = eda_results.get('correlation_analysis', {}).get('strong_correlations', [])
            st.write(f"- Found {len(strong_corr)} strong correlations")
            
            st.markdown("**Trends:**")
            trends = eda_results.get('trend_detection', {})
            st.write(f"- Detected trends in {len(trends)} variables")
            
            st.markdown("**Outliers:**")
            outliers = eda_results.get('outlier_detection', {})
            st.write(f"- Outlier analysis on {len(outliers)} columns")


def dashboards_tab():
    """Tab 3: Dynamic dashboards from dataset"""
    st.markdown("### 📊 Interactive Dashboards")
    
    if not st.session_state.data_loaded:
        st.warning("⚠️ Please upload data first")
        return
    
    data = st.session_state.data
    numeric_cols = st.session_state.metadata.get('numeric_columns', [])
    categorical_cols = st.session_state.metadata.get('categorical_columns', [])
    
    # Dashboard type selector
    dashboard_type = st.selectbox(
        "Select Dashboard Type:",
        ["Sales Overview", "KPI Summary", "Trend Analysis", "Distribution Analysis"],
        key="dashboard_type"
    )
    
    st.markdown("---")
    
    # Sales Overview Dashboard
    if dashboard_type == "Sales Overview":
        st.markdown("#### Sales Overview Dashboard")
        
        if len(numeric_cols) == 0:
            st.warning("No numeric columns found for sales metrics")
            return
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        if len(numeric_cols) > 0:
            total_col = st.selectbox("Total Sales Column:", numeric_cols, key="sales_col")
            with col1:
                total = data[total_col].sum()
                st.metric("Total Sales", f"{total:,.2f}")
            with col2:
                avg = data[total_col].mean()
                st.metric("Average", f"{avg:,.2f}")
            with col3:
                max_val = data[total_col].max()
                st.metric("Maximum", f"{max_val:,.2f}")
            with col4:
                count = len(data)
                st.metric("Records", f"{count:,}")
        
        # Charts
        st.markdown("---")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("##### Sales Trend")
            if len(numeric_cols) > 0:
                trend_col = st.selectbox("Y-axis:", numeric_cols, key="trend_y")
                fig = px.line(data, y=trend_col, title=f"{trend_col} Over Time")
                st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            st.markdown("##### Distribution")
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                cat_col = st.selectbox("Category:", categorical_cols, key="dist_cat")
                val_col = st.selectbox("Value:", numeric_cols, key="dist_val")
                fig = px.bar(data.groupby(cat_col)[val_col].sum().reset_index(),
                            x=cat_col, y=val_col, title=f"{val_col} by {cat_col}")
                st.plotly_chart(fig, use_container_width=True)
        
        # Store dashboard context
        st.session_state.dashboard_context = {
            'type': 'Sales Overview',
            'total_sales': data[numeric_cols[0]].sum() if numeric_cols else 0,
            'metrics': {col: data[col].sum() for col in numeric_cols[:3]}
        }
    
    # KPI Summary Dashboard
    elif dashboard_type == "KPI Summary":
        st.markdown("#### KPI Summary Dashboard")
        
        # Power BI KPIs
        if st.session_state.powerbi_metadata:
            st.markdown("##### Power BI KPIs")
            kpis = st.session_state.powerbi_metadata.get('kpis', [])
            
            cols = st.columns(min(4, len(kpis)))
            for idx, kpi in enumerate(kpis[:4]):
                with cols[idx]:
                    trend = kpi.get('trend', {})
                    delta = f"{trend.get('value', 0):+.1f}%" if trend else None
                    st.metric(
                        kpi['name'],
                        kpi.get('value', 'N/A'),
                        delta=delta
                    )
            
            st.markdown("---")
            st.markdown("##### KPI Details")
            for kpi in kpis:
                with st.expander(f"📊 {kpi['name']}"):
                    st.write(f"**Current Value:** {kpi.get('value', 'N/A')}")
                    st.write(f"**Target:** {kpi.get('target', 'N/A')}")
                    trend = kpi.get('trend', {})
                    st.write(f"**Trend:** {trend.get('direction', 'N/A')} ({trend.get('value', 0):+.2f}%)")
                    if 'description' in kpi:
                        st.write(f"**Description:** {kpi['description']}")
        
        # Dataset KPIs
        st.markdown("---")
        st.markdown("##### Dataset Metrics")
        
        if len(numeric_cols) >= 3:
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                col = numeric_cols[0]
                st.metric(f"{col} Total", f"{data[col].sum():,.2f}")
            with mcol2:
                col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
                st.metric(f"{col} Avg", f"{data[col].mean():,.2f}")
            with mcol3:
                col = numeric_cols[2] if len(numeric_cols) > 2 else numeric_cols[0]
                st.metric(f"{col} Max", f"{data[col].max():,.2f}")
    
    # Trend Analysis Dashboard
    elif dashboard_type == "Trend Analysis":
        st.markdown("#### Trend Analysis Dashboard")
        
        if len(numeric_cols) == 0:
            st.warning("No numeric columns for trend analysis")
            return
        
        # Column selector
        selected_cols = st.multiselect(
            "Select columns to analyze:",
            numeric_cols,
            default=numeric_cols[:3] if len(numeric_cols) >= 3 else numeric_cols,
            key="trend_cols"
        )
        
        if selected_cols:
            # Line chart
            st.markdown("##### Trends Over Time")
            fig = go.Figure()
            for col in selected_cols:
                fig.add_trace(go.Scatter(
                    y=data[col],
                    mode='lines',
                    name=col
                ))
            fig.update_layout(title="Multi-Variable Trend Analysis", height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Trend statistics from EDA
            if st.session_state.eda_complete:
                st.markdown("##### Statistical Trends")
                trends = st.session_state.eda_results.get('trend_detection', {})
                
                for col in selected_cols:
                    if col in trends:
                        trend_info = trends[col]
                        with st.expander(f"📈 {col} Trend Details"):
                            tcol1, tcol2, tcol3 = st.columns(3)
                            with tcol1:
                                st.write(f"**Direction:** {trend_info['trend_direction']}")
                            with tcol2:
                                st.write(f"**Change:** {trend_info['percent_change']:+.2f}%")
                            with tcol3:
                                st.write(f"**Strength:** {trend_info['trend_strength']}")
    
    # Distribution Analysis Dashboard
    elif dashboard_type == "Distribution Analysis":
        st.markdown("#### Distribution Analysis Dashboard")
        
        if len(numeric_cols) == 0:
            st.warning("No numeric columns for distribution analysis")
            return
        
        # Column selector
        dist_col = st.selectbox("Select column:", numeric_cols, key="dist_col")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Histogram")
            fig = px.histogram(data, x=dist_col, nbins=30, title=f"Distribution of {dist_col}")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("##### Box Plot")
            fig = px.box(data, y=dist_col, title=f"Box Plot - {dist_col}")
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.markdown("##### Statistical Summary")
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        with stats_col1:
            st.metric("Mean", f"{data[dist_col].mean():,.2f}")
        with stats_col2:
            st.metric("Median", f"{data[dist_col].median():,.2f}")
        with stats_col3:
            st.metric("Std Dev", f"{data[dist_col].std():,.2f}")
        with stats_col4:
            st.metric("Range", f"{data[dist_col].max() - data[dist_col].min():,.2f}")
        
        # Distribution insights from EDA
        if st.session_state.eda_complete:
            dist_analysis = st.session_state.eda_results.get('distribution_analysis', {})
            if dist_col in dist_analysis:
                info = dist_analysis[dist_col]
                st.info(f"Distribution Type: {info['distribution_type']} | "
                       f"Skewness: {info['skewness']:.3f} | "
                       f"Kurtosis: {info['kurtosis']:.3f}")
    
    # Update chatbot with dashboard context
    if st.session_state.chatbot:
        update_chatbot_context()


def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🤖 AI-Powered Data Analyst</div>', unsafe_allow_html=True)
    st.markdown("**LLM-Powered Conversational AI with Dynamic Dashboards**")
    
    # Sidebar Chatbot (always visible)
    sidebar_chatbot()
    
    # Main area with tabs
    tab1, tab2, tab3 = st.tabs(["📁 Upload", "🔍 Analysis", "📊 Dashboards"])
    
    with tab1:
        upload_tab()
    
    with tab2:
        analysis_tab()
    
    with tab3:
        dashboards_tab()


if __name__ == "__main__":
    main()
