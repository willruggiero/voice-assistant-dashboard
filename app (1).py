import streamlit as st
import pandas as pd
import altair as alt

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv('voice-assistant-failures.csv')
    df_clean = df[['accent', 'race', 'age', 'Failure_Type', 'gender', 'Frequency']].dropna()
    return df_clean

df_clean = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filter Data")

failure_types = df_clean['Failure_Type'].unique().tolist()
selected_failures = st.sidebar.multiselect("Select Failure Types", failure_types, default=failure_types)

races = df_clean['race'].unique().tolist()
selected_races = st.sidebar.multiselect("Select Races", races, default=races)

accents = df_clean['accent'].unique().tolist()
selected_accents = st.sidebar.multiselect("Select Accents", accents, default=accents)

ages = df_clean['age'].unique().tolist()
selected_ages = st.sidebar.multiselect("Select Age Groups", ages, default=ages)

genders = df_clean['gender'].unique().tolist()
selected_genders = st.sidebar.multiselect("Select Genders", genders, default=genders)

# Filter data based on sidebar selections
df_filtered = df_clean[
    (df_clean['Failure_Type'].isin(selected_failures)) &
    (df_clean['race'].isin(selected_races)) &
    (df_clean['accent'].isin(selected_accents)) &
    (df_clean['age'].isin(selected_ages)) &
    (df_clean['gender'].isin(selected_genders))
]

# --- Prepare charts data ---
# Top 3 failure types for facets
top_failure_types = df_filtered['Failure_Type'].value_counts().nlargest(3).index.tolist()
df_top_failures = df_filtered[df_filtered['Failure_Type'].isin(top_failure_types)]

# Top 4 races
top_races = df_top_failures['race'].value_counts().nlargest(4).index.tolist()
df_top_races = df_top_failures[df_top_failures['race'].isin(top_races)]

# --- Selection & Interaction ---
selection = alt.selection_multi(fields=['Failure_Type'], bind='legend')  # Multi-select via legend

brush = alt.selection_interval(encodings=['x'])  # Brushing on X axis

# --- Chart 1: Race Facet ---
race_chart = alt.Chart(df_top_races).mark_bar(size=20).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.Color('accent:N', scale=alt.Scale(scheme='category10')),
    column=alt.Column('race:N', title='Race', spacing=30),
    tooltip=['Failure_Type', 'race', 'accent', 'count()'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
).add_selection(
    selection,
    brush
).properties(
    title='Failure Types by Accent and Race (Top 4)',
    width=240,
    height=300
).configure_axisX(labelAngle=40)

# --- Chart 2: Age Facet ---
age_chart = alt.Chart(df_top_failures).mark_bar(size=20).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.Color('accent:N', scale=alt.Scale(scheme='category10')),
    column=alt.Column('age:N', title='Age Group', spacing=30),
    tooltip=['Failure_Type', 'age', 'accent', 'count()'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
).transform_filter(
    brush
).properties(
    title='Failure Types by Accent and Age Group',
    width=240,
    height=300
).configure_axisX(labelAngle=40)

# --- Chart 3: Failure Types by Source ---
# Aggregate for this chart
df_source = df_filtered.groupby(['Failure_Type', 'Failure_Source']).size().reset_index(name='count')

failure_source_chart = alt.Chart(df_source).mark_bar().encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count:Q', title='Count'),
    color=alt.Color('Failure_Source:N'),
    tooltip=['Failure_Type', 'Failure_Source', 'count'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
).add_selection(selection).properties(
    title='Most Common Voice Assistant Failure Types by Source',
    width=600,
    height=300
)

# --- Chart 4: Failure Types by Accent ---
df_accent = df_filtered.groupby(['Failure_Type', 'accent']).size().reset_index(name='count')

accent_chart = alt.Chart(df_accent).mark_bar().encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count:Q', title='Count'),
    color=alt.Color('accent:N'),
    tooltip=['Failure_Type', 'accent', 'count'],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
).add_selection(selection).properties(
    title='Failure Types Experienced by Users with/without Accents',
    width=600,
    height=300
)

# --- Chart 5: Voice Assistant Usage by Gender ---
df_gender = df_filtered.groupby(['gender']).size().reset_index(name='count')

gender_chart = alt.Chart(df_gender).mark_bar().encode(
    x=alt.X('gender:N', title='Gender'),
    y=alt.Y('count:Q', title='Number of Users'),
    color=alt.Color('gender:N'),
    tooltip=['gender', 'count']
).properties(
    title='Voice Assistant Usage by Gender',
    width=400,
    height=300
)

# --- Layout in Streamlit ---
st.title("Voice Assistant Failures Dashboard")

st.markdown("### Use the sidebar filters to explore data.")

# Show charts one by one
st.altair_chart(race_chart, use_container_width=True)
st.altair_chart(age_chart, use_container_width=True)
st.altair_chart(failure_source_chart, use_container_width=True)
st.altair_chart(accent_chart, use_container_width=True)
st.altair_chart(gender_chart, use_container_width=True)
