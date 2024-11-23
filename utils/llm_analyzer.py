import groq
import json
from typing import Dict, Any
from datetime import datetime
from config.config import GROQ_API_KEY

class WeatherAnalyzer:
    def __init__(self):
        self.client = groq.Groq(api_key=GROQ_API_KEY)

    def _format_weather_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format and filter weather data to include only essential information
        """
        location = weather_data['location']
        current = weather_data['current']
        forecast = weather_data['forecast']['forecastday']

        # Format location data
        formatted_location = {
            'name': location['name'],
            'country': location['country'],
            'localtime': location['localtime']
        }

        # Format current weather
        formatted_current = {
            'temp_c': current['temp_c'],
            'condition': current['condition']['text'],
            'humidity': current['humidity'],
            'wind_kph': current['wind_kph'],
            'precip_mm': current['precip_mm']
        }

        # Format forecast data (only essential fields)
        formatted_forecast = []
        for day in forecast:
            formatted_forecast.append({
                'date': day['date'],
                'max_temp_c': day['day']['maxtemp_c'],
                'min_temp_c': day['day']['mintemp_c'],
                'condition': day['day']['condition']['text'],
                'chance_of_rain': day['day']['daily_chance_of_rain'],
                'totalprecip_mm': day['day']['totalprecip_mm'],
                'max_wind_kph': day['day']['maxwind_kph']
            })

        return {
            'location': formatted_location,
            'current': formatted_current,
            'forecast': formatted_forecast
        }

    def analyze_weather(self, weather_data: Dict[str, Any], activity: str) -> str:
        """
        Analyze weather data using LLM and provide recommendations
        """
        # Format and filter weather data
        formatted_data = self._format_weather_data(weather_data)
        
        # Create a concise prompt
        prompt = f"""Based on the following weather data, provide a brief analysis and recommendation for: {activity}

Location: {formatted_data['location']['name']}, {formatted_data['location']['country']}
Current Conditions:
- Temperature: {formatted_data['current']['temp_c']}°C
- Weather: {formatted_data['current']['condition']}
- Humidity: {formatted_data['current']['humidity']}%
- Wind Speed: {formatted_data['current']['wind_kph']} km/h
- Precipitation: {formatted_data['current']['precip_mm']} mm

Forecast Summary:"""

        # Add forecast data
        for day in formatted_data['forecast']:
            date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%A, %b %d')
            prompt += f"""
{date}:
- High/Low: {day['max_temp_c']}°C/{day['min_temp_c']}°C
- Condition: {day['condition']}
- Rain Chance: {day['chance_of_rain']}%
- Precipitation: {day['totalprecip_mm']} mm"""

        prompt += """

Please provide:
1. A brief analysis of current conditions
2. The best day and time for the planned activity
3. Any specific precautions or recommendations
4. Alternative suggestions if weather is unfavorable"""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-70b-versatile",
                temperature=0.7,
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error in LLM analysis: {str(e)}")
            
    def format_report(self, analysis: str, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analysis and weather data into a structured report
        """
        location = weather_data['location']['name']
        current_temp = weather_data['current']['temp_c']
        current_condition = weather_data['current']['condition']['text']
        
        report = {
            'location': location,
            'current_conditions': {
                'temperature': current_temp,
                'condition': current_condition,
                'humidity': weather_data['current']['humidity'],
                'wind_speed': weather_data['current']['wind_kph']
            },
            'analysis': analysis,
            'forecast_summary': weather_data['forecast']['forecastday']
        }
        
        return report