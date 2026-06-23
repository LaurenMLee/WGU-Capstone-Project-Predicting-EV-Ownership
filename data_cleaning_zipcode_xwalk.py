import pandas as pd

def clean_zipcode_data():
    # Load raw data
    zip_code_mapping= pd.read_csv("data/raw_data/Zip_Code_Lookup_Table_raw.csv",
    dtype={"Zip Code": str})

    # Display starting rows
    print("Starting Rows:", len(zip_code_mapping))

    # Cleanup column names
    zip_code_mapping.columns = zip_code_mapping.columns.str.strip()

    # Rename Zip code column to match other files
    zip_code_mapping = zip_code_mapping.rename(columns={"Zip Code": "Zip_Code"})

    # Remove rows with missing values
    zip_code_mapping = zip_code_mapping.dropna(subset=["Zip_Code", "City", "County"]
    )

    # Display rows after removing missing values
    print("Rows after removing missing values:", len(zip_code_mapping))

    # Format Zip Codes to match other tables- Format as strings, remove extra spaces and ensure all are 5 digits
    zip_code_mapping["Zip_Code"] = (zip_code_mapping["Zip_Code"]
        .astype(str)
        .str.strip()
        .str.zfill(5)
        )

    # Remove duplicate zip codes
    zip_code_mapping = zip_code_mapping.drop_duplicates(subset=["Zip_Code"])

    # Display  rows after removing duplicate zip codes
    print("Rows after duplicates removed:", len(zip_code_mapping))

    # Save cleaned data
    zip_code_mapping.to_csv(
        "data/processed_data/zipcode_mapping_clean.csv",
        index=False
    )


    # Display Results
    print("Zip Code Mapping Cleaning Complete")
    print("Rows after cleaning completion:", len(zip_code_mapping))
    return zip_code_mapping

if __name__ == "__main__":
    clean_zipcode_data()