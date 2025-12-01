import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json

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
    client = gspread.authorize(creds)
    st.session_state.client = gspread.authorize(creds)



# -------------------------------
# Load Google Sheet ONLY ONCE
# -------------------------------
if "df" not in st.session_state:
    sheet = st.session_state.client.open("Room").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["ARRIVAL DATE"] = pd.to_datetime(df["ARRIVAL DATE"], errors="coerce")
    st.session_state.df = df   # store permanently

df = st.session_state.df   # use stored data

# -------------------------------
# Title
# -------------------------------
st.title("🏨 Room Allotment List")

# -------------------------------
# FILTERS
# -------------------------------
st.subheader("Filters")

col1, col2, col3 = st.columns(3)

room_filter = col1.selectbox("Room Key", [""] + sorted(df["Room Key"].unique()))
name_filter = col2.selectbox("Member Name", [""] + sorted(df["MEMBER NAME"].unique()))
date_filter = col3.date_input("Arrival Date", value=None)

# -------------------------------
# APPLY FILTERS (FAST)
# -------------------------------
filtered = df.copy()

if room_filter:
    filtered = filtered[filtered["Room Key"] == room_filter]

if name_filter:
    filtered = filtered[filtered["MEMBER NAME"] == name_filter]

if date_filter:
    filtered = filtered[filtered["ARRIVAL DATE"].dt.date == date_filter]

# Convert to date only for display
filtered["ARRIVAL DATE"] = filtered["ARRIVAL DATE"].dt.date

# -------------------------------
# TABLE
# -------------------------------
st.subheader("Allotment List")
st.dataframe(filtered, use_container_width=True)
