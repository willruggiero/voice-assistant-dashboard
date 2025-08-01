import streamlit as st
import pandas as pd
import altair as alt

# Set up Streamlit page
st.set_page_config(page_title="Voice Assistant Failures Dashboard", layout="wide")
st.title("Voice Assistant Failures Dashboard")

# ==============================
# Load and clean data
# ==============================
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("voice-assistant-failures.csv")
    df['Failure_Type'] = df['Failure_Type'].fillna('Unknown')
    df['Failure_Source'] = df['Failure_Source'].fillna('Unknown')
    df['gender'] = df['gender'].fillna('Unknown')
    df['age'] = df['age'].fillna('Unknown')
    df['race'] = df['race'].fillna('Unknown')
    df['accent'] = df['accent'].fillna('Unknown')

    gender_mapping = {
        'Woman': 'Woman',
        'Man': 'Man',
        'Man,Woman': 'Non-binary/Other',
        'Prefer not to answer': 'Prefer not to answer'
    }
    df['gender_clean'] = df['gender'].map(gender_mapping).fillna(df['gender'])

    df['has_accent'] = df['accent'].map({
        'Yes': 'Yes', 'No': 'No', 'Maybe': 'Maybe', 'Unknown': 'Unknown'
    }).fillna('Unknown')

    age_order = ['18-24', '25-34', '35-44', '45-54', '55-64', 'Prefer not to answer', 'Unknown']
    df['age_clean'] = df['age'].apply(lambda x: x if x in age_order else 'Unknown')
    return df

df = load_and_clean_data()

# ==============================
# Dashboard sections
# ==============================

st.header("Failure Types and Sources")
failure_counts = df['Failure_Type'].value_counts().reset_index()
failure_counts.columns = ['Failure_Type', 'count']
failure_chart = alt.Chart(failure_counts).mark_bar(color='steelblue').encode(
    x=alt.X('count:Q', title='Number of Failures'),
    y=alt.Y('Failure_Type:N', sort='-x'),
    tooltip=['Failure_Type:N', 'count:Q']
).properties(width=400, height=200)
st.altair_chart(failure_chart, use_container_width=True)

source_counts = df['Failure_Source'].value_counts().reset_index()
source_counts.columns = ['Failure_Source', 'count']
source_chart = alt.Chart(source_counts).mark_bar(color='orange').encode(
    x=alt.X('count:Q', title='Number of Failures'),
    y=alt.Y('Failure_Source:N', sort='-x'),
    tooltip=['Failure_Source:N', 'count:Q']
).properties(width=400, height=250)
st.altair_chart(source_chart, use_container_width=True)

heatmap_data = df.groupby(['Failure_Type', 'Failure_Source']).size().reset_index(name='count')
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x=alt.X('Failure_Source:N'),
    y=alt.Y('Failure_Type:N'),
    color=alt.Color('count:Q', scale=alt.Scale(scheme='blues')),
    tooltip=['Failure_Type', 'Failure_Source', 'count']
).properties(width=600, height=300)
st.altair_chart(heatmap, use_container_width=True)

# ==============================
st.header("Accent and Failures")
df_accent = df[df['has_accent'] != 'Unknown']
accent_data = df_accent.groupby(['has_accent', 'Failure_Type']).size().reset_index(name='count')
accent_totals = df_accent.groupby('has_accent').size().reset_index(name='total')
accent_data = accent_data.merge(accent_totals, on='has_accent')
accent_data['proportion'] = accent_data['count'] / accent_data['total']

accent_chart = alt.Chart(accent_data).mark_bar().encode(
    x=alt.X('has_accent:N', title='Has Accent'),
    y=alt.Y('proportion:Q', title='Proportion'),
    color=alt.Color('Failure_Type:N'),
    tooltip=['has_accent', 'Failure_Type', 'proportion']
).properties(width=500, height=300)
st.altair_chart(accent_chart, use_container_width=True)

# ==============================
st.header("Demographics and Failures")
df['race_clean'] = df['race'].apply(lambda x: 'Multi/Other' if ',' in str(x) else x)
race_data = df.groupby(['race_clean', 'has_accent', 'Failure_Type']).size().reset_index(name='count')
race_chart = alt.Chart(race_data).mark_circle(size=100).encode(
    x='race_clean:N',
    y='Failure_Type:N',
    size='count:Q',
    color='has_accent:N',
    tooltip=['race_clean', 'Failure_Type', 'count']
).properties(width=600, height=300)
st.altair_chart(race_chart, use_container_width=True)

age_data = df[df['age_clean'] != 'Unknown'].groupby(['age_clean', 'has_accent', 'Failure_Type']).size().reset_index(name='count')
age_chart = alt.Chart(age_data).mark_bar().encode(
    x=alt.X('age_clean:N', sort=['18-24', '25-34', '35-44', '45-54', '55-64']),
    y='count:Q',
    color='Failure_Type:N',
    column='has_accent:N',
    tooltip=['age_clean', 'Failure_Type', 'count']
).properties(width=150, height=200)
st.altair_chart(age_chart, use_container_width=True)

# ==============================
st.header("Gender Analysis")
gender_counts = df['gender_clean'].value_counts().reset_index()
gender_counts.columns = ['gender_clean', 'count']
gender_pie = alt.Chart(gender_counts).mark_arc(innerRadius=50).encode(
    theta='count:Q',
    color='gender_clean:N',
    tooltip=['gender_clean', 'count']
).properties(width=300, height=300)
st.altair_chart(gender_pie, use_container_width=True)

gender_failure = df.groupby(['gender_clean', 'Failure_Type']).size().reset_index(name='count')
gender_totals = df.groupby('gender_clean').size().reset_index(name='total')
gender_failure = gender_failure.merge(gender_totals, on='gender_clean')
gender_failure['proportion'] = gender_failure['count'] / gender_failure['total']

gender_chart = alt.Chart(gender_failure).mark_bar().encode(
    x='gender_clean:N',
    y='proportion:Q',
    color='Failure_Type:N',
    tooltip=['gender_clean', 'Failure_Type', 'proportion']
).properties(width=500, height=300)
st.altair_chart(gender_chart, use_container_width=True)

frequency_mapping = {
    'Daily': 7, '4-6 times a week': 5, '2-3 times a week': 2.5,
    'Once a week': 1, 'Unknown': 0
}
df['frequency_numeric'] = df['Frequency'].map(frequency_mapping).fillna(0)
usage = df.groupby('gender_clean')['frequency_numeric'].mean().reset_index()
usage_chart = alt.Chart(usage).mark_bar(color='teal').encode(
    x='gender_clean:N',
    y='frequency_numeric:Q',
    tooltip=['gender_clean', 'frequency_numeric']
).properties(title="Avg Usage by Gender", width=400, height=300)
st.altair_chart(usage_chart, use_container_width=True)
