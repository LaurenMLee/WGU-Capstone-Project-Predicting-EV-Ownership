# Compares the predictions from the model to the charging station data to rank Zip Codes by highest need

import pandas as pd
import os

def compare_predictions_to_availability():

# Load predictions
predictions = pd.read_csv(
    "results/tables/model_test_predictions.csv",
    dtype={"Zip_Code": str}
)

# Display Status
print("Prediction rows loaded:", len(predictions))
print("Charging station rows loaded:", len(charging_stations))

# Load charging station data
charging_stations = pd.read_csv(
"data/processed_data/chargingstations_clean.csv",
    dtype={"Zip_Code": str}
    )

# Define dates to compare

predictions["Month_Registered"] = pd.to_datetime(
    predictions["Month_Registered"]
)

latest_month = predictions["Month_Registered"].max()

latest_predictions = predictions[
    predictions["Month_Registered"] == latest_month
    ].copy()

print("Latest prediction month:", latest_month)
    print("Rows in latest prediction month:", len(latest_predictions))


# Count charging stations in each Zip Code

# Declare which predictions to use

# Calculate the need score
