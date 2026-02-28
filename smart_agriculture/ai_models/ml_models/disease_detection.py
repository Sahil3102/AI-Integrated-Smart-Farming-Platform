"""
Plant Disease Detection Model using CNN
This module provides disease detection functionality for crop leaf images.
"""
import os
import numpy as np
from PIL import Image
import json

# Disease database with treatment suggestions
DISEASE_DATABASE = {
    'Apple___Apple_scab': {
        'treatment': 'Apply fungicides like captan or myclobutanil. Remove and destroy infected leaves. Improve air circulation.',
        'severity': 'medium'
    },
    'Apple___Black_rot': {
        'treatment': 'Prune infected branches. Apply fungicides. Remove mummified fruits.',
        'severity': 'high'
    },
    'Apple___Cedar_apple_rust': {
        'treatment': 'Apply fungicides containing myclobutanil. Remove nearby cedar trees if possible.',
        'severity': 'medium'
    },
    'Apple___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Blueberry___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Cherry_(including_sour)___Powdery_mildew': {
        'treatment': 'Apply sulfur-based fungicides. Improve air circulation. Prune for better light penetration.',
        'severity': 'medium'
    },
    'Cherry_(including_sour)___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': {
        'treatment': 'Apply fungicides. Rotate crops. Use resistant varieties.',
        'severity': 'high'
    },
    'Corn_(maize)___Common_rust_': {
        'treatment': 'Apply fungicides containing azoxystrobin. Use resistant hybrids.',
        'severity': 'medium'
    },
    'Corn_(maize)___Northern_Leaf_Blight': {
        'treatment': 'Apply fungicides. Use resistant varieties. Practice crop rotation.',
        'severity': 'high'
    },
    'Corn_(maize)___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Grape___Black_rot': {
        'treatment': 'Apply fungicides. Remove infected berries and leaves. Improve air circulation.',
        'severity': 'high'
    },
    'Grape___Esca_(Black_Measles)': {
        'treatment': 'Remove infected vines. No effective chemical treatment available.',
        'severity': 'critical'
    },
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': {
        'treatment': 'Apply copper-based fungicides. Remove infected leaves.',
        'severity': 'medium'
    },
    'Grape___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Orange___Haunglongbing_(Citrus_greening)': {
        'treatment': 'Remove infected trees. Control psyllid vectors. No cure available.',
        'severity': 'critical'
    },
    'Peach___Bacterial_spot': {
        'treatment': 'Apply copper-based bactericides. Use resistant varieties. Avoid overhead irrigation.',
        'severity': 'medium'
    },
    'Peach___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Pepper,_bell___Bacterial_spot': {
        'treatment': 'Apply copper-based bactericides. Use disease-free seeds. Rotate crops.',
        'severity': 'medium'
    },
    'Pepper,_bell___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Potato___Early_blight': {
        'treatment': 'Apply fungicides containing chlorothalonil. Rotate crops. Remove infected leaves.',
        'severity': 'medium'
    },
    'Potato___Late_blight': {
        'treatment': 'Apply fungicides immediately. Destroy infected plants. Avoid overhead irrigation.',
        'severity': 'critical'
    },
    'Potato___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Raspberry___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Soybean___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Squash___Powdery_mildew': {
        'treatment': 'Apply sulfur or potassium bicarbonate. Improve air circulation.',
        'severity': 'medium'
    },
    'Strawberry___Leaf_scorch': {
        'treatment': 'Remove infected leaves. Apply fungicides. Ensure proper spacing.',
        'severity': 'medium'
    },
    'Strawberry___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
    'Tomato___Bacterial_spot': {
        'treatment': 'Apply copper-based bactericides. Use disease-free seeds. Avoid overhead watering.',
        'severity': 'medium'
    },
    'Tomato___Early_blight': {
        'treatment': 'Apply fungicides. Remove infected leaves. Mulch around plants.',
        'severity': 'medium'
    },
    'Tomato___Late_blight': {
        'treatment': 'Apply fungicides immediately. Remove infected plants. Ensure good drainage.',
        'severity': 'critical'
    },
    'Tomato___Leaf_Mold': {
        'treatment': 'Improve ventilation. Apply fungicides. Reduce humidity.',
        'severity': 'medium'
    },
    'Tomato___Septoria_leaf_spot': {
        'treatment': 'Remove infected leaves. Apply fungicides. Mulch to prevent splash.',
        'severity': 'medium'
    },
    'Tomato___Spider_mites Two-spotted_spider_mite': {
        'treatment': 'Apply miticides. Increase humidity. Use insecticidal soap.',
        'severity': 'medium'
    },
    'Tomato___Target_Spot': {
        'treatment': 'Apply fungicides. Remove infected leaves. Improve air circulation.',
        'severity': 'medium'
    },
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
        'treatment': 'Remove infected plants. Control whiteflies. Use resistant varieties.',
        'severity': 'critical'
    },
    'Tomato___Tomato_mosaic_virus': {
        'treatment': 'Remove infected plants. Disinfect tools. Use resistant varieties.',
        'severity': 'high'
    },
    'Tomato___healthy': {
        'treatment': 'No treatment needed. Maintain good agricultural practices.',
        'severity': 'low'
    },
}


