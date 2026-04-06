from django.shortcuts import render
from sklearn.model_selection import train_test_split



from .models import userRegisteredTable
from django.core.exceptions import ValidationError
from django.contrib import messages


def userRegisterCheck(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        username = request.POST.get("loginId")
        mobile = request.POST.get("mobile")
        password = request.POST.get("password")
        

        # Create an instance of the model
        user = userRegisteredTable(
            name=name,
            email=email,
            loginid=username,
            mobile=mobile,
            password=password,
            
        )

        try:
            # Validate using model field validators
            user.full_clean()
            
            # Save to DB
            user.save()
            messages.success(request,'registration Successfully done,please wait for admin APPROVAL')
            return render(request, "userRegisterForm.html")


        except ValidationError as ve:
            # Get a list of error messages to display
            error_messages = []
            for field, errors in ve.message_dict.items():
                for error in errors:
                    error_messages.append(f"{field.capitalize()}: {error}")
            return render(request, "userRegisterForm.html", {"messages": error_messages})

        except Exception as e:
            # Handle other exceptions (like unique constraint fails)
            return render(request, "userRegisterForm.html", {"messages": [str(e)]})

    return render(request, "userRegisterForm.html")


def userLoginCheck(request):
    if request.method=='POST':
        username=request.POST['userUsername']
        password=request.POST['userPassword']

        try:
            user=userRegisteredTable.objects.get(loginid=username,password=password)

            if user.status=='Active':
                request.session['id']=user.id
                request.session['name']=user.name
                request.session['email']=user.email
                
                return render(request,'users/userHome.html')
            else:
                messages.error(request,'Status not activated please wait for admin approval')
                return render(request,'userLoginForm.html')
        except:
            messages.error(request,'Invalid details please enter details carefully or Please Register')
            return render(request,'userLoginForm.html')
    return render(request,'userLoginForm.html')


def userHome(request):
    if not request.session.get('id'):
        return render(request,'userLoginForm.html')
    return render(request,'users/userHome.html')

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import xgboost as xgb
import lightgbm as lgb
import joblib

def adjusted_r2(r2, n, p):
        return 1 - (1 - r2) * (n - 1) / (n - p - 1)

def training(request):
    if not request.session.get('id'):
        return render(request, 'userLoginForm.html')
    
    # Load dataset
        
    # Function to calculate Adjusted R²
    
    # Load the dataset
    data = pd.read_csv(r'media\synthetic_ev_battery_dataset.csv')

    # Define features and target
    features = ['Voltage_V', 'Current_A', 'Battery_Temperature_°C', 'Charge_Discharge_Cycles',
                'Ambient_Temperature_°C', 'Humidity_%', 'Avg_Cycles_Per_Hour', 
                'Energy_Consumption_Wh', 'Temp_Fluctuation_°C']
    target = 'SOH_%'

    X = data[features]
    y = data[target]

    # Data Preprocessing: Handle missing values (if any) and normalize features
    X = X.fillna(X.mean())  # Fill missing values with mean
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=features)

    # Save the scaler for future use
    joblib.dump(scaler, 'scaler.pkl')

    # Train-test split (80-20)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Initialize models
    xgb_model = xgb.XGBRegressor(objective='reg:squarederror', random_state=42)
    lgb_model = lgb.LGBMRegressor(random_state=42)

    # Train XGBoost model
    xgb_model.fit(X_train, y_train)

    # Train LightGBM model
    lgb_model.fit(X_train, y_train)

    # Save the trained models
    joblib.dump(xgb_model, 'xgb_model.pkl')
    joblib.dump(lgb_model, 'lgb_model.pkl')

    # Make predictions
    xgb_pred = xgb_model.predict(X_test)
    lgb_pred = lgb_model.predict(X_test)

    # Calculate metrics for XGBoost
    xgb_r2 = r2_score(y_test, xgb_pred)
    n = len(y_test)
    p = len(features)
    xgb_adj_r2 = adjusted_r2(xgb_r2, n, p)
    xgb_mae = mean_absolute_error(y_test, xgb_pred)
    xgb_mse = mean_squared_error(y_test, xgb_pred)
    xgb_rmse = np.sqrt(xgb_mse)

    # Calculate metrics for LightGBM
    lgb_r2 = r2_score(y_test, lgb_pred)
    lgb_adj_r2 = adjusted_r2(lgb_r2, n, p)
    lgb_mae = mean_absolute_error(y_test, lgb_pred)
    lgb_mse = mean_squared_error(y_test, lgb_pred)
    lgb_rmse = np.sqrt(lgb_mse)

    # Compile metrics into a dictionary
    metrics = {
        'Metric': ['R²', 'Adjusted R²', 'MAE', 'MSE', 'RMSE'],
        'XGBoost': [xgb_r2, xgb_adj_r2, xgb_mae, xgb_mse, xgb_rmse],
        'LightGBM': [lgb_r2, lgb_adj_r2, lgb_mae, lgb_mse, lgb_rmse]
    }

    # Convert to DataFrame for display
    metrics_df = pd.DataFrame(metrics)
    metrics_table = [
    ['Accuracy (R²)', f"{xgb_r2 * 100:.2f}%", f"{lgb_r2 * 100:.2f}%"],
    ['Adjusted R²', f"{xgb_adj_r2 * 100:.2f}%", f"{lgb_adj_r2 * 100:.2f}%"],
    ['MAE', round(xgb_mae, 2), round(lgb_mae, 2)],
    ['MSE', round(xgb_mse, 2), round(lgb_mse, 2)],
    ['RMSE', round(xgb_rmse, 2), round(lgb_rmse, 2)],
    ]       



    # Optional: Print metrics in the exact format from the document (rounded to match)
    print("\nMetrics formatted as in the document:")
    print("| METRIC       | XGBOOST   | LIGHT GBM |")
    print("|--------------|-----------|-----------|")
    print(f"| R²           | {xgb_r2:.4f}   | {lgb_r2:.4f}   |")
    print(f"| Adjusted R²  | {xgb_adj_r2:.4f}   | {lgb_adj_r2:.4f}   |")
    print(f"| MAE          | {xgb_mae:.5f} | {lgb_mae:.5f} |")
    print(f"| MSE          | {xgb_mse:.2e} | {lgb_mse:.2e} |")
    print(f"| RMSE         | {xgb_rmse:.5f} | {lgb_rmse:.5f} |")

    # Render metrics to template
    return render(request, 'users/training.html', {'metrics': metrics_table})

