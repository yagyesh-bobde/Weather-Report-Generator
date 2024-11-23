import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Weather API endpoints
WEATHER_BASE_URL = "http://api.weatherapi.com/v1"
CURRENT_WEATHER_ENDPOINT = f"{WEATHER_BASE_URL}/current.json"
FORECAST_WEATHER_ENDPOINT = f"{WEATHER_BASE_URL}/forecast.json"

# Default values
DEFAULT_FORECAST_DAYS = 5

# LLM Configuration
TEMPERATURE = 0.7
MAX_TOKENS = 1000

# Import these at the top of llm_analyzer.py
from datetime import datetime
from config.config import GROQ_API_KEY, TEMPERATURE