"""
Soil-based Crop Recommendation Model
This module provides crop recommendations based on soil nutrients.
"""
import os
import numpy as np

# Crop requirements database
# Format: crop_name: (N_min, N_max, P_min, P_max, K_min, K_max, pH_min, pH_max)
CROP_REQUIREMENTS = {
    'rice': (80, 120, 40, 60, 40, 60, 5.5, 6.5),
    'wheat': (100, 150, 50, 75, 50, 75, 6.0, 7.0),
    'maize': (100, 150, 50, 75, 50, 75, 5.8, 7.0),
    'cotton': (100, 150, 50, 75, 50, 75, 6.0, 7.5),
    'sugarcane': (150, 250, 60, 100, 80, 120, 6.0, 7.5),
    'potato': (100, 150, 50, 75, 100, 150, 5.0, 6.5),
    'tomato': (80, 120, 60, 90, 80, 120, 6.0, 6.8),
    'onion': (80, 120, 40, 60, 80, 120, 6.0, 7.0),
    'soybean': (20, 40, 40, 60, 40, 60, 6.0, 7.0),
    'groundnut': (20, 40, 40, 60, 40, 60, 6.0, 7.0),
    'mustard': (60, 100, 30, 50, 30, 50, 6.0, 7.5),
    'chickpea': (20, 40, 40, 60, 40, 60, 6.0, 7.5),
    'lentil': (20, 40, 30, 50, 30, 50, 5.5, 7.0),
    'pearl_millet': (40, 60, 20, 40, 20, 40, 6.0, 7.5),
    'sorghum': (60, 100, 30, 50, 30, 50, 5.5, 7.5),
    'barley': (60, 100, 30, 50, 30, 50, 6.0, 7.5),
    'sunflower': (60, 100, 40, 60, 40, 60, 6.0, 7.5),
    'sesame': (40, 60, 20, 40, 20, 40, 5.5, 7.0),
    'turmeric': (100, 150, 50, 75, 100, 150, 5.5, 7.0),
    'ginger': (100, 150, 50, 75, 100, 150, 5.5, 7.0),
    'carrot': (60, 100, 40, 60, 80, 120, 5.5, 7.0),
    'cabbage': (100, 150, 50, 75, 80, 120, 6.0, 7.5),
    'cauliflower': (100, 150, 50, 75, 80, 120, 5.5, 7.0),
    'brinjal': (80, 120, 50, 75, 80, 120, 5.5, 6.5),
    'okra': (60, 100, 40, 60, 60, 100, 6.0, 7.0),
    'chili': (80, 120, 50, 75, 60, 100, 5.5, 6.5),
    'spinach': (60, 100, 40, 60, 60, 100, 6.0, 7.5),
    'fenugreek': (20, 40, 20, 40, 20, 40, 6.0, 7.5),
    'coriander': (40, 60, 20, 40, 20, 40, 6.0, 7.5),
    'garlic': (80, 120, 50, 75, 80, 120, 5.5, 7.0),
}

