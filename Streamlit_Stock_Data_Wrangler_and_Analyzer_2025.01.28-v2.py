"""
Workflow outline for the initial inspection of the uploaded XLSX and CSV files:

File Upload:
    Use st.file_uploader to allow the user to upload an XLSX or CSV file.
    If no file is uploaded, stop the execution using st.stop().

Read the File:
    Check the file extension to determine whether it is an XLSX or CSV file.
    Use pd.read_excel for XLSX files and pd.read_csv for CSV files to read the file into a DataFrame.

Clean Column Names:
    Use the clean_column_names function to clean the column names by replacing spaces, parentheses, and special characters with underscores.

Initial Data Inspection:
    Display the first few rows of the uploaded file using st.write(df.head()).

Extract Column Headers:
    Extract the column headers from the DataFrame and store them in a list called file_header_labels_list.
    Display the extracted column headers to the user using st.write(file_header_labels_list).

Analyze and Convert Date Columns:
    Iterate through each column in the DataFrame and check if the column contains string representations of dates or datetimes.
    Convert detected date/datetime strings to appropriate data types using pd.to_datetime.
    Split datetime columns into separate date and time columns using the column header label as a prefix for the new column names (e.g., "Opened" becomes "Date_Opened" and "Time_Opened").

Display Intermediate Data:
    Use st.expander to create a collapsible container for displaying the DataFrame immediately after splitting columns.

Display Processed Data:
    Use st.expander to create a collapsible container for displaying the fully processed DataFrame.

Use iTables for DataFrame Display:
    Import and configure iTables for DataFrame display, paging, and filtering.
    Use nest_asyncio to handle iTables events inside the Streamlit event loop.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from itables import show, init_notebook_mode
import nest_asyncio
import pyarrow as pa
from datetime import datetime
import logging
from pathlib import Path
import os
import io
import zipfile

# Initialize iTables
init_notebook_mode()

# Set Streamlit to wide mode
st.set_page_config(layout="wide")

nest_asyncio.apply()

# Set up logging
log_file = Path(f"trade_data_preparation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to clean column names
def clean_column_names(df):
    return df.rename(columns=lambda x: x.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', ''))

# Function to display initial data inspection
def display_initial_inspection(df):
    st.subheader("Initial Data Inspection")
    st.write("First few rows of the uploaded file:")
    st.write(df.head())

# Function to display column headers and datatypes
def display_column_headers(df):
    st.subheader("Extracted Column Headers and Datatypes")
    headers_df = pd.DataFrame({
        'Column_Name': df.columns,
        'Column_Datatype': df.dtypes
    })
    st.dataframe(headers_df)

# Function to create datatype selection options
def create_datatype_options(current_type):
    options = []
    if current_type == 'object':
        options = ['int64', 'float64', 'datetime64', 'object']
    elif current_type in ['int64', 'float64']:
        options = ['int64', 'float64', 'object']
    elif 'datetime64' in current_type:
        options = ['datetime64', 'object']
    else:
        options = ['object']
    return options

# Function to convert datatypes
def convert_datatypes(df, datatype_map):
    for col, new_type in datatype_map.items():
        try:
            if new_type == 'datetime64':
                df[col] = pd.to_datetime(df[col], errors='coerce')
            else:
                df[col] = df[col].astype(new_type)
            logging.info(f"Converted column {col} to {new_type}")
        except Exception as e:
            logging.error(f"Error converting column {col} to {new_type}: {str(e)}")
            st.error(f"Error converting column {col} to {new_type}: {str(e)}")
    return df

# Function to preview data after datatype conversion
def preview_data(df, datatype_map):
    st.subheader("Preview of Data After Datatype Conversion")
    st.write("You can sort the DataFrame by clicking on the column headers.")
    sorted_df = st.dataframe(df)
    st.write(df.dtypes)
    return sorted_df

# Function to save sorted dataset
def save_sorted_dataset(df, filename):
    try:
        df.to_csv(filename, index=False)
        logging.info(f"Successfully saved sorted dataset to {filename}")
        st.success(f"Successfully saved sorted dataset to {filename}")
    except Exception as e:
        logging.error(f"Error saving sorted dataset to {filename}: {str(e)}")
        st.error(f"Error saving sorted dataset to {filename}: {str(e)}")

# Function to load saved dataset
def load_saved_dataset():
    saved_files = [f for f in os.listdir() if f.startswith('trade_performance_dataset_cleaned_') and f.endswith('.xlsx')]
    if saved_files:
        selected_file = st.selectbox("Select a saved dataset", saved_files)
        try:
            df = pd.read_excel(selected_file)
            logging.info(f"Loaded saved dataset from {selected_file}")
            st.success(f"Loaded saved dataset from {selected_file}")
            return df
        except Exception as e:
            logging.error(f"Error loading dataset from {selected_file}: {str(e)}")
            st.error(f"Error loading dataset from {selected_file}: {str(e)}")
    else:
        st.info("No saved datasets found.")
        return None

# Main function
def main():
    st.title("Trade Transaction Performance Analyzer")

    # File upload
    file = st.file_uploader("Upload your XLSX or CSV file", type=["xlsx", "csv"])
    if not file:
        st.stop()

    # Read the file
    @st.cache_data
    def read_file(file):
        try:
            if file.name.endswith('.xlsx'):
                return pd.read_excel(file)
            else:
                return pd.read_csv(file)
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            return None

    df = read_file(file)
    if df is None:
        return

    # Clean column names
    @st.cache_data
    def clean_columns(df):
        return clean_column_names(df)

    df = clean_columns(df)

    # Display initial data inspection
    display_initial_inspection(df)

    # Display column headers and datatypes
    display_column_headers(df)

    # Create datatype selection options
    datatype_options = {col: create_datatype_options(str(dtype)) for col, dtype in df.dtypes.items()}

    # Create interactive grid for datatype selection
    with st.expander("Select Datatypes"):
        datatype_map = {}
        for col, options in datatype_options.items():
            current_type = str(df[col].dtype)
            if 'datetime64' in current_type:
                current_type = 'datetime64'
            datatype_map[col] = st.selectbox(f"Select datatype for {col}", options, index=options.index(current_type))

    # Preview data after datatype conversion
    if st.button("Preview Data After Datatype Conversion"):
        @st.cache_data
        def convert_and_preview(df, datatype_map):
            df_converted = convert_datatypes(df.copy(), datatype_map)
            return df_converted

        df_preview = convert_and_preview(df, datatype_map)
        sorted_df = preview_data(df_preview, datatype_map)

        # Save sorted dataset
        if st.button("Save Sorted Dataset"):
            current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
            sorted_csv_filename = f"trade_performance_dataset_sorted_{current_datetime}.csv"
            save_sorted_dataset(sorted_df, sorted_csv_filename)

    # Save dataset
    if st.button("Save Cleaned Dataset"):
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"trade_performance_dataset_cleaned_{current_datetime}.csv"
        xlsx_filename = f"trade_performance_dataset_cleaned_{current_datetime}.xlsx"
        
        df_cleaned = convert_datatypes(df, datatype_map)
        save_sorted_dataset(df_cleaned, csv_filename)
        df_cleaned.to_excel(xlsx_filename, index=False)
        logging.info(f"Successfully saved cleaned dataset to {csv_filename} and {xlsx_filename}")
        st.success(f"Successfully saved cleaned dataset to {csv_filename} and {xlsx_filename}")

    # Load saved dataset
    if st.button("Load Saved Dataset"):
        df = load_saved_dataset()
        if df is not None:
            display_initial_inspection(df)
            display_column_headers(df)

    # Analyze trades
    if st.button("Analyze Trades"):
        if 'df' not in locals():
            st.error("Please load or upload a dataset first.")
            return

        try:
            df['Cumulative_Profit_Loss'] = df['Profit_Loss'].cumsum()
        except Exception as e:
            st.error(f"Error calculating Cumulative Profit/Loss: {str(e)}")
            return

        # Display data
        st.subheader("Trade data:")
        st.dataframe(df)

        # Create and display plot
        st.subheader("Cumulative Profit/Loss Chart:")
        try:
            fig = px.line(df, x='Opened', y='Cumulative_Profit_Loss', title='Cumulative Profit/Loss Over Time')
            fig.update_xaxes(title='Date')
            fig.update_yaxes(title='Cumulative Profit/Loss')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating plot: {str(e)}")

        # Allow user to select date range for chart
        st.subheader("Select date range for chart:")
        try:
            start_date = st.date_input("Start date", value=df['Opened'].min())
            end_date = st.date_input("End date", value=df['Opened'].max())
        except Exception as e:
            st.error(f"Error selecting date range: {str(e)}")
            return

        # Filter data and create new plot
        try:
            filtered_df = df[(df['Opened'] >= start_date) & (df['Opened'] <= end_date)]
            fig = px.line(filtered_df, x='Opened', y='Cumulative_Profit_Loss', title='Filtered Cumulative Profit/Loss Over Time')
            fig.update_xaxes(title='Date')
            fig.update_yaxes(title='Cumulative Profit/Loss')
            st.subheader("Filtered Cumulative Profit/Loss Chart:")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error filtering data or creating filtered plot: {str(e)}")

if __name__ == "__main__":
    main()