import numpy as np
import streamlit as st
import functions as functions
import config
import pandas as pd
from PIL import Image
import re
import os
import datetime
import zipfile
from io import BytesIO
import zipfile
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,)



#----------------------------------------------------
# Housekeeping
#----------------------------------------------------

def set_page_definitition():
    app_name = config.app_name

    # Loading Image using PIL
    icon = Image.open('content/Subsidiary Salmon Logo.png')

    # Enable wide mode and set light theme and add tab icon
    st.set_page_config(layout="wide", page_title=app_name, page_icon=icon, initial_sidebar_state="expanded")
    # st.set_page_config(layout="wide", page_title=app_name, page_icon=":material/sound_detection_dog_barking:", initial_sidebar_state="expanded")

    return app_name

def initialize_session_state():

    # if force_load:
    #     st.session_state.all_invoice_lines = merge_invoice_lines_and_payments()
    #     st.session_state.all_payments = extract_tl_Payments()

    try:
        # Collect Invoice Lines
        if 'all_invoice_lines' not in st.session_state:
            print("Invoice lines not in session state - Running Invoice Lines function...")
            st.session_state.all_invoice_lines = None
            st.session_state.all_invoice_lines = merge_invoice_lines_and_payments()
            print("Invoice lines processed and entered into Session State: ")
            print(st.session_state.all_invoice_lines.info())
        else:
            print("Invoice lines already in session state - Skipping Invoice Lines function...")

            # Collect Payments
        if 'all_payments' not in st.session_state:
            print("Payments  not in session state - Running Payments function...")
            # st.session_state.all_payments = None
            st.session_state.all_payments = extract_tl_Payments()
            print("Payments file processed and entered into Session State: ")
            print(st.session_state.all_payments.info())
        else:
            print("Payments already in session state - Skipping Payments function...")

    except TypeError:
        st.warning("Please upload the required files to proceed.")

def normalize_id(id_value):
    if id_value == "nan":
        return np.nan

    if pd.isna(id_value):
        return np.nan

    # Convert to string if it's a number
    id_value = str(id_value)

    # Remove ".0" if it is at the end of the entry
    if id_value.endswith('.0'):
        id_value = id_value[:-2]

    # Remove any commas
    id_value = id_value.replace(',', '')

    # Ensure it's exactly 6 digits
    if len(id_value) == 6 and id_value.isdigit():
        return id_value
    else:
        raise ValueError(f"Invalid ID format for value: {id_value}")

#----------------------------------------------------
# File Management
#----------------------------------------------------

