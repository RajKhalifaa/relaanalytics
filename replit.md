# RELA Malaysia Analytics Dashboard

## Overview

This is a Streamlit-based analytics dashboard for RELA Malaysia (People's Volunteer Corps), designed to provide comprehensive insights into member management, operations tracking, and assignment analytics. The application uses synthetic data generation to simulate real-world scenarios for demonstration and testing purposes.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Visualization**: Plotly for interactive charts and graphs
- **Styling**: Custom CSS for government-style appearance with Malaysian branding
- **Layout**: Wide layout with expandable sidebar for filtering and navigation

### Backend Architecture
- **Data Processing**: Pandas for data manipulation and analysis
- **Synthetic Data**: Faker library with Malaysian locale for realistic test data
- **Analytics Engine**: Custom Analytics class for data filtering and processing
- **Dashboard Engine**: Modular Dashboard class for visualization components

### Data Architecture
- **Data Storage**: In-memory DataFrames (no persistent database)
- **Data Generation**: Real-time synthetic data generation with Malaysian context
- **Data Models**: Three main entities - Members, Operations, and Assignments

## Key Components

### 1. Data Generator (`data_generator.py`)
- **Purpose**: Generates realistic Malaysian RELA data for testing and demonstration
- **Features**: 
  - Malaysian states and districts mapping
  - RELA-specific operation types and ranks
  - Realistic member profiles with Malaysian names and locations
  - Time-based operation and assignment data

### 2. Analytics Engine (`analytics.py`)
- **Purpose**: Provides data filtering and analysis capabilities
- **Features**:
  - Multi-dimensional filtering (states, status, date ranges)
  - Cross-dataset filtering maintaining data relationships
  - Scalable filtering architecture for future enhancements

### 3. Dashboard System (`dashboard.py`)
- **Purpose**: Renders interactive visualizations and metrics
- **Features**:
  - Executive overview with KPIs
  - Interactive charts using Plotly
  - Government-style color scheme and branding
  - Modular component architecture

### 4. Main Application (`app.py`)
- **Purpose**: Entry point and overall application orchestration
- **Features**:
  - Streamlit configuration and page setup
  - Custom CSS styling for professional appearance
  - Component integration and routing

## Data Flow

1. **Data Generation**: DataGenerator creates synthetic Malaysian RELA data
2. **Data Processing**: Analytics engine filters and processes data based on user selections
3. **Visualization**: Dashboard components render processed data into interactive charts
4. **User Interaction**: Streamlit handles user inputs and triggers data updates

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Plotly**: Interactive visualizations

### Data Generation
- **Faker**: Synthetic data generation with Malaysian locale support

### Utility Libraries
- **datetime**: Date and time handling
- **json**: Data serialization (minimal usage)
- **random**: Random number generation for synthetic data

## Deployment Strategy

### Current Setup
- **Platform**: Replit-ready Python application
- **Dependencies**: All dependencies installable via pip
- **Runtime**: Pure Python with no external database requirements

### Scalability Considerations
- **Database Integration**: Architecture supports future database integration
- **Authentication**: Modular design allows for future auth implementation
- **Performance**: In-memory processing suitable for demonstration, can be enhanced for production

### Malaysian Context
- **Localization**: Malaysian states, districts, and cultural context
- **Government Styling**: Professional appearance suitable for government use
- **RELA-Specific**: Tailored for Malaysian People's Volunteer Corps operations

## Recent Changes

### July 21, 2025 - Data Persistence & Predictive Analytics System
- **Implemented Data Persistence**: Added comprehensive data persistence system to save/load generated datasets from CSV files
- **Performance Optimization**: Eliminated need to regenerate 75K+ records every session, dramatically improving load times
- **Data Management Controls**: Added "Generate New" and "Delete Data" buttons with metadata tracking
- **Automatic Data Loading**: System automatically loads saved data on startup if available
- **Bilingual Data Controls**: All data management interfaces support English/Bahasa Malaysia switching
- **File Organization**: Created structured data directory with metadata tracking (generation date, record counts)
- **Persistent State Management**: Data persists across sessions and browser refreshes for better user experience
- **Fixed Performance Trends**: Corrected declining performance issue by implementing temporal improvement factors and seasonal variations
- **Machine Learning Integration**: Added comprehensive predictive analytics system with scikit-learn
- **Performance Prediction Model**: Trained Random Forest/Gradient Boosting models to predict member performance based on demographics, experience, and historical data
- **Operations Forecasting**: Implemented 6-month operations prediction model with state-wise and type-wise breakdowns
- **Model Persistence**: ML models save/load automatically with metadata tracking and performance metrics
- **Bilingual ML Interface**: All predictive analytics features support both English and Bahasa Malaysia

### July 17, 2025 - Enhanced Data Realism
- **Fixed Faker Locale Issue**: Resolved Malaysian locale configuration error by using supported English locale
- **Authentic Malaysian Names**: Added comprehensive Malaysian name generation by ethnicity (Malay, Chinese, Indian)
- **Realistic IC Numbers**: Implemented authentic Malaysian IC number format with proper state birth codes
- **Smart Phone Numbers**: Enhanced phone generation with 80% mobile/20% landline distribution and proper area codes
- **Intelligent Performance Correlation**: Performance scores now correlate with member experience, rank, and attendance
- **Weather-based Success Rates**: Operation success rates affected by weather conditions and complexity
- **Email Generation**: Created realistic email patterns based on actual names with Malaysian providers
- **Training & Commendations**: Made training counts and commendations realistic based on years of service and rank
- **Response Rate Logic**: Volunteer response rates now correlate with operation urgency and timing

### Data Quality Improvements
- **Optimized Dataset Size**: Reduced to 50K members, 5K operations, 20K assignments for faster loading
- **Correlation Patterns**: Added logical relationships between age, experience, rank, performance, and attendance
- **Malaysian Context**: Enhanced all data fields to reflect authentic Malaysian organizational structure

The application is designed to be easily extensible, with clear separation of concerns between data generation, analysis, and visualization components. The enhanced synthetic data approach now provides highly realistic patterns without requiring real sensitive data.