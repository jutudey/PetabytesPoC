import streamlit as st
import pandas as pd
import datetime
import functions
import altair as alt

functions.set_page_definitition()
st.title("📊  Petabytes PoC")

allInvoicelines = "data/Invoice Lines-2024-10-25-17-47-28.csv"
df = functions.load_cvs_data(allInvoicelines)

# Convert 'Invoice Date' from string to datetime format
df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%d-%m-%Y')

# Data Cleaning
df = df[df['Type'] != 'Header']
df = df[df['Product Name'] != 'Subscription Fee']
df = df[df['Product Name'] != 'Cancellation Fee']
df = df[df['Client Contact Code'] != 'ezyVet']

# Change miscategorised Meloxicam and Methadone away from Consultations
df['Product Group'] = df.apply(lambda row: "Medication - Miscategorised " if row['Product Name'] == "(1) Includes: Meloxicam and Methadone" else row['Product Group'], axis=1)

# Set 'Medication' for medication groups
medication_groups = ["Medication - Oral", "Medication - Injectable", "Medication - Flea & Worm", "Medication - Topical", "Anaesthesia", "Medication - Miscategorised", "Medication - Other"]
df['reporting_categories'] = df['Product Group'].apply(lambda x: "Medication" if x in medication_groups else None)

# Set 'other categories' , without overwriting existing non-null values
vaccination_groups = ["Vaccinations", "Vaccine Stock"]
df['reporting_categories'] = df.apply(lambda row: "Vaccinations" if row['Product Group'] in vaccination_groups else row['reporting_categories'], axis=1)
consultations = ["Consultations"]
df['reporting_categories'] = df.apply(lambda row: "Consultations" if row['Product Group'] in consultations else row['reporting_categories'], axis=1)
procedures_groups = ["Procedures", "Dental", "Surgery", "Fluids  Therapy"]
df['reporting_categories'] = df.apply(lambda row: "Procedures" if row['Product Group'] in procedures_groups else row['reporting_categories'], axis=1)
diagnostics_groups = ["Diagnostic Procedures", "Diagnostic Imaging"]
df['reporting_categories'] = df.apply(lambda row: "Diagnostic" if row['Product Group'] in diagnostics_groups else row['reporting_categories'], axis=1)
lab_work_groups = ["Idexx External", "Idexx In-House"]
df['reporting_categories'] = df.apply(lambda row: "Lab Work" if row['Product Group'] in lab_work_groups else row['reporting_categories'], axis=1)
hospitalisation = ["Boarding", "Hospitalisation"]
df['reporting_categories'] = df.apply(lambda row: "Hospitalisation" if row['Product Group'] in hospitalisation else row['reporting_categories'], axis=1)
consumables = ["Consumables", "Surgery Consumables", "Suture Material", "Bandages"]
df['reporting_categories'] = df.apply(lambda row: "Consumables" if row['Product Group'] in consumables else row['reporting_categories'], axis=1)
service_fee = ["Service Fee"]
df['reporting_categories'] = df.apply(lambda row: "Service Fee" if row['Product Group'] in service_fee else row['reporting_categories'], axis=1)
pts = ["Euthanasia & Cremation", "Individual Cremations"]
df['reporting_categories'] = df.apply(lambda row: "PTS & Cremations" if row['Product Group'] in pts else row['reporting_categories'], axis=1)
df['reporting_categories'] = df['reporting_categories'].fillna("Misc")

# Categorise 'Created By'
vets = [
    "Amy Gaines", "Kate Dakin", "Ashton-Rae Nash", "Sarah Halligan",
    "Hannah Brightmore", "Kaitlin Austin", "James French", "Joshua Findlay", "Andrew Hunt", "Georgia Cleaton",
    "Alan Robinson", "Sheldon Middleton", "Horatio Marchis", "Claire Hodgson", "Sara Jackson"
]
cops = [
    "System", "Jennifer Hammersley", "Hannah Pointon", "Sheila Rimes",
    "Victoria Johnson", "Linda Spooner", "Amy Bache", "Katie Goodwin", "Catriona Bagnall", "Francesca James",
    "Katie Jones", "Emily Freeman", "Esmee Holt", "Charlotte Middleton", "Maz Darley"
]
nurses = [
    "Zoe Van-Leth", "Amy Wood", "Charlotte Crimes", "Emma Foreman",
    "Charlie Hewitt", "Hannah Brown", "Emily Castle", "Holly Davies", "Liz Hanson",
    "Emily Smith", "Saffron Marshall", "Charlie Lea-Atkin", "Amber Smith", "Katie Jenkinson",
     "Nicky Oakden"
]

df['created_by_category'] = df['Created By'].apply(lambda x: 'Vets' if x in vets else ('COPS' if x in cops else ('Nurses' if x in nurses else 'Other')))

# Push the filtered DataFrame to session state
st.session_state['df'] = df

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
df_filtered = df[(df['Invoice Date'] >= start_date) & (df['Invoice Date'] <= end_date)]



# Display the filtered DataFrame
if not df_filtered.empty:
    st.subheader(f"Showing data based on {len(df_filtered)} invoice lines from the period between {start_date.strftime('%B %d, %Y')} and {end_date.strftime('%B %d, %Y')}")

    # Create tabs for different aggregations
    tab1, tab2 = st.tabs(["By Count", "By Internal Cost"])

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
