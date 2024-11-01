import streamlit as st
import pandas as pd
import datetime
import altair as alt
import functions

# General page setup
functions.set_page_definitition()

# Load the DataFrame from session state
df = st.session_state.get('df')

if df is None:
    st.error("Data is not available in session state. Please ensure the main page has been loaded and processed.")
else:
    # Date Range Selector
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

    # Filter DataFrame by date
    df_filtered = df[(df['Invoice Date'] >= start_date) & (df['Invoice Date'] <= end_date)]

    # Staff Member Selector
    st.sidebar.subheader("👥 Staff Members")
    staff_members = st.sidebar.multiselect(
        "Select Staff Members",
        sorted(df_filtered['Created By'].unique()),
        default=sorted(df_filtered['Created By'].unique())
    )

    if staff_members:
        df_filtered = df_filtered[df_filtered['Created By'].isin(staff_members)]

    # Product Category Selector for the Line Graph
    st.sidebar.subheader("📦 Product Category")
    product_cat = st.sidebar.multiselect(
        "Select Product Category",
        sorted(df_filtered["reporting_categories"].unique()),
        default=None
    )

    if product_cat:
        df_filtered = df_filtered[df_filtered["reporting_categories"].isin(product_cat)]

    st.title("📊 Comparison of Activities by Staff Members")
    st.subheader(
        f"Showing data based on {len(df_filtered)} invoice lines from the period between {start_date.strftime('%B %d, %Y')} and {end_date.strftime('%B %d, %Y')}" )

    # Create Line Chart
    if not df_filtered.empty:
        df_filtered['Month'] = df_filtered['Invoice Date'].dt.to_period('M').dt.to_timestamp()
        line_chart_data = df_filtered.groupby(['Month', 'Created By']).size().reset_index(name='Count')
        line_chart = alt.Chart(line_chart_data).mark_line().encode(
            x=alt.X('Month:T', title='Month', timeUnit='yearmonth'),
            y=alt.Y('Count:Q', title='Total Activities'),
            color='Created By:N'
        ).properties(
            width=600,
            height=400
        )

        st.altair_chart(line_chart, use_container_width=True)

    else:
        st.warning("No data available for the selected filters.")