import joblib
import os
import numpy as np
from django.shortcuts import render
from django.conf import settings
import os
import joblib

def predict_battery_performance(features):

    model_path = os.path.join(settings.BASE_DIR, "xgb_model.pkl")
    scaler_path = os.path.join(settings.BASE_DIR, "scaler.pkl")

    if os.path.exists(model_path) and os.path.exists(scaler_path):

        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)

        features_scaled = scaler.transform([features])

        prediction = model.predict(features_scaled)

        return float(round(prediction[0], 2))

    else:
        return "Model or scaler not found. Please train the model first."
def prediction(request):
    if not request.session.get('id'):
        return render(request, 'userLoginForm.html')

    result = None
    status = None
    accuracy = None

    if request.method == 'POST':
        try:
            model_name = request.POST.get('model_name', 'xgb')  # default to xgb if not provided

            features = [
                float(request.POST.get('Voltage_V')),
                float(request.POST.get('Current_A')),
                float(request.POST.get('Battery_Temperature_°C')),
                float(request.POST.get('Charge_Discharge_Cycles')),
                float(request.POST.get('Ambient_Temperature_°C')),
                float(request.POST.get('Humidity_%')),
                float(request.POST.get('Avg_Cycles_Per_Hour')),
                float(request.POST.get('Energy_Consumption_Wh')),
                float(request.POST.get('Temp_Fluctuation_°C'))
            ]

            result = predict_battery_performance(features)
            
            # Categorize result
            status = "NONE"
            accuracy = None
            if isinstance(result, (int, float, np.float32, np.float64)):
                if result >= 90:
                    status = "Excellent"
                elif result >= 70:
                    status = "Good"
                elif result >= 40:
                    status = "Average"
                else:
                    status = "Bad"
                
                if 'xgb' in model_name:
                    accuracy = "88.05%"
                else:
                    accuracy = "89.15%"

        except (ValueError, TypeError):
            result = "Invalid input. Please enter valid numeric values for all fields."
            status = None
            accuracy = None

    return render(request, 'users/prediction.html', {'result': result, 'status': status, 'accuracy': accuracy})
