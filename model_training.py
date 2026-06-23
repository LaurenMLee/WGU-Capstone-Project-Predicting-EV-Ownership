import pandas as pd
import os
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

def train_ev_registration_model():
    # Load cleaned registration data (monthlyregistrations_clean.csv)
    monthly_data = pd.read_csv("data/processed_data/monthlyregistrations_clean.csv", dtype={"Zip_Code": str})

    # Print Start Message
    print("Model Training Started")
    print("Rows loaded: ", len(monthly_data))


    # Provide dates
    monthly_data["Month_Registered"] = pd.to_datetime(
        monthly_data["Month_Registered"]
    )

    # Sort data
    monthly_data = monthly_data.sort_values(["Zip_Code", "Month_Registered"])

    # Create date-based features
    monthly_data["Year"] = monthly_data["Month_Registered"].dt.year
    monthly_data["Month"] = monthly_data["Month_Registered"].dt.month

    # Create time index to calculate time from start of data range
    monthly_data["Months_Since_Start"] = (
    (monthly_data["Year"] - monthly_data["Year"].min()) * 12 + monthly_data["Month"])

    # Prepare X features and y target

    # Determine how many months of data each zipcode has
    monthly_data["Months_Of_History"] = monthly_data.groupby("Zip_Code").cumcount()
    # Previous month

    # Current Month in Previous year

    # 3 Previous Months AVG

    # 6 Previous Months AVG

    # 12 Previous Months AVG







    # Train Random Forest Regressor

    # Evaluate model

    # Save predictions/results