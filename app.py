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
from translations import get_text, get_language_options

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

# Initialize language preference
if 'language' not in st.session_state:
    st.session_state.language = 'en'  # Default to English

def render_header(lang):
    """Render the main header with language support"""
    st.markdown(f"""
    <div class="main-header">
        <h1>🇲🇾 {get_text(lang, 'app_title')}</h1>
        <p>{get_text(lang, 'app_subtitle')}</p>
        <p style="font-size: 0.9rem; margin-top: 0.5rem;">{get_text(lang, 'app_description')}</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Language selector in sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Flag_of_Malaysia.svg/320px-Flag_of_Malaysia.svg.png", width=200)
        
        # Language selection
        language_options = get_language_options()
        selected_language_name = st.selectbox(
            "🌍 Language / Bahasa",
            list(language_options.keys()),
            index=0 if st.session_state.language == 'en' else 1
        )
        
        # Update session state when language changes
        new_language = language_options[selected_language_name]
        if new_language != st.session_state.language:
            st.session_state.language = new_language
            st.rerun()
        
        lang = st.session_state.language
        
        st.markdown(f"### {get_text(lang, 'navigation')}")
        
        # Navigation options with translations
        nav_options = [
            get_text(lang, 'overview'),
            get_text(lang, 'member_analytics'), 
            get_text(lang, 'operations'),
            get_text(lang, 'performance'),
            get_text(lang, 'regional_analysis'),
            get_text(lang, 'trends'),
            get_text(lang, 'reports')
        ]
        
        page = st.selectbox(
            get_text(lang, 'navigation'),
            nav_options
        )
    
    # Render header with selected language
    render_header(lang)
    
    # Initialize classes
    data_gen = DataGenerator()
    dashboard = Dashboard(lang)  # Pass language to dashboard
    analytics = Analytics()
    
    # Continue with sidebar controls
    with st.sidebar:
        
        st.markdown("---")
        st.markdown(f"### {get_text(lang, 'data_controls')}")
        
        # Generate data button
        if st.button(get_text(lang, 'generate_data'), type="primary"):
            with st.spinner(get_text(lang, 'generating_dataset')):
                # Generate datasets (reduced size for faster loading)
                members_df = data_gen.generate_members_data(50000)  # 50k members for demo
                operations_df = data_gen.generate_operations_data(5000)  # 5k operations
                assignments_df = data_gen.generate_assignments_data(members_df, 20000)  # 20k assignments
                
                # Store in session state
                st.session_state.members_df = members_df
                st.session_state.operations_df = operations_df
                st.session_state.assignments_df = assignments_df
                st.session_state.data_generated = True
                
            st.success(get_text(lang, 'data_generated'))
            st.rerun()
        
        # Data status
        if st.session_state.data_generated:
            st.success(get_text(lang, 'data_ready'))
            st.metric(get_text(lang, 'total_members'), f"{len(st.session_state.members_df):,}")
            st.metric(get_text(lang, 'total_operations'), f"{len(st.session_state.operations_df):,}")
            st.metric(get_text(lang, 'assignments'), f"{len(st.session_state.assignments_df):,}")
        else:
            st.warning(get_text(lang, 'click_generate'))
        
        st.markdown("---")
        st.markdown(f"### {get_text(lang, 'quick_filters')}")
        
        if st.session_state.data_generated:
            # Date range filter
            date_range = st.date_input(
                get_text(lang, 'date_range'),
                value=(datetime.now() - timedelta(days=365), datetime.now()),
                max_value=datetime.now()
            )
            
            # State filter
            states = st.session_state.members_df['state'].unique().tolist()
            selected_states = st.multiselect(
                get_text(lang, 'states_territories'),
                states,
                default=states[:5]
            )
            
            # Status filter - translate options
            status_options = [
                get_text(lang, 'active'),
                get_text(lang, 'inactive'), 
                get_text(lang, 'on_leave'),
                get_text(lang, 'training')
            ]
            status_mapping = {
                get_text(lang, 'active'): 'Active',
                get_text(lang, 'inactive'): 'Inactive',
                get_text(lang, 'on_leave'): 'On Leave',
                get_text(lang, 'training'): 'Training'
            }
            
            selected_status_display = st.multiselect(
                get_text(lang, 'member_status'),
                status_options,
                default=[get_text(lang, 'active')]
            )
            
            # Convert back to English for data filtering
            selected_status = [status_mapping[status] for status in selected_status_display]
    
    # Main content area
    if not st.session_state.data_generated:
        st.info(get_text(lang, 'welcome_message'))
        
        # Show some information about RELA
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            ### {get_text(lang, 'about_rela')}
            {get_text(lang, 'about_description')}
            """)
        
        with col2:
            st.markdown(f"### {get_text(lang, 'core_functions')}")
            functions_list = get_text(lang, 'core_functions_list')
            for func in functions_list:
                st.markdown(f"- {func}")
        
        with col3:
            st.markdown(f"### {get_text(lang, 'coverage')}")
            coverage_list = get_text(lang, 'coverage_list')
            for coverage in coverage_list:
                st.markdown(f"- {coverage}")
        
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
    
    # Route to different pages based on translated navigation
    if page == get_text(lang, 'overview'):
        dashboard.show_overview(filtered_data)
    elif page == get_text(lang, 'member_analytics'):
        dashboard.show_member_analytics(filtered_data)
    elif page == get_text(lang, 'operations'):
        dashboard.show_operations(filtered_data)
    elif page == get_text(lang, 'performance'):
        dashboard.show_performance(filtered_data)
    elif page == get_text(lang, 'regional_analysis'):
        dashboard.show_regional_analysis(filtered_data)
    elif page == get_text(lang, 'trends'):
        dashboard.show_trends(filtered_data)
    elif page == get_text(lang, 'reports'):
        dashboard.show_reports(filtered_data)

if __name__ == "__main__":
    main()
