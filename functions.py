import pandas as pd
import streamlit as st
from PIL import Image


def set_page_definitition():
  app_name = "Petabytes PoC v0.1"

  # Loading Image using PIL
  icon = Image.open('content/Subsidiary Salmon Logo.png')

  # Enable wide mode and set light theme and add tab icon
  st.set_page_config(layout="wide", page_title=app_name, page_icon=icon, initial_sidebar_state="expanded")
  # st.set_page_config(layout="wide", page_title=app_name, page_icon=":material/sound_detection_dog_barking:", initial_sidebar_state="expanded")

  return app_name


@st.cache_data

def load_cvs_data(file_path):
  df = pd.read_csv(file_path, index_col=0)

  # # Identify blank rows (rows where all cells are NaN)
  # blank_rows = df.isnull().all(axis=1)
  #
  # # Show only the blank rows
  # blank_df = df[blank_rows]
  #
  # # Count how many blank rows there are
  # blank_row_count = blank_rows.sum()
  #
  # # If you want to remove blank rows
  # df = df[~blank_rows]

  return df

