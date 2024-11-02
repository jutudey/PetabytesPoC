import streamlit as st
import os
import pandas as pd
from datetime import datetime
import functions

app_name = functions.set_page_definitition()

st.title("💾   File Manager")

# Directory to store uploaded files
data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Two-column layout
left_column, right_column = st.columns([1, 2])

# File Upload in the left column
with left_column:
    st.subheader("Upload New File")
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file is not None:
        file_name, file_extension = os.path.splitext(uploaded_file.name)
        file_path = os.path.join(data_folder, uploaded_file.name)
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{os.path.basename(file_path)}' uploaded successfully! Refresh the page to see updated file list.")

# List of Files in the right column
with right_column:
    st.subheader("Files in Data Folder")
    files = [f for f in os.listdir(data_folder) if f not in ['.DS_Store', '.ipynb_checkpoints'] and not f.endswith('.ipynb')]
    if files:
        file_data = []
        for file in files:
            file_path = os.path.join(data_folder, file)
            if os.path.isfile(file_path):
                num_lines = sum(1 for line in open(file_path)) if file.endswith(".csv") else 'N/A'
                upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                file_data.append((file, num_lines, upload_time))

        # Display files as a DataFrame
        file_df = pd.DataFrame(file_data, columns=["File Name", "Number of Lines", "Upload Date"])
        st.dataframe(file_df, height=600, use_container_width=True)
    else:
        st.write("No files uploaded yet.")

# File Delete Functionality
with left_column:
    st.subheader("Delete Files")
    if files:
        delete_file = st.selectbox("Select a file to delete", sorted(files))
        if st.button("Delete File"):
            os.remove(os.path.join(data_folder, delete_file))
            st.success(f"File '{delete_file}' deleted successfully!")
    else:
        st.write("No files available for deletion.")

