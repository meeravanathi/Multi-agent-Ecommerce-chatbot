from groq_llm import GroqLLM
from tools.weather_tools import WeatherTools
import json

class WeatherAgent:
    def __init__(self):
        self.llm = GroqLLM()
        self.tools = WeatherTools()
        self.name = "Weather Agent"
        self.description = "Provides current weather information and forecasts"
    
    def process(self, query: str, context: dict = None) -> dict:
        """Process weather-related queries"""
        
        analysis_prompt = f"""
        Analyze this weather query and extract information:
        Query: "{query}"
        
        Determine:
        1. Location mentioned
        2. Type of weather request (current weather or forecast)
        3. Number of days for forecast (if applicable)
        
        Common patterns:
        - "weather in [location]" = current weather
        - "forecast for [location]" = weather forecast
        - "[number] day forecast" = specific forecast days
        
        Respond in JSON format:
        {{
            "location": "extracted_location_or_null",
            "request_type": "current_weather|forecast",  
            "forecast_days": 5,
            "confidence": 0.95
        }}
        """
        
        analysis_result = self.llm._call(analysis_prompt)
        
        try:
            analysis = json.loads(analysis_result)
            location = analysis.get("location")
            request_type = analysis.get("request_type", "current_weather")
            forecast_days = analysis.get("forecast_days", 5)
            
            if location:
                if request_type == "forecast":
                    result = self.tools.get_weather_forecast(location, forecast_days)
                    return self._format_forecast_response(query, result, location)
                else:
                    result = self.tools.get_weather(location)
                    return self._format_weather_response(query, result, location)
            else:
                return self._ask_for_location(query)
                
        except json.JSONDecodeError:
            return self._ask_for_location(query)
    
    def _format_weather_response(self, query: str, result: dict, location: str) -> dict:
        """Format the current weather response"""
        
        if result.get("success"):
            weather_info = []
            weather_info.append(f"📍 Location: {result['location']}")
            
            if result.get("country"):
                weather_info[-1] += f", {result['country']}"
            
            weather_info.extend([
                f"🌡️ Temperature: {result['temperature']}°C",
                f"🌤️ Condition: {result['condition']}"
            ])
            
            if result.get("feels_like"):
                weather_info.append(f"🔥 Feels like: {result['feels_like']}°C")
            
            weather_info.append(f"💧 Humidity: {result['humidity']}%")
            
            if result.get("pressure"):
                weather_info.append(f"🏔️ Pressure: {result['pressure']} hPa")
            
            if result.get("wind_speed"):
                weather_info.append(f"💨 Wind Speed: {result['wind_speed']} m/s")
            
            if result.get("visibility"):
                weather_info.append(f"👁️ Visibility: {result['visibility']} km")
            
            response = f"Here's the current weather for {result['location']}:\n\n" + "\n".join(weather_info)
            
            if result.get("note"):
                response += f"\n\n⚠️ {result['note']}"
            
            response += "\n\nWould you like a weather forecast or weather for another location?"
            
        else:
            response = result.get("message", f"I couldn't find weather information for {location}.")
            response += "\n\nPlease try again with a different location or check the spelling."
        
        return {
            "agent": self.name,
            "response": response,
            "data": result,
            "success": result.get("success", True)
        }
    
    def _format_forecast_response(self, query: str, result: dict, location: str) -> dict:
        """Format the weather forecast response"""
        
        if result.get("success"):
            response_parts = []
            response_parts.append(f"Here's the weather forecast for {result['location']}, {result.get('country', '')}:\n")
            
            for i, forecast in enumerate(result.get("forecasts", []), 1):
                day_info = [
                    f"📅 Day {i} ({forecast['date']}):",
                    f"   🌡️ Temperature: {forecast['temperature_min']}°C - {forecast['temperature_max']}°C",
                    f"   🌤️ Condition: {forecast['condition']}",
                    f"   💧 Humidity: {forecast['humidity']}%"
                ]
                
                if forecast.get("wind_speed"):
                    day_info.append(f"   💨 Wind: {forecast['wind_speed']} m/s")
                
                response_parts.extend(day_info)
                response_parts.append("")  # Empty line between days
            
            response = "\n".join(response_parts)
            response += "Need weather for another location or different dates?"
            
        else:
            response = result.get("message", f"I couldn't get forecast information for {location}.")
        
        return {
            "agent": self.name,
            "response": response,
            "data": result,
            "success": result.get("success", True)
        }
    
    def _ask_for_location(self, query: str) -> dict:
        """Ask user to specify location"""
        response = """I'd be happy to provide weather information! Please specify which location you'd like weather for.

I can provide:
🌤️ Current weather conditions
📅 Weather forecasts (up to 5 days)

Examples:
• "Weather in London"
• "New York weather forecast"  
• "5 day forecast for Tokyo"

Which location would you like weather information for?"""
        
        return {
            "agent": self.name,
            "response": response,
            "data": {},
            "success": True
        }
