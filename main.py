import streamlit as st
import pandas as pd

import functions

functions.set_page_definitition()
st.title("Petabytes PoC")


allInvoicelines = "data/Invoice+Lines-2024-10-21-15-29-05.csv"
df = functions.load_cvs_data(allInvoicelines)


df = df[df['Type'] != 'Header']
df = df[df['Product Name'] != 'Subscription Fee']
df = df[df['Product Name'] != 'Cancellation Fee']
df = df[df['Client Contact Code'] != 'ezyVet']
# df=df2
st.dataframe(df)
st.write(len(df))



# st.bar_chart(df[["Staff Member", "Consult ID"]],
#              x="Staff Member",
#              y="Consult ID")

# st.dataframe(df["Product Group"])


product_cat = st.multiselect("Pick which product categories",
                            list(df["Product Group"].unique())[::-1],
                             None)
# date_range = st.slider("Pick your date range",
#                        2010, 2019,
#                        (2010, 2019))

# st.dataframe(product_cat)
# st.dataframe(df["Product Group"])

if product_cat:
    chart_data = df[df["Product Group"].isin(product_cat)]
    # chart_data = chart_data[chart_data['year'].between(date_range[0], date_range[1])]
    # chart_data['year'] = chart_data['year'].astype(str)

    st.write(len(chart_data))

    # Count the occurrences of each name and creates a list of names and counts
    chart_data = chart_data['Created By'].value_counts()
    st.dataframe(chart_data)
    #
    # Convert to a DataFrame for plotting
    chart_data = chart_data.reset_index()
    st.dataframe(chart_data)
    #
    # name_counts_df.columns = ['Created By', 'count']

# Display the bar chart in Streamlit
st.write("Name Occurrences:")
st.bar_chart(chart_data.set_index('Created By'))



# List all column names
columns = df.columns.tolist()
print(columns)

# In a Streamlit app, you can display them like this:
import streamlit as st
st.write("Column names:")
st.write(columns)