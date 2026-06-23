import pandas as pd

def clean_monthly_registrations_data():

    # Load monthly registration data
    monthly_registration_data = pd.read_csv("data/raw_data/monthlyregistrations_raw.csv",
    dtype={"Zip_Code": str})

    # Display starting rows
    print("Starting Rows:", len(monthly_registration_data))

    # Cleanup column names to remove empty spaces at front or end of string'
    monthly_registration_data.columns = monthly_registration_data.columns.str.strip()

    # Remove rows with missing values
    monthly_registration_data = monthly_registration_data.dropna(
        subset=["Year_Month","Fuel_Category","Zip_Code", "Count"]
    )

    # Format Zip Codes to match other tables Format as strings, remove extra spaces and ensure all are 5 digits
    monthly_registration_data["Zip_Code"] = (monthly_registration_data["Zip_Code"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
    )

    # Cleanup values in fuel category column to remove differentiation between Plug-In and Plug-in to normalize the data.

    monthly_registration_data["Fuel_Category"] = monthly_registration_data["Fuel_Category"].replace({
    "Plug-in Hybrid" : "Plug-In Hybrid"})

    # Combine total EV counts by month/year and zipcode into new column called Total_EV_Registrations

    monthly_registration_data = monthly_registration_data.groupby(
        ["Year_Month", "Zip_Code"],
        as_index=False
    )["Count"].sum()

    monthly_registration_data = monthly_registration_data.rename(
        columns={"Count": "Total_EV_Registrations"}
)
    # Display count after combining Full Electric and Plug In Hybrid registrations
    print("Rows after combining fuel categories", len(monthly_registration_data))
    # Add City/ County Names to zip codes



    # Load Zip Code Mapping Crosswalk
    zip_code_mapping = pd.read_csv("data/processed_data/zipcode_mapping_clean.csv",
        dtype={"Zip_Code": str})

    monthly_registration_data = monthly_registration_data.merge(
        zip_code_mapping[["Zip_Code", "City", "County"]],
        on="Zip_Code",
        how="inner"
    )

    # Save Data

    monthly_registration_data.to_csv("data/processed_data/monthlyregistrations_clean.csv", index=False)

    # Display Results
    print("Monthly Registration Cleaning Complete")
    print("Rows after cleaning completion:", len(monthly_registration_data))

    return monthly_registration_data

if __name__ == "__main__":
        clean_monthly_registrations_data()

