import pandas as pd 
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
import pycountry

def files_concat(uploaded_files): 
    dfs = []
    for file_obj in uploaded_files:
        delimiter = detect_delimiter(file_obj)
        df = pd.read_csv(file_obj, delimiter=delimiter)
        dfs.append(df)

        combined_df = pd.concat(dfs, ignore_index=True)
    return(combined_df)


def detect_delimiter(file_obj):
    file_obj.seek(0)  # Reset file pointer to the beginning
    sample = file_obj.read(1024).decode('utf-8')  # Read the first 1024 bytes to inspect
    file_obj.seek(0)  # Reset file pointer to the beginning again for future reads
    delimiters = [',', ';', '\t']  # Common delimiters
    counts = {delim: sample.count(delim) for delim in delimiters}
    return max(counts, key=counts.get)  # Return the most frequent delimiter


def apply_mapping(df, mapping):
    df = df.rename(columns=mapping)
    return df

# Function to apply data cleaning rules
valid_device_categories = [
    "LAPTOP", "DESKTOP", "NOTEBOOK", "SMARTPHONE", "MONITOR",
    "TABLET", "PRINTER", "SERVER", "SWITCH", "ROUTER",
    "VIRTUAL_MACHINE", "FIREWALL", "WIFI_ACCESS_POINT",
    "LOAD_BALANCER", "GENERATOR", "UNINTERRUPTED_POWER_SUPPLY",
    "REFRIGERATION_UNIT", "AIR_CONDITIONING_CABINET", "OTHER"
]

def date_check(df):
    # Define columns to check
    date_columns = ["deviceEntryDate", "devicePurchaseDate", "deviceRetirementDate"]
    
    issues = []  # List to store issue rows

    for col in date_columns:
        if col in df.columns:
            for index, value in df[col].items():
                try:
                    # Try to parse with the expected format
                    pd.to_datetime(value, format='%Y-%m-%d')
                except ValueError:
                    try:
                        # Attempt to parse with a flexible format
                        parsed_date = pd.to_datetime(value, errors='coerce')
                        if pd.notna(parsed_date):  # Check if parsing was successful
                            formatted_date = parsed_date.strftime('%Y-%m-%d')
                            issues.append({
                                "row": index,
                                "column": col, 
                                "value": value,
                                "error": "Invalid date format",
                                "suggestion": formatted_date
                            })
                        else:
                            issues.append({
                                "row": index,
                                "column": col, 
                                "value": value,
                                "error": "Invalid date format",
                                "suggestion": ""
                            })
                    except Exception as e:
                        issues.append({
                            "row": index,
                            "column": col, 
                            "value": value,
                            "error": str(e),
                            "suggestion": ""
                        })

    # Create a DataFrame from the issues list
    issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
    
    return df, issues_df


def category_check(df):
    issues = []

    # Ensure all device categories are in upper case
    df["deviceCategory"] = df["deviceCategory"].str.upper()

    for index, value in df["deviceCategory"].items():
        if value not in valid_device_categories:
            issues.append({
                "row": index,
                "column": "deviceCategory",
                "deviceCategory": value,
                "error": "Invalid device category",
                "suggestion": "Check category format"
            })

    # Create a DataFrame from the issues list
    issues_df = pd.DataFrame(issues, columns=["row", "column", "deviceCategory", "error", "suggestion"])
    
    return df, issues_df, valid_device_categories

#Get a country in the right format 
def get_country_code(location_string):
    geolocator = Nominatim(user_agent="my_agent")
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(location_string, addressdetails=True)
            if location:
                address = location.raw.get('address', {})
                country_code = address.get('country_code', '').upper()
                if country_code:
                    return country_code
                else:
                    return ""
            else:
                return ""
        except (GeocoderTimedOut, GeocoderUnavailable):
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return ""
        except Exception as e:
            return ""

def countries_check(df):
    issues = []  # List to store issue rows
    if "country" in df.columns:
        for index, value in df["country"].items():
            formatted_country = get_country_code(value)
            if value != formatted_country: #value wasn't already in the right format 
                if formatted_country == "": #value can't be formatted 
                    issues.append({
                                "row": index,
                                "column": "country", 
                                "value": value,
                                "error": "Invalid country format",
                                "suggestion": ""
                            })
                else: #value can be formatted automatically 
                    issues.append({
                                "row": index,
                                "column": 'country', 
                                "value": value,
                                "error": "Invalid country format",
                                "suggestion": formatted_country
                            })

    # Create a DataFrame from the issues list
    issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
    
    return df, issues_df

