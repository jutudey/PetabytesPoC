import streamlit as st
import pandas as pd
import datetime
import functions

functions.set_page_definitition()
st.title("Petabytes PoC")

allInvoicelines = "data/Invoice+Lines-2024-10-21-15-29-05.csv"
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

st.sidebar.subheader("Select a date filter")

# Predefined date range options
date_options = ["Today", "This Week", "This Month", "This Quarter", "This Year", "Last Month", "Custom Range"]
selected_option = st.sidebar.selectbox("Pick a date range", date_options)

# Get today's date
today = datetime.date.today()

# Set default start and end dates based on the selected option
if selected_option == "Today":
    start_date = today
    end_date = today
elif selected_option == "This Week":
    start_date = today - datetime.timedelta(days=today.weekday())  # Start of the week (Monday)
    end_date = today
elif selected_option == "This Month":
    start_date = today.replace(day=1)  # First day of this month
    end_date = today
elif selected_option == "This Quarter":
    current_month = today.month
    quarter_start_month = current_month - (current_month - 1) % 3
    start_date = today.replace(month=quarter_start_month, day=1)
    end_date = today
elif selected_option == "This Year":
    start_date = today.replace(month=1, day=1)  # First day of this year
    end_date = today
elif selected_option == "Last Month":
    first_day_of_this_month = today.replace(day=1)
    start_date = first_day_of_this_month - datetime.timedelta(days=1)  # Last day of the previous month
    start_date = start_date.replace(day=1)  # First day of the previous month
    end_date = first_day_of_this_month - datetime.timedelta(days=1)
else:
    # Custom date range
    start_date = st.sidebar.date_input("Start date", min_value=datetime.date(2023, 12, 4), format="DD.MM.YYYY")
    end_date = st.sidebar.date_input("End date", format="DD.MM.YYYY")

# Convert start_date and end_date to pandas Timestamps
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)





product_cat = st.multiselect("Pick which product categories you want to examine",
                            list(df["Product Group"].unique())[::-1],
                             None)


# st.dataframe(product_cat)
# st.dataframe(df["Product Group"])

df = df[df["Product Group"].isin(product_cat)]

# Filter the DataFrame to only include rows between the start and end dates
df_filtered = df[(df['Invoice Date'] >= start_date) & (df['Invoice Date'] <= end_date)]
df = df_filtered
# Display the filtered DataFrame
# st.dataframe(df_filtered)

if product_cat:

    # st.write(len(chart_data))

    st.subheader(f"Showing data from the period between {start_date} and {end_date}")

    # Create 5 columns where the last 4 are merged into one
    col1, col2 = st.columns([1, 4])  # The first column is narrow, the second one spans the width of four columns

    with col1:
        # Count the occurrences of each name and creates a list of names and counts
        chart_data = df['Created By'].value_counts()
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

    st.dataframe(df)

#
# # List all column names
# columns = df.columns.tolist()
# print(columns)
#
# # In a Streamlit app, you can display them like this:
# import streamlit as st
# st.write("Column names:")
# st.write(columns)