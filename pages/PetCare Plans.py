import streamlit as st
import pandas as pd
import datetime
import functions
import plotly.express as px
import config

functions.set_page_definitition()
st.title("📦  PetCare Plan Analysis")

with st.spinner('Loading and preparing data...'):
    functions.initialize_session_state()

# Load the data from session state
invoice_lines = st.session_state.all_invoice_lines
payments = st.session_state.all_payments

# st.dataframe(payments)

###############################
# Choose the date range
###############################

st.sidebar.subheader("📃  Date Range")

date_options = [
    "Custom Range", "Today", "This Week", "This Week-to-date", "This Month", "This Month-to-date",
    "This Quarter", "This Quarter-to-date", "This Year", "This Year-to-date", "This Year-to-last-month",
    "Yesterday", "Last Week", "Last Month",
    "Last Quarter", "Last Year",
    "Last 30 Days", "Last 60 Days", "Last 90 Days", "Last 365 Days"
]
selected_option = st.sidebar.selectbox("Select a date filter", date_options, index=date_options.index("This Year"))

# Get start and end dates based on the selected option
if selected_option == "Custom Range":
    custom_start = st.sidebar.date_input("Start date", min_value=datetime.date(2023, 11, 1), format="YYYY-MM-DD")
    custom_end = st.sidebar.date_input("End date", format="YYYY-MM-DD")
    start_date, end_date = functions.get_date_range(selected_option, custom_start, custom_end)
else:
    start_date, end_date = functions.get_date_range(selected_option)

# Convert start_date and end_date to pandas Timestamps
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filter the invoice lines and payments data based on the selected date range
invoice_lines_grouped = invoice_lines.groupby(['Invoice Date', 'petcare_plan_in_vera'])['Product Cost'].sum().reset_index().round(2)
# rename Invoice Date to Date
invoice_lines_grouped.columns = ['Date', 'petcare_plan_in_vera', 'Cost']
payments_grouped = payments.groupby(['tl_Date', 'petcare_plan_in_vera'])['tl_Revenue'].sum().reset_index().round(2)
# rename tl_Date to Date
payments_grouped.columns = ['Date', 'petcare_plan_in_vera', 'Revenue']
# payments_grouped

# concatenate invoice_lines_grouped and payments_grouped by where Invoice Date = tl_Date and petcare_plan_in_vera = petcare_plan_in_vera
merged_df = pd.merge(invoice_lines_grouped, payments_grouped, on=['Date', 'petcare_plan_in_vera'], how='inner')
merged_df["month_year"] = merged_df['Date'].dt.to_period('M')
# Filter the Invoice Lines to only include rows between the start and end dates
merged_df = merged_df[(merged_df['Date'] >= start_date) & (merged_df['Date'] <= end_date)]
merged_df['petcare_plan_group'] = merged_df['petcare_plan_in_vera'].apply(
    lambda x: 'Dogs' if x[:3] in config.dogs else
    ('Cats' if x[:3] in config.cats else
     ('Complex' if x[:3] in config.complex_cases else
      ('Rabbits/Ferrets' if x[:3] in config.rabbits_ferrets else
       ('Small Furries' if x[:3] in config.small_furries else
        'Other')))))

###############################
# Choose the PetCare Plans
###############################

st.sidebar.subheader("📦  PetCare Plans")

selection = st.sidebar.pills("Grouping level", options=["Individual", "Grouped", "All"], key="selection")

if selection    == "Individual":
    petcareplan_to_display = st.sidebar.multiselect(
        "Select individual PetCare Plans",
        sorted(invoice_lines["petcare_plan_in_vera"].unique()),
        default=None
    )

    if petcareplan_to_display:
        merged_df = merged_df[merged_df["petcare_plan_in_vera"].isin(petcareplan_to_display)]
    #     group merged_df by petcare_plan_in_vera and month and summarize the Cost and Revenue
        merged_df = merged_df.groupby(['petcare_plan_in_vera', merged_df['month_year']]).agg({'Cost': 'sum', 'Revenue': 'sum'}).reset_index()


        # Create a bar chart showing the total cost and revenue for each petcare plan
        fig = px.bar(merged_df, x='petcare_plan_in_vera', y=['Cost', 'Revenue'], barmode='group', title='Cost and Revenue per PetCare Plan ')
        st.plotly_chart(fig)

        # add a column to merged_df that calculates the profit
        merged_df['Profit'] = merged_df['Revenue'] - merged_df['Cost']
        merged_df['month_year'] = merged_df['month_year'].astype(str)
        # Create a line chart showing the profit for each petcare plan where the y axis is the profit and the x axis is the petcare plan. Each line should be colored based on the petcare_plan_in_vera
        fig = px.line(
            merged_df,
            x='month_year',
            y='Profit',
            color='petcare_plan_in_vera',
            title='Profit over Time for Different Pet Care Plans',
            labels={'month_year': 'Month-Year', 'Profit': 'Profit'}
        )

        st.plotly_chart(fig)

