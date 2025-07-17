import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json

# Import custom modules
from data_generator import DataGenerator
from dashboard import Dashboard
from analytics import Analytics

# Page configuration
st.set_page_config(
    page_title="RELA Malaysia Analytics Dashboard",
    page_icon="🇲🇾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for government-style appearance
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #e8f4fd;
        text-align: center;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stSelectbox label, .stMultiselect label {
        font-weight: bold;
        color: #1f4e79;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_generated' not in st.session_state:
    st.session_state.data_generated = False
    st.session_state.members_df = None
    st.session_state.operations_df = None
    st.session_state.assignments_df = None

# Main header
st.markdown("""
<div class="main-header">
    <h1>🇲🇾 RELA MALAYSIA</h1>
    <p>Jabatan Sukarelawan Malaysia - Analytics Dashboard</p>
    <p style="font-size: 0.9rem; margin-top: 0.5rem;">Malaysia Volunteers Corps Department | Comprehensive Operations Analytics</p>
</div>
""", unsafe_allow_html=True)

def main():
    # Initialize classes
    data_gen = DataGenerator()
    dashboard = Dashboard()
    analytics = Analytics()
    
    # Sidebar for navigation and controls
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Flag_of_Malaysia.svg/320px-Flag_of_Malaysia.svg.png", width=200)
        st.markdown("### Navigation")
        
        page = st.selectbox(
            "Select Dashboard Section",
            ["🏠 Overview", "👥 Member Analytics", "🚨 Operations", "📊 Performance", "🗺️ Regional Analysis", "📈 Trends", "📋 Reports"]
        )
        
        st.markdown("---")
        st.markdown("### Data Controls")
        
        # Generate data button
        if st.button("🔄 Generate/Refresh Data", type="primary"):
            with st.spinner("Generating comprehensive RELA dataset..."):
                # Generate datasets
                members_df = data_gen.generate_members_data(3000000)  # 3 million members
                operations_df = data_gen.generate_operations_data(50000)  # 50k operations
                assignments_df = data_gen.generate_assignments_data(members_df, 200000)  # 200k assignments
                
                # Store in session state
                st.session_state.members_df = members_df
                st.session_state.operations_df = operations_df
                st.session_state.assignments_df = assignments_df
                st.session_state.data_generated = True
                
            st.success("✅ Data generated successfully!")
            st.rerun()
        
        # Data status
        if st.session_state.data_generated:
            st.success("✅ Data Ready")
            st.metric("👥 Members", f"{len(st.session_state.members_df):,}")
            st.metric("🚨 Operations", f"{len(st.session_state.operations_df):,}")
            st.metric("📋 Assignments", f"{len(st.session_state.assignments_df):,}")
        else:
            st.warning("⚠️ Click 'Generate Data' to start")
        
        st.markdown("---")
        st.markdown("### Quick Filters")
        
        if st.session_state.data_generated:
            # Date range filter
            date_range = st.date_input(
                "📅 Date Range",
                value=(datetime.now() - timedelta(days=365), datetime.now()),
                max_value=datetime.now()
            )
            
            # State filter
            states = st.session_state.members_df['state'].unique().tolist()
            selected_states = st.multiselect(
                "🏛️ States/Territories",
                states,
                default=states[:5]
            )
            
            # Status filter
            status_options = ['Active', 'Inactive', 'On Leave', 'Training']
            selected_status = st.multiselect(
                "📊 Member Status",
                status_options,
                default=['Active']
            )
    
    # Main content area
    if not st.session_state.data_generated:
        st.info("🚀 Welcome to RELA Malaysia Analytics Dashboard. Please generate the dataset using the sidebar to begin analysis.")
        
        # Show some information about RELA
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### About RELA Malaysia
            The People's Volunteer Corps (RELA) is Malaysia's largest civil volunteer organization with over 3 million members nationwide.
            """)
        
        with col2:
            st.markdown("""
            ### Core Functions
            - Security control and monitoring
            - Emergency response operations
            - Immigration assistance
            - Community safety programs
            """)
        
        with col3:
            st.markdown("""
            ### Coverage
            - All 13 states + 3 federal territories
            - Urban and rural areas
            - 24/7 operations capability
            - Multi-ethnic volunteer force
            """)
        
        return
    
    # Filter data based on sidebar selections
    filtered_data = analytics.filter_data(
        st.session_state.members_df,
        st.session_state.operations_df,
        st.session_state.assignments_df,
        selected_states if 'selected_states' in locals() else None,
        selected_status if 'selected_status' in locals() else None,
        date_range if 'date_range' in locals() else None
    )
    
    # Route to different pages
    if page == "🏠 Overview":
        dashboard.show_overview(filtered_data)
    elif page == "👥 Member Analytics":
        dashboard.show_member_analytics(filtered_data)
    elif page == "🚨 Operations":
        dashboard.show_operations(filtered_data)
    elif page == "📊 Performance":
        dashboard.show_performance(filtered_data)
    elif page == "🗺️ Regional Analysis":
        dashboard.show_regional_analysis(filtered_data)
    elif page == "📈 Trends":
        dashboard.show_trends(filtered_data)
    elif page == "📋 Reports":
        dashboard.show_reports(filtered_data)

if __name__ == "__main__":
    main()
