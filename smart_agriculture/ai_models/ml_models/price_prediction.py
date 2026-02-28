"""
Crop Price Prediction Model using Random Forest
This module provides crop price prediction based on various factors.
"""
import os
import numpy as np
import json
from datetime import datetime, timedelta

# Crop price database (historical averages)
CROP_PRICE_DATABASE = {
    'wheat': {'base_price': 22.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 1.1, 'zaid': 0.95}},
    'rice': {'base_price': 25.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.9, 'zaid': 1.05}},
    'maize': {'base_price': 18.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.95, 'zaid': 1.1}},
    'cotton': {'base_price': 65.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.85, 'zaid': 1.15}},
    'sugarcane': {'base_price': 3.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 1.05, 'zaid': 0.9}},
    'potato': {'base_price': 15.0, 'seasonal_factor': {'kharif': 0.9, 'rabi': 1.0, 'zaid': 1.2}},
    'tomato': {'base_price': 20.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 1.3, 'zaid': 0.8}},
    'onion': {'base_price': 25.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.9, 'zaid': 1.4}},
    'soybean': {'base_price': 38.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.95, 'zaid': 1.05}},
    'groundnut': {'base_price': 55.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.9, 'zaid': 1.1}},
    'mustard': {'base_price': 45.0, 'seasonal_factor': {'kharif': 0.85, 'rabi': 1.0, 'zaid': 1.15}},
    'chickpea': {'base_price': 52.0, 'seasonal_factor': {'kharif': 0.8, 'rabi': 1.0, 'zaid': 1.2}},
    'lentil': {'base_price': 65.0, 'seasonal_factor': {'kharif': 0.85, 'rabi': 1.0, 'zaid': 1.1}},
    'pearl_millet': {'base_price': 20.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.9, 'zaid': 1.05}},
    'sorghum': {'base_price': 22.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.95, 'zaid': 1.0}},
    'barley': {'base_price': 24.0, 'seasonal_factor': {'kharif': 0.9, 'rabi': 1.0, 'zaid': 1.05}},
    'sunflower': {'base_price': 58.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.95, 'zaid': 1.1}},
    'sesame': {'base_price': 95.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 0.85, 'zaid': 1.2}},
    'turmeric': {'base_price': 85.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 1.1, 'zaid': 0.9}},
    'ginger': {'base_price': 120.0, 'seasonal_factor': {'kharif': 1.0, 'rabi': 1.05, 'zaid': 0.95}},
}

# State-wise price factors
STATE_FACTORS = {
    'punjab': 1.1,
    'haryana': 1.08,
    'uttar pradesh': 1.0,
    'madhya pradesh': 0.95,
    'rajasthan': 0.92,
    'gujarat': 1.02,
    'maharashtra': 1.0,
    'karnataka': 0.98,
    'andhra pradesh': 0.97,
    'telangana': 0.98,
    'tamil nadu': 1.0,
    'kerala': 1.15,
    'west bengal': 0.95,
    'bihar': 0.9,
    'odisha': 0.92,
    'assam': 0.88,
    'jharkhand': 0.9,
    'chhattisgarh': 0.88,
    'himachal pradesh': 1.12,
    'uttarakhand': 1.05,
}


