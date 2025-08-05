# RELA Malaysia Analytics Dashboard 🇲🇾

A comprehensive bilingual analytics dashboard for the Malaysian People's Volunteer Corps (RELA), featuring AI-powered predictive analytics and real-time operational insights.

![RELA Analytics](assets/rela_logo.jpg)

## 🌟 Features

- **📊 Real-time Analytics**: Live operational insights and KPIs
- **🤖 Machine Learning**: Predictive analytics for performance forecasting
- **💬 AI Chatbot**: Natural language query interface for instant insights
- **🌐 Bilingual Support**: Complete English/Bahasa Malaysia interface
- **📈 Forecasting**: 3-24 month operational predictions
- **🗺️ Geographic Intelligence**: State and district-level analysis
- **👥 Member Management**: Comprehensive volunteer tracking
- **📋 Operations Tracking**: Success rates and resource optimization

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git (for cloning)
- Docker (optional, for containerized deployment)

### Local Development

1. **Clone the repository**:

   ```bash
   git clone https://github.com/RajKhalifaa/relaanalytics.git
   cd relaanalytics
   ```

2. **Set up environment variables**:

   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```bash
   streamlit run app.py
   ```

5. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:8501`

### Docker Deployment

1. **Build the Docker image**:

   ```bash
   docker build -t rela-analytics .
   ```

2. **Run the container**:

   ```bash
   docker run -d -p 80:8501 rela-analytics
   ```

3. **Access the dashboard**:
   Open your browser and navigate to `http://localhost`

### Production Deployment

For production deployment with Docker Compose:

```bash
docker-compose up -d
```

## 📁 Project Structure

```
RelaAnalytics/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Container configuration
├── docker-compose.yml             # Docker orchestration
├── README.md                       # Project documentation
├── CHATBOT_DOCUMENTATION.md        # Chatbot feature documentation
├── test_chatbot.py                 # Chatbot test suite
├── .gitignore                      # Git ignore rules
├── assets/                         # Static assets
│   └── rela_logo.jpg
├── config/                         # Configuration files
│   ├── __init__.py
│   └── settings.py
├── src/                           # Source code
│   ├── core/                      # Core application modules
│   │   ├── analytics.py           # Analytics engine
│   │   ├── chatbot.py             # AI-powered chatbot interface
│   │   ├── dashboard.py           # Dashboard components
│   │   ├── forecasting_engine.py  # ML forecasting
│   │   ├── ml_model_manager.py    # Model management
│   │   └── predictive_analytics.py # Predictive features
│   └── utils/                     # Utility modules
│       ├── data_generator.py      # Data generation
│       ├── data_persistence.py    # Data storage
│       └── translations.py        # Bilingual support
├── scripts/                       # Development scripts
│   ├── build-push-simple.bat     # Docker build script
│   ├── deploy.sh                  # Deployment script
│   └── run.bat                    # Local run script
└── tests/                         # Test files
    └── test_translations.py       # Translation tests
```

## 🔧 Technology Stack

- **Frontend**: Streamlit Web Framework
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly Interactive Charts
- **Machine Learning**: Scikit-learn
- **Language Support**: Custom translation system
- **Containerization**: Docker & Docker Compose

## 📊 Dashboard Features

### Core Modules

- **Member Analytics**: Demographics, performance tracking, rankings
- **Operations Analysis**: Success rates, resource utilization, efficiency
- **Predictive Analytics**: ML-powered forecasting and predictions
- **Regional Intelligence**: Geographic insights across Malaysian states
- **Reporting System**: Comprehensive analytics with export capabilities
- **🤖 Analytics Chatbot**: Natural language query interface with AI insights

### AI/ML Capabilities

- **Performance Prediction**: Random Forest, Gradient Boosting models
- **Time Series Forecasting**: 3-24 month operational predictions
- **Risk Assessment**: Early intervention identification
- **Resource Optimization**: Data-driven allocation recommendations
- **Conversational AI**: Natural language processing for dashboard queries

## 🌍 Bilingual Support

- **English**: Complete interface and documentation
- **Bahasa Malaysia**: Full translation support
- **Dynamic Switching**: Real-time language toggle
- **Cultural Adaptation**: Malaysian context and terminology

## 🛡️ Data & Privacy

- **Synthetic Data**: All data is artificially generated for demonstration
- **Privacy Compliant**: No real personal information used
- **PDPA Standards**: Malaysian data protection compliance
- **Security**: Professional-grade security measures

## 🎨 Configuration

### Environment Variables

```bash
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
```

### Theme Customization

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f4e79"    # RELA Blue
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
```

## 📦 Development

### Scripts

- `scripts/run.bat` - Local development server
- `scripts/build-push-simple.bat` - Docker build and push
- `scripts/deploy.sh` - Production deployment

### Testing

```bash
python -m pytest tests/
```

### Data Generation

The system automatically generates sample data on first run. To manually regenerate:

```bash
python src/utils/data_generator.py
```

## 🚀 Production Deployment

### Docker Production

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Access at http://your-server
```

### Manual Production Setup

1. Clone repository on server
2. Install Python 3.11+ and dependencies
3. Configure reverse proxy (nginx/apache)
4. Set up systemd service for auto-restart
5. Configure SSL certificates

See `DEPLOYMENT_COMPLETE.md` for detailed production deployment guide.

## � Dependencies

Core requirements (see `requirements.txt` for complete list):

- `streamlit >= 1.47.0` - Web framework
- `pandas >= 2.3.1` - Data processing
- `plotly >= 6.2.0` - Interactive visualizations
- `scikit-learn >= 1.7.1` - Machine learning
- `numpy >= 2.3.1` - Numerical computing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **RELA Malaysia** - People's Volunteer Corps of Malaysia
- **Malaysian Government** - Support for civic technology initiatives
- **Open Source Community** - Various libraries and tools used

## 📧 Contact

For questions, support, or collaboration opportunities:

- **Project Repository**: [GitHub](https://github.com/yourusername/RelaAnalytics)
- **Issues**: [Report Issues](https://github.com/yourusername/RelaAnalytics/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/RelaAnalytics/wiki)

---

**Built with ❤️ for Malaysia** 🇲🇾
│ │ ├── dashboard.py # Dashboard components
│ │ ├── analytics.py # Analytics engine
│ │ ├── ml_model_manager.py
│ │ ├── forecasting_engine.py
│ │ └── predictive_analytics.py
│ └── utils/ # Utility modules
│ ├── data_generator.py
│ ├── data_persistence.py
│ └── translations.py
├── config/ # Configuration files
│ └── settings.py
├── data/ # Data files
├── models/ # ML models
├── assets/ # Static assets
├── app.py # Main application
├── requirements.txt # Python dependencies
├── Dockerfile # Docker configuration
├── docker-compose.yml # Docker Compose setup
├── deploy.sh # Deployment script
└── README.md # Documentation

```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is developed for RELA Malaysia. All rights reserved.

## 🏢 Credits

**Developed by**: Credence AI & Analytics
**For**: RELA Malaysia (Malaysian People's Volunteer Corps)
**Year**: 2025

## 📞 Support

For technical support and inquiries:

- 📧 Email: support@credenceai.com
- 📱 Issues: [GitHub Issues](https://github.com/yourusername/rela-analytics-dashboard/issues)

---

**🇲🇾 Serving Malaysia with Data-Driven Excellence**
```
