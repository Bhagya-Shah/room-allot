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


col1, col2, col3 = st.columns(3)
filter_values = {}

# MEMBER NAME filter
filter_values["MEMBER NAME"] = col1.selectbox(
    "Member Name", [""] + sorted(df["MEMBER NAME"].dropna().astype(str).unique())
)

# Room Key filter
filter_values["Room Key"] = col2.selectbox(
    "Room Key", [""] + sorted(df["Room Key"].dropna().astype(str).unique())
)

# Arrival Date filter
filter_values["ARRIVAL DATE"] = col3.date_input("Arrival Date", value=None)

# -------------------------------
# APPLY FILTERS
# -------------------------------
filtered = df.copy()

for col_name, val in filter_values.items():
    if val:
        if col_name == "ARRIVAL DATE":
            filtered = filtered[filtered[col_name].dt.date == val]
        else:
            filtered = filtered[filtered[col_name].astype(str) == val]

# Convert ARRIVAL DATE to date for display
if "ARRIVAL DATE" in filtered.columns:
    filtered["ARRIVAL DATE"] = filtered["ARRIVAL DATE"].dt.date

if any(filter_values.values()):
    st.markdown("### Filter Summary")
    st.write(f"Total Records: **{len(filtered)}**")

    if "Room Key" in filtered.columns:
        st.write("Room Key Counts:")
        st.write(filtered["Room Key"].value_counts())

# -------------------------------
# TABLE
# -------------------------------
st.subheader("Allotment List")
st.dataframe(filtered, use_container_width=True)
