# Importing the necessary libraries
import pandas as pd  # Helps in handling and reading data (like from Excel)
import numpy as np  # Helps with numbers and math functions
import pickle  # Used to save and load models
from sklearn.model_selection import train_test_split  # Used to split data into training and testing sets
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier  # Machine learning models
from sklearn.preprocessing import LabelEncoder  # Converts text data into numbers
from sklearn.metrics import mean_squared_error, classification_report, accuracy_score  # To check how good our model is
from sklearn.pipeline import Pipeline  # Not used here, but helpful for combining steps together

# Load the Excel file into a DataFrame
df = pd.read_excel('Maharashtra_Agriculture_Realistic.xlsx')

# Pick the input columns (features) and the outputs we want to predict (targets)
X = df[['Crop Name', 'Region', 'Season', 'Temperature (°C)', 'Moisture (%)', 'Soil Type', 'Soil pH']]
y_seed_size = df['Seed Size Category']  # This is what we want to classify (like Small, Medium, Large)
y_sowing_depth = df['Sowing Depth (cm)']  # This is a number we want to predict
y_spacing = df['Spacing Between Seeds (cm)']  # Another number to predict

# Convert text values in some columns into numbers (since models only understand numbers)
label_encoders = {}
for column in ['Crop Name', 'Region', 'Season', 'Soil Type']:
    le = LabelEncoder()
    X[column] = le.fit_transform(X[column])  # Replace text with numbers
    label_encoders[column] = le  # Save the encoder so we can convert back later if needed

# Do the same for the "Seed Size Category" column
le_seed_size = LabelEncoder()
y_seed_size_encoded = le_seed_size.fit_transform(y_seed_size)
label_encoders['Seed Size Category'] = le_seed_size  # Save this encoder too

# Split the data into training and testing sets (80% train, 20% test)
X_train, X_test, y_seed_size_train, y_seed_size_test, y_depth_train, y_depth_test, y_spacing_train, y_spacing_test = train_test_split(
    X, y_seed_size_encoded, y_sowing_depth, y_spacing, test_size=0.2, random_state=42
)

# Create and train the models

# 1. Classification model to predict seed size category
seed_size_model = RandomForestClassifier(n_estimators=100, random_state=42)
seed_size_model.fit(X_train, y_seed_size_train)

# 2. Regression model to predict how deep to sow the seeds
sowing_depth_model = RandomForestRegressor(n_estimators=100, random_state=42)
sowing_depth_model.fit(X_train, y_depth_train)

# 3. Regression model to predict how much space to keep between seeds
spacing_model = RandomForestRegressor(n_estimators=100, random_state=42)
spacing_model.fit(X_train, y_spacing_train)

# Test the models and check their performance

# Test seed size model and show accuracy
y_seed_size_pred = seed_size_model.predict(X_test)
seed_size_accuracy = accuracy_score(y_seed_size_test, y_seed_size_pred)
print(f"Seed Size Classification Accuracy: {seed_size_accuracy:.4f}")
print("Classification Report for Seed Size:")
print(classification_report(y_seed_size_test, y_seed_size_pred))

# Test sowing depth model and show error (lower is better)
y_depth_pred = sowing_depth_model.predict(X_test)
depth_rmse = np.sqrt(mean_squared_error(y_depth_test, y_depth_pred))
print(f"Sowing Depth RMSE: {depth_rmse:.4f} cm")

# Test spacing model and show error (lower is better)
y_spacing_pred = spacing_model.predict(X_test)
spacing_rmse = np.sqrt(mean_squared_error(y_spacing_test, y_spacing_pred))
print(f"Spacing RMSE: {spacing_rmse:.4f} cm")

# Show which features were most important for each model
print("\nFeature importance for Seed Size prediction:")
for feature, importance in zip(X.columns, seed_size_model.feature_importances_):
    print(f"{feature}: {importance:.4f}")

print("\nFeature importance for Sowing Depth prediction:")
for feature, importance in zip(X.columns, sowing_depth_model.feature_importances_):
    print(f"{feature}: {importance:.4f}")

print("\nFeature importance for Spacing prediction:")
for feature, importance in zip(X.columns, spacing_model.feature_importances_):
    print(f"{feature}: {importance:.4f}")

# Save the trained models and label encoders to a file so we can use them later without retraining
models = {
    'seed_size_model': seed_size_model,
    'sowing_depth_model': sowing_depth_model,
    'spacing_model': spacing_model,
    'label_encoders': label_encoders
}

with open('agricultural_models.pkl', 'wb') as f:
    pickle.dump(models, f)

print("\nModels saved to 'agricultural_models.pkl'")

# Get the unique values of the text columns so we can show them as options in a web app dropdown
unique_values = {
    'Crop Name': df['Crop Name'].unique().tolist(),
    'Region': df['Region'].unique().tolist(),
    'Season': df['Season'].unique().tolist(),
    'Soil Type': df['Soil Type'].unique().tolist()
}

# Save these unique values for use in the web app
with open('unique_values.pkl', 'wb') as f:
    pickle.dump(unique_values, f)

print("Unique values saved to 'unique_values.pkl'")
