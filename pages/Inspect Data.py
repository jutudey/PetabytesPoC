import streamlit as st
import pandas as pd
import functions

# sets the app details
app_name = functions.set_page_definitition()


appointments_path = "data/appointments.csv"
procedures_path = "data/Procedures.csv"
invoice_lines_path = "data/Invoice+Lines-2024-10-21-15-29-05.csv"

st.title("Inspect the Invoice Lines data")

df = functions.load_cvs_data(invoice_lines_path)

st.data_editor(df)

st.title("Inspect the procedures data")

df = functions.load_cvs_data(procedures_path)

st.data_editor(df)