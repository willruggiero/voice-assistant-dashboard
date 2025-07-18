import streamlit as st
import pandas as pd
import altair as alt

st.title("Voice Assistant Failures Dashboard")

# Load data
df = pd.read_csv("voice-assistant-failures.csv")
df_clean = df[['accent', 'race', 'age', 'Failure_Type', 'gender', 'Frequency']].dropna()

# 1. Prepare data for Race Facet Chart (Top 4 races and top 3 failure types)
top_failure_types = df_clean['Failure_Type'].value_counts().nlargest(3).index.tolist()
df_q2 = df_clean[df_clean['Failure_Type'].isin(top_failure_types)]
top_races = df_q2['race'].value_counts().nlargest(4).index.tolist()
df_race = df_q2[df_q2['race'].isin(top_races)]

bar_size = 20
facet_width = 240
facet_height = 300

race_chart = alt.Chart(df_race).mark_bar(size=bar_size).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.Color('accent:N', title='Accent', scale=alt.Scale(scheme='category10')),
    column=alt.Column('race:N', title='Race', spacing=30)
).properties(
    title='Failure Types by Accent and Race (Top 4)',
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
    continuousWidth=facet_width,
    continuousHeight=facet_height
).configure_axisX(
    labelAngle=40
)

# 2. Prepare data for Age Facet Chart
age_chart = alt.Chart(df_q2).mark_bar(size=bar_size).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.Color('accent:N', title='Accent', scale=alt.Scale(scheme='category10')),
    column=alt.Column('age:N', title='Age Group', spacing=30)
).properties(
    title='Failure Types by Accent and Age Group',
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
    continuousWidth=facet_width,
    continuousHeight=facet_height
).configure_axisX(
    labelAngle=40
)

# 3. Most Common Failure Types by Source - hardcoded from your Vega-Lite spec
source_data = pd.DataFrame([
    {"Failure_Type": "Attention", "Failure_Source": "Delayed Trigger", "count": 8},
    {"Failure_Type": "Attention", "Failure_Source": "Missed Trigger", "count": 25},
    {"Failure_Type": "Attention", "Failure_Source": "Spurious Trigger", "count": 11},
    {"Failure_Type": "Perception", "Failure_Source": "Noisy Channel", "count": 22},
    {"Failure_Type": "Perception", "Failure_Source": "Overcapture", "count": 7},
    {"Failure_Type": "Perception", "Failure_Source": "Transcription", "count": 15},
    {"Failure_Type": "Perception", "Failure_Source": "Truncation", "count": 7},
    {"Failure_Type": "Response", "Failure_Source": "Action Execution: Incorrect", "count": 14},
    {"Failure_Type": "Response", "Failure_Source": "Action Execution: No Action", "count": 14},
    {"Failure_Type": "Understanding", "Failure_Source": "Ambiguity", "count": 18},
    {"Failure_Type": "Understanding", "Failure_Source": "Misunderstanding", "count": 38},
    {"Failure_Type": "Understanding", "Failure_Source": "No Understanding", "count": 20}
])

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

# 4. Failure Types by Accent (Yes/No/Maybe etc)
accent_data = pd.DataFrame([
    {"accent": "Maybe", "Failure_Type": "Attention", "count": 16},
    {"accent": "Maybe", "Failure_Type": "Perception", "count": 20},
    {"accent": "Maybe", "Failure_Type": "Response", "count": 4},
    {"accent": "Maybe", "Failure_Type": "Understanding", "count": 31},
    {"accent": "No", "Failure_Type": "Attention", "count": 20},
    {"accent": "No", "Failure_Type": "Perception", "count": 24},
    {"accent": "No", "Failure_Type": "Response", "count": 19},
    {"accent": "No", "Failure_Type": "Understanding", "count": 34},
    {"accent": "Unknown", "Failure_Type": "Attention", "count": 1},
    {"accent": "Unknown", "Failure_Type": "Understanding", "count": 2},
    {"accent": "Yes", "Failure_Type": "Attention", "count": 7},
    {"accent": "Yes", "Failure_Type": "Perception", "count": 7},
    {"accent": "Yes", "Failure_Type": "Response", "count": 5},
    {"accent": "Yes", "Failure_Type": "Understanding", "count": 9}
])

accent_chart = alt.Chart(accent_data).mark_bar().encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count:Q', title='Count'),
    color=alt.Color('accent:N', title='Accent'),
    tooltip=['accent', 'Failure_Type', 'count']
).properties(
    title="Failure Types Experienced by Users with/without Accents",
    width=600,
    height=300
)

# 5. Voice Assistant Usage by Gender
gender_data = pd.DataFrame([
    {"gender": "Man", "count": 101},
    {"gender": "Woman", "count": 90},
    {"gender": "Prefer Not To Answer", "count": 4},
    {"gender": "Unknown", "count": 3},
    {"gender": "Man,Woman", "count": 1}
])

gender_chart = alt.Chart(gender_data).mark_bar().encode(
    x=alt.X('gender:N', title='Gender'),
    y=alt.Y('count:Q', title='Number of Users'),
    color=alt.Color('gender:N', legend=None),
    tooltip=['gender', 'count']
).properties(
    title="Voice Assistant Usage by Gender",
    width=400,
    height=300
)

# Display all charts with titles and spacing
st.markdown("## Failure Types by Accent and Race (Top 4 Races)")
st.altair_chart(race_chart, use_container_width=True)

st.markdown("## Failure Types by Accent and Age Group")
st.altair_chart(age_chart, use_container_width=True)

st.markdown("## Most Common Voice Assistant Failure Types by Source")
st.altair_chart(source_chart, use_container_width=True)

st.markdown("## Failure Types Experienced by Users with/without Accents")
st.altair_chart(accent_chart, use_container_width=True)

st.markdown("## Voice Assistant Usage by Gender")
st.altair_chart(gender_chart, use_container_width=True)

