import pycountry 
import pandas as pd

def country_check(value):
    issues = []  # List to store issue rows
    index = 0
    
    if not value:
        issues.append({
                        "row": index,
                        "column": "country", 
                        "value": value,
                        "error": "Country should not be empty",
                        "suggestion": ""
                    })
        issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
        return(issues)
        
    if not isinstance(value, str):
        issues.append({
                        "row": index,
                        "column": "country", 
                        "value": value,
                        "error": "Country should be a string",
                        "suggestion": ""
                    })
        issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
        return(issues)
        
    country = pycountry.countries.get(alpha_2=value)  #check if country is in the right format
    if not country: 
        try:
            country = pycountry.countries.search_fuzzy(value)[0]     #try and find the alpha 2 value for the country 
            issues.append({
                        "row": index,
                        "column": "country", 
                        "value": value,
                        "error": "Country not in Alpha 2 format",
                        "suggestion": country
                    })
            issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
            return(issues)
        except (LookupError, IndexError):
            issues.append({
                        "row": index,
                        "column": "country", 
                        "value": value,
                        "error": "Country not in Alpha 2 format",
                        "suggestion": ""
                    })
            issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
            return(issues)

    # Create a DataFrame from the issues list
    issues_df = pd.DataFrame(issues, columns=["row", "column", "value", "error", "suggestion"])
    
    return issues_df

print(country_check(None))