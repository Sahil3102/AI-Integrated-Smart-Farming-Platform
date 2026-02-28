"""
Weather Forecast Module
Provides weather forecasting functionality for agricultural planning.
"""
import random
from datetime import datetime, timedelta


class WeatherForecastModel:
    """
    Weather Forecast Model
    Provides weather forecasts for agricultural locations.
    """
    
    # Weather conditions
    WEATHER_CONDITIONS = [
        'Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain', 
        'Heavy Rain', 'Thunderstorm', 'Foggy', 'Clear'
    ]
    
    # Seasonal patterns for India
    SEASONAL_PATTERNS = {
        'summer': {
            'temp_range': (30, 45),
            'humidity_range': (30, 60),
            'rain_prob': 0.2,
            'conditions': ['Sunny', 'Clear', 'Partly Cloudy']
        },
        'monsoon': {
            'temp_range': (25, 35),
            'humidity_range': (70, 95),
            'rain_prob': 0.7,
            'conditions': ['Light Rain', 'Heavy Rain', 'Thunderstorm', 'Cloudy']
        },
        'post_monsoon': {
            'temp_range': (20, 30),
            'humidity_range': (50, 75),
            'rain_prob': 0.3,
            'conditions': ['Partly Cloudy', 'Sunny', 'Light Rain']
        },
        'winter': {
            'temp_range': (10, 25),
            'humidity_range': (40, 70),
            'rain_prob': 0.15,
            'conditions': ['Clear', 'Sunny', 'Foggy', 'Partly Cloudy']
        },
    }
    
    def __init__(self):
        pass
    
    def _get_current_season(self):
        """Get current season based on month"""
        month = datetime.now().month
        
        if month in [3, 4, 5]:
            return 'summer'
        elif month in [6, 7, 8, 9]:
            return 'monsoon'
        elif month in [10, 11]:
            return 'post_monsoon'
        else:
            return 'winter'
    
    def _generate_daily_forecast(self, date, location, base_temp=None):
        """Generate forecast for a single day"""
        season = self._get_current_season()
        pattern = self.SEASONAL_PATTERNS[season]
        
        # Generate temperature
        if base_temp is None:
            temp_min = random.randint(pattern['temp_range'][0], pattern['temp_range'][1] - 5)
        else:
            # Add some variation to base temperature
            variation = random.randint(-3, 3)
            temp_min = base_temp + variation
            temp_min = max(pattern['temp_range'][0], min(pattern['temp_range'][1] - 5, temp_min))
        
        temp_max = temp_min + random.randint(5, 12)
        
        # Generate humidity
        humidity = random.randint(pattern['humidity_range'][0], pattern['humidity_range'][1])
        
        # Determine weather condition
        rainy_choices = [
            c for c in pattern["conditions"] if ("Rain" in c) or ("Thunderstorm" in c)
        ]
        dry_choices = [
            c for c in pattern["conditions"] if ("Rain" not in c) and ("Thunderstorm" not in c)
        ]

        # Fallbacks: some seasons (e.g. summer) have rain_prob > 0 but no rainy conditions listed.
        if not rainy_choices:
            rainy_choices = [c for c in self.WEATHER_CONDITIONS if ("Rain" in c) or ("Thunderstorm" in c)]
        if not dry_choices:
            dry_choices = [c for c in self.WEATHER_CONDITIONS if ("Rain" not in c) and ("Thunderstorm" not in c)]

        # Final guard: should never be empty, but keep it safe.
        if not rainy_choices:
            rainy_choices = ["Light Rain"]
        if not dry_choices:
            dry_choices = ["Partly Cloudy"]

        if random.random() < pattern['rain_prob']:
            condition = random.choice(rainy_choices)
            rain_prob = random.randint(60, 95)
            rain_amount = random.uniform(5, 50) if 'Heavy' in condition else random.uniform(0, 15)
        else:
            condition = random.choice(dry_choices)
            rain_prob = random.randint(0, 30)
            rain_amount = 0
        
        # Generate wind speed
        wind_speed = random.uniform(5, 25)
        
        # Generate UV index
        if condition in ['Sunny', 'Clear']:
            uv_index = random.uniform(6, 11)
        elif condition in ['Partly Cloudy']:
            uv_index = random.uniform(3, 6)
        else:
            uv_index = random.uniform(0, 3)
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'day_name': date.strftime('%A'),
            'temperature_max': round(temp_max, 1),
            'temperature_min': round(temp_min, 1),
            'humidity': humidity,
            'rainfall_probability': rain_prob,
            'rainfall_amount': round(rain_amount, 1),
            'weather_condition': condition,
            'wind_speed': round(wind_speed, 1),
            'uv_index': round(uv_index, 1),
        }
    
    def get_forecast(self, location, days=7):
        """
        Get weather forecast for a location
        
        Args:
            location: Location name
            days: Number of days to forecast (default 7)
            
        Returns:
            Dictionary with forecast data
        """
        forecasts = []
        base_date = datetime.now()
        
        # Generate base temperature based on season
        season = self._get_current_season()
        pattern = self.SEASONAL_PATTERNS[season]
        base_temp = random.randint(pattern['temp_range'][0], pattern['temp_range'][1] - 5)
        
        for i in range(days):
            forecast_date = base_date + timedelta(days=i)
            forecast = self._generate_daily_forecast(forecast_date, location, base_temp)
            forecasts.append(forecast)
        
        # Calculate summary statistics
        avg_temp_max = sum(f['temperature_max'] for f in forecasts) / len(forecasts)
        avg_temp_min = sum(f['temperature_min'] for f in forecasts) / len(forecasts)
        avg_humidity = sum(f['humidity'] for f in forecasts) / len(forecasts)
        total_rainfall = sum(f['rainfall_amount'] for f in forecasts)
        
        # Determine overall trend
        rain_days = sum(1 for f in forecasts if f['rainfall_amount'] > 0)
        if rain_days >= days * 0.5:
            overall_trend = 'Rainy period expected'
        elif avg_temp_max > 35:
            overall_trend = 'Hot and dry conditions'
        elif avg_temp_max < 20:
            overall_trend = 'Cool weather expected'
        else:
            overall_trend = 'Moderate conditions'
        
        return {
            'location': location,
            'forecast_period': f"{days} days",
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overall_trend': overall_trend,
            'summary': {
                'avg_temperature_max': round(avg_temp_max, 1),
                'avg_temperature_min': round(avg_temp_min, 1),
                'avg_humidity': round(avg_humidity, 1),
                'total_rainfall': round(total_rainfall, 1),
                'rainy_days': rain_days,
            },
            'daily_forecasts': forecasts,
            'agricultural_advice': self._get_agricultural_advice(forecasts),
        }
    
    def _get_agricultural_advice(self, forecasts):
        """Generate agricultural advice based on forecast"""
        advice = []
        
        # Check for rain
        rain_forecasts = [f for f in forecasts if f['rainfall_amount'] > 10]
        if rain_forecasts:
            advice.append("Heavy rainfall expected. Avoid spraying pesticides and fertilizers.")
            advice.append("Ensure proper drainage in fields to prevent waterlogging.")
        
        # Check for high temperature
        hot_days = [f for f in forecasts if f['temperature_max'] > 40]
        if hot_days:
            advice.append("High temperatures expected. Increase irrigation frequency.")
            advice.append("Consider mulching to conserve soil moisture.")
        
        # Check for low humidity
        dry_days = [f for f in forecasts if f['humidity'] < 40]
        if dry_days:
            advice.append("Low humidity conditions. Monitor for pest infestations.")
        
        # Check for UV index
        high_uv_days = [f for f in forecasts if f['uv_index'] > 8]
        if high_uv_days:
            advice.append("High UV index expected. Protect sensitive crops with shade nets if possible.")
        
        # Default advice
        if not advice:
            advice.append("Favorable weather conditions for most agricultural activities.")
            advice.append("Continue regular farm operations and monitoring.")
        
        return advice
    
    def get_current_weather(self, location):
        """
        Get current weather conditions
        
        Args:
            location: Location name
            
        Returns:
            Dictionary with current weather data
        """
        season = self._get_current_season()
        pattern = self.SEASONAL_PATTERNS[season]
        
        temp = random.randint(pattern['temp_range'][0], pattern['temp_range'][1])
        humidity = random.randint(pattern['humidity_range'][0], pattern['humidity_range'][1])
        
        if random.random() < pattern['rain_prob']:
            condition = random.choice([c for c in pattern['conditions'] if 'Rain' in c or 'Thunderstorm' in c])
        else:
            condition = random.choice([c for c in pattern['conditions'] if 'Rain' not in c and 'Thunderstorm' not in c])
        
        return {
            'location': location,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': temp,
            'feels_like': temp + random.randint(-2, 3),
            'humidity': humidity,
            'weather_condition': condition,
            'wind_speed': round(random.uniform(5, 25), 1),
            'pressure': random.randint(1000, 1020),
            'visibility': random.randint(5, 10),
            'uv_index': round(random.uniform(0, 10), 1),
        }


# Singleton instance
weather_model = WeatherForecastModel()


def get_weather_forecast(location, days=7):
    """
    Convenience function to get weather forecast
    
    Args:
        location: Location name
        days: Number of days to forecast
        
    Returns:
        Dictionary with forecast data
    """
    return weather_model.get_forecast(location, days)


def get_current_weather(location):
    """
    Convenience function to get current weather
    
    Args:
        location: Location name
        
    Returns:
        Dictionary with current weather data
    """
    return weather_model.get_current_weather(location)
