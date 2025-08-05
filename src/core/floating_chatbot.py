"""
RELA Analytics Floating Chatbot
Real-time AI assistant with OpenAI integration
"""

import streamlit as st
import pandas as pd
import openai
import json
import time
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

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
        openai.api_key = self.api_key

        # Initialize session state for chat
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "chat_open" not in st.session_state:
            st.session_state.chat_open = False
        if "current_page_context" not in st.session_state:
            st.session_state.current_page_context = ""

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
        - Top States: {', '.join(members_df['state'].value_counts().head(3).index.tolist())}
        
        Operations Overview:
        - Operation Types: {', '.join(operations_df['operation_type'].unique())}
        - Success Rate: {(operations_df['status'] == 'Completed').mean():.1%}
        - Date Range: {operations_df['date'].min()} to {operations_df['date'].max()}
        
        Performance Metrics:
        - Average Performance Score: {members_df['performance_score'].mean():.1f}/100
        - Attendance Rate: {assignments_df['attendance'].mean():.1%}
        
        Page Context: {st.session_state.current_page_context}
        
        Please provide helpful insights based on this RELA Malaysia dashboard data.
        You can answer questions about members, operations, performance, demographics, trends, and analytics.
        """
        return context

    def call_openai_api(self, user_message: str, context: str) -> str:
        """Call OpenAI API with context and user message"""
        try:
            system_prompt = f"""
            You are RELA Analytics Assistant, an AI helper for the Malaysian People's Volunteer Corps (RELA) analytics dashboard.
            
            Context about the current dashboard:
            {context}
            
            Guidelines:
            - Provide concise, helpful answers about RELA data and analytics
            - Use specific numbers and statistics when available
            - Suggest relevant dashboard sections if applicable
            - Be professional and supportive
            - If asked about trends, mention specific data points
            - For complex queries, break down the analysis
            - Support both English and Bahasa Malaysia responses when appropriate
            - Keep responses under 300 words for better readability
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=400,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"

    def render_floating_chatbot(
        self,
        members_df: pd.DataFrame,
        operations_df: pd.DataFrame,
        assignments_df: pd.DataFrame,
    ):
        """Render the floating chatbot interface using Streamlit components"""

        # Add floating chatbot CSS
        st.markdown(
            """
        <style>
        .floating-chat-btn {
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #1f4e79, #2d5aa0);
            color: white;
            font-size: 24px;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .floating-chat-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        }
        
        .chat-container {
            position: fixed;
            bottom: 90px;
            left: 20px;
            width: 350px;
            max-height: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            border: 1px solid #e0e0e0;
            z-index: 999;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #1f4e79, #2d5aa0);
            color: white;
            padding: 15px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chat-messages {
            max-height: 300px;
            overflow-y: auto;
            padding: 15px;
            background: #f8f9fa;
        }
        
        .user-msg {
            background: #e3f2fd;
            padding: 8px 12px;
            border-radius: 12px;
            margin: 5px 0;
            margin-left: 20%;
            text-align: right;
        }
        
        .bot-msg {
            background: white;
            padding: 8px 12px;
            border-radius: 12px;
            margin: 5px 0;
            margin-right: 20%;
            border: 1px solid #e0e0e0;
        }
        
        .chat-input {
            padding: 15px;
            border-top: 1px solid #e0e0e0;
            background: white;
        }
        
        /* Hide default streamlit elements in chat */
        .chat-container .stTextInput > div > div > input {
            border: 1px solid #ddd;
            border-radius: 20px;
            padding: 8px 12px;
        }
        
        .chat-container .stButton > button {
            background: #1f4e79;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 6px 15px;
            font-size: 12px;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Chat toggle button (always visible)
        if st.button("🤖", key="chat_toggle", help="Open RELA Analytics Assistant"):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()

        # Render chat window if open
        if st.session_state.chat_open:
            with st.container():
                # Create chat window with custom styling
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)

                # Chat header
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown("**🤖 RELA Analytics Assistant**")
                with col2:
                    if st.button("✕", key="close_chat", help="Close"):
                        st.session_state.chat_open = False
                        st.rerun()

                # Chat messages area
                if st.session_state.chat_history:
                    for i, message in enumerate(
                        st.session_state.chat_history[-6:]
                    ):  # Show last 6 messages
                        if message["role"] == "user":
                            st.markdown(
                                f'<div class="user-msg">{message["content"]}</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f'<div class="bot-msg">{message["content"]}</div>',
                                unsafe_allow_html=True,
                            )
                else:
                    st.info(
                        "👋 Hi! I'm your RELA Analytics Assistant. Ask me anything about the dashboard data!"
                    )

                # Chat input
                col1, col2 = st.columns([4, 1])
                with col1:
                    user_input = st.text_input(
                        "",
                        placeholder="Ask about RELA data...",
                        key="chat_input",
                        label_visibility="collapsed",
                    )
                with col2:
                    send_pressed = st.button("Send", key="send_msg")

                # Handle user input
                if send_pressed and user_input.strip():
                    # Add user message
                    st.session_state.chat_history.append(
                        {"role": "user", "content": user_input}
                    )

                    # Get AI response
                    with st.spinner("🤔 Thinking..."):
                        context = self.get_dashboard_context(
                            members_df, operations_df, assignments_df
                        )
                        ai_response = self.call_openai_api(user_input, context)

                    # Add AI response
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": ai_response}
                    )

                    # Clear input and refresh
                    st.rerun()

                # Add some suggested questions
                st.markdown("**Quick questions:**")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Show key metrics", key="q1"):
                        st.session_state.chat_history.append(
                            {
                                "role": "user",
                                "content": "Show me the key performance metrics",
                            }
                        )
                        context = self.get_dashboard_context(
                            members_df, operations_df, assignments_df
                        )
                        response = self.call_openai_api(
                            "Show me the key performance metrics", context
                        )
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": response}
                        )
                        st.rerun()
                with col2:
                    if st.button("🏢 Top states", key="q2"):
                        st.session_state.chat_history.append(
                            {
                                "role": "user",
                                "content": "Which states have the most RELA members?",
                            }
                        )
                        context = self.get_dashboard_context(
                            members_df, operations_df, assignments_df
                        )
                        response = self.call_openai_api(
                            "Which states have the most RELA members?", context
                        )
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": response}
                        )
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

        # Add floating button styling
        if not st.session_state.chat_open:
            st.markdown(
                """
            <div class="floating-chat-btn" onclick="document.querySelector('[data-testid=stButton] button').click()">
                🤖
            </div>
            """,
                unsafe_allow_html=True,
            )

    def clear_chat_history(self):
        """Clear the chat history"""
        st.session_state.chat_history = []
