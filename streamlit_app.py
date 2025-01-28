import streamlit as st

st.set_page_config(page_title="Trade Performance Analyzer", layout="wide")

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Trade Performance Analyzer", "Prepare Data", "Analyze Trade Performance"])

# Check for query parameters to handle button navigation
# Replace st.experimental_get_query_params with st.query_params
query_params = st.query_params
if "page" in query_params:
    page = query_params["page"][0]

if page == "Trade Performance Analyzer":
    import app_main
    app_main.main()
elif page == "Prepare Data":
    import prepare_data
    prepare_data.main()
elif page == "Analyze Trade Performance":
    import perform_analyzer
    perform_analyzer.main()