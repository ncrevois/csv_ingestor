import streamlit as st
import pandas as pd
from functions import *  # Ensure this contains the apply_mapping function
from collections import Counter
import plotly.express as px
import seaborn as sns
from typing import Literal
from datetime import datetime, date


# Set the page config
st.set_page_config(
    page_title="CSV Ingestor",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state variables
if 'initial_df' not in st.session_state:
    st.session_state.initial_df = pd.DataFrame()
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
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
if 'issues_df_final' not in st.session_state:
    st.session_state.issues_df_final = pd.DataFrame()
if 'issues_without_suggestions' not in st.session_state:
    st.session_state.issues_without_suggestions = pd.DataFrame()
if 'issues_with_suggestions' not in st.session_state:
    st.session_state.issues_with_suggestions = pd.DataFrame()


def reset_state():
    st.session_state.df = pd.DataFrame()
    st.session_state.missing_columns_flag = False
    st.session_state.categories_issues = pd.DataFrame()
    st.session_state.selected_replacements = {}
    st.session_state.category_checked = False
    st.session_state.show_updated_df = False
    st.session_state.dates_issues = pd.DataFrame()
    st.session_state.dates_replacements = pd.DataFrame()
    st.session_state.suggested_fixes = pd.DataFrame()
    st.session_state.issues_df_final = pd.DataFrame()
    st.session_state.issues_without_suggestions = pd.DataFrame()
    st.session_state.issues_with_suggestions = pd.DataFrame()
    st.session_state.countries_issues = pd.DataFrame()
    st.session_state.ignore_df = pd.DataFrame()
    st.session_state.initial_df = pd.DataFrame()

# Add your logo at the top
st.image("Sopht_logo.png", width=150)  # Adjust the width as needed

# Add a title and description
st.markdown("<h1 style='color: #d7ffcd;'>CSV Ingestor</h1>", unsafe_allow_html=True)
st.markdown("""
This tool will help you upload your data and make the needed fix for it to be accepted into the database.
            It will also allow you to generate a report with all the issues found in your data. 
""")

# Helper functions
def update_df(new_df):
    st.session_state.df = new_df

def update_ignore_df(new_ignore_df):
    st.session_state.ignore_df = pd.concat([st.session_state.ignore_df, new_ignore_df], ignore_index=True)


def ignore_rows_form(rows_with_issues): 

    st.write("Those rows will be added to an 'ignored_rows' file that you can download at the end.")
    with st.form(key='ignore_all'):
        # Button to process ignoring rows
        ignore_button = st.form_submit_button("Ignore All Rows")
        if ignore_button:
            # Remove the ignored rows from the original DataFrame
            update_ignore_df(rows_with_issues)
            update_df(st.session_state.df[~st.session_state.df.index.isin(rows_with_issues.index)])
            st.write("The following rows were added to an ignored dataset and deleted from the working dataset:")
            st.write(st.session_state.ignore_df)
            st.session_state.show_updated_df = True

def replace_all_form(rows_with_issues, column, type: Literal["options", "date", "freeform"], extra_data = None): 
    with st.form(key=f'replace_all_form_{column}'):
        if type == "freeform":
            replace_all_by = st.text_input(
                    "Replace all problematic values by:",
                    key=f"replace_all_by_input_{column}"
                )

        if type == "options": 
            replace_all_by = st.selectbox(
                "Replace all problematic values by:",
                options=extra_data,
                key=f"replace_all_by_select_{column}"
            )

        if type == "date": 
            replace_all_by = st.date_input(
                "Replace all problematic values with this date:",
                value=date.today(),
                format="YYYY-MM-DD",
                key=f"replace_all_by_{column}"
            )
        
        replace_all_button = st.form_submit_button("Replace All")

        if replace_all_button:
            rows_with_issues[column] = replace_all_by
            st.session_state.df.loc[st.session_state.df.index.isin(rows_with_issues.index), column] = rows_with_issues[column]
            st.success(f"All problematic categories replaced with '{replace_all_by}'.")
            st.session_state.show_updated_df = True

def replace_all_by_hand(rows_with_issues, column, type: Literal["options", "date", "freeform"], extra_data = None):
    with st.form(key='edit_form_category'):
        if type == "options":
            edited_df = st.data_editor(
                        rows_with_issues,
                        key=f"manual_editor_{column}",
                        column_config={
                            column: st.column_config.SelectboxColumn(
                                label = f"{column}",
                                help="Enter a valid value from the list.",
                                options=extra_data,
                                required=True
                            )}
                    )
        
        if type == "date":
            edited_df = st.data_editor(
                            rows_with_issues,
                            key=f"manual_editor_{column}", 
                            column_config={column: st.column_config.TextColumn(label=f"{column}", max_chars=10, validate="^\\d{4}-\\d{2}-\\d{2}$", required=True)}
                        )
        
        if type == "freeform":
            edited_df = st.data_editor(
                            rows_with_issues,
                            key=f"manual_editor_{column}"
                        )

        if st.form_submit_button(label='Apply All'):
            for index, row in edited_df.iterrows():
                st.session_state.df.loc[index, "deviceCategory"] = row["deviceCategory"]
            st.success("Changes have been applied successfully!")
            st.session_state.show_updated_df = True


# File uploader
uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True)

