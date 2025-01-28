import streamlit as st

def main():
    st.title("Trade Performance Analyzer")
    st.write("Welcome to the Trade Performance Analyzer. Use the navigation menu to prepare data or analyze trade performance.")
    
    if st.button("Go to Prepare Data"):
        # Replace st.experimental_set_query_params with st.set_query_params
        st.set_query_params(page="Prepare Data")

if __name__ == "__main__":
    main()