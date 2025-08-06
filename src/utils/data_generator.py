import pandas as pd
import numpy as np
import math
from faker import Faker
from datetime import datetime, timedelta
import random


class DataGenerator:
    def __init__(self):
        # Use English locale since Malaysian locales are not supported
        self.fake = Faker("en_US")  # Use standard English locale for name generation

        # Malaysian states and federal territories
        self.states = [
            "Johor",
            "Kedah",
            "Kelantan",
            "Malacca",
            "Negeri Sembilan",
            "Pahang",
            "Penang",
            "Perak",
            "Perlis",
            "Sabah",
            "Sarawak",
            "Selangor",
            "Terengganu",
            "Kuala Lumpur",
            "Labuan",
            "Putrajaya",
        ]

        # Malaysian districts (sample for each state)
        self.districts = {
            "Johor": ["Johor Bahru", "Kulai", "Pontian", "Segamat", "Kluang"],
            "Kedah": ["Alor Setar", "Sungai Petani", "Kulim", "Langkawi", "Baling"],
            "Kelantan": [
                "Kota Bharu",
                "Tanah Merah",
                "Machang",
                "Pasir Mas",
                "Gua Musang",
            ],
            "Malacca": ["Melaka Tengah", "Alor Gajah", "Jasin"],
            "Negeri Sembilan": [
                "Seremban",
                "Port Dickson",
                "Rembau",
                "Tampin",
                "Kuala Pilah",
            ],
            "Pahang": ["Kuantan", "Temerloh", "Bentong", "Raub", "Pekan"],
            "Penang": ["Georgetown", "Seberang Perai", "Bayan Lepas", "Bukit Mertajam"],
            "Perak": ["Ipoh", "Taiping", "Kuala Kangsar", "Teluk Intan", "Sitiawan"],
            "Perlis": ["Kangar", "Arau", "Padang Besar"],
            "Sabah": ["Kota Kinabalu", "Sandakan", "Tawau", "Lahad Datu", "Keningau"],
            "Sarawak": ["Kuching", "Miri", "Sibu", "Bintulu", "Sri Aman"],
            "Selangor": [
                "Shah Alam",
                "Petaling Jaya",
                "Subang Jaya",
                "Kajang",
                "Klang",
            ],
            "Terengganu": ["Kuala Terengganu", "Kemaman", "Dungun", "Marang", "Besut"],
            "Kuala Lumpur": [
                "Cheras",
                "Wangsa Maju",
                "Kepong",
                "Seputeh",
                "Titiwangsa",
            ],
            "Labuan": ["Victoria"],
            "Putrajaya": ["Putrajaya"],
        }

        # RELA operation types
        self.operation_types = [
            "Security Control",
            "Immigration Check",
            "Emergency Response",
            "Traffic Control",
            "Crowd Control",
            "Search and Rescue",
            "Disaster Relief",
            "Community Patrol",
            "Border Security",
            "Event Security",
            "Crime Prevention",
            "Public Safety",
        ]

        # RELA ranks/positions
        self.ranks = [
            "Volunteer",
            "Senior Volunteer",
            "Team Leader",
            "Squad Leader",
            "Platoon Commander",
            "Company Commander",
            "Battalion Commander",
            "District Commander",
            "State Commander",
        ]

        # Malaysian ethnic groups
        self.ethnicities = ["Malay", "Chinese", "Indian", "Others"]

        # Education levels
        self.education_levels = [
            "Primary",
            "Secondary",
            "Certificate/Diploma",
            "Degree",
            "Postgraduate",
        ]

        # Age groups with realistic distributions for volunteers
        self.age_groups = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]

        # Malaysian names for realistic data generation
        self.malay_male_names = [
            "Ahmad",
            "Muhammad",
            "Abdul",
            "Mohd",
            "Azman",
            "Rahman",
            "Hassan",
            "Ibrahim",
            "Ismail",
            "Karim",
            "Rashid",
            "Salleh",
            "Yusof",
            "Zainal",
            "Rosli",
            "Hamid",
        ]
        self.malay_female_names = [
            "Siti",
            "Fatimah",
            "Aminah",
            "Khadijah",
            "Mariam",
            "Zainab",
            "Rohana",
            "Halimah",
            "Noraini",
            "Salimah",
            "Ramlah",
            "Zaharah",
            "Fauziah",
            "Normah",
            "Sharifah",
            "Zaleha",
        ]
        self.chinese_male_names = [
            "Wei Ming",
            "Jun Hao",
            "Kai Xin",
            "Chong Wei",
            "Yee Chuan",
            "Teck Wah",
            "Boon Seng",
            "Chee Kong",
            "Wai Kit",
            "Jin Seng",
            "Kok Leong",
            "Swee Heng",
            "Yong Seng",
            "Tian Wei",
        ]
        self.chinese_female_names = [
            "Li Ling",
            "Mei Yee",
            "Pei Ling",
            "Hui Min",
            "Yee Ling",
            "Siew Mei",
            "Bee Lian",
            "Lai Yee",
            "Mun Yee",
            "Swee Lian",
            "Chui Ling",
            "Yoke Lan",
            "Wai Yee",
            "Geok Lan",
        ]
        self.indian_male_names = [
            "Rajesh",
            "Suresh",
            "Ramesh",
            "Ganesh",
            "Vikram",
            "Arun",
            "Ravi",
            "Kumar",
            "Deepak",
            "Mohan",
            "Prakash",
            "Vinod",
            "Ajay",
            "Sanjay",
            "Mukesh",
            "Mahesh",
        ]
        self.indian_female_names = [
            "Priya",
            "Sunita",
            "Meera",
            "Kavitha",
            "Shanti",
            "Latha",
            "Prema",
            "Kamala",
            "Radha",
            "Sushila",
            "Usha",
            "Geetha",
            "Malathi",
            "Vasantha",
            "Chitra",
            "Indira",
        ]

    def generate_members_data(self, num_members=3000000):
        """Generate comprehensive RELA member dataset"""
        print(f"Generating {num_members:,} RELA member records...")

        members = []

        for i in range(num_members):
            if i % 100000 == 0:
                print(f"Generated {i:,} members...")

            # Basic demographics
            gender = random.choice(["Male", "Female"])
            age = self._generate_realistic_age()
            age_group = self._get_age_group(age)

            # Location
            state = random.choices(
                self.states,
                weights=[
                    15,
                    8,
                    7,
                    4,
                    5,
                    6,
                    4,
                    9,
                    1,
                    12,
                    10,
                    18,
                    5,
                    8,
                    1,
                    1,
                ],  # Population-based weights
                k=1,
            )[0]
            district = random.choice(self.districts[state])

            # RELA specific data
            rank = random.choices(
                self.ranks,
                weights=[40, 25, 15, 8, 5, 3, 2, 1.5, 0.5],  # Hierarchical distribution
                k=1,
            )[0]

            # Generate more realistic join dates with growth patterns
            # Simulate organizational growth: more recent hires, expansion periods
            current_year = datetime.now().year

            # Create weighted periods for more realistic growth
            if i < num_members * 0.15:  # 15% - founding members (8-10 years ago)
                join_date = self.fake.date_between(start_date="-10y", end_date="-8y")
            elif i < num_members * 0.35:  # 20% - early growth (6-8 years ago)
                join_date = self.fake.date_between(start_date="-8y", end_date="-6y")
            elif i < num_members * 0.55:  # 20% - steady period (4-6 years ago)
                join_date = self.fake.date_between(start_date="-6y", end_date="-4y")
            elif i < num_members * 0.75:  # 20% - expansion (2-4 years ago)
                join_date = self.fake.date_between(start_date="-4y", end_date="-2y")
            else:  # 25% - recent growth (0-2 years ago)
                join_date = self.fake.date_between(start_date="-2y", end_date="today")

            years_service = (datetime.now().date() - join_date).days / 365.25

            status = random.choices(
                ["Active", "Inactive", "On Leave", "Training"],
                weights=[70, 20, 5, 5],
                k=1,
            )[0]

            # Generate ethnicity-appropriate name
            ethnicity = random.choices(
                self.ethnicities,
                weights=[
                    60,
                    25,
                    10,
                    5,
                ],  # Malaysian demographic distribution: Malay, Chinese, Indian, Others
                k=1,
            )[0]

            full_name = self._generate_malaysian_name(gender, ethnicity)

            # Generate member record
            member = {
                "member_id": f"RELA{str(i+1).zfill(8)}",
                "full_name": full_name,
                "ic_number": self._generate_ic_number(),
                "gender": gender,
                "age": age,
                "age_group": age_group,
                "ethnicity": ethnicity,
                "education_level": random.choices(
                    self.education_levels, weights=[10, 35, 30, 20, 5], k=1
                )[0],
                "state": state,
                "district": district,
                "rank": rank,
                "status": status,
                "join_date": join_date,
                "years_of_service": round(years_service, 1),
                "phone_number": self._generate_malaysian_phone(),
                "email": self._generate_realistic_email(full_name),
                "training_completed": self._generate_realistic_training(
                    years_service, rank
                ),
                "operations_participated": self._generate_realistic_operations_count(
                    years_service, status
                ),
                "commendations": self._generate_realistic_commendations(
                    years_service, rank
                ),
                "last_active_date": self._generate_last_active_date(status),
                "emergency_contact": self.fake.phone_number(),
                "address": f"{self.fake.street_address()}, {district}, {state}",
                "postal_code": self.fake.postcode(),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
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

            start_date = self.fake.date_time_between(start_date="-2y", end_date="now")
            duration_hours = random.choices(
                [2, 4, 6, 8, 12, 24, 48], weights=[20, 25, 20, 15, 10, 8, 2], k=1
            )[0]
            end_date = start_date + timedelta(hours=duration_hours)

            # Operation complexity affects resource allocation
            complexity = random.choices(
                ["Low", "Medium", "High", "Critical"], weights=[40, 35, 20, 5], k=1
            )[0]

            volunteers_assigned = self._get_volunteers_by_complexity(complexity)

            # More realistic success rate based on multiple factors
            base_success_rate = 0.82

            # Complexity affects success rate
            complexity_modifier = {
                "Low": 0.08,
                "Medium": 0.03,
                "High": -0.05,
                "Critical": -0.12,
            }

            # Weather affects success rate
            weather = random.choices(
                ["Clear", "Rainy", "Cloudy", "Stormy"], weights=[50, 25, 20, 5], k=1
            )[0]
            weather_modifier = {
                "Clear": 0.05,
                "Cloudy": 0.02,
                "Rainy": -0.08,
                "Stormy": -0.15,
            }

            # Duration affects success rate (very long operations are harder)
            duration_modifier = -0.01 * max(0, duration_hours - 8)

            final_success_rate = (
                base_success_rate
                + complexity_modifier.get(complexity, 0)
                + weather_modifier.get(weather, 0)
                + duration_modifier
            )
            final_success_rate = max(
                0.3, min(1.0, final_success_rate + random.uniform(-0.1, 0.1))
            )

            # Response rate correlates with operation urgency and timing
            base_response_rate = 0.85
            if complexity == "Critical":
                base_response_rate = 0.95
            elif complexity == "High":
                base_response_rate = 0.9

            # Night operations have lower response rates
            time_of_day = self._get_time_category(start_date.hour)
            if time_of_day == "Night":
                base_response_rate -= 0.1

            volunteers_responded = int(
                volunteers_assigned * (base_response_rate + random.uniform(-0.05, 0.05))
            )
            volunteers_responded = max(
                1, min(volunteers_assigned, volunteers_responded)
            )

            # Budget allocation based on complexity and duration
            base_budget = {
                "Low": 2000,
                "Medium": 8000,
                "High": 20000,
                "Critical": 50000,
            }
            budget_allocated = (
                base_budget[complexity]
                * (1 + duration_hours * 0.1)
                * random.uniform(0.8, 1.2)
            )

            operation = {
                "operation_id": f"OPS{str(i+1).zfill(6)}",
                "operation_name": f"{operation_type} - {district}",
                "operation_type": operation_type,
                "state": state,
                "district": district,
                "start_date": start_date,
                "end_date": end_date,
                "duration_hours": duration_hours,
                "status": random.choices(
                    ["Completed", "Ongoing", "Planned", "Cancelled"],
                    weights=[70, 15, 10, 5],
                    k=1,
                )[0],
                "complexity": complexity,
                "volunteers_assigned": volunteers_assigned,
                "volunteers_responded": volunteers_responded,
                "success_rate": round(final_success_rate, 3),
                "budget_allocated": round(budget_allocated, 2),
                "equipment_used": random.randint(
                    max(1, volunteers_assigned // 5), volunteers_assigned // 2
                ),
                "vehicles_deployed": random.randint(
                    1, max(2, volunteers_assigned // 10)
                ),
                "public_impact_score": round(random.uniform(1, 10), 1),
                "media_coverage": random.random()
                < (0.8 if complexity in ["High", "Critical"] else 0.2),
                "weather_condition": weather,
                "time_of_day": time_of_day,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
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
        active_members = members_df[members_df["status"] == "Active"].sample(
            min(len(members_df), num_assignments // 3)
        )

        for i in range(num_assignments):
            if i % 20000 == 0:
                print(f"Generated {i:,} assignments...")

            # Select random member
            member = active_members.sample(1).iloc[0]

            assignment_type = random.choice(self.operation_types)
            assignment_date = self.fake.date_time_between(
                start_date="-1y", end_date="now"
            )

            # More realistic performance metrics
            # Attendance rate correlates with member experience and rank
            base_attendance_rate = 0.85

            # Adjust based on member characteristics
            rank_bonus = {
                "Volunteer": 0,
                "Senior Volunteer": 0.02,
                "Team Leader": 0.05,
                "Squad Leader": 0.07,
                "Platoon Commander": 0.1,
            }
            rank_adj = rank_bonus.get(member.get("rank", "Volunteer"), 0)

            years_bonus = min(member.get("years_of_service", 0) * 0.01, 0.1)
            final_attendance_rate = min(
                base_attendance_rate + rank_adj + years_bonus, 0.95
            )

            attendance = random.random() < final_attendance_rate

            # Performance score based on attendance, experience, and temporal improvement
            if attendance:
                base_score = 7.0
                experience_bonus = min(member.get("years_of_service", 0) * 0.1, 1.5)
                rank_bonus_score = (
                    rank_bonus.get(member.get("rank", "Volunteer"), 0) * 10
                )

                # Add realistic temporal improvement with fluctuations
                days_from_start = (assignment_date - datetime(2023, 1, 1)).days
                # Base improvement trend
                base_improvement = min(days_from_start * 0.0003, 0.8)
                # Add quarterly fluctuations (training cycles, seasonal effects)
                quarter = ((assignment_date.month - 1) // 3) + 1
                quarterly_variation = 0.2 * math.sin(quarter * math.pi / 2)
                # Add some realistic noise and occasional setbacks
                noise = random.uniform(-0.3, 0.3)
                # Occasional performance dips (10% chance)
                if random.random() < 0.1:
                    noise -= random.uniform(0.2, 0.5)
                temporal_improvement = base_improvement + quarterly_variation + noise
                temporal_improvement = max(
                    temporal_improvement, -0.5
                )  # Don't go too negative

                # More realistic seasonal variations
                seasonal_base = 0.05 * math.sin(
                    (assignment_date.month - 1) * math.pi / 6
                )
                # Add weather-related effects
                if assignment_date.month in [11, 12, 1, 2]:  # Monsoon season
                    seasonal_base -= 0.1
                elif assignment_date.month in [
                    6,
                    7,
                    8,
                ]:  # School holidays - better availability
                    seasonal_base += 0.05
                month_factor = 1.0 + seasonal_base

                performance_score = (
                    base_score
                    + experience_bonus
                    + rank_bonus_score
                    + temporal_improvement
                )
                performance_score *= month_factor
                performance_score += random.uniform(
                    -1.2, 1.2
                )  # More realistic random variation
                performance_score = min(
                    max(performance_score, 5.0), 10.0
                )  # Bounds checking
            else:
                performance_score = 0

            assignment = {
                "assignment_id": f"ASG{str(i+1).zfill(7)}",
                "member_id": member["member_id"],
                "assignment_type": assignment_type,
                "assignment_date": assignment_date,
                "state": member["state"],
                "district": member["district"],
                "duration_hours": random.choice([2, 4, 6, 8, 10, 12]),
                "attendance": attendance,
                "performance_score": round(performance_score, 1),
                "role": random.choice(["Leader", "Member", "Coordinator", "Support"]),
                "equipment_issued": random.choice([True, False]),
                "transportation_provided": random.choice([True, False]),
                "overtime": random.choice([True, False]),
                "hazard_level": random.choice(["Low", "Medium", "High"]),
                "training_required": random.choice([True, False]),
                "feedback_score": random.uniform(1, 5) if attendance else None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            assignments.append(assignment)

        df = pd.DataFrame(assignments)
        print(f"✅ Generated {len(df):,} assignment records")
        return df

    def _generate_realistic_age(self):
        """Generate realistic age distribution for volunteers"""
        # More realistic age distribution for Malaysian volunteers
        age = int(np.random.normal(42, 14))  # Mean 42, std 14
        return max(18, min(75, age))  # Ensure within valid range

    def _get_age_group(self, age):
        """Categorize age into groups"""
        if age < 26:
            return "18-25"
        elif age < 36:
            return "26-35"
        elif age < 46:
            return "36-45"
        elif age < 56:
            return "46-55"
        elif age < 66:
            return "56-65"
        else:
            return "65+"

    def _generate_ic_number(self):
        """Generate realistic Malaysian IC number format"""
        # Generate birth year based on realistic age ranges
        current_year = datetime.now().year
        birth_year = current_year - random.randint(18, 75)
        year_code = birth_year % 100

        month = random.randint(1, 12)
        day = random.randint(1, 28)

        # Malaysian state birth place codes (realistic)
        state_codes = {
            "Johor": [1, 21, 22, 24],
            "Kedah": [2, 25, 26, 27],
            "Kelantan": [3, 28, 29],
            "Malacca": [4, 30],
            "Negeri Sembilan": [5, 31, 59],
            "Pahang": [6, 32, 33],
            "Penang": [7, 34, 35],
            "Perak": [8, 36, 37, 38, 39],
            "Perlis": [9, 40],
            "Sabah": [12, 47, 48, 49],
            "Sarawak": [13, 50, 51, 52, 53],
            "Selangor": [10, 41, 42, 43, 44],
            "Terengganu": [11, 45, 46],
            "Kuala Lumpur": [14, 54, 55, 56, 57],
            "Labuan": [15, 58],
            "Putrajaya": [16],
        }

        # Random state and corresponding place code
        state = random.choice(list(state_codes.keys()))
        place_code = random.choice(state_codes[state])

        # Last 4 digits (first 3 are sequence, last is check digit)
        sequence = random.randint(100, 999)
        check_digit = random.randint(0, 9)

        return f"{year_code:02d}{month:02d}{day:02d}{place_code:02d}{sequence}{check_digit}"

    def _generate_malaysian_phone(self):
        """Generate realistic Malaysian phone number format"""
        # 80% mobile, 20% landline (realistic distribution)
        if random.random() < 0.8:
            # Mobile numbers (more realistic prefixes)
            mobile_prefixes = [
                "010",
                "011",
                "012",
                "013",
                "014",
                "015",
                "016",
                "017",
                "018",
                "019",
            ]
            prefix = random.choice(mobile_prefixes)
            number = f"{prefix}-{random.randint(1000000, 9999999)}"
        else:
            # Landline numbers by state
            landline_prefixes = {
                "Kuala Lumpur": "03",
                "Selangor": "03",
                "Johor": "07",
                "Penang": "04",
                "Perak": "05",
                "Kedah": "04",
                "Kelantan": "09",
                "Terengganu": "09",
                "Pahang": "09",
                "Negeri Sembilan": "06",
                "Malacca": "06",
                "Sabah": "088",
                "Sarawak": "082",
                "Perlis": "04",
                "Labuan": "087",
                "Putrajaya": "03",
            }
            state = random.choice(list(landline_prefixes.keys()))
            prefix = landline_prefixes[state]
            if len(prefix) == 2:
                number = f"{prefix}-{random.randint(1000000, 9999999)}"
            else:  # 3-digit prefix for East Malaysia
                number = f"{prefix}-{random.randint(100000, 999999)}"

        return number

    def _generate_last_active_date(self, status):
        """Generate last active date based on status"""
        if status == "Active":
            return self.fake.date_between(start_date="-30d", end_date="today")
        elif status == "On Leave":
            return self.fake.date_between(start_date="-90d", end_date="-30d")
        elif status == "Training":
            return self.fake.date_between(start_date="-7d", end_date="today")
        else:  # Inactive
            return self.fake.date_between(start_date="-365d", end_date="-90d")

    def _get_volunteers_by_complexity(self, complexity):
        """Determine volunteer allocation based on operation complexity"""
        if complexity == "Low":
            return random.randint(5, 20)
        elif complexity == "Medium":
            return random.randint(20, 50)
        elif complexity == "High":
            return random.randint(50, 100)
        else:  # Critical
            return random.randint(100, 200)

    def _get_time_category(self, hour):
        """Categorize time of day"""
        if 6 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 18:
            return "Afternoon"
        elif 18 <= hour < 22:
            return "Evening"
        else:
            return "Night"

    def _generate_malaysian_name(self, gender, ethnicity):
        """Generate Malaysian names based on ethnicity and gender"""
        if ethnicity == "Malay":
            if gender == "Male":
                first_name = random.choice(self.malay_male_names)
                last_name = (
                    random.choice(["bin", "b."])
                    + " "
                    + random.choice(self.malay_male_names)
                )
            else:
                first_name = random.choice(self.malay_female_names)
                last_name = (
                    random.choice(["binti", "bt."])
                    + " "
                    + random.choice(self.malay_male_names)
                )
            return f"{first_name} {last_name}"

        elif ethnicity == "Chinese":
            if gender == "Male":
                name = random.choice(self.chinese_male_names)
            else:
                name = random.choice(self.chinese_female_names)
            family_name = random.choice(
                ["Lim", "Tan", "Lee", "Ong", "Ng", "Wong", "Teh", "Chan"]
            )
            return f"{family_name} {name}"

        elif ethnicity == "Indian":
            if gender == "Male":
                first_name = random.choice(self.indian_male_names)
                last_name = (
                    random.choice(["s/o", "a/l"])
                    + " "
                    + random.choice(self.indian_male_names)
                )
            else:
                first_name = random.choice(self.indian_female_names)
                last_name = (
                    random.choice(["d/o", "a/p"])
                    + " "
                    + random.choice(self.indian_male_names)
                )
            return f"{first_name} {last_name}"

        else:  # Indigenous or Others
            # Use faker for other ethnicities
            return self.fake.name()

    def _generate_realistic_email(self, full_name):
        """Generate realistic email addresses based on name"""
        # Clean the name for email generation
        name_parts = (
            full_name.lower()
            .replace(" bin ", " ")
            .replace(" binti ", " ")
            .replace(" bt. ", " ")
            .replace(" b. ", " ")
            .replace(" s/o ", " ")
            .replace(" a/l ", " ")
            .replace(" d/o ", " ")
            .replace(" a/p ", " ")
            .split()
        )

        # Common email patterns
        patterns = [
            f"{name_parts[0]}.{name_parts[-1]}",
            f"{name_parts[0]}{name_parts[-1]}",
            f"{name_parts[0]}.{name_parts[-1]}{random.randint(1, 99)}",
            f"{name_parts[0][0]}.{name_parts[-1]}",
            f"{name_parts[0]}.{name_parts[-1][0]}",
        ]

        # Malaysian email providers
        providers = [
            "gmail.com",
            "hotmail.com",
            "yahoo.com",
            "outlook.com",
            "rela.gov.my",
        ]
        weights = [40, 20, 15, 10, 15]  # rela.gov.my for official use

        pattern = random.choice(patterns)
        provider = random.choices(providers, weights=weights, k=1)[0]

        # Clean pattern (remove special characters, limit length)
        pattern = "".join(c for c in pattern if c.isalnum() or c == ".")
        pattern = pattern[:20]  # Limit length

        return f"{pattern}@{provider}"

    def _generate_realistic_training(self, years_service, rank):
        """Generate realistic training count based on service years and rank"""
        base_training = max(
            1, int(years_service * 1.5)
        )  # 1.5 training per year on average

        # Rank multiplier (higher ranks tend to have more training)
        rank_multiplier = {
            "Volunteer": 1.0,
            "Senior Volunteer": 1.2,
            "Team Leader": 1.5,
            "Squad Leader": 1.8,
            "Platoon Commander": 2.2,
            "Company Commander": 2.5,
            "Battalion Commander": 3.0,
            "District Commander": 3.5,
            "State Commander": 4.0,
        }

        multiplier = rank_multiplier.get(rank, 1.0)
        training_count = int(base_training * multiplier * random.uniform(0.8, 1.2))

        return max(1, min(training_count, 50))  # Reasonable limits

    def _generate_realistic_operations_count(self, years_service, status):
        """Generate realistic operations participation count"""
        if status == "Inactive":
            return random.randint(0, max(1, int(years_service * 2)))
        elif status == "On Leave":
            return random.randint(0, max(1, int(years_service * 4)))
        elif status == "Training":
            return random.randint(0, max(1, int(years_service * 3)))
        else:  # Active
            base_ops = int(
                years_service * 6
            )  # 6 operations per year average for active members
            return max(0, int(base_ops * random.uniform(0.5, 1.5)))

    def _generate_realistic_commendations(self, years_service, rank):
        """Generate realistic commendations based on service and rank"""
        # Base chance increases with service years
        base_chance = min(years_service * 0.05, 0.3)  # Max 30% chance

        # Rank bonus
        rank_bonus = {
            "Volunteer": 0,
            "Senior Volunteer": 0.02,
            "Team Leader": 0.05,
            "Squad Leader": 0.08,
            "Platoon Commander": 0.12,
            "Company Commander": 0.15,
            "Battalion Commander": 0.20,
            "District Commander": 0.25,
            "State Commander": 0.30,
        }

        final_chance = base_chance + rank_bonus.get(rank, 0)

        # Generate commendations
        commendations = 0
        for year in range(int(years_service)):
            if random.random() < final_chance:
                commendations += 1

        return min(commendations, 10)  # Reasonable maximum

    def generate_all_data(
        self, members_count=50000, operations_count=5000, assignments_count=20000
    ):
        """Generate all datasets and save to files"""
        import os
        import json
        from datetime import datetime

        print("🔄 Generating complete RELA Malaysia Analytics dataset...")

        # Generate all data
        members_df = self.generate_members_data(members_count)
        operations_df = self.generate_operations_data(operations_count)
        assignments_df = self.generate_assignments_data(members_df, assignments_count)

        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Save CSV files
        members_df.to_csv("data/members.csv", index=False)
        operations_df.to_csv("data/operations.csv", index=False)
        assignments_df.to_csv("data/assignments.csv", index=False)

        # Save metadata
        metadata = {
            "generated_date": datetime.now().isoformat(),
            "members_count": len(members_df),
            "operations_count": len(operations_df),
            "assignments_count": len(assignments_df),
            "version": "2.0",
        }

        with open("data/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✅ Complete dataset generated and saved!")
        print(f"📊 Members: {len(members_df):,}")
        print(f"🚀 Operations: {len(operations_df):,}")
        print(f"📋 Assignments: {len(assignments_df):,}")

        return members_df, operations_df, assignments_df


if __name__ == "__main__":
    # Allow running data generation directly
    dg = DataGenerator()
    dg.generate_all_data()
