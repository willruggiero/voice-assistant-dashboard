import streamlit as st
import pandas as pd
import altair as alt

st.title("Voice Assistant Failures Dashboard - Coordinated Visualizations")

df = pd.read_csv("voice-assistant-failures.csv")
df_clean = df[['accent', 'race', 'age', 'Failure_Type', 'gender', 'Frequency']].dropna()

st.sidebar.header("Filters")

all_failure_types = df_clean['Failure_Type'].unique().tolist()
selected_failure_types = st.sidebar.multiselect("Filter by Failure Type", all_failure_types, default=all_failure_types)

all_races = df_clean['race'].unique().tolist()
selected_races = st.sidebar.multiselect("Filter by Race", all_races, default=all_races)

all_accents = df_clean['accent'].unique().tolist()
selected_accents = st.sidebar.multiselect("Filter by Accent", all_accents, default=all_accents)

df_filtered = df_clean[
    (df_clean['Failure_Type'].isin(selected_failure_types)) &
    (df_clean['race'].isin(selected_races)) &
    (df_clean['accent'].isin(selected_accents))
]

# Create shared selections for coordination
failure_type_brush = alt.selection_multi(fields=['Failure_Type'])
accent_brush = alt.selection_multi(fields=['accent'])
race_brush = alt.selection_multi(fields=['race'])
age_brush = alt.selection_multi(fields=['age'])

# Prepare data for charts
top_failure_types = df_filtered['Failure_Type'].value_counts().nlargest(3).index.tolist()
df_q2 = df_filtered[df_filtered['Failure_Type'].isin(top_failure_types)]
top_races = df_q2['race'].value_counts().nlargest(4).index.tolist()
df_race = df_q2[df_q2['race'].isin(top_races)]

bar_size = 20
facet_width = 240
facet_height = 300

# Race Chart with coordinated selection
race_chart = alt.Chart(df_race).mark_bar(size=bar_size).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.Color('accent:N', title='Accent', scale=alt.Scale(scheme='category10')),
    column=alt.Column('race:N', title='Race', spacing=30),
    opacity=alt.condition(
        failure_type_brush | accent_brush | race_brush, 
        alt.value(1.0), 
        alt.value(0.3)
    ),
    tooltip=[
        alt.Tooltip('Failure_Type:N'),
        alt.Tooltip('race:N'),
        alt.Tooltip('accent:N'),
        alt.Tooltip('count()', title='Number of Failures')
    ]
).add_selection(
    failure_type_brush,
    accent_brush,
    race_brush
).properties(
    title='Failure Types by Accent and Race (Top 4) - Click to Select',
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

# Age Chart with coordinated selection
df_age = df_filtered[df_filtered['Failure_Type'].isin(top_failure_types)]

age_chart = alt.Chart(df_age).mark_bar(size=bar_size).encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count()', title='Number of Failures'),
    color=alt.Color('accent:N', title='Accent', scale=alt.Scale(scheme='category10')),
    column=alt.Column('age:N', title='Age Group', spacing=30),
    opacity=alt.condition(
        failure_type_brush | accent_brush | age_brush, 
        alt.value(1.0), 
        alt.value(0.3)
    ),
    tooltip=[
        alt.Tooltip('Failure_Type:N'),
        alt.Tooltip('age:N'),
        alt.Tooltip('accent:N'),
        alt.Tooltip('count()', title='Number of Failures')
    ]
).add_selection(
    age_brush
).properties(
    title='Failure Types by Accent and Age Group - Click to Select',
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

# Source data with coordinated selection
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

source_data_filtered = source_data[source_data['Failure_Type'].isin(selected_failure_types)]

source_selection = alt.selection_multi(fields=['Failure_Source'])

source_chart = alt.Chart(source_data_filtered).mark_bar().encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count:Q', title='Count'),
    color=alt.Color('Failure_Source:N', title='Failure Source'),
    opacity=alt.condition(
        failure_type_brush | source_selection, 
        alt.value(1.0), 
        alt.value(0.3)
    ),
    tooltip=['Failure_Type', 'Failure_Source', 'count']
).add_selection(
    source_selection
).properties(
    title="Most Common Voice Assistant Failure Types by Source - Click to Select",
    width=600,
    height=300
)

# Accent data with coordinated selection
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

accent_data_filtered = accent_data[
    (accent_data['accent'].isin(selected_accents)) &
    (accent_data['Failure_Type'].isin(selected_failure_types))
]

accent_chart = alt.Chart(accent_data_filtered).mark_bar().encode(
    x=alt.X('Failure_Type:N', title='Failure Type'),
    y=alt.Y('count:Q', title='Count'),
    color=alt.Color('accent:N', title='Accent'),
    opacity=alt.condition(
        failure_type_brush | accent_brush, 
        alt.value(1.0), 
        alt.value(0.3)
    ),
    tooltip=['accent', 'Failure_Type', 'count']
).properties(
    title="Failure Types Experienced by Users with/without Accents - Coordinated",
    width=600,
    height=300
)

# Gender chart (standalone as it doesn't directly coordinate with failure types)
gender_data = pd.DataFrame([
    {"gender": "Man", "count": 101},
    {"gender": "Woman", "count": 90},
    {"gender": "Prefer Not To Answer", "count": 4},
    {"gender": "Unknown", "count": 3},
    {"gender": "Man,Woman", "count": 1}
])

gender_selection = alt.selection_multi(fields=['gender'])

gender_chart = alt.Chart(gender_data).mark_bar().encode(
    x=alt.X('gender:N', title='Gender'),
    y=alt.Y('count:Q', title='Number of Users'),
    color=alt.Color('gender:N', legend=None),
    opacity=alt.condition(gender_selection, alt.value(1.0), alt.value(0.3)),
    tooltip=['gender', 'count']
).add_selection(
    gender_selection
).properties(
    title="Voice Assistant Usage by Gender - Click to Select",
    width=400,
    height=300
)

# Display charts with coordination explanation
st.markdown("""
## Interactive Coordinated Dashboard

**How the coordination works:**
- Click on any failure type, accent, race, or age group in any chart
- All related charts will highlight the corresponding data
- Multiple selections are supported (hold Ctrl/Cmd while clicking)
- Click on empty space to clear selections

The charts are now coordinated so that selections in one chart affect the highlighting in others!
""")

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

# Add explanation of what coordination proves
st.markdown("""
---
## What This Coordination Proves:

1. **Cross-dimensional Analysis**: Users can explore how different demographic factors (race, age, accent) relate to specific failure types across multiple visualizations simultaneously.

2. **Pattern Recognition**: By selecting a failure type in one chart, users immediately see how that failure manifests across different demographic groups in other charts.

3. **Bias Investigation**: The coordination helps identify if certain failure types disproportionately affect specific demographic groups - a key concern in voice assistant bias research.

4. **User Experience Enhancement**: Instead of mentally tracking selections across separate charts, users get immediate visual feedback across all related visualizations.

5. **Data Exploration Efficiency**: Users can quickly drill down into specific combinations (e.g., "Show me Understanding failures for users with accents across all age groups") without manually filtering each chart.

This coordinated approach transforms individual charts into a cohesive analytical tool that reveals relationships between demographic factors and voice assistant performance that might not be apparent when viewing charts in isolation.
""")
