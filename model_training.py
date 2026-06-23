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



    # Determine how many months of data each zipcode has
    monthly_data["Months_Of_History"] = monthly_data.groupby("Zip_Code").cumcount()

    # Create Features

    # Previous month
    monthly_data["Previous_Month_Registrations"] = monthly_data.groupby(
        "Zip_Code"
    )["Total_EV_Registrations"].shift(1)

    # Current Month in Previous year
    monthly_data["Current_Month_Previous_Year"] = monthly_data.groupby(
        "Zip_Code"
    )["Total_EV_Registrations"].shift(12)


    # 3 Previous Months AVG
    monthly_data["Three_Previous_Months_AVG"] = monthly_data.groupby(
        "Zip_Code"
    )["Total_EV_Registrations"].transform(
        lambda x: x.shift(1).rolling(window=3, min_periods=1).mean()
    )

    # 6 Previous Months AVG
    monthly_data["Six_Previous_Months_AVG"] = monthly_data.groupby(
        "Zip_Code"
    )["Total_EV_Registrations"].transform(
        lambda x: x.shift(1).rolling(window=6, min_periods=1).mean()
    )

    # 12 Previous Months AVG
    monthly_data["Twelve_Previous_Months_AVG"] = monthly_data.groupby(
        "Zip_Code"
    )["Total_EV_Registrations"].transform(
        lambda x: x.shift(1).rolling(window=12, min_periods=1).mean()
    )

    # If any previous data does not exist for  a feature, add a 0
    previous_registration_columns = [
        "Previous_Month_Registrations",
        "Current_Month_Previous_Year",
        "Three_Previous_Months_AVG",
        "Six_Previous_Months_AVG",
        "Twelve_Previous_Months_AVG"
    ]

    monthly_data[previous_registration_columns] = monthly_data[
        previous_registration_columns
    ].fillna(0)


    # Define Target
    target = "Total_EV_Registrations"

    # Define Feature Columns
    feature_columns = [
        "Zip_Code",
        "City",
        "County",
        "Year",
        "Month",
        "Months_Since_Start",
        "Months_Of_History",
        "Previous_Month_Registrations",
        "Current_Month_Previous_Year",
        "Three_Previous_Months_AVG",
        "Six_Previous_Months_AVG",
        "Twelve_Previous_Months_AVG"
    ]
    #  Define X and y

    X = monthly_data[feature_columns]
    y = monthly_data[target]


    # Define training and testing datasets - Oldest 80% for training/ newest 20% for testing
    cutoff_date = monthly_data["Month_Registered"].quantile(0.8)

    train_rows = monthly_data["Month_Registered"] <= cutoff_date
    test_rows = monthly_data["Month_Registered"] > cutoff_date

    X_train = X[train_rows]
    X_test = X[test_rows]
    y_train = y[train_rows]
    y_test = y[test_rows]

    # Display count of rows in Training Data and count of rows in Testing Data
    print("Training Rows:", len(X_train))
    print("Testing Rows:", len(X_test))

    # Define categorical and numeric features
    categorical_features = ["Zip_Code", "City", "County"]

    numeric_features = [
        "Year",
        "Month",
        "Months_Since_Start",
        "Months_Of_History",
        "Previous_Month_Registrations",
        "Current_Month_Previous_Year",
        "Three_Previous_Months_AVG",
        "Six_Previous_Months_AVG",
        "Twelve_Previous_Months_AVG"
    ]

    # Encode Categorical Features
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("numeric", "passthrough", numeric_features)
        ]
    )

    # Create Random Forest Regressor model pipeline
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", RandomForestRegressor(
                    n_estimators=100,
                    max_depth=15,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
              ))
        ]
    )
    # Display Status
    print("Training Started")

    # Train the model
    model.fit(X_train, y_train)

    # Display Status
    print("Training Complete")

    # Display Status
    print("Predictions Started")

    # Make predictions on the testing data
    predictions = model.predict(X_test)

    # Display Status
    print("Predictions Complete")

    print("Random Forest Regressor training complete.")

    # Evaluate model
    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    print("Model Evaluation Results")
    print("Mean Absolute Error:", round(mae, 2))
    print("Root Mean Squared Error:", round(rmse, 2))
    print("R-squared Score:", round(r2, 4))

    # Save predictions/results
    results = monthly_data.loc[
        test_rows,
        ["Month_Registered", "Zip_Code", "City", "County", "Total_EV_Registrations"]
    ].copy()

    results = results.rename(
        columns={"Total_EV_Registrations": "Actual_EV_Registrations"}
    )

    results["Predicted_EV_Registrations"] = predictions.round(0).astype(int)

    os.makedirs("results/tables", exist_ok=True)

    results.to_csv(
        "results/tables/model_test_predictions.csv",
        index=False
    )

    print("Model test predictions saved to results/tables/model_test_predictions.csv")

    return model



if __name__ == "__main__": train_ev_registration_model()
