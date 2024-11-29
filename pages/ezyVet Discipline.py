import streamlit as st
import pandas as pd
import datetime
import altair as alt
import functions
import plotly.express as px

# General page setup
functions.set_page_definitition()

functions.initialize_session_state()

st.title("ezyVet Discipline")



# df = functions.load_newest_file("NonApprovedInvoiceLinesSinceNewRule")
df = functions.prepare_invoice_lines("NonApprovedInvoiceLinesSinceNewRule")

options = ["Vets", "Nurses", "Cops", "Locums", "Students", "Others"]
selection = st.segmented_control(
    "Select which roles to include in the analysis", options, selection_mode="multi"
)

# only show Others in the created_by_category column
df = df[df['created_by_category'].isin(selection)]

# add a tickbox filter for petcare_plan_in_vera. If the box is ticked only include "Plan not in Vera" and "PCAV1-DOG" from the column petcare_plan_in_vera
if st.checkbox('Exclude PetCare Premium'):
    df = df[df['petcare_plan_in_vera'].isin(['Plan not in Vera', 'PCAV1-DOG'])]

# st.dataframe(df)

# group by Created by and invoice number and count the unique number of invoice numbers per created_by and sum the total invoiced amount
df1 = df.groupby(['Created By', 'Invoice #']).agg({'Total Invoiced (incl)': 'sum'}).reset_index()
df1 = df1.groupby('Created By').agg({'Invoice #': 'nunique', 'Total Invoiced (incl)': 'sum'}).reset_index()
df1.columns = ['Created By', 'Total Invoices', 'Total Invoiced (incl)']

st.dataframe(df1)
st.subheader(":hash:   Number of non-approved invoices by staff member")

# create a plotly express bar chart where x is the created by, y is the total invoices, and color is the created by category
fig = px.bar(df1, x='Created By', y='Total Invoices', color='Created By')
st.plotly_chart(fig)

# # group by Created by and count unique invoice numbers
# df3 = df.groupby('Created By').agg({'Invoice #': 'nunique'}).reset_index()
# df3.columns = ['Created By', 'Total Invoices']
# # create a plotly express bar chart where x is the created by, y is the total invoices
# fig = px.bar(df3, x='Created By', y='Total Invoices')
# st.plotly_chart(fig)


# group by Invoice # and sum the total invoiced amount
df2 = df.groupby('Created By').agg({'Total Invoiced (incl)': 'sum'}).reset_index()

st.subheader(":pound:   Total Invoice Amount in non-approved invoices by staff member")
# create a plotly express bar chart where x is the created by, y is the total invoiced, and color is the created by category
fig = px.bar(df2, x='Created By', y='Total Invoiced (incl)', color='Created By')
st.plotly_chart(fig)



