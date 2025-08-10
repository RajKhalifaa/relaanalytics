"""
RELA Analytics Floating Chatbot
Modern floating AI assistant with OpenAI integration
"""

import streamlit as st
import pandas as pd

try:
    from openai import OpenAI
except ImportError:
    st.error(
        "OpenAI package not found. Please install with: pip install openai>=1.55.0"
    )
    st.stop()
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from datetime import datetime

# Load environment variables
load_dotenv()

from ..utils.translations import get_text


class FloatingChatbot:
    def __init__(self, language="en"):
        self.language = language
        # Get API key from environment variable for security
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            st.error(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )
            return

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # Initialize session state for chat
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "chat_open" not in st.session_state:
            st.session_state.chat_open = False
        if "current_page_context" not in st.session_state:
            st.session_state.current_page_context = ""

    def update_language(self, language):
        """Update the chatbot language"""
        self.language = language

    def get_ai_response(self, user_message: str, context: str) -> str:
        """Get AI response using OpenAI API"""
        try:
            # Language-specific instructions
            language_instructions = {
                "en": {
                    "greeting": "You are a helpful AI assistant for RELA Malaysia Analytics Dashboard.",
                    "response_language": "Respond in English",
                    "fallback": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                },
                "ms": {
                    "greeting": "Anda adalah pembantu AI yang berguna untuk Papan Pemuka Analitik RELA Malaysia.",
                    "response_language": "Respond in Bahasa Malaysia (Malay language)",
                    "fallback": "Maaf, saya mengalami kesulitan teknikal. Sila cuba lagi nanti.",
                },
            }

            lang_config = language_instructions.get(
                self.language, language_instructions["en"]
            )

            system_prompt = f"""
            {lang_config["greeting"]}
            
            IMPORTANT: {lang_config["response_language"]}. All responses must be in the same language as this instruction.
            
            Context about the current dashboard:
            {context}
            
            Guidelines:
            - Provide concise, helpful answers about RELA data and analytics
            - Use specific numbers and statistics when available
            - Suggest relevant dashboard sections if applicable
            - Be professional and supportive
            - If asked about trends, mention specific data points
            - For complex queries, break down the analysis
            - Keep responses under 250 words for better readability
            - Always respond in the language specified above
            
            If responding in Bahasa Malaysia:
            - Use proper Malay terminology for RELA operations
            - "Members" = "Ahli", "Operations" = "Operasi", "Performance" = "Prestasi"
            - "States" = "Negeri", "Active" = "Aktif", "Total" = "Jumlah"
            - "Analytics" = "Analitik", "Dashboard" = "Papan Pemuka"
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=350,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            lang_config = language_instructions.get(
                self.language, language_instructions["en"]
            )
            return f"{lang_config['fallback']} Error: {str(e)}"

    def render_floating_chatbot(
        self,
        members_df: pd.DataFrame,
        operations_df: pd.DataFrame,
        assignments_df: pd.DataFrame,
    ):
        """Render modern floating chatbot interface with icon toggle"""

        # Get current language
        lang = self.language

        # Only render if we have valid API key
        if not self.api_key:
            return

        # Chat toggle positioned at bottom-right
        with st.container():
            # Create columns to position the button at the right
            col1, col2, col3 = st.columns([8, 1, 1])

            with col3:
                if st.button(
                    "💬",
                    key="chat_toggle",
                    help=get_text(
                        lang, "chat_with_rela_assistant", "Chat with RELA Assistant"
                    ),
                    use_container_width=True,
                ):
                    st.session_state.chat_open = not st.session_state.chat_open
                    st.rerun()

        # Render chat window if open
        if st.session_state.chat_open:
            # Create a sidebar-like container for the chat
            with st.expander("🤖 RELA Analytics Assistant", expanded=True):
                # Welcome message
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
                        <h4 style="margin: 0; color: white;">{get_text(lang, 'chatbot_greeting', '👋 Hi! I\'m your RELA Analytics Assistant')}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">{get_text(lang, 'chatbot_prompt', 'Ask me anything about the dashboard data!')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Quick action buttons
                st.markdown(
                    f"**{get_text(lang, 'quick_questions', 'Quick Questions')}:**"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(
                        get_text(lang, "key_metrics", "📊 Key Metrics"),
                        key="quick_metrics",
                        use_container_width=True,
                    ):
                        question_text = (
                            "Show me the key metrics and statistics"
                            if lang == "en"
                            else "Tunjukkan saya metrik dan statistik utama"
                        )
                        self._process_quick_question(
                            question_text,
                            members_df,
                            operations_df,
                            assignments_df,
                        )

                with col2:
                    if st.button(
                        get_text(lang, "top_states", "🗺️ Top States"),
                        key="quick_states",
                        use_container_width=True,
                    ):
                        question_text = (
                            "Which states have the most RELA members?"
                            if lang == "en"
                            else "Negeri mana yang mempunyai ahli RELA paling ramai?"
                        )
                        self._process_quick_question(
                            question_text,
                            members_df,
                            operations_df,
                            assignments_df,
                        )

                # Chat messages display
                if st.session_state.chat_history:
                    st.markdown("---")
                    st.markdown(
                        f"**{get_text(lang, 'conversation', 'Conversation')}:**"
                    )

                    # Display last 6 messages to avoid clutter
                    for message in st.session_state.chat_history[-6:]:
                        if message["role"] == "user":
                            st.markdown(
                                f"""
                                <div style="text-align: right; margin: 10px 0;">
                                    <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                                color: white; padding: 10px 15px; border-radius: 15px 15px 5px 15px; 
                                                max-width: 80%; font-size: 14px;">
                                        <strong>{get_text(lang, 'you', 'You')}:</strong> {message["content"]}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"""
                                <div style="margin: 10px 0;">
                                    <div style="display: inline-block; background: #f8f9fa; color: #495057; 
                                                border: 1px solid #e9ecef; padding: 10px 15px; 
                                                border-radius: 15px 15px 15px 5px; max-width: 90%; font-size: 14px;">
                                        <strong>{get_text(lang, 'assistant', '🤖 Assistant')}:</strong> {message["content"]}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                # Chat input
                st.markdown("---")

                # Create input form
                with st.form("chat_form", clear_on_submit=True):
                    user_input = st.text_input(
                        get_text(lang, "ask_about_rela_data", "Ask about RELA data:"),
                        placeholder=get_text(
                            lang,
                            "ask_placeholder",
                            "e.g., How many active members are there?",
                        ),
                        label_visibility="collapsed",
                    )

                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        submit_button = st.form_submit_button(
                            get_text(lang, "send", "Send 📤"), use_container_width=True
                        )

                    with col2:
                        if st.form_submit_button(
                            get_text(lang, "clear", "Clear 🗑️"), use_container_width=True
                        ):
                            st.session_state.chat_history = []
                            st.rerun()

                    with col3:
                        if st.form_submit_button(
                            get_text(lang, "close", "Close ❌"),
                            use_container_width=True,
                        ):
                            st.session_state.chat_open = False
                            st.rerun()

                # Process chat message
                if submit_button and user_input.strip():
                    self._process_chat_message(
                        user_input.strip(), members_df, operations_df, assignments_df
                    )
                    st.rerun()

    def _process_quick_question(
        self,
        question: str,
        members_df: pd.DataFrame,
        operations_df: pd.DataFrame,
        assignments_df: pd.DataFrame,
    ):
        """Process a quick question button click"""
        self._process_chat_message(question, members_df, operations_df, assignments_df)
        st.rerun()

    def _process_chat_message(
        self,
        user_input: str,
        members_df: pd.DataFrame,
        operations_df: pd.DataFrame,
        assignments_df: pd.DataFrame,
    ):
        """Process and respond to chat message"""
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Generate context from data
        context = self._generate_context(members_df, operations_df, assignments_df)

        # Get AI response
        bot_response = self.get_ai_response(user_input, context)

        # Add bot response to history
        st.session_state.chat_history.append(
            {"role": "assistant", "content": bot_response}
        )

    def _generate_context(
        self,
        members_df: pd.DataFrame,
        operations_df: pd.DataFrame,
        assignments_df: pd.DataFrame,
    ) -> str:
        """Generate context from current data"""
        try:
            total_members = len(members_df) if not members_df.empty else 0
            active_members = (
                len(members_df[members_df["status"] == "Active"])
                if not members_df.empty
                else 0
            )
            total_operations = len(operations_df) if not operations_df.empty else 0
            total_states = members_df["state"].nunique() if not members_df.empty else 0

            top_state = (
                members_df["state"].value_counts().index[0]
                if not members_df.empty
                else "N/A"
            )
            top_state_count = (
                members_df["state"].value_counts().iloc[0]
                if not members_df.empty
                else 0
            )

            context = f"""
            Current RELA Malaysia Analytics Dashboard Data Summary:
            - Total Members: {total_members:,}
            - Active Members: {active_members:,}
            - Inactive Members: {total_members - active_members:,}
            - Total Operations: {total_operations:,}
            - States Covered: {total_states}
            - Top State by Members: {top_state} ({top_state_count:,} members)
            
            Current page context: {st.session_state.get('current_page_context', 'Dashboard overview')}
            """

            return context

        except Exception as e:
            return f"Dashboard data available but unable to generate detailed context. Error: {str(e)}"

    def update_language(self, language: str):
        """Update the chatbot language"""
        self.language = language

    def set_page_context(self, page: str, context: str):
        """Set context for the current page"""
        st.session_state.current_page_context = f"Page: {page} - {context}"

    def clear_chat_history(self):
        """Clear the chat history"""
        st.session_state.chat_history = []
