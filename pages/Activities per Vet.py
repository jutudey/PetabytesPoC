import streamlit as st
import pandas as pd
import datetime
import functions

functions.set_page_definitition()
st.title("Petabytes PoC")

allInvoicelines = "data/Invoice Lines-2024-10-25-17-47-28.csv"
df = functions.load_cvs_data(allInvoicelines)

# Convert 'Invoice Date' from string to datetime format
df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%d-%m-%Y')

df = df[df['Type'] != 'Header']
df = df[df['Product Name'] != 'Subscription Fee']
df = df[df['Product Name'] != 'Cancellation Fee']
df = df[df['Client Contact Code'] != 'ezyVet']
# df=df2
# st.dataframe(df)
# st.write(len(df))


medication_groups = ["Medication - Oral", "Medication - Injectable", "Medication - Flea & Worm", "Medication - Topical", "Anaesthesia", "Medication - Miscategorised ", "Medication - Other"]
vaccination_groups = ["Vaccinations", "Vaccine Stock"]
consultations = ["Consultations"]
procedures_groups = ["Procedures", "Dental", "Surgery", "Fluids  Therapy"]
diagnostics_groups = ["Diagnostic Procedures", "Diagnostic Imaging"]
lab_work_groups = ["Idexx External", "Idexx In-House"]
hospitalisation = ["Boarding", "Hospitalisation"]
consumables = ["Consumables", "Surgery Consumables", "Suture Material", "Bandages"]
service_fee = ["Service Fee"]
pts = ['Euthanasia & Cremation', 'Individual Cremations']

# Data Cleaning
# Change miscategorised Meloxicam and Methadone away from Consultations
df['Product Group'] = df.apply(lambda row: "Medication - Miscategorised " if row['Product Name'] == "(1) Includes: Meloxicam and Methadone" else row['Product Group'], axis=1)

# Set 'Medication' for medication groups
df['reporting_categories'] = df['Product Group'].apply(lambda x: "Medication" if x in medication_groups else None)

# Set 'other categories' , without overwriting existing non-null values
df['reporting_categories'] = df.apply(lambda row: "Vaccinations" if row['Product Group'] in vaccination_groups else row['reporting_categories'], axis=1)
df['reporting_categories'] = df.apply(lambda row: "Consultations" if row['Product Group'] in consultations else row['reporting_categories'], axis=1)
df['reporting_categories'] = df.apply(lambda row: "Diagnostic" if row['Product Group'] in diagnostics_groups else row['reporting_categories'], axis=1)
df['reporting_categories'] = df.apply(lambda row: "Procedures" if row['Product Group'] in procedures_groups else row['reporting_categories'], axis=1)
df['reporting_categories'] = df.apply(lambda row: "Lab Work" if row['Product Group'] in lab_work_groups else row['reporting_categories'], axis=1)
df['reporting_categories'] = df.apply(lambda row: "Hospitalisation" if row['Product Group'] in hospitalisation else row['reporting_categories'], axis=1)
df['reporting_categories'] = df.apply(lambda row: "Consumables" if row['Product Group'] in consumables else row['reporting_categories'], axis=1)
df['reporting_categories'] = df.apply(lambda row: "Service Fee" if row['Product Group'] in service_fee else row['reporting_categories'], axis=1)
df['reporting_categories'] = df.apply(lambda row: "PTS & Creamations" if row['Product Group'] in pts else row['reporting_categories'], axis=1)
df['reporting_categories'] = df['reporting_categories'].fillna("Misc")


st.sidebar.subheader("Select a date filter")

date_options = [
    "Custom Range", "Today", "This Week", "This Week-to-date", "This Month", "This Month-to-date",
    "This Quarter", "This Quarter-to-date", "This Year", "This Year-to-date", "This Year-to-last-month",
    "Yesterday", "Last Week", "Last Month",
    "Last Quarter", "Last Year",
    "Last 30 Days", "Last 60 Days", "Last 90 Days", "Last 365 Days",
    # "Next Week", "Next 4 Weeks", "Next Month", "Next Quarter", "Next Year"
    ]
selected_option = st.sidebar.selectbox("Pick a date range", date_options)

# Get start and end dates based on the selected option
if selected_option == "Custom Range":
    custom_start = st.sidebar.date_input("Start date", min_value=datetime.date(2023, 12, 4), format="YYYY-MM-DD")
    custom_end = st.sidebar.date_input("End date", format="YYYY-MM-DD")
    start_date, end_date = functions.get_date_range(selected_option, custom_start, custom_end)
else:
    start_date, end_date = functions.get_date_range(selected_option)

# Convert start_date and end_date to pandas Timestamps
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)


product_cat = st.multiselect("Pick which product categories you want to examine",
                            list(df["reporting_categories"].unique())[::-1],
                             None)


# st.dataframe(product_cat)
# st.dataframe(df["reporting_categories"])

df = df[df["reporting_categories"].isin(product_cat)]

# Filter the DataFrame to only include rows between the start and end dates
df_filtered = df[(df['Invoice Date'] >= start_date) & (df['Invoice Date'] <= end_date)]
df = df_filtered
# Display the filtered DataFrame
# st.dataframe(df_filtered)

if product_cat:
    # by count
    chart_data = df['Created By'].value_counts()
    chart_items = len(df)
    chart_start_date = start_date.strftime("%B %d, %Y")
    chart_end_date = end_date.strftime("%B %d, %Y")

    # by Sum
    # Group by 'Created By' and aggregate the sum of 'Standard Price(incl)'
    chart_data2 = df.groupby('Created By')['Standard Price(incl)'].sum().reset_index(). round(2)

    # Rename columns to be more descriptive
    chart_data2.columns = ['Created By', 'Total internal cost']

    # Display the table in Streamlit
    # st.dataframe(chart_data2)

    st.subheader(f"Showing data based on {chart_items} invoices lines from the period between {chart_start_date} and {chart_end_date}")

    # Create 5 columns where the last 4 are merged into one
    col1, col2 = st.columns([1, 4])  # The first column is narrow, the second one spans the width of four columns

    with col1:
        # Count the occurrences of each name and creates a list of names and counts
        st.dataframe(chart_data)


    # Convert to a DataFrame for plotting
    chart_data = chart_data.reset_index()
    # st.dataframe(chart_data)
            #
            # name_counts_df.columns = ['Created By', 'count']
    with col2:
        # Display the bar chart in Streamlit
        # st.write("Name Occurrences:")
        st.bar_chart(chart_data.set_index('Created By'))

    col1, col2 = st.columns([2, 4])  # The first column is narrow, the second one spans the width of four columns

    with col1:
        # Reset the index so that it's not included
        chart_data2_reset = chart_data2.reset_index(drop=True)

        # Display the DataFrame without index in Streamlit
        st.dataframe(chart_data2_reset)

    with col2:
        # Use the original DataFrame for plotting without resetting the index again
        st.bar_chart(chart_data2.set_index('Created By'))

    st.dataframe(df_filtered)

#
# # List all column names
# columns = df.columns.tolist()
# print(columns)
#
# # In a Streamlit app, you can display them like this:
# import streamlit as st
# st.write("Column names:")
# st.write(columns)