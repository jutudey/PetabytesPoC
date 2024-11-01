import datetime
import pandas as pd
import streamlit as st
from PIL import Image
import re
import os


def set_page_definitition():
  app_name = "Petabytes PoC v0.1"

  # Loading Image using PIL
  icon = Image.open('content/Subsidiary Salmon Logo.png')

  # Enable wide mode and set light theme and add tab icon
  st.set_page_config(layout="wide", page_title=app_name, page_icon=icon, initial_sidebar_state="expanded")
  # st.set_page_config(layout="wide", page_title=app_name, page_icon=":material/sound_detection_dog_barking:", initial_sidebar_state="expanded")

  return app_name


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


@st.cache_data

def load_cvs_data(file_path):
  df = pd.read_csv(file_path, index_col=0)

  return df

