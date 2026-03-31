"""
Weather forecast service for 7-day rainfall prediction.
Integrates with OpenWeatherMap API for real-time forecast data.
"""

import os
import requests
from typing import Optional
from datetime import datetime, timedelta
from services.flood_prediction import WeatherForecast


class WeatherForecastService:
    """Service for fetching 7-day weather forecasts"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
    
    def __init__(self):
        """Initialize with API key from environment"""
        self.api_key = os.environ.get('OPENWEATHER_API_KEY', '')
    
    def get_7day_forecast(self, city: str, country_code: str = "IN") -> list[WeatherForecast]:
        """
        Fetch 7-day weather forecast for a city.
        
        Args:
            city: City name
            country_code: Country code (default: IN for India)
            
        Returns:
            List of WeatherForecast objects for next 7 days
        """
        if not self.api_key:
            # Return mock data if no API key
            return self._generate_mock_forecast()
        
        try:
            params = {
                'q': f"{city},{country_code}",
                'appid': self.api_key,
                'units': 'metric',
                'cnt': 56  # 7 days * 8 (3-hour intervals)
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_forecast_data(data)
            else:
                return self._generate_mock_forecast()
                
        except Exception:
            return self._generate_mock_forecast()
    
    def _parse_forecast_data(self, data: dict) -> list[WeatherForecast]:
        """Parse OpenWeatherMap API response into daily forecasts"""
        daily_data = {}
        
        for item in data.get('list', []):
            date_str = item['dt_txt'].split(' ')[0]
            
            if date_str not in daily_data:
                daily_data[date_str] = {
                    'rainfall': 0.0,
                    'temp_sum': 0.0,
                    'humidity_sum': 0.0,
                    'count': 0
                }
            
            # Accumulate rainfall (mm)
            rain_3h = item.get('rain', {}).get('3h', 0.0)
            daily_data[date_str]['rainfall'] += rain_3h
            
            # Average temperature and humidity
            daily_data[date_str]['temp_sum'] += item['main']['temp']
            daily_data[date_str]['humidity_sum'] += item['main']['humidity']
            daily_data[date_str]['count'] += 1
        
        # Convert to WeatherForecast objects
        forecasts = []
        for date_str, values in sorted(daily_data.items())[:7]:
            count = values['count']
            forecasts.append(WeatherForecast(
                date=date_str,
                rainfall_mm=round(values['rainfall'], 2),
                temperature=round(values['temp_sum'] / count, 1),
                humidity=round(values['humidity_sum'] / count, 1)
            ))
        
        return forecasts
    
    def _generate_mock_forecast(self, scenario: str = "normal") -> list[WeatherForecast]:
        """Generate mock forecast data for testing/fallback with scenario support"""
        import random
        
        forecasts = []
        base_date = datetime.now()
        
        for i in range(7):
            date = base_date + timedelta(days=i)
            
            # Scenario-based rainfall generation
            if scenario == "heavy_rain":
                # Flood scenario - heavy rainfall
                rainfall = random.uniform(40, 80)
            elif scenario == "drought":
                # Drought scenario - minimal rainfall
                rainfall = random.uniform(0, 3)
            else:
                # Normal scenario - varied rainfall
                rainfall = random.uniform(0, 30) if random.random() > 0.3 else 0
            
            forecasts.append(WeatherForecast(
                date=date.strftime('%Y-%m-%d'),
                rainfall_mm=round(rainfall, 2),
                temperature=round(random.uniform(20, 35), 1),
                humidity=round(random.uniform(40, 90), 1)
            ))
        
        return forecasts
    
    def get_simulated_forecast(self, scenario: str = "normal") -> list[WeatherForecast]:
        """Get simulated forecast for demo scenarios"""
        return self._generate_mock_forecast(scenario)


# Singleton instance
weather_forecast_service = WeatherForecastService()
