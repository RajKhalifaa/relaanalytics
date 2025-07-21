import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PredictiveAnalytics:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_metadata = {}
        self.models_dir = "models"
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def prepare_features(self, members_df, operations_df, assignments_df):
        """Prepare features for predictive modeling"""
        
        # Aggregate member performance data
        member_performance = assignments_df.groupby('member_id').agg({
            'performance_score': ['mean', 'std', 'count'],
            'attendance': 'mean',
            'duration_hours': 'mean',
            'assignment_date': ['min', 'max']
        }).round(2)
        
        # Flatten column names
        member_performance.columns = [f"{col[0]}_{col[1]}" for col in member_performance.columns]
        member_performance = member_performance.reset_index()
        
        # Calculate member experience metrics
        member_performance['days_active'] = (
            member_performance['assignment_date_max'] - member_performance['assignment_date_min']
        ).dt.days
        member_performance['assignments_per_month'] = (
            member_performance['performance_score_count'] / 
            (member_performance['days_active'] / 30 + 1)
        ).round(2)
        
        # Merge with member demographics
        feature_df = members_df.merge(member_performance, on='member_id', how='left')
        
        # Fill missing values for members with no assignments
        numeric_columns = feature_df.select_dtypes(include=[np.number]).columns
        feature_df[numeric_columns] = feature_df[numeric_columns].fillna(0)
        
        # Add time-based features
        feature_df['join_date'] = pd.to_datetime(feature_df['join_date'])
        feature_df['days_since_joining'] = (datetime.now() - feature_df['join_date']).dt.days
        feature_df['join_year'] = feature_df['join_date'].dt.year
        feature_df['join_month'] = feature_df['join_date'].dt.month
        
        return feature_df
    
    def encode_categorical_features(self, df, categorical_columns, fit=True):
        """Encode categorical features for ML models"""
        df_encoded = df.copy()
        
        for column in categorical_columns:
            if column in df_encoded.columns:
                if fit:
                    if column not in self.encoders:
                        self.encoders[column] = LabelEncoder()
                    df_encoded[f'{column}_encoded'] = self.encoders[column].fit_transform(df_encoded[column].astype(str))
                else:
                    if column in self.encoders:
                        # Handle unseen categories
                        unique_values = set(df_encoded[column].astype(str))
                        known_values = set(self.encoders[column].classes_)
                        
                        # Replace unseen values with most frequent known value
                        if unique_values - known_values:
                            most_frequent = self.encoders[column].classes_[0]
                            df_encoded[column] = df_encoded[column].astype(str).apply(
                                lambda x: most_frequent if x not in known_values else x
                            )
                        
                        df_encoded[f'{column}_encoded'] = self.encoders[column].transform(df_encoded[column].astype(str))
        
        return df_encoded
    
    def train_performance_prediction_model(self, feature_df):
        """Train model to predict member performance scores"""
        
        # Select features for performance prediction
        categorical_features = ['state', 'rank', 'status', 'gender']
        numerical_features = [
            'age', 'years_of_service', 'training_completed', 'operations_participated',
            'commendations', 'attendance_mean', 'duration_hours_mean', 'days_since_joining',
            'join_year', 'join_month', 'assignments_per_month'
        ]
        
        # Filter data - only include members with assignment history
        training_data = feature_df[feature_df['performance_score_count'] > 0].copy()
        
        if len(training_data) < 100:
            return None, "Insufficient data for training (need at least 100 records)"
        
        # Encode categorical features
        training_data = self.encode_categorical_features(training_data, categorical_features, fit=True)
        
        # Prepare feature matrix
        feature_columns = numerical_features + [f'{col}_encoded' for col in categorical_features]
        feature_columns = [col for col in feature_columns if col in training_data.columns]
        
        X = training_data[feature_columns].fillna(0)
        y = training_data['performance_score_mean']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train multiple models and select best
        models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        
        best_model = None
        best_score = -np.inf
        best_model_name = ""
        
        model_scores = {}
        
        for name, model in models.items():
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
            avg_cv_score = np.mean(cv_scores)
            
            # Train on full training set
            model.fit(X_train_scaled, y_train)
            test_score = model.score(X_test_scaled, y_test)
            
            model_scores[name] = {
                'cv_score': avg_cv_score,
                'test_score': test_score,
                'cv_std': np.std(cv_scores)
            }
            
            if avg_cv_score > best_score:
                best_score = avg_cv_score
                best_model = model
                best_model_name = name
        
        # Save best model and scaler
        self.models['performance_prediction'] = best_model
        self.scalers['performance_prediction'] = scaler
        
        # Calculate predictions and metrics
        y_pred = best_model.predict(X_test_scaled)
        
        metrics = {
            'model_name': best_model_name,
            'r2_score': r2_score(y_test, y_pred),
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'feature_importance': dict(zip(feature_columns, 
                getattr(best_model, 'feature_importances_', [0]*len(feature_columns)))),
            'training_size': len(X_train),
            'test_size': len(X_test),
            'all_model_scores': model_scores
        }
        
        self.model_metadata['performance_prediction'] = metrics
        
        # Save model to disk
        self.save_model('performance_prediction')
        
        return metrics, "Model trained successfully"
    
    def train_operations_prediction_model(self, operations_df, assignments_df):
        """Train model to predict future operation needs"""
        
        # Aggregate operations data by month and state
        # Use start_date column (actual column name in the operations data)
        operations_df['start_date'] = pd.to_datetime(operations_df['start_date'])
        operations_df['year_month'] = operations_df['start_date'].dt.to_period('M')
        operations_df['month'] = operations_df['start_date'].dt.month
        operations_df['year'] = operations_df['start_date'].dt.year
        operations_df['day_of_week'] = operations_df['start_date'].dt.dayofweek
        
        # Create time series features
        monthly_ops = operations_df.groupby(['year_month', 'state', 'operation_type']).agg({
            'operation_id': 'count',
            'volunteers_required': 'sum',
            'complexity': lambda x: (x == 'High').sum(),
            'success_rate': 'mean'
        }).reset_index()
        
        monthly_ops.columns = ['year_month', 'state', 'operation_type', 'operation_count', 
                              'total_volunteers', 'high_complexity_count', 'avg_success_rate']
        
        # Add temporal features
        monthly_ops['year_month'] = monthly_ops['year_month'].astype(str)
        monthly_ops['year'] = monthly_ops['year_month'].str[:4].astype(int)
        monthly_ops['month'] = monthly_ops['year_month'].str[-2:].astype(int)
        
        # Add lag features (previous month's data)
        monthly_ops = monthly_ops.sort_values(['state', 'operation_type', 'year', 'month'])
        monthly_ops['prev_operation_count'] = monthly_ops.groupby(['state', 'operation_type'])['operation_count'].shift(1)
        monthly_ops['prev_volunteers'] = monthly_ops.groupby(['state', 'operation_type'])['total_volunteers'].shift(1)
        
        # Remove rows with missing lag features
        training_data = monthly_ops.dropna()
        
        if len(training_data) < 50:
            return None, "Insufficient data for operations prediction"
        
        # Encode categorical features
        categorical_features = ['state', 'operation_type']
        training_data = self.encode_categorical_features(training_data, categorical_features, fit=True)
        
        # Prepare features
        feature_columns = [
            'year', 'month', 'prev_operation_count', 'prev_volunteers', 
            'high_complexity_count', 'avg_success_rate'
        ] + [f'{col}_encoded' for col in categorical_features]
        
        feature_columns = [col for col in feature_columns if col in training_data.columns]
        
        X = training_data[feature_columns].fillna(0)
        y = training_data['operation_count']
        
        # Split and train
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest (best for count prediction)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Save model
        self.models['operations_prediction'] = model
        self.scalers['operations_prediction'] = scaler
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        
        metrics = {
            'model_name': 'random_forest',
            'r2_score': r2_score(y_test, y_pred),
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'feature_importance': dict(zip(feature_columns, model.feature_importances_)),
            'training_size': len(X_train),
            'test_size': len(X_test)
        }
        
        self.model_metadata['operations_prediction'] = metrics
        self.save_model('operations_prediction')
        
        return metrics, "Operations prediction model trained successfully"
    
    def predict_member_performance(self, member_data):
        """Predict performance for new/existing members"""
        if 'performance_prediction' not in self.models:
            return None, "Performance prediction model not trained"
        
        model = self.models['performance_prediction']
        scaler = self.scalers['performance_prediction']
        
        # Prepare features (similar to training)
        categorical_features = ['state', 'rank', 'status', 'gender']
        member_data_encoded = self.encode_categorical_features(member_data, categorical_features, fit=False)
        
        # Use same feature columns as training
        feature_columns = list(self.model_metadata['performance_prediction']['feature_importance'].keys())
        
        X = member_data_encoded[feature_columns].fillna(0)
        X_scaled = scaler.transform(X)
        
        predictions = model.predict(X_scaled)
        return predictions, "Predictions generated successfully"
    
    def predict_future_operations(self, months_ahead=6):
        """Predict future operation needs"""
        if 'operations_prediction' not in self.models:
            return None, "Operations prediction model not trained"
        
        # Generate future time periods
        current_date = datetime.now()
        future_data = []
        
        states = ['Kuala Lumpur', 'Selangor', 'Johor', 'Penang', 'Sabah']  # Sample states
        operation_types = ['Security Patrol', 'Emergency Response', 'Immigration Control', 'Community Safety']
        
        for month_offset in range(1, months_ahead + 1):
            future_date = current_date + timedelta(days=30 * month_offset)
            year = future_date.year
            month = future_date.month
            
            for state in states:
                for op_type in operation_types:
                    future_data.append({
                        'year': year,
                        'month': month,
                        'state': state,
                        'operation_type': op_type,
                        'prev_operation_count': 10,  # Average estimate
                        'prev_volunteers': 150,      # Average estimate
                        'high_complexity_count': 2,
                        'avg_success_rate': 0.85
                    })
        
        future_df = pd.DataFrame(future_data)
        
        # Encode categorical features
        categorical_features = ['state', 'operation_type']
        future_df_encoded = self.encode_categorical_features(future_df, categorical_features, fit=False)
        
        # Prepare features
        feature_columns = list(self.model_metadata['operations_prediction']['feature_importance'].keys())
        X = future_df_encoded[feature_columns].fillna(0)
        
        # Scale and predict
        scaler = self.scalers['operations_prediction']
        model = self.models['operations_prediction']
        
        X_scaled = scaler.transform(X)
        predictions = model.predict(X_scaled)
        
        # Add predictions to dataframe
        future_df['predicted_operations'] = predictions.round().astype(int)
        
        return future_df, "Future operations predicted successfully"
    
    def save_model(self, model_name):
        """Save model, scaler, and metadata to disk"""
        if model_name in self.models:
            model_path = os.path.join(self.models_dir, f"{model_name}_model.pkl")
            scaler_path = os.path.join(self.models_dir, f"{model_name}_scaler.pkl")
            encoder_path = os.path.join(self.models_dir, f"{model_name}_encoders.pkl")
            metadata_path = os.path.join(self.models_dir, f"{model_name}_metadata.pkl")
            
            joblib.dump(self.models[model_name], model_path)
            if model_name in self.scalers:
                joblib.dump(self.scalers[model_name], scaler_path)
            joblib.dump(self.encoders, encoder_path)
            if model_name in self.model_metadata:
                joblib.dump(self.model_metadata[model_name], metadata_path)
    
    def load_model(self, model_name):
        """Load model, scaler, and metadata from disk"""
        model_path = os.path.join(self.models_dir, f"{model_name}_model.pkl")
        scaler_path = os.path.join(self.models_dir, f"{model_name}_scaler.pkl")
        encoder_path = os.path.join(self.models_dir, f"{model_name}_encoders.pkl")
        metadata_path = os.path.join(self.models_dir, f"{model_name}_metadata.pkl")
        
        if os.path.exists(model_path):
            self.models[model_name] = joblib.load(model_path)
            
            if os.path.exists(scaler_path):
                self.scalers[model_name] = joblib.load(scaler_path)
            
            if os.path.exists(encoder_path):
                self.encoders = joblib.load(encoder_path)
                
            if os.path.exists(metadata_path):
                self.model_metadata[model_name] = joblib.load(metadata_path)
            
            return True
        return False
    
    def get_model_summary(self):
        """Get summary of all trained models"""
        summary = {}
        for model_name, metadata in self.model_metadata.items():
            summary[model_name] = {
                'model_type': metadata.get('model_name', 'unknown'),
                'r2_score': metadata.get('r2_score', 0),
                'mae': metadata.get('mae', 0),
                'training_size': metadata.get('training_size', 0),
                'trained_at': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        return summary