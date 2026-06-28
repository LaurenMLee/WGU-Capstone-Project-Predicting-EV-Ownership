# Compares the predictions from the model to the charging station data to rank Zip Codes by highest need

import pandas as pd
import os

def compare_predictions_to_availability():

    # Load predictions
    predictions = pd.read_csv(
        "results/tables/ev_registration_predictions.csv",
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


    # Count charging stations in each Zip Code
    charging_station_counts = charging_stations.groupby(
    "Zip_Code",
    as_index=False
    ).size()

    charging_station_counts = charging_station_counts.rename(
        columns={"size": "Charging_Station_Count"}
    )

    # Combine predictions with charging station counts
    comparison = predictions.merge(
    charging_station_counts,
    on = "Zip_Code",
    how = "left"
    )
    # If a ZIP code has no charging stations, fill missing count with 0
    comparison["Charging_Station_Count"] = (
    comparison["Charging_Station_Count"]
    .fillna(0)
    .astype(int)
    )

    # Create need scores for current, 1-year, 3-year, and 5-year predictions
    comparison["Current_Need_Score"] = (
    comparison["Current_Predicted_EV_Registrations"]
    / (comparison["Charging_Station_Count"] + 1)
    )

    comparison["Need_Score_1_Year"] = (
    comparison["Predicted_EV_Registrations_1_Year"]
    / (comparison["Charging_Station_Count"] + 1)
    )

    comparison["Need_Score_3_Years"] = (
    comparison["Predicted_EV_Registrations_3_Years"]
    / (comparison["Charging_Station_Count"] + 1)
    )

    comparison["Need_Score_5_Years"] = (
    comparison["Predicted_EV_Registrations_5_Years"]
    / (comparison["Charging_Station_Count"] + 1)
    )

    # Round Need Scores
    comparison["Current_Need_Score"] = comparison["Current_Need_Score"].round(1)
    comparison["Need_Score_1_Year"] = comparison["Need_Score_1_Year"].round(1)
    comparison["Need_Score_3_Years"] = comparison["Need_Score_3_Years"].round(1)
    comparison["Need_Score_5_Years"] = comparison["Need_Score_5_Years"].round(1)

    # Sort by highest 5-year need score
    comparison = comparison.sort_values(
    "Need_Score_5_Years",
    ascending = False
    ).reset_index(drop=True)

    # Display top 20 zip codes with highest current need
    top_20_current = comparison.sort_values(
        "Current_Need_Score",
        ascending=False
    ).head(20)

    print("\nTop 20 ZIP codes by CURRENT charging need score:")
    print(
        top_20_current[
            [
                "Zip_Code",
                "City",
                "County",
                "Current_Predicted_EV_Registrations",
                "Charging_Station_Count",
                "Current_Need_Score"
            ]
        ].to_string(index=False)
    )

    # Display top 20 zip codes with highest 1-year need
    top_20_1_year = comparison.sort_values(
        "Need_Score_1_Year",
        ascending=False
    ).head(20)

    print("\nTop 20 ZIP codes by 1-YEAR charging need score:")
    print(
        top_20_1_year[
            [
                "Zip_Code",
                "City",
                "County",
                "Predicted_EV_Registrations_1_Year",
                "Charging_Station_Count",
                "Need_Score_1_Year"
            ]
        ].to_string(index=False)
    )

    # Display top 20 zip codes with highest 3-year need
    top_20_3_years = comparison.sort_values(
        "Need_Score_3_Years",
        ascending=False
    ).head(20)

    print("\nTop 20 ZIP codes by 3-YEAR charging need score:")
    print(
        top_20_3_years[
            [
                "Zip_Code",
                "City",
                "County",
                "Predicted_EV_Registrations_3_Years",
                "Charging_Station_Count",
                "Need_Score_3_Years"
            ]
        ].to_string(index=False)
    )

    # Display top 20 zip codes with highest 5-year need
    top_20_5_years = comparison.sort_values(
        "Need_Score_5_Years",
        ascending=False
    ).head(20)

    print("\nTop 20 ZIP codes by 5-YEAR charging need score:")
    print(
        top_20_5_years[
            [
                "Zip_Code",
                "City",
                "County",
                "Predicted_EV_Registrations_5_Years",
                "Charging_Station_Count",
                "Need_Score_5_Years"
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
