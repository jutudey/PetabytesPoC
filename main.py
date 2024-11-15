import config
import streamlit as st
import pandas as pd
import datetime
import functions

functions.set_page_definitition()
st.title("Petabytes PoC")

with st.spinner('Loading and preparing data...'):
    functions.initialize_session_state()


if st.button("I want to upload more files"):
    col1, col2 = st.columns([3, 1])

    with col1:
        functions.required_files_description(config.required_files_description)

    with col2:
        functions.upload_file()
