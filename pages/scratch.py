import pandas as pd
import streamlit as st
import datetime

# Example DataFrame with 'DD-MM-YYYY' date format in 'Invoice Date' column
data = {
    'Invoice Date': ['30-11-2023', '15-12-2023', '01-12-2023', '05-11-2023'],
    'Amount': [200, 150, 300, 250]
}
df = pd.DataFrame(data)

# Convert 'Invoice Date' from string to datetime format with the correct 'DD-MM-YYYY' format
df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%d-%m-%Y')

# Date input in Streamlit with default date format
start_date = st.date_input("Start date", min_value=datetime.date(2023, 12, 4))
st.write("start date", start_date)
end_date = st.date_input("End date")
st.write("end date", end_date)

# Convert start_date and end_date to pandas Timestamps
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter the DataFrame to only include rows between the start and end dates
df_filtered = df[(df['Invoice Date'] >= start_date) & (df['Invoice Date'] <= end_date)]

# Display the filtered DataFrame
st.write("Filtered DataFrame:")
st.write(df_filtered)