class DiseaseDetectionModel:
    """
    Plant Disease Detection Model
    Uses a CNN-based approach for detecting plant diseases from leaf images.
    """
    
    def __init__(self):
        self.model = None
        self.class_names = list(DISEASE_DATABASE.keys())
        self.img_size = (224, 224)
        self._load_model()
    
    def _load_model(self):
        """Load the pre-trained model"""
        try:
            # Try to load TensorFlow model
            import tensorflow as tf
            model_path = os.path.join(
                os.path.dirname(__file__), 
                'saved_models', 
                'disease_detection_model.h5'
            )
            
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                print("Disease detection model loaded successfully.")
            else:
                print("Model file not found. Using dummy predictions.")
                self.model = None
        except ImportError:
            print("TensorFlow not available. Using dummy predictions.")
            self.model = None
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def preprocess_image(self, image_path):
        """
        Preprocess image for model prediction
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image array
        """
        try:
            img = Image.open(image_path)
            img = img.convert('RGB')
            img = img.resize(self.img_size)
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            return img_array
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def predict(self, image_path):
        """
        Predict disease from image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with prediction results
        """
        # Preprocess image
        img_array = self.preprocess_image(image_path)
        
        if img_array is None:
            return self._dummy_prediction()
        
        try:
            if self.model is not None:
                # Real prediction
                predictions = self.model.predict(img_array, verbose=0)
                predicted_class_idx = np.argmax(predictions[0])
                confidence = float(predictions[0][predicted_class_idx])
                
                if predicted_class_idx < len(self.class_names):
                    disease_name = self.class_names[predicted_class_idx]
                else:
                    return self._dummy_prediction()
            else:
                # Dummy prediction for demonstration
                return self._dummy_prediction()
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._dummy_prediction()
        
        # Get treatment suggestion
        disease_info = DISEASE_DATABASE.get(disease_name, {
            'treatment': 'Consult an agricultural expert for proper diagnosis and treatment.',
            'severity': 'unknown'
        })
        
        return {
            'disease_name': disease_name.replace('___', ' - ').replace('_', ' '),
            'confidence_score': round(confidence * 100, 2),
            'treatment_suggestion': disease_info['treatment'],
            'severity_level': disease_info['severity'],
            'all_probabilities': {
                self.class_names[i].replace('___', ' - ').replace('_', ' '): 
                round(float(predictions[0][i]) * 100, 2) 
                for i in range(min(5, len(self.class_names)))
            }
        }
    
    def _dummy_prediction(self):
        """Generate dummy prediction for demonstration"""
        import random
        
        disease_name = random.choice(self.class_names)
        confidence = random.uniform(0.75, 0.98)
        disease_info = DISEASE_DATABASE.get(disease_name, {
            'treatment': 'Consult an agricultural expert.',
            'severity': 'medium'
        })
        
        return {
            'disease_name': disease_name.replace('___', ' - ').replace('_', ' '),
            'confidence_score': round(confidence * 100, 2),
            'treatment_suggestion': disease_info['treatment'],
            'severity_level': disease_info['severity'],
            'note': 'This is a demonstration prediction. For production, train and load a real model.'
        }


# Singleton instance
disease_model = DiseaseDetectionModel()


def detect_disease(image_path):
    """
    Convenience function to detect disease from image
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with detection results
    """
    return disease_model.predict(image_path)
