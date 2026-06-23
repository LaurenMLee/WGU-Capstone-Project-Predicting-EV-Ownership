import pandas as pd

def clean_monthly_registrations_data():

    # Load monthly registration data
    monthly_registration_data = pd.read_csv("data/raw_data/monthlyregistrations_raw.csv",
    dtype={"Zip_Code": str})

    # Display starting rows
    print("Starting Rows:", len(monthly_registration_data))

    # Cleanup column names to remove empty spaces at front or end of string'
    monthly_registration_data.columns = monthly_registration_data.columns.str.strip()

    # Remove rows with missing values in date/fuel category or zip code columns
    monthly_registration_data = monthly_registration_data.dropna(
        subset=["Year_Month","Fuel_Category","Zip_Code"]
    )

    # Display  rows after deleting rows with missing values
    print("Rows after missing values removed:", len(monthly_registration_data))

    # Format Zip Codes to match other tables Format as strings, remove extra spaces and ensure all are 5 digits
    monthly_registration_data["Zip_Code"] = (monthly_registration_data["Zip_Code"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )
    # Rename Year_Month to Month_Registered
    monthly_registration_data = monthly_registration_data.rename(
        columns={"Year_Month": "Month_Registered"}
    )
    # Cleanup values in fuel category column to remove differentiation between Plug-In and Plug-in to normalize the data.

    monthly_registration_data["Fuel_Category"] = monthly_registration_data["Fuel_Category"].replace({
    "Plug-in Hybrid" : "Plug-In Hybrid"})

    # Convert Month_Registered to full date using the last day of the month
    monthly_registration_data["Month_Registered"] = (
            pd.to_datetime(monthly_registration_data["Month_Registered"], format="%Y/%m")
            + pd.offsets.MonthEnd(0)
    )


    # Combine total EV counts by month/year and zipcode into new column called Total_EV_Registrations

    monthly_registration_data = monthly_registration_data.groupby(
        ["Month_Registered", "Zip_Code"],
        as_index=False
    )["Count"].sum()

    monthly_registration_data = monthly_registration_data.rename(
        columns={"Count": "Total_EV_Registrations"}
)
    # Display count after combining Full Electric and Plug In Hybrid registrations
    print("Rows after combining fuel categories", len(monthly_registration_data))




    # Load Zip Code Mapping Crosswalk to add City/County Names and to serve as dataset for all MD Zip Codes that exist
    zip_code_mapping = pd.read_csv("data/processed_data/zipcode_mapping_clean.csv",
        dtype={"Zip_Code": str})

    # Create complete list of all months in the registration data without duplicates and sort them
    all_months = monthly_registration_data["Month_Registered"].drop_duplicates().sort_values()
    all_months = pd.DataFrame({"Month_Registered": all_months})

    print("Number of months:", len(all_months))
    print("Number of Maryland ZIP codes:", len(zip_code_mapping))

    all_zip_month_combos = all_months.merge(
        zip_code_mapping,
        how="cross"
    )
    # Display row count after adding in all MD Zip Codes
    print("Rows after creating all month/ZIP combinations:", len(all_zip_month_combos))

    # Fill in data for months where registration data exists

    monthly_registration_data = all_zip_month_combos.merge(
        monthly_registration_data[
            ["Month_Registered", "Zip_Code", "Total_EV_Registrations"]
        ],
        on=["Month_Registered", "Zip_Code"],
        how="left"
    )

    # Add 0 for all months that a zipcode has no new registrations
    monthly_registration_data["Total_EV_Registrations"] = (
        monthly_registration_data["Total_EV_Registrations"]
        .fillna(0)
        .astype(int)
    )
    # Display count of rows that have no registrations in a given month

    print(
        "Rows with 0 registrations in Month:",
        (monthly_registration_data["Total_EV_Registrations"] == 0).sum()
    )
    # Display count of rows that have at least 1 registration in a given month
    print(
        "Rows with 1 or more registrations in Month",
        (monthly_registration_data["Total_EV_Registrations"] > 0).sum()
    )
    # Arrange Column Order
    monthly_registration_data = monthly_registration_data[
        ["Month_Registered", "Zip_Code", "City", "County", "Total_EV_Registrations"]
    ]

    # Sort by date first, then zip code
    monthly_registration_data = monthly_registration_data.sort_values(
        ["Month_Registered", "Zip_Code"]
    ).reset_index(drop=True)

    # Save Data

    monthly_registration_data.to_csv("data/processed_data/monthlyregistrations_clean.csv", index=False)

    # Display Results
    print("Monthly Registration Cleaning Complete")
    print("Rows after Cleaning Completion:", len(monthly_registration_data))

    return monthly_registration_data

if __name__ == "__main__":
        clean_monthly_registrations_data()

