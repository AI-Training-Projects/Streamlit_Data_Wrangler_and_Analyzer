# Enhancements To Stock Data Wrangler and Analyzer: 


1) TODO: Let the user Sort the dataframe immediately after importing it the first time.  Save it with the sorted configuration.  

2) TODO: Make all grid displays the "full" width.  

3) TODO: Improve file handling to store processed files and logfiles outside "Project Main" folder.
    a) Modify the program to store run "logfiles" in the "Logfiles" folder.
    b) Modify the program to store run "cleaned_datasets" in the "Logfiles" folder.


3) TODO: Make separate workflow pages in a Streamlit Sidebar Navigator
    Move the "Prepare Data" into a separate page in the Streamlit Sidebar. 
    Add the "Analyze Data" into its own page in the Streamlit Sidebar. 


TODO: Change dropdown menus for selecting datatypes to an interactive iTables grid with "in-place menus". 

TODO: Cache all datagrids after they are loaded and displayed, i.e., no screen refresh when events fire.

TODO: Use "best practices" approach stated in this notebook (Making_Streamlit_Pandas_iTables_and_PyArrow_Play_Nicely_Together.ipynb) to make pandas, iTables, and streamlit work together better.  
    
    Based on the discussion below, convert or intentionally filter out column values (rows) with mixed data types that will cause problems with Arrow, OR only use Pandas-Arrow compatible datatypes by converting problematic Pandas objects to the appropriate Arrow datatype

    Eliminate this error: 2025-01-27 21:12:37.354 Serialization of dataframe to Arrow table was unsuccessful due to: ("Could not convert dtype('int64') with type numpy.dtypes.Int64DType: did not recognize Python value type when inferring an Arrow data type", 'Conversion failed for column Column_Datatype with type object'). Applying automatic fixes for column types to make the dataframe Arrow-compatible."

    ### Best Practices for Using These Packages Together

        1. **Ensure Data Type Compatibility**:
        - Before passing a DataFrame to Streamlit or iTables, ensure that all columns have compatible data types.
        - Convert `datetime` columns to Pandas `datetime64` format.
        - Ensure that all columns have consistent data types (e.g., no mixed types within a column).

        2. **Use Explicit Data Type Conversions**:
        - Explicitly convert columns to the appropriate data types using Pandas' `astype` method.
        - For example, convert `datetime` columns using `pd.to_datetime`.

        3. **Handle Mixed Data Types**:
        - If a column contains mixed data types, convert it to a single data type that is compatible with Arrow.
        - For example, convert a column with mixed integers and strings to strings using `astype(str)`.

        4. **Check Data Types Before Serialization**:
        - Use Pandas' `dtypes` attribute to check the data types of all columns before passing the DataFrame to Streamlit or iTables.
        - Ensure that all data types are compatible with Arrow.