if selection == "Grouped":
    petcareplan_group_to_display = st.sidebar.multiselect(
        "Select PetCare Plan groups",
        sorted(invoice_lines["petcare_plan_group"].unique()),
        default=None
    )

    if petcareplan_group_to_display:
        merged_df = merged_df[merged_df["petcare_plan_group"].isin(petcareplan_group_to_display)]
        #     group merged_df by petcare_plan_in_vera and month and summarize the Cost and Revenue
        merged_df = merged_df.groupby(['petcare_plan_group', merged_df['month_year']]).agg(
            {'Cost': 'sum', 'Revenue': 'sum'}).reset_index()

        # Create a bar chart showing the total cost and revenue for each petcare plan
        fig = px.bar(merged_df, x='petcare_plan_group', y=['Cost', 'Revenue'], barmode='group',
                     title='Cost and Revenue per PetCare Plan Group')
        st.plotly_chart(fig)

        # add a column to merged_df that calculates the profit
        merged_df['Profit'] = merged_df['Revenue'] - merged_df['Cost']
        merged_df['month_year'] = merged_df['month_year'].astype(str)
        # Create a line chart showing the profit for each petcare plan where the y axis is the profit and the x axis is the petcare plan. Each line should be colored based on the petcare_plan_in_vera
        fig = px.line(
            merged_df,
            x='month_year',
            y='Profit',
            color='petcare_plan_group',
            title='Profit over Time for Different Pet Care Plan Groups',
            labels={'month_year': 'Month-Year', 'Profit': 'Profit'}
        )

        st.plotly_chart(fig)

if selection == "All":
    merged_df = merged_df.groupby([merged_df['month_year']]).agg(
        {'Cost': 'sum', 'Revenue': 'sum'}).reset_index()

    # Create a bar chart showing the total cost and revenue for each petcare plan
    merged_df['all'] = 'All'
    fig = px.bar(merged_df, x='all', y=['Cost', 'Revenue'], barmode='group',
                 title='Cost and Revenue per PetCare Plan Group')
    st.plotly_chart(fig)

    # add a column to merged_df that calculates the profit
    merged_df['Profit'] = merged_df['Revenue'] - merged_df['Cost']
    merged_df['month_year'] = merged_df['month_year'].astype(str)
    # Create a line chart showing the profit for each petcare plan where the y axis is the profit and the x axis is the petcare plan. Each line should be colored based on the petcare_plan_in_vera
    fig = px.line(
        merged_df,
        x='month_year',
        y='Profit',
        color='all',
        title='Profit over Time for Different Pet Care Plan Groups',
        labels={'month_year': 'Month-Year', 'Profit': 'Profit'}
    )

    st.plotly_chart(fig)

# Filter by petcare plans if any are selected


st.sidebar.checkbox("Detailed data extracts", value=False, key="display_details")
if st.session_state.display_details:
    # add a tickbox that allows the user to choose whether to display the invoice lines and payments data
    display_data = st.checkbox("Display Monthly summaries", value=False, key="display_data")
    if display_data:
        merged_df

    if selection == "Individual":
        display_data2 = st.checkbox("Display Invoice Lines and Payments details", value=False, key="display_data2")
        if display_data2:
            st.subheader('Invoice Lines')
            invoice_lines = invoice_lines[invoice_lines["petcare_plan_in_vera"].isin(petcareplan_to_display)]
            invoice_lines = invoice_lines[(invoice_lines['Invoice Date'] >= start_date) & (invoice_lines['Invoice Date'] <= end_date)]
            invoice_lines

            st.subheader('Payments from Vera')

            payments = payments[payments["petcare_plan_in_vera"].isin(petcareplan_to_display)]
            payments = payments[(payments['tl_Date'] >= start_date) & (payments['tl_Date'] <= end_date)]
            payments

