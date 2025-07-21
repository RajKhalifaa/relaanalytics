import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

class ForecastingEngine:
    def __init__(self):
        self.forecasting_models = {}
        self.historical_data = {}
    
    def prepare_time_series_data(self, df, date_column, value_column, frequency='M'):
        """Prepare time series data for forecasting"""
        df[date_column] = pd.to_datetime(df[date_column])
        
        if frequency == 'M':
            # For counting operations, we just need the count, not mean/sum of IDs
            time_series = df.groupby(df[date_column].dt.to_period('M')).size().reset_index(name='count')
            time_series['date'] = time_series[date_column].dt.to_timestamp()
        elif frequency == 'W':
            time_series = df.groupby(df[date_column].dt.to_period('W')).size().reset_index(name='count')
            time_series['date'] = time_series[date_column].dt.to_timestamp()
        else:  # Daily
            time_series = df.groupby(df[date_column].dt.date).size().reset_index(name='count')
            time_series['date'] = pd.to_datetime(time_series[date_column])
        
        time_series = time_series.sort_values('date').reset_index(drop=True)
        return time_series
    
    def create_trend_model(self, dates, values, polynomial_degree=2):
        """Create polynomial trend model for forecasting"""
        # Convert dates to numerical values
        start_date = dates.min()
        x = (dates - start_date).dt.days.values.reshape(-1, 1)
        
        # Create polynomial features
        poly_features = PolynomialFeatures(degree=polynomial_degree)
        x_poly = poly_features.fit_transform(x)
        
        # Train model
        model = LinearRegression()
        model.fit(x_poly, values)
        
        return model, poly_features, start_date
    
    def forecast_operations(self, operations_df, months_ahead=6):
        """Forecast future operations count and trends"""
        # Prepare monthly operations data
        operations_df['start_date'] = pd.to_datetime(operations_df['start_date'])
        monthly_ops = self.prepare_time_series_data(operations_df, 'start_date', 'operation_id', 'M')
        
        if len(monthly_ops) < 3:
            return None, "Insufficient historical data for forecasting"
        
        # Create trend model
        model, poly_features, start_date = self.create_trend_model(monthly_ops['date'], monthly_ops['count'])
        
        # Generate future dates
        last_date = monthly_ops['date'].max()
        future_dates = pd.date_range(
            start=last_date + timedelta(days=30), 
            periods=months_ahead, 
            freq='MS'
        )
        
        # Make predictions
        future_x = (future_dates - start_date).days.values.reshape(-1, 1)
        future_x_poly = poly_features.transform(future_x)
        predictions = model.predict(future_x_poly)
        
        # Add seasonal adjustment based on historical patterns
        monthly_seasonal = monthly_ops.groupby(monthly_ops['date'].dt.month)['count'].mean()
        seasonal_factors = []
        for date in future_dates:
            month = date.month
            if month in monthly_seasonal.index:
                factor = monthly_seasonal[month] / monthly_seasonal.mean()
            else:
                factor = 1.0
            seasonal_factors.append(factor)
        
        predictions_adjusted = predictions * seasonal_factors
        predictions_adjusted = np.maximum(predictions_adjusted, 0)  # Ensure non-negative
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_operations': np.round(predictions_adjusted).astype(int),
            'trend_component': np.round(predictions).astype(int),
            'seasonal_factor': seasonal_factors,
            'month': future_dates.month,
            'year': future_dates.year
        })
        
        # Add state-wise breakdown based on historical distribution
        state_distribution = operations_df['state'].value_counts(normalize=True)
        forecast_by_state = []
        
        for _, row in forecast_df.iterrows():
            for state, proportion in state_distribution.items():
                forecast_by_state.append({
                    'date': row['date'],
                    'state': state,
                    'predicted_operations': int(row['predicted_operations'] * proportion),
                    'month': row['month'],
                    'year': row['year']
                })
        
        forecast_state_df = pd.DataFrame(forecast_by_state)
        
        # Add operation type breakdown
        type_distribution = operations_df['operation_type'].value_counts(normalize=True)
        forecast_by_type = []
        
        for _, row in forecast_df.iterrows():
            for op_type, proportion in type_distribution.items():
                forecast_by_type.append({
                    'date': row['date'],
                    'operation_type': op_type,
                    'predicted_operations': int(row['predicted_operations'] * proportion),
                    'month': row['month'],
                    'year': row['year']
                })
        
        forecast_type_df = pd.DataFrame(forecast_by_type)
        
        # Calculate model accuracy on historical data
        historical_x = (monthly_ops['date'] - start_date).dt.days.values.reshape(-1, 1)
        historical_x_poly = poly_features.transform(historical_x)
        historical_predictions = model.predict(historical_x_poly)
        
        accuracy_metrics = {
            'r2_score': r2_score(monthly_ops['count'], historical_predictions),
            'mae': mean_absolute_error(monthly_ops['count'], historical_predictions),
            'mape': np.mean(np.abs((monthly_ops['count'] - historical_predictions) / monthly_ops['count'])) * 100
        }
        
        return {
            'overall_forecast': forecast_df,
            'state_forecast': forecast_state_df,
            'type_forecast': forecast_type_df,
            'historical_data': monthly_ops,
            'accuracy_metrics': accuracy_metrics
        }, "Operations forecast generated successfully"
    
    def forecast_member_performance(self, assignments_df, months_ahead=6):
        """Forecast future member performance trends"""
        assignments_df['assignment_date'] = pd.to_datetime(assignments_df['assignment_date'])
        
        # Prepare monthly performance data
        monthly_perf = assignments_df[assignments_df['performance_score'] > 0].groupby(
            assignments_df['assignment_date'].dt.to_period('M')
        ).agg({
            'performance_score': ['mean', 'std', 'count'],
            'attendance': 'mean'
        }).reset_index()
        
        monthly_perf.columns = ['date', 'avg_performance', 'std_performance', 'assignments_count', 'avg_attendance']
        monthly_perf['date'] = monthly_perf['date'].dt.to_timestamp()
        
        if len(monthly_perf) < 3:
            return None, "Insufficient performance data for forecasting"
        
        # Create trend models for different metrics
        perf_model, perf_poly, start_date = self.create_trend_model(monthly_perf['date'], monthly_perf['avg_performance'])
        attendance_model, attendance_poly, _ = self.create_trend_model(monthly_perf['date'], monthly_perf['avg_attendance'])
        
        # Generate future dates
        last_date = monthly_perf['date'].max()
        future_dates = pd.date_range(
            start=last_date + timedelta(days=30), 
            periods=months_ahead, 
            freq='MS'
        )
        
        # Make predictions
        future_x = (future_dates - start_date).days.values.reshape(-1, 1)
        future_perf_poly = perf_poly.transform(future_x)
        future_attendance_poly = attendance_poly.transform(future_x)
        
        perf_predictions = perf_model.predict(future_perf_poly)
        attendance_predictions = attendance_model.predict(future_attendance_poly)
        
        # Ensure realistic bounds
        perf_predictions = np.clip(perf_predictions, 1.0, 10.0)
        attendance_predictions = np.clip(attendance_predictions, 0.0, 1.0)
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_performance': perf_predictions,
            'predicted_attendance': attendance_predictions,
            'month': future_dates.month,
            'year': future_dates.year
        })
        
        return {
            'performance_forecast': forecast_df,
            'historical_performance': monthly_perf
        }, "Performance forecast generated successfully"
    
    def forecast_resource_needs(self, operations_df, assignments_df, months_ahead=6):
        """Forecast future resource requirements"""
        operations_df['start_date'] = pd.to_datetime(operations_df['start_date'])
        
        # Aggregate monthly resource usage
        monthly_resources = operations_df.groupby(
            operations_df['start_date'].dt.to_period('M')
        ).agg({
            'volunteers_assigned': ['sum', 'mean'],
            'budget_allocated': ['sum', 'mean'],
            'equipment_used': 'sum',
            'vehicles_deployed': 'sum'
        }).reset_index()
        
        monthly_resources.columns = [
            'date', 'total_volunteers', 'avg_volunteers_per_op',
            'total_budget', 'avg_budget_per_op', 'total_equipment', 'total_vehicles'
        ]
        monthly_resources['date'] = monthly_resources['date'].dt.to_timestamp()
        
        if len(monthly_resources) < 3:
            return None, "Insufficient resource data for forecasting"
        
        # Create models for different resources
        resource_forecasts = {}
        
        for column in ['total_volunteers', 'total_budget', 'total_equipment', 'total_vehicles']:
            model, poly, start_date = self.create_trend_model(monthly_resources['date'], monthly_resources[column])
            
            # Generate future dates
            last_date = monthly_resources['date'].max()
            future_dates = pd.date_range(
                start=last_date + timedelta(days=30), 
                periods=months_ahead, 
                freq='MS'
            )
            
            # Make predictions
            future_x = (future_dates - start_date).days.values.reshape(-1, 1)
            future_poly = poly.transform(future_x)
            predictions = model.predict(future_poly)
            
            # Ensure non-negative values
            predictions = np.maximum(predictions, 0)
            
            resource_forecasts[column] = predictions
        
        forecast_df = pd.DataFrame({
            'date': future_dates,
            'predicted_volunteers': resource_forecasts['total_volunteers'].astype(int),
            'predicted_budget': resource_forecasts['total_budget'].astype(int),
            'predicted_equipment': resource_forecasts['total_equipment'].astype(int),
            'predicted_vehicles': resource_forecasts['total_vehicles'].astype(int),
            'month': future_dates.month,
            'year': future_dates.year
        })
        
        return {
            'resource_forecast': forecast_df,
            'historical_resources': monthly_resources
        }, "Resource forecast generated successfully"
    
    def create_forecast_visualizations(self, forecast_data, forecast_type='operations'):
        """Create comprehensive forecast visualizations"""
        
        if forecast_type == 'operations':
            return self._create_operations_forecast_charts(forecast_data)
        elif forecast_type == 'performance':
            return self._create_performance_forecast_charts(forecast_data)
        elif forecast_type == 'resources':
            return self._create_resource_forecast_charts(forecast_data)
    
    def _create_operations_forecast_charts(self, forecast_data):
        """Create operations forecast charts"""
        overall_forecast = forecast_data['overall_forecast']
        historical_data = forecast_data['historical_data']
        state_forecast = forecast_data['state_forecast']
        type_forecast = forecast_data['type_forecast']
        
        # Main forecast chart
        fig_main = go.Figure()
        
        # Historical data
        fig_main.add_trace(go.Scatter(
            x=historical_data['date'],
            y=historical_data['count'],
            mode='lines+markers',
            name='Historical Operations',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))
        
        # Forecast data
        fig_main.add_trace(go.Scatter(
            x=overall_forecast['date'],
            y=overall_forecast['predicted_operations'],
            mode='lines+markers',
            name='Predicted Operations',
            line=dict(color='red', width=2, dash='dash'),
            marker=dict(size=6, symbol='diamond')
        ))
        
        fig_main.update_layout(
            title='Operations Forecast - Next 6 Months',
            xaxis_title='Date',
            yaxis_title='Number of Operations',
            height=400,
            hovermode='x unified'
        )
        
        # State-wise forecast
        fig_state = px.bar(
            state_forecast.groupby('state')['predicted_operations'].sum().reset_index(),
            x='state',
            y='predicted_operations',
            title='Predicted Operations by State (Next 6 Months)',
            color='predicted_operations',
            color_continuous_scale='viridis'
        )
        fig_state.update_layout(height=400)
        
        # Monthly breakdown
        monthly_breakdown = overall_forecast.copy()
        monthly_breakdown['month_name'] = monthly_breakdown['date'].dt.strftime('%B %Y')
        
        fig_monthly = px.bar(
            monthly_breakdown,
            x='month_name',
            y='predicted_operations',
            title='Monthly Operations Forecast',
            color='predicted_operations',
            color_continuous_scale='plasma'
        )
        fig_monthly.update_layout(height=400)
        fig_monthly.update_xaxes(tickangle=45)
        
        return {
            'main_forecast': fig_main,
            'state_breakdown': fig_state,
            'monthly_breakdown': fig_monthly
        }
    
    def _create_performance_forecast_charts(self, forecast_data):
        """Create performance forecast charts"""
        perf_forecast = forecast_data['performance_forecast']
        historical_perf = forecast_data['historical_performance']
        
        # Performance trend forecast
        fig_perf = go.Figure()
        
        # Historical performance
        fig_perf.add_trace(go.Scatter(
            x=historical_perf['date'],
            y=historical_perf['avg_performance'],
            mode='lines+markers',
            name='Historical Performance',
            line=dict(color='green', width=2)
        ))
        
        # Forecast performance
        fig_perf.add_trace(go.Scatter(
            x=perf_forecast['date'],
            y=perf_forecast['predicted_performance'],
            mode='lines+markers',
            name='Predicted Performance',
            line=dict(color='orange', width=2, dash='dash')
        ))
        
        fig_perf.update_layout(
            title='Member Performance Forecast',
            xaxis_title='Date',
            yaxis_title='Average Performance Score',
            height=400
        )
        
        # Attendance forecast
        fig_attendance = go.Figure()
        
        fig_attendance.add_trace(go.Scatter(
            x=historical_perf['date'],
            y=historical_perf['avg_attendance'],
            mode='lines+markers',
            name='Historical Attendance',
            line=dict(color='blue', width=2)
        ))
        
        fig_attendance.add_trace(go.Scatter(
            x=perf_forecast['date'],
            y=perf_forecast['predicted_attendance'],
            mode='lines+markers',
            name='Predicted Attendance',
            line=dict(color='red', width=2, dash='dash')
        ))
        
        fig_attendance.update_layout(
            title='Member Attendance Forecast',
            xaxis_title='Date',
            yaxis_title='Average Attendance Rate',
            height=400
        )
        
        return {
            'performance_forecast': fig_perf,
            'attendance_forecast': fig_attendance
        }
    
    def _create_resource_forecast_charts(self, forecast_data):
        """Create resource forecast charts"""
        resource_forecast = forecast_data['resource_forecast']
        historical_resources = forecast_data['historical_resources']
        
        # Multi-metric resource forecast
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Volunteers', 'Budget (RM)', 'Equipment', 'Vehicles'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Volunteers
        fig.add_trace(
            go.Scatter(x=historical_resources['date'], y=historical_resources['total_volunteers'],
                      mode='lines', name='Historical Volunteers', line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=resource_forecast['date'], y=resource_forecast['predicted_volunteers'],
                      mode='lines+markers', name='Predicted Volunteers', line=dict(color='red', dash='dash')),
            row=1, col=1
        )
        
        # Budget
        fig.add_trace(
            go.Scatter(x=historical_resources['date'], y=historical_resources['total_budget'],
                      mode='lines', name='Historical Budget', line=dict(color='green')),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=resource_forecast['date'], y=resource_forecast['predicted_budget'],
                      mode='lines+markers', name='Predicted Budget', line=dict(color='orange', dash='dash')),
            row=1, col=2
        )
        
        # Equipment
        fig.add_trace(
            go.Scatter(x=historical_resources['date'], y=historical_resources['total_equipment'],
                      mode='lines', name='Historical Equipment', line=dict(color='purple')),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=resource_forecast['date'], y=resource_forecast['predicted_equipment'],
                      mode='lines+markers', name='Predicted Equipment', line=dict(color='brown', dash='dash')),
            row=2, col=1
        )
        
        # Vehicles
        fig.add_trace(
            go.Scatter(x=historical_resources['date'], y=historical_resources['total_vehicles'],
                      mode='lines', name='Historical Vehicles', line=dict(color='cyan')),
            row=2, col=2
        )
        fig.add_trace(
            go.Scatter(x=resource_forecast['date'], y=resource_forecast['predicted_vehicles'],
                      mode='lines+markers', name='Predicted Vehicles', line=dict(color='magenta', dash='dash')),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Resource Requirements Forecast',
            height=600,
            showlegend=False
        )
        
        return {
            'resource_forecast': fig
        }