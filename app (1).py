import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("Voice Assistant Failures Dashboard")


df = pd.read_csv("voice-assistant-failures.csv")

# Clean and filter relevant columns
df_clean = df[['accent', 'race', 'age', 'Failure_Type', 'gender', 'Frequency', 'Failure_Source']].dropna()

# Sidebar filters
st.sidebar.header("Filters")
selected_race = st.sidebar.multiselect("Race", df_clean['race'].unique(), default=list(df_clean['race'].unique()))
selected_age = st.sidebar.multiselect("Age Group", df_clean['age'].unique(), default=list(df_clean['age'].unique()))
selected_accent = st.sidebar.multiselect("Accent", df_clean['accent'].unique(), default=list(df_clean['accent'].unique()))
selected_gender = st.sidebar.multiselect("Gender", df_clean['gender'].unique(), default=list(df_clean['gender'].unique()))

# Filter data by sidebar selections
filtered_df = df_clean[
    (df_clean['race'].isin(selected_race)) &
    (df_clean['age'].isin(selected_age)) &
    (df_clean['accent'].isin(selected_accent)) &
    (df_clean['gender'].isin(selected_gender))
]

# Filter top 3 failure types for first two charts (like original)
top_failure_types = filtered_df['Failure_Type'].value_counts().nlargest(3).index.tolist()
df_q2 = filtered_df[filtered_df['Failure_Type'].isin(top_failure_types)]

# Filter top 4 races for race chart (like original)
top_races = df_q2['race'].value_counts().nlargest(4).index.tolist()
df_race = df_q2[df_q2['race'].isin(top_races)]

# Selection for coordinated filtering by Failure_Type (click legend or bars)
failure_type_select = alt.selection_multi(fields=['Failure_Type'], bind='legend')

# Chart 1: Race Facet (Altair)
race_chart = alt.Chart(df_race).mark_bar(size=20).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.Color('accent:N', title='Accent', scale=alt.Scale(scheme='category10')),
    column=alt.Column('race:N', title='Race', spacing=30),
    tooltip=['Failure_Type', 'accent', 'race', 'count()']
).add_selection(
    failure_type_select
).properties(
    title='Failure Types by Accent and Race (Top 4)',
    width=240,
    height=300
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_header(
    titleFontSize=14,
    labelFontSize=8,
    labelAngle=0
).configure_legend(
    titleFontSize=13,
    labelFontSize=12,
    orient='top'
).configure_view(
    continuousWidth=240,
    continuousHeight=300
).configure_axisX(
    labelAngle=40
)

# Chart 2: Age Facet (Altair)
age_chart = alt.Chart(df_q2).mark_bar(size=20).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.Color('accent:N', title='Accent', scale=alt.Scale(scheme='category10')),
    column=alt.Column('age:N', title='Age Group', spacing=30),
    tooltip=['Failure_Type', 'accent', 'age', 'count()']
).transform_filter(
    failure_type_select
).properties(
    title='Failure Types by Accent and Age Group',
    width=240,
    height=300
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_header(
    titleFontSize=14,
    labelFontSize=13,
    labelAngle=0
).configure_legend(
    titleFontSize=13,
    labelFontSize=12,
    orient='top'
).configure_view(
    continuousWidth=240,
    continuousHeight=300
).configure_axisX(
    labelAngle=40
)

# Chart 3: Failure Types by Source (converted from Vega-Lite HTML)
source_df = filtered_df.groupby(['Failure_Type', 'Failure_Source']).size().reset_index(name='count')

source_chart = alt.Chart(source_df).mark_bar().encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count:Q', title='Count'),
    color=alt.Color('Failure_Source:N', title='Failure Source'),
    tooltip=['Failure_Type', 'Failure_Source', 'count']
).transform_filter(
    failure_type_select
).properties(
    title='Most Common Voice Assistant Failure Types by Source',
    width=600,
    height=300
)

# Chart 4: Failure Types by Accent (converted from Vega-Lite HTML)
accent_df = filtered_df.groupby(['Failure_Type', 'accent']).size().reset_index(name='count')

accent_chart = alt.Chart(accent_df).mark_bar().encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count:Q', title='Count'),
    color=alt.Color('accent:N', title='Accent'),
    tooltip=['Failure_Type', 'accent', 'count']
).transform_filter(
    failure_type_select
).properties(
    title='Failure Types Experienced by Users with/without Accents',
    width=600,
    height=300
)

# Chart 5: Voice Assistant Usage by Gender (converted from Vega-Lite HTML)
gender_df = filtered_df.groupby('gender').size().reset_index(name='count')

gender_chart = alt.Chart(gender_df).mark_bar().encode(
    x=alt.X('gender:N', title='Gender'),
    y=alt.Y('count:Q', title='Number of Users'),
    color=alt.Color('gender:N', title='Gender'),
    tooltip=['gender', 'count']
).properties(
    title='Voice Assistant Usage by Gender',
    width=400,
    height=300
)

# Layout the dashboard
st.markdown("### Failure Types by Accent and Race (Top 4 Races)")
st.altair_chart(race_chart, use_container_width=True)

st.markdown("### Failure Types by Accent and Age Group")
st.altair_chart(age_chart, use_container_width=True)

st.markdown("### Most Common Voice Assistant Failure Types by Source")
st.altair_chart(source_chart, use_container_width=True)

st.markdown("### Failure Types Experienced by Users with/without Accents")
st.altair_chart(accent_chart, use_container_width=True)

st.markdown("### Voice Assistant Usage by Gender")
st.altair_chart(gender_chart, use_container_width=True)
