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



    # Count the no of months of data each zipcode has
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



    # Create current/latest prediction results from the testing data
    current_results = monthly_data.loc[
        test_rows,
        ["Month_Registered", "Zip_Code", "City", "County", "Total_EV_Registrations"]
    ].copy()

    current_results = current_results.rename(
        columns={"Total_EV_Registrations": "Current_Actual_EV_Registrations"}
    )

    current_results["Current_Predicted_EV_Registrations"] = (
        predictions.round(0).astype(int)
    )

    # Keep most current prediction for each ZIP code
    current_results = current_results.sort_values(
        ["Zip_Code", "Month_Registered"]
    ).groupby("Zip_Code").tail(1).copy()

    current_results = current_results.rename(
        columns={"Month_Registered": "Current_Prediction_Month"}
    )

    # Create future predictions for 1 year, 3 years, and 5 years
    future_months = 60

    future_months_to_save = {
        12: "Predicted_EV_Registrations_1_Year",
        36: "Predicted_EV_Registrations_3_Years",
        60: "Predicted_EV_Registrations_5_Years"
    }

    current_data = monthly_data.copy()

    current_results["Predicted_EV_Registrations_1_Year"] = np.nan
    current_results["Predicted_EV_Registrations_3_Years"] = np.nan
    current_results["Predicted_EV_Registrations_5_Years"] = np.nan


    for month_number in range(1, future_months + 1):

        # Get the most recent row for each ZIP code
        future_data = current_data.sort_values(
            ["Zip_Code", "Month_Registered"]
        ).groupby("Zip_Code").tail(1).copy()

        # Move each ZIP code forward by one month
        future_data["Month_Registered"] = (
            future_data["Month_Registered"] + pd.DateOffset(months=1)
        ) + pd.offsets.MonthEnd(0)

        # Update date-based features
        future_data["Year"] = future_data["Month_Registered"].dt.year
        future_data["Month"] = future_data["Month_Registered"].dt.month

        future_data["Months_Since_Start"] = (
            (future_data["Year"] - monthly_data["Year"].min()) * 12
            + future_data["Month"]
        )

        future_data["Months_Of_History"] = future_data["Months_Of_History"] + 1

        # Previous month
        future_data["Previous_Month_Registrations"] = future_data[
            "Total_EV_Registrations"
        ]

        # Current Month in Previous year
        future_data["Current_Month_Previous_Year"] = future_data.apply(
            lambda row: current_data[
                (current_data["Zip_Code"] == row["Zip_Code"])
                & (current_data["Year"] == row["Year"] - 1)
                & (current_data["Month"] == row["Month"])
            ]["Total_EV_Registrations"].sum(),
            axis=1
        )

        # 3 Previous Months AVG
        future_data["Three_Previous_Months_AVG"] = future_data["Zip_Code"].apply(
            lambda zip_code: current_data[current_data["Zip_Code"] == zip_code]
            .sort_values("Month_Registered")
            .tail(3)["Total_EV_Registrations"]
            .mean()
        )

        # 6 Previous Months AVG
        future_data["Six_Previous_Months_AVG"] = future_data["Zip_Code"].apply(
            lambda zip_code: current_data[current_data["Zip_Code"] == zip_code]
            .sort_values("Month_Registered")
            .tail(6)["Total_EV_Registrations"]
            .mean()
        )

        # 12 Previous Months AVG
        future_data["Twelve_Previous_Months_AVG"] = future_data["Zip_Code"].apply(
            lambda zip_code: current_data[current_data["Zip_Code"] == zip_code]
            .sort_values("Month_Registered")
            .tail(12)["Total_EV_Registrations"]
            .mean()
        )

        # Make future predictions
        X_future = future_data[feature_columns]
        future_predictions = model.predict(X_future)

        future_data["Predicted_EV_Registrations"] = (
            future_predictions.round(0).astype(int)
        )

        # Save the 1-year, 3-year, and 5-year predictions
        if month_number in future_months_to_save:
            column_name = future_months_to_save[month_number]

            future_prediction_lookup = future_data.set_index("Zip_Code")[
                "Predicted_EV_Registrations"
            ]

            current_results[column_name] = current_results["Zip_Code"].map(
                future_prediction_lookup
            )

            print(column_name, "saved")

        # Use predicted value as the registration value for the next future month
        future_data["Total_EV_Registrations"] = future_data[
            "Predicted_EV_Registrations"
        ]

        # Add this future month to the data so the next future month can use it
        current_data = pd.concat(
            [current_data, future_data],
            ignore_index=True
        )

        # Arrange final column order
        final_predictions = current_results[
            [
                "Zip_Code",
                "City",
                "County",
                "Current_Prediction_Month",
                "Current_Actual_EV_Registrations",
                "Current_Predicted_EV_Registrations",
                "Predicted_EV_Registrations_1_Year",
                "Predicted_EV_Registrations_3_Years",
                "Predicted_EV_Registrations_5_Years"
            ]
        ]

        os.makedirs("results/tables", exist_ok=True)

        final_predictions.to_csv(
            "results/tables/ev_registration_predictions.csv",
            index=False
        )

        print("EV registration predictions saved to results/tables/ev_registration_predictions.csv")

        return model



if __name__ == "__main__": train_ev_registration_model()
