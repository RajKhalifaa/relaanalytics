"""
RELA Analytics Simple Chatbot
Real-time AI assistant with OpenAI integration - Sidebar implementation
"""

import streamlit as st
import pandas as pd
from openai import OpenAI
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

from ..utils.translations import get_text


class SimpleChatbot:
    def __init__(self, language="en"):
        self.language = language
        # Get API key from environment variable for security
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            st.error(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
            )
            return

        # Initialize OpenAI client with new v1.0+ format
        self.client = OpenAI(api_key=self.api_key)

        # Initialize session state for chat
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "current_page_context" not in st.session_state:
            st.session_state.current_page_context = ""

    def update_language(self, language: str):
        """Update the chatbot language"""
        self.language = language

    def set_page_context(self, page_name: str, data_summary: str = ""):
        """Set context about the current page for better AI responses"""
        st.session_state.current_page_context = (
            f"Current page: {page_name}. {data_summary}"
        )

    def get_dashboard_context(
        self,
        members_df: pd.DataFrame,
        operations_df: pd.DataFrame,
        assignments_df: pd.DataFrame,
    ) -> str:
        """Generate context about the dashboard data for AI"""
        try:
            if self.language == "ms":
                context = f"""
                Konteks Papan Pemuka Analitik RELA Malaysia:
                
                Ringkasan Data Semasa:
                - Jumlah Ahli: {len(members_df):,}
                - Jumlah Operasi: {len(operations_df):,}
                - Jumlah Tugasan: {len(assignments_df):,}
                
                Statistik Ahli:
                - Ahli Aktif: {len(members_df[members_df['status'] == 'Active']):,}
                - Julat Umur: {members_df['age'].min()}-{members_df['age'].max()} tahun
                - Negeri Dilindungi: {members_df['state'].nunique()} negeri
                - 3 Negeri Teratas: {', '.join(members_df['state'].value_counts().head(3).index.tolist())}
                
                Gambaran Operasi:
                - Jenis Operasi: {', '.join(operations_df['operation_type'].unique())}
                - Kadar Kejayaan: {(operations_df['status'] == 'Completed').mean():.1%}
                - Julat Tarikh: {operations_df['date'].min()} hingga {operations_df['date'].max()}
                
                Metrik Prestasi:
                - Purata Skor Prestasi: {members_df['performance_score'].mean():.1f}/100
                - Kadar Kehadiran: {assignments_df['attendance'].mean():.1%}
                
                Konteks Halaman: {st.session_state.current_page_context}
                
                Sila berikan cerapan berguna berdasarkan data papan pemuka RELA Malaysia ini.
                """
            else:
                context = f"""
                RELA Malaysia Analytics Dashboard Context:
                
                Current Data Summary:
                - Total Members: {len(members_df):,}
                - Total Operations: {len(operations_df):,}
                - Total Assignments: {len(assignments_df):,}
                
                Member Statistics:
                - Active Members: {len(members_df[members_df['status'] == 'Active']):,}
                - Age Range: {members_df['age'].min()}-{members_df['age'].max()} years
                - States Covered: {members_df['state'].nunique()} states
                - Top 3 States: {', '.join(members_df['state'].value_counts().head(3).index.tolist())}
                
                Operations Overview:
                - Operation Types: {', '.join(operations_df['operation_type'].unique())}
                - Success Rate: {(operations_df['status'] == 'Completed').mean():.1%}
                - Date Range: {operations_df['date'].min()} to {operations_df['date'].max()}
                
                Performance Metrics:
                - Average Performance Score: {members_df['performance_score'].mean():.1f}/100
                - Attendance Rate: {assignments_df['attendance'].mean():.1%}
                
                Page Context: {st.session_state.current_page_context}
                
                Please provide helpful insights based on this RELA Malaysia dashboard data.
                """
            return context
        except Exception as e:
            if self.language == "ms":
                return f"Konteks papan pemuka tidak tersedia. Ralat: {str(e)}"
            else:
                return f"Dashboard context unavailable. Error: {str(e)}"

    def call_openai_api(self, user_message: str, context: str) -> str:
        """Call OpenAI API with context and user message"""
        try:
            # Language-specific instructions
            language_instructions = {
                "en": {
                    "response_language": "Respond in English",
                    "greeting": "You are RELA Analytics Assistant, an AI helper for the Malaysian People's Volunteer Corps (RELA) analytics dashboard.",
                    "fallback": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                },
                "ms": {
                    "response_language": "Respond in Bahasa Malaysia (Malay language)",
                    "greeting": "Anda adalah Pembantu Analitik RELA, pembantu AI untuk papan pemuka analitik Jabatan Sukarelawan Rakyat Malaysia (RELA).",
                    "fallback": "Saya mohon maaf, tetapi saya mengalami kesulitan teknikal. Sila cuba lagi kemudian.",
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

    def render_sidebar_chatbot(
        self,
        members_df: pd.DataFrame,
        operations_df: pd.DataFrame,
        assignments_df: pd.DataFrame,
    ):
        """Render chatbot in sidebar"""

        with st.sidebar:
            st.markdown("---")
            # Use translated text for AI Assistant
            if self.language == "ms":
                st.markdown("### 🤖 Pembantu AI")
                placeholder_text = "Tanya tentang data RELA:"
                placeholder_example = "cth: Berapa ramai ahli aktif?"
                ask_btn_text = "Tanya"
                clear_btn_text = "Padam"
                recent_conv_text = "**Perbualan Terkini:**"
                you_text = "**Anda:**"
                ai_text = "**AI:**"
                quick_questions_text = "**Soalan Pantas:**"
                key_metrics_text = "📊 Metrik Utama"
                top_states_text = "🏢 Negeri Teratas"
                analyzing_text = "🤔 Menganalisis..."
                greeting_text = "👋 Hai! Saya pembantu Analitik RELA anda. Tanya saya apa-apa tentang data papan pemuka!"
            else:
                st.markdown("### 🤖 AI Assistant")
                placeholder_text = "Ask about RELA data:"
                placeholder_example = "e.g., How many active members?"
                ask_btn_text = "Ask"
                clear_btn_text = "Clear"
                recent_conv_text = "**Recent Conversation:**"
                you_text = "**You:**"
                ai_text = "**AI:**"
                quick_questions_text = "**Quick Questions:**"
                key_metrics_text = "📊 Key Metrics"
                top_states_text = "🏢 Top States"
                analyzing_text = "🤔 Analyzing..."
                greeting_text = "👋 Hi! I'm your RELA Analytics Assistant. Ask me anything about the dashboard data!"

            # Chat interface
            user_input = st.text_input(
                placeholder_text,
                placeholder=placeholder_example,
                key="ai_chat_input",
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                ask_btn = st.button(
                    ask_btn_text, key="ask_ai", use_container_width=True
                )
            with col2:
                clear_btn = st.button(
                    clear_btn_text, key="clear_ai", use_container_width=True
                )

            if clear_btn:
                st.session_state.chat_history = []
                st.rerun()

            if ask_btn and user_input.strip():
                # Add user message
                st.session_state.chat_history.append(
                    {"role": "user", "content": user_input}
                )

                # Get AI response
                with st.spinner(analyzing_text):
                    context = self.get_dashboard_context(
                        members_df, operations_df, assignments_df
                    )
                    ai_response = self.call_openai_api(user_input, context)

                # Add AI response
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": ai_response}
                )
                st.rerun()

            # Display chat history (last 4 messages)
            if st.session_state.chat_history:
                st.markdown(recent_conv_text)
                for message in st.session_state.chat_history[-4:]:
                    if message["role"] == "user":
                        st.markdown(f"{you_text} {message['content']}")
                    else:
                        st.markdown(f"{ai_text} {message['content']}")
                    st.markdown("---")
            else:
                st.info(greeting_text)

            # Quick action buttons
            st.markdown(quick_questions_text)
            if st.button(key_metrics_text, key="quick1", use_container_width=True):
                if self.language == "ms":
                    question = "Tunjukkan metrik prestasi utama"
                else:
                    question = "Show me the key performance metrics"
                st.session_state.chat_history.append(
                    {"role": "user", "content": question}
                )
                context = self.get_dashboard_context(
                    members_df, operations_df, assignments_df
                )
                response = self.call_openai_api(question, context)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

            if st.button(top_states_text, key="quick2", use_container_width=True):
                if self.language == "ms":
                    question = "Negeri mana yang mempunyai ahli RELA paling ramai?"
                else:
                    question = "Which states have the most RELA members?"
                st.session_state.chat_history.append(
                    {"role": "user", "content": question}
                )
                context = self.get_dashboard_context(
                    members_df, operations_df, assignments_df
                )
                response = self.call_openai_api(question, context)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

    def render_floating_icon_chatbot(
        self,
        members_df: pd.DataFrame,
        operations_df: pd.DataFrame,
        assignments_df: pd.DataFrame,
    ):
        """Render a floating icon that opens a modal-style chatbot"""

        # Custom CSS for floating button
        st.markdown(
            """
        <style>
        .floating-chat-icon {
            position: fixed;
            bottom: 20px;
            left: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #1f4e79, #2d5aa0);
            border-radius: 50%;
            color: white;
            font-size: 24px;
            text-align: center;
            line-height: 60px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            transition: all 0.3s ease;
        }
        
        .floating-chat-icon:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        }
        </style>
        
        <div class="floating-chat-icon" onclick="document.querySelector('[data-testid=stSidebar] .stTextInput input').focus()">
            🤖
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Also add the sidebar chatbot
        self.render_sidebar_chatbot(members_df, operations_df, assignments_df)
