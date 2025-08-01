import pandas as pd
import altair as alt
import numpy as np
from io import StringIO

# Enable Altair to render in Jupyter
alt.data_transformers.enable('json')

# Load and clean the data
def load_and_clean_data():
    """Load and preprocess the voice assistant failures dataset"""
    
    # Read the CSV data
    df = pd.read_csv('voice-assistant-failures.csv')
    
    # Clean and standardize the data
    df['Failure_Type'] = df['Failure_Type'].fillna('Unknown')
    df['Failure_Source'] = df['Failure_Source'].fillna('Unknown')
    df['gender'] = df['gender'].fillna('Unknown')
    df['age'] = df['age'].fillna('Unknown')
    df['race'] = df['race'].fillna('Unknown')
    df['accent'] = df['accent'].fillna('Unknown')
    
    # Standardize gender values
    gender_mapping = {
        'Woman': 'Woman',
        'Man': 'Man', 
        'Man,Woman': 'Non-binary/Other',
        'Prefer not to answer': 'Prefer not to answer'
    }
    df['gender_clean'] = df['gender'].map(gender_mapping).fillna(df['gender'])
    
    # Clean accent column
    df['has_accent'] = df['accent'].map({
        'Yes': 'Yes',
        'No': 'No',
        'Maybe': 'Maybe',
        'Unknown': 'Unknown'
    }).fillna('Unknown')
    
    # Clean age groups
    age_order = ['18-24', '25-34', '35-44', '45-54', '55-64', 'Prefer not to answer', 'Unknown']
    df['age_clean'] = df['age'].apply(lambda x: x if x in age_order else 'Unknown')
    
    return df

# Question 1: Most common failure types and their sources (with coordinated views)
def create_failure_analysis_charts(df):
    """Create charts analyzing failure types and sources with coordinated interactions"""
    
    # Create shared selections for coordinated views
    failure_type_selection = alt.selection_single(fields=['Failure_Type'], name='failure_type_brush')
    failure_source_selection = alt.selection_single(fields=['Failure_Source'], name='failure_source_brush')
    
    # Chart 1a: Overall failure type distribution with selection
    failure_counts = df.groupby('Failure_Type').size().reset_index(name='count')
    
    failure_type_chart = alt.Chart(failure_counts).mark_bar(color='steelblue').add_selection(
        failure_type_selection
    ).encode(
        x=alt.X('count:Q', title='Number of Failures'),
        y=alt.Y('Failure_Type:N', sort='-x', title='Failure Type'),
        tooltip=['Failure_Type:N', 'count:Q'],
        opacity=alt.condition(failure_type_selection, alt.value(0.9), alt.value(0.6)),
        stroke=alt.condition(failure_type_selection, alt.value('black'), alt.value(None)),
        strokeWidth=alt.condition(failure_type_selection, alt.value(2), alt.value(0))
    ).properties(
        title="Distribution of Voice Assistant Failure Types (Click to Filter)",
        width=400,
        height=200
    )
    
    # Chart 1b: Failure source distribution with selection
    source_counts = df.groupby('Failure_Source').size().reset_index(name='count')
    
    failure_source_chart = alt.Chart(source_counts).mark_bar(color='orange').add_selection(
        failure_source_selection
    ).encode(
        x=alt.X('count:Q', title='Number of Failures'),
        y=alt.Y('Failure_Source:N', sort='-x', title='Failure Source'),
        tooltip=['Failure_Source:N', 'count:Q'],
        opacity=alt.condition(failure_source_selection, alt.value(0.9), alt.value(0.6)),
        stroke=alt.condition(failure_source_selection, alt.value('black'), alt.value(None)),
        strokeWidth=alt.condition(failure_source_selection, alt.value(2), alt.value(0))
    ).properties(
        title="Distribution of Failure Sources (Click to Filter)",
        width=400,
        height=250
    )
    
    # Chart 1c: Interactive heatmap that responds to selections from above charts
    failure_heatmap_data = df.groupby(['Failure_Type', 'Failure_Source']).size().reset_index(name='count')
    
    heatmap = alt.Chart(failure_heatmap_data).mark_rect().add_selection(
        failure_type_selection,
        failure_source_selection
    ).encode(
        x=alt.X('Failure_Source:N', title='Failure Source'),
        y=alt.Y('Failure_Type:N', title='Failure Type'),
        color=alt.Color('count:Q', 
                       scale=alt.Scale(scheme='blues'),
                       title='Count'),
        opacity=alt.condition(
            failure_type_selection | failure_source_selection,
            alt.value(1.0),
            alt.value(0.7)
        ),
        stroke=alt.condition(
            failure_type_selection | failure_source_selection,
            alt.value('black'),
            alt.value(None)
        ),
        strokeWidth=alt.condition(
            failure_type_selection | failure_source_selection,
            alt.value(2),
            alt.value(0)
        ),
        tooltip=['Failure_Type:N', 'Failure_Source:N', 'count:Q']
    ).properties(
        title="Failure Type vs Source Relationship (Responds to Selections Above)",
        width=500,
        height=200
    )
    
    # Coordinated demographic breakdown chart
    demo_breakdown = alt.Chart(df).mark_circle(size=60).add_selection(
        failure_type_selection,
        failure_source_selection
    ).encode(
        x=alt.X('gender_clean:N', title='Gender'),
        y=alt.Y('has_accent:N', title='Has Accent'),
        color=alt.Color('Failure_Type:N', title='Failure Type'),
        size=alt.Size('count():Q', title='Count', scale=alt.Scale(range=[50, 200])),
        opacity=alt.condition(
            failure_type_selection | failure_source_selection,
            alt.value(0.9),
            alt.value(0.4)
        ),
        tooltip=['gender_clean:N', 'has_accent:N', 'Failure_Type:N', 'count():Q']
    ).properties(
        title="Demographics Breakdown (Filtered by Selections)",
        width=300,
        height=150
    )
    
    return failure_type_chart, failure_source_chart, heatmap, demo_breakdown

