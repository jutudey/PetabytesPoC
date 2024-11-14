import streamlit as st
import os
import pandas as pd
from datetime import datetime
import config
import functions


# Set page name or title
functions.set_page_definitition()

st.title("💾   File Manager")


# Directory to store uploaded files
data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Helper function to list files
def list_files():
    """
    List all files in the data folder, excluding certain system files and Jupyter notebook checkpoints.
    Returns a DataFrame with file names and their upload dates.
    """
    files = [f for f in os.listdir(data_folder) if f not in ['.DS_Store', '.ipynb_checkpoints'] and not f.endswith('.ipynb')]
    file_data = []
    for file in files:
        file_path = os.path.join(data_folder, file)
        if os.path.isfile(file_path):
            upload_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            file_data.append((file, upload_time))
    return pd.DataFrame(file_data, columns=["File Name", "Upload Date"]) if file_data else None

# Two-column layout
left_column, right_column = st.columns([1, 1])

# List of Files in the left column
with right_column:
    st.header("Files in Data Folder")
    file_df = list_files()
    if file_df is not None:
        # Sort the DataFrame by "Upload Date" in descending order
        file_df = file_df.sort_values(by="Upload Date", ascending=False)
        st.dataframe(file_df, height=500, use_container_width=True, hide_index=True)
    else:
        st.write("No files uploaded yet.")

    if st.button("Refresh Filelist"):
        selected_file = None
        st.rerun()

# File Upload in the right column
with right_column:
    st.header("Upload New File")
    functions.upload_file()

    if st.button("Refresh Filelist", key="rerun_trigger"):
        st.rerun()
    if st.button("Process new files"):
        functions.initialize_session_state("force_load")

if 'rerun_trigger' in st.session_state:
    del st.session_state['rerun_trigger']

# Add the download button at the bottom of the right column
with right_column:
    st.header("Download All Files")
    date_stamp = datetime.now().strftime("%Y%m%d")
    st.download_button(
        label="Download All Files",
        data=functions.create_zip_file(),
        file_name=f"all_files_{date_stamp}_{config.app_name}.zip",
        mime="application/zip"
    )

with left_column:
    functions.required_files_description(config.required_files_description)

