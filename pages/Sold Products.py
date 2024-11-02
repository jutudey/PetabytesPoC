import streamlit as st
import pandas as pd
import datetime
import functions
import altair as alt

functions.set_page_definitition()
st.title("📦  Sold Products (ezyVet)")


# Load the DataFrame from session state
df = st.session_state.get('df')

# if df is not in sessions state, generate it
if df is None:
    df = functions.prepare_invoice_lines()


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
    custom_start = st.sidebar.date_input("Start date", min_value=datetime.date(2023, 12, 4), format="YYYY-MM-DD")
    custom_end = st.sidebar.date_input("End date", format="YYYY-MM-DD")
    start_date, end_date = functions.get_date_range(selected_option, custom_start, custom_end)
else:
    start_date, end_date = functions.get_date_range(selected_option)

# Convert start_date and end_date to pandas Timestamps
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

st.sidebar.subheader("📦  Products")

product_cat = st.sidebar.multiselect(
    "Select Product Category",
    sorted(df["reporting_categories"].unique()),
    default=None
)

# Checkbox to show detailed product information
show_category_details = st.sidebar.checkbox("Show Category Details")

# Tickboxes to include specific categories
include_vets = st.sidebar.checkbox("Include Vets", value=True)
include_nurses = st.sidebar.checkbox("Include Nurses", value=False)
include_cops = st.sidebar.checkbox("Include COPS", value=False)

# Filter by selected Created By categories
categories_to_include = []
if include_vets:
    categories_to_include.append('Vets')
if include_nurses:
    categories_to_include.append('Nurses')
if include_cops:
    categories_to_include.append('COPS')

if categories_to_include:
    df = df[df['created_by_category'].isin(categories_to_include)]

# Filter by product categories if any are selected
if product_cat:
    df = df[df["reporting_categories"].isin(product_cat)]

# Filter the DataFrame to only include rows between the start and end dates
df_filtered = df[(df['Invoice Line Date: Created'] >= start_date) & (df['Invoice Line Date: Created'] <= end_date)]



# Display the filtered DataFrame
if not df_filtered.empty:
    st.subheader(f"Showing data based on {len(df_filtered)} invoice lines from the period between {start_date.strftime('%B %d, %Y')} and {end_date.strftime('%B %d, %Y')}")

    # Create tabs for different aggregations
    tab1, tab2 = st.tabs(["By Number of Invoice Lines", "By Internal Cost"])

    with tab1:
        if show_category_details:
            # Show details by Product Name
            chart_data = df_filtered.groupby(['Created By', 'reporting_categories', 'Product Name']).size().reset_index(name='Count')
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Created By:N', title='Created By'),
                y=alt.Y('Count:Q', title='Count'),
                color='Product Name:N'
            ).properties(
                width=600,
                height=400
            )
        else:
            # Show by Category
            chart_data = df_filtered.groupby(['Created By', 'reporting_categories']).size().reset_index(name='Count')
            chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Created By:N', title='Created By'),
                y=alt.Y('Count:Q', title='Count'),
                color='reporting_categories:N'
            ).properties(
                width=600,
                height=400
            )

        st.altair_chart(chart, use_container_width=True)

    with tab2:
        if show_category_details:
            # Show details by Product Name
            chart_data2 = df_filtered.groupby(['Created By', 'reporting_categories', 'Product Name'])['Standard Price(incl)'].sum().reset_index().round(2)
            chart_data2.columns = ['Created By', 'reporting_categories', 'Product Name', 'Total Internal Cost']
            chart2 = alt.Chart(chart_data2).mark_bar().encode(
                x=alt.X('Created By:N', title='Created By'),
                y=alt.Y('Total Internal Cost:Q', title='Total Internal Cost'),
                color='Product Name:N'
            ).properties(
                width=600,
                height=400
            )
        else:
            # Show by Category
            chart_data2 = df_filtered.groupby(['Created By', 'reporting_categories'])['Standard Price(incl)'].sum().reset_index().round(2)
            chart_data2.columns = ['Created By', 'reporting_categories', 'Total Internal Cost']
            chart2 = alt.Chart(chart_data2).mark_bar().encode(
                x=alt.X('Created By:N', title='Created By'),
                y=alt.Y('Total Internal Cost:Q', title='Total Internal Cost'),
                color='reporting_categories:N'
            ).properties(
                width=600,
                height=400
            )

        st.altair_chart(chart2, use_container_width=True)

    st.dataframe(df_filtered)
else:
    st.warning("No data available for the selected filters.")
