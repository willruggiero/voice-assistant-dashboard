import streamlit as st
import pandas as pd
import altair as alt

# Page config
st.set_page_config(page_title="Voice Assistant Failures Dashboard", layout="wide")
st.title("🎤 Voice Assistant Failures: Exploring the Human Impact")
st.caption("Interactive dashboard summarizing when and why voice assistants fail, "
           "who is most affected, and the patterns across demographics.")

# ==============================
# Load and clean data
# ==============================
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("voice-assistant-failures.csv")
    df.fillna("Unknown", inplace=True)

    df['Gender'] = df['gender'].map({
        'Woman': 'Woman',
        'Man': 'Man',
        'Man,Woman': 'Non-binary / Other',
        'Prefer not to answer': 'Prefer not to answer'
    }).fillna('Unknown')

    df['Has Accent'] = df['accent'].map({
        'Yes': 'Yes', 'No': 'No', 'Maybe': 'Maybe', 'Unknown': 'Unknown'
    }).fillna('Unknown')

    age_order = ['18-24', '25-34', '35-44', '45-54', '55-64', 'Prefer not to answer', 'Unknown']
    df['Age Group'] = df['age'].apply(lambda x: x if x in age_order else 'Unknown')

    df['Race / Ethnicity'] = df['race'].apply(
        lambda x: 'Multi / Other' if ',' in str(x) else x
    ).fillna('Unknown')

    frequency_mapping = {
        'Daily': 7, '4-6 times a week': 5, '2-3 times a week': 2.5,
        'Once a week': 1, 'Unknown': 0
    }
    df['Weekly Use (days)'] = df['Frequency'].map(frequency_mapping).fillna(0)

    return df

df = load_and_clean_data()

# ==============================
# Filters
# ==============================
st.sidebar.header("🔍 Filters")
failure_types = sorted(df['Failure_Type'].unique())
accents = sorted(df['Has Accent'].unique())
genders = sorted(df['Gender'].unique())
races = sorted(df['Race / Ethnicity'].unique())

selected_failure = st.sidebar.multiselect("Failure Type", failure_types, default=failure_types)
selected_accent = st.sidebar.multiselect("Has Accent", accents, default=accents)
selected_gender = st.sidebar.multiselect("Gender", genders, default=genders)
selected_race = st.sidebar.multiselect("Race / Ethnicity", races, default=races)

df_filtered = df[
    df['Failure_Type'].isin(selected_failure) &
    df['Has Accent'].isin(selected_accent) &
    df['Gender'].isin(selected_gender) &
    df['Race / Ethnicity'].isin(selected_race)
]

# ==============================
# Section 1: Failure Overview
# ==============================
st.header("❗ Common Failure Types & Sources")
st.write("Select filters on the left to see how failure types and sources change across demographics.")

fail_type_counts = df_filtered['Failure_Type'].value_counts(normalize=True).reset_index()
fail_type_counts.columns = ['Failure Type', 'Proportion']

fail_source_counts = df_filtered['Failure_Source'].value_counts(normalize=True).reset_index()
fail_source_counts.columns = ['Failure Source', 'Proportion']

col1, col2 = st.columns(2)
with col1:
    chart1 = alt.Chart(fail_type_counts).mark_bar(color='crimson').encode(
        x=alt.X('Proportion:Q', axis=alt.Axis(format='%')),
        y=alt.Y('Failure Type:N', sort='-x'),
        tooltip=['Failure Type', alt.Tooltip('Proportion:Q', format='.1%')]
    ).properties(title="Most Common Failure Types", height=250)
    st.altair_chart(chart1, use_container_width=True)

with col2:
    chart2 = alt.Chart(fail_source_counts).mark_bar(color='orange').encode(
        x=alt.X('Proportion:Q', axis=alt.Axis(format='%')),
        y=alt.Y('Failure Source:N', sort='-x'),
        tooltip=['Failure Source', alt.Tooltip('Proportion:Q', format='.1%')]
    ).properties(title="Most Common Failure Sources", height=250)
    st.altair_chart(chart2, use_container_width=True)

