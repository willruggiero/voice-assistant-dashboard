import streamlit as st
import pandas as pd
import altair as alt

# Assuming df_clean and datasets (source_data, accent_data, gender_data) are already loaded above

st.title("Voice Assistant Failures Dashboard with Rich Interactions")

# --- MULTIPLE UI INTERACTIONS ---

# Dropdown: Filter by Failure Type
failure_types = df_clean['Failure_Type'].unique().tolist()
selected_failure_type = st.selectbox("Filter by Failure Type", ["All"] + failure_types)

# Multi-select: Filter by Race
races = df_clean['race'].unique().tolist()
selected_races = st.multiselect("Select Races", options=races, default=races)

# Radio Buttons: Filter by Accent presence
accent_options = ['All', 'Yes', 'No', 'Maybe', 'Unknown']
selected_accent = st.radio("Accent Filter", options=accent_options)

# Slider: Minimum Frequency threshold
min_frequency = st.slider("Minimum Frequency", min_value=int(df_clean['Frequency'].min()), max_value=int(df_clean['Frequency'].max()), value=int(df_clean['Frequency'].min()))

# Filter dataframe based on UI selections
filtered_df = df_clean.copy()

if selected_failure_type != "All":
    filtered_df = filtered_df[filtered_df['Failure_Type'] == selected_failure_type]

if selected_races:
    filtered_df = filtered_df[filtered_df['race'].isin(selected_races)]

if selected_accent != "All":
    filtered_df = filtered_df[filtered_df['accent'] == selected_accent]

filtered_df = filtered_df[filtered_df['Frequency'] >= min_frequency]

# --- SELECTIONS FOR COORDINATED VISUALIZATIONS ---

# Selection for Race (single-click)
race_selection = alt.selection_single(fields=['race'], empty='all', on='click')

# Selection for Age group (multi-select via brushing)
age_selection = alt.selection_interval(encodings=['x'])

# Filter top failure types and top races again on filtered data
top_failure_types = filtered_df['Failure_Type'].value_counts().nlargest(3).index.tolist()
df_q2 = filtered_df[filtered_df['Failure_Type'].isin(top_failure_types)]
top_races = df_q2['race'].value_counts().nlargest(4).index.tolist()
df_race = df_q2[df_q2['race'].isin(top_races)]

# ---- RACE CHART with click selection and tooltip ----
race_chart = alt.Chart(df_race).mark_bar(size=20).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.condition(race_selection, alt.Color('accent:N', legend=alt.Legend(title='Accent')), alt.value('lightgray')),
    column=alt.Column('race:N', title='Race', spacing=30),
    tooltip=[alt.Tooltip('race:N'), alt.Tooltip('Failure_Type:N'), alt.Tooltip('accent:N'), alt.Tooltip('count()', title='Count')]
).add_selection(
    race_selection
).properties(
    title='Failure Types by Accent and Race (Top 4)',
    width=200,
    height=300
)

# --- AGE CHART with brushing selection and coordinated filtering ---
age_chart = alt.Chart(df_q2).mark_bar(size=20).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.Color('accent:N', legend=alt.Legend(title='Accent')),
    column=alt.Column('age:N', title='Age Group', spacing=30),
    tooltip=[alt.Tooltip('age:N'), alt.Tooltip('Failure_Type:N'), alt.Tooltip('accent:N'), alt.Tooltip('count()', title='Count')]
).transform_filter(
    race_selection  # coordinated filter: only show age data for selected race
).add_selection(
    age_selection
).properties(
    title='Failure Types by Accent and Age Group',
    width=200,
    height=300
)

# --- ACCENT CHART filtered by brushing selection on Age ---
accent_chart = alt.Chart(df_q2).mark_bar().encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Count'),
    color=alt.Color('accent:N', legend=alt.Legend(title='Accent')),
    tooltip=[alt.Tooltip('Failure_Type:N'), alt.Tooltip('accent:N'), alt.Tooltip('count()', title='Count')]
).transform_filter(
    age_selection  # coordinated filter by Age brushing selection
).properties(
    title="Failure Types Experienced by Users with/without Accents",
    width=600,
    height=300
)

# --- SOURCE CHART (static with tooltip) ---
source_chart = alt.Chart(source_data).mark_bar().encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count:Q', title='Count'),
    color=alt.Color('Failure_Source:N', title='Failure Source'),
    tooltip=['Failure_Type', 'Failure_Source', 'count']
).properties(
    title="Most Common Voice Assistant Failure Types by Source",
    width=600,
    height=300
)

# --- GENDER CHART (static with tooltip) ---
gender_chart = alt.Chart(gender_data).mark_bar().encode(
    x=alt.X('gender:N', title='Gender'),
    y=alt.Y('count:Q', title='Number of Users'),
    color=alt.Color('gender:N', legend=None),
    tooltip=[alt.Tooltip('gender:N'), alt.Tooltip('count:Q')]
).properties(
    title="Voice Assistant Usage by Gender",
    width=400,
    height=300
)

# --- STREAMLIT LAYOUT ---
st.markdown("### Filter Controls")
st.write(f"Selected Failure Type: **{selected_failure_type}**")
st.write(f"Selected Races: **{selected_races}**")
st.write(f"Selected Accent: **{selected_accent}**")
st.write(f"Minimum Frequency: **{min_frequency}**")

st.markdown("### Failure Types by Accent and Race (Click Race to Filter Age Chart)")
st.altair_chart(race_chart, use_container_width=True)

st.markdown("### Failure Types by Accent and Age Group (Brushing on X-axis filters Accent chart)")
st.altair_chart(age_chart, use_container_width=True)

st.markdown("### Failure Types Experienced by Users with/without Accents (Filtered by Age selection)")
st.altair_chart(accent_chart, use_container_width=True)

st.markdown("### Most Common Voice Assistant Failure Types by Source")
st.altair_chart(source_chart, use_container_width=True)

st.markdown("### Voice Assistant Usage by Gender")
st.altair_chart(gender_chart, use_container_width=True)