# Question 2a: Accent and failure types (with coordinated brush selection)
def create_accent_failure_analysis(df):
    """Analyze relationship between accent and failure types with coordinated interactions"""
    
    # Filter out unknown accent data for cleaner analysis
    df_accent = df[df['has_accent'] != 'Unknown'].copy()
    
    # Create brush selection for coordinated views
    accent_brush = alt.selection_interval(name='accent_brush')
    
    # Calculate proportions for each accent group
    accent_failure_data = df_accent.groupby(['has_accent', 'Failure_Type']).size().reset_index(name='count')
    accent_totals = df_accent.groupby('has_accent').size().reset_index(name='total')
    accent_failure_data = accent_failure_data.merge(accent_totals, on='has_accent')
    accent_failure_data['proportion'] = accent_failure_data['count'] / accent_failure_data['total']
    
    # Stacked bar chart showing failure types by accent perception with brush selection
    accent_chart = alt.Chart(accent_failure_data).mark_bar().add_selection(
        accent_brush
    ).encode(
        x=alt.X('has_accent:N', title='Self-Perceived Accent'),
        y=alt.Y('proportion:Q', title='Proportion of Failures', scale=alt.Scale(domain=[0, 1])),
        color=alt.Color('Failure_Type:N', 
                       scale=alt.Scale(scheme='category10'),
                       title='Failure Type'),
        opacity=alt.condition(accent_brush, alt.value(0.9), alt.value(0.6)),
        tooltip=['has_accent:N', 'Failure_Type:N', 'count:Q', 'proportion:Q']
    ).properties(
        title="Failure Types by Accent Status (Brush to Filter Details)",
        width=400,
        height=300
    )
    
    # Detailed scatter plot that responds to brush selection
    accent_detail = alt.Chart(df_accent).mark_circle(size=80).add_selection(
        accent_brush
    ).encode(
        x=alt.X('age_clean:N', title='Age Group', sort=['18-24', '25-34', '35-44', '45-54', '55-64']),
        y=alt.Y('Failure_freq:N', title='Failure Frequency'),
        color=alt.Color('Failure_Type:N', title='Failure Type'),
        column=alt.Column('has_accent:N', title='Has Accent'),
        opacity=alt.condition(accent_brush, alt.value(0.9), alt.value(0.3)),
        tooltip=['has_accent:N', 'age_clean:N', 'Failure_Type:N', 'Failure_freq:N']
    ).properties(
        title="Detailed View: Age vs Failure Frequency (Filtered by Brush)",
        width=120,
        height=200
    )
    
    return accent_chart, accent_detail

