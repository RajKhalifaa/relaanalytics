import pandas as pd
import os
import json
from datetime import datetime
from data_generator import DataGenerator

class DataPersistence:
    def __init__(self):
        self.data_dir = "data"
        self.members_file = "members.csv"
        self.operations_file = "operations.csv"
        self.assignments_file = "assignments.csv"
        self.metadata_file = "metadata.json"
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def get_file_paths(self):
        return {
            'members': os.path.join(self.data_dir, self.members_file),
            'operations': os.path.join(self.data_dir, self.operations_file),
            'assignments': os.path.join(self.data_dir, self.assignments_file),
            'metadata': os.path.join(self.data_dir, self.metadata_file)
        }
    
    def data_exists(self):
        """Check if all required data files exist"""
        paths = self.get_file_paths()
        return all(os.path.exists(path) for path in [paths['members'], paths['operations'], paths['assignments']])
    
    def save_data(self, members_df, operations_df, assignments_df):
        """Save all dataframes to CSV files with metadata"""
        paths = self.get_file_paths()
        
        try:
            # Save dataframes
            members_df.to_csv(paths['members'], index=False)
            operations_df.to_csv(paths['operations'], index=False)
            assignments_df.to_csv(paths['assignments'], index=False)
            
            # Save metadata
            metadata = {
                'generated_date': datetime.now().isoformat(),
                'members_count': len(members_df),
                'operations_count': len(operations_df),
                'assignments_count': len(assignments_df),
                'version': '1.0'
            }
            
            with open(paths['metadata'], 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_data(self):
        """Load all dataframes from CSV files"""
        paths = self.get_file_paths()
        
        try:
            members_df = pd.read_csv(paths['members'])
            operations_df = pd.read_csv(paths['operations'])
            assignments_df = pd.read_csv(paths['assignments'])
            
            # Convert date columns back to datetime
            members_df['join_date'] = pd.to_datetime(members_df['join_date'])
            operations_df['start_date'] = pd.to_datetime(operations_df['start_date'])
            operations_df['end_date'] = pd.to_datetime(operations_df['end_date'])
            assignments_df['assignment_date'] = pd.to_datetime(assignments_df['assignment_date'])
            
            return members_df, operations_df, assignments_df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None, None, None
    
    def get_metadata(self):
        """Get metadata about the saved data"""
        paths = self.get_file_paths()
        
        try:
            with open(paths['metadata'], 'r') as f:
                return json.load(f)
        except:
            return None
    
    def generate_and_save_data(self, members_count=50000, operations_count=5000, assignments_count=20000):
        """Generate new data and save it"""
        data_gen = DataGenerator()
        
        print(f"Generating {members_count:,} members...")
        members_df = data_gen.generate_members_data(members_count)
        
        print(f"Generating {operations_count:,} operations...")
        operations_df = data_gen.generate_operations_data(operations_count)
        
        print(f"Generating {assignments_count:,} assignments...")
        assignments_df = data_gen.generate_assignments_data(members_df, assignments_count)
        
        print("Saving data to files...")
        success = self.save_data(members_df, operations_df, assignments_df)
        
        if success:
            print("Data generated and saved successfully!")
            return members_df, operations_df, assignments_df
        else:
            print("Failed to save data!")
            return None, None, None
    
    def delete_data(self):
        """Delete all saved data files"""
        paths = self.get_file_paths()
        
        for path in paths.values():
            if os.path.exists(path):
                os.remove(path)
        
        # Remove directory if empty
        if os.path.exists(self.data_dir) and not os.listdir(self.data_dir):
            os.rmdir(self.data_dir)