if st.button("Start/Restart"):
    reset_state()
    if uploaded_files:
        st.session_state.initial_df = files_concat(uploaded_files)
        st.session_state.df = st.session_state.initial_df.copy()
        st.write(f"You are working on cleaning the data from these files: {[file.name for file in uploaded_files]}")
    else: 
        st.error("Please upload one or more files.")


# Create tabs
tabs = st.tabs(["Step 1: Map Your Columns",  "Step 2: Data Quality Report", "Step 3: Clean Your Data", "Step 4: Download Your Data"])

if not st.session_state.df.empty:

    with tabs[0]:
        st.markdown("<h2>Step 1: Map Your Columns</h2>", unsafe_allow_html=True)

        required_columns = ['deviceManufacturer', 'deviceModel', 'deviceSerialnumber', 'deviceEntryDate', 'deviceCategory', 'country']
        optional_columns = ['deviceRetirementDate', 'deviceHostname', 'devicePrice', 'devicePurchaseDate', 'site', 'user', 'operatingSystemName', 'operatingSystemVersion', 'usage', 'maxPower', 'status']
        all_columns = required_columns + optional_columns + ["Add as a tag", "Delete"]

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

    with tabs[1]:
        st.markdown("<h2>Step 2: Data Quality Report</h2>", unsafe_allow_html=True)
        # Redefining checks
        checks = ["date", "category", "country", "serial_number", "manufacturer", "model"]
        st.session_state.issues_df_final = pd.DataFrame()
        for check in checks:
            func = globals()[f"{check}_check"]
            issues_df = func(st.session_state.df)
            st.session_state.issues_df_final = pd.concat([st.session_state.issues_df_final, issues_df], ignore_index=True)

        st.session_state.issues_without_suggestions = st.session_state.issues_df_final[st.session_state.issues_df_final['suggestion'] == '']
        st.session_state.issues_with_suggestions = st.session_state.issues_df_final[st.session_state.issues_df_final['suggestion'] != '']

        # Calculate global statistics
        ##[uncomment these lines for showing suggestions] cells, before correction 
        ##cells_with_issues = len(st.session_state.issues_df_final['row'])
        ##cells_with_issues_no_suggestion = len(st.session_state.issues_without_suggestions) 
        ##cells_automatically_corrected = cells_with_issues - cells_with_issues_no_suggestion
        ##percentage_cells_automatically_corrected = (cells_automatically_corrected / cells_with_issues) * 100

        #rows, after correction 
        total_rows = len(st.session_state.df)
        len_rows_with_issues = len(st.session_state.issues_without_suggestions['row'].unique())
        percentage_rows_with_issues = (len_rows_with_issues / total_rows) * 100

        # Group by error type for detailed view
        error_summary = st.session_state.issues_without_suggestions.groupby('error').size().reset_index(name='count')
        error_by_column = st.session_state.issues_without_suggestions.groupby(['column', 'error']).size().reset_index(name='count')

        # Global statistics
        st.markdown("<h3 style='color: #d7ffcd;'>Global Overview</h3>", unsafe_allow_html=True)
        
        ##[uncomment these lines for showing suggestions] if we ever want to show suggestions 
        ##st.markdown(f"We detected {cells_with_issues:,} cells with errors in your data. {percentage_cells_automatically_corrected:.2f}% of them can be automatically corrected.")
        ##st.markdown("After correction, this is the amount of rows that still have an error in your dataset:")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows in your dataset", f"{total_rows:,}")
        with col2:
            st.metric("Rows with Issues", f"{len_rows_with_issues:,}")
        with col3:
            st.metric("Percentage of Rows with Issues", f"{percentage_rows_with_issues:.0f}%")

        st.divider()

        # Detailed error breakdown
        st.markdown("<h3 style='color: #d7ffcd;'>Detailed Error View</h3>", unsafe_allow_html=True)
        custom_colors1 = sns.color_palette("crest", n_colors=10).as_hex()
        custom_colors2 = sns.color_palette("cubehelix", n_colors = 10).as_hex()

        # Error by type chart
        fig = px.pie(error_by_column, values='count', names='column', title='Distribution of Errors by Column', color_discrete_sequence=custom_colors1)
        st.plotly_chart(fig)

        # Errors by column and type
        fig = px.bar(error_by_column, x='column', y='count', color='error', title='Error Distribution by Column and Type', labels={'count': 'Number of Errors'}, color_discrete_sequence=custom_colors2)
        st.plotly_chart(fig)

        # Filter options
        all_error_types = st.session_state.issues_without_suggestions['error'].unique()
        selected_errors = st.multiselect("Select error types to filter", options=all_error_types, default=all_error_types)

        # Filter issues based on selected error types
        filtered_issues_without_suggestions = st.session_state.issues_without_suggestions[st.session_state.issues_without_suggestions['error'].isin(selected_errors)]

        # Group the issues by 'row' and create the columns based on the new logic
        issue_details = (
            filtered_issues_without_suggestions.groupby('row').agg(
                issue_detail=('error', lambda x: ', '.join(x)),  # Concatenate error strings
                number_of_errors=('error', 'count'),  # Count number of errors
                column_with_problems=('column', lambda x: list(x))  # List of problematic columns
            )
        )

        st.divider()

        # Select only rows in st.session_state.df where index is in 'row' of filtered_issues
        df_with_issues = st.session_state.df.loc[st.session_state.df.index.isin(filtered_issues_without_suggestions['row'])].copy()

        # Merge issue details back to df_with_issues
        df_with_issues = df_with_issues.merge(issue_details, left_index=True, right_index=True, how='left')

        # Optionally show the full dataframe with error details
        st.subheader("Rows with Errors (Original Data + Error Details)")
        st.write("Showing only rows with issues:")
        st.dataframe(df_with_issues)

        # Download button for issues DataFrame
        csv = df_with_issues.to_csv(index=False)
        st.download_button(
            label="Download problematic rows as CSV",
            data=csv,
            file_name="problematic_rows.csv",
            mime="text/csv",
        )

        # Optionally show the full dataframe with error details
        st.subheader("Rows with Errors that were automatically corrected (Original Data + Error Details)")
        
        if not st.session_state.issues_with_suggestions.empty:
            st.write("Showing only rows with issues that were automatically corrected:")
            st.dataframe(st.session_state.issues_with_suggestions)
            
            for _, row in st.session_state.issues_with_suggestions.iterrows():
                st.session_state.df.at[row['row'], row['column']] = row['suggestion']
            
        else: 
            st.write("None of the errors could be automatically corrected.")


    with tabs[2]: 
        columns_to_fix = st.session_state.issues_without_suggestions['column'].unique()
        st.markdown("<h2>Step 3: Clean your Data</h2>", unsafe_allow_html=True)
        column_to_fix =  st.selectbox("Which column would you want to clean?", options = columns_to_fix)
        

        if column_to_fix == "deviceCategory": 
            st.session_state.categories_issues = st.session_state.issues_without_suggestions[st.session_state.issues_without_suggestions["column"] == column_to_fix]
            st.session_state.show_updated_df = False
            rows_with_issues = df_with_issues.loc[st.session_state.categories_issues['row'].tolist()]
            problematic_categories = st.session_state.categories_issues['value'].unique()

            st.error("You have categories that are not allowed. Please replace those with allowed values.")

            ### Option 1: Replace All by Form ###
            st.markdown("### Option 1: Replace All Problematic Categories")
            replace_all_form(rows_with_issues, column = column_to_fix , type = "options", extra_data = valid_device_categories)

            ### Option 2: Ignore those rows ###
            st.markdown("### Option 2: Ignore all Problematic Rows")
            ignore_rows_form(rows_with_issues)

            ### Option 3: Replace In Bulk Form ###
            st.markdown("### Option 3: Replace Categories In Bulk")
            with st.form(key='category_cleanup_form'):
                for category in problematic_categories:
                    count = st.session_state.categories_issues[st.session_state.categories_issues['value'] == category].shape[0]
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
            
            ### Option 4: Replace Individually Form ###
            st.markdown("### Option 4: Replace All Problematic Rows By Hand")

            replace_all_by_hand(rows_with_issues, column = column_to_fix, type = "options", extra_data = valid_device_categories)

            if st.session_state.categories_issues.empty:
                st.success("No issues found Your data is clean.")
                st.session_state.show_updated_df = False  # Do not show updated DataFrame if there are no issues

            # Show updated DataFrame outside the form
            if st.session_state.show_updated_df:
                st.success("Your changes have been applied. Here is the updated data:")
                st.write(st.session_state.df)

        if column_to_fix in ["deviceEntryDate", "deviceRetirementDate", "devicePurchaseDate"]: 
            st.session_state.dates_issues = st.session_state.issues_without_suggestions[st.session_state.issues_without_suggestions["column"] == column_to_fix]
            if not st.session_state.dates_issues.empty:
                st.error("You have dates that weren't able to be parsed. Please review and correct them.")
                rows_with_issues = df_with_issues.loc[st.session_state.dates_issues['row'].unique()].copy()


                st.markdown("### Option 1: Replace All Problematic By Hand")
                replace_all_by_hand(rows_with_issues, column = column_to_fix, type = "date")

                st.markdown("### Option 2: Replace All Problematic Dates by one date")
                replace_all_form(rows_with_issues, column = column_to_fix, type = "date")

                st.markdown("### Option 3: Ignore all Problematic Rows")
                ignore_rows_form(rows_with_issues)


            if st.session_state.show_updated_df:
                st.success("Manual changes have been applied. You can proceed to the next step. Here is the updated data:")
                st.write(st.session_state.df)


        if column_to_fix == "country": 
            
            st.session_state.countries_issues = st.session_state.issues_without_suggestions[st.session_state.issues_without_suggestions["column"] == column_to_fix]
            rows_with_issues = df_with_issues.loc[st.session_state.countries_issues['row'].tolist()]
                
            st.markdown("### Option 1: Ignore all Problematic Rows")
            ignore_rows_form(rows_with_issues)

            st.markdown("### Option 2: Replace All Problematic By Hand")
            replace_all_by_hand(rows_with_issues, column = column_to_fix, type = "freeform")
        
            if st.session_state.show_updated_df:
                st.success("Manual changes have been applied. You can proceed to the next step. Here is the updated data:")
                st.write(st.session_state.df)

        if column_to_fix == "deviceModel": 
            
            st.session_state.models_issues = st.session_state.issues_without_suggestions[st.session_state.issues_without_suggestions["column"] == column_to_fix]
            rows_with_issues = df_with_issues.loc[st.session_state.models_issues['row'].tolist()]
                
            st.markdown("### Option 1: Ignore all Problematic Rows")
            ignore_rows_form(rows_with_issues)

            st.markdown("### Option 2: Replace All Problematic By Hand")
            replace_all_by_hand(rows_with_issues, column = column_to_fix, type = "freeform")

            if st.session_state.show_updated_df:
                st.success("Manual changes have been applied. You can proceed to the next step. Here is the updated data:")
                st.write(st.session_state.df)

        if column_to_fix == "deviceManufacturer": 
            
            st.session_state.manufacturer_issues = st.session_state.issues_without_suggestions[st.session_state.issues_without_suggestions["column"] == column_to_fix]
            rows_with_issues = df_with_issues.loc[st.session_state.manufacturer_issues['row'].tolist()]
                
            st.markdown("### Option 1: Ignore all Problematic Rows")
            ignore_rows_form(rows_with_issues)

            st.markdown("### Option 2: Replace All Problematic By Hand")
            replace_all_by_hand(rows_with_issues, column = column_to_fix, type = "freeform")    

            if st.session_state.show_updated_df:
                st.success("Manual changes have been applied. You can proceed to the next step. Here is the updated data:")
                st.write(st.session_state.df)  

        
        if column_to_fix == "deviceSerialnumber": 
            
            st.session_state.serial_number_issues = st.session_state.issues_without_suggestions[st.session_state.issues_without_suggestions["column"] == column_to_fix]
            rows_with_issues = df_with_issues.loc[st.session_state.serial_number_issues['row'].tolist()]
                
            st.markdown("### Option 1: Ignore all Problematic Rows")
            ignore_rows_form(rows_with_issues)

            st.markdown("### Option 2: Replace All Problematic By Hand")
            replace_all_by_hand(rows_with_issues, column = column_to_fix, type = "freeform")    

            if st.session_state.show_updated_df:
                st.success("Manual changes have been applied. You can proceed to the next step. Here is the updated data:")
                st.write(st.session_state.df)  

    with tabs[3]: 

        st.markdown("<h2>Step 3: Download your Data</h2>", unsafe_allow_html=True)

        total_rows = len(st.session_state.initial_df)
        ignored_rows = len(st.session_state.ignore_df)
        ignored_percentage = (ignored_rows / total_rows) * 100

        # Display the percentages
        st.metric("Percentage of Data Ignored", f"{ignored_percentage:.2f}%")

        # View and download cleaned dataset
        st.markdown("<h2>Step 3: Cleaned Data</h2>", unsafe_allow_html=True)
        st.dataframe(st.session_state.df)
        csv = st.session_state.df.to_csv(index=False)
        st.download_button(
            label="Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime='text/csv',
        )

        # View and download cleaned dataset
        st.markdown("<h2>Step 3: Ignored Data</h2>", unsafe_allow_html=True)
        st.dataframe(st.session_state.ignore_df)
        csv = st.session_state.df.to_csv(index=False)
        st.download_button(
            label="Download Ignored Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime='text/csv',
        )



        



        