# ==============================
# Section 2: Accent & Failure Relationship
# ==============================
st.header("🗣️ Accent & Failure Relationship")
st.write("Percentages reflect the proportion of each failure type within accent categories.")

accent_summary = df_filtered.groupby(['Has Accent', 'Failure_Type']).size().reset_index(name='Count')
accent_totals = df_filtered.groupby('Has Accent').size().reset_index(name='Total')
accent_summary = accent_summary.merge(accent_totals, on='Has Accent')
accent_summary['Proportion'] = accent_summary['Count'] / accent_summary['Total']

accent_chart = alt.Chart(accent_summary).mark_bar().encode(
    x=alt.X('Has Accent:N', title='Has Accent'),
    y=alt.Y('Proportion:Q', axis=alt.Axis(format='%')),
    color='Failure_Type:N',
    tooltip=['Has Accent', 'Failure_Type', alt.Tooltip('Proportion:Q', format='.1%'), 'Count']
).properties(height=300)
st.altair_chart(accent_chart, use_container_width=True)

# ==============================
# Section 3: Demographic Breakdown
# ==============================
st.header("👥 Demographic Differences in Failures")
st.write("Failure proportions shown within each demographic group.")

gender_failure = df_filtered.groupby(['Gender', 'Failure_Type']).size().reset_index(name='Count')
gender_totals = df_filtered.groupby('Gender').size().reset_index(name='Total')
gender_failure = gender_failure.merge(gender_totals, on='Gender')
gender_failure['Proportion'] = gender_failure['Count'] / gender_failure['Total']

gender_chart = alt.Chart(gender_failure).mark_bar().encode(
    x='Gender:N',
    y=alt.Y('Proportion:Q', axis=alt.Axis(format='%')),
    color='Failure_Type:N',
    tooltip=['Gender', 'Failure_Type', alt.Tooltip('Proportion:Q', format='.1%'), 'Count']
).properties(height=300)
st.altair_chart(gender_chart, use_container_width=True)

with st.expander("Race & Accent Interactions"):
    race_data = df_filtered.groupby(['Race / Ethnicity', 'Has Accent', 'Failure_Type']).size().reset_index(name='Count')
    race_chart = alt.Chart(race_data).mark_circle(size=100).encode(
        x='Race / Ethnicity:N',
        y='Failure_Type:N',
        size='Count:Q',
        color='Has Accent:N',
        tooltip=['Race / Ethnicity', 'Failure_Type', 'Has Accent', 'Count']
    ).properties(height=300)
    st.altair_chart(race_chart, use_container_width=True)

# ==============================
# Section 4: Age & Usage
# ==============================
st.header("📅 Age and Usage Patterns")
st.write("Usage patterns can influence how often failures occur.")

age_data = df_filtered[df_filtered['Age Group'] != 'Unknown'].groupby(
    ['Age Group', 'Has Accent', 'Failure_Type']
).size().reset_index(name='Count')

age_chart = alt.Chart(age_data).mark_bar().encode(
    x=alt.X('Age Group:N', sort=['18-24', '25-34', '35-44', '45-54', '55-64']),
    y='Count:Q',
    color='Failure_Type:N',
    column=alt.Column('Has Accent:N', title='Has Accent'),
    tooltip=['Age Group', 'Failure_Type', 'Count']
).properties(height=200)
st.altair_chart(age_chart, use_container_width=True)

with st.expander("Average Weekly Usage by Gender"):
    usage = df_filtered.groupby('Gender')['Weekly Use (days)'].mean().reset_index()
    usage_chart = alt.Chart(usage).mark_bar(color='teal').encode(
        x='Gender:N',
        y='Weekly Use (days):Q',
        tooltip=['Gender', 'Weekly Use (days)']
    ).properties(title="Average Weekly Use", height=300)
    st.altair_chart(usage_chart, use_container_width=True)

# ==============================
# Key Term Help
# ==============================
st.markdown("""
---
**Key Terms**  
- **Failure**: Any instance where the voice assistant did not respond as intended.  
- **Capture**: The system recorded input but did not interpret it correctly.  
- **Maybe (Accent)**: Respondent was unsure whether they had an accent.  
""")
