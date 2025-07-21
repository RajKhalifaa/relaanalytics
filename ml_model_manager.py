import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MLModelManager:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_metadata = {}
        self.best_models = {}
        self.models_dir = "models"
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def prepare_performance_features(self, members_df, operations_df, assignments_df):
        """Prepare features for performance prediction"""
        
        # Aggregate member performance data
        member_performance = assignments_df.groupby('member_id').agg({
            'performance_score': ['mean', 'std', 'count', 'max', 'min'],
            'attendance': ['mean', 'sum'],
            'duration_hours': ['mean', 'sum'],
            'assignment_date': ['min', 'max', 'count']
        }).round(2)
        
        # Flatten column names
        member_performance.columns = [f"{col[0]}_{col[1]}" for col in member_performance.columns]
        member_performance = member_performance.reset_index()
        
        # Calculate advanced metrics
        member_performance['performance_consistency'] = 1 / (member_performance['performance_score_std'] + 0.1)
        member_performance['days_active'] = (
            member_performance['assignment_date_max'] - member_performance['assignment_date_min']
        ).dt.days
        member_performance['assignments_per_month'] = (
            member_performance['assignment_date_count'] / 
            ((member_performance['days_active'] + 1) / 30)
        ).round(2)
        member_performance['total_hours_worked'] = member_performance['duration_hours_sum']
        member_performance['avg_hours_per_assignment'] = member_performance['duration_hours_mean']
        
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
        feature_df['join_quarter'] = feature_df['join_date'].dt.quarter
        
        # Create derived features
        feature_df['experience_score'] = (
            feature_df['years_of_service'] * 0.3 + 
            feature_df['training_completed'] * 0.2 + 
            feature_df['operations_participated'] * 0.1 +
            feature_df['commendations'] * 0.4
        )
        
        # Age categories
        feature_df['age_category'] = pd.cut(feature_df['age'], 
                                          bins=[0, 25, 35, 45, 55, 100], 
                                          labels=['Young', 'Adult', 'Middle', 'Senior', 'Elder'])
        
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
    
    def train_and_select_best_model(self, feature_df, target_column='performance_score_mean'):
        """Train multiple models and select the best performing one"""
        
        # Filter data - only include members with assignment history
        training_data = feature_df[feature_df['performance_score_count'] > 0].copy()
        
        if len(training_data) < 100:
            return None, "Insufficient data for training (need at least 100 records)"
        
        # Define feature sets
        categorical_features = ['state', 'rank', 'status', 'gender', 'age_category']
        numerical_features = [
            'age', 'years_of_service', 'training_completed', 'operations_participated',
            'commendations', 'attendance_mean', 'duration_hours_mean', 'days_since_joining',
            'join_year', 'join_month', 'join_quarter', 'assignments_per_month',
            'experience_score', 'performance_consistency', 'total_hours_worked',
            'avg_hours_per_assignment', 'attendance_sum'
        ]
        
        # Encode categorical features
        training_data = self.encode_categorical_features(training_data, categorical_features, fit=True)
        
        # Prepare feature matrix
        feature_columns = numerical_features + [f'{col}_encoded' for col in categorical_features]
        feature_columns = [col for col in feature_columns if col in training_data.columns]
        
        X = training_data[feature_columns].fillna(0)
        y = training_data[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=None)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Define models with hyperparameter tuning
        models = {
            'random_forest': {
                'model': RandomForestRegressor(random_state=42),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5, 10]
                }
            },
            'gradient_boosting': {
                'model': GradientBoostingRegressor(random_state=42),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'learning_rate': [0.05, 0.1, 0.2],
                    'max_depth': [3, 5, 7]
                }
            },
            'extra_trees': {
                'model': ExtraTreesRegressor(random_state=42),
                'params': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [10, 20, None]
                }
            },
            'ridge': {
                'model': Ridge(),
                'params': {
                    'alpha': [0.1, 1.0, 10.0, 100.0]
                }
            }
        }
        
        best_model = None
        best_score = -np.inf
        best_model_name = ""
        model_results = {}
        
        print("Training and evaluating models...")
        
        for name, model_config in models.items():
            print(f"Training {name}...")
            
            # Grid search for best hyperparameters
            grid_search = GridSearchCV(
                model_config['model'], 
                model_config['params'], 
                cv=5, 
                scoring='r2',
                n_jobs=-1
            )
            
            grid_search.fit(X_train_scaled, y_train)
            
            # Get best model
            best_estimator = grid_search.best_estimator_
            
            # Cross-validation score
            cv_scores = cross_val_score(best_estimator, X_train_scaled, y_train, cv=5, scoring='r2')
            avg_cv_score = np.mean(cv_scores)
            
            # Test score
            test_score = best_estimator.score(X_test_scaled, y_test)
            
            # Predictions for detailed metrics
            y_pred_train = best_estimator.predict(X_train_scaled)
            y_pred_test = best_estimator.predict(X_test_scaled)
            
            model_results[name] = {
                'model': best_estimator,
                'best_params': grid_search.best_params_,
                'cv_score_mean': avg_cv_score,
                'cv_score_std': np.std(cv_scores),
                'test_r2': test_score,
                'test_mae': mean_absolute_error(y_test, y_pred_test),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'train_r2': r2_score(y_train, y_pred_train),
                'overfitting': abs(r2_score(y_train, y_pred_train) - test_score),
                'feature_importance': getattr(best_estimator, 'feature_importances_', None)
            }
            
            # Select best model based on CV score with penalty for overfitting
            adjusted_score = avg_cv_score - (model_results[name]['overfitting'] * 0.1)
            
            if adjusted_score > best_score:
                best_score = adjusted_score
                best_model = best_estimator
                best_model_name = name
        
        # Store the best model
        self.models['performance_prediction'] = best_model
        self.scalers['performance_prediction'] = scaler
        self.best_models['performance_prediction'] = best_model_name
        
        # Prepare comprehensive metadata
        best_result = model_results[best_model_name]
        
        # Feature importance analysis
        feature_importance = {}
        if best_result['feature_importance'] is not None:
            importance_pairs = list(zip(feature_columns, best_result['feature_importance']))
            importance_pairs.sort(key=lambda x: x[1], reverse=True)
            feature_importance = dict(importance_pairs[:15])  # Top 15 features
        
        metadata = {
            'best_model_name': best_model_name,
            'best_model_params': best_result['best_params'],
            'all_models_results': model_results,
            'performance_metrics': {
                'cv_r2_mean': best_result['cv_score_mean'],
                'cv_r2_std': best_result['cv_score_std'],
                'test_r2': best_result['test_r2'],
                'test_mae': best_result['test_mae'],
                'test_rmse': best_result['test_rmse'],
                'train_r2': best_result['train_r2'],
                'overfitting_score': best_result['overfitting']
            },
            'feature_importance': feature_importance,
            'training_info': {
                'training_size': len(X_train),
                'test_size': len(X_test),
                'feature_count': len(feature_columns),
                'target_column': target_column,
                'trained_at': datetime.now().isoformat()
            },
            'model_comparison': {
                name: {
                    'cv_score': results['cv_score_mean'],
                    'test_r2': results['test_r2'],
                    'overfitting': results['overfitting']
                } 
                for name, results in model_results.items()
            }
        }
        
        self.model_metadata['performance_prediction'] = metadata
        
        # Save model
        self.save_model('performance_prediction')
        
        print(f"Best model: {best_model_name} with CV R² = {best_result['cv_score_mean']:.4f}")
        
        return metadata, f"Successfully trained {best_model_name} model with {best_result['cv_score_mean']:.3f} R² score"
    
    def predict_member_performance(self, member_data):
        """Predict performance for new/existing members"""
        if 'performance_prediction' not in self.models:
            # Try to load saved model
            if not self.load_model('performance_prediction'):
                return None, "No trained model available"
        
        model = self.models['performance_prediction']
        scaler = self.scalers['performance_prediction']
        
        # Prepare features similar to training
        categorical_features = ['state', 'rank', 'status', 'gender', 'age_category']
        member_data_encoded = self.encode_categorical_features(member_data, categorical_features, fit=False)
        
        # Use same feature columns as training
        feature_columns = list(self.model_metadata['performance_prediction']['feature_importance'].keys())
        
        X = member_data_encoded[feature_columns].fillna(0)
        X_scaled = scaler.transform(X)
        
        predictions = model.predict(X_scaled)
        
        # Add confidence intervals (simplified)
        std_pred = np.std(predictions)
        confidence_lower = predictions - 1.96 * std_pred
        confidence_upper = predictions + 1.96 * std_pred
        
        return {
            'predictions': predictions,
            'confidence_lower': confidence_lower,
            'confidence_upper': confidence_upper,
            'model_name': self.best_models.get('performance_prediction', 'unknown')
        }, "Predictions generated successfully"
    
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
        
        try:
            if os.path.exists(model_path):
                self.models[model_name] = joblib.load(model_path)
                
                if os.path.exists(scaler_path):
                    self.scalers[model_name] = joblib.load(scaler_path)
                
                if os.path.exists(encoder_path):
                    self.encoders = joblib.load(encoder_path)
                    
                if os.path.exists(metadata_path):
                    self.model_metadata[model_name] = joblib.load(metadata_path)
                    self.best_models[model_name] = self.model_metadata[model_name].get('best_model_name', 'unknown')
                
                return True
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            
        return False
    
    def get_model_performance_summary(self):
        """Get detailed performance summary of trained models"""
        if 'performance_prediction' not in self.model_metadata:
            return None
            
        metadata = self.model_metadata['performance_prediction']
        
        return {
            'best_model': metadata['best_model_name'],
            'accuracy_metrics': metadata['performance_metrics'],
            'model_comparison': metadata['model_comparison'],
            'training_info': metadata['training_info'],
            'top_features': list(metadata['feature_importance'].keys())[:10]
        }