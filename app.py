import pandas as pd
import os
import json
import xlrd
import openpyxl ##NEW##
import streamlit as st
from io import StringIO


def read_file(file):
    file_name, file_extension = os.path.splitext(file.name)
    file_extension = file_extension.lower()

    if file_extension == ".csv":
        df = pd.read_csv(file)
    elif file_extension == ".xlsx":
        df = pd.read_excel(file)
    elif file_extension == ".json":
        df = pd.read_json(file)
    elif file_extension == ".xls":
        df = pd.read_excel(file)
    else:
        st.error("Unsupported file type.")
        return None

    return df


st.title("Data Cleaning Tool")

uploaded_file = st.file_uploader(
    "Choose a file. Upload a CSV, Excel or JSON.",
    type=["csv", "xls", "xlsx", "json"],
)

if uploaded_file is not None:
    # Read original data
    df = read_file(uploaded_file)

    if df is not None:
        if ("current_filename" not in st.session_state or st.session_state["current_filename"] != uploaded_file.name):
            st.session_state["current_filename"] = uploaded_file.name
            st.session_state["df_cleaned"] = df.copy()

        df_cleaned = st.session_state["df_cleaned"]

        st.subheader("Preview of Original File")
        st.dataframe(df.head())

        st.subheader("Original File Information")
        st.write(f"Shape of Data: {df.shape[0]} rows, {df.shape[1]} columns")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Variable Data Types (original)")
            st.dataframe(df.dtypes.astype(str))
        with col2:
            st.write("Count of N/As (original)")
            st.dataframe(df.isna().sum())

        st.markdown("---")
        st.write("### What kind of cleaning would you like to do?")
        clean_choice = st.radio(
            "Choose one:",
            ("Remove all N/As", "Clean individual columns", "Remove Duplicates"),
        )

        # CLEANING WHOLE TABLE
        if clean_choice == "Remove all N/As":
            if st.button("Apply Cleaning (whole table)"):
                df_new = df_cleaned.dropna()
                st.session_state["df_cleaned"] = df_new
                st.success("Cleaning complete!")
                csv = df_cleaned.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Cleaned File",
                    data=csv,
                    file_name="cleaned_output.csv",
                    mime="text/csv",
                )

        # REMOVING DUPLICATES
        elif clean_choice == "Remove Duplicates":
            st.write("This will remove duplicate rows.")
            if st.button("Remove Duplicate Rows"):
                initial_rows = len(df_cleaned)
                df_new = df_cleaned.drop_duplicates()
                dup_count = initial_rows - len(df_new)
                st.session_state["df_cleaned"] = df_new
                st.success(f"Removed {dup_count} duplicates!")
                csv = df_cleaned.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Cleaned File",
                    data=csv,
                    file_name="cleaned_output.csv",
                    mime="text/csv",
                )


        # CLEAN INDIVIDUAL COLUMNS
        else:
            all_cols = list(df_cleaned.columns)
            selected_cols = st.multiselect("Select columns to clean", all_cols)
            cleaning_ops = {}

            if selected_cols:
                for col in selected_cols:
                    st.write(f"#### Column: **{col}**")
                    choice = st.selectbox(
                        f"What cleaning to perform on {col}?",
                        ("None", "Remove NAs", "Change Type", "Format as Date", "Drop Column"),
                        key=f"action_{col}",
                    )
                    col_ops = {"action": choice, "type": None}
                    if choice == "Change Type":
                        new_type = st.selectbox(
                            f"Convert {col} to:",
                            ("String", "Float", "Boolean"),
                            key=f"type_{col}",
                        )
                        col_ops["type"] = new_type
                    cleaning_ops[col] = col_ops

                if st.button("Apply Cleaning for selected columns"):
                    df_new = df_cleaned.copy()
                    for col, ops in cleaning_ops.items():
                        action = ops["action"]
                        new_type = ops.get("type")
                        if action == "Remove NAs":
                            df_new = df_new[df_new[col].notna()]
                        elif action == "Change Type":
                            if new_type == "String":
                                df_new[col] = df_new[col].astype(str)
                            elif new_type == "Float":
                                df_new[col] = pd.to_numeric(df_new[col], errors="coerce")
                            elif new_type == "Boolean":
                                df_new[col] = df_new[col].astype(bool)

                        elif action == "Format as Date":
                            df_new[col] = pd.to_datetime(df_new[col], errors="coerce")
                        elif action == "Drop Column":
                            df_new=df_new.drop(columns=[col])

                    st.session_state["df_cleaned"] = df_new
                    st.success("Column cleaning complete!")

        # CURRENT CLEANED DATA + DOWNLOAD - Indented 

            st.markdown("---")
            st.subheader("Current cleaned data (working copy)")
            df_cleaned = st.session_state["df_cleaned"]
            st.dataframe(df_cleaned.head())
            st.subheader("Current cleaned dtypes")
            st.dataframe(df_cleaned.dtypes.astype(str))

            csv = df_cleaned.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Cleaned File",
                data=csv,
                file_name="cleaned_output.csv",
                mime="text/csv",
            )