# Question 2b: Race, age, accent and failures
def create_demographic_analysis(df):
    """Analyze failures by demographic characteristics"""
    
    # Clean race data for better visualization
    df_demo = df.copy()
    df_demo['race_clean'] = df_demo['race'].apply(lambda x: 'Multi/Other' if ',' in str(x) else x)
    
    # Race and accent analysis
    race_accent_data = df_demo.groupby(['race_clean', 'has_accent', 'Failure_Type']).size().reset_index(name='count')
    
    race_chart = alt.Chart(race_accent_data).mark_circle(size=100).encode(
        x=alt.X('race_clean:N', title='Race/Ethnicity'),
        y=alt.Y('Failure_Type:N', title='Failure Type'),
        size=alt.Size('count:Q', title='Count', scale=alt.Scale(range=[50, 400])),
        color=alt.Color('has_accent:N', title='Has Accent'),
        tooltip=['race_clean:N', 'Failure_Type:N', 'has_accent:N', 'count:Q']
    ).properties(
        title="Failures by Race and Accent Status",
        width=600,
        height=300
    )
    
    # Age group analysis
    age_accent_data = df_demo[df_demo['age_clean'] != 'Unknown'].groupby(['age_clean', 'has_accent', 'Failure_Type']).size().reset_index(name='count')
    
    age_chart = alt.Chart(age_accent_data).mark_bar().encode(
        x=alt.X('age_clean:N', title='Age Group', sort=['18-24', '25-34', '35-44', '45-54', '55-64']),
        y=alt.Y('count:Q', title='Count'),
        color=alt.Color('Failure_Type:N', title='Failure Type'),
        column=alt.Column('has_accent:N', title='Has Accent'),
        tooltip=['age_clean:N', 'has_accent:N', 'Failure_Type:N', 'count:Q']
    ).properties(
        title="Failures by Age Group and Accent",
        width=150,
        height=200
    )
    
    return race_chart, age_chart

# Question 3: Gender analysis
def create_gender_analysis(df):
    """Analyze gender patterns in voice assistant usage and failures"""
    
    # Gender distribution of users
    gender_dist = df.groupby('gender_clean').size().reset_index(name='count')
    
    gender_pie = alt.Chart(gender_dist).mark_arc(innerRadius=50).encode(
        theta=alt.Theta('count:Q'),
        color=alt.Color('gender_clean:N', title='Gender'),
        tooltip=['gender_clean:N', 'count:Q']
    ).properties(
        title="Gender Distribution of Users",
        width=200,
        height=200
    )
    
    # Failure types by gender
    gender_failure_data = df.groupby(['gender_clean', 'Failure_Type']).size().reset_index(name='count')
    gender_totals = df.groupby('gender_clean').size().reset_index(name='total')
    gender_failure_data = gender_failure_data.merge(gender_totals, on='gender_clean')
    gender_failure_data['proportion'] = gender_failure_data['count'] / gender_failure_data['total']
    
    gender_failure_chart = alt.Chart(gender_failure_data).mark_bar().encode(
        x=alt.X('gender_clean:N', title='Gender'),
        y=alt.Y('proportion:Q', title='Proportion of Failures'),
        color=alt.Color('Failure_Type:N', title='Failure Type'),
        tooltip=['gender_clean:N', 'Failure_Type:N', 'proportion:Q']
    ).properties(
        title="Failure Type Proportions by Gender",
        width=400,
        height=300
    )
    
    # Usage frequency by gender
    frequency_mapping = {
        'Daily': 7,
        '4-6 times a week': 5,
        '2-3 times a week': 2.5,
        'Once a week': 1,
        'Unknown': 0
    }
    
    df_freq = df.copy()
    df_freq['frequency_numeric'] = df_freq['Frequency'].map(frequency_mapping).fillna(0)
    
    gender_usage = df_freq.groupby('gender_clean')['frequency_numeric'].mean().reset_index()
    
    usage_chart = alt.Chart(gender_usage).mark_bar(color='teal').encode(
        x=alt.X('gender_clean:N', title='Gender'),
        y=alt.Y('frequency_numeric:Q', title='Average Usage Frequency (times/week)'),
        tooltip=['gender_clean:N', 'frequency_numeric:Q']
    ).properties(
        title="Average Usage Frequency by Gender",
        width=300,
        height=200
    )
    
    return gender_pie, gender_failure_chart, usage_chart

# Create comprehensive dashboard
def create_dashboard():
    """Create the complete interactive dashboard"""
    
    # Load data
    df = load_and_clean_data()
    
    # Create all charts
    failure_type_chart, failure_source_chart, heatmap, demo_breakdown = create_failure_analysis_charts(df)
    accent_chart, accent_detail = create_accent_failure_analysis(df)
    race_chart, age_chart = create_demographic_analysis(df)
    gender_pie, gender_failure_chart, usage_chart = create_gender_analysis(df)
    
    # Combine charts into dashboard sections with coordinated views
    
    # Section 1: Overall failure analysis with coordinated filtering
    section1_top = alt.hconcat(
        failure_type_chart,
        failure_source_chart
    ).resolve_scale(color='independent')
    
    section1_bottom = alt.hconcat(
        heatmap,
        demo_breakdown
    ).resolve_scale(color='independent')
    
    section1_with_coordination = alt.vconcat(
        section1_top,
        section1_bottom
    )
    
    # Section 2: Accent analysis with brush coordination
    section2 = alt.vconcat(
        accent_chart,
        accent_detail
    ).resolve_scale(color='independent')
    
    # Section 3: Demographic analysis
    section3 = alt.vconcat(
        race_chart,
        age_chart
    ).resolve_scale(color='independent')
    
    # Section 4: Gender analysis
    section4 = alt.hconcat(
        gender_pie,
        alt.vconcat(gender_failure_chart, usage_chart)
    ).resolve_scale(color='independent')
    
    # Create final dashboard with coordinated interactions
    dashboard = alt.vconcat(
        alt.hconcat(
            alt.vconcat(
                section1_with_coordination
            ).properties(title="Question 1: Failure Types and Sources (Interactive Filtering)"),
            alt.vconcat(
                section2
            ).properties(title="Question 2a: Accent and Failures (Brush Selection)")
        ),
        alt.hconcat(
            alt.vconcat(
                section3
            ).properties(title="Question 2b: Demographics and Failures"),
            alt.vconcat(
                section4
            ).properties(title="Question 3: Gender Analysis")
        )
    ).resolve_scale(
        color='independent'
    ).properties(
        title=alt.TitleParams(
            text="Voice Assistant Failures Analysis Dashboard - Interactive Coordinated Views",
            fontSize=16,
            anchor='start'
        )
    )
    
    return dashboard

# Usage example and summary statistics
def generate_summary_statistics():
    """Generate key insights and statistics"""
    
    df = load_and_clean_data()
    
    print("=== VOICE ASSISTANT FAILURES ANALYSIS ===\n")
    
    print("Dataset Overview:")
    print(f"Total failures recorded: {len(df)}")
    print(f"Unique users: {df['PID'].nunique()}")
    print(f"Date range: {df.shape[0]} entries\n")
    
    print("Question 1 - Most Common Failures:")
    failure_counts = df['Failure_Type'].value_counts()
    print(failure_counts.head())
    print(f"\nMost common failure source: {df['Failure_Source'].value_counts().index[0]}")
    
    print("\nQuestion 2a - Accent Impact:")
    accent_stats = df[df['has_accent'] != 'Unknown'].groupby('has_accent')['Failure_Type'].value_counts(normalize=True).unstack(fill_value=0)
    print("Failure type proportions by accent status:")
    print(accent_stats)
    
    print("\nQuestion 3 - Gender Analysis:")
    gender_counts = df['gender_clean'].value_counts()
    print("User distribution by gender:")
    print(gender_counts)
    
    return df

# Main execution
if __name__ == "__main__":
    # Generate summary statistics
    df = generate_summary_statistics()
    
    # Create and display dashboard
    dashboard = create_dashboard()
    
    # Save dashboard
    dashboard.save('voice_assistant_failures_dashboard.html')
    
    print("\n=== DASHBOARD CREATED ===")
    print("Interactive dashboard saved as 'voice_assistant_failures_dashboard.html'")
    print("Open this file in a web browser to view the interactive visualizations.")
    
    # Display dashboard (in Jupyter notebook)
    dashboard.show()
