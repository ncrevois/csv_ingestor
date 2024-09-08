import pandas as pd 
from geopy.geocoders import Nominatim
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
                if col == "deviceEntryDate":
                    if pd.isna(value):
                        issues.append({
                            "row": index,
                            "column": col, 
                            "value": value,
                            "error": f"The column {col} shouldn't be empty",
                            "suggestion": ""
                        })
                    else:
                        # Perform date checks
                        try:
                            pd.to_datetime(value, format='%Y-%m-%d', errors='raise')
                        except ValueError:
                            try:
                                # Attempt to parse with a flexible format
                                parsed_date = pd.to_datetime(value, errors='coerce')
                                if pd.notna(parsed_date):  # Check if parsing was successful
                                    formatted_date = parsed_date.strftime('%Y-%m-%d')
                                    # Update the DataFrame with the corrected date
                                    df.at[index, col] = formatted_date
                                    issues.append({
                                        "row": index,
                                        "column": col,
                                        "value": value,
                                        "error": f"The column {col} has an invalid date format",
                                        "suggestion": formatted_date
                                    })
                                else:
                                    issues.append({
                                        "row": index,
                                        "column": col, 
                                        "value": value,
                                        "error": f"The column {col} has an invalid date format",
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
                else:
                    if pd.notna(value):  # Only perform checks if the value is not NaN
                        try:
                            pd.to_datetime(value, format='%Y-%m-%d', errors='raise')
                        except ValueError:
                            try:
                                # Attempt to parse with a flexible format
                                parsed_date = pd.to_datetime(value, errors='coerce')
                                if pd.notna(parsed_date):  # Check if parsing was successful
                                    formatted_date = parsed_date.strftime('%Y-%m-%d')
                                    # Update the DataFrame with the corrected date
                                    df.at[index, col] = formatted_date
                                    issues.append({
                                        "row": index,
                                        "column": col,
                                        "value": value,
                                        "error": f"The column {col} has an invalid date format",
                                        "suggestion": formatted_date
                                    })
                                else:
                                    issues.append({
                                        "row": index,
                                        "column": col, 
                                        "value": value,
                                        "error": f"The column {col} has an invalid date format",
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
    
    return issues_df



def category_check(df):
    issues = []
    col = "deviceCategory"
    for index, value in df[col].items():
        if pd.isna(value): 
            issues.append({
                "row": index,
                "column": col,
                "value": value,
                "error": f"The column {col} shouldn't be empty.",
                "suggestion": ""
            })

        elif not isinstance(value, str): 
                issues.append({
                    "row": index,
                    "column": col,
                    "value": value,
                    "error": f"The column {col} should contain a string.",
                    "suggestion": ""
                })

        else: 
            value = value.upper()
            if value not in valid_device_categories:
                issues.append({
                    "row": index,
                    "column": col,
                    "value": value,
                    "error": "Invalid device category",
                    "suggestion": ""
                })

    # Create a DataFrame from the issues list
    issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
    return issues_df


def country_check(df):
    issues = []  # List to store issue rows
    col = "country"
    if col in df.columns:
        for index, value in df[col].items():
            if pd.isna(value):
                issues.append({
                                "row": index,
                                "column": col, 
                                "value": value,
                                "error": f"The column {col} should not be empty",
                                "suggestion": ""
                            })
                issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
                return issues_df

            if not isinstance(value, str):
                issues.append({
                                "row": index,
                                "column": col, 
                                "value": value,
                                "error": f"The column {col} should contain a string",
                                "suggestion": ""
                            })
                issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
                return issues_df
                            
            country = pycountry.countries.get(alpha_2=value)  #check if country is in the right format
            if not country: 
                try:
                    country = pycountry.countries.search_fuzzy(value)[0]     #try and find the alpha 2 value for the country 
                    issues.append({
                                "row": index,
                                "column": col, 
                                "value": value,
                                "error": f"The column {col} not in Alpha 2 format",
                                "suggestion": country
                            })
                except (LookupError, IndexError):
                    issues.append({
                                "row": index,
                                "column": col, 
                                "value": value,
                                "error": f"The column {col} not in Alpha 2 format",
                                "suggestion": ""
                            })

    issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
    return issues_df