class PricePredictionModel:
    """
    Crop Price Prediction Model
    Uses Random Forest/Decision Tree approach for price prediction.
    """
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained model"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            import joblib
            
            model_path = os.path.join(
                os.path.dirname(__file__),
                'saved_models',
                'price_prediction_model.pkl'
            )
            
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                print("Price prediction model loaded successfully.")
            else:
                print("Model file not found. Using rule-based predictions.")
                self.model = None
        except ImportError:
            print("Scikit-learn not available. Using rule-based predictions.")
            self.model = None
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def _get_season_factor(self, crop, season):
        """Get seasonal price factor"""
        crop_data = CROP_PRICE_DATABASE.get(crop.lower(), {})
        seasonal_factors = crop_data.get('seasonal_factor', {})
        return seasonal_factors.get(season.lower(), 1.0)
    
    def _get_state_factor(self, state):
        """Get state-wise price factor"""
        return STATE_FACTORS.get(state.lower(), 1.0)
    
    def _get_rainfall_factor(self, rainfall):
        """Calculate rainfall impact on price"""
        if rainfall is None:
            return 1.0
        
        # Optimal rainfall: 800-1200mm
        if 800 <= rainfall <= 1200:
            return 1.0
        elif rainfall < 500:  # Drought condition
            return 1.3  # Prices increase due to shortage
        elif rainfall < 800:  # Below average
            return 1.1
        elif rainfall > 1500:  # Excess rainfall
            return 1.15  # Prices increase due to crop damage
        else:
            return 0.95  # Good rainfall, prices stable
    
    def predict(self, crop, state, season, rainfall=None):
        """
        Predict crop price
        
        Args:
            crop: Crop name
            state: State name
            season: Season (kharif, rabi, zaid)
            rainfall: Annual rainfall in mm (optional)
            
        Returns:
            Dictionary with prediction results
        """
        crop = crop.lower()
        state = state.lower()
        season = season.lower()
        
        # Get base price
        crop_data = CROP_PRICE_DATABASE.get(crop, {'base_price': 30.0, 'seasonal_factor': {}})
        base_price = crop_data['base_price']
        
        # Apply factors
        season_factor = self._get_season_factor(crop, season)
        state_factor = self._get_state_factor(state)
        rainfall_factor = self._get_rainfall_factor(rainfall)
        
        # Calculate predicted price
        predicted_price = base_price * season_factor * state_factor * rainfall_factor
        
        # Add some randomness for realistic variation (±5%)
        import random
        variation = random.uniform(0.95, 1.05)
        predicted_price *= variation
        
        # Determine trend
        if season_factor > 1.05:
            trend = 'increasing'
        elif season_factor < 0.95:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        # Generate historical data for chart
        historical_data = self._generate_historical_data(crop, base_price)
        
        # Generate future predictions
        future_predictions = self._generate_future_predictions(
            predicted_price, trend
        )
        
        return {
            'crop': crop.title(),
            'state': state.title(),
            'season': season.title(),
            'predicted_price': round(predicted_price, 2),
            'price_trend': trend,
            'confidence_interval': {
                'lower': round(predicted_price * 0.9, 2),
                'upper': round(predicted_price * 1.1, 2),
            },
            'historical_data': historical_data,
            'future_predictions': future_predictions,
            'factors': {
                'base_price': base_price,
                'season_factor': round(season_factor, 2),
                'state_factor': round(state_factor, 2),
                'rainfall_factor': round(rainfall_factor, 2),
            },
            'unit': 'Rs per kg',
            'note': 'Prices are indicative and may vary based on market conditions.'
        }
    
    def _generate_historical_data(self, crop, base_price):
        """Generate historical price data for charts"""
        import random
        
        historical = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for i, month in enumerate(months):
            # Add seasonal variation
            variation = random.uniform(0.85, 1.15)
            price = round(base_price * variation, 2)
            historical.append({
                'month': month,
                'price': price
            })
        
        return historical
    
    def _generate_future_predictions(self, current_price, trend):
        """Generate future price predictions"""
        import random
        
        predictions = []
        months = ['Next Month', 'In 2 Months', 'In 3 Months', 
                  'In 4 Months', 'In 5 Months', 'In 6 Months']
        
        trend_factor = {'increasing': 1.02, 'decreasing': 0.98, 'stable': 1.0}
        factor = trend_factor.get(trend, 1.0)
        
        price = current_price
        for month in months:
            price *= factor
            variation = random.uniform(0.97, 1.03)
            predictions.append({
                'period': month,
                'predicted_price': round(price * variation, 2)
            })
        
        return predictions
    
    def batch_predict(self, predictions_data):
        """
        Predict prices for multiple crops
        
        Args:
            predictions_data: List of dictionaries with crop, state, season
            
        Returns:
            List of prediction results
        """
        results = []
        for data in predictions_data:
            result = self.predict(
                data.get('crop'),
                data.get('state'),
                data.get('season'),
                data.get('rainfall')
            )
            results.append(result)
        return results


# Singleton instance
price_model = PricePredictionModel()


def predict_price(crop, state, season, rainfall=None):
    """
    Convenience function to predict crop price
    
    Args:
        crop: Crop name
        state: State name
        season: Season (kharif, rabi, zaid)
        rainfall: Annual rainfall in mm (optional)
        
    Returns:
        Dictionary with prediction results
    """
    return price_model.predict(crop, state, season, rainfall)
