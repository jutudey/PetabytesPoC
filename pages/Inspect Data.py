import streamlit as st
import pandas as pd
import config
import functions
import os

# Set the app details
app_name = functions.set_page_definitition()

with st.spinner('Loading and preparing data...'):
    functions.initialize_session_state()

# define 2 streamlit tabs
raw_data_tab, invoice_lines_tab = st.tabs(["Inspect the source files", "Inspect the processed Invoice Lines Data"])

# with raw_data_tab:
#     files_for_analysis = [[sublist[0], sublist[2]] for sublist in config.required_files_description]
#     files_for_analysis = pd.DataFrame(files_for_analysis, columns=['File Name', 'filename_prefix'])
#
#     def safe_get_newest_filename(value):
#         result = functions.get_newest_filename(value)
#         return result if result else "Not uploaded yet"
#
#     files_for_analysis['latest_uploaded_file'] = files_for_analysis.iloc[:, 1].apply(safe_get_newest_filename)
#     # st.dataframe(files_for_analysis)
#
#     unique_file_names = files_for_analysis['File Name'].unique()
#     selected_file_name = st.selectbox("Select a File Name", unique_file_names)
#
#     latest_file = files_for_analysis.loc[
#         files_for_analysis['File Name'] == selected_file_name, 'latest_uploaded_file'
#     ].values[0]
#
#     folder_path = 'data/'
#
#     if latest_file == "Not uploaded yet":
#         st.warning("The file has not been uploaded yet.")
#     else:
#         file_path = os.path.join(folder_path, latest_file)
#
#         if latest_file.endswith('.csv'):
#             df = pd.read_csv(file_path)
#             # st.write("CSV file loaded successfully.")
#             st.header(latest_file)
#             st.dataframe(df, hide_index=True)
#         elif latest_file.endswith('.xlsx'):
#             df = pd.read_excel(file_path)
#             # st.write("Excel file loaded successfully.")
#             st.header(latest_file)
#             st.dataframe(df, hide_index=True)
#         else:
#             st.error("The file format is not supported.")

with invoice_lines_tab:
    df = st.session_state.all_invoice_lines

    # if df is None:
    #     df = functions.merge_invoice_lines_and_payments()
    #     st.session_state['df'] = df

    st.title("️🔍  Inspect the Invoice Lines Data")

    filter_col, empty_col, summary_col = st.columns([5, 0.5, 2])

    with filter_col:
        filtered_df = functions.filter_dataframe(df)

        number_invoice_lines = filtered_df["Invoice Line ID"].count()
        sum_internal_cost = f"£{filtered_df['Product Cost'].sum():,.2f}"
        sum_sales_price = f"£{filtered_df['Standard Price(incl)'].sum():,.2f}"
        theoretical_profit_value = filtered_df['Standard Price(incl)'].sum() - filtered_df["Product Cost"].sum()
        theoretical_profit = f"£{theoretical_profit_value:,.2f}"
        sum_actual_invoiced = f"£{filtered_df['Total Invoiced (incl)'].sum():,.2f}"
        applied_discount_value = filtered_df['Standard Price(incl)'].sum() - filtered_df['Total Invoiced (incl)'].sum()
        applied_discount = f"£{applied_discount_value:,.2f}"


        st.dataframe(filtered_df[[
            'Invoice Line Date: Created', 'Invoice Line ID',
            'Invoice Date', 'Product Name', 'Product Description', 'Product Group', 'reporting_categories',
            'Created By', 'created_by_category', 'Client Contact Code',
            'Business Name', 'First Name', 'Last Name',
            'Animal Code', 'Animal Name', 'Species', 'Breed',
            'Product Cost', 'Standard Price(incl)', 'Discount(£)', 'Total Invoiced (incl)'
        ]], hide_index=True)

    with summary_col:
        container = st.container(border=True)
        container.write(f"Number of Invoice Lines: {number_invoice_lines}")
        container.write(f"Sum Internal Cost: {sum_internal_cost}")
        container.write(f"Sum Sales Price: {sum_sales_price}")
        container.write(f"Theoretical Profit: {theoretical_profit}")
        container.write(f"Sum Actual Invoiced: {sum_actual_invoiced}")
        container.write(f"Applied Discounts: {applied_discount}")
