import requests
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class WeatherTools:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Fallback mock data if API key is not provided
        self.mock_weather_data = {
            "new york": {"temperature": 22, "condition": "sunny", "humidity": 45},
            "london": {"temperature": 15, "condition": "cloudy", "humidity": 70},
            "tokyo": {"temperature": 28, "condition": "rainy", "humidity": 80},
        }
    
    def get_weather(self, location: str) -> Dict[str, Any]:
        """Get weather information for a location using OpenWeatherMap API"""
        
        # If no API key, use mock data
        if not self.api_key:
            return self._get_mock_weather(location)
        
        try:
            # Prepare API request parameters
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'  # Use Celsius
            }
            
            # Make API request
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_weather_response(data)
            elif response.status_code == 404:
                return {
                    "success": False,
                    "message": f"Location '{location}' not found. Please check the spelling and try again."
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "Invalid API key. Please check your OpenWeatherMap API configuration."
                }
            else:
                return {
                    "success": False,
                    "message": f"Weather service error: {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Weather service timeout. Please try again later."
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "Unable to connect to weather service. Please check your internet connection."
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Weather service error: {str(e)}"
            }
    
    def _format_weather_response(self, data: Dict) -> Dict[str, Any]:
        """Format OpenWeatherMap API response"""
        try:
            return {
                "success": True,
                "location": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"]),
                "feels_like": round(data["main"]["feels_like"]),
                "condition": data["weather"][0]["description"].title(),
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "visibility": data.get("visibility", 0) / 1000 if data.get("visibility") else None,  # Convert to km
                "sunrise": data["sys"]["sunrise"],
                "sunset": data["sys"]["sunset"]
            }
        except KeyError as e:
            return {
                "success": False,
                "message": f"Error parsing weather data: missing field {str(e)}"
            }
    
    def _get_mock_weather(self, location: str) -> Dict[str, Any]:
        """Fallback to mock weather data when API key is not available"""
        location_lower = location.lower()
        
        if location_lower in self.mock_weather_data:
            weather = self.mock_weather_data[location_lower]
            return {
                "success": True,
                "location": location.title(),
                "temperature": weather["temperature"],
                "condition": weather["condition"].title(),
                "humidity": weather["humidity"],
                "note": "Using mock data - Please add OPENWEATHERMAP_API_KEY to .env for real weather data"
            }
        
        return {
            "success": False,
            "message": f"Weather data not available for {location}. Please add OPENWEATHERMAP_API_KEY to .env for real weather data."
        }
    
    def get_weather_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for multiple days (requires API key)"""
        
        if not self.api_key:
            return {
                "success": False,
                "message": "Weather forecast requires OpenWeatherMap API key. Please add OPENWEATHERMAP_API_KEY to .env"
            }
        
        try:
            forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': min(days * 8, 40) 
            }
            
            response = requests.get(forecast_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_forecast_response(data, days)
            else:
                return {
                    "success": False,
                    "message": f"Forecast service error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Forecast service error: {str(e)}"
            }
    
    def _format_forecast_response(self, data: Dict, days: int) -> Dict[str, Any]:
        """Format forecast API response"""
        try:
            forecasts = []
            current_date = None
            daily_data = {}
            
            for item in data["list"]:
                date = item["dt_txt"].split()[0] 
                if date != current_date:
                    if current_date and daily_data:
                        forecasts.append(daily_data)
                    
                    current_date = date
                    daily_data = {
                        "date": date,
                        "temperature_min": item["main"]["temp"],
                        "temperature_max": item["main"]["temp"],
                        "condition": item["weather"][0]["description"].title(),
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item.get("wind", {}).get("speed", 0)
                    }
                else:
                   
                    daily_data["temperature_min"] = min(daily_data["temperature_min"], item["main"]["temp"])
                    daily_data["temperature_max"] = max(daily_data["temperature_max"], item["main"]["temp"])
            
        
            if daily_data:
                forecasts.append(daily_data)
         
            for forecast in forecasts:
                forecast["temperature_min"] = round(forecast["temperature_min"])
                forecast["temperature_max"] = round(forecast["temperature_max"])
            
            return {
                "success": True,
                "location": data["city"]["name"],
                "country": data["city"]["country"],
                "forecasts": forecasts[:days]
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error parsing forecast data: {str(e)}"
            }
