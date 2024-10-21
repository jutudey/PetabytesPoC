import streamlit as st
import pandas as pd

st.title("Petabytes PoC")

@st.cache_data

def load_data():
  return pd.read_csv("https://github.com/dataprofessor/population-dashboard/raw/master/data/us-population-2010-2019-reshaped.csv", index_col=0