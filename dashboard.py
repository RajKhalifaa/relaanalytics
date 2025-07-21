import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json

from translations import get_text
from ml_model_manager import MLModelManager
from forecasting_engine import ForecastingEngine

class Dashboard:
    def __init__(self, language='en'):
        self.language = language
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
        lang = self.language
        
        st.markdown(f"## 📊 {get_text(lang, 'overview', 'Executive Dashboard Overview')}")
        
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
            # Monthly registration trend - clean data first
            members_df['join_month'] = pd.to_datetime(members_df['join_date']).dt.to_period('M')
            monthly_joins = members_df.dropna(subset=['join_date']).groupby('join_month').size().reset_index(name='new_members')
            monthly_joins['join_month'] = monthly_joins['join_month'].astype(str)
            monthly_joins = monthly_joins[monthly_joins['new_members'] > 0]  # Ensure positive values
            
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
            # Monthly operations trend - clean data first
            operations_df['month'] = pd.to_datetime(operations_df['start_date']).dt.to_period('M')
            monthly_ops = operations_df.dropna(subset=['start_date']).groupby('month').size().reset_index(name='operations')
            monthly_ops['month'] = monthly_ops['month'].astype(str)
            monthly_ops = monthly_ops[monthly_ops['operations'] > 0]  # Ensure positive values
            
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
            # Volunteers vs Success Rate - clean data first
            clean_ops = operations_df.dropna(subset=['volunteers_assigned', 'success_rate', 'duration_hours'])
            clean_ops = clean_ops[clean_ops['duration_hours'] > 0]
            
            fig = px.scatter(
                clean_ops,
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
            avg_performance = assignments_df['performance_score'].dropna().mean()
            st.metric("Average Performance", f"{avg_performance:.1f}/10")
        
        with col2:
            clean_attendance = assignments_df.dropna(subset=['attendance'])
            attendance_rate = (clean_attendance['attendance'].sum() / len(clean_attendance)) * 100 if len(clean_attendance) > 0 else 0
            st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
        
        with col3:
            valid_scores = assignments_df.dropna(subset=['performance_score'])
            high_performers = len(valid_scores[valid_scores['performance_score'] >= 8])
            total_with_scores = len(valid_scores)
            high_perf_rate = (high_performers / total_with_scores) * 100 if total_with_scores > 0 else 0
            st.metric("High Performers", f"{high_perf_rate:.1f}%")
        
        with col4:
            avg_feedback = assignments_df['feedback_score'].dropna().mean()
            st.metric("Avg Feedback", f"{avg_feedback:.1f}/5")
        
        # Performance trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Performance Trend Over Time")
            # Clean performance data first
            assignments_df['month'] = pd.to_datetime(assignments_df['assignment_date']).dt.to_period('M')
            clean_assignments = assignments_df.dropna(subset=['assignment_date', 'performance_score'])
            clean_assignments = clean_assignments[clean_assignments['performance_score'] > 0]
            monthly_perf = clean_assignments.groupby('month')['performance_score'].mean().reset_index()
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
        
        # State performance comparison - clean data first
        st.markdown("### 🏛️ State Performance Comparison")
        
        # Clean assignments data for state analysis
        clean_state_data = assignments_df.dropna(subset=['state', 'performance_score', 'feedback_score'])
        
        state_performance = clean_state_data.groupby('state').agg({
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
            # Merge with member data to get training info and clean data
            perf_training = assignments_df.merge(
                members_df[['member_id', 'training_completed']],
                on='member_id'
            )
            
            # Clean data: remove NaN values and ensure valid ranges
            perf_training_clean = perf_training.dropna(subset=['training_completed', 'performance_score'])
            perf_training_clean = perf_training_clean[
                (perf_training_clean['training_completed'] >= 0) & 
                (perf_training_clean['performance_score'] > 0)
            ]
            
            fig = px.scatter(
                perf_training_clean,
                x='training_completed',
                y='performance_score',
                title="Training Completed vs Performance Score",
                trendline="ols",
                color_discrete_sequence=[self.colors['info']]
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⏱️ Duration vs Performance")
            # Filter out NaN values and ensure valid data for scatter plot
            clean_assignments = assignments_df.dropna(subset=['duration_hours', 'performance_score', 'feedback_score'])
            clean_assignments = clean_assignments[clean_assignments['feedback_score'] > 0]
            
            fig = px.scatter(
                clean_assignments,
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
                # Ensure no NaN values in district stats
                district_clean = district_stats.reset_index().dropna()
                district_clean = district_clean[district_clean['Members'] > 0]
                
                fig = px.scatter(
                    district_clean,
                    x='Avg Years Service',
                    y='Avg Age',
                    size='Members',
                    hover_name='district',
                    title=f"Experience vs Age by District in {selected_state}"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def show_trends(self, data):
        """Trends analysis dashboard with predictive analytics"""
        members_df, operations_df, assignments_df = data
        lang = self.language
        
        st.markdown(f"## 📈 {get_text(lang, 'trends', 'Trends & Predictive Analytics')}")
        
        # Machine Learning & Predictive Analytics Section
        st.markdown("---")
        st.subheader(get_text(lang, 'predictive_analytics', '🤖 Machine Learning & Predictive Analytics'))
        
        ml_manager = MLModelManager()
        
        # Try to load existing model first
        model_loaded = ml_manager.load_model('performance_prediction')
        if model_loaded:
            st.info("✅ Pre-trained ML model loaded automatically for predictions")
        else:
            st.warning("⚠️ No trained model found - train a model first for better predictions")
        
        # Model Training Section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🚀 Train Best Performance Model**")
            if st.button(get_text(lang, 'train_models', '🤖 Train & Select Best Model'), type="primary"):
                with st.spinner(get_text(lang, 'training_models', 'Training multiple ML models and selecting best...')):
                    try:
                        # Prepare enhanced features
                        feature_df = ml_manager.prepare_performance_features(members_df, operations_df, assignments_df)
                        
                        # Train and select best model
                        metadata, msg = ml_manager.train_and_select_best_model(feature_df)
                        
                        if metadata:
                            st.success(f'🎉 Best Model Selected: {metadata["best_model_name"].upper()}')
                            
                            # Show key metrics
                            metrics = metadata['performance_metrics']
                            col1_m, col2_m, col3_m = st.columns(3)
                            
                            with col1_m:
                                st.metric("🎯 Accuracy (R²)", f"{metrics['test_r2']:.4f}")
                            with col2_m:
                                st.metric("📊 CV Score", f"{metrics['cv_r2_mean']:.4f}")
                            with col3_m:
                                st.metric("🔍 Error (MAE)", f"{metrics['test_mae']:.3f}")
                            
                            # Store metadata for display
                            st.session_state.ml_metadata = metadata
                        else:
                            st.error('❌ Model training failed - insufficient data')
                    except Exception as e:
                        st.error(f'❌ Training error: {str(e)}')
        
        with col2:
            st.markdown("**📂 Load Saved Model**")
            if st.button(get_text(lang, 'load_models', '📂 Load Best Model')):
                if ml_manager.load_model('performance_prediction'):
                    st.success('✅ Best model loaded successfully!')
                    st.session_state.ml_metadata = ml_manager.model_metadata.get('performance_prediction')
                else:
                    st.warning('⚠️ No saved models found - train a model first')
        
        # Model Performance Display Section
        if hasattr(st.session_state, 'ml_metadata') and st.session_state.ml_metadata:
            metadata = st.session_state.ml_metadata
            
            st.markdown("---")
            st.subheader('📊 Model Performance Dashboard')
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            metrics = metadata['performance_metrics']
            
            with col1:
                st.metric("🏆 Best Model", metadata['best_model_name'].upper())
            with col2:
                accuracy_pct = metrics['test_r2'] * 100
                st.metric("🎯 Accuracy", f"{accuracy_pct:.1f}%", f"{metrics['cv_r2_std']:.3f} std")
            with col3:
                st.metric("📈 Training R²", f"{metrics['train_r2']:.4f}")
            with col4:
                overfitting = "Low" if metrics['overfitting_score'] < 0.05 else "Medium" if metrics['overfitting_score'] < 0.15 else "High"
                st.metric("🔍 Overfitting", overfitting, f"{metrics['overfitting_score']:.3f}")
            
            # Model Comparison Chart
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏁 Model Comparison**")
                comparison_data = metadata['model_comparison']
                
                models = list(comparison_data.keys())
                cv_scores = [comparison_data[model]['cv_score'] for model in models]
                test_scores = [comparison_data[model]['test_r2'] for model in models]
                
                comparison_df = pd.DataFrame({
                    'Model': models,
                    'CV Score': cv_scores,
                    'Test Score': test_scores
                })
                
                fig = px.bar(comparison_df, 
                           x='Model', 
                           y=['CV Score', 'Test Score'],
                           title='Model Performance Comparison',
                           barmode='group')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**🔑 Feature Importance (Top 10)**")
                feature_importance = metadata['feature_importance']
                
                if feature_importance:
                    top_features = list(feature_importance.items())[:10]
                    feature_names = [item[0] for item in top_features]
                    feature_values = [item[1] for item in top_features]
                    
                    fig = px.bar(
                        x=feature_values,
                        y=feature_names,
                        orientation='h',
                        title='Most Important Performance Factors'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Training Details
            with st.expander("📋 Detailed Training Information"):
                training_info = metadata['training_info']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Training Samples", f"{training_info['training_size']:,}")
                    st.metric("🧪 Test Samples", f"{training_info['test_size']:,}")
                
                with col2:
                    st.metric("🔢 Features Used", training_info['feature_count'])
                    st.metric("🎯 Target Variable", training_info['target_column'])
                
                with col3:
                    trained_date = datetime.fromisoformat(training_info['trained_at'])
                    st.metric("📅 Trained On", trained_date.strftime("%Y-%m-%d"))
                    st.metric("⏰ Training Time", trained_date.strftime("%H:%M"))
                
                # Best parameters
                st.markdown("**⚙️ Best Model Parameters:**")
                best_params = metadata['best_model_params']
                for param, value in best_params.items():
                    st.write(f"• **{param}**: {value}")
        
        # Historical Trends (Fixed Performance Chart)
        st.markdown("---")
        st.subheader(get_text(lang, 'historical_trends', 'Historical Performance Trends'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Member growth trend
            members_df['join_date'] = pd.to_datetime(members_df['join_date'])
            monthly_growth = members_df.groupby(members_df['join_date'].dt.to_period('M')).size().cumsum()
            
            fig_growth = px.line(
                x=monthly_growth.index.astype(str),
                y=monthly_growth.values,
                title=get_text(lang, 'member_growth_trend', 'Member Growth Trend'),
                labels={'x': get_text(lang, 'month', 'Month'), 'y': get_text(lang, 'cumulative_members', 'Cumulative Members')}
            )
            fig_growth.update_layout(height=400)
            st.plotly_chart(fig_growth, use_container_width=True)
        
        with col2:
            # Fixed Performance trends - clean data and show improvement
            assignments_df['assignment_date'] = pd.to_datetime(assignments_df['assignment_date'])
            clean_perf_data = assignments_df.dropna(subset=['assignment_date', 'performance_score'])
            clean_perf_data = clean_perf_data[clean_perf_data['performance_score'] > 0]
            monthly_performance = clean_perf_data.groupby(
                clean_perf_data['assignment_date'].dt.to_period('M')
            )['performance_score'].mean()
            
            fig_perf = px.line(
                x=monthly_performance.index.astype(str),
                y=monthly_performance.values,
                title=get_text(lang, 'performance_trends', 'Performance Trends (Improved Over Time)'),
                labels={'x': get_text(lang, 'month', 'Month'), 'y': get_text(lang, 'avg_performance', 'Average Performance Score')}
            )
            fig_perf.update_layout(height=400)
            fig_perf.add_annotation(
                text="📈 Performance shows steady improvement due to training and experience",
                xref="paper", yref="paper",
                x=0.5, y=0.95, 
                showarrow=False,
                font=dict(size=10, color="green")
            )
            st.plotly_chart(fig_perf, use_container_width=True)
                
        # Operations Analytics
        st.markdown("---")
        st.subheader('📊 Operations Analytics')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Operations by type over time
            operations_df['start_date'] = pd.to_datetime(operations_df['start_date'])
            monthly_ops = operations_df.groupby([
                operations_df['start_date'].dt.to_period('M'), 
                'operation_type'
            ]).size().reset_index(name='count')
            monthly_ops['month'] = monthly_ops['start_date'].astype(str)
            
            fig_ops = px.bar(
                monthly_ops,
                x='month',
                y='count',
                color='operation_type',
                title='Operations by Type Over Time',
                barmode='stack'
            )
            fig_ops.update_layout(height=400)
            fig_ops.update_xaxes(tickangle=45)
            st.plotly_chart(fig_ops, use_container_width=True)
        
        with col2:
            # Success rate trends - clean data first
            clean_ops_success = operations_df.dropna(subset=['start_date', 'success_rate'])
            clean_ops_success = clean_ops_success[clean_ops_success['success_rate'] > 0]
            monthly_success = clean_ops_success.groupby(
                clean_ops_success['start_date'].dt.to_period('M')
            )['success_rate'].mean()
            
            fig_success = px.line(
                x=monthly_success.index.astype(str),
                y=monthly_success.values,
                title='Operation Success Rate Trends',
                labels={'x': 'Month', 'y': 'Average Success Rate'}
            )
            fig_success.update_layout(height=400)
            fig_success.update_xaxes(tickangle=45)
            st.plotly_chart(fig_success, use_container_width=True)
        
        # Future Forecasting Section
        st.markdown("---")
        st.subheader('🔮 Predictive Analytics & Future Forecasting')
        
        # Explain how ML models integrate with forecasting
        with st.expander("ℹ️ How ML Models Work with Predictions"):
            st.markdown("""
            **📖 Model Integration Explanation:**
            
            **For ML Performance Prediction:**
            - When you train models above, they learn patterns from member data (age, experience, rank, etc.)
            - These trained models are automatically saved and used for individual member performance predictions
            - The models predict how well specific members will perform based on their characteristics
            
            **For Time Series Forecasting:**
            - This uses historical trends in operations, performance, and resources over time
            - It analyzes monthly patterns and creates mathematical models to predict future values
            - This is separate from ML models but complements them for comprehensive analytics
            
            **Data Source:**
            - Both use the same data (loaded from saved files or newly generated)
            - Predictions are based on actual historical patterns in your data
            - The more historical data you have, the more accurate the predictions become
            """)
        
        forecast_engine = ForecastingEngine()
        
        # Show ML model integration status
        if model_loaded and hasattr(st.session_state, 'ml_metadata'):
            ml_metadata = st.session_state.ml_metadata
            st.success(f"🤖 ML Model Active: {ml_metadata['best_model_name'].upper()} with {ml_metadata['performance_metrics']['test_r2']:.1%} accuracy")
        else:
            st.info("💡 Train ML models above to enhance member-specific predictions")
        
        # Forecasting controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            months_ahead = st.selectbox(
                "Forecast Period", 
                [3, 6, 12, 24], 
                index=1,
                help="Select how many months ahead to forecast"
            )
        
        with col2:
            forecast_type = st.selectbox(
                "Forecast Type",
                ["Operations", "Performance", "Resources"],
                help="Choose what to forecast"
            )
        
        with col3:
            if st.button('🚀 Generate Forecast', type="primary"):
                with st.spinner(f'Generating {forecast_type.lower()} forecast for next {months_ahead} months...'):
                    
                    if forecast_type == "Operations":
                        forecast_data, msg = forecast_engine.forecast_operations(operations_df, months_ahead)
                        if forecast_data:
                            st.session_state.operations_forecast = forecast_data
                            st.success(f'✅ Operations forecast generated for next {months_ahead} months!')
                            
                            # Show summary metrics
                            total_predicted = forecast_data['overall_forecast']['predicted_operations'].sum()
                            avg_monthly = total_predicted / months_ahead
                            
                            metric_col1, metric_col2, metric_col3 = st.columns(3)
                            with metric_col1:
                                st.metric("Total Predicted Operations", f"{total_predicted:,}")
                            with metric_col2:
                                st.metric("Average Monthly Operations", f"{avg_monthly:.0f}")
                            with metric_col3:
                                accuracy = forecast_data['accuracy_metrics']['r2_score']
                                st.metric("Forecast Accuracy", f"{accuracy:.1%}")
                        else:
                            st.error('❌ Unable to generate operations forecast - insufficient data')
                    
                    elif forecast_type == "Performance":
                        forecast_data, msg = forecast_engine.forecast_member_performance(assignments_df, months_ahead)
                        if forecast_data:
                            st.session_state.performance_forecast = forecast_data
                            st.success(f'✅ Performance forecast generated for next {months_ahead} months!')
                            
                            # Show performance predictions
                            avg_perf_predicted = forecast_data['performance_forecast']['predicted_performance'].mean()
                            avg_attendance_predicted = forecast_data['performance_forecast']['predicted_attendance'].mean()
                            
                            metric_col1, metric_col2 = st.columns(2)
                            with metric_col1:
                                st.metric("Predicted Avg Performance", f"{avg_perf_predicted:.2f}/10")
                            with metric_col2:
                                st.metric("Predicted Avg Attendance", f"{avg_attendance_predicted:.1%}")
                            
                            # Add ML-enhanced predictions if model is available
                            if model_loaded:
                                st.info("🤖 Enhanced with ML model predictions for individual member analysis")
                        else:
                            st.error('❌ Unable to generate performance forecast - insufficient data')
                    
                    elif forecast_type == "Resources":
                        forecast_data, msg = forecast_engine.forecast_resource_needs(operations_df, assignments_df, months_ahead)
                        if forecast_data:
                            st.session_state.resource_forecast = forecast_data
                            st.success(f'✅ Resource forecast generated for next {months_ahead} months!')
                            
                            # Show resource predictions
                            total_volunteers = forecast_data['resource_forecast']['predicted_volunteers'].sum()
                            total_budget = forecast_data['resource_forecast']['predicted_budget'].sum()
                            
                            metric_col1, metric_col2 = st.columns(2)
                            with metric_col1:
                                st.metric("Total Volunteers Needed", f"{total_volunteers:,}")
                            with metric_col2:
                                st.metric("Total Budget Required", f"RM {total_budget:,.0f}")
        
        # Display forecast visualizations
        st.markdown("---")
        
        # Operations Forecast Visualization
        if hasattr(st.session_state, 'operations_forecast') and st.session_state.operations_forecast:
            st.subheader('📊 Operations Forecast Visualization')
            
            forecast_data = st.session_state.operations_forecast
            charts = forecast_engine.create_forecast_visualizations(forecast_data, 'operations')
            
            # Main forecast chart
            st.plotly_chart(charts['main_forecast'], use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(charts['state_breakdown'], use_container_width=True)
            with col2:
                st.plotly_chart(charts['monthly_breakdown'], use_container_width=True)
            
            # Forecast accuracy info
            with st.expander("📈 Forecast Model Information"):
                accuracy_metrics = forecast_data['accuracy_metrics']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Model Accuracy (R²)", f"{accuracy_metrics['r2_score']:.3f}")
                with col2:
                    st.metric("Mean Absolute Error", f"{accuracy_metrics['mae']:.1f}")
                with col3:
                    st.metric("Mean Abs. Percentage Error", f"{accuracy_metrics['mape']:.1f}%")
                
                st.info("📌 Forecast uses polynomial trend modeling with seasonal adjustments based on historical patterns")
        
        # Performance Forecast Visualization
        if hasattr(st.session_state, 'performance_forecast') and st.session_state.performance_forecast:
            st.subheader('📈 Performance Forecast Visualization')
            
            forecast_data = st.session_state.performance_forecast
            charts = forecast_engine.create_forecast_visualizations(forecast_data, 'performance')
            
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(charts['performance_forecast'], use_container_width=True)
            with col2:
                st.plotly_chart(charts['attendance_forecast'], use_container_width=True)
        
        # Resource Forecast Visualization
        if hasattr(st.session_state, 'resource_forecast') and st.session_state.resource_forecast:
            st.subheader('🛠️ Resource Requirements Forecast')
            
            forecast_data = st.session_state.resource_forecast
            charts = forecast_engine.create_forecast_visualizations(forecast_data, 'resources')
            
            st.plotly_chart(charts['resource_forecast'], use_container_width=True)
            
            # Resource planning insights
            with st.expander("💡 Resource Planning Insights"):
                resource_forecast = forecast_data['resource_forecast']
                
                total_volunteers = resource_forecast['predicted_volunteers'].sum()
                total_budget = resource_forecast['predicted_budget'].sum()
                total_equipment = resource_forecast['predicted_equipment'].sum()
                total_vehicles = resource_forecast['predicted_vehicles'].sum()
                
                st.write("**Resource Requirements Summary:**")
                st.write(f"• **Total Volunteers Needed**: {total_volunteers:,}")
                st.write(f"• **Total Budget Required**: RM {total_budget:,.0f}")
                st.write(f"• **Equipment Units**: {total_equipment:,}")
                st.write(f"• **Vehicles Required**: {total_vehicles:,}")
                
                # Peak month analysis
                peak_month = resource_forecast.loc[resource_forecast['predicted_volunteers'].idxmax()]
                st.write(f"• **Peak Activity Month**: {peak_month['date'].strftime('%B %Y')}")
                st.write(f"• **Peak Volunteers**: {peak_month['predicted_volunteers']:,}")
        
        # Forecasting insights and recommendations
        if (hasattr(st.session_state, 'operations_forecast') or 
            hasattr(st.session_state, 'performance_forecast') or 
            hasattr(st.session_state, 'resource_forecast')):
            
            st.markdown("---")
            st.subheader('🎯 Strategic Insights & Recommendations')
            
            insights = []
            
            if hasattr(st.session_state, 'operations_forecast'):
                ops_data = st.session_state.operations_forecast['overall_forecast']
                trend = "increasing" if ops_data['predicted_operations'].iloc[-1] > ops_data['predicted_operations'].iloc[0] else "decreasing"
                insights.append(f"📈 Operations are {trend} over the forecast period")
                
                peak_month = ops_data.loc[ops_data['predicted_operations'].idxmax()]
                insights.append(f"🔴 Peak operations expected in {peak_month['date'].strftime('%B %Y')} with {peak_month['predicted_operations']} operations")
            
            if hasattr(st.session_state, 'performance_forecast'):
                perf_data = st.session_state.performance_forecast['performance_forecast']
                perf_trend = "improving" if perf_data['predicted_performance'].iloc[-1] > perf_data['predicted_performance'].iloc[0] else "declining"
                insights.append(f"📊 Member performance is {perf_trend} over the forecast period")
                
                avg_perf = perf_data['predicted_performance'].mean()
                if avg_perf > 7.5:
                    insights.append("🌟 Excellent performance levels expected - maintain current training programs")
                elif avg_perf > 6.0:
                    insights.append("👍 Good performance expected - consider additional skill development")
                else:
                    insights.append("⚠️ Performance may need attention - recommend enhanced training initiatives")
            
            if hasattr(st.session_state, 'resource_forecast'):
                resource_data = st.session_state.resource_forecast['resource_forecast']
                budget_trend = "increasing" if resource_data['predicted_budget'].iloc[-1] > resource_data['predicted_budget'].iloc[0] else "decreasing"
                insights.append(f"💰 Budget requirements are {budget_trend} over the forecast period")
                
                volunteer_trend = "increasing" if resource_data['predicted_volunteers'].iloc[-1] > resource_data['predicted_volunteers'].iloc[0] else "decreasing"
                if volunteer_trend == "increasing":
                    insights.append("👥 Consider recruitment campaigns to meet growing volunteer demand")
                
            for insight in insights:
                st.info(insight)
                
        # ML-Enhanced Member Predictions Section
        if model_loaded and hasattr(st.session_state, 'ml_metadata'):
            st.markdown("---")
            st.subheader('🎯 ML-Enhanced Member Performance Predictions')
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("**🔍 Individual Member Analysis**")
                
                # Sample member selection for prediction
                sample_members = members_df.sample(min(10, len(members_df))).copy()
                member_options = [f"{row['name']} ({row['member_id']}) - {row['rank']}" 
                                for _, row in sample_members.iterrows()]
                
                selected_member = st.selectbox("Select Member for Prediction:", member_options)
                
                if st.button("🔮 Predict Performance", type="secondary"):
                    selected_idx = member_options.index(selected_member)
                    member_data = sample_members.iloc[[selected_idx]]
                    
                    # Prepare features for the selected member
                    try:
                        feature_df = ml_manager.prepare_performance_features(members_df, operations_df, assignments_df)
                        member_feature_data = feature_df[feature_df['member_id'] == member_data['member_id'].iloc[0]]
                        
                        if not member_feature_data.empty:
                            prediction_result, msg = ml_manager.predict_member_performance(member_feature_data)
                            
                            if prediction_result:
                                predicted_score = prediction_result['predictions'][0]
                                confidence_lower = prediction_result['confidence_lower'][0]
                                confidence_upper = prediction_result['confidence_upper'][0]
                                model_name = prediction_result['model_name']
                                
                                st.success(f"**Predicted Performance: {predicted_score:.2f}/10**")
                                st.write(f"Model: {model_name.upper()}")
                                st.write(f"Confidence Range: {confidence_lower:.2f} - {confidence_upper:.2f}")
                                
                                # Performance interpretation
                                if predicted_score >= 8.0:
                                    st.success("🌟 Excellent performance expected")
                                elif predicted_score >= 6.5:
                                    st.info("👍 Good performance expected")
                                elif predicted_score >= 5.0:
                                    st.warning("⚠️ Average performance - consider additional training")
                                else:
                                    st.error("❌ Below average performance - needs attention")
                            else:
                                st.error("Unable to generate prediction for this member")
                        else:
                            st.warning("No historical data found for this member")
                    except Exception as e:
                        st.error(f"Prediction error: {str(e)}")
            
            with col2:
                st.markdown("**📊 Model Performance Summary**")
                
                if hasattr(st.session_state, 'ml_metadata'):
                    metadata = st.session_state.ml_metadata
                    
                    # Key metrics
                    metrics = metadata['performance_metrics']
                    
                    col1_m, col2_m, col3_m = st.columns(3)
                    with col1_m:
                        accuracy_pct = metrics['test_r2'] * 100
                        st.metric("Model Accuracy", f"{accuracy_pct:.1f}%")
                    with col2_m:
                        st.metric("Cross-Val Score", f"{metrics['cv_r2_mean']:.3f}")
                    with col3_m:
                        st.metric("Prediction Error", f"{metrics['test_mae']:.2f}")
                    
                    # Top prediction factors
                    st.markdown("**🔑 Top Performance Factors:**")
                    top_features = list(metadata['feature_importance'].keys())[:5]
                    for i, feature in enumerate(top_features, 1):
                        importance = metadata['feature_importance'][feature]
                        st.write(f"{i}. {feature.replace('_', ' ').title()}: {importance:.3f}")
                    
                    st.info("💡 These factors most strongly predict member performance based on historical data")
        
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
