"""
RELA Analytics Chatbot
Advanced natural language query interface for dashboard insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple, Any, Optional

from ..utils.translations import get_text


class RELAChatbot:
    def __init__(self, language="en"):
        self.language = language
        self.colors = {
            "primary": "#1f4e79",
            "secondary": "#2d5aa0",
            "success": "#28a745",
            "warning": "#ffc107",
            "danger": "#dc3545",
            "info": "#17a2b8",
        }

        # Initialize conversation history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Query patterns and their handlers
        self.query_patterns = {
            # Member-related queries
            "total_members": r"(how many|total|number of).*(members|volunteers)",
            "active_members": r"(active|working).*(members|volunteers)",
            "member_by_state": r"(members|volunteers).*(in|from).*(state|states)",
            "average_age": r"(average|mean).*(age)",
            "gender_distribution": r"(gender|male|female).*(distribution|breakdown)",
            "education_levels": r"(education|qualification).*(level|distribution)",
            # Operations-related queries
            "total_operations": r"(how many|total|number of).*(operations|missions)",
            "operation_success": r"(success|completion).*(rate|percentage)",
            "operation_types": r"(types? of|what).*(operations|missions)",
            "recent_operations": r"(recent|latest).*(operations|missions)",
            "operation_by_state": r"(operations|missions).*(in|from).*(state|states)",
            # Performance-related queries
            "performance_score": r"(performance|score).*(average|mean)",
            "attendance_rate": r"(attendance).*(rate|percentage)",
            "top_performers": r"(top|best|highest).*(perform|member|volunteer)",
            "performance_trends": r"(performance).*(trend|over time)",
            # Analytics and insights
            "statistics": r"(statistics|stats|summary)",
            "insights": r"(insights|recommendations|analysis)",
            "predictions": r"(predict|forecast|future)",
            "comparisons": r"(compare|comparison|versus|vs)",
            # Time-based queries
            "monthly_data": r"(monthly|month|last month)",
            "yearly_data": r"(yearly|year|annual)",
            "trends": r"(trend|trending|over time)",
            # General queries
            "help": r"(help|what can|capabilities)",
            "dashboard_features": r"(features|sections|modules)",
        }

    def process_query(
        self, query: str, data: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Process natural language query and return structured response"""
        members_df, operations_df, assignments_df = data
        query_lower = query.lower()

        # Match query patterns
        matched_patterns = []
        for pattern_name, pattern in self.query_patterns.items():
            if re.search(pattern, query_lower):
                matched_patterns.append(pattern_name)

        # Generate response based on matched patterns
        if not matched_patterns:
            return self._handle_general_query(query, data)

        # Handle specific queries
        response = {}
        for pattern in matched_patterns[:3]:  # Limit to top 3 matches
            handler_method = f"_handle_{pattern}"
            if hasattr(self, handler_method):
                result = getattr(self, handler_method)(query, data)
                response.update(result)

        return response

    def _handle_total_members(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about total members"""
        members_df, _, _ = data
        total = len(members_df)
        active = len(members_df[members_df["status"] == "Active"])

        return {
            "text": f"RELA Malaysia currently has **{total:,} total members**, with **{active:,} active members** ({active/total*100:.1f}% active rate).",
            "metric": {"Total Members": total, "Active Members": active},
            "chart_data": members_df["status"].value_counts(),
        }

    def _handle_active_members(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about active members"""
        members_df, _, _ = data
        active = len(members_df[members_df["status"] == "Active"])
        total = len(members_df)

        return {
            "text": f"There are **{active:,} active members** out of {total:,} total members ({active/total*100:.1f}% of all members).",
            "metric": {
                "Active Members": active,
                "Percentage": f"{active/total*100:.1f}%",
            },
        }

    def _handle_member_by_state(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about members by state"""
        members_df, _, _ = data
        state_counts = members_df["state"].value_counts()
        top_state = state_counts.index[0]

        # Check if specific state mentioned
        states = members_df["state"].unique()
        mentioned_state = None
        for state in states:
            if state.lower() in query.lower():
                mentioned_state = state
                break

        if mentioned_state:
            count = len(members_df[members_df["state"] == mentioned_state])
            return {
                "text": f"**{mentioned_state}** has **{count:,} members** ({count/len(members_df)*100:.1f}% of total membership).",
                "metric": {f"{mentioned_state} Members": count},
            }
        else:
            return {
                "text": f"**{top_state}** has the most members with **{state_counts.iloc[0]:,} members**. Here's the breakdown by state:",
                "chart_data": state_counts.head(10),
                "metric": {"Top State": top_state, "Members": state_counts.iloc[0]},
            }

    def _handle_average_age(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about average age"""
        members_df, _, _ = data
        avg_age = members_df["age"].mean()
        age_by_state = members_df.groupby("state")["age"].mean().round(1)

        return {
            "text": f"The average age of RELA members is **{avg_age:.1f} years**. Age varies by state with the youngest average in {age_by_state.idxmin()} ({age_by_state.min():.1f} years) and oldest in {age_by_state.idxmax()} ({age_by_state.max():.1f} years).",
            "metric": {"Average Age": f"{avg_age:.1f} years"},
            "chart_data": members_df["age_group"].value_counts(),
        }

    def _handle_gender_distribution(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about gender distribution"""
        members_df, _, _ = data
        gender_dist = members_df["gender"].value_counts()
        gender_pct = (gender_dist / len(members_df) * 100).round(1)

        return {
            "text": f"Gender distribution: **{gender_pct.iloc[0]:.1f}% {gender_dist.index[0]}** and **{gender_pct.iloc[1]:.1f}% {gender_dist.index[1]}**.",
            "metric": {
                f"{gender_dist.index[0]}": f"{gender_pct.iloc[0]:.1f}%",
                f"{gender_dist.index[1]}": f"{gender_pct.iloc[1]:.1f}%",
            },
            "chart_data": gender_dist,
        }

    def _handle_total_operations(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about total operations"""
        _, operations_df, _ = data
        total = len(operations_df)
        completed = len(operations_df[operations_df["status"] == "Completed"])
        success_rate = operations_df["success_rate"].mean()

        return {
            "text": f"RELA has conducted **{total:,} total operations** with **{completed:,} completed** ({completed/total*100:.1f}% completion rate) and an average success rate of **{success_rate:.1%}**.",
            "metric": {
                "Total Operations": total,
                "Completed": completed,
                "Success Rate": f"{success_rate:.1%}",
            },
        }

    def _handle_operation_success(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about operation success rates"""
        _, operations_df, _ = data
        success_rate = operations_df["success_rate"].mean()
        success_by_type = (
            operations_df.groupby("operation_type")["success_rate"]
            .mean()
            .sort_values(ascending=False)
        )

        return {
            "text": f"Overall operation success rate is **{success_rate:.1%}**. **{success_by_type.index[0]}** operations have the highest success rate at **{success_by_type.iloc[0]:.1%}**.",
            "metric": {"Overall Success Rate": f"{success_rate:.1%}"},
            "chart_data": success_by_type,
        }

    def _handle_performance_score(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about performance scores"""
        _, _, assignments_df = data
        avg_performance = assignments_df["performance_score"].mean()
        high_performers = len(assignments_df[assignments_df["performance_score"] >= 8])
        total_assignments = len(assignments_df)

        return {
            "text": f"Average performance score is **{avg_performance:.1f}/10**. **{high_performers:,} assignments** ({high_performers/total_assignments*100:.1f}%) achieved high performance (8+).",
            "metric": {
                "Average Performance": f"{avg_performance:.1f}/10",
                "High Performers": f"{high_performers/total_assignments*100:.1f}%",
            },
        }

    def _handle_attendance_rate(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about attendance rates"""
        _, _, assignments_df = data
        attendance_rate = (
            assignments_df["attendance"].sum() / len(assignments_df)
        ) * 100
        by_state = assignments_df.groupby("state")["attendance"].mean() * 100

        return {
            "text": f"Overall attendance rate is **{attendance_rate:.1f}%**. Best attendance is in **{by_state.idxmax()}** ({by_state.max():.1f}%).",
            "metric": {"Attendance Rate": f"{attendance_rate:.1f}%"},
            "chart_data": by_state.sort_values(ascending=False),
        }

    def _handle_top_performers(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries about top performers"""
        members_df, _, assignments_df = data

        # Calculate member performance
        member_performance = (
            assignments_df.groupby("member_id")
            .agg(
                {
                    "performance_score": "mean",
                    "attendance": "sum",
                    "assignment_id": "count",
                }
            )
            .round(2)
        )

        # Filter members with at least 5 assignments
        qualified_members = member_performance[member_performance["assignment_id"] >= 5]
        top_performers = qualified_members.nlargest(10, "performance_score")

        # Merge with member details
        top_performers_info = members_df.merge(
            top_performers, left_on="member_id", right_index=True
        )

        return {
            "text": f"Top performer: **{top_performers_info.iloc[0]['full_name']}** from **{top_performers_info.iloc[0]['state']}** with **{top_performers_info.iloc[0]['performance_score']:.1f}/10** average performance.",
            "table_data": top_performers_info[
                ["full_name", "state", "rank", "performance_score"]
            ].head(10),
        }

    def _handle_statistics(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle general statistics queries"""
        members_df, operations_df, assignments_df = data

        stats = {
            "Total Members": f"{len(members_df):,}",
            "Active Members": f"{len(members_df[members_df['status'] == 'Active']):,}",
            "Total Operations": f"{len(operations_df):,}",
            "Avg Success Rate": f"{operations_df['success_rate'].mean():.1%}",
            "Avg Performance": f"{assignments_df['performance_score'].mean():.1f}/10",
            "Attendance Rate": f"{(assignments_df['attendance'].sum() / len(assignments_df)) * 100:.1f}%",
        }

        return {
            "text": "Here's a comprehensive overview of RELA Malaysia statistics:",
            "metric": stats,
        }

    def _handle_insights(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries asking for insights and recommendations"""
        members_df, operations_df, assignments_df = data

        insights = []

        # Member insights
        avg_age = members_df["age"].mean()
        if avg_age > 45:
            insights.append(
                f"🔍 **Age Analysis**: Average member age is {avg_age:.1f} years - consider youth recruitment programs"
            )

        # Performance insights
        performance_avg = assignments_df["performance_score"].mean()
        if performance_avg < 7:
            insights.append(
                f"⚠️ **Performance**: Average performance is {performance_avg:.1f}/10 - training programs may help"
            )
        else:
            insights.append(
                f"✅ **Performance**: Excellent average performance of {performance_avg:.1f}/10"
            )

        # Attendance insights
        attendance_rate = (
            assignments_df["attendance"].sum() / len(assignments_df)
        ) * 100
        if attendance_rate < 85:
            insights.append(
                f"📊 **Attendance**: {attendance_rate:.1f}% attendance rate needs improvement"
            )
        else:
            insights.append(
                f"✅ **Attendance**: Strong {attendance_rate:.1f}% attendance rate"
            )

        # Operation insights
        best_op_type = (
            operations_df.groupby("operation_type")["success_rate"].mean().idxmax()
        )
        best_success = (
            operations_df.groupby("operation_type")["success_rate"].mean().max()
        )
        insights.append(
            f"🎯 **Operations**: '{best_op_type}' operations show highest success rate ({best_success:.1%})"
        )

        # Regional insights
        top_state = members_df["state"].value_counts().index[0]
        insights.append(
            f"🏛️ **Regional**: {top_state} leads in member count - potential model for other states"
        )

        return {
            "text": "**Key Insights and Recommendations:**\n\n" + "\n\n".join(insights),
            "insights": insights,
        }

    def _handle_help(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle help queries"""
        help_text = """
**🤖 RELA Analytics Chatbot - How I Can Help You:**

**📊 Member Analytics:**
- "How many members do we have?"
- "What's the average age?"
- "Show me gender distribution"
- "Members in Selangor"

**🚨 Operations Data:**
- "Total operations this year"
- "What's our success rate?"
- "Recent operations"
- "Operation types"

**📈 Performance Metrics:**
- "Average performance score"
- "Top performers"
- "Attendance rate"
- "Performance trends"

**🔍 Analytics & Insights:**
- "Give me insights"
- "Show statistics"
- "Compare states"
- "Predict future trends"

**💡 Try asking natural questions like:**
- "Which state has the most volunteers?"
- "What's our best operation type?"
- "How is performance trending?"
- "Show me key statistics"
        """

        return {"text": help_text, "help": True}

    def _handle_general_query(self, query: str, data: Tuple) -> Dict[str, Any]:
        """Handle queries that don't match specific patterns"""
        members_df, operations_df, assignments_df = data

        # Try to extract numbers or keywords for basic analysis
        if "state" in query.lower():
            state_data = members_df["state"].value_counts()
            return {
                "text": f"Here's the state-wise member distribution. **{state_data.index[0]}** leads with **{state_data.iloc[0]:,} members**.",
                "chart_data": state_data.head(10),
            }

        if any(
            word in query.lower() for word in ["compare", "comparison", "versus", "vs"]
        ):
            return {
                "text": "I can help you compare different metrics! Try asking: 'Compare performance by state' or 'Compare operation success rates'.",
                "suggestion": True,
            }

        # Default response with suggestions
        return {
            "text": "I'd be happy to help! I can provide information about members, operations, performance, and analytics. Try asking specific questions like 'How many members do we have?' or 'What's our success rate?' Type 'help' for more examples.",
            "suggestion": True,
        }

    def display_response(self, response: Dict[str, Any], query: str):
        """Display chatbot response with appropriate visualizations"""

        # Display main text response
        if "text" in response:
            st.markdown(response["text"])

        # Display metrics if available
        if "metric" in response:
            cols = st.columns(len(response["metric"]))
            for i, (key, value) in enumerate(response["metric"].items()):
                with cols[i]:
                    st.metric(key, value)

        # Display charts if available
        if "chart_data" in response:
            data = response["chart_data"]
            if isinstance(data, pd.Series):
                if len(data) <= 15:  # Bar chart for reasonable number of items
                    fig = px.bar(
                        x=data.values,
                        y=data.index,
                        orientation="h",
                        title=f"Distribution",
                        color=data.values,
                        color_continuous_scale="Blues",
                    )
                    fig.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:  # Top 10 for many items
                    fig = px.bar(
                        x=data.head(10).values,
                        y=data.head(10).index,
                        orientation="h",
                        title=f"Top 10 Distribution",
                        color=data.head(10).values,
                        color_continuous_scale="Blues",
                    )
                    fig.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

        # Display tables if available
        if "table_data" in response:
            st.dataframe(response["table_data"], use_container_width=True)

        # Add to chat history
        st.session_state.chat_history.append(
            {
                "query": query,
                "response": (
                    response["text"] if "text" in response else "Response generated"
                ),
                "timestamp": datetime.now(),
            }
        )

    def show_chat_interface(
        self, data: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
    ):
        """Display the main chatbot interface"""
        lang = self.language

        st.markdown(f"## {get_text(lang, 'chatbot', '🤖 RELA Analytics Chatbot')}")
        st.markdown(
            get_text(
                lang,
                "chatbot_description",
                "Ask me anything about the dashboard data! I can provide insights, statistics, and answer your questions in natural language.",
            )
        )

        # Quick action buttons
        st.markdown(f"### {get_text(lang, 'quick_questions', '🚀 Quick Questions')}")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button(f"📊 {get_text(lang, 'show_statistics', 'Show Statistics')}"):
                response = self._handle_statistics("statistics", data)
                self.display_response(
                    response,
                    get_text(lang, "show_statistics", "Show overall statistics"),
                )

        with col2:
            if st.button(f"🔍 {get_text(lang, 'key_insights', 'Key Insights')}"):
                response = self._handle_insights("insights", data)
                self.display_response(
                    response, get_text(lang, "key_insights", "Give me key insights")
                )

        with col3:
            if st.button(f"👥 {get_text(lang, 'member_info', 'Member Info')}"):
                response = self._handle_total_members("total members", data)
                self.display_response(response, "How many members do we have?")

        with col4:
            if st.button(f"🚨 {get_text(lang, 'operations_info', 'Operations')}"):
                response = self._handle_total_operations("total operations", data)
                self.display_response(response, "Tell me about operations")

        st.markdown("---")

        # Main chat interface
        st.markdown(f"### {get_text(lang, 'ask_question', '💬 Ask Your Question')}")

        # Chat input
        user_query = st.text_input(
            get_text(lang, "type_question", "Type your question here..."),
            placeholder="e.g., How many active members do we have in Selangor?",
            key="chat_input",
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            ask_button = st.button(
                f"🚀 {get_text(lang, 'ask_button', 'Ask')}", type="primary"
            )
        with col2:
            if st.button(f"🆘 {get_text(lang, 'help_button', 'Help')}"):
                response = self._handle_help("help", data)
                self.display_response(response, "help")

        # Process query when button is clicked or Enter is pressed
        if ask_button and user_query:
            with st.spinner(
                get_text(lang, "processing_question", "🔍 Analyzing your question...")
            ):
                response = self.process_query(user_query, data)
                st.markdown("---")
                st.markdown(
                    f"**{get_text(lang, 'your_question', 'Your Question')}:** {user_query}"
                )
                st.markdown(f"**{get_text(lang, 'answer', 'Answer')}:**")
                self.display_response(response, user_query)

        # Display recent chat history
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown(
                f"### {get_text(lang, 'recent_questions', '📜 Recent Questions')}"
            )

            # Show last 5 interactions
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
                with st.expander(
                    f"Q: {chat['query'][:50]}..."
                    if len(chat["query"]) > 50
                    else f"Q: {chat['query']}"
                ):
                    st.markdown(
                        f"**{get_text(lang, 'asked', 'Asked')}:** {chat['timestamp'].strftime('%Y-%m-%d %H:%M')}"
                    )
                    st.markdown(
                        f"**{get_text(lang, 'answer', 'Answer')}:** {chat['response']}"
                    )

        # Example queries section
        st.markdown("---")
        st.markdown(
            f"### {get_text(lang, 'example_questions', '💡 Example Questions You Can Ask')}"
        )

        examples = [
            "How many active members do we have?",
            "What's the average performance score?",
            "Which state has the most volunteers?",
            "Show me attendance rates by state",
            "What's our operation success rate?",
            "Give me insights about member demographics",
            "Compare performance across different states",
            "What are the top performing operation types?",
            "Show me monthly trends",
            "Which rank has the best performance?",
        ]

        # Display examples in columns
        cols = st.columns(2)
        for i, example in enumerate(examples):
            with cols[i % 2]:
                if st.button(f"📝 {example}", key=f"example_{i}"):
                    with st.spinner(
                        get_text(
                            lang,
                            "processing_question",
                            "🔍 Processing example question...",
                        )
                    ):
                        response = self.process_query(example, data)
                        st.markdown("---")
                        st.markdown(
                            f"**{get_text(lang, 'your_question', 'Example Question')}:** {example}"
                        )
                        st.markdown(f"**{get_text(lang, 'answer', 'Answer')}:**")
                        self.display_response(response, example)
