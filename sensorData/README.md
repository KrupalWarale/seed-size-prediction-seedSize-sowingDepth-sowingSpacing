# Smart Plant Monitor Tool

A Python script to read data once from a Smart Plant Monitor system at http://192.168.1.14/.

## Setup

Install required dependencies:
```
pip install -r requirements.txt
```

## Usage

Run the script:
```
python plant_monitor.py
```

The script will:
1. Connect to the plant monitor
2. Read the current sensor data
3. Save data to CSV and JSON formats (overwriting any existing files)
4. Display the readings in the console

## Monitored Data

- Temperature (°C)
- Humidity (%)
- Soil Moisture (0-255)
- Motion Detection (YES/NO)
- Pump State (ON/OFF)

## Output Files

- `plant_data.csv`: CSV file with the latest sensor reading
- `plant_data.json`: JSON file with the latest sensor reading

## Configuration

You can modify these settings in the script:
- `URL`: The address of the plant monitor
- `CSV_FILE`: Name of the CSV output file
- `JSON_FILE`: Name of the JSON output file 