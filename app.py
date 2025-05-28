# Importing required Python libraries
import pickle  # Used to load the saved machine learning models
import pandas as pd  # For handling data (though not used much here)
import os  # Helps with file paths
import requests  # Can be used to make web requests (not used in this code)
import json  # Helps to work with JSON data
from flask import Flask, request, jsonify, render_template, send_from_directory  # Flask web framework
from datetime import datetime  # For working with dates and time (not used here)
import re  # Regular expressions (not used here)

# Get the current directory of the running file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Set the paths for static and template folders
static_folder = os.path.join(current_dir, 'static')
template_folder = os.path.join(current_dir, 'templates')

# Create a Flask app and link it to the folders
app = Flask(__name__, 
            static_folder=static_folder,
            static_url_path='/static',
            template_folder=template_folder)

# This function creates a complete path to access files
def get_absolute_path(relative_path):
    return os.path.join(current_dir, relative_path)

# Load the machine learning models and encoders that were saved earlier
with open(get_absolute_path('agricultural_models.pkl'), 'rb') as f:
    models = pickle.load(f)

# Extract individual models and encoders from the dictionary
seed_size_model = models['seed_size_model']
sowing_depth_model = models['sowing_depth_model']
spacing_model = models['spacing_model']
label_encoders = models['label_encoders']

# Load unique dropdown values for crop name, region, etc.
with open(get_absolute_path('unique_values.pkl'), 'rb') as f:
    unique_values = pickle.load(f)

# This will hold detailed information about soil types (can be used in frontend)
soil_types = unique_values['Soil Type']

# Home page route
@app.route('/')
def home():
    return render_template('index.html',
                           crops=unique_values['Crop Name'],
                           regions=unique_values['Region'],
                           seasons=unique_values['Season'],
                           soil_types=unique_values['Soil Type'],
                           soil_data=soil_types)

# Route to serve static files (like CSS, JS, images)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Route to handle prediction requests from the web form
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input values from the HTML form
        crop_name = request.form['crop_name']
        region = request.form['region']
        season = request.form['season']
        temperature = float(request.form.get('temperature', 0))  # default to 0 if missing
        moisture = float(request.form.get('moisture', 0))  # default to 0 if missing
        soil_type = request.form['soil_type']
        soil_ph = float(request.form['soil_ph'])

        # Convert text inputs to numbers using label encoders
        crop_name_encoded = label_encoders['Crop Name'].transform([crop_name])[0]
        region_encoded = label_encoders['Region'].transform([region])[0]
        season_encoded = label_encoders['Season'].transform([season])[0]
        soil_type_encoded = label_encoders['Soil Type'].transform([soil_type])[0]

        # Put all input values into a 2D list (model expects it this way)
        input_features = [[crop_name_encoded, region_encoded, season_encoded,
                           temperature, moisture, soil_type_encoded, soil_ph]]

        # Make predictions using the loaded models
        seed_size_encoded = seed_size_model.predict(input_features)[0]
        sowing_depth = sowing_depth_model.predict(input_features)[0]
        spacing = spacing_model.predict(input_features)[0]

        # Convert the predicted seed size from a number back to text (e.g. 0 → 'Small')
        seed_size = label_encoders['Seed Size Category'].inverse_transform([seed_size_encoded])[0]

        # Round the numeric values to two decimal places for better display
        sowing_depth = round(sowing_depth, 2)
        spacing = round(spacing, 2)

        # Try to find extra info about the selected soil type from the soil_types list
        soil_data = {}
        for soil in soil_types:
            if soil['name'] == soil_type:
                soil_data = soil
                break

        # If we don't find matching soil data, create a default message
        if not soil_data:
            soil_description = get_soil_info(soil_type)  # You might have a function for this
            soil_data = {
                'name': soil_type,
                'description': soil_description,
                'suitable_crops': []
            }

        # Return the prediction results in JSON format
        return jsonify({
            'seed_size': seed_size,
            'sowing_depth': sowing_depth,
            'spacing': spacing,
            'selected_soil_type': soil_type,
            'soil_description': soil_data.get('description', ''),
            'recommended_crops': []  # This will be filled using Gemini or manually later
        })

    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)})

# API route to provide soil type info to frontend
@app.route('/api/soil-types', methods=['GET'])
def get_soil_types():
    """Returns all soil type details as JSON"""
    return jsonify(soil_types)


#--------------------------------------------------------------------------------------------------------------------------------------



