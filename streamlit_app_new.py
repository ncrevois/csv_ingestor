import streamlit as st
import pandas as pd
from functions import *  # Ensure this contains the apply_mapping function
from collections import Counter
import plotly.express as px


# Set the page config
st.set_page_config(
    page_title="CSV Ingestor",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state variables
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
if 'issues_df_final' not in st.session_state:
    st.session_state.issues_without_suggestions = pd.DataFrame()


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
    st.session_state.countries_issues = pd.DataFrame()
    st.session_state.ignore_df = pd.DataFrame()

# Add your logo at the top
st.image("Sopht_logo.png", width=150)  # Adjust the width as needed

# Add a title and description
st.markdown("<h1 style='color: #d7ffcd;'>CSV Ingestor</h1>", unsafe_allow_html=True)
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
tabs = st.tabs(["Step 1: Map Your Columns",  "Step 2: Data Quality Report", "Step 3: Clean Your Data"])

if not st.session_state.df.empty:

    with tabs[0]:
        st.markdown("<h2>Step 1: Map Your Columns</h1>", unsafe_allow_html=True)

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
        st.markdown("<h2>Step 2: Data Quality Report</h1>", unsafe_allow_html=True)
        # Redefining checks
        checks = ["date", "category", "country"]

        for check in checks:
            func = globals()[f"{check}_check"]
            issues_df = func(st.session_state.df)
            st.session_state.issues_df_final = pd.concat([st.session_state.issues_df_final, issues_df], ignore_index=True)

        st.session_state.issues_without_suggestions = st.session_state.issues_df_final[st.session_state.issues_df_final['suggestion'] == '']

        # Calculate global statistics
        total_rows = len(st.session_state.df)
        rows_with_issues_no_suggestion = len(st.session_state.issues_df_final['row'].unique())
        rows_automatically_corrected = total_rows - rows_with_issues_no_suggestion
        percentage_with_issues = (rows_with_issues_no_suggestion / total_rows) * 100
        percentage_automatically_corrected = (rows_automatically_corrected / total_rows) * 100

        # Automatically corrected 
        st.markdown("")

        # Group by error type for detailed view
        error_summary = st.session_state.issues_without_suggestions.groupby('error').size().reset_index(name='count')
        error_by_column = st.session_state.issues_without_suggestions.groupby(['column', 'error']).size().reset_index(name='count')

        # Global statistics
        st.markdown("<h3 style='color: #d7ffcd;'>Global Overview</h3>", unsafe_allow_html=True)
        
        # Automatically corrected 
        if rows_automatically_corrected != 0: 
            st.markdown(f"We were able to automatically correct {rows_automatically_corrected:,} of your problematic rows ({percentage_automatically_corrected:.2f}%).")
            st.markdown(f"The metrics below show the number of rows with problems that we couldn't automatically correct.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{total_rows:,}")
        with col2:
            st.metric("Rows with Issues", f"{rows_with_issues_no_suggestion:,}")
        with col3:
            st.metric("Percentage with Issues", f"{percentage_with_issues:.2f}%")

        st.divider()

        # Detailed error breakdown
        st.markdown("<h3 style='color: #d7ffcd;'>Detailed Error View</h3>", unsafe_allow_html=True)

        # Error by type chart
        fig = px.pie(error_summary, values='count', names='error', title='Distribution of Error Types')
        st.plotly_chart(fig)

        # Errors by column and type
        fig = px.bar(error_by_column, x='column', y='count', color='error', title='Error Distribution by Column and Type')
        st.plotly_chart(fig)

        # Filter issues where 'suggestion' is an empty string
        issues_without_suggestions = st.session_state.issues_df_final[st.session_state.issues_df_final['suggestion'] == '']

        # Group the issues by 'row' and create the columns based on the new logic
        issue_details = (
            issues_without_suggestions.groupby('row').agg(
                issue_detail=('error', lambda x: ', '.join(x)),  # Concatenate error strings
                number_of_errors=('error', 'count'),  # Count number of errors
                column_with_problems=('column', lambda x: list(x))  # List of problematic columns
            )
        )

        st.divider()

        # Select only rows in st.session_state.df where index is in 'row' of issues_df_final
        df_with_issues = st.session_state.df.loc[st.session_state.df.index.isin(issues_without_suggestions['row'])].copy()

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
