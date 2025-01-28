import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from pathlib import Path

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

# Main function
def main():
    st.title("Prepare Data")

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

if __name__ == "__main__":
    main()