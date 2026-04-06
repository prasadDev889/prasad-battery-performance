import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import pickle

# Load dataset
data = pd.read_csv("synthetic_ev_battery_dataset.csv")

print("Columns in dataset:", data.columns)

# Features and Target
X = data.drop("SOH_%", axis=1)
y = data["SOH_%"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train model
model = XGBRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=6
)

model.fit(X_train, y_train)

# Save model
pickle.dump(model, open("xgb_model.pkl", "wb"))

# Save scaler
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("Model Training Completed")
print("xgb_model.pkl and scaler.pkl saved successfully")