# Fertilizer recommendations
FERTILIZER_RECOMMENDATIONS = {
    'rice': {
        'deficiency': {
            'N': 'Apply Urea (46% N) @ 110 kg/ha or Ammonium Sulfate (21% N) @ 240 kg/ha',
            'P': 'Apply Single Super Phosphate (16% P) @ 312 kg/ha or DAP (46% P) @ 109 kg/ha',
            'K': 'Apply Muriate of Potash (60% K) @ 83 kg/ha or Sulfate of Potash (50% K) @ 100 kg/ha',
        },
        'general': 'Apply NPK 20-20-20 @ 500 kg/ha as basal dose. Top dress with Urea @ 50 kg/ha at tillering stage.',
    },
    'wheat': {
        'deficiency': {
            'N': 'Apply Urea @ 130 kg/ha in split doses - 1/3 at sowing, 1/3 at crown root initiation, 1/3 at flowering',
            'P': 'Apply DAP @ 130 kg/ha at sowing time',
            'K': 'Apply Muriate of Potash @ 63 kg/ha at sowing',
        },
        'general': 'Apply NPK 15-15-15 @ 400 kg/ha as basal. Top dress with Urea @ 60 kg/ha at first irrigation.',
    },
    'maize': {
        'deficiency': {
            'N': 'Apply Urea @ 130 kg/ha - 1/2 at sowing, 1/4 at knee-high stage, 1/4 at tasseling',
            'P': 'Apply DAP @ 109 kg/ha at sowing',
            'K': 'Apply Muriate of Potash @ 63 kg/ha at sowing',
        },
        'general': 'Apply NPK 20-20-0 @ 400 kg/ha as basal. Side dress with Urea @ 50 kg/ha at 30 days after sowing.',
    },
    'cotton': {
        'deficiency': {
            'N': 'Apply Urea @ 130 kg/ha in split doses',
            'P': 'Apply DAP @ 109 kg/ha at sowing',
            'K': 'Apply Muriate of Potash @ 63 kg/ha at sowing',
        },
        'general': 'Apply NPK 20-20-20 @ 500 kg/ha as basal. Foliar spray of Urea @ 2% at flowering and boll formation.',
    },
    'sugarcane': {
        'deficiency': {
            'N': 'Apply Urea @ 250 kg/ha in 3 split doses',
            'P': 'Apply DAP @ 152 kg/ha at planting',
            'K': 'Apply Muriate of Potash @ 167 kg/ha in 2 split doses',
        },
        'general': 'Apply NPK 20-20-20 @ 750 kg/ha as basal. Apply Urea @ 100 kg/ha at 45 and 90 days after planting.',
    },
    'potato': {
        'deficiency': {
            'N': 'Apply Urea @ 125 kg/ha at planting',
            'P': 'Apply DAP @ 163 kg/ha at planting',
            'K': 'Apply Muriate of Potash @ 208 kg/ha at planting',
        },
        'general': 'Apply NPK 15-15-20 @ 500 kg/ha as basal. Top dress with Urea @ 50 kg/ha at earthing up.',
    },
    'tomato': {
        'deficiency': {
            'N': 'Apply Urea @ 100 kg/ha in split doses',
            'P': 'Apply DAP @ 130 kg/ha at transplanting',
            'K': 'Apply Muriate of Potash @ 167 kg/ha in split doses',
        },
        'general': 'Apply NPK 17-17-17 @ 500 kg/ha as basal. Fertigate with NPK 19-19-19 @ 5 kg/acre at 15-day intervals.',
    },
    'onion': {
        'deficiency': {
            'N': 'Apply Urea @ 100 kg/ha in split doses',
            'P': 'Apply DAP @ 87 kg/ha at transplanting',
            'K': 'Apply Muriate of Potash @ 167 kg/ha in split doses',
        },
        'general': 'Apply NPK 12-32-16 @ 400 kg/ha as basal. Top dress with Urea @ 50 kg/ha at 30 and 45 days.',
    },
    'soybean': {
        'deficiency': {
            'N': 'Apply minimal N as soybean fixes nitrogen. Use Rhizobium inoculation.',
            'P': 'Apply DAP @ 87 kg/ha at sowing',
            'K': 'Apply Muriate of Potash @ 63 kg/ha at sowing',
        },
        'general': 'Apply NPK 0-20-20 @ 250 kg/ha as basal. Use Rhizobium culture for seed treatment.',
    },
    'groundnut': {
        'deficiency': {
            'N': 'Apply minimal N. Use Rhizobium inoculation.',
            'P': 'Apply DAP @ 87 kg/ha at sowing',
            'K': 'Apply Muriate of Potash @ 63 kg/ha at sowing',
        },
        'general': 'Apply NPK 0-20-20 @ 250 kg/ha as basal. Apply Gypsum @ 400 kg/ha at pegging.',
    },
    'default': {
        'deficiency': {
            'N': 'Apply Urea @ 100 kg/ha based on soil test results',
            'P': 'Apply DAP @ 100 kg/ha at sowing/planting',
            'K': 'Apply Muriate of Potash @ 80 kg/ha at sowing/planting',
        },
        'general': 'Apply balanced NPK fertilizer based on soil test. Incorporate organic matter for long-term soil health.',
    },
}


