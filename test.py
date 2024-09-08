import pycountry 
import pandas as pd


def country_check(df):
    issues = []  # List to store issue rows
    col = "country"
    for index, value in df[col].items():
        if index == 12844: 
            print(index, value, type(value), pd.isna(value))
        if pd.isna(value):
            issues.append({
                            "row": index,
                            "column": col, 
                            "value": value,
                            "error": f"The column {col} shouldn't be empty",
                            "suggestion": ""
                        })
            issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
            return issues_df

        elif not isinstance(value, str):
            issues.append({
                            "row": index,
                            "column": col, 
                            "value": value,
                            "error": f"The column {col} should contain a string",
                            "suggestion": ""
                        })
            issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
            return issues_df
        else: 
            if value == "" or value.lower() == "unknown" : 
                issues.append({
                            "row": index,
                            "column": col, 
                            "value": value,
                            "error": f"The column {col} shouldn't be empty",
                            "suggestion": ""
                        })                       
            else: 
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

df = pd.read_csv("data_file.csv")
print(df.index)