import streamlit as st
import pandas as pd
from io import StringIO
from functions import *  # Ensure this contains the apply_mapping function
from collections import Counter


# Set the page config
st.set_page_config(
    page_title="CSV Ingestor",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'df' not in st.session_state:
    st.session_state.df = None
if 'missing_columns_flag' not in st.session_state:
    st.session_state.missing_columns_flag = False
if 'categories_issues' not in st.session_state:
    st.session_state.categories_issues = pd.DataFrame()
if 'selected_replacements' not in st.session_state:
    st.session_state.selected_replacements = {}
if 'category_checked' not in st.session_state:
    st.session_state.category_checked = False
if 'show_updated_df' not in st.session_state:
    st.session_state.show_updated_df = False
if 'dates_issues' not in st.session_state:
    st.session_state.dates_issues = pd.DataFrame()
if 'dates_replacements' not in st.session_state:
    st.session_state.dates_replacements = pd.DataFrame()
if 'suggested_fixes' not in st.session_state:
    st.session_state.suggested_fixes = pd.DataFrame()
if 'countries_issues' not in st.session_state:
    st.session_state.countries_issues = pd.DataFrame()
if 'ignore_df' not in st.session_state:
    st.session_state.ignore_df = pd.DataFrame()
if 'null_issues' not in st.session_state:
    st.session_state.null_issues = pd.DataFrame()
if 'categories_issues' not in st.session_state:
    st.session_state.categories_issues = pd.DataFrame()
if 'dates_issues' not in st.session_state:
    st.session_state.dates_issues = pd.DataFrame()
if 'countries_issues' not in st.session_state:
    st.session_state.countries_issues = pd.DataFrame()

def reset_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.df = None
    st.session_state.missing_columns_flag = False
    st.session_state.null_issues = pd.DataFrame()
    st.session_state.categories_issues = pd.DataFrame()
    st.session_state.dates_issues = pd.DataFrame()
    st.session_state.countries_issues = pd.DataFrame()
    st.session_state.categories_issues = pd.DataFrame()
    st.session_state.selected_replacements = {}
    st.session_state.category_checked = False
    st.session_state.show_updated_df = False
    st.session_state.dates_issues = pd.DataFrame()
    st.session_state.dates_replacements = pd.DataFrame()
    st.session_state.suggested_fixes = pd.DataFrame()
    st.session_state.countries_issues = pd.DataFrame()
    st.session_state.ignore_df = pd.DataFrame()

# Helper functions
def update_df(new_df):
    st.session_state.df = new_df

def update_ignore_df(new_ignore_df):
    st.session_state.ignore_df = pd.concat([st.session_state.ignore_df, new_ignore_df], ignore_index=True)

def on_check_dates():
    if st.session_state.df is not None:
        st.session_state.df, st.session_state.dates_issues = date_check(st.session_state.df)
        st.session_state.show_updated_df = False

def on_check_countries():
    if st.session_state.df is not None:
        st.session_state.df, st.session_state.countries_issues = countries_check(st.session_state.df)
        st.session_state.show_updated_df = False

def on_check_categories():
    if st.session_state.df is not None:
        st.session_state.df, st.session_state.categories_issues, valid_device_categories = category_check(st.session_state.df)
        st.session_state.show_updated_df = False

# Add your logo at the top
st.image("Sopht_logo.png", width=150)  # Adjust the width as needed

# Add a title and description
st.markdown(f"<h1 style='color: #d7ffcd;'>CSV Ingestor</h1>", unsafe_allow_html=True)
st.markdown("""
This tool will help you upload your data and make the needed fix for it to be accepted into the database.
            It will also allow you to generate a report with all the issues found in your data. 
""")

# File uploader
uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True)


if st.button("Start/Restart"):
    reset_state()
    if uploaded_files:
        combined_df = files_concat(uploaded_files)
        st.session_state.df = combined_df
        st.write(f"You are working on cleaning the data from these files: {[file.name for file in uploaded_files]}")
    else: 
        st.error("Please upload one or more files.")

# Create tabs
tabs = st.tabs(["Step 1: Map Your Columns", "Step 2: Check all problems", "Step 3: Null Values", "Step 4: Clean Your Categories", "Step 5: Clean Your Dates", "Step 6:Clean Your Countries"])