class SoilRecommendationModel:
    """
    Soil-based Crop Recommendation Model
    Recommends crops based on soil NPK values and pH level.
    """
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained model"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            import joblib
            
            model_path = os.path.join(
                os.path.dirname(__file__),
                'saved_models',
                'soil_recommendation_model.pkl'
            )
            
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                print("Soil recommendation model loaded successfully.")
            else:
                print("Model file not found. Using rule-based recommendations.")
                self.model = None
        except ImportError:
            print("Scikit-learn not available. Using rule-based recommendations.")
            self.model = None
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def calculate_soil_health_score(self, N, P, K, pH):
        """
        Calculate overall soil health score
        
        Args:
            N: Nitrogen content (kg/ha)
            P: Phosphorus content (kg/ha)
            K: Potassium content (kg/ha)
            pH: pH level
            
        Returns:
            Soil health score (0-100)
        """
        # Ideal ranges
        N_ideal = 100
        P_ideal = 50
        K_ideal = 75
        pH_ideal = 6.5
        
        # Calculate deviations
        N_score = max(0, 100 - abs(N - N_ideal) / N_ideal * 100)
        P_score = max(0, 100 - abs(P - P_ideal) / P_ideal * 100)
        K_score = max(0, 100 - abs(K - K_ideal) / K_ideal * 100)
        pH_score = max(0, 100 - abs(pH - pH_ideal) / 3.5 * 100)
        
        # Weighted average
        soil_health = (N_score * 0.3 + P_score * 0.25 + K_score * 0.25 + pH_score * 0.2)
        
        return round(soil_health, 2)
    
    def calculate_crop_suitability(self, N, P, K, pH, crop):
        """
        Calculate suitability score for a specific crop
        
        Args:
            N, P, K, pH: Soil parameters
            crop: Crop name
            
        Returns:
            Suitability score (0-100)
        """
        if crop not in CROP_REQUIREMENTS:
            return 0
        
        req = CROP_REQUIREMENTS[crop]
        N_min, N_max, P_min, P_max, K_min, K_max, pH_min, pH_max = req
        
        # Calculate individual scores
        N_score = self._parameter_score(N, N_min, N_max)
        P_score = self._parameter_score(P, P_min, P_max)
        K_score = self._parameter_score(K, K_min, K_max)
        pH_score = self._parameter_score(pH, pH_min, pH_max)
        
        # Weighted average
        suitability = (N_score * 0.3 + P_score * 0.25 + K_score * 0.25 + pH_score * 0.2)
        
        return round(suitability, 2)
    
    def _parameter_score(self, value, min_val, max_val):
        """Calculate score for a single parameter"""
        if min_val <= value <= max_val:
            return 100
        
        # Calculate deviation
        if value < min_val:
            deviation = (min_val - value) / min_val
        else:
            deviation = (value - max_val) / max_val
        
        score = max(0, 100 - deviation * 100)
        return score
    
    def get_fertilizer_recommendation(self, crop, N, P, K, pH):
        """
        Get fertilizer recommendation based on crop and soil status
        
        Args:
            crop: Recommended crop
            N, P, K, pH: Current soil parameters
            
        Returns:
            Fertilizer recommendation string
        """
        crop_lower = crop.lower()
        rec = FERTILIZER_RECOMMENDATIONS.get(crop_lower, FERTILIZER_RECOMMENDATIONS['default'])
        
        recommendations = []
        
        # Check for deficiencies
        if crop_lower in CROP_REQUIREMENTS:
            req = CROP_REQUIREMENTS[crop_lower]
            
            if N < req[0]:  # Below minimum N
                recommendations.append(f"Nitrogen: {rec['deficiency']['N']}")
            if P < req[2]:  # Below minimum P
                recommendations.append(f"Phosphorus: {rec['deficiency']['P']}")
            if K < req[4]:  # Below minimum K
                recommendations.append(f"Potassium: {rec['deficiency']['K']}")
        
        # pH adjustment
        if pH < 5.5:
            recommendations.append("pH: Apply agricultural lime @ 2-3 tonnes/ha to raise pH")
        elif pH > 7.5:
            recommendations.append("pH: Apply elemental sulfur @ 300-500 kg/ha to lower pH")
        
        # General recommendation
        if not recommendations:
            recommendations.append(rec['general'])
        
        return "\n".join(recommendations)
    
    def recommend(self, N, P, K, pH, humidity=None, temperature=None, rainfall=None):
        """
        Recommend crops based on soil parameters
        
        Args:
            N: Nitrogen content (kg/ha)
            P: Phosphorus content (kg/ha)
            K: Potassium content (kg/ha)
            pH: pH level
            humidity: Relative humidity % (optional)
            temperature: Temperature in Celsius (optional)
            rainfall: Annual rainfall in mm (optional)
            
        Returns:
            Dictionary with recommendation results
        """
        # Calculate soil health score
        soil_health = self.calculate_soil_health_score(N, P, K, pH)
        
        # Calculate suitability for all crops
        crop_scores = []
        for crop in CROP_REQUIREMENTS:
            score = self.calculate_crop_suitability(N, P, K, pH, crop)
            crop_scores.append((crop, score))
        
        # Sort by score
        crop_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top recommendation
        recommended_crop = crop_scores[0][0]
        confidence = crop_scores[0][1]
        
        # Get alternative crops
        alternatives = [
            {'crop': crop, 'suitability': score}
            for crop, score in crop_scores[1:4]
        ]
        
        # Get fertilizer recommendation
        fertilizer = self.get_fertilizer_recommendation(recommended_crop, N, P, K, pH)
        
        # Determine soil status
        if soil_health >= 80:
            soil_status = 'Excellent'
        elif soil_health >= 60:
            soil_status = 'Good'
        elif soil_health >= 40:
            soil_status = 'Fair'
        else:
            soil_status = 'Poor'
        
        return {
            'recommended_crop': recommended_crop.title(),
            'confidence_score': confidence,
            'soil_health_score': soil_health,
            'soil_status': soil_status,
            'alternative_crops': alternatives,
            'fertilizer_recommendation': fertilizer,
            'input_parameters': {
                'nitrogen': N,
                'phosphorus': P,
                'potassium': K,
                'ph': pH,
                'humidity': humidity,
                'temperature': temperature,
                'rainfall': rainfall,
            },
            'nutrient_status': {
                'nitrogen': 'Low' if N < 80 else 'Optimal' if N < 150 else 'High',
                'phosphorus': 'Low' if P < 40 else 'Optimal' if P < 80 else 'High',
                'potassium': 'Low' if K < 60 else 'Optimal' if K < 120 else 'High',
                'ph': 'Acidic' if pH < 6.0 else 'Neutral' if pH < 7.5 else 'Alkaline',
            },
            'note': 'Recommendations are based on soil nutrient levels. Consider climate and market factors before final decision.'
        }
    
    def batch_recommend(self, soil_data_list):
        """
        Get recommendations for multiple soil samples
        
        Args:
            soil_data_list: List of dictionaries with soil parameters
            
        Returns:
            List of recommendation results
        """
        results = []
        for data in soil_data_list:
            result = self.recommend(
                data.get('N'),
                data.get('P'),
                data.get('K'),
                data.get('pH'),
                data.get('humidity'),
                data.get('temperature'),
                data.get('rainfall')
            )
            results.append(result)
        return results


# Singleton instance
soil_model = SoilRecommendationModel()


def recommend_crop(N, P, K, pH, humidity=None, temperature=None, rainfall=None):
    """
    Convenience function to get crop recommendation
    
    Args:
        N: Nitrogen content (kg/ha)
        P: Phosphorus content (kg/ha)
        K: Potassium content (kg/ha)
        pH: pH level
        humidity: Relative humidity % (optional)
        temperature: Temperature in Celsius (optional)
        rainfall: Annual rainfall in mm (optional)
        
    Returns:
        Dictionary with recommendation results
    """
    return soil_model.recommend(N, P, K, pH, humidity, temperature, rainfall)