def get_newest_filename(filename_prefix):
    folder_path = config.data_folder
    try:
        files = os.listdir(folder_path)
        source_files = [file for file in files if file.startswith(filename_prefix)]
        if source_files:
            highest_file = max(source_files)
            print(highest_file)
            file_path = os.path.join(folder_path, highest_file)

            if highest_file.endswith(".csv"):
                df = pd.read_csv(file_path, low_memory=False)

                return highest_file
            elif highest_file.endswith(".xlsx"):
                df = pd.read_excel(file_path)
                return highest_file
    except FileNotFoundError:
        print(f"The folder '{folder_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to create a zip file of all files in the data folder
def create_zip_file():
    """
    Create a zip file containing all files in the data folder.
    Returns a BytesIO object containing the zip file.
    """
    data_folder = config.data_folder
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in os.listdir(data_folder):
            file_path = os.path.join(data_folder, file)
            if os.path.isfile(file_path):
                zip_file.write(file_path, os.path.basename(file_path))
    zip_buffer.seek(0)
    return zip_buffer

def required_files_dashboard(required_files_description):
    st.header('Required Files Status')
    st.write(f"In order to work properly the application requires up-to-date versions of the following files:")

    for file_name in required_files_description:
        st.markdown("##### " + file_name[0])
        # st.write('File name prefix: "' + file_name[1] + '"')

        newest_file = get_newest_filename(file_name[2])

        if newest_file is None:
            st.markdown("<span style='color:red'>❌ Not yet uploaded</span>", unsafe_allow_html=True)
        else:
            st.write('✅ ' + str(newest_file))


def age_of_file(required_files_description):
    for file_description in required_files_description:
        newest_file = get_newest_filename(file_description[2])
        st.write(f"##### {file_description[2]}")
        if newest_file is not None:
            file_path = os.path.join(config.data_folder, newest_file)
            file_age = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            now = datetime.datetime.now()
            age = now - file_age
            print(f"{newest_file} is {age.days} days old")


def required_files_description(required_files_description):
    st.header('Required Files')
    st.write(f"In order to work properly the application requires up-to-date versions of the following files:")

    for file_description in required_files_description:
        st.markdown("##### " + file_description[0])
        st.write('File name prefix: "' + file_description[1] + '"')

        newest_file = get_newest_filename(file_description[2])

        if newest_file is None:
            st.markdown("<span style='color:red'>Not yet uploaded</span>", unsafe_allow_html=True)
        else:
            st.write('Newest file uploaded: ' + str(newest_file))

        with st.expander('Where to find the file', expanded=False):
            st.write(file_description[3])

def upload_file():
    data_folder = config.data_folder
    uploaded_files = st.file_uploader("Choose CSV or Excel files",
                                      type=["csv", "xlsx"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(data_folder, uploaded_file.name)
            if os.path.exists(file_path):
                os.remove(file_path)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success("Files uploaded successfully!")


#----------------------------------------------------
# Load Data
#----------------------------------------------------

def load_newest_file(filename_prefix):
    print("    Starting to look for the newest file with the prefix  " + filename_prefix)
    folder_path = config.data_folder
    try:
        files = os.listdir(folder_path)
        invoice_files = [file for file in files if file.startswith(filename_prefix)]
        if invoice_files:
            highest_file = max(invoice_files)
            file_path = os.path.join(folder_path, highest_file)
            if highest_file.endswith(".csv"):
                df = pd.read_csv(file_path, low_memory=False)
                print(f"    Found and loaded into dataframe: {highest_file}")
                return df
            elif highest_file.endswith(".xlsx"):
                df = pd.read_excel(file_path)
                print(f"    Found and loaded into dataframe: {highest_file}")
                return df
    except FileNotFoundError:
        print(f"The folder '{folder_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Adds a UI on top of a dataframe to let viewers filter columns
#
#     Args:
#         df (pd.DataFrame): Original dataframe
#
#     Returns:
#         pd.DataFrame: Filtered dataframe
#     """
#     modify = st.checkbox("Add filters")
#
#     if not modify:
#         return df
#
#     df = df.copy()
#     print(df.info())
#
#     # Try to convert datetimes into a standard format (datetime, no timezone)
#     for col in df.columns:
#         if is_object_dtype(df[col]):
#             try:
#                 # Attempt to convert to datetime with a specific format
#                 df[col] = pd.to_datetime(df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
#             except Exception as e:
#                 # You can optionally log or print the exception for debugging
#                 print(f"Could not convert column {col}: {e}")
#                 pass
#
#         if is_datetime64_any_dtype(df[col]):
#             df[col] = df[col].dt.tz_localize(None)
#
#     modification_container = st.container()
#
#     with modification_container:
#         to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
#         for column in to_filter_columns:
#             left, right = st.columns((1, 20))
#             # Treat columns with < 10 unique values as categorical
#             if is_categorical_dtype(df[column]) or df[column].nunique() < 100:
#                 user_cat_input = right.multiselect(
#                     f"Values for {column}",
#                     df[column].unique(),
#                     default=list(df[column].unique()),
#                 )
#                 df = df[df[column].isin(user_cat_input)]
#             elif is_numeric_dtype(df[column]):
#                 _min = float(df[column].min())
#                 _max = float(df[column].max())
#                 step = (_max - _min) / 100
#                 user_num_input = right.slider(
#                     f"Values for {column}",
#                     min_value=_min,
#                     max_value=_max,
#                     value=(_min, _max),
#                     step=step,
#                 )
#                 df = df[df[column].between(*user_num_input)]
#             elif is_datetime64_any_dtype(df[column]):
#                 user_date_input = right.date_input(
#                     f"Values for {column}",
#                     value=(
#                         df[column].min(),
#                         df[column].max(),
#                     ),
#                 )
#                 if len(user_date_input) == 2:
#                     user_date_input = tuple(map(pd.to_datetime, user_date_input))
#                     start_date, end_date = user_date_input
#                     df = df.loc[df[column].between(start_date, end_date)]
#             else:
#                 user_text_input = right.text_input(
#                     f"Substring or regex in {column}",
#                 )
#                 if user_text_input:
#                     df = df[df[column].astype(str).str.contains(user_text_input)]
#
#     return df

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

def get_date_range(selected_option, custom_start=None, custom_end=None):
    today = datetime.date.today()
    today = datetime.date.today()

    if selected_option == "Today":
      start_date = today
      end_date = today
    elif selected_option == "This Week":
      start_date = today - datetime.timedelta(days=today.weekday())  # Start of the week (Monday)
      end_date = today
    elif selected_option == "This Week-to-date":
      start_date = today - datetime.timedelta(days=today.weekday())
      end_date = today
    elif selected_option == "This Month":
      start_date = today.replace(day=1)  # First day of this month
      end_date = today
    elif selected_option == "This Month-to-date":
      start_date = today.replace(day=1)
      end_date = today
    elif selected_option == "This Quarter":
      current_month = today.month
      quarter_start_month = current_month - (current_month - 1) % 3
      start_date = today.replace(month=quarter_start_month, day=1)
      end_date = today
    elif selected_option == "This Quarter-to-date":
      current_month = today.month
      quarter_start_month = current_month - (current_month - 1) % 3
      start_date = today.replace(month=quarter_start_month, day=1)
      end_date = today
    elif selected_option == "This Year":
      start_date = today.replace(month=1, day=1)  # First day of this year
      end_date = today
    elif selected_option == "This Year-to-date":
      start_date = today.replace(month=1, day=1)
      end_date = today
    elif selected_option == "This Year-to-last-month":
      start_date = today.replace(month=1, day=1)
      end_date = today.replace(month=today.month - 1, day=1) - datetime.timedelta(days=1)
    elif selected_option == "Yesterday":
      start_date = today - datetime.timedelta(days=1)
      end_date = today - datetime.timedelta(days=1)
    elif selected_option == "Recent":
      # Placeholder for "Recent" - you can define your own range here
      start_date = today - datetime.timedelta(days=7)
      end_date = today
    elif selected_option == "Last Week":
      start_date = today - datetime.timedelta(days=today.weekday() + 7)
      end_date = start_date + datetime.timedelta(days=6)
    elif selected_option == "Last Month":
      first_day_of_this_month = today.replace(day=1)
      start_date = first_day_of_this_month - datetime.timedelta(days=1)  # Last day of the previous month
      start_date = start_date.replace(day=1)  # First day of the previous month
      end_date = first_day_of_this_month - datetime.timedelta(days=1)
    elif selected_option == "Last Month-to-date":
      first_day_of_this_month = today.replace(day=1)
      start_date = first_day_of_this_month - datetime.timedelta(days=1)
      start_date = start_date.replace(day=1)
      end_date = today - datetime.timedelta(days=today.day)
    elif selected_option == "Last Quarter":
      current_month = today.month
      quarter_start_month = current_month - (current_month - 1) % 3
      start_date = today.replace(month=quarter_start_month, day=1) - datetime.timedelta(days=1)
      start_date = start_date.replace(month=start_date.month - 2, day=1)
      end_date = today.replace(month=quarter_start_month, day=1) - datetime.timedelta(days=1)
    elif selected_option == "Last Quarter-to-date":
      current_month = today.month
      quarter_start_month = current_month - (current_month - 1) % 3
      start_date = today.replace(month=quarter_start_month, day=1) - datetime.timedelta(days=1)
      start_date = start_date.replace(month=start_date.month - 2, day=1)
      end_date = today
    elif selected_option == "Last Year":
      start_date = today.replace(year=today.year - 1, month=1, day=1)
      end_date = today.replace(year=today.year - 1, month=12, day=31)
    elif selected_option == "Last Year-to-date":
      start_date = today.replace(year=today.year - 1, month=1, day=1)
      end_date = today.replace(year=today.year - 1, month=today.month, day=today.day)
    elif selected_option == "Last 30 Days":
      start_date = today - datetime.timedelta(days=30)
      end_date = today
    elif selected_option == "Last 60 Days":
      start_date = today - datetime.timedelta(days=60)
      end_date = today
    elif selected_option == "Last 90 Days":
      start_date = today - datetime.timedelta(days=90)
      end_date = today
    elif selected_option == "Last 365 Days":
      start_date = today - datetime.timedelta(days=365)
      end_date = today
    elif selected_option == "Next Week":
      start_date = today + datetime.timedelta(days=(7 - today.weekday()))
      end_date = start_date + datetime.timedelta(days=6)
    elif selected_option == "Next 4 Weeks":
      start_date = today
      end_date = today + datetime.timedelta(weeks=4)
    elif selected_option == "Next Month":
      start_date = today.replace(day=1) + datetime.timedelta(days=32)
      start_date = start_date.replace(day=1)
      end_date = start_date.replace(month=start_date.month + 1, day=1) - datetime.timedelta(days=1)
    elif selected_option == "Next Quarter":
      current_month = today.month
      next_quarter_start_month = ((current_month - 1) // 3 + 1) * 3 + 1
      if next_quarter_start_month > 12:
        next_quarter_start_month = 1
        start_date = today.replace(year=today.year + 1, month=next_quarter_start_month, day=1)
      else:
        start_date = today.replace(month=next_quarter_start_month, day=1)
      end_date = start_date + datetime.timedelta(days=90)
    elif selected_option == "Next Year":
      start_date = today.replace(year=today.year + 1, month=1, day=1)
      end_date = today.replace(year=today.year + 1, month=12, day=31)
    elif selected_option == "Custom Range":
      if custom_start and custom_end:
        start_date = custom_start
        end_date = custom_end
      else:
        raise ValueError("Custom start and end dates must be provided for 'Custom Range'")

    return start_date, end_date

def merge_invoice_lines_and_payments():
    print("    Calling Invoice Script for approved invoice lines....")
    approved_invoice_lines = functions.prepare_invoice_lines(config.invoice_lines_prefix)
    print("    Completed Invoice Script for approved invoice lines....")

    print("    Calling Invoice Script for NON-approved invoice lines....")
    non_approved_invoice_lines = functions.prepare_invoice_lines(config.non_approved_invoice_lines_prefix)
    print("    Completed Invoice Script for NON-approved invoice lines....")

    print("    Merging Approved and NON-approved invoice lines....")
    all_invoice_lines = pd.concat([approved_invoice_lines, non_approved_invoice_lines], ignore_index=True)
    return all_invoice_lines

def prepare_invoice_lines(filename_prefix):
    """
    Prepares the invoice lines data by loading the newest file, normalizing IDs, converting date formats,
    cleaning data, categorizing product groups, and adding pet care plan information.

    Returns:
        pd.DataFrame: The prepared invoice lines DataFrame.
    """
    print("        Running Invoice Lines script....")

    # Define the filename prefix for invoice lines
    invoice_lines_filename_prefix = filename_prefix

    # Load the newest file with the given prefix
    df = load_newest_file(invoice_lines_filename_prefix)

    # drop unnecessary columns
    df = df.drop(columns=['Parent Line ID',
                          'Invoice Line Date: Last Modified', 'Invoice Line Time: Last Modified',
                          'Department ID', 'Department', 'Inventory Location', 'Invoice Line Reference',
                          'Account', 'Salesperson is Vet', 'Consult ID', 'Surcharge Adjustment','Surcharge Name',
                          'Rounding Adjustment', 'Rounding Name', 'Tax per Qty After Discount', 'Total Tax Amount',
                          'Total Invoiced (excl)', 'Price After Discount(excl)', 'Total Invoiced (excl)',
                          'Total Earned(excl)', 'Payment Terms'])

    # Normalize the 'Animal Code' column
    df['Animal Code'] = df['Animal Code'].apply(normalize_id)

    # Convert 'Invoice Date' and 'Invoice Line Date: Created' from string to datetime format
    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%d-%m-%Y')
    df['Invoice Line Date: Created'] = pd.to_datetime(df['Invoice Line Date: Created'], format='%d-%m-%Y')
    # df['Invoice Line Date: Last Modified'] = pd.to_datetime(df['Invoice Line Date: Last Modified'], format='%d-%m-%Y')
    df['Invoice Line Date'] = pd.to_datetime(df['Invoice Line Date'], format='%d-%m-%Y')

    # Data Cleaning: Remove rows with specific values in 'Type', 'Product Name', and 'Client Contact Code'
    df = df[df['Type'] != 'Header']
    df = df.drop(columns=['Type'])
    df = df[df['Product Name'] != 'Subscription Fee']
    df = df[df['Product Name'] != 'Cancellation Fee']
    df = df[df['Client Contact Code'] != 'ezyVet']

    # Change miscategorized Meloxicam and Methadone away from Consultations
    df['Product Group'] = df.apply(lambda row: "Medication - Miscategorised " if row['Product Name'] == "(1) Includes: Meloxicam and Methadone" else row['Product Group'], axis=1)

    # Set 'Medication' for medication groups
    medication_groups = ["Medication - Oral", "Medication - Injectable", "Medication - Flea & Worm",
                         "Medication - Topical", "Anaesthesia", "Medication - Miscategorised", "Medication - Other"]
    df['reporting_categories'] = df['Product Group'].apply(lambda x: "Medication" if x in medication_groups else None)

    # Set 'other categories' without overwriting existing non-null values
    vaccination_groups = ["Vaccinations", "Vaccine Stock"]
    df['reporting_categories'] = df.apply(
        lambda row: "Vaccinations" if row['Product Group'] in vaccination_groups else row['reporting_categories'],
        axis=1)
    consultations = ["Consultations"]
    df['reporting_categories'] = df.apply(
        lambda row: "Consultations" if row['Product Group'] in consultations else row['reporting_categories'], axis=1)
    procedures_groups = ["Procedures", "Dental", "Surgery", "Fluids  Therapy"]
    df['reporting_categories'] = df.apply(
        lambda row: "Procedures" if row['Product Group'] in procedures_groups else row['reporting_categories'], axis=1)
    diagnostics_groups = ["Diagnostic Procedures", "Diagnostic Imaging"]
    df['reporting_categories'] = df.apply(
        lambda row: "Diagnostic" if row['Product Group'] in diagnostics_groups else row['reporting_categories'], axis=1)
    lab_work_groups = ["Idexx External", "Idexx In-House"]
    df['reporting_categories'] = df.apply(
        lambda row: "Lab Work" if row['Product Group'] in lab_work_groups else row['reporting_categories'], axis=1)
    hospitalisation = ["Boarding", "Hospitalisation"]
    df['reporting_categories'] = df.apply(
        lambda row: "Hospitalisation" if row['Product Group'] in hospitalisation else row['reporting_categories'],
        axis=1)
    consumables = ["Consumables", "Surgery Consumables", "Suture Material", "Bandages"]
    df['reporting_categories'] = df.apply(
        lambda row: "Consumables" if row['Product Group'] in consumables else row['reporting_categories'], axis=1)
    service_fee = ["Service Fee"]
    df['reporting_categories'] = df.apply(
        lambda row: "Service Fee" if row['Product Group'] in service_fee else row['reporting_categories'], axis=1)
    pts = ["Euthanasia & Cremation", "Individual Cremations"]
    df['reporting_categories'] = df.apply(
        lambda row: "PTS & Cremations" if row['Product Group'] in pts else row['reporting_categories'], axis=1)
    df['reporting_categories'] = df['reporting_categories'].fillna("Misc")

    df['created_by_category'] = df['Created By'].apply(
    lambda x: 'Vets' if x in config.vets else
                ('COPS' if x in config.cops else
                ('Nurses' if x in config.nurses else
                ('Locums' if x in config.locums else
                ('Students' if x in config.students else
                 'Other')))))
    if filename_prefix == config.invoice_lines_prefix:
    #     create a new column for approval status and set it to True
        df['Approved'] = True
    else:
        df['Approved'] = False

    # Add pet care plan information to the invoice lines
    print("            Adding petcare plans to invoice lines....")
    df = add_petcareplan_to_invoice_lines(df)
    print("            Completed petcare plans to invoice lines....")

    print("        Completed Invoice Lines script and returned dataframe....")
    return df


def load_petcare_plans():
    filename_prefix = "pet-care-plans-"

    # load data into df
    df = load_newest_file(filename_prefix)

    df['EvPetId'] = df['EvPetId'].astype(str).fillna('')
    df['EvPetId'] = df['EvPetId'].astype(str).str.replace('\.0$', '', regex=True).fillna('')

    # Apply prefix based on the length of EvPetId
    def format_evpetid(id_value):
        if len(id_value) == 3:
            return f"100{id_value}"
        elif len(id_value) == 4:
            return f"10{id_value}"
        elif len(id_value) == 2:
            return f"1000{id_value}"
        else:
            return id_value

    df['EvPetId'] = df['EvPetId'].apply(format_evpetid)
    # formatting datatypes
    # Replace "v1" with "V1" in all cells of ActualEvWp
    df['ActualEvWp'] = df['ActualEvWp'].str.replace('v1', 'V1', regex=False)

    # Map specific ProductCode values to their new values
    df['ProductCode'] = df['ProductCode'].replace({
        "D1": "D1V1", "D2": "D2V2", "D3": "D3V1",
        "C1": "C1V1", "C2": "C2V2", "C3": "C3V3"
    })

    # Specifically change "C3V1 Cat-Senior" to "C3V1-Cat-Senior"
    df['ActualEvWp'] = df['ActualEvWp'].replace("C3V1 Cat-Senior", "C3V1-Cat-Senior")

    # Extract text before the first hyphen in ActualEvWp
    df['EvWPcode'] = df['ActualEvWp'].str.split('-').str[0]

    # Apply conditional changes to EvWPcode based on Species
    df['EvWPcode'] = df.apply(lambda x: "PCAV1-DOG" if x['EvWPcode'] == "PCAV1" and x['Species'] == "Dog" else (
        "PCAV1-CAT" if x['EvWPcode'] == "PCAV1" else x['EvWPcode']), axis=1)

    # Map specific ProductCode values to their new values
    df['EvWPcode'] = df['EvWPcode'].replace({
        "D1": "D1V1", "D2": "D2V2", "D3": "D3V1",
        "C1": "C1V1", "C2": "C2V2", "C3": "C3V3"
    })

    # Strip spaces and standardize case before comparing
    import numpy as np

    # Set VeraEvDiff to True when ProductCode and EvWPcode are the same, and False when they differ
    df['VeraEvDiff'] = np.where(df['EvWPcode'].isna(), False,
                                df['EvWPcode'].str.strip().str.upper() == df['ProductCode'].str.strip().str.upper())


    # Load ezyvet data to extract the customer id which is missing the Vera extract
    df2 = load_ezyvet_customers()

    df2['Animal Code'] = df2['Animal Code'].astype(str)
    df2['Owner Contact Code'] = df2['Owner Contact Code'].astype(str)

    # Assuming df2 contains 'Animal Code' and 'Owner Contact Code' columns
    df = df.merge(df2[['Animal Code', 'Owner Contact Code']], how='left', left_on='EvPetId', right_on='Animal Code')

    # Rename the merged 'Owner Contact Code' to 'EvCustomerID' and drop 'Animal Code' from the merged dataframe
    df = df.rename(columns={'Owner Contact Code': 'EvCustomerID'}).drop(columns=['Animal Code'])

    # Push the filtered DataFrame to session state
    st.session_state['ss_petcare_plans'] = df

    return df

def load_ezyvet_customers(customer_id=None):
    filename_prefix = "Animals_Report-"

    # load data into df
    df = load_newest_file(filename_prefix)

    if customer_id == None:
        return df
    else:
        filt = (df['Owner Contact Code'] == customer_id)
        df = df[filt]
        return df

def add_petcareplan_to_invoice_lines(invoice_lines_df):
    print("           Adding petcare plan id to invoice lines... ")
    petcare_plans = load_petcare_plans()

    # Create a lookup function to get the product code from petcare_plans
    def lookup_petcare_plan(animal_code):
        matching_row = petcare_plans[petcare_plans['EvPetId'] == animal_code]
        if not matching_row.empty:
            return matching_row['ProductCode'].values[0]
        return "Plan not in VERA"

    # Apply the lookup function to each row in invoice_lines
    invoice_lines_df['petcare_plan_in_vera'] = invoice_lines_df['Animal Code'].apply(lookup_petcare_plan)
    print("           Completed adding petcare plan id to invoice lines... ")
    return invoice_lines_df

def add_petcareplan_to_payments(payments_df):
    petcare_plans = load_petcare_plans()

    print("Adding petcare plan id to payments... ")

    # Create a lookup function to get the product code from petcare_plans
    def lookup_petcare_plan(tl_PetID):
        matching_row = petcare_plans[petcare_plans['EvPetId'] == tl_PetID]
        if not matching_row.empty:
            return matching_row['ProductCode'].values[0]
        return "Plan not in VERA"

    # Apply the lookup function to each row in payments
    payments_df['petcare_plan_in_vera'] = payments_df['tl_PetID'].apply(lookup_petcare_plan)

    return payments_df

def extract_tl_Payments():
    filename_prefix = "payment-history-"

    print("Processing payment lines... ")

    # load data into df
    df = load_newest_file(filename_prefix)

    # formatting datatypes
    df["ezyvetPetIDs"] = df["ezyvetPetIDs"].astype(str)
    df["ezyvetContactId"] = df["ezyvetContactId"].astype(str)
    df["cardDetails_lastFour"] = df["cardDetails_lastFour"].astype(str)
    # df['amount'] = df['amount'].astype(float).round(2) / 100
    df["eventDate"] = pd.to_datetime(df["eventDate"], utc=True)
    df['eventDate'] = df['eventDate'].dt.date

    # st.header('pre-split DF')
    # st.dataframe(df)

    # splitting multipet payments
    # Add new column 'PetsInSubscription' with the number of pet IDs in 'ezyvetPetIDs'
    df['PetsInSubscription'] = df['ezyvetPetIDs'].apply(lambda x: x.count(',') + 1)

    # Split rows with multiple pet IDs into separate rows
    df['ezyvetPetIDs'] = df['ezyvetPetIDs'].str.split(',')
    df = df.explode('ezyvetPetIDs')

    # st.header('post-split DF')
    # st.dataframe(df)

    # Identifying number of failed payments in a row
    # Create a subset where status is 'Refused'
    df_refused = df[df['status'] == 'Refused']

    # Sort df_refused by 'ezyvetPetIDs' and 'eventDate'
    df_refused = df_refused.sort_values(by=['ezyvetPetIDs', 'eventDate']).reset_index(drop=True)

    # Add new column 'MissedPayments' with the sequence number for each 'ezyvetPetIDs'
    def assign_sequence(df):
        sequence = []
        current_seq = 1
        for i in range(len(df)):
            if i == 0:
                sequence.append(current_seq)
            else:
                if df['ezyvetPetIDs'][i] == df['ezyvetPetIDs'][i - 1] and pd.to_datetime(
                        df['eventDate'][i]) == pd.to_datetime(df['eventDate'][i - 1]) + pd.Timedelta(days=1):
                    current_seq += 1
                else:
                    current_seq = 1
                sequence.append(current_seq)
        return sequence

    # Sort the dataframe by 'ezyvetPetIDs' and 'eventDate'
    df_refused = df_refused.sort_values(by=['ezyvetPetIDs', 'eventDate']).reset_index(drop=True)

    df_refused['MissedPayments'] = assign_sequence(df_refused)

    # st.title("Sorted payments with label")
    # st.dataframe(df_refused)


    # Update 'type' column based on 'MissedPayments'
    df_refused['type'] = df_refused.apply(lambda row: 'SUSPENDED ACCOUNT' if row['MissedPayments'] >= 8 else
    f"Missed Payment {row['MissedPayments']} - £{row['amount']}" if 1 <= row['MissedPayments'] < 8 else None, axis=1)
    df_refused['amount'] = 0

    # st.header('refused with sequence number')
    # st.dataframe(df_refused)

    # Drop duplicate 'adyenReference' in df_refused
    df_refused = df_refused.drop_duplicates(subset='adyenReference')

    # Merge df with df_refused to update 'type' and 'amount'
    df = df.merge(df_refused[['adyenReference', 'type', 'amount']], on='adyenReference', how='left',
                  suffixes=('', '_refused'))
    df["ezyvetContactId"] = df["ezyvetContactId"].astype(str)

    # Update 'type' and 'amount' only where there are values from df_refused
    df['type'] = df['type_refused'].combine_first(df['type'])
    df['amount'] = df['amount_refused'].combine_first(df['amount'])

    # Drop the temporary columns
    df = df.drop(columns=['type_refused', 'amount_refused'])

    # st.header('Merged df - are amounts 0')
    # st.dataframe(df)

    df.loc[df['adyenEvent'] == 'REFUND', 'amount'] *= -1

    # Grouping and adding sums, and renaming columns in one go
    df = df.assign(
        tl_ID=df["veraReference"],
        tl_Date=df["eventDate"],
        tl_CustomerID=df["ezyvetContactId"],
        tl_CustomerName="",
        tl_PetID=df["ezyvetPetIDs"],
        tl_PetName="",
        tl_Cost=0,
        tl_Discount=0,
        tl_Revenue=df["amount"],
        tl_Event=df["type"],
        tl_Comment=(
                df['xeroReference'].fillna('') + " " +
                df['paymentLinkId'].fillna('') + " " +
                df['remark'].fillna(''))
        )


    payments = df[[
        "tl_ID", "tl_Date", "tl_CustomerID", "tl_CustomerName", "tl_PetID",
        "tl_PetName", "tl_Cost", "tl_Discount", "tl_Revenue", "tl_Event","tl_Comment"
    ]]

    payments.loc[:, 'tl_CustomerID'] = payments['tl_CustomerID'].apply(normalize_id)
    payments.loc[:, 'tl_PetID'] = payments['tl_PetID'].apply(normalize_id)

    # Load pet details
    pet_details_df = get_ezyvet_pet_details()
    pet_details_df.loc[:, 'Animal Code'] = pet_details_df['Animal Code'].apply(normalize_id)

    payments = payments.merge(
        pet_details_df[['Animal Code', 'Animal Name', 'Owner Contact Code', 'Owner Last Name', 'Owner First Name']],
        how='left',
        left_on='tl_PetID',
        right_on='Animal Code')

    payments['tl_CustomerName'] = payments['Owner First Name'] +" " + payments['Owner Last Name']
    payments['tl_PetName'] = payments['Animal Name']
    print("Converting tl_Date to date format!")
    payments['tl_Date'] = pd.to_datetime(payments['tl_Date'])

    # Drop all columns after 'tl_Comment'
    payments = payments.loc[:, :'tl_Comment']

    # st.header('output DF')
    # st.dataframe(payments)
    # return the aggregated DataFrame

    payments = add_petcareplan_to_payments(payments)
    # print(payments.info())
    return payments

def get_ezyvet_pet_details(pet_id=None):
    filename_prefix = "Animals_Report-"

    # load data into df
    df = load_newest_file(filename_prefix)

    if pet_id == None:
        df.loc[:, 'Animal Code'] = df['Animal Code'].apply(normalize_id)
        return df
    else:
        df.loc[:, 'Animal Code'] = df['Animal Code'].apply(normalize_id)
        filt = (df['Animal Code'] == pet_id)
        df = df[filt]
        return df
