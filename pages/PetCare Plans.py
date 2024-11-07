import streamlit as st
import pandas as pd
import datetime
import functions
import altair as alt

functions.set_page_definitition()
st.title("📦  PetCare Plan Analysis")

functions.initialize_session_state()

# Load the data from session state
invoice_lines = st.session_state.all_invoice_lines
payments = st.session_state.all_payments

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

st.sidebar.subheader("📦  PetCare Plans")
#
# product_cat = st.sidebar.multiselect(
#     "Select Plans",
#     sorted(invoice_lines["reporting_categories"].unique()),
#     default=None
# )

product_cat = None

petcareplan_to_display = st.sidebar.multiselect(
    "Select PetCare Plans",
    sorted(invoice_lines["petcare_plan_in_vera"].unique()),
    default=None
)


# Checkbox to show detailed product information
show_category_details = st.sidebar.checkbox("Show Category Details")

# Tickboxes to include specific categories
# include_vets = st.sidebar.checkbox("Include Vets", value=True)
# include_nurses = st.sidebar.checkbox("Include Nurses", value=True)
# include_cops = st.sidebar.checkbox("Include COPS", value=True)
#
include_vets = True
include_nurses = True
include_cops = True

# Filter by selected Created By categories
# categories_to_include = []
# if include_vets:
#     categories_to_include.append('Vets')
# if include_nurses:
#     categories_to_include.append('Nurses')
# if include_cops:
#     categories_to_include.append('COPS')

# Filter by petcare plans if any are selected
if petcareplan_to_display:
    invoice_lines = invoice_lines[invoice_lines["petcare_plan_in_vera"].isin(petcareplan_to_display)]
    payments = payments[payments["petcare_plan_in_vera"].isin(petcareplan_to_display)]

# Filter the DataFrame to only include rows between the start and end dates
invoice_lines_filtered = invoice_lines[(invoice_lines['Invoice Line Date: Created'] >= start_date) & (invoice_lines['Invoice Line Date: Created'] <= end_date)]
payments_start_date = pd.to_datetime(start_date)
payments_end_date = pd.to_datetime(end_date)

payments_filtered = payments[
    (payments['tl_Date'] >= payments_start_date) & (payments['tl_Date'] <= payments_end_date)
]

# Display the filtered DataFrame
if not invoice_lines_filtered.empty:
    st.subheader(f"Showing data based on {len(invoice_lines_filtered)} invoice lines from the period between {start_date.strftime('%B %d, %Y')} and {end_date.strftime('%B %d, %Y')}")


    if show_category_details:
        # Show details by Product Name
        chart_data2 = invoice_lines_filtered.groupby(['petcare_plan_in_vera', 'reporting_categories', 'Product Name'])['Standard Price(incl)'].sum().reset_index().round(2)
        chart_data2.columns = ['petcare_plan_in_vera', 'reporting_categories', 'Product Name', 'Total Internal Cost']
        chart2 = alt.Chart(chart_data2).mark_bar().encode(
            x=alt.X('petcare_plan_in_vera:N', title='£ by PetCare Plans'),
            y=alt.Y('Total Internal Cost:Q', title='Total Internal Cost'),
            color='Product Name:N'
        ).properties(
            width=600,
            height=500
        )
    else:
        # Show by Category
        chart_data2 = invoice_lines_filtered.groupby(['petcare_plan_in_vera', 'reporting_categories'])['Standard Price(incl)'].sum().reset_index().round(2)
        chart_data2.columns = ['petcare_plan_in_vera', 'reporting_categories', 'Total Internal Cost']
        chart2 = alt.Chart(chart_data2).mark_bar().encode(
            x=alt.X('petcare_plan_in_vera:N', title='Count of Invoice Lines by PetCare Plans'),
            y=alt.Y('Total Internal Cost:Q', title='Total Internal Cost'),
            color='reporting_categories:N'
        ).properties(
            width=600,
            height=500
        )

        # # Show revenue
        # chart_data3 = payments_filtered.groupby(['petcare_plan_in_vera'])[
        #     'tl_Revenue'].sum().reset_index().round(2)
        # chart_data3.columns = ['petcare_plan_in_vera', 'tl_Revenue']
        # chart3 = alt.Chart(chart_data3).mark_bar().encode(
        #     x=alt.X('petcare_plan_in_vera:N', title='Count of Invoice Lines by PetCare Plans'),
        #     y=alt.Y('tl_Revenue:Q', title='Total Internal Cost'),
        #     # color='reporting_categories:N'
        # ).properties(
        #     width=600,
        #     height=500
        # )

        # Add a source column to differentiate the two DataFrames
        payments_filtered['Source'] = 'Revenue'
        invoice_lines_filtered['Source'] = 'Cost'

        # Select the relevant columns and rename for consistency
        df1 = payments_filtered[['petcare_plan_in_vera', 'tl_Revenue', 'Source']].rename(
            columns={'tl_Revenue': 'Value'})
        df2 = invoice_lines_filtered[['petcare_plan_in_vera', 'Standard Price(incl)', 'Source']].rename(
            columns={'Standard Price(incl)': 'Value'})

        # Concatenate the DataFrames
        combined_df = pd.concat([df1, df2], ignore_index=True)

        # Create the Altair bar chart with grouped bars
        chart = alt.Chart(combined_df).mark_bar().encode(
            x=alt.X('petcare_plan_in_vera:N', title='Petcare Plan in VERA', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Value:Q', title='Value'),
            color=alt.Color('Source:N', title='Data Source'),
            xOffset='Source:N',
            tooltip=['petcare_plan_in_vera', 'Source', 'Value']
        ).properties(
            width=600,
            height=400
        )

        # Display the chart in Streamlit
        st.title("Comparison of Revenue and Cost  by Petcare Plan in VERA")
        st.altair_chart(chart, use_container_width=True)

    #
    # st.altair_chart(chart2, use_container_width=True)
    # st.altair_chart(chart3, use_container_width=True)



    with st.expander("Show Invoice Line Details"):
        # Content inside the expandable box
        st.write("Here are the details for the enriched invoice lines:")
        st.dataframe(invoice_lines_filtered)


else:
    st.warning("No data available for the selected filters.")
