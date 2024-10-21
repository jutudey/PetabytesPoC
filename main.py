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

st.sidebar.subheader("Set the date range")


# select date range
start_date = st.sidebar.date_input("Start date",min_value=datetime.date(2023,12,4), format="DD.MM.YYYY")
# st.write("start date", start_date)
end_date = st.sidebar.date_input("End date",format="DD.MM.YYYY")
# st.write("end date", end_date)

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