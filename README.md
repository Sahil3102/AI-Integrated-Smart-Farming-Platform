# Smart AI Agriculture Decision Platform

A comprehensive Django-based web platform that uses AI/ML to help farmers detect plant diseases, predict crop prices, get soil-based crop recommendations, and access weather forecasts. The platform also connects farmers with buyers for direct crop sales.

## Features

### For Farmers
- **AI Disease Detection**: Upload crop leaf images to detect diseases and get treatment suggestions
- **Crop Price Prediction**: Predict crop prices based on location, season, and weather conditions
- **Soil Recommendation**: Get personalized crop recommendations based on soil NPK values and pH
- **Weather Forecast**: Access 7-day weather forecasts with agricultural advice
- **Crop Listing**: List crops for sale with images, price, and quantity
- **Order Management**: Manage incoming orders from buyers
- **Sales History**: Track all sales and revenue
- **Reputation Score**: Build reputation based on sales, ratings, and performance

### For Buyers
- **Browse Crops**: Search and filter crops by price, location, and type
- **View Farmer Profiles**: Check farmer reputation scores before purchasing
- **Place Orders**: Buy crops directly from farmers
- **Order History**: Track all purchases
- **Wishlist**: Save favorite crops for later

### For Admins
- **User Management**: Manage all users (farmers, buyers, analysts)
- **System Analytics**: View platform statistics and metrics
- **Activity Logs**: Monitor system activities

### For Analysts
- **Analytics Dashboard**: View comprehensive charts and reports
- **AI Model Metrics**: Monitor disease detection accuracy, price trends, prediction usage
- **Farmer Sales Analytics**: Analyze sales patterns and performance

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL
- **AI/ML**: TensorFlow, Keras, Scikit-learn, XGBoost
- **API**: Django REST Framework with JWT Authentication
- **Frontend**: Tailwind CSS, Chart.js
- **Authentication**: Django Auth + JWT Tokens

## Project Structure

```
smart_agriculture_platform/
├── smart_agriculture/          # Main Django project
│   ├── accounts/               # User authentication & management
│   ├── farmer/                 # Farmer dashboard & features
│   ├── buyer/                  # Buyer dashboard & features
│   ├── ai_models/              # AI/ML models & predictions
│   │   └── ml_models/          # ML model implementations
│   ├── analytics/              # Analytics & reporting
│   ├── soil/                   # Soil data management
│   ├── weather/                # Weather data & forecasts
│   ├── core_dashboard/         # Main dashboard & admin views
│   ├── templates/              # HTML templates
│   └── static/                 # Static files (CSS, JS, images)
├── media/                      # User-uploaded files
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- pip

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd smart_agriculture_platform
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Database
1. Create a PostgreSQL database:
```bash
createdb smart_agriculture
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` with your database credentials:
```
DB_NAME=smart_agriculture
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 5: Run Migrations
```bash
python manage.py migrate
```

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

Access the application at: http://127.0.0.1:8000/

## AI/ML Models

### 1. Plant Disease Detection
- Uses CNN-based image classification
- Supports 38 different plant diseases
- Provides confidence scores and treatment suggestions

### 2. Crop Price Prediction
- Uses Random Forest/Decision Tree algorithms
- Considers location, season, and rainfall data
- Provides price trends and future predictions

### 3. Soil Recommendation
- Recommends crops based on NPK values and pH
- Provides fertilizer recommendations
- Calculates soil health scores

### 4. Weather Forecast
- Provides 7-day weather forecasts
- Includes agricultural advice
- Tracks temperature, humidity, and rainfall

## API Endpoints

### Authentication
- `POST /accounts/api/register/` - User registration
- `POST /accounts/api/login/` - User login (returns JWT tokens)
- `POST /accounts/api/logout/` - User logout
- `GET /accounts/api/profile/` - Get user profile

### AI Predictions
- `POST /api/disease/` - Disease detection from image
- `POST /api/price/` - Crop price prediction
- `POST /api/soil/` - Soil-based crop recommendation
- `GET /api/weather/` - Weather forecast

### Farmer
- `GET /farmer/api/dashboard-stats/` - Dashboard statistics
- `POST /farmer/api/add-crop/` - Add new crop listing
- `GET /farmer/api/orders/` - Get farmer orders

### Buyer
- `GET /buyer/api/dashboard-stats/` - Dashboard statistics
- `GET /buyer/api/browse/` - Browse available crops
- `POST /buyer/api/buy/` - Place an order

### Analytics
- `GET /analytics/api/summary/` - Platform summary
- `GET /analytics/api/model-accuracy/` - AI model metrics

## User Roles

1. **Farmer**: Can list crops, use AI tools, manage orders
2. **Buyer**: Can browse crops, place orders, view farmer profiles
3. **Admin**: Full system access, user management
4. **Analyst**: Access to analytics dashboards and reports

## Reputation Score System

The reputation score is calculated using the formula:
```
reputation_score = (total_sales * 0.4) + 
                   (avg_rating * 0.3 * 10) + 
                   (product_quality * 0.2 * 10) + 
                   (on_time_delivery * 0.1 * 10)
```

Factors:
- Total sales (40% weight)
- Average rating (30% weight)
- Product quality rating (20% weight)
- On-time delivery rate (10% weight)

## Security Features

- Django authentication system
- JWT token-based API authentication
- CSRF protection
- Role-based access control
- Secure file uploads
- Password hashing with bcrypt

## Development

### Running Tests
```bash
python manage.py test
```

### Loading Sample Data
```bash
python manage.py loaddata sample_data.json
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure proper `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Set up PostgreSQL database
5. Configure static files with WhiteNoise or CDN
6. Set up media file storage (AWS S3, etc.)
7. Use HTTPS
8. Configure proper logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email support@smartagri.ai or create an issue in the repository.

## Acknowledgments

- Plant disease dataset from PlantVillage
- Weather data APIs
- Agricultural research institutions for crop data