with tabs[0]:
    st.header("Step 1: Map Your Columns")

    required_columns = ['deviceManufacturer', 'deviceModel', 'deviceSerialnumber', 'deviceEntryDate', 'deviceCategory', 'country']
    optional_columns = ['deviceRetirementDate', 'deviceHostname', 'devicePrice', 'devicePurchaseDate', 'site', 'user', 'operatingSystemName', 'operatingSystemVersion', 'usage', 'maxPower', 'status']
    all_columns = required_columns + optional_columns + ["Add as a tag", "Delete"]

    if st.session_state.df is not None:
        # Check for missing required columns
        missing_required_columns = [col for col in required_columns if col not in st.session_state.df.columns]
        non_standard_columns = [col for col in st.session_state.df.columns if col not in required_columns and col not in optional_columns]

        # Format the column lists
        missing_columns_text = ""
        if missing_required_columns:
            missing_columns_text = "<ul>" + "".join(f"<li style='color:red;'>{col}</li>" for col in missing_required_columns) + "</ul>"

        non_standard_columns_text = ""
        if non_standard_columns:
            non_standard_columns_text = "<ul>" + "".join(f"<li style='color:red;'>{col}</li>" for col in non_standard_columns) + "</ul>"

        if missing_required_columns:
            st.error("You don't have all the necessary columns in your dataframe. Please add the following columns before you proceed:")
            st.markdown(missing_columns_text, unsafe_allow_html=True)
            st.session_state.missing_columns_flag = True
        else:
            st.session_state.missing_columns_flag = False

            # Notify about non-standard columns
            if non_standard_columns and any(not col.startswith('tag:') for col in non_standard_columns):
                st.warning("The following columns are not in the required or optional columns list and will be added as tags:")
                st.markdown(non_standard_columns_text, unsafe_allow_html=True)
            else:
                st.success("All columns are accounted for. You can now proceed to the next step.")

        # Use st.form to create a form
        with st.form(key='column_mapping_form'):
            column_mapping = {}
            columns_to_add_as_a_tag = []
            columns_to_delete = []

            # Create UI for each column in the DataFrame
            for col in st.session_state.df.columns:
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.write(col)

                # Set default value for selectbox
                default_value = col if col in all_columns else "Add as a tag"

                with col2:
                    selected_mapping = st.selectbox(
                        f"Map '{col}' to:",
                        options=all_columns,
                        index=all_columns.index(default_value) if default_value in all_columns else 0,
                        key=f"select_{col}"
                    )

                    # Check if the selected option is "Delete"
                    if selected_mapping == "Delete":
                        columns_to_delete.append(col)
                    elif selected_mapping == "Add as a tag": 
                        columns_to_add_as_a_tag.append(col)
                    else:
                        column_mapping[col] = selected_mapping

            # Submit button for the form
            submit_button = st.form_submit_button(label='Apply Mapping')

            if submit_button:
                # Delete the selected columns
                if columns_to_delete:
                    st.session_state.df.drop(columns=columns_to_delete, inplace=True)
                    st.success(f"Columns {', '.join(columns_to_delete)} deleted successfully.")

                if columns_to_add_as_a_tag: 
                    for col in columns_to_add_as_a_tag: 
                        if not col.startswith("tag:"): 
                            st.session_state.df.rename(columns={col: f"tag:{col}"}, inplace=True)

                # Check for duplicate mappings
                if len(set(column_mapping.values())) != len(column_mapping.values()):
                    st.error("You have selected the same column multiple times for mapping. Please ensure each column is mapped uniquely.")
                    st.write(str([item for item, count in Counter(list(column_mapping.values())).items() if count > 1]))
                else:
                    # Apply the column mappings
                    st.session_state.df = apply_mapping(st.session_state.df, column_mapping)

                    # Recompute missing_columns_flag based on the newly mapped DataFrame
                    st.session_state.missing_columns_flag = not set(required_columns).issubset(st.session_state.df.columns)
                    if not st.session_state.missing_columns_flag:
                        st.success("Mapping applied successfully. Proceed to the next step.")
                    else:
                        st.error("Mapping applied, but some required columns are still missing. Please review.")
                        st.write(str([item for item in required_columns if item not in st.session_state.df.columns]))

        # Display the updated DataFrame after the form logic
        if st.session_state.df is not None:
            st.write("This is the updated version of your data:")
            st.write(st.session_state.df)


