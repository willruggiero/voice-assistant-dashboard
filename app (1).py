
import streamlit as st
import pandas as pd
import altair as alt

st.title("Voice Assistant Failures Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("voice-assistant-failures.csv")  # fallback for local use

# Sidebar filters
races = st.sidebar.multiselect("Race", df["race"].unique(), default=df["race"].unique())
ages = st.sidebar.multiselect("Age", df["age"].unique(), default=df["age"].unique())
accents = st.sidebar.multiselect("Accent", df["accent"].unique(), default=df["accent"].unique())
genders = st.sidebar.multiselect("Gender", df["gender"].unique(), default=df["gender"].unique())

# Filtered data
filtered_df = df[
    (df["race"].isin(races)) &
    (df["age"].isin(ages)) &
    (df["accent"].isin(accents)) &
    (df["gender"].isin(genders))
]

# Chart: Failure Types by Accent
chart = alt.Chart(filtered_df).mark_bar().encode(
    x="Failure_Type:N",
    y="count()",
    color="accent:N",
    tooltip=["Failure_Type", "accent", "count()"]
).properties(
    title="Failure Types by Accent",
    width=600
)

st.altair_chart(chart, use_container_width=True)
