import config
import streamlit as st
import pandas as pd
import datetime
import functions

functions.set_page_definitition()
st.title("Petabytes PoC")

with st.spinner('Loading and preparing data...'):
    functions.initialize_session_state()

functions.required_files_dashboard(config.required_files_description)

if st.button("I want to upload more files"):
    functions.upload_file()

