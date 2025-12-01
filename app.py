import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Room Allotment", layout="wide")

# -------------------------------
# Load credentials + gspread ONLY ONCE (session_state)
# -------------------------------
if "client" not in st.session_state:
    creds_dict = {
        "type": st.secrets["type"],
        "project_id": st.secrets["project_id"],
        "private_key_id": st.secrets["private_key_id"],
        "private_key": st.secrets["private_key"],
        "client_email": st.secrets["client_email"],
        "client_id": st.secrets["client_id"],
        "auth_uri": st.secrets["auth_uri"],
        "token_uri": st.secrets["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["client_x509_cert_url"],
        "universe_domain": st.secrets["universe_domain"],
    }
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    st.session_state.client = gspread.authorize(creds)

# -------------------------------
# Load Google Sheet ONLY ONCE
# -------------------------------
if "df" not in st.session_state:
    sheet = st.session_state.client.open("Room").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    # Ensure ARRIVAL DATE is datetime
    if "ARRIVAL DATE" in df.columns:
        df["ARRIVAL DATE"] = pd.to_datetime(df["ARRIVAL DATE"], errors="coerce")
    st.session_state.df = df

df = st.session_state.df

# -------------------------------
# Title
# -------------------------------
st.title("🏨 Room Allotment List")

# -------------------------------
# FILTERS
# -------------------------------
st.subheader("Filters")

# Prepare columns for filters (3 per row)
cols = st.columns(3)
filter_values = {}

# Dynamically create filters for each column
for i, col_name in enumerate(df.columns):
    col = cols[i % 3]  # distribute filters across 3 columns
    if pd.api.types.is_datetime64_any_dtype(df[col_name]):
        # Date filter
        filter_values[col_name] = col.date_input(col_name, value=None)
    else:
        # Convert values to string for consistent sorting and display
        unique_vals = df[col_name].dropna().astype(str).unique()
        filter_values[col_name] = col.selectbox(
            col_name, [""] + sorted(unique_vals)
        )

# -------------------------------
# APPLY FILTERS
# -------------------------------
filtered = df.copy()

for col_name, val in filter_values.items():
    if val:
        if pd.api.types.is_datetime64_any_dtype(df[col_name]):
            filtered = filtered[filtered[col_name].dt.date == val]
        else:
            filtered = filtered[filtered[col_name].astype(str) == val]

# Convert ARRIVAL DATE to date for display
if "ARRIVAL DATE" in filtered.columns:
    filtered["ARRIVAL DATE"] = filtered["ARRIVAL DATE"].dt.date

# -------------------------------
# TABLE
# -------------------------------
st.subheader("Allotment List")
st.dataframe(filtered, use_container_width=True)
