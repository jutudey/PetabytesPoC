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
# df=df2
st.dataframe(df)
st.write(len(df))



st.bar_chart(df[["Staff Member", "Consult ID"]],
             x="Staff Member",
             y="Consult ID")

# List all column names
columns = df.columns.tolist()
print(columns)

# In a Streamlit app, you can display them like this:
import streamlit as st
st.write("Column names:")
st.write(columns)