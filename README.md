﻿# Agricultural Seed Predictor

An AI-powered web application that predicts optimal seed parameters (size, sowing depth, spacing) for different crops in Maharashtra, India, based on regional and environmental conditions.

## Features

- **Intelligent Predictions**: Machine learning models trained on agricultural data specific to Maharashtra.
- **Geolocation Integration**: Automatically detects user location and suggests regional parameters.
- **Weather Integration**: Fetches real-time weather data to improve prediction accuracy.
- **Interactive Soil Type Visualization**: Visual representation of different soil types in Maharashtra.
- **Region-Based Recommendations**: Customized suggestions based on five main agricultural regions of Maharashtra.

## Requirements

- Python 3.7+
- Flask
- Pandas
- Scikit-learn
- Requests

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Access the application at http://127.0.0.1:5000/

## Usage

1. **Auto-Detection**: Click "Detect My Location" to automatically fill environmental parameters.
2. **Manual Input**: Alternatively, select crop, region, season, and soil type manually.
3. **Adjust Parameters**: Use sliders to set temperature, soil moisture, and pH levels.
4. **Get Predictions**: Click "Get Predictions" to receive recommendations for seed parameters.
5. **Review Results**: View the predicted seed size, sowing depth, and spacing, along with soil information.

## Regions of Maharashtra

The application covers five main agricultural regions of Maharashtra:

- **Vidarbha**: Characterized by black soil, suitable for cotton and soybean.
- **Marathwada**: Known for black soil, ideal for jowar and pulses.
- **Western Maharashtra**: Features red soil, good for rice and jowar.
- **Konkan**: Has laterite soil, excellent for rice and mango cultivation.
- **North Maharashtra**: Contains medium black soil, suitable for cotton and bajra.

## Soil Types

The application includes data and visual representations for:

- Black Soil (Regur)
- Red Soil
- Laterite Soil
- Medium Black Soil
- Alluvial Soil

## Weather Integration

The application uses the OpenWeatherMap API to fetch current weather data for your location, which helps in:

- Setting accurate temperature values
- Estimating soil moisture based on recent precipitation
- Suggesting appropriate crops for current conditions

## Data Privacy

This application only uses location data to provide better agricultural recommendations. No personal data is stored or shared with third parties.

