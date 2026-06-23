from data_cleaning_zipcode_xwalk import clean_zipcode_data
from data_cleaning_monthly_registrations import clean_monthly_registrations_data
from data_cleaning_charging_stations import clean_charging_stations_data


def main():
    print("Starting EV analysis pipeline...")

    print("\nCleaning ZIP code mapping data...")
    clean_zipcode_data()

    print("\nCleaning monthly registration data...")
    clean_monthly_registrations_data()

    print("\nCleaning charging station data...")
    clean_charging_stations_data()

    print("\nData cleaning pipeline complete.")


if __name__ == "__main__":
    main()