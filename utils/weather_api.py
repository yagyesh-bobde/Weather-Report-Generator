import requests
from typing import Dict, Any
from config.config import (
    WEATHER_API_KEY,
    CURRENT_WEATHER_ENDPOINT,
    FORECAST_WEATHER_ENDPOINT,
    DEFAULT_FORECAST_DAYS
)

class WeatherAPI:
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """
        Get current weather data for a specific location
        """
        params = {
            'key': self.api_key,
            'q': location,
            'aqi': 'no'
        }
        
        try:
            response = requests.get(CURRENT_WEATHER_ENDPOINT, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error fetching current weather: {str(e)}")
            
    def get_weather_forecast(self, location: str, days: int = DEFAULT_FORECAST_DAYS) -> Dict[str, Any]:
        """
        Get weather forecast for a specific location
        """
        params = {
            'key': self.api_key,
            'q': location,
            'days': days,
            'aqi': 'no',
            'alerts': 'no'
        }
        
        try:
            response = requests.get(FORECAST_WEATHER_ENDPOINT, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error fetching weather forecast: {str(e)}")
            
    def get_combined_weather_data(self, location: str) -> Dict[str, Any]:
        """
        Get both current weather and forecast data
        """
        forecast_data = self.get_weather_forecast(location)
        return {
            'current': forecast_data['current'],
            'location': forecast_data['location'],
            'forecast': forecast_data['forecast']
        }