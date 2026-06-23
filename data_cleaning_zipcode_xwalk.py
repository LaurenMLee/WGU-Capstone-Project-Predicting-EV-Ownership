import pandas as pd

def clean_zipcode_data():
    # Load raw data
    zip_code_mapping= pd.read_csv("data/raw_data/Zip_Code_Lookup_Table_raw.csv")

    # Cleanup column names
    zip_code_mapping.columns = zip_code_mapping.columns.str.strip()

    # Rename Zip code column to match other files
    zip_code_mapping = zip_code_mapping.rename(columns={"Zip Code": "Zip_Code"})

    # Remove rows with missing values
    zip_code_mapping = zip_code_mapping.dropna(subset=["Zip_Code", "City", "County"]
    )

    # Remove duplicate zip codes
    zip_code_mapping = zip_code_mapping.drop_duplicates(subset=["Zip_Code"])

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