@st.fragment
def check_all_errors_fragment():
    st.header("Step 1: Check All Problems")
    st.write("This step will check for all types of issues in your dataset.")

    # Check for null values
    null_issues = st.session_state.df[st.session_state.df[required_columns].isnull().any(axis=1)]

    # Check for category problems
    st.session_state.df, categories_issues, valid_device_categories = category_check(st.session_state.df)
    problematic_categories = categories_issues['deviceCategory'].unique()

    # Check for date problems
    st.session_state.df, dates_issues = date_check(st.session_state.df)

    # Check for country problems
    st.session_state.df, countries_issues = countries_check(st.session_state.df)

    # Display summary of issues
    st.subheader("Summary of Issues:")

    if not null_issues.empty:
        st.error(f"⚠️ Null Values: {len(null_issues)} rows have missing values in mandatory columns.")
    
    if not categories_issues.empty:
        st.error(f"⚠️ Category Issues: {len(problematic_categories)} problematic categories found.")
    
    if not dates_issues.empty:
        st.error(f"⚠️ Date Issues: {len(dates_issues)} date-related issues found.")
    
    if not countries_issues.empty:
        st.error(f"⚠️ Country Issues: {len(countries_issues)} country-related issues found.")

    if null_issues.empty and categories_issues.empty and dates_issues.empty and countries_issues.empty:
        st.success("✅ No issues found in your dataset. Great job!")
    else:
        st.warning("Please proceed to the following tabs to address these issues individually.")

    # Option to display detailed issues
    if st.checkbox("Show detailed issues"):
        if not null_issues.empty:
            st.subheader("Null Value Issues")
            st.write(null_issues)
        
        if not categories_issues.empty:
            st.subheader("Category Issues")
            st.write(categories_issues)
        
        if not dates_issues.empty:
            st.subheader("Date Issues")
            st.write(dates_issues)
        
        if not countries_issues.empty:
            st.subheader("Country Issues")
            st.write(countries_issues)


# Define the fragment for null values in mandatory columns
@st.fragment
def check_null_values_fragment(null_issues):
    
    if not null_issues.empty:
        st.error("There are rows with missing values in mandatory columns.")
        issue_rows = null_issues.index

        st.markdown("### Option 1: Ignore All Problematic Rows")
        st.write("Those rows will be added to an 'ignored_rows' file that you can download at the end.")
        if st.button("Ignore All Rows", key="null_ignore"):
            update_ignore_df(null_issues)
            update_df(st.session_state.df.drop(issue_rows))
            st.write("These are the rows that were ignored:")
            st.write(st.session_state.ignore_df)
            st.write("This is the updated dataset you are working on:")
            st.write(st.session_state.df)

        st.markdown("### Option 2: Replace All Problematic By Hand")
        with st.form(key='edit_form_nulls'):
            edited_dfs = {}
            for col in required_columns:
                col_null_issues = null_issues[null_issues[col].isnull()]  # Filter for null values in the current column
                if not col_null_issues.empty:
                    st.write(f"Please edit the column {col} with missing values:")
                    edited_dfs[col] = st.data_editor(
                        col_null_issues,
                        key=f"manual_null_editor_{col}",
                        column_config={col: st.column_config.TextColumn(label=f"{col}", required=True)}
                    )

            if st.form_submit_button(label='Apply All'):
                for col, edited_df in edited_dfs.items():
                    for index, row in edited_df.iterrows():
                        st.session_state.df.loc[index, col] = row[col]
                st.success("Changes have been applied successfully!")
                st.session_state.show_updated_df = True

    else:
        st.success("You have no issues with missing values, you can continue to the next step.")

    if st.session_state.show_updated_df:
        st.success("Manual changes have been applied. You can proceed to the next step. Here is the updated data:")
        st.write(st.session_state.df)


# Define the fragment for category check
@st.fragment
def check_categories_fragment():

    # Run category check
    st.session_state.df, st.session_state.categories_issues, valid_device_categories = category_check(st.session_state.df)
    st.session_state.show_updated_df = False
    problematic_categories = st.session_state.categories_issues['deviceCategory'].unique()
    rows_with_issues = st.session_state.df[st.session_state.df['deviceCategory'].isin(problematic_categories)]

    if not st.session_state.categories_issues.empty:
        st.error("You have categories that are not allowed. Please replace those with allowed values.")

        ### Option 1: Replace All by Form ###
        st.markdown("### Option 1: Replace All Problematic Categories")
        with st.form(key='replace_all_form'):
            replace_all_by = st.selectbox(
                "Replace all problematic categories by:",
                options=["Select an option"] + valid_device_categories,
                key="replace_all_by_select"
            )
            replace_all_button = st.form_submit_button("Replace All")

            if replace_all_button and replace_all_by != "Select an option":
                for category in problematic_categories:
                    st.session_state.df.loc[st.session_state.df['deviceCategory'] == category, 'deviceCategory'] = replace_all_by
                st.success(f"All problematic categories replaced with '{replace_all_by}'.")
                st.session_state.show_updated_df = True

        ### Option 2: Ignore those rows ###
        st.markdown("### Option 2: Ignore all Problematic Rows")
        st.write("Those rows will be added to an 'ignored_rows' file that you can download at the end.")
        with st.form(key='ignore_all'):

            # Button to process ignoring rows
            ignore_button = st.form_submit_button("Ignore All Rows")
            if ignore_button:
                # Remove the ignored rows from the original DataFrame
                st.session_state.ignore_df = pd.concat([st.session_state.ignore_df, rows_with_issues])
                st.session_state.df = st.session_state.df[~st.session_state.df['deviceCategory'].isin(problematic_categories)]
                st.write("The following rows were added to an ignored dataset and deleted from the working dataset:")
                st.write(st.session_state.ignore_df)
                st.session_state.show_updated_df = True

        ### Option 3: Replace In Bulk Form ###
        st.markdown("### Option 3: Replace Categories In Bulk")
        with st.form(key='category_cleanup_form'):
            for category in problematic_categories:
                count = st.session_state.categories_issues[st.session_state.categories_issues['deviceCategory'] == category].shape[0]
                st.markdown(f"**Problematic Category:** `{category}`")
                st.markdown(f"**Number of Rows:** `{count}`")

                if category not in st.session_state.selected_replacements:
                    st.session_state.selected_replacements[category] = valid_device_categories[0]  # Default to the first valid category

                st.session_state.selected_replacements[category] = st.selectbox(
                    f"Select a valid category for '{category}':",
                    options=valid_device_categories,
                    key=f"select_{category}"
                )

            apply_button = st.form_submit_button("Apply Individually")

            if apply_button:
                for category, replacement in st.session_state.selected_replacements.items():
                    st.session_state.df.loc[st.session_state.df['deviceCategory'] == category, 'deviceCategory'] = replacement
                st.success("Individual replacements applied.")
                st.session_state.show_updated_df = True
        
        ### Option 3: Replace Individually Form ###
        st.markdown("### Option 4: Replace All Problematic Rows By Hand")

        with st.form(key='edit_form_country'):
            edited_df = st.data_editor(
                rows_with_issues,
                key="manual_category_editor",
                column_config={
                    "country": st.column_config.SelectboxColumn(
                        f"Select a valid category for '{category}':",
                        help="Enter a valid category from the list.",
                        options=valid_device_categories,
                        required=True
                    )}
            )

            if st.form_submit_button(label='Apply All'):
                for index, row in edited_df.iterrows():
                    st.session_state.df.loc[index, "country"] = row["country"]
                st.success("Changes have been applied successfully!")
                st.session_state.show_updated_df = True

    if st.session_state.categories_issues.empty:
        st.success("No issues found Your data is clean.")
        st.session_state.show_updated_df = False  # Do not show updated DataFrame if there are no issues

    # Show updated DataFrame outside the form
    if st.session_state.show_updated_df:
        st.success("Your changes have been applied. Here is the updated data:")
        st.write(st.session_state.df)


# Define the fragment for date check
@st.fragment
def check_dates_fragment():
    if not st.session_state.dates_issues.empty:
        suggested_fixes = st.session_state.dates_issues[st.session_state.dates_issues['suggestion'] != '']
        manual_fixes = st.session_state.dates_issues[st.session_state.dates_issues['suggestion'] == '']

        if not suggested_fixes.empty:
            for _, row in suggested_fixes.iterrows():
                st.session_state.df.at[row['row'], row['column']] = row['suggestion']
            st.success(f"Automatically fixed {len(suggested_fixes)} dates based on suggestions.")

        if not manual_fixes.empty:
            st.error("You have dates that weren't able to be parsed. Please review and correct them.")
            issue_rows = manual_fixes["row"].unique()
            rows_with_issues = st.session_state.df.loc[st.session_state.df.index.isin(issue_rows)].copy()

            st.markdown("### Option 1: Ignore all Problematic Rows")
            if st.button("Ignore All Rows", key = "date_ignore"):
                update_ignore_df(rows_with_issues)
                update_df(st.session_state.df[~st.session_state.df.index.isin(issue_rows)])
                st.write("These are the rows that were ignored:")
                st.write(st.session_state.ignore_df)
                st.write("This is the updated dataset you are working on:")
                st.write(st.session_state.df)

            st.markdown("### Option 2: Replace All Problematic By Hand")
            with st.form(key='edit_form_dates'):
                edited_dfs = {}
                for col in manual_fixes["column"].unique():
                    st.write(f"Please edit the column {col}")
                    if col in rows_with_issues.columns:
                        rows_with_issues[col] = pd.to_datetime(rows_with_issues[col], errors='coerce').dt.date
                    edited_dfs[col] = st.data_editor(
                        rows_with_issues,
                        key=f"manual_date_editor_{col}", 
                        column_config={col: st.column_config.DateColumn(label=f"{col}", format="YYYY-MM-DD", required=True)}
                    )

                if st.form_submit_button(label='Apply All'):
                    for col, edited_df in edited_dfs.items():
                        for index, row in edited_df.iterrows():
                            st.session_state.df.loc[index, col] = row[col].strftime("%Y-%m-%d")
                    st.success("Changes have been applied successfully!")
                    st.session_state.show_updated_df = True

    else:
        st.success("You have no date issues, you can continue to the next step.")

    if st.session_state.show_updated_df:
        st.success("Manual changes have been applied. You can proceed to the next step. Here is the updated data:")
        st.write(st.session_state.df)
# Define the fragment for country check
@st.fragment
def check_countries_fragment():
    if not st.session_state.countries_issues.empty:
        suggested_fixes = st.session_state.countries_issues[st.session_state.countries_issues['suggestion'] != '']
        manual_fixes = st.session_state.countries_issues[st.session_state.countries_issues['suggestion'] == '']

        if not suggested_fixes.empty:
            for _, row in suggested_fixes.iterrows():
                st.session_state.df.at[row['row'], row['column']] = row['suggestion']
            st.success(f"Automatically fixed {len(suggested_fixes)} countries based on suggestions.")

        if not manual_fixes.empty:
            st.error("You have countries that couldn't be parsed. Please review and correct them.")
            issue_rows = manual_fixes["row"].unique()
            rows_with_issues = st.session_state.df.loc[st.session_state.df.index.isin(issue_rows)].copy()

            st.markdown("### Option 1: Ignore all Problematic Rows")
            if st.button("Ignore All Rows", key = "country_ignore"):
                update_ignore_df(rows_with_issues)
                update_df(st.session_state.df[~st.session_state.df.index.isin(issue_rows)])
                st.write("These are the rows that were ignored:")
                st.write(st.session_state.ignore_df)
                st.write("This is the updated dataset you are working on:")
                st.write(st.session_state.df)

            st.markdown("### Option 2: Replace All Problematic By Hand")
            with st.form(key='edit_form_country'):
                edited_df = st.data_editor(
                    rows_with_issues,
                    key="manual_country_editor",
                    column_config={
                        "country": st.column_config.TextColumn(
                            help="Enter a valid ISO 3166-1 alpha-2 country code (e.g., 'GB', 'FR')",
                            validate="^[A-Z]{2}$",
                            required=True,
                            max_chars=2
                        )}
                )

                if st.form_submit_button(label='Apply All'):
                    for index, row in edited_df.iterrows():
                        st.session_state.df.loc[index, "country"] = row["country"]
                    st.success("Changes have been applied successfully!")
                    st.session_state.show_updated_df = True

    else:
        st.success("You have no country issues, you can continue to the next step.")

    if st.session_state.show_updated_df:
        st.success("Manual changes have been applied. You can proceed to the next step. Here is the updated data:")
        st.write(st.session_state.df)

with tabs[1]:
    check_all_errors_fragment()

# Tab for checking null values 
with tabs[2]:
    st.header("Step 1: Null values")
    st.write("Click the button below to check for unallowed null values in your data.")
    
    # Check categories button
    check_button = st.button("Check null values")

    if check_button:
        check_null_values_fragment()

# Tab for category check
with tabs[3]:
    st.header("Step 3: Clean Your Data (Categories)")
    st.write("Click the button below to check for issues with device categories in your data.")
    
    # Check categories button
    check_button = st.button("Check categories")

    if check_button:
        check_categories_fragment()
        
# Tab for date check
with tabs[4]:
    st.header("Step 4: Clean Your Data (Dates)")
    st.write("Click the button below to check for issues with dates in your data.")

    # Check dates button
    check_dates_button = st.button("Check dates", on_click=on_check_dates)

    if check_dates_button:
        check_dates_fragment()

# Tab for country check
with tabs[5]:
    st.header("Step 5: Clean Your Countries")
    st.write("Click the button below to check for issues with country names in your data.")

    # Check countries button
    check_countries_button = st.button("Check countries", on_click=on_check_countries)

    if check_countries_button:
        check_countries_fragment()