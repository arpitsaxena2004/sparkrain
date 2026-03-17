# 🌧️ JalNidhi AI - Rainwater Harvesting System

A comprehensive Django-based AI system for rainwater harvesting calculations, cost estimation, and water conservation analytics.

## 🚀 Features

- **Smart Calculator**: ML-powered suitability and cost predictions
- **AI Chatbot**: Intelligent assistant for rainwater harvesting queries
- **Analytics Dashboard**: Visual insights and data analysis
- **Water Savings Tracker**: Monitor your conservation impact
- **Weather Integration**: Real-time weather data
- **District Coverage**: 600+ Indian districts with rainfall data

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Engineer-Bhai/RoofTop_Rainwater_Harvesting.git
cd RoofTop_Rainwater_Harvesting
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file and add your API keys:
# - Get GROQ API key from https://console.groq.com/
# - Add your Django secret key
```

### 4. Database Setup
```bash
python manage.py migrate
```

### 5. Run the Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to access the application.

## 🔑 API Keys Required

### GROQ API Key (for AI Chatbot)
1. Visit [https://console.groq.com/](https://console.groq.com/)
2. Create a free account
3. Generate an API key
4. Add it to your `.env` file as `GROQ_API_KEY=your_key_here`

**Note**: Without the GROQ API key, the chatbot will use fallback responses with limited functionality.

## 📁 Project Structure

```
├── core/                   # Main Django app
├── services/              # Business logic and APIs
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── ml_models/            # Pre-trained ML models
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── manage.py           # Django management script
```

## 🤖 Chatbot Features

- **Definition Queries**: Ask "define rainwater harvesting"
- **Cost Information**: Get pricing estimates
- **Rainfall Data**: District-specific weather information
- **Technical Help**: Calculator guidance and specifications
- **Environmental Impact**: Benefits and statistics

## 🌍 Deployment

For production deployment:
1. Set `DEBUG=False` in `.env`
2. Configure proper `SECRET_KEY`
3. Set up environment variables on your hosting platform
4. Use a production WSGI server (gunicorn included)

## 📊 ML Models

The system includes pre-trained models for:
- **Suitability Prediction**: Based on rainfall, soil type, and location
- **Cost Estimation**: Accurate pricing for different system sizes
- **Water Potential Calculation**: Annual collection estimates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the chatbot for common queries
- Review the documentation

---

**Made with 💧 for water conservation in India**