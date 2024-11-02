import streamlit as st
import pandas as pd
import functions
import locale


# sets the app details
app_name = functions.set_page_definitition()

# Load the DataFrame from session state
df = st.session_state.get('df')

# if df is not in sessions state, generate it
if df is None:
    df = functions.prepare_invoice_lines()

#
#
# appointments_path = "data/appointments.csv"
# procedures_path = "data/Procedures.csv"

st.title("Inspect the Invoice Lines data")

filter_col, summary_col = st.columns([2,1])

with filter_col:
    filtered_df = functions.filter_dataframe(df)
    # st.dataframe(filtered_df)



number_invoice_lines = (filtered_df["Invoice Line ID"].count())
sum_internal_cost = locale.currency((filtered_df["Product Cost"].sum()), grouping=True)
sum_sales_price = locale.currency((filtered_df['Standard Price(incl)'].sum()), grouping=True)
theoretical_profit = (filtered_df['Standard Price(incl)'].sum()) - (filtered_df["Product Cost"].sum())
theoretical_profit = locale.currency((theoretical_profit), grouping=True)
sum_actual_invoiced = locale.currency(filtered_df['Total Invoiced (incl)'].sum(), grouping=True)
applied_discount = (filtered_df['Standard Price(incl)'].sum()) - (filtered_df['Total Invoiced (incl)'].sum())
applied_discount = locale.currency((applied_discount), grouping=True)


st.sidebar.subheader(f"Number of Invoice Lines: {number_invoice_lines}")
st.sidebar.subheader(f"Sum Internal Cost: {sum_internal_cost}")
st.sidebar.subheader(f"Sum Sales Price: {sum_sales_price}")
st.sidebar.subheader(f"Theoretical Profit: {theoretical_profit}")
st.sidebar.subheader(f"Sum Actual Invoiced: {sum_actual_invoiced}")
st.sidebar.subheader(f"Applied Discounts: {applied_discount}")

st.dataframe(filtered_df[[
    'Invoice Line Time: Created', 'Invoice Line ID',
    'Invoice Date', 'Product Name', 'Product Description','Product Group','reporting_categories',

    # 'Type',
    # 'Parent Line ID', 'Invoice Line Date: Created',
    # 'Invoice Line Time: Created',
    'Created By', 'created_by_category',
    # 'Invoice Line Date: Last Modified', 'Invoice Line Time: Last Modified',
    # 'Last Modified By', 'Invoice Line Date', 'Invoice Line Time',
    # 'Department ID', 'Department', 'Inventory Location',
    'Client Contact Code',
    'Business Name', 'First Name', 'Last Name',
    # 'Email',
    'Animal Code', 'Animal Name', 'Species', 'Breed',
    #  'Invoice Line Reference',
    #  'Product Code',

    # 'Account',
    'Product Cost',

    # 'Staff Member ID', 'Staff Member',
    # 'Salesperson is Vet', 'Consult ID', 'Consult Number', 'Case Owner',
    # 'Qty',
    'Standard Price(incl)',
    # 'Discount(%)',
    'Discount(£)',
    # 'User Reason', 'Surcharge Adjustment', 'Surcharge Name',
    # 'Discount Adjustment', 'Discount Name', 'Rounding Adjustment',
    # 'Rounding Name', 'Price After Discount(excl)',
    # 'Tax per Qty After Discount',
    # 'Price After Discount(incl)',
    # 'Total Invoiced (excl)', 'Total Tax Amount',
    'Total Invoiced (incl)',
    # 'Total Earned(excl)', 'Total Earned(incl)', 'Payment Terms',
    #
]])