# Soil type data
soil_types = [
    {
        "id": "black_soil",
        "name": "Black Soil",
        "description": "Black soil, or Regur soil, is rich in clay minerals, calcium carbonate, magnesium, potash, and lime. It has excellent water retention capacity and is highly suitable for cotton cultivation.",
        "color": "#2d2d2d",
        "characteristics": [
            "High water retention",
            "Rich in nutrients",
            "Clay-like texture",
            "Self-ploughing nature"
        ],
        "suitable_crops": [], # Will be dynamically populated by Gemini
        "regions": ["Vidarbha", "Marathwada"]
    },
    {
        "id": "red_soil",
        "name": "Red Soil",
        "description": "Red soil gets its color from iron oxide. It is generally poor in nitrogen, phosphoric acid, and organic matter but rich in potash. It's porous with good drainage properties.",
        "color": "#8B2500",
        "characteristics": [
            "Porous and well-drained",
            "Rich in iron oxides",
            "Poor in nitrogen",
            "Sandy to clayey texture"
        ],
        "suitable_crops": [], # Will be dynamically populated by Gemini
        "regions": ["Western Maharashtra"]
    },
    {
        "id": "laterite_soil",
        "name": "Laterite Soil",
        "description": "Laterite soil is formed under tropical conditions due to intense weathering. It's rich in iron and aluminum but poor in nitrogen, potash, potassium, lime, and magnesium.",
        "color": "#BA8759",
        "characteristics": [
            "Highly weathered",
            "Rich in iron and aluminum",
            "Poor in organic matter",
            "Acidic nature"
        ],
        "suitable_crops": [], # Will be dynamically populated by Gemini
        "regions": ["Konkan"]
    },
    {
        "id": "medium_black_soil",
        "name": "Medium Black Soil",
        "description": "Medium black soil is less clayey than pure black soil but still has good moisture retention and nutrient content. It's versatile and supports a wide range of crops.",
        "color": "#4A4A4A",
        "characteristics": [
            "Moderate water retention",
            "Well-balanced texture",
            "Good fertility",
            "Mixed clayey and loamy"
        ],
        "suitable_crops": [], # Will be dynamically populated by Gemini
        "regions": ["North Maharashtra"]
    },
    {
        "id": "alluvial_soil",
        "name": "Alluvial Soil",
        "description": "Alluvial soil is formed by sediment deposited by rivers. It's extremely fertile with high amounts of potash, phosphoric acid, and lime but varying proportions of organic matter.",
        "color": "#D3C1AD",
        "characteristics": [
            "Very fertile",
            "Rich in minerals",
            "Variable texture",
            "Renewable fertility"
        ],
        "suitable_crops": [], # Will be dynamically populated by Gemini
        "regions": ["Various river basins in Maharashtra"]
    }
]

@app.route('/api/weather-proxy', methods=['GET'])
def weather_proxy():
    """API proxy for OpenWeatherMap with improved reliability and error handling"""
    try:
        # Get coordinates from request, defaulting to Mumbai if not provided
        lat = request.args.get('lat', '19.0760')
        lon = request.args.get('lon', '72.8777')
        
        # Use the API key directly
        api_key = 'write your api key here'
        
        # If there's an API key available, try the live API first
        if api_key:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
            response = requests.get(url, timeout=5)
            
            # Check if we got a valid response
            if response.status_code == 200:
                data = response.json()
                
                # Validate that the response contains required fields
                if 'main' in data and 'temp' in data['main'] and 'weather' in data and len(data['weather']) > 0:
                    return jsonify(data)
        
        # If we reach here, we need to use the fallback data
        return get_fallback_weather_data(lat, lon)
            
    except Exception as e:
        app.logger.error(f"Weather proxy error: {str(e)}")
        return get_fallback_weather_data(lat, lon)

def get_fallback_weather_data(lat=None, lon=None):
    """Simplified function to provide fallback weather data"""
    now = datetime.now()
    
    # Initialize with zero values
    temp = 0
    humidity = 0
    weather = {"main": "Clear", "description": "clear sky"}
    
    # Generate location name based on coordinates
    location_name = "Maharashtra"
    if lat and lon:
        lat_f = float(lat)
        lon_f = float(lon)
        
        if lat_f > 19.5 and lat_f <= 21.8 and lon_f >= 75.0 and lon_f <= 78.5:
            location_name = "Vidarbha Region"
        elif lat_f >= 17.5 and lat_f <= 19.5 and lon_f >= 75.5 and lon_f <= 78.0:
            location_name = "Marathwada Region"
        elif lat_f >= 15.5 and lat_f <= 19.0 and lon_f >= 73.5 and lon_f <= 75.5:
            location_name = "Western Maharashtra"
        elif lat_f >= 15.5 and lat_f <= 20.0 and lon_f >= 72.5 and lon_f <= 73.5:
            location_name = "Konkan Region"
        elif lat_f >= 20.0 and lat_f <= 22.0 and lon_f >= 73.5 and lon_f <= 75.0:
            location_name = "North Maharashtra"
    
    result = {
        'main': {
            'temp': round(temp, 1),
            'humidity': round(humidity),
            'pressure': 1013
        },
        'weather': [weather],
        'wind': {
            'speed': 3.5
        },
        'name': location_name,
        'sys': {
            'country': 'IN',
            'sunrise': int((now.replace(hour=6, minute=0, second=0)).timestamp()),
            'sunset': int((now.replace(hour=18, minute=30, second=0)).timestamp())
        },
        'dt': int(now.timestamp()),
        'coord': {
            'lat': float(lat) if lat else 19.0760,
            'lon': float(lon) if lon else 72.8777
        },
        'fallback': True
    }
    
    return jsonify(result)

@app.route('/sensorData/plant_data.json')
def get_sensor_data():
    """API endpoint to serve the sensor data from the sensorData folder"""
    try:
        # Read the plant_data.json file from the sensorData folder
        sensor_data_path = os.path.join(current_dir, 'sensorData', 'plant_data.json')
        
        # Check if the file exists
        if not os.path.exists(sensor_data_path):
            # If file doesn't exist, generate dummy data
            dummy_data = [{
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": 0,
                "humidity": 0,
                "soil_moisture": 0,  # Raw value from 0-255 range
                "motion_detected": "NO",
                "pump_state": "OFF"
            }]
            return jsonify(dummy_data)
        
        # Open and read the file
        with open(sensor_data_path, 'r') as file:
            sensor_data = file.read()
            
        # Return the JSON data
        return app.response_class(
            response=sensor_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        app.logger.error(f"Sensor data error: {str(e)}")
        return jsonify([{
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": 0,
            "humidity": 0,
            "soil_moisture": 0,
            "motion_detected": "ERROR",
            "pump_state": "ERROR"
        }]), 500

# Execute plant_monitor.py to update sensor data
@app.route('/api/update-sensor-data', methods=['POST'])
def update_sensor_data():
    """API endpoint to execute plant_monitor.py and update sensor data"""
    try:
        # Path to the plant_monitor.py script
        plant_monitor_path = os.path.join(current_dir, 'sensorData', 'plant_monitor.py')
        
        # Execute the script using subprocess
        import subprocess
        result = subprocess.run(['python', plant_monitor_path], 
                               capture_output=True, 
                               text=True,
                               cwd=os.path.join(current_dir, 'sensorData'))
        
        # Check if execution was successful
        if result.returncode == 0:
            return jsonify({"status": "success", "message": "Sensor data updated"})
        else:
            return jsonify({
                "status": "error", 
                "message": "Failed to update sensor data",
                "error": result.stderr
            }), 500
    except Exception as e:
        app.logger.error(f"Update sensor data error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/crops/recommend', methods=['POST'])
def recommend_crops():
    """API endpoint to get crop recommendations using Gemini API"""
    try:
        # Get input parameters
        data = request.json
        crop_name = data.get('crop_name', '')
        region = data.get('region', '')
        season = data.get('season', '')
        temperature = data.get('temperature', 0)
        moisture = data.get('moisture', 0)
        humidity = data.get('humidity', 0)
        soil_type = data.get('soil_type', '')
        soil_ph = data.get('soil_ph', 7.0)
        
        # Get soil and region specific details
        soil_info = get_soil_info(soil_type)
        region_info = get_region_info(region)
        season_info = get_season_info(season)
        
        # Prepare a more specific prompt for Gemini
        prompt = f"""
As an agricultural specialist for Maharashtra, India, provide SPECIFIC and VARIED crop recommendations for these EXACT growing conditions:

DETAILED CONDITIONS:
- Region: {region} ({region_info})
- Season: {season} ({season_info})
- Soil Type: {soil_type} ({soil_info})
- Current Temperature: {temperature}°C
- Current Soil Moisture: {moisture}%
- Current Humidity: {humidity}%
- Soil pH: {soil_ph}

IMPORTANT:
1. DO NOT return generic crops like "Wheat, Rice, Cotton, Jowar, Bajra" - be specific to these conditions
2. Include at least 2-3 specialty or niche crops suitable for these specific conditions
3. Make recommendations DIFFERENT from what you would recommend for other soil types or conditions

Format your response ONLY as a JSON array containing 5-7 crop names:
["Crop1", "Crop2", "Crop3", "Crop4", "Crop5"]
"""
        
        # Call Gemini API with a higher temperature setting for more varied responses
        api_key = os.environ.get('GEMINI_API_KEY', 'write your api key here')
        if not api_key:
            return jsonify({"error": "Gemini API key not found"}), 400
            
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
            json={
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.9,
                    "maxOutputTokens": 1024
                }
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"API request failed with status {response.status_code}")
            
        result = response.json()
        text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        # Extract crops from text
        try:
            # Try to parse as JSON array
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                crops_list = json.loads(json_str)
                if not isinstance(crops_list, list):
                    raise ValueError("Not a list")
            else:
                # Fallback to text parsing if JSON parsing fails
                crops_list = [line.strip() for line in text.split('\n') if line.strip()]
                # Remove any list markers
                crops_list = [re.sub(r'^\d+\.?\s*|\*\s*|[\[\]"\',.]+', '', crop).strip() for crop in crops_list]
                crops_list = [crop for crop in crops_list if len(crop) > 2]
        except Exception as e:
            app.logger.error(f"Error parsing crops: {str(e)}")
            # Fallback to region/soil/season specific crops
            crops_list = get_fallback_crops(soil_type, region, season, temperature, moisture)
            
        # Return only the first 5-7 items
        crops_list = crops_list[:7]
        
        # Make sure we don't return the "wheat, rice, cotton, jowar, bajra" default set
        if is_default_set(crops_list):
            crops_list = get_fallback_crops(soil_type, region, season, temperature, moisture)
        
        return jsonify({"crops": crops_list})
        
    except Exception as e:
        app.logger.error(f"Crop recommendation error: {str(e)}")
        # Fallback recommendations
        return jsonify({
            "crops": get_fallback_crops(soil_type, region, season, temperature, moisture),
            "error": str(e)
        })

def is_default_set(crops):
    """Check if the crop list matches the common default set"""
    default_crops = set(['wheat', 'rice', 'cotton', 'jowar', 'bajra'])
    found_crops = set([c.lower() for c in crops])
    return len(found_crops.intersection(default_crops)) >= 3

def get_soil_info(soil_type):
    """Get soil type specific information with detailed descriptions"""
    # First check our detailed soil data array with exact match
    for soil in soil_types:
        if soil['name'].lower() == soil_type.lower():
            return soil['description']
    
    # If no exact match, check partial match with soil_types
    for soil in soil_types:
        if soil_type.lower() in soil['name'].lower() or soil['name'].lower() in soil_type.lower():
            return soil['description']
    
    # If not found in soil_types, check our backup detailed descriptions with exact match
    soil_info = {
        'Black Soil': 'Black soil, or Regur soil, is rich in clay minerals, calcium carbonate, magnesium, potash, and lime. It has excellent water retention capacity with high clay content (alkaline with pH 7.5-8.5). Ideal for cotton cultivation and self-ploughing in nature.',
        'Red Soil': 'Red soil gets its color from iron oxide. It is generally poor in nitrogen, phosphoric acid, and organic matter but rich in potash. It has porous structure with good drainage properties, slightly acidic with pH 6.0-6.8, suitable for millets and legumes.',
        'Laterite Soil': 'Laterite soil is formed under tropical conditions due to intense weathering. It\'s rich in iron and aluminum oxides but poor in nitrogen, potash, calcium, lime, and magnesium. Highly acidic with pH 5.0-6.0, requires fertilization, suitable for plantation crops.',
        'Medium Black Soil': 'Medium black soil is less clayey than pure black soil but still has good moisture retention and nutrient content. It has balanced drainage and water retention with pH 7.0-8.0. Versatile and supports a wide range of crops with good fertility.',
        'Alluvial Soil': 'Alluvial soil is formed by sediment deposited by rivers. It\'s extremely fertile with high amounts of potash, phosphoric acid, and lime but varying proportions of organic matter. Has variable texture with pH 6.5-7.5, excellent for intensive agriculture.',
        'Sandy Soil': 'Sandy soil has large particles with excellent drainage but poor water and nutrient retention. It\'s typically acidic with pH 5.5-6.5 and warms quickly in spring. Suitable for early planting, root vegetables, and drought-resistant plants.'
    }
    
    # Check exact match in soil_info dictionary
    for key, description in soil_info.items():
        if key.lower() == soil_type.lower():
            return description
    
    # Check partial match in soil_info dictionary
    for key, description in soil_info.items():
        if key.lower() in soil_type.lower() or soil_type.lower() in key.lower():
            return description
    
    # For completely unknown soil types, try to extract the soil type name
    soil_keywords = ['black', 'red', 'laterite', 'alluvial', 'sandy', 'medium']
    soil_type_lower = soil_type.lower()
    
    for keyword in soil_keywords:
        if keyword in soil_type_lower:
            for key, description in soil_info.items():
                if keyword in key.lower():
                    return description
    
    # Last resort - return information about Maharashtra soils but with the specific soil type mentioned
    return f"{soil_type} is found across various regions of Maharashtra. It has distinctive properties that influence crop selection and agricultural practices based on its texture, drainage characteristics, and mineral composition."

def get_region_info(region):
    """Get region specific information"""
    region_info = {
        'Vidarbha': 'hot and dry climate, moderate rainfall of 700-900mm annually',
        'Marathwada': 'semi-arid climate, low rainfall (600-800mm), prone to drought',
        'Western Maharashtra': 'moderate rainfall (700-1200mm), diverse climate zones',
        'Konkan': 'high rainfall region (2500-3500mm), coastal climate, humid',
        'North Maharashtra': 'varied climate with moderate rainfall (600-900mm)'
    }
    return region_info.get(region, 'specific regional climate and growing conditions')

def get_season_info(season):
    """Get seasonal information"""
    season_info = {
        'Kharif': 'monsoon season from June to October, warm and humid with plenty of rainfall',
        'Rabi': 'winter season from October to March, cooler temperatures with limited rainfall',
        'Summer': 'hot dry season from March to June, high temperatures with very limited rainfall'
    }
    return season_info.get(season, 'specific growing season with characteristic climate')

def get_fallback_crops(soil_type, region, season, temperature, moisture):
    """Get fallback crops based on soil type, region, and season"""
    # Create a combination key with temperature and moisture ranges
    temp_range = 'Normal'
    if temperature < 20:
        temp_range = 'Cool'
    elif temperature > 30:
        temp_range = 'Hot'
    
    moisture_range = 'Medium'
    if moisture < 40:
        moisture_range = 'Dry'
    elif moisture > 70:
        moisture_range = 'Wet'
    
    key = f"{soil_type}_{region}_{season}_{temp_range}_{moisture_range}".replace(' ', '')
    
    # Define a wide variety of crop combinations
    fallbacks = {
        # Black Soil combinations
        'BlackSoil_Vidarbha_Kharif_Hot_Dry': ['Cotton', 'Moth Bean', 'Cluster Bean', 'Castor', 'Sesame'],
        'BlackSoil_Vidarbha_Rabi_Cool_Medium': ['Wheat', 'Chickpea', 'Safflower', 'Linseed', 'Coriander'],
        'BlackSoil_Vidarbha_Summer_Hot_Dry': ['Sunflower', 'Mung Bean', 'Cluster Bean', 'Watermelon', 'Bitter Gourd'],
        
        # Red Soil combinations
        'RedSoil_WesternMaharashtra_Kharif_Hot_Dry': ['Pearl Millet', 'Moth Bean', 'Cluster Bean', 'Horse Gram', 'Castor'],
        'RedSoil_WesternMaharashtra_Rabi_Cool_Medium': ['Chickpea', 'Safflower', 'Fenugreek', 'Coriander', 'Mustard'],
        'RedSoil_WesternMaharashtra_Summer_Hot_Medium': ['Groundnut', 'Sesame', 'Okra', 'Bitter Gourd', 'Ridge Gourd'],
        
        # Laterite Soil combinations
        'LateriteSoil_Konkan_Kharif_Hot_Wet': ['Rice', 'Finger Millet', 'Black Gram', 'Cowpea', 'Bitter Gourd'],
        'LateriteSoil_Konkan_Rabi_Cool_Medium': ['Sweet Potato', 'Colocasia', 'Turmeric', 'Elephant Foot Yam', 'Pulses'],
        'LateriteSoil_Konkan_Summer_Hot_Wet': ['Snake Gourd', 'Ridge Gourd', 'Bitter Gourd', 'Cucumber', 'Chillies'],
        
        # Alluvial Soil combinations
        'AlluvialSoil_WesternMaharashtra_Kharif_Hot_Wet': ['Rice', 'Taro', 'Water Chestnut', 'Lotus Root', 'Turmeric'],
        'AlluvialSoil_WesternMaharashtra_Rabi_Cool_Medium': ['Potato', 'Onion', 'Garlic', 'Tomato', 'Spinach'],
        'AlluvialSoil_WesternMaharashtra_Summer_Hot_Medium': ['Muskmelon', 'Bitter Gourd', 'Okra', 'Snake Gourd', 'Cucumber']
    }
    
    # Try to find matching fallback
    if key in fallbacks:
        return fallbacks[key]
    
    # Try with just soil and season
    key_simple = f"{soil_type}_{season}".replace(' ', '')
    simple_fallbacks = {
        'BlackSoil_Kharif': ['Cotton', 'Soybean', 'Pigeon Pea', 'Green Gram', 'Sorghum'],
        'BlackSoil_Rabi': ['Wheat', 'Chickpea', 'Safflower', 'Linseed', 'Mustard'],
        'BlackSoil_Summer': ['Sunflower', 'Sesame', 'Green Gram', 'Groundnut', 'Bottle Gourd'],
        'RedSoil_Kharif': ['Pearl Millet', 'Groundnut', 'Pigeon Pea', 'Green Gram', 'Sorghum'],
        'RedSoil_Rabi': ['Sorghum', 'Chickpea', 'Safflower', 'Sunflower', 'Mustard'],
        'RedSoil_Summer': ['Groundnut', 'Sesame', 'Bitter Gourd', 'Watermelon', 'Muskmelon'],
        'LateriteSoil_Kharif': ['Rice', 'Finger Millet', 'Cowpea', 'Horse Gram', 'Sesame'],
        'LateriteSoil_Rabi': ['Finger Millet', 'Sweet Potato', 'Pulses', 'Turmeric', 'Elephant Foot Yam'],
        'LateriteSoil_Summer': ['Bitter Gourd', 'Ridge Gourd', 'Cucumber', 'Snake Gourd', 'Chillies'],
        'MediumBlackSoil_Kharif': ['Cotton', 'Pearl Millet', 'Sorghum', 'Pigeon Pea', 'Green Gram'],
        'MediumBlackSoil_Rabi': ['Wheat', 'Chickpea', 'Safflower', 'Mustard', 'Fenugreek'],
        'MediumBlackSoil_Summer': ['Groundnut', 'Sunflower', 'Bitter Gourd', 'Ridge Gourd', 'Watermelon'],
        'AlluvialSoil_Kharif': ['Rice', 'Sugarcane', 'Turmeric', 'Ginger', 'Taro'],
        'AlluvialSoil_Rabi': ['Wheat', 'Potato', 'Onion', 'Garlic', 'Tomato'],
        'AlluvialSoil_Summer': ['Muskmelon', 'Watermelon', 'Cucumber', 'Bitter Gourd', 'Okra'],
        'SandySoil_Kharif': ['Pearl Millet', 'Cluster Bean', 'Moth Bean', 'Sesame', 'Cowpea'],
        'SandySoil_Rabi': ['Cumin', 'Mustard', 'Chickpea', 'Coriander', 'Fenugreek'],
        'SandySoil_Summer': ['Watermelon', 'Muskmelon', 'Cluster Bean', 'Cucumber', 'Ridge Gourd']
    }
    
    if key_simple in simple_fallbacks:
        return simple_fallbacks[key_simple]
    
    # Final fallback - some unique crops that aren't wheat, rice, cotton, jowar, bajra
    soil_fallbacks = {
        'Black Soil': ['Soybean', 'Pigeon Pea', 'Sunflower', 'Safflower', 'Chickpea'],
        'Red Soil': ['Pearl Millet', 'Groundnut', 'Pigeon Pea', 'Sesame', 'Mustard'],
        'Laterite Soil': ['Finger Millet', 'Sweet Potato', 'Turmeric', 'Bitter Gourd', 'Snake Gourd'],
        'Medium Black Soil': ['Soybean', 'Chickpea', 'Sunflower', 'Mustard', 'Pigeon Pea'],
        'Alluvial Soil': ['Potato', 'Sugarcane', 'Onion', 'Turmeric', 'Ginger'],
        'Sandy Soil': ['Watermelon', 'Muskmelon', 'Cluster Bean', 'Groundnut', 'Sesame']
    }
    
    if soil_type in soil_fallbacks:
        return soil_fallbacks[soil_type]
    
    # Last resort
    return ['Sunflower', 'Green Gram', 'Groundnut', 'Okra', 'Bitter Gourd']

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
