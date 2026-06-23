import pandas as pd


def clean_charging_stations_data():

    # Load dataset
    charging_station_data = pd.read_csv("data/raw_data/chargingstations_raw.csv",
    dtype={"ZipCode": str})

    # Cleanup column names
    charging_station_data.columns = charging_station_data.columns.str.strip()

    # Display starting number of rows
    print("Starting Rows:", len(charging_station_data))

    # Rename Zip code column to match other files
    charging_station_data = charging_station_data.rename(columns={"ZipCode": "Zip_Code"})

    # Remove rows with missing values in relevant columns
    charging_station_data = charging_station_data.dropna(
        subset=["Zip_Code", "Program", "Access"]
    )


    # Format Zip Codes to match other tables- Format as strings, remove extra spaces and ensure all are 5 digits
    charging_station_data["Zip_Code"] = (charging_station_data["Zip_Code"]
        .astype(str)
        .str.strip()
        .str.zfill(5)

        )
    # Display starting number of rows
    print("Rows after removing missing values:", len(charging_station_data))

    # Define which programs to include from dataset
    relevant_location_types =  ["Electric Vehicle Charging Stations", "Electric Vehicle Infrastructure Program (EVIP)", "Electric Vehicle Supply Equipment Tax Credit Program"
    ]
    # Filter to only relevant programs
    charging_station_data = charging_station_data[charging_station_data["Program"].isin(relevant_location_types)]

    # Display rows after filtering to only relevant locations
    print("Rows after Relevant Program filtering:", len(charging_station_data))

    # Filter to only publicly accessible locations
    charging_station_data = charging_station_data[charging_station_data["Access"].str.contains ("public", case=False, na=False)
    ]

    # Display rows after filtering to only relevant locations
    print("Rows after Publicly Accessible filtering:", len(charging_station_data))

    # Save new file
    charging_station_data.to_csv("data/processed_data/chargingstations_clean.csv", index=False)

    # Display Results
    print("Charging Station Data Cleaning Complete")
    print("Rows after cleaning completion:", len(charging_station_data))

    return charging_station_data

if __name__ == "__main__":
   clean_charging_stations_data()
