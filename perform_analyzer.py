import os
import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
log_file = Path(f"trade_data_analysis_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
    st.title("Analyze Trade Performance")

    # Load saved dataset
    if st.button("Load Saved Dataset"):
        df = load_saved_dataset()
        if df is not None:
            st.subheader("Trade data:")
            st.dataframe(df)

            # Analyze trades
            if st.button("Analyze Trades"):
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