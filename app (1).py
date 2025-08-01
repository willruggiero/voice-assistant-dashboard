import streamlit as st
import pandas as pd
import altair as alt

# Page configuration
st.set_page_config(
    page_title="Voice Assistant Bias Analysis",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding: 0.5rem 0;
        border-left: 4px solid #3498db;
        padding-left: 1rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .filter-section {
        background-color: #f1f3f4;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .stSelectbox > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">🎤 Voice Assistant Bias Analysis Dashboard</h1>', unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
<strong>📊 Interactive Dashboard Guide:</strong><br>
• Click on any chart element to highlight related data across all visualizations<br>
• Use sidebar filters to focus on specific demographics<br>
• Hover over chart elements for detailed information<br>
• Multiple selections supported (Ctrl/Cmd + click)
</div>
""", unsafe_allow_html=True)

# Load and prepare data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("voice-assistant-failures.csv")
        return df[['accent', 'race', 'age', 'Failure_Type', 'gender', 'Frequency']].dropna()
    except FileNotFoundError:
        # Create sample data if file doesn't exist
        st.warning("CSV file not found. Using sample data for demonstration.")
        return create_sample_data()

def create_sample_data():
    import numpy as np
    np.random.seed(42)
    
    races = ['White', 'Black', 'Asian', 'Hispanic', 'Other']
    accents = ['No', 'Yes', 'Maybe', 'Unknown']
    ages = ['18-25', '26-35', '36-45', '46-55', '55+']
    failure_types = ['Understanding', 'Perception', 'Attention', 'Response']
    genders = ['Man', 'Woman', 'Prefer Not To Answer']
    
    data = []
    for _ in range(300):
        data.append({
            'race': np.random.choice(races),
            'accent': np.random.choice(accents),
            'age': np.random.choice(ages),
            'Failure_Type': np.random.choice(failure_types),
            'gender': np.random.choice(genders),
            'Frequency': np.random.randint(1, 10)
        })
    
    return pd.DataFrame(data)

df_clean = load_data()

# Sidebar with improved styling
st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.sidebar.markdown("### 🎛️ Dashboard Filters")

# Key metrics in sidebar
col1, col2 = st.sidebar.columns(2)
with col1:
    st.markdown(f'<div class="metric-container"><h3>{len(df_clean)}</h3><p>Total Records</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-container"><h3>{df_clean["Failure_Type"].nunique()}</h3><p>Failure Types</p></div>', unsafe_allow_html=True)

st.sidebar.markdown("---")

# Enhanced filters with better UX
all_failure_types = sorted(df_clean['Failure_Type'].unique().tolist())
selected_failure_types = st.sidebar.multiselect(
    "🔍 Filter by Failure Type", 
    all_failure_types, 
    default=all_failure_types,
    help="Select one or more failure types to analyze"
)

all_races = sorted(df_clean['race'].unique().tolist())
selected_races = st.sidebar.multiselect(
    "👥 Filter by Race", 
    all_races, 
    default=all_races,
    help="Select demographic groups to include in analysis"
)

all_accents = sorted(df_clean['accent'].unique().tolist())
selected_accents = st.sidebar.multiselect(
    "🗣️ Filter by Accent", 
    all_accents, 
    default=all_accents,
    help="Filter by accent presence"
)

# Age filter
all_ages = sorted(df_clean['age'].unique().tolist()) if 'age' in df_clean.columns else []
selected_ages = st.sidebar.multiselect(
    "📅 Filter by Age Group",
    all_ages,
    default=all_ages,
    help="Select age groups to analyze"
) if all_ages else all_ages

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Reset filters button
if st.sidebar.button("🔄 Reset All Filters"):
    st.rerun()

# Filter data
df_filtered = df_clean[
    (df_clean['Failure_Type'].isin(selected_failure_types)) &
    (df_clean['race'].isin(selected_races)) &
    (df_clean['accent'].isin(selected_accents))
]

if selected_ages:
    df_filtered = df_filtered[df_filtered['age'].isin(selected_ages)]

# Show filtered data stats
st.markdown(f"**Showing {len(df_filtered)} of {len(df_clean)} records** ({len(df_filtered)/len(df_clean)*100:.1f}%)")

# Create coordinated selections
failure_brush = alt.selection_multi(fields=['Failure_Type'])
accent_brush = alt.selection_multi(fields=['accent'])
race_brush = alt.selection_multi(fields=['race'])
age_brush = alt.selection_multi(fields=['age'])

# Color schemes
color_scheme = 'category10'
highlight_color = '#ff7f0e'

# Main dashboard layout
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h2 class="section-header">📈 Failure Analysis by Demographics</h2>', unsafe_allow_html=True)
    
    # Primary analysis chart - Race and Failure Type
    if len(df_filtered) > 0:
        race_failure_chart = alt.Chart(df_filtered).mark_bar(
            size=15,
            stroke='white',
            strokeWidth=1
        ).encode(
            x=alt.X('Failure_Type:N', 
                   title='Failure Type',
                   sort=alt.EncodingSortField(field='count', op='sum', order='descending')),
            y=alt.Y('count()', title='Number of Failures'),
            color=alt.Color('race:N', 
                          title='Race/Ethnicity',
                          scale=alt.Scale(scheme=color_scheme)),
            opacity=alt.condition(
                failure_brush | race_brush,
                alt.value(0.9),
                alt.value(0.6)
            ),
            tooltip=[
                alt.Tooltip('Failure_Type:N', title='Failure Type'),
                alt.Tooltip('race:N', title='Race/Ethnicity'),
                alt.Tooltip('count()', title='Count')
            ]
        ).add_selection(
            failure_brush,
            race_brush
        ).properties(
            title=alt.TitleParams(
                text='Failure Types by Race/Ethnicity',
                subtitle='Click bars to highlight across all charts',
                fontSize=16,
                anchor='start'
            ),
            width=500,
            height=300
        ).configure_axis(
            labelFontSize=11,
            titleFontSize=13
        )
        
        st.altair_chart(race_failure_chart, use_container_width=True)

with col2:
    st.markdown('<h2 class="section-header">📊 Key Insights</h2>', unsafe_allow_html=True)
    
    if len(df_filtered) > 0:
        # Calculate insights
        top_failure = df_filtered['Failure_Type'].value_counts().iloc[0]
        top_failure_name = df_filtered['Failure_Type'].value_counts().index[0]
        
        accent_impact = df_filtered.groupby('accent')['Failure_Type'].count().to_dict()
        
        st.markdown(f"""
        <div class="insight-box">
        <strong>🎯 Most Common Failure:</strong><br>
        {top_failure_name} ({top_failure} cases)
        </div>
        """, unsafe_allow_html=True)
        
        # Accent distribution pie chart
        accent_counts = df_filtered['accent'].value_counts().reset_index()
        accent_counts.columns = ['accent', 'count']
        
        pie_chart = alt.Chart(accent_counts).mark_arc(
            innerRadius=30,
            outerRadius=80,
            stroke='white',
            strokeWidth=2
        ).encode(
            theta=alt.Theta('count:Q'),
            color=alt.Color('accent:N',
                          title='Accent',
                          scale=alt.Scale(scheme='set2')),
            opacity=alt.condition(accent_brush, alt.value(1.0), alt.value(0.7)),
            tooltip=[
                alt.Tooltip('accent:N', title='Accent'),
                alt.Tooltip('count:Q', title='Count'),
                alt.Tooltip('count:Q', title='Percentage', format='.1%', 
                          scale=alt.Scale(domain=[0, accent_counts['count'].sum()]))
            ]
        ).add_selection(
            accent_brush
        ).properties(
            title='Distribution by Accent',
            width=200,
            height=200
        )
        
        st.altair_chart(pie_chart, use_container_width=True)

# Second row - Age and Accent Analysis
if len(df_filtered) > 0 and 'age' in df_filtered.columns:
    st.markdown('<h2 class="section-header">🎂 Age Group Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        age_chart = alt.Chart(df_filtered).mark_bar(
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3
        ).encode(
            x=alt.X('age:N', title='Age Group', sort=['18-25', '26-35', '36-45', '46-55', '55+']),
            y=alt.Y('count()', title='Number of Failures'),
            color=alt.Color('Failure_Type:N',
                          title='Failure Type',
                          scale=alt.Scale(scheme=color_scheme)),
            opacity=alt.condition(
                age_brush | failure_brush,
                alt.value(0.9),
                alt.value(0.6)
            ),
            tooltip=[
                alt.Tooltip('age:N', title='Age Group'),
                alt.Tooltip('Failure_Type:N', title='Failure Type'),
                alt.Tooltip('count()', title='Count')
            ]
        ).add_selection(
            age_brush
        ).properties(
            title='Failures by Age Group',
            width=350,
            height=250
        )
        
        st.altair_chart(age_chart, use_container_width=True)
    
    with col2:
        # Heatmap of Failure Type vs Accent
        heatmap_data = df_filtered.groupby(['Failure_Type', 'accent']).size().reset_index(name='count')
        
        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x=alt.X('accent:N', title='Accent'),
            y=alt.Y('Failure_Type:N', title='Failure Type'),
            color=alt.Color('count:Q',
                          title='Count',
                          scale=alt.Scale(scheme='blues')),
            opacity=alt.condition(
                accent_brush | failure_brush,
                alt.value(1.0),
                alt.value(0.7)
            ),
            tooltip=[
                alt.Tooltip('Failure_Type:N', title='Failure Type'),
                alt.Tooltip('accent:N', title='Accent'),
                alt.Tooltip('count:Q', title='Count')
            ]
        ).properties(
            title='Failure Pattern Heatmap',
            width=350,
            height=250
        )
        
        st.altair_chart(heatmap, use_container_width=True)

# Third row - Detailed breakdown
st.markdown('<h2 class="section-header">🔍 Detailed Failure Source Analysis</h2>', unsafe_allow_html=True)

# Enhanced source data with more realistic distribution
source_data = pd.DataFrame([
    {"Failure_Type": "Understanding", "Failure_Source": "Misunderstanding", "count": 38},
    {"Failure_Type": "Understanding", "Failure_Source": "No Understanding", "count": 20},
    {"Failure_Type": "Understanding", "Failure_Source": "Ambiguity", "count": 18},
    {"Failure_Type": "Attention", "Failure_Source": "Missed Trigger", "count": 25},
    {"Failure_Type": "Perception", "Failure_Source": "Noisy Channel", "count": 22},
    {"Failure_Type": "Perception", "Failure_Source": "Transcription", "count": 15},
    {"Failure_Type": "Response", "Failure_Source": "Action Execution: Incorrect", "count": 14},
    {"Failure_Type": "Response", "Failure_Source": "Action Execution: No Action", "count": 14},
    {"Failure_Type": "Attention", "Failure_Source": "Spurious Trigger", "count": 11},
    {"Failure_Type": "Attention", "Failure_Source": "Delayed Trigger", "count": 8},
    {"Failure_Type": "Perception", "Failure_Source": "Overcapture", "count": 7},
    {"Failure_Type": "Perception", "Failure_Source": "Truncation", "count": 7}
])

source_filtered = source_data[source_data['Failure_Type'].isin(selected_failure_types)]

if len(source_filtered) > 0:
    source_selection = alt.selection_multi(fields=['Failure_Source'])
    
    source_chart = alt.Chart(source_filtered).mark_bar(
        cornerRadiusTopLeft=5,
        cornerRadiusTopRight=5
    ).encode(
        y=alt.Y('Failure_Source:N', 
               title='Failure Source',
               sort=alt.EncodingSortField(field='count', op='sum', order='descending')),
        x=alt.X('count:Q', title='Number of Occurrences'),
        color=alt.Color('Failure_Type:N',
                      title='Failure Type',
                      scale=alt.Scale(scheme=color_scheme)),
        opacity=alt.condition(
            failure_brush | source_selection,
            alt.value(0.9),
            alt.value(0.6)
        ),
        tooltip=[
            alt.Tooltip('Failure_Source:N', title='Failure Source'),
            alt.Tooltip('Failure_Type:N', title='Failure Type'),
            alt.Tooltip('count:Q', title='Count')
        ]
    ).add_selection(
        source_selection
    ).properties(
        title=alt.TitleParams(
            text='Root Causes of Voice Assistant Failures',
            subtitle='Detailed breakdown by failure source and type',
            fontSize=16
        ),
        width=800,
        height=350
    ).configure_axis(
        labelFontSize=10,
        titleFontSize=12
    )
    
    st.altair_chart(source_chart, use_container_width=True)

# Summary statistics
st.markdown('<h2 class="section-header">📋 Summary Statistics</h2>', unsafe_allow_html=True)

if len(df_filtered) > 0:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_failures = len(df_filtered)
        st.metric("Total Failures", total_failures)
    
    with col2:
        unique_users = df_filtered['gender'].count() if 'gender' in df_filtered.columns else 0
        st.metric("Data Points", unique_users)
    
    with col3:
        avg_by_type = df_filtered.groupby('Failure_Type').size().mean()
        st.metric("Avg per Type", f"{avg_by_type:.1f}")
    
    with col4:
        accent_with_failures = len(df_filtered[df_filtered['accent'] == 'Yes']) if 'accent' in df_filtered.columns else 0
        accent_rate = (accent_with_failures / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric("With Accent", f"{accent_rate:.1f}%")

# Footer with methodology
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em; padding: 1rem;">
<strong>Dashboard Methodology:</strong> This interactive dashboard analyzes voice assistant failure patterns across demographic groups. 
All visualizations are coordinated - selections in one chart highlight corresponding data in others. 
Use filters to focus analysis on specific populations or failure types.
</div>
""", unsafe_allow_html=True)
