import streamlit as st
import pandas as pd
import functions


# Set the app details
app_name = functions.set_page_definitition()

# Load the DataFrame from session state
df = st.session_state.get('df')

# If df is not in session state, generate it
if df is None:
    df = functions.prepare_invoice_lines()
    st.session_state['df'] = df  # Save it to session state

st.title("🛢️️  Inspect the Invoice Lines Data")

filter_col, summary_col = st.columns([2, 1])

with filter_col:
    filtered_df = functions.filter_dataframe(df)

# Summary calculations
number_invoice_lines = filtered_df["Invoice Line ID"].count()
sum_internal_cost = f"£{filtered_df['Product Cost'].sum():,.2f}"
sum_sales_price = f"£{filtered_df['Standard Price(incl)'].sum():,.2f}"
theoretical_profit_value = filtered_df['Standard Price(incl)'].sum() - filtered_df["Product Cost"].sum()
theoretical_profit = f"£{theoretical_profit_value:,.2f}"
sum_actual_invoiced = f"£{filtered_df['Total Invoiced (incl)'].sum():,.2f}"
applied_discount_value = filtered_df['Standard Price(incl)'].sum() - filtered_df['Total Invoiced (incl)'].sum()
applied_discount = f"£{applied_discount_value:,.2f}"

# Sidebar summaries
st.sidebar.subheader(f"Number of Invoice Lines: {number_invoice_lines}")
st.sidebar.subheader(f"Sum Internal Cost: {sum_internal_cost}")
st.sidebar.subheader(f"Sum Sales Price: {sum_sales_price}")
st.sidebar.subheader(f"Theoretical Profit: {theoretical_profit}")
st.sidebar.subheader(f"Sum Actual Invoiced: {sum_actual_invoiced}")
st.sidebar.subheader(f"Applied Discounts: {applied_discount}")

# Display the filtered DataFrame
st.dataframe(filtered_df[[
    'Invoice Line Date: Created', 'Invoice Line ID',
    'Invoice Date', 'Product Name', 'Product Description', 'Product Group', 'reporting_categories',
    'Created By', 'created_by_category', 'Client Contact Code',
    'Business Name', 'First Name', 'Last Name',
    'Animal Code', 'Animal Name', 'Species', 'Breed',
    'Product Cost', 'Standard Price(incl)', 'Discount(£)', 'Total Invoiced (incl)',
]])
