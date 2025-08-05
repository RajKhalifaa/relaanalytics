import sys
import os

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json

# Import custom modules
from src.utils.data_generator import DataGenerator
from src.core.dashboard import Dashboard
from src.core.analytics import Analytics
from src.core.simple_chatbot import SimpleChatbot
from src.utils.translations import get_text, get_language_options
from src.utils.data_persistence import DataPersistence

# Page configuration
st.set_page_config(
    page_title="RELA Malaysia Analytics Dashboard",
    page_icon="🇲🇾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for government-style appearance
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "data_generated" not in st.session_state:
    st.session_state.data_generated = False
    st.session_state.members_df = None
    st.session_state.operations_df = None
    st.session_state.assignments_df = None

# Initialize language preference
if "language" not in st.session_state:
    st.session_state.language = "en"  # Default to English


def render_header(lang):
    """Render the main header with RELA logo and language support"""

    # Create header with logo and title
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        # Display RELA logo
        try:
            st.image("assets/rela_logo.jpg", width=120)
        except:
            st.write("🇲🇾")  # Fallback if logo not found

    with col2:
        st.markdown(
            f"""
        <div style="text-align: center; padding: 10px;">
            <h1 style="color: #1f4e79; margin: 0; font-size: 2.5rem;">RELA MALAYSIA</h1>
            <h3 style="color: #2d5aa0; margin: 5px 0; font-size: 1.3rem;">Analytics Dashboard</h3>
            <p style="color: #666; margin: 5px 0; font-size: 1rem;">Powered by <strong>Credence AI & Analytics</strong></p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        # Language selector in the header
        pass
    # Main header with RELA branding
    st.markdown(
        """
    <div style="background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%); 
                padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <p style="color: #e8f4fd; text-align: center; margin: 0; font-size: 1.1rem;">
            Comprehensive Member Management & Operations Analytics
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def main():
    # Language selector in sidebar
    with st.sidebar:
        st.markdown("**RELA MALAYSIA**")
        st.markdown("*People's Volunteer Corps*")

        # Language selection
        language_options = get_language_options()
        selected_language_name = st.selectbox(
            "🌍 Language / Bahasa",
            list(language_options.keys()),
            index=0 if st.session_state.language == "en" else 1,
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
            get_text(lang, "overview"),
            get_text(lang, "member_analytics"),
            get_text(lang, "operations"),
            get_text(lang, "performance"),
            get_text(lang, "regional_analysis"),
            get_text(lang, "trends"),
            get_text(lang, "reports"),
        ]

        page = st.selectbox(get_text(lang, "navigation"), nav_options)

    # Render header with selected language
    render_header(lang)

    # Initialize classes
    dashboard = Dashboard(lang)  # Pass language to dashboard
    analytics = Analytics()
    ai_chatbot = SimpleChatbot(lang)  # Initialize AI chatbot with language
    ai_chatbot.update_language(lang)  # Update language dynamically
    data_persistence = DataPersistence()

    # Check if data is already loaded in session state
    if not st.session_state.data_generated:
        # Try to load saved data first
        if data_persistence.data_exists():
            with st.spinner(
                get_text(lang, "loading_saved_data", "Loading saved data...")
            ):
                members_df, operations_df, assignments_df = data_persistence.load_data()
                if members_df is not None:
                    st.session_state.members_df = members_df
                    st.session_state.operations_df = operations_df
                    st.session_state.assignments_df = assignments_df
                    st.session_state.data_generated = True
                    st.rerun()

    # Continue with sidebar controls
    with st.sidebar:

        st.markdown("---")
        st.markdown(f"### {get_text(lang, 'data_controls')}")

        # Show data status and metadata
        if data_persistence.data_exists():
            metadata = data_persistence.get_metadata()
            if metadata:
                st.success(get_text(lang, "data_ready"))
                st.metric(
                    get_text(lang, "total_members"), f"{metadata['members_count']:,}"
                )
                st.metric(
                    get_text(lang, "total_operations"),
                    f"{metadata['operations_count']:,}",
                )
                st.metric(
                    get_text(lang, "assignments"), f"{metadata['assignments_count']:,}"
                )

                # Show when data was generated
                gen_date = datetime.fromisoformat(metadata["generated_date"]).strftime(
                    "%Y-%m-%d %H:%M"
                )
                st.caption(
                    f"{get_text(lang, 'data_generated_on', 'Generated on')}: {gen_date}"
                )

        # Data control buttons
        col1, col2 = st.columns(2)

        with col1:
            # Generate new data button
            if st.button(
                get_text(lang, "generate_new", "🔄 Generate New"), type="primary"
            ):
                with st.spinner(get_text(lang, "generating_dataset")):
                    data_gen = DataGenerator()
                    members_df, operations_df, assignments_df = (
                        data_persistence.generate_and_save_data(50000, 5000, 20000)
                    )

                    if members_df is not None:
                        # Store in session state
                        st.session_state.members_df = members_df
                        st.session_state.operations_df = operations_df
                        st.session_state.assignments_df = assignments_df
                        st.session_state.data_generated = True
                        st.success(get_text(lang, "data_generated"))
                        st.rerun()
                    else:
                        st.error(
                            get_text(
                                lang,
                                "data_generation_failed",
                                "Failed to generate data",
                            )
                        )

        with col2:
            # Delete data button
            if data_persistence.data_exists():
                if st.button(
                    get_text(lang, "delete_data", "🗑️ Delete Data"), type="secondary"
                ):
                    data_persistence.delete_data()
                    st.session_state.data_generated = False
                    if "members_df" in st.session_state:
                        del st.session_state.members_df
                        del st.session_state.operations_df
                        del st.session_state.assignments_df
                    st.success(
                        get_text(lang, "data_deleted", "Data deleted successfully")
                    )
                    st.rerun()

        # Show message if no data exists
        if not st.session_state.data_generated and not data_persistence.data_exists():
            st.warning(get_text(lang, "click_generate"))

        st.markdown("---")
        st.markdown(f"### {get_text(lang, 'quick_filters')}")

        if st.session_state.data_generated:
            # Date range filter
            date_range = st.date_input(
                get_text(lang, "date_range"),
                value=(datetime.now() - timedelta(days=365), datetime.now()),
                max_value=datetime.now(),
            )

            # State filter
            states = st.session_state.members_df["state"].unique().tolist()
            selected_states = st.multiselect(
                get_text(lang, "states_territories"), states, default=states[:5]
            )

            # Status filter - translate options
            status_options = [
                get_text(lang, "active"),
                get_text(lang, "inactive"),
                get_text(lang, "on_leave"),
                get_text(lang, "training"),
            ]
            status_mapping = {
                get_text(lang, "active"): "Active",
                get_text(lang, "inactive"): "Inactive",
                get_text(lang, "on_leave"): "On Leave",
                get_text(lang, "training"): "Training",
            }

            selected_status_display = st.multiselect(
                get_text(lang, "member_status"),
                status_options,
                default=[get_text(lang, "active")],
            )

            # Convert back to English for data filtering
            selected_status = [
                status_mapping[status] for status in selected_status_display
            ]

    # Main content area
    if not st.session_state.data_generated:
        st.info(get_text(lang, "welcome_message"))

        # Show some information about RELA
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
            ### {get_text(lang, 'about_rela')}
            {get_text(lang, 'about_description')}
            """
            )

        with col2:
            st.markdown(f"### {get_text(lang, 'core_functions')}")
            functions_list = get_text(lang, "core_functions_list")
            for func in functions_list:
                st.markdown(f"- {func}")

        with col3:
            st.markdown(f"### {get_text(lang, 'coverage')}")
            coverage_list = get_text(lang, "coverage_list")
            for coverage in coverage_list:
                st.markdown(f"- {coverage}")

        return

    # Filter data based on sidebar selections
    filtered_data = analytics.filter_data(
        st.session_state.members_df,
        st.session_state.operations_df,
        st.session_state.assignments_df,
        selected_states if "selected_states" in locals() else None,
        selected_status if "selected_status" in locals() else None,
        date_range if "date_range" in locals() else None,
    )

    # Route to different pages based on translated navigation
    if page == get_text(lang, "overview"):
        dashboard.show_overview(filtered_data)
    elif page == get_text(lang, "member_analytics"):
        dashboard.show_member_analytics(filtered_data)
    elif page == get_text(lang, "operations"):
        dashboard.show_operations(filtered_data)
    elif page == get_text(lang, "performance"):
        dashboard.show_performance(filtered_data)
    elif page == get_text(lang, "regional_analysis"):
        dashboard.show_regional_analysis(filtered_data)
    elif page == get_text(lang, "trends"):
        dashboard.show_trends(filtered_data)
    elif page == get_text(lang, "reports"):
        dashboard.show_reports(filtered_data)

    # Render AI chatbot on all pages
    if st.session_state.data_generated:
        # Set context for current page
        ai_chatbot.set_page_context(
            page, f"Currently viewing {page} with {len(filtered_data[0])} members"
        )
        ai_chatbot.render_floating_icon_chatbot(
            filtered_data[0], filtered_data[1], filtered_data[2]
        )


if __name__ == "__main__":
    main()
