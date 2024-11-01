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
    df_filtered = df[(df['Invoice Line Date: Created'] >= start_date) & (df['Invoice Line Date: Created'] <= end_date)]

    # Created By Selector (single selection only)
    st.sidebar.subheader("👥 Created By")
    created_by_options = sorted(df_filtered['Created By'].unique())
    selected_created_by = st.sidebar.selectbox("Select Created By", created_by_options)

    if selected_created_by:
        df_filtered = df_filtered[df_filtered['Created By'] == selected_created_by]

    # Product Category Selector
    st.sidebar.subheader("📦 Product Category")
    product_cat = st.sidebar.multiselect(
        "Select Product Category",
        sorted(df_filtered["reporting_categories"].unique()),
        default=None
    )

    if product_cat:
        df_filtered = df_filtered[df_filtered["reporting_categories"].isin(product_cat)]

    # Checkbox to show detailed product information
    show_category_details = st.sidebar.checkbox("Show Category Details")

    st.title(f"🩺 {selected_created_by} - ezyVet activities")
    st.subheader(
        f"Showing data based on {len(df_filtered)} invoice lines from the period between {start_date.strftime('%B %d, %Y')} and {end_date.strftime('%B %d, %Y')}")

    # Display the filtered DataFrame
    if not df_filtered.empty:
        # Create tabs
        tab1, tab2 = st.tabs(["By Count", "By Standard Price(incl)"])

        with tab1:
            # Create Bar Chart for Selected Staff Member (Count)
            df_filtered['Month'] = df_filtered['Invoice Line Date: Created'].dt.to_period('M').dt.to_timestamp()
            if len(product_cat) > 1 or show_category_details:
                # Stacked bar chart by product names (Count)
                chart_data = df_filtered.groupby(['Month', 'Product Name']).size().reset_index(name='Count')
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X('Month:T', title='Month', timeUnit='yearmonth'),
                    y=alt.Y('Count:Q', title='Count'),
                    color='Product Name:N'
                ).properties(
                    width=600,
                    height=400
                )
            else:
                # Bar chart by month (Count)
                chart_data = df_filtered.groupby('Month').size().reset_index(name='Count')
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X('Month:T', title='Month', timeUnit='yearmonth'),
                    y=alt.Y('Count:Q', title='Count')
                ).properties(
                    width=600,
                    height=400
                )

            st.altair_chart(chart, use_container_width=True)

        with tab2:
            # Create Bar Chart for Selected Staff Member (Sum of Standard Price(incl))
            if len(product_cat) > 1 or show_category_details:
                # Stacked bar chart by product names (Standard Price incl)
                chart_data = df_filtered.groupby(['Month', 'Product Name'])['Standard Price(incl)'].sum().reset_index()
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X('Month:T', title='Month', timeUnit='yearmonth'),
                    y=alt.Y('Standard Price(incl):Q', title='Total Standard Price(incl)'),
                    color='Product Name:N'
                ).properties(
                    width=600,
                    height=400
                )
            else:
                # Bar chart by month (Standard Price incl)
                chart_data = df_filtered.groupby('Month')['Standard Price(incl)'].sum().reset_index()
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X('Month:T', title='Month', timeUnit='yearmonth'),
                    y=alt.Y('Standard Price(incl):Q', title='Total Standard Price(incl)')
                ).properties(
                    width=600,
                    height=400
                )

            st.altair_chart(chart, use_container_width=True)

        st.dataframe(df_filtered)
    else:
        st.warning("No data available for the selected filters.")
