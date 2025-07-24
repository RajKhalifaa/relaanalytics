import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Analytics:
    def __init__(self):
        pass
    
    def filter_data(self, members_df, operations_df, assignments_df, selected_states=None, selected_status=None, date_range=None):
        """Filter datasets based on user selections"""
        
        # Filter members
        filtered_members = members_df.copy()
        
        if selected_states:
            filtered_members = filtered_members[filtered_members['state'].isin(selected_states)]
        
        if selected_status:
            filtered_members = filtered_members[filtered_members['status'].isin(selected_status)]
        
        # Filter operations
        filtered_operations = operations_df.copy()
        
        if selected_states:
            filtered_operations = filtered_operations[filtered_operations['state'].isin(selected_states)]
        
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_operations = filtered_operations[
                (pd.to_datetime(filtered_operations['start_date']).dt.date >= start_date) &
                (pd.to_datetime(filtered_operations['start_date']).dt.date <= end_date)
            ]
        
        # Filter assignments
        filtered_assignments = assignments_df.copy()
        
        # Filter assignments based on filtered members
        member_ids = filtered_members['member_id'].tolist()
        filtered_assignments = filtered_assignments[filtered_assignments['member_id'].isin(member_ids)]
        
        if selected_states:
            filtered_assignments = filtered_assignments[filtered_assignments['state'].isin(selected_states)]
        
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_assignments = filtered_assignments[
                (pd.to_datetime(filtered_assignments['assignment_date']).dt.date >= start_date) &
                (pd.to_datetime(filtered_assignments['assignment_date']).dt.date <= end_date)
            ]
        
        return filtered_members, filtered_operations, filtered_assignments
    
    def calculate_kpis(self, members_df, operations_df, assignments_df):
        """Calculate key performance indicators"""
        
        kpis = {}
        
        # Member KPIs
        kpis['total_members'] = len(members_df)
        kpis['active_members'] = len(members_df[members_df['status'] == 'Active'])
        kpis['avg_age'] = members_df['age'].mean()
        kpis['avg_service_years'] = members_df['years_of_service'].mean()
        
        # Operations KPIs
        kpis['total_operations'] = len(operations_df)
        kpis['completed_operations'] = len(operations_df[operations_df['status'] == 'Completed'])
        kpis['avg_success_rate'] = operations_df['success_rate'].mean()
        kpis['avg_operation_duration'] = operations_df['duration_hours'].mean()
        
        # Assignment KPIs
        kpis['total_assignments'] = len(assignments_df)
        kpis['attendance_rate'] = (assignments_df['attendance'].sum() / len(assignments_df)) * 100
        kpis['avg_performance'] = assignments_df['performance_score'].mean()
        kpis['avg_feedback'] = assignments_df['feedback_score'].mean()
        
        # Derived KPIs
        kpis['completion_rate'] = (kpis['completed_operations'] / kpis['total_operations']) * 100 if kpis['total_operations'] > 0 else 0
        kpis['volunteer_utilization'] = (kpis['total_assignments'] / kpis['active_members']) if kpis['active_members'] > 0 else 0
        
        return kpis
    
    def get_trend_analysis(self, data_df, date_column, value_column, period='M'):
        """Perform trend analysis on time-series data"""
        
        df = data_df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df['period'] = df[date_column].dt.to_period(period)
        
        if value_column in df.columns:
            trend_data = df.groupby('period')[value_column].agg(['count', 'mean', 'sum']).reset_index()
        else:
            trend_data = df.groupby('period').size().reset_index(name='count')
        
        trend_data['period'] = trend_data['period'].astype(str)
        
        return trend_data
    
    def calculate_correlation_matrix(self, assignments_df, members_df):
        """Calculate correlation matrix for performance analysis"""
        
        # Merge assignments with member data
        merged_df = assignments_df.merge(
            members_df[['member_id', 'age', 'years_of_service', 'training_completed']],
            on='member_id'
        )
        
        # Select numeric columns for correlation
        numeric_cols = [
            'performance_score', 'duration_hours', 'age', 
            'years_of_service', 'training_completed'
        ]
        
        correlation_matrix = merged_df[numeric_cols].corr()
        
        return correlation_matrix
    
    def get_top_performers(self, assignments_df, members_df, metric='performance_score', top_n=20):
        """Get top performing members based on specified metric"""
        
        # Calculate member performance statistics
        member_stats = assignments_df.groupby('member_id').agg({
            'performance_score': 'mean',
            'attendance': 'sum',
            'assignment_id': 'count',
            'feedback_score': 'mean'
        }).round(2)
        
        member_stats.columns = ['avg_performance', 'total_attendance', 'total_assignments', 'avg_feedback']
        
        # Filter members with minimum assignments
        member_stats = member_stats[member_stats['total_assignments'] >= 3]
        
        # Merge with member details
        top_performers = members_df.merge(member_stats, left_on='member_id', right_index=True)
        
        # Sort by specified metric
        if metric in top_performers.columns:
            top_performers = top_performers.nlargest(top_n, metric)
        else:
            top_performers = top_performers.nlargest(top_n, 'avg_performance')
        
        return top_performers
    
    def analyze_operation_efficiency(self, operations_df):
        """Analyze operational efficiency metrics"""
        
        efficiency_metrics = {}
        
        # Success rate by operation type
        efficiency_metrics['success_by_type'] = operations_df.groupby('operation_type')['success_rate'].mean().sort_values(ascending=False)
        
        # Resource utilization
        efficiency_metrics['resource_utilization'] = operations_df.groupby('operation_type').agg({
            'volunteers_assigned': 'mean',
            'duration_hours': 'mean',
            'budget_allocated': 'mean'
        }).round(2)
        
        # Complexity vs Success Rate
        efficiency_metrics['complexity_analysis'] = operations_df.groupby('complexity').agg({
            'success_rate': 'mean',
            'duration_hours': 'mean',
            'volunteers_assigned': 'mean'
        }).round(2)
        
        # Time-based efficiency
        efficiency_metrics['time_efficiency'] = operations_df.groupby('time_of_day')['success_rate'].mean().sort_values(ascending=False)
        
        return efficiency_metrics
    
    def predict_volunteer_needs(self, operations_df, assignments_df):
        """Simple prediction model for volunteer needs"""
        
        # Calculate average volunteers needed per operation type
        volunteer_needs = operations_df.groupby('operation_type').agg({
            'volunteers_assigned': 'mean',
            'duration_hours': 'mean',
            'success_rate': 'mean'
        }).round(2)
        
        # Calculate assignment completion rates
        assignment_rates = assignments_df.groupby('assignment_type').agg({
            'attendance': 'mean',
            'performance_score': 'mean'
        }).round(2)
        
        predictions = {
            'volunteer_needs_by_type': volunteer_needs,
            'assignment_completion_rates': assignment_rates
        }
        
        return predictions
    
    def generate_insights(self, members_df, operations_df, assignments_df):
        """Generate automated insights from the data"""
        
        insights = []
        
        # Member insights
        most_active_state = members_df['state'].value_counts().index[0]
        insights.append(f"🏛️ {most_active_state} has the highest number of RELA members")
        
        avg_age = members_df['age'].mean()
        if avg_age > 45:
            insights.append(f"👴 Average member age is {avg_age:.1f} years - consider youth recruitment programs")
        
        # Operations insights
        best_operation_type = operations_df.groupby('operation_type')['success_rate'].mean().idxmax()
        best_success_rate = operations_df.groupby('operation_type')['success_rate'].mean().max()
        insights.append(f"🎯 '{best_operation_type}' operations have the highest success rate at {best_success_rate:.1%}")
        
        # Performance insights
        attendance_rate = (assignments_df['attendance'].sum() / len(assignments_df)) * 100
        if attendance_rate < 85:
            insights.append(f"⚠️ Attendance rate is {attendance_rate:.1f}% - below optimal threshold")
        else:
            insights.append(f"✅ Excellent attendance rate of {attendance_rate:.1f}%")
        
        # Regional insights
        state_performance = assignments_df.groupby('state')['performance_score'].mean()
        top_performing_state = state_performance.idxmax()
        insights.append(f"🏆 {top_performing_state} shows the highest performance scores")
        
        return insights
    
    def calculate_diversity_metrics(self, members_df):
        """Calculate diversity and inclusion metrics"""
        
        diversity_metrics = {}
        
        # Gender diversity
        gender_dist = members_df['gender'].value_counts(normalize=True) * 100
        diversity_metrics['gender_distribution'] = gender_dist.round(1)
        
        # Ethnic diversity
        ethnic_dist = members_df['ethnicity'].value_counts(normalize=True) * 100
        diversity_metrics['ethnic_distribution'] = ethnic_dist.round(1)
        
        # Age diversity
        age_dist = members_df['age_group'].value_counts(normalize=True) * 100
        diversity_metrics['age_distribution'] = age_dist.round(1)
        
        # Education diversity
        edu_dist = members_df['education_level'].value_counts(normalize=True) * 100
        diversity_metrics['education_distribution'] = edu_dist.round(1)
        
        # Calculate diversity index (Simpson's Diversity Index)
        def simpson_diversity_index(series):
            proportions = series.value_counts(normalize=True)
            return 1 - sum(proportions ** 2)
        
        diversity_metrics['diversity_indices'] = {
            'gender': simpson_diversity_index(members_df['gender']),
            'ethnicity': simpson_diversity_index(members_df['ethnicity']),
            'age_group': simpson_diversity_index(members_df['age_group']),
            'education': simpson_diversity_index(members_df['education_level'])
        }
        
        return diversity_metrics
    
    def analyze_retention(self, members_df, assignments_df):
        """Analyze member retention patterns"""
        
        retention_metrics = {}
        
        # Years of service distribution
        service_dist = members_df['years_of_service'].describe()
        retention_metrics['service_statistics'] = service_dist
        
        # Retention by demographic
        retention_by_demo = members_df.groupby(['age_group', 'gender'])['years_of_service'].mean().unstack()
        retention_metrics['retention_by_demographics'] = retention_by_demo.round(2)
        
        # Activity-based retention
        member_activity = assignments_df.groupby('member_id').size()
        member_retention = members_df.merge(
            member_activity.rename('total_assignments'), 
            left_on='member_id', 
            right_index=True, 
            how='left'
        )
        member_retention['total_assignments'] = member_retention['total_assignments'].fillna(0)
        
        # Correlation between activity and service years
        activity_retention_corr = member_retention[['years_of_service', 'total_assignments']].corr()
        retention_metrics['activity_retention_correlation'] = activity_retention_corr
        
        return retention_metrics
