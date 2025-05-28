#!/usr/bin/env python3
import requests
import re
import json
import os
import csv
from datetime import datetime

# Configuration (can be modified as needed)
URL = "http://192.168.14.162/"
CSV_FILE = "plant_data.csv"
JSON_FILE = "plant_data.json"

def fetch_and_parse_data():
    """Fetch and parse data from the Smart Plant Monitor website"""
    try:
        # Fetch data
        print(f"Connecting to {URL}...")
        response = requests.get(URL, timeout=10)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return None
            
        html_content = response.text
        print("Data received successfully.")
        
        # Extract data using regex
        patterns = {
            'temperature': r'<b>Temperature:</b>\s*([\d.]+)',
            'humidity': r'<b>Humidity:</b>\s*([\d.]+)',
            'soil_moisture': r'<b>Soil Moisture:</b>\s*(\d+)',
            'motion_detected': r'<b>Motion Detected:</b>\s*(\w+)',
            'pump_state': r'<b>Pump State:</b>\s*(\w+)'
        }
        
        data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Extract each value
        for key, pattern in patterns.items():
            match = re.search(pattern, html_content)
            if match:
                value = match.group(1)
                # Convert to appropriate type
                if key in ['temperature', 'humidity']:
                    data[key] = float(value)
                elif key == 'soil_moisture':
                    # Store raw soil moisture sensor value (0-255 range)
                    # Note: For prediction, this needs to be converted to 0-100% in the frontend
                    data[key] = int(value)
                else:
                    data[key] = value
            else:
                data[key] = None
                
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None

def save_data(data):
    """Save data to both CSV and JSON files (overwriting existing files)"""
    # Save to CSV (overwriting mode)
    with open(CSV_FILE, 'w', newline='') as csvfile:
        fieldnames = ["timestamp", "temperature", "humidity", "soil_moisture", "motion_detected", "pump_state"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(data)
    print(f"Data saved to {CSV_FILE}")
    
    # Save to JSON (overwriting mode)
    with open(JSON_FILE, 'w') as jsonfile:
        json.dump([data], jsonfile, indent=2)
    print(f"Data saved to {JSON_FILE}")

def display_data(data):
    """Display the current plant data"""
    print("\n==== Smart Plant Monitor Data ====")
    print(f"Time: {data['timestamp']}")
    print(f"Temperature: {data['temperature']}°C")
    print(f"Humidity: {data['humidity']}%")
    print(f"Soil Moisture: {data['soil_moisture']} (0-255)")
    print(f"Motion Detected: {data['motion_detected']}")
    print(f"Pump State: {data['pump_state']}")
    print("================================")

def main():
    """Main function to read plant data once"""
    print("Starting Smart Plant Monitor Single Read")
    
    # Fetch and parse data
    data = fetch_and_parse_data()
    
    if data:
        display_data(data)
        save_data(data)
        print("Process complete.")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    main() 