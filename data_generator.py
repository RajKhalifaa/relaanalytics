import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

class DataGenerator:
    def __init__(self):
        # Use English locale since Malaysian locales are not supported
        self.fake = Faker('en_US')  # Use standard English locale for name generation
        
        # Malaysian states and federal territories
        self.states = [
            'Johor', 'Kedah', 'Kelantan', 'Malacca', 'Negeri Sembilan',
            'Pahang', 'Penang', 'Perak', 'Perlis', 'Sabah', 'Sarawak',
            'Selangor', 'Terengganu', 'Kuala Lumpur', 'Labuan', 'Putrajaya'
        ]
        
        # Malaysian districts (sample for each state)
        self.districts = {
            'Johor': ['Johor Bahru', 'Kulai', 'Pontian', 'Segamat', 'Kluang'],
            'Kedah': ['Alor Setar', 'Sungai Petani', 'Kulim', 'Langkawi', 'Baling'],
            'Kelantan': ['Kota Bharu', 'Tanah Merah', 'Machang', 'Pasir Mas', 'Gua Musang'],
            'Malacca': ['Melaka Tengah', 'Alor Gajah', 'Jasin'],
            'Negeri Sembilan': ['Seremban', 'Port Dickson', 'Rembau', 'Tampin', 'Kuala Pilah'],
            'Pahang': ['Kuantan', 'Temerloh', 'Bentong', 'Raub', 'Pekan'],
            'Penang': ['Georgetown', 'Seberang Perai', 'Bayan Lepas', 'Bukit Mertajam'],
            'Perak': ['Ipoh', 'Taiping', 'Kuala Kangsar', 'Teluk Intan', 'Sitiawan'],
            'Perlis': ['Kangar', 'Arau', 'Padang Besar'],
            'Sabah': ['Kota Kinabalu', 'Sandakan', 'Tawau', 'Lahad Datu', 'Keningau'],
            'Sarawak': ['Kuching', 'Miri', 'Sibu', 'Bintulu', 'Sri Aman'],
            'Selangor': ['Shah Alam', 'Petaling Jaya', 'Subang Jaya', 'Kajang', 'Klang'],
            'Terengganu': ['Kuala Terengganu', 'Kemaman', 'Dungun', 'Marang', 'Besut'],
            'Kuala Lumpur': ['Cheras', 'Wangsa Maju', 'Kepong', 'Seputeh', 'Titiwangsa'],
            'Labuan': ['Victoria'],
            'Putrajaya': ['Putrajaya']
        }
        
        # RELA operation types
        self.operation_types = [
            'Security Control', 'Immigration Check', 'Emergency Response',
            'Traffic Control', 'Crowd Control', 'Search and Rescue',
            'Disaster Relief', 'Community Patrol', 'Border Security',
            'Event Security', 'Crime Prevention', 'Public Safety'
        ]
        
        # RELA ranks/positions
        self.ranks = [
            'Volunteer', 'Senior Volunteer', 'Team Leader', 'Squad Leader',
            'Platoon Commander', 'Company Commander', 'Battalion Commander',
            'District Commander', 'State Commander'
        ]
        
        # Malaysian ethnic groups
        self.ethnicities = ['Malay', 'Chinese', 'Indian', 'Indigenous', 'Others']
        
        # Education levels
        self.education_levels = [
            'Primary', 'Secondary', 'Certificate/Diploma', 'Degree', 'Postgraduate'
        ]
        
        # Age groups with realistic distributions for volunteers
        self.age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        
        # Malaysian names for realistic data generation
        self.malay_male_names = [
            'Ahmad', 'Muhammad', 'Abdul', 'Mohd', 'Azman', 'Rahman', 'Hassan', 'Ibrahim',
            'Ismail', 'Karim', 'Rashid', 'Salleh', 'Yusof', 'Zainal', 'Rosli', 'Hamid'
        ]
        self.malay_female_names = [
            'Siti', 'Fatimah', 'Aminah', 'Khadijah', 'Mariam', 'Zainab', 'Rohana', 'Halimah',
            'Noraini', 'Salimah', 'Ramlah', 'Zaharah', 'Fauziah', 'Normah', 'Sharifah', 'Zaleha'
        ]
        self.chinese_male_names = [
            'Wei Ming', 'Jun Hao', 'Kai Xin', 'Chong Wei', 'Yee Chuan', 'Teck Wah', 'Boon Seng',
            'Chee Kong', 'Wai Kit', 'Jin Seng', 'Kok Leong', 'Swee Heng', 'Yong Seng', 'Tian Wei'
        ]
        self.chinese_female_names = [
            'Li Ling', 'Mei Yee', 'Pei Ling', 'Hui Min', 'Yee Ling', 'Siew Mei', 'Bee Lian',
            'Lai Yee', 'Mun Yee', 'Swee Lian', 'Chui Ling', 'Yoke Lan', 'Wai Yee', 'Geok Lan'
        ]
        self.indian_male_names = [
            'Rajesh', 'Suresh', 'Ramesh', 'Ganesh', 'Vikram', 'Arun', 'Ravi', 'Kumar',
            'Deepak', 'Mohan', 'Prakash', 'Vinod', 'Ajay', 'Sanjay', 'Mukesh', 'Mahesh'
        ]
        self.indian_female_names = [
            'Priya', 'Sunita', 'Meera', 'Kavitha', 'Shanti', 'Latha', 'Prema', 'Kamala',
            'Radha', 'Sushila', 'Usha', 'Geetha', 'Malathi', 'Vasantha', 'Chitra', 'Indira'
        ]
        
    def generate_members_data(self, num_members=3000000):
        """Generate comprehensive RELA member dataset"""
        print(f"Generating {num_members:,} RELA member records...")
        
        members = []
        
        for i in range(num_members):
            if i % 100000 == 0:
                print(f"Generated {i:,} members...")
            
            # Basic demographics
            gender = random.choice(['Male', 'Female'])
            age = self._generate_realistic_age()
            age_group = self._get_age_group(age)
            
            # Location
            state = random.choices(
                self.states,
                weights=[15, 8, 7, 4, 5, 6, 4, 9, 1, 12, 10, 18, 5, 8, 1, 1],  # Population-based weights
                k=1
            )[0]
            district = random.choice(self.districts[state])
            
            # RELA specific data
            rank = random.choices(
                self.ranks,
                weights=[40, 25, 15, 8, 5, 3, 2, 1.5, 0.5],  # Hierarchical distribution
                k=1
            )[0]
            
            join_date = self.fake.date_between(start_date='-20y', end_date='today')
            years_service = (datetime.now().date() - join_date).days / 365.25
            
            status = random.choices(
                ['Active', 'Inactive', 'On Leave', 'Training'],
                weights=[70, 20, 5, 5],
                k=1
            )[0]
            
            # Generate ethnicity-appropriate name
            ethnicity = random.choices(
                self.ethnicities,
                weights=[60, 25, 8, 5, 2],  # Malaysian demographic distribution
                k=1
            )[0]
            
            full_name = self._generate_malaysian_name(gender, ethnicity)
            
            # Generate member record
            member = {
                'member_id': f"RELA{str(i+1).zfill(8)}",
                'full_name': full_name,
                'ic_number': self._generate_ic_number(),
                'gender': gender,
                'age': age,
                'age_group': age_group,
                'ethnicity': ethnicity,
                'education_level': random.choices(
                    self.education_levels,
                    weights=[10, 35, 30, 20, 5],
                    k=1
                )[0],
                'state': state,
                'district': district,
                'rank': rank,
                'status': status,
                'join_date': join_date,
                'years_of_service': round(years_service, 1),
                'phone_number': self._generate_malaysian_phone(),
                'email': self.fake.email(),
                'training_completed': random.randint(1, 15),
                'operations_participated': random.randint(0, 50),
                'commendations': random.randint(0, 5),
                'last_active_date': self._generate_last_active_date(status),
                'emergency_contact': self.fake.phone_number(),
                'address': f"{self.fake.street_address()}, {district}, {state}",
                'postal_code': self.fake.postcode(),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            members.append(member)
        
        df = pd.DataFrame(members)
        print(f"✅ Generated {len(df):,} RELA member records")
        return df
    
    def generate_operations_data(self, num_operations=50000):
        """Generate RELA operations dataset"""
        print(f"Generating {num_operations:,} operation records...")
        
        operations = []
        
        for i in range(num_operations):
            if i % 10000 == 0:
                print(f"Generated {i:,} operations...")
            
            state = random.choice(self.states)
            district = random.choice(self.districts[state])
            operation_type = random.choice(self.operation_types)
            
            start_date = self.fake.date_time_between(start_date='-2y', end_date='now')
            duration_hours = random.choices(
                [2, 4, 6, 8, 12, 24, 48],
                weights=[20, 25, 20, 15, 10, 8, 2],
                k=1
            )[0]
            end_date = start_date + timedelta(hours=duration_hours)
            
            # Operation complexity affects resource allocation
            complexity = random.choices(
                ['Low', 'Medium', 'High', 'Critical'],
                weights=[40, 35, 20, 5],
                k=1
            )[0]
            
            volunteers_assigned = self._get_volunteers_by_complexity(complexity)
            
            operation = {
                'operation_id': f"OPS{str(i+1).zfill(6)}",
                'operation_name': f"{operation_type} - {district}",
                'operation_type': operation_type,
                'state': state,
                'district': district,
                'start_date': start_date,
                'end_date': end_date,
                'duration_hours': duration_hours,
                'status': random.choices(
                    ['Completed', 'Ongoing', 'Planned', 'Cancelled'],
                    weights=[70, 15, 10, 5],
                    k=1
                )[0],
                'complexity': complexity,
                'volunteers_assigned': volunteers_assigned,
                'volunteers_responded': random.randint(
                    int(volunteers_assigned * 0.7), volunteers_assigned
                ),
                'success_rate': random.uniform(0.75, 1.0),
                'budget_allocated': random.uniform(1000, 50000),
                'equipment_used': random.randint(5, 50),
                'vehicles_deployed': random.randint(1, 10),
                'public_impact_score': random.uniform(1, 10),
                'media_coverage': random.choice([True, False]),
                'weather_condition': random.choice(['Clear', 'Rainy', 'Cloudy', 'Stormy']),
                'time_of_day': self._get_time_category(start_date.hour),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            operations.append(operation)
        
        df = pd.DataFrame(operations)
        print(f"✅ Generated {len(df):,} operation records")
        return df
    
    def generate_assignments_data(self, members_df, num_assignments=200000):
        """Generate individual volunteer assignments"""
        print(f"Generating {num_assignments:,} assignment records...")
        
        assignments = []
        
        # Sample active members for assignments
        active_members = members_df[members_df['status'] == 'Active'].sample(
            min(len(members_df), num_assignments // 3)
        )
        
        for i in range(num_assignments):
            if i % 20000 == 0:
                print(f"Generated {i:,} assignments...")
            
            # Select random member
            member = active_members.sample(1).iloc[0]
            
            assignment_type = random.choice(self.operation_types)
            assignment_date = self.fake.date_time_between(start_date='-1y', end_date='now')
            
            # Performance metrics
            attendance = random.choice([True, False]) if random.random() > 0.1 else True
            performance_score = random.uniform(6, 10) if attendance else 0
            
            assignment = {
                'assignment_id': f"ASG{str(i+1).zfill(7)}",
                'member_id': member['member_id'],
                'assignment_type': assignment_type,
                'assignment_date': assignment_date,
                'state': member['state'],
                'district': member['district'],
                'duration_hours': random.choice([2, 4, 6, 8, 12]),
                'attendance': attendance,
                'performance_score': round(performance_score, 1),
                'role': random.choice(['Leader', 'Member', 'Coordinator', 'Support']),
                'equipment_issued': random.choice([True, False]),
                'transportation_provided': random.choice([True, False]),
                'overtime': random.choice([True, False]),
                'hazard_level': random.choice(['Low', 'Medium', 'High']),
                'training_required': random.choice([True, False]),
                'feedback_score': random.uniform(1, 5) if attendance else None,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            assignments.append(assignment)
        
        df = pd.DataFrame(assignments)
        print(f"✅ Generated {len(df):,} assignment records")
        return df
    
    def _generate_realistic_age(self):
        """Generate realistic age distribution for volunteers"""
        return int(np.random.normal(40, 12))  # Mean 40, std 12
    
    def _get_age_group(self, age):
        """Categorize age into groups"""
        if age < 26:
            return '18-25'
        elif age < 36:
            return '26-35'
        elif age < 46:
            return '36-45'
        elif age < 56:
            return '46-55'
        elif age < 66:
            return '56-65'
        else:
            return '65+'
    
    def _generate_ic_number(self):
        """Generate Malaysian IC number format"""
        year = random.randint(50, 99)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        place = random.randint(1, 99)
        last_digits = random.randint(1000, 9999)
        return f"{year:02d}{month:02d}{day:02d}{place:02d}{last_digits}"
    
    def _generate_malaysian_phone(self):
        """Generate Malaysian phone number format"""
        prefixes = ['01', '03', '04', '05', '06', '07', '08', '09']
        prefix = random.choice(prefixes)
        if prefix == '01':
            # Mobile numbers
            middle = random.choice(['2', '3', '4', '5', '6', '7', '8', '9'])
            number = f"01{middle}-{random.randint(1000000, 9999999)}"
        else:
            # Landline numbers
            number = f"{prefix}-{random.randint(1000000, 9999999)}"
        return number
    
    def _generate_last_active_date(self, status):
        """Generate last active date based on status"""
        if status == 'Active':
            return self.fake.date_between(start_date='-30d', end_date='today')
        elif status == 'On Leave':
            return self.fake.date_between(start_date='-90d', end_date='-30d')
        elif status == 'Training':
            return self.fake.date_between(start_date='-7d', end_date='today')
        else:  # Inactive
            return self.fake.date_between(start_date='-365d', end_date='-90d')
    
    def _get_volunteers_by_complexity(self, complexity):
        """Determine volunteer allocation based on operation complexity"""
        if complexity == 'Low':
            return random.randint(5, 20)
        elif complexity == 'Medium':
            return random.randint(20, 50)
        elif complexity == 'High':
            return random.randint(50, 100)
        else:  # Critical
            return random.randint(100, 200)
    
    def _get_time_category(self, hour):
        """Categorize time of day"""
        if 6 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 18:
            return 'Afternoon'
        elif 18 <= hour < 22:
            return 'Evening'
        else:
            return 'Night'
    
    def _generate_malaysian_name(self, gender, ethnicity):
        """Generate Malaysian names based on ethnicity and gender"""
        if ethnicity == 'Malay':
            if gender == 'Male':
                first_name = random.choice(self.malay_male_names)
                last_name = random.choice(['bin', 'b.']) + ' ' + random.choice(self.malay_male_names)
            else:
                first_name = random.choice(self.malay_female_names)
                last_name = random.choice(['binti', 'bt.']) + ' ' + random.choice(self.malay_male_names)
            return f"{first_name} {last_name}"
        
        elif ethnicity == 'Chinese':
            if gender == 'Male':
                name = random.choice(self.chinese_male_names)
            else:
                name = random.choice(self.chinese_female_names)
            family_name = random.choice(['Lim', 'Tan', 'Lee', 'Ong', 'Ng', 'Wong', 'Teh', 'Chan'])
            return f"{family_name} {name}"
        
        elif ethnicity == 'Indian':
            if gender == 'Male':
                first_name = random.choice(self.indian_male_names)
                last_name = random.choice(['s/o', 'a/l']) + ' ' + random.choice(self.indian_male_names)
            else:
                first_name = random.choice(self.indian_female_names)
                last_name = random.choice(['d/o', 'a/p']) + ' ' + random.choice(self.indian_male_names)
            return f"{first_name} {last_name}"
        
        else:  # Indigenous or Others
            # Use faker for other ethnicities
            return self.fake.name()
