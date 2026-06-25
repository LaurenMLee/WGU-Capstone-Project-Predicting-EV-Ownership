# Compares the predictions from the model to the charging station data to rank Zip Codes by highest need

import pandas as pd
import os

def compare_predictions_to_availability():

    # Load predictions
    predictions = pd.read_csv(
    "results/tables/model_test_predictions.csv",
    dtype={"Zip_Code": str}
)

    # Load charging station data
    charging_stations = pd.read_csv(
"data/processed_data/chargingstations_clean.csv",
    dtype={"Zip_Code": str}
    )

    # Display Status
    print("Prediction rows loaded:", len(predictions))
    print("Charging station rows loaded:", len(charging_stations))

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
    charging_station_counts = charging_stations.groupby(
    "Zip_Code",
    as_index=False
    ).size()

    charging_station_counts = charging_station_counts.rename(
        columns={"size": "Charging_Station_Count"}
    )

    # Combine predictions with charging station counts
    comparison = latest_predictions.merge(
    charging_station_counts,
    on="Zip_Code",
    how="left"
    )

    # If a ZIP code has no charging stations, fill missing count with 0
    comparison["Charging_Station_Count"] = (
    comparison["Charging_Station_Count"]
    .fillna(0)
    .astype(int)
    )

    # Create need score
    comparison["Need_Score"] = (
        comparison["Predicted_EV_Registrations"]
        / (comparison["Charging_Station_Count"] + 1)
    )

    # Round Need Score
    comparison["Need_Score"] = comparison["Need_Score"].round(1)

    # Sort by highest need score
    comparison = comparison.sort_values(
        "Need_Score",
        ascending=False
    ).reset_index(drop=True)

    # Display top 20 zip codes with highest need

    top_20_zipcodes = comparison.head(20)

    print("\nTop 20 ZIP codes by charging need score:")
    print(
        top_20_zipcodes[
            [
                "Zip_Code",
                "City",
                "County",
                "Predicted_EV_Registrations",
                "Charging_Station_Count",
                "Need_Score"
            ]
        ].to_string(index=False)
    )

    # Save results
    os.makedirs("results/tables", exist_ok=True)

    comparison.to_csv(
        "results/tables/ev_charging_need_comparison.csv",
        index=False
        )

    print("EV charging need comparison saved to results/tables/ev_charging_need_comparison.csv")

    return comparison


if __name__ == "__main__":
    compare_predictions_to_availability()
