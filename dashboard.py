import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json

class Dashboard:
    def __init__(self):
        self.colors = {
            'primary': '#1f4e79',
            'secondary': '#2d5aa0',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8'
        }
    
    def show_overview(self, data):
        """Main overview dashboard"""
        members_df, operations_df, assignments_df = data
        
        st.markdown("## 📊 Executive Dashboard Overview")
        
        # Key Performance Indicators
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_members = len(members_df)
            active_members = len(members_df[members_df['status'] == 'Active'])
            st.metric(
                "👥 Total Members",
                f"{total_members:,}",
                f"+{active_members:,} Active"
            )
        
        with col2:
            total_ops = len(operations_df)
            completed_ops = len(operations_df[operations_df['status'] == 'Completed'])
            completion_rate = (completed_ops / total_ops * 100) if total_ops > 0 else 0
            st.metric(
                "🚨 Total Operations",
                f"{total_ops:,}",
                f"{completion_rate:.1f}% Complete"
            )
        
        with col3:
            total_assignments = len(assignments_df)
            attended = len(assignments_df[assignments_df['attendance'] == True])
            attendance_rate = (attended / total_assignments * 100) if total_assignments > 0 else 0
            st.metric(
                "📋 Assignments",
                f"{total_assignments:,}",
                f"{attendance_rate:.1f}% Attendance"
            )
        
        with col4:
            avg_performance = assignments_df['performance_score'].mean()
            st.metric(
                "⭐ Avg Performance",
                f"{avg_performance:.1f}/10",
                "Excellent"
            )
        
        with col5:
            states_covered = members_df['state'].nunique()
            st.metric(
                "🏛️ States/Territories",
                f"{states_covered}/16",
                "Full Coverage"
            )
        
        st.markdown("---")
        
        # Charts row 1
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Member Growth Trend")
            # Monthly registration trend
            members_df['join_month'] = pd.to_datetime(members_df['join_date']).dt.to_period('M')
            monthly_joins = members_df.groupby('join_month').size().reset_index(name='new_members')
            monthly_joins['join_month'] = monthly_joins['join_month'].astype(str)
            
            fig = px.line(
                monthly_joins.tail(24),  # Last 24 months
                x='join_month',
                y='new_members',
                title="New Member Registrations (Last 24 Months)",
                color_discrete_sequence=[self.colors['primary']]
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Operations by Type")
            ops_by_type = operations_df['operation_type'].value_counts()
            
            fig = px.pie(
                values=ops_by_type.values,
                names=ops_by_type.index,
                title="Distribution of Operation Types",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Charts row 2
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🗺️ State-wise Member Distribution")
            state_members = members_df['state'].value_counts()
            
            fig = px.bar(
                x=state_members.values,
                y=state_members.index,
                orientation='h',
                title="RELA Members by State",
                color=state_members.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Performance Analytics")
            
            # Performance distribution
            perf_ranges = pd.cut(
                assignments_df['performance_score'].dropna(),
                bins=[0, 5, 6, 7, 8, 9, 10],
                labels=['0-5', '5-6', '6-7', '7-8', '8-9', '9-10']
            ).value_counts().sort_index()
            
            fig = px.bar(
                x=perf_ranges.index,
                y=perf_ranges.values,
                title="Performance Score Distribution",
                color=perf_ranges.values,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Activity heatmap
        st.markdown("### 🕒 Operational Activity Heatmap")
        
        # Create activity by day of week and hour
        operations_df['hour'] = pd.to_datetime(operations_df['start_date']).dt.hour
        operations_df['day_of_week'] = pd.to_datetime(operations_df['start_date']).dt.day_name()
        
        activity_heatmap = operations_df.groupby(['day_of_week', 'hour']).size().reset_index(name='operations')
        activity_pivot = activity_heatmap.pivot(index='day_of_week', columns='hour', values='operations').fillna(0)
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        activity_pivot = activity_pivot.reindex(day_order)
        
        fig = px.imshow(
            activity_pivot,
            labels=dict(x="Hour of Day", y="Day of Week", color="Operations"),
            title="Operations Activity Heatmap",
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def show_member_analytics(self, data):
        """Member-focused analytics"""
        members_df, operations_df, assignments_df = data
        
        st.markdown("## 👥 Member Analytics Dashboard")
        
        # Member demographics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎂 Age Distribution")
            age_dist = members_df['age_group'].value_counts()
            fig = px.bar(
                x=age_dist.index,
                y=age_dist.values,
                title="Members by Age Group",
                color=age_dist.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 👨‍👩‍👧‍👦 Gender Distribution")
            gender_dist = members_df['gender'].value_counts()
            fig = px.pie(
                values=gender_dist.values,
                names=gender_dist.index,
                title="Gender Distribution",
                color_discrete_sequence=['#FF6B6B', '#4ECDC4']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.markdown("### 🌍 Ethnicity Distribution")
            ethnic_dist = members_df['ethnicity'].value_counts()
            fig = px.pie(
                values=ethnic_dist.values,
                names=ethnic_dist.index,
                title="Ethnic Composition",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Education and Rank Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎓 Education Levels")
            edu_dist = members_df['education_level'].value_counts()
            fig = px.bar(
                x=edu_dist.index,
                y=edu_dist.values,
                title="Education Level Distribution",
                color=edu_dist.values,
                color_continuous_scale='Blues'
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🏆 Rank Distribution")
            rank_dist = members_df['rank'].value_counts()
            fig = px.bar(
                x=rank_dist.values,
                y=rank_dist.index,
                orientation='h',
                title="RELA Rank Hierarchy",
                color=rank_dist.values,
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Service analysis
        st.markdown("### ⏰ Years of Service Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Service duration histogram
            fig = px.histogram(
                members_df,
                x='years_of_service',
                nbins=20,
                title="Distribution of Years of Service",
                color_discrete_sequence=[self.colors['primary']]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Service vs rank analysis
            service_rank = members_df.groupby('rank')['years_of_service'].mean().sort_values(ascending=False)
            fig = px.bar(
                x=service_rank.values,
                y=service_rank.index,
                orientation='h',
                title="Average Years of Service by Rank",
                color=service_rank.values,
                color_continuous_scale='RdYlBu'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top performers
        st.markdown("### ⭐ Top Performing Members")
        
        # Merge member data with performance
        member_performance = assignments_df.groupby('member_id').agg({
            'performance_score': 'mean',
            'attendance': 'sum',
            'assignment_id': 'count'
        }).round(2)
        member_performance.columns = ['avg_performance', 'total_attendance', 'total_assignments']
        
        # Merge with member details
        top_performers = members_df.merge(member_performance, left_on='member_id', right_index=True)
        top_performers = top_performers[top_performers['total_assignments'] >= 5]  # Min 5 assignments
        top_performers = top_performers.nlargest(20, 'avg_performance')
        
        st.dataframe(
            top_performers[['member_id', 'full_name', 'state', 'rank', 'avg_performance', 'total_assignments', 'total_attendance']],
            use_container_width=True
        )
    
    def show_operations(self, data):
        """Operations analytics dashboard"""
        members_df, operations_df, assignments_df = data
        
        st.markdown("## 🚨 Operations Analytics Dashboard")
        
        # Operations summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_ops = len(operations_df)
            st.metric("Total Operations", f"{total_ops:,}")
        
        with col2:
            avg_duration = operations_df['duration_hours'].mean()
            st.metric("Avg Duration", f"{avg_duration:.1f} hours")
        
        with col3:
            total_volunteers = operations_df['volunteers_assigned'].sum()
            st.metric("Volunteers Deployed", f"{total_volunteers:,}")
        
        with col4:
            avg_success = operations_df['success_rate'].mean()
            st.metric("Success Rate", f"{avg_success:.1%}")
        
        # Operations by complexity and status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Operations by Complexity")
            complexity_dist = operations_df['complexity'].value_counts()
            fig = px.pie(
                values=complexity_dist.values,
                names=complexity_dist.index,
                title="Operation Complexity Distribution",
                color_discrete_sequence=['#28a745', '#ffc107', '#fd7e14', '#dc3545']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Operations Status")
            status_dist = operations_df['status'].value_counts()
            fig = px.bar(
                x=status_dist.index,
                y=status_dist.values,
                title="Operations by Status",
                color=status_dist.values,
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Time-based analysis
        st.markdown("### ⏰ Temporal Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Operations by time of day
            time_dist = operations_df['time_of_day'].value_counts()
            fig = px.bar(
                x=time_dist.index,
                y=time_dist.values,
                title="Operations by Time of Day",
                color=time_dist.values,
                color_continuous_scale='Sunset'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Monthly operations trend
            operations_df['month'] = pd.to_datetime(operations_df['start_date']).dt.to_period('M')
            monthly_ops = operations_df.groupby('month').size().reset_index(name='operations')
            monthly_ops['month'] = monthly_ops['month'].astype(str)
            
            fig = px.line(
                monthly_ops,
                x='month',
                y='operations',
                title="Monthly Operations Trend",
                color_discrete_sequence=[self.colors['primary']]
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Resource allocation
        st.markdown("### 🚗 Resource Allocation Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Volunteers vs Success Rate
            fig = px.scatter(
                operations_df,
                x='volunteers_assigned',
                y='success_rate',
                color='complexity',
                size='duration_hours',
                title="Volunteers Assigned vs Success Rate",
                hover_data=['operation_type']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Budget allocation
            budget_by_type = operations_df.groupby('operation_type')['budget_allocated'].mean().sort_values(ascending=False)
            fig = px.bar(
                x=budget_by_type.values,
                y=budget_by_type.index,
                orientation='h',
                title="Average Budget by Operation Type",
                color=budget_by_type.values,
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent operations table
        st.markdown("### 📋 Recent Operations")
        recent_ops = operations_df.nlargest(20, 'start_date')
        st.dataframe(
            recent_ops[['operation_id', 'operation_name', 'operation_type', 'state', 'status', 'complexity', 'volunteers_assigned', 'success_rate']],
            use_container_width=True
        )
    
    def show_performance(self, data):
        """Performance analytics dashboard"""
        members_df, operations_df, assignments_df = data
        
        st.markdown("## 📊 Performance Analytics Dashboard")
        
        # Performance KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_performance = assignments_df['performance_score'].mean()
            st.metric("Average Performance", f"{avg_performance:.1f}/10")
        
        with col2:
            attendance_rate = (assignments_df['attendance'].sum() / len(assignments_df)) * 100
            st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
        
        with col3:
            high_performers = len(assignments_df[assignments_df['performance_score'] >= 8])
            total_with_scores = len(assignments_df.dropna(subset=['performance_score']))
            high_perf_rate = (high_performers / total_with_scores) * 100 if total_with_scores > 0 else 0
            st.metric("High Performers", f"{high_perf_rate:.1f}%")
        
        with col4:
            avg_feedback = assignments_df['feedback_score'].mean()
            st.metric("Avg Feedback", f"{avg_feedback:.1f}/5")
        
        # Performance trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Performance Trend Over Time")
            assignments_df['month'] = pd.to_datetime(assignments_df['assignment_date']).dt.to_period('M')
            monthly_perf = assignments_df.groupby('month')['performance_score'].mean().reset_index()
            monthly_perf['month'] = monthly_perf['month'].astype(str)
            
            fig = px.line(
                monthly_perf,
                x='month',
                y='performance_score',
                title="Monthly Average Performance Score",
                color_discrete_sequence=[self.colors['success']]
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Performance by Assignment Type")
            perf_by_type = assignments_df.groupby('assignment_type')['performance_score'].mean().sort_values(ascending=False)
            fig = px.bar(
                x=perf_by_type.values,
                y=perf_by_type.index,
                orientation='h',
                title="Average Performance by Assignment Type",
                color=perf_by_type.values,
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # State performance comparison
        st.markdown("### 🏛️ State Performance Comparison")
        
        state_performance = assignments_df.groupby('state').agg({
            'performance_score': 'mean',
            'attendance': lambda x: (x.sum() / len(x)) * 100,
            'feedback_score': 'mean'
        }).round(2)
        state_performance.columns = ['Avg Performance', 'Attendance Rate (%)', 'Avg Feedback']
        
        fig = px.bar(
            state_performance.reset_index(),
            x='state',
            y='Avg Performance',
            title="Average Performance Score by State",
            color='Avg Performance',
            color_continuous_scale='Viridis'
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance correlation analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔗 Training vs Performance")
            # Merge with member data to get training info
            perf_training = assignments_df.merge(
                members_df[['member_id', 'training_completed']],
                on='member_id'
            )
            
            fig = px.scatter(
                perf_training,
                x='training_completed',
                y='performance_score',
                title="Training Completed vs Performance Score",
                trendline="ols",
                color_discrete_sequence=[self.colors['info']]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⏱️ Duration vs Performance")
            fig = px.scatter(
                assignments_df,
                x='duration_hours',
                y='performance_score',
                color='assignment_type',
                title="Assignment Duration vs Performance",
                size='feedback_score',
                hover_data=['attendance']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top performing states table
        st.markdown("### 🏆 State Performance Rankings")
        st.dataframe(
            state_performance.sort_values('Avg Performance', ascending=False),
            use_container_width=True
        )
    
    def show_regional_analysis(self, data):
        """Regional analysis dashboard"""
        members_df, operations_df, assignments_df = data
        
        st.markdown("## 🗺️ Regional Analysis Dashboard")
        
        # Regional overview
        st.markdown("### 📊 Regional Overview")
        
        regional_stats = members_df.groupby('state').agg({
            'member_id': 'count',
            'years_of_service': 'mean',
            'operations_participated': 'mean'
        }).round(1)
        regional_stats.columns = ['Total Members', 'Avg Years Service', 'Avg Operations']
        
        # Add operations data
        ops_by_state = operations_df.groupby('state').size()
        regional_stats['Total Operations'] = ops_by_state
        regional_stats['Total Operations'] = regional_stats['Total Operations'].fillna(0)
        
        # Calculate members per operation ratio
        regional_stats['Members per Operation'] = (
            regional_stats['Total Members'] / regional_stats['Total Operations']
        ).round(1)
        regional_stats['Members per Operation'] = regional_stats['Members per Operation'].replace([np.inf], 0)
        
        st.dataframe(regional_stats.sort_values('Total Members', ascending=False), use_container_width=True)
        
        # Map visualization (simulated)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏛️ Members Distribution by State")
            state_members = members_df['state'].value_counts()
            fig = px.treemap(
                names=state_members.index,
                values=state_members.values,
                title="RELA Members Distribution (Treemap)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🚨 Operations Intensity")
            ops_intensity = operations_df['state'].value_counts()
            fig = px.bar(
                x=ops_intensity.values,
                y=ops_intensity.index,
                orientation='h',
                title="Operations by State",
                color=ops_intensity.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # District analysis
        st.markdown("### 🏘️ District-Level Analysis")
        
        selected_state = st.selectbox(
            "Select State for District Analysis",
            options=members_df['state'].unique()
        )
        
        if selected_state:
            state_data = members_df[members_df['state'] == selected_state]
            district_stats = state_data.groupby('district').agg({
                'member_id': 'count',
                'years_of_service': 'mean',
                'age': 'mean'
            }).round(1)
            district_stats.columns = ['Members', 'Avg Years Service', 'Avg Age']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    district_stats.reset_index(),
                    x='district',
                    y='Members',
                    title=f"Members by District in {selected_state}",
                    color='Members',
                    color_continuous_scale='Blues'
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(
                    district_stats.reset_index(),
                    x='Avg Years Service',
                    y='Avg Age',
                    size='Members',
                    hover_name='district',
                    title=f"Experience vs Age by District in {selected_state}"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def show_trends(self, data):
        """Trends analysis dashboard"""
        members_df, operations_df, assignments_df = data
        
        st.markdown("## 📈 Trends Analysis Dashboard")
        
        # Recruitment trends
        st.markdown("### 👥 Recruitment Trends")
        
        members_df['join_year'] = pd.to_datetime(members_df['join_date']).dt.year
        yearly_recruitment = members_df.groupby('join_year').size().reset_index(name='new_members')
        
        fig = px.bar(
            yearly_recruitment,
            x='join_year',
            y='new_members',
            title="Annual Recruitment Trend",
            color='new_members',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Seasonal patterns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌍 Seasonal Operation Patterns")
            operations_df['month'] = pd.to_datetime(operations_df['start_date']).dt.month
            monthly_ops = operations_df.groupby('month').size().reset_index(name='operations')
            monthly_ops['month_name'] = pd.to_datetime(monthly_ops['month'], format='%m').dt.month_name()
            
            fig = px.line(
                monthly_ops,
                x='month_name',
                y='operations',
                title="Seasonal Operations Pattern",
                color_discrete_sequence=[self.colors['primary']]
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Assignment Patterns")
            assignments_df['month'] = pd.to_datetime(assignments_df['assignment_date']).dt.month
            monthly_assignments = assignments_df.groupby('month').size().reset_index(name='assignments')
            monthly_assignments['month_name'] = pd.to_datetime(monthly_assignments['month'], format='%m').dt.month_name()
            
            fig = px.line(
                monthly_assignments,
                x='month_name',
                y='assignments',
                title="Monthly Assignment Volume",
                color_discrete_sequence=[self.colors['success']]
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Multi-year comparison
        st.markdown("### 📅 Multi-Year Comparison")
        
        # Operations by year
        operations_df['year'] = pd.to_datetime(operations_df['start_date']).dt.year
        ops_by_year_type = operations_df.groupby(['year', 'operation_type']).size().reset_index(name='count')
        
        fig = px.bar(
            ops_by_year_type,
            x='year',
            y='count',
            color='operation_type',
            title="Operations by Type and Year",
            barmode='stack'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance trends
        st.markdown("### ⭐ Performance Evolution")
        
        assignments_df['year'] = pd.to_datetime(assignments_df['assignment_date']).dt.year
        yearly_performance = assignments_df.groupby('year').agg({
            'performance_score': 'mean',
            'attendance': lambda x: (x.sum() / len(x)) * 100,
            'feedback_score': 'mean'
        }).round(2)
        yearly_performance.columns = ['Avg Performance', 'Attendance Rate', 'Avg Feedback']
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Performance Score', 'Attendance Rate', 'Feedback Score')
        )
        
        fig.add_trace(
            go.Scatter(
                x=yearly_performance.index,
                y=yearly_performance['Avg Performance'],
                mode='lines+markers',
                name='Performance'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=yearly_performance.index,
                y=yearly_performance['Attendance Rate'],
                mode='lines+markers',
                name='Attendance'
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=yearly_performance.index,
                y=yearly_performance['Avg Feedback'],
                mode='lines+markers',
                name='Feedback'
            ),
            row=1, col=3
        )
        
        fig.update_layout(height=400, title_text="Performance Metrics Trends")
        st.plotly_chart(fig, use_container_width=True)
    
    def show_reports(self, data):
        """Reports generation dashboard"""
        members_df, operations_df, assignments_df = data
        
        st.markdown("## 📋 Reports Dashboard")
        
        # Report selection
        report_type = st.selectbox(
            "Select Report Type",
            [
                "Executive Summary",
                "Member Demographics Report",
                "Operations Analysis Report",
                "Performance Report",
                "Regional Breakdown Report"
            ]
        )
        
        if report_type == "Executive Summary":
            self._generate_executive_summary(members_df, operations_df, assignments_df)
        elif report_type == "Member Demographics Report":
            self._generate_demographics_report(members_df)
        elif report_type == "Operations Analysis Report":
            self._generate_operations_report(operations_df)
        elif report_type == "Performance Report":
            self._generate_performance_report(assignments_df, members_df)
        elif report_type == "Regional Breakdown Report":
            self._generate_regional_report(members_df, operations_df)
        
        # Export options
        st.markdown("---")
        st.markdown("### 📤 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Members Data"):
                csv = members_df.to_csv(index=False)
                st.download_button(
                    label="Download Members CSV",
                    data=csv,
                    file_name=f"rela_members_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("🚨 Export Operations Data"):
                csv = operations_df.to_csv(index=False)
                st.download_button(
                    label="Download Operations CSV",
                    data=csv,
                    file_name=f"rela_operations_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("📋 Export Assignments Data"):
                csv = assignments_df.to_csv(index=False)
                st.download_button(
                    label="Download Assignments CSV",
                    data=csv,
                    file_name=f"rela_assignments_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    def _generate_executive_summary(self, members_df, operations_df, assignments_df):
        """Generate executive summary report"""
        st.markdown("### 📊 Executive Summary Report")
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 👥 Membership Overview")
            st.write(f"- Total Members: {len(members_df):,}")
            st.write(f"- Active Members: {len(members_df[members_df['status'] == 'Active']):,}")
            st.write(f"- Average Age: {members_df['age'].mean():.1f} years")
            st.write(f"- Average Service: {members_df['years_of_service'].mean():.1f} years")
        
        with col2:
            st.markdown("#### 🚨 Operations Summary")
            st.write(f"- Total Operations: {len(operations_df):,}")
            st.write(f"- Completed: {len(operations_df[operations_df['status'] == 'Completed']):,}")
            st.write(f"- Success Rate: {operations_df['success_rate'].mean():.1%}")
            st.write(f"- Avg Duration: {operations_df['duration_hours'].mean():.1f} hours")
        
        with col3:
            st.markdown("#### 📋 Performance Metrics")
            st.write(f"- Total Assignments: {len(assignments_df):,}")
            st.write(f"- Attendance Rate: {(assignments_df['attendance'].sum()/len(assignments_df)*100):.1f}%")
            st.write(f"- Avg Performance: {assignments_df['performance_score'].mean():.1f}/10")
            st.write(f"- Avg Feedback: {assignments_df['feedback_score'].mean():.1f}/5")
        
        # Top insights
        st.markdown("#### 🔍 Key Insights")
        st.write("- Highest performing state: " + 
                assignments_df.groupby('state')['performance_score'].mean().idxmax())
        st.write("- Most common operation: " + operations_df['operation_type'].value_counts().index[0])
        st.write("- Peak operation time: " + operations_df['time_of_day'].value_counts().index[0])
        st.write("- Largest age group: " + members_df['age_group'].value_counts().index[0])
    
    def _generate_demographics_report(self, members_df):
        """Generate demographics report"""
        st.markdown("### 👥 Member Demographics Report")
        
        # Demographics breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Gender Distribution")
            gender_counts = members_df['gender'].value_counts()
            for gender, count in gender_counts.items():
                percentage = (count / len(members_df)) * 100
                st.write(f"- {gender}: {count:,} ({percentage:.1f}%)")
        
        with col2:
            st.markdown("#### Age Group Distribution")
            age_counts = members_df['age_group'].value_counts()
            for age_group, count in age_counts.items():
                percentage = (count / len(members_df)) * 100
                st.write(f"- {age_group}: {count:,} ({percentage:.1f}%)")
        
        # State distribution
        st.markdown("#### State-wise Distribution")
        state_stats = members_df.groupby('state').agg({
            'member_id': 'count',
            'age': 'mean',
            'years_of_service': 'mean'
        }).round(1)
        state_stats.columns = ['Members', 'Avg Age', 'Avg Service Years']
        st.dataframe(state_stats.sort_values('Members', ascending=False), use_container_width=True)
    
    def _generate_operations_report(self, operations_df):
        """Generate operations analysis report"""
        st.markdown("### 🚨 Operations Analysis Report")
        
        # Operations summary by type
        ops_summary = operations_df.groupby('operation_type').agg({
            'operation_id': 'count',
            'duration_hours': 'mean',
            'volunteers_assigned': 'mean',
            'success_rate': 'mean',
            'budget_allocated': 'mean'
        }).round(2)
        ops_summary.columns = ['Count', 'Avg Duration', 'Avg Volunteers', 'Success Rate', 'Avg Budget']
        
        st.dataframe(ops_summary.sort_values('Count', ascending=False), use_container_width=True)
        
        # Complexity analysis
        st.markdown("#### Complexity Analysis")
        complexity_stats = operations_df.groupby('complexity').agg({
            'operation_id': 'count',
            'volunteers_assigned': 'mean',
            'success_rate': 'mean'
        }).round(2)
        complexity_stats.columns = ['Operations', 'Avg Volunteers', 'Success Rate']
        st.dataframe(complexity_stats, use_container_width=True)
    
    def _generate_performance_report(self, assignments_df, members_df):
        """Generate performance analysis report"""
        st.markdown("### ⭐ Performance Analysis Report")
        
        # Overall performance metrics
        st.markdown("#### Overall Performance Metrics")
        st.write(f"- Average Performance Score: {assignments_df['performance_score'].mean():.2f}/10")
        st.write(f"- Attendance Rate: {(assignments_df['attendance'].sum()/len(assignments_df)*100):.1f}%")
        st.write(f"- High Performers (8+ score): {len(assignments_df[assignments_df['performance_score'] >= 8]):,}")
        
        # Performance by assignment type
        st.markdown("#### Performance by Assignment Type")
        perf_by_type = assignments_df.groupby('assignment_type').agg({
            'performance_score': 'mean',
            'attendance': lambda x: (x.sum() / len(x)) * 100,
            'assignment_id': 'count'
        }).round(2)
        perf_by_type.columns = ['Avg Performance', 'Attendance Rate (%)', 'Total Assignments']
        st.dataframe(perf_by_type.sort_values('Avg Performance', ascending=False), use_container_width=True)
    
    def _generate_regional_report(self, members_df, operations_df):
        """Generate regional breakdown report"""
        st.markdown("### 🗺️ Regional Breakdown Report")
        
        # Regional summary
        regional_summary = members_df.groupby('state').agg({
            'member_id': 'count',
            'age': 'mean',
            'years_of_service': 'mean'
        }).round(1)
        
        # Add operations data
        ops_by_state = operations_df.groupby('state').size()
        regional_summary['Operations'] = ops_by_state
        regional_summary['Operations'] = regional_summary['Operations'].fillna(0)
        
        regional_summary.columns = ['Members', 'Avg Age', 'Avg Service', 'Operations']
        regional_summary['Members per Operation'] = (regional_summary['Members'] / regional_summary['Operations']).round(1)
        regional_summary['Members per Operation'] = regional_summary['Members per Operation'].replace([np.inf], 0)
        
        st.dataframe(regional_summary.sort_values('Members', ascending=False), use_container_width=True)
