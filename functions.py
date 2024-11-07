import datetime
import pandas as pd
import streamlit as st
from PIL import Image
import re
import os
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,)



#----------------------------------------------------
# Housekeeping
#----------------------------------------------------

def set_page_definitition():
  app_name = "Petabytes PoC v0.1"

  # Loading Image using PIL
  icon = Image.open('content/Subsidiary Salmon Logo.png')

  # Enable wide mode and set light theme and add tab icon
  st.set_page_config(layout="wide", page_title=app_name, page_icon=icon, initial_sidebar_state="expanded")
  # st.set_page_config(layout="wide", page_title=app_name, page_icon=":material/sound_detection_dog_barking:", initial_sidebar_state="expanded")


  return app_name

def initialize_session_state():

    # Collect Invoice Lines
    if 'all_invoice_lines' not in st.session_state:
        print("Running Invoice Lines function...")
        st.session_state.all_invoice_lines = prepare_invoice_lines()




#----------------------------------------------------
# Load Data
#----------------------------------------------------

def load_newest_file(filename_prefix):
    folder_path = "data"
    try:
        files = os.listdir(folder_path)
        invoice_files = [file for file in files if file.startswith(filename_prefix)]
        if invoice_files:
            highest_file = max(invoice_files)
            print(highest_file)
            file_path = os.path.join(folder_path, highest_file)
            if highest_file.endswith(".csv"):
                df = pd.read_csv(file_path, low_memory=False)
                return df
            elif highest_file.endswith(".xlsx"):
                df = pd.read_excel(file_path)
                return df
    except FileNotFoundError:
        print(f"The folder '{folder_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


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
            if is_categorical_dtype(df[column]) or df[column].nunique() < 100:
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


def prepare_invoice_lines():
    # import data lines
    invoice_lines_filename_prefix = "Invoice Lines Report-"

    df = load_newest_file(invoice_lines_filename_prefix)

    # Convert 'Invoice Date' from string to datetime format
    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%d-%m-%Y')
    df['Invoice Line Date: Created'] = pd.to_datetime(df['Invoice Line Date: Created'], format='%d-%m-%Y')

    # Data Cleaning
    df = df[df['Type'] != 'Header']
    df = df[df['Product Name'] != 'Subscription Fee']
    df = df[df['Product Name'] != 'Cancellation Fee']
    df = df[df['Client Contact Code'] != 'ezyVet']

    # Change miscategorised Meloxicam and Methadone away from Consultations
    df['Product Group'] = df.apply(lambda row: "Medication - Miscategorised " if row[
                                                                                     'Product Name'] == "(1) Includes: Meloxicam and Methadone" else
    row['Product Group'], axis=1)

    # Set 'Medication' for medication groups
    medication_groups = ["Medication - Oral", "Medication - Injectable", "Medication - Flea & Worm",
                         "Medication - Topical", "Anaesthesia", "Medication - Miscategorised", "Medication - Other"]
    df['reporting_categories'] = df['Product Group'].apply(lambda x: "Medication" if x in medication_groups else None)

    # Set 'other categories' , without overwriting existing non-null values
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

    df['created_by_category'] = df['Created By'].apply(
        lambda x: 'Vets' if x in vets else ('COPS' if x in cops else ('Nurses' if x in nurses else 'Other')))

    # # Push the filtered DataFrame to session state
    # st.session_state['df'] = df

    return df
