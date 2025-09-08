import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from traffic_chatbot import render_chatbot_widget

# Set page configuration
st.set_page_config(
    page_title="Road Segment Traffic Analysis",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1rem;
        color: #6c757d;
    }
    .section-header {
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Load the data
@st.cache_data
def load_data():
    data = pd.read_csv('data/road_segment_traffic_clusters.csv')
    return data

# Load the dataset
df = load_data()

# Sidebar for filters with improved styling
st.sidebar.markdown("<h2 style='color: #1f77b4;'>Filters & Controls</h2>", unsafe_allow_html=True)

# Cluster filter
st.sidebar.markdown("**Cluster Selection**")
cluster_options = sorted(df['cluster_id'].unique())
selected_clusters = st.sidebar.multiselect(
    'Select Cluster IDs',
    options=cluster_options,
    default=cluster_options,
    label_visibility="collapsed"
)

# Category filter
st.sidebar.markdown("**Traffic Category**")
category_options = df['category'].unique()
selected_categories = st.sidebar.multiselect(
    'Select Traffic Categories',
    options=category_options,
    default=category_options,
    label_visibility="collapsed"
)

# Segment search
st.sidebar.markdown("**Segment Search**")
segment_search = st.sidebar.text_input(
    'Search for specific segments',
    label_visibility="collapsed"
)

# Traffic range filter
st.sidebar.markdown("**Traffic Range**")
min_traffic, max_traffic = st.sidebar.slider(
    'Select traffic range',
    min_value=float(df['avg_raw_traffic'].min()),
    max_value=float(df['avg_raw_traffic'].max()),
    value=(float(df['avg_raw_traffic'].min()), float(df['avg_raw_traffic'].max())),
    step=0.1
)

# Apply filters
filtered_df = df[
    (df['cluster_id'].isin(selected_clusters)) &
    (df['category'].isin(selected_categories)) &
    (df['avg_raw_traffic'] >= min_traffic) &
    (df['avg_raw_traffic'] <= max_traffic)
]

if segment_search:
    filtered_df = filtered_df[filtered_df['segment'].str.contains(segment_search, case=False)]

# Main content
st.markdown("<h1 class='main-header'>🚦 Road Segment Traffic Analysis Dashboard</h1>", unsafe_allow_html=True)

# Key metrics with improved styling
st.markdown("<h2 class='section-header'>Key Performance Indicators</h2>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='metric-card'><div class='metric-value'>{}</div><div class='metric-label'>Total Segments</div></div>".format(len(df)), unsafe_allow_html=True)
with col2:
    st.markdown("<div class='metric-card'><div class='metric-value'>{}</div><div class='metric-label'>Low Traffic Segments</div></div>".format(len(df[df['category'] == 'Low Traffic'])), unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-card'><div class='metric-value'>{}</div><div class='metric-label'>Medium Traffic Segments</div></div>".format(len(df[df['category'] == 'Medium Traffic'])), unsafe_allow_html=True)
with col4:
    st.markdown("<div class='metric-card'><div class='metric-value'>{}</div><div class='metric-label'>High Traffic Segments</div></div>".format(len(df[df['category'] == 'High Traffic'])), unsafe_allow_html=True)

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Cluster Analysis", "Segment Details", "Geospatial View", "Data Explorer", "AI Assistant"])

with tab1:
    st.markdown("<h2 class='section-header'>Traffic Distribution Overview</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Traffic category distribution with custom colors
        category_counts = df['category'].value_counts()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green
        fig1 = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title='Distribution of Traffic Categories',
            color_discrete_sequence=colors
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Average traffic by category with custom colors
        avg_traffic = df.groupby('category')['avg_raw_traffic'].mean().reset_index()
        fig2 = px.bar(
            avg_traffic,
            x='category',
            y='avg_raw_traffic',
            title='Average Traffic by Category',
            labels={'avg_raw_traffic': 'Average Traffic', 'category': 'Traffic Category'},
            color='category',
            color_discrete_sequence=colors
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Traffic distribution histogram
    st.markdown("<h3 class='section-header'>Traffic Distribution Histogram</h3>", unsafe_allow_html=True)
    fig_hist = px.histogram(
        df, 
        x='avg_raw_traffic', 
        color='category',
        title='Distribution of Traffic Values',
        nbins=20,
        color_discrete_sequence=colors
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    st.markdown("<h2 class='section-header'>Cluster Analysis</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Traffic distribution by cluster
        fig3 = px.box(
            filtered_df,
            x='cluster_id',
            y='avg_raw_traffic',
            color='category',
            title='Traffic Distribution by Cluster',
            labels={'cluster_id': 'Cluster ID', 'avg_raw_traffic': 'Average Traffic'},
            color_discrete_sequence=colors
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Segment count by cluster
        cluster_counts = filtered_df['cluster_id'].value_counts().sort_index()
        fig4 = px.bar(
            x=cluster_counts.index.astype(str),
            y=cluster_counts.values,
            title='Number of Segments by Cluster',
            labels={'x': 'Cluster ID', 'y': 'Number of Segments'},
            color=cluster_counts.index.astype(str),
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig4.update_layout(showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Cluster statistics
    st.markdown("<h3 class='section-header'>Cluster Statistics</h3>", unsafe_allow_html=True)
    cluster_stats = df.groupby('cluster_id').agg({
        'avg_raw_traffic': ['mean', 'min', 'max', 'std'],
        'segment': 'count'
    }).round(2)
    cluster_stats.columns = ['Avg Traffic', 'Min Traffic', 'Max Traffic', 'Std Deviation', 'Segment Count']
    st.dataframe(cluster_stats.style.background_gradient(cmap='Blues'))

with tab3:
    st.markdown("<h2 class='section-header'>Segment Details</h2>", unsafe_allow_html=True)
    
    # Interactive scatter plot
    fig5 = px.scatter(
        filtered_df,
        x='segment',
        y='avg_raw_traffic',
        color='category',
        hover_data=['cluster_id'],
        title='Traffic Levels by Segment',
        labels={'avg_raw_traffic': 'Average Traffic', 'segment': 'Road Segment'},
        color_discrete_sequence=colors
    )
    fig5.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig5, use_container_width=True)
    
    # Top segments by traffic
    st.markdown("<h3 class='section-header'>Top Segments by Traffic Volume</h3>", unsafe_allow_html=True)
    top_n = st.slider("Number of segments to show", 5, 20, 10, key="top_n_slider")
    top_segments = filtered_df.nlargest(top_n, 'avg_raw_traffic')
    
    # Create a horizontal bar chart for top segments
    fig_top = px.bar(
        top_segments,
        y='segment',
        x='avg_raw_traffic',
        color='category',
        orientation='h',
        title=f'Top {top_n} Segments by Traffic Volume',
        labels={'avg_raw_traffic': 'Average Traffic', 'segment': 'Road Segment'},
        color_discrete_sequence=colors
    )
    st.plotly_chart(fig_top, use_container_width=True)

with tab4:
    st.markdown("<h2 class='section-header'>Geospatial View</h2>", unsafe_allow_html=True)
    
    # Create a mock geospatial visualization
    st.info("This is a simulated geospatial view. In a real scenario, you would have actual coordinates for each road segment.")
    
    # Generate mock coordinates for visualization
    np.random.seed(42)
    mock_coords = pd.DataFrame({
        'segment': df['segment'],
        'lat': np.random.uniform(37.7, 37.8, len(df)),
        'lon': np.random.uniform(-122.4, -122.5, len(df)),
        'traffic': df['avg_raw_traffic'],
        'category': df['category']
    })
    
    # Create a map visualization
    fig_map = px.scatter_mapbox(
        mock_coords,
        lat="lat",
        lon="lon",
        hover_name="segment",
        hover_data={"traffic": True, "category": True, "lat": False, "lon": False},
        color="category",
        size="traffic",
        color_discrete_sequence=colors,
        zoom=10,
        height=500,
        title="Simulated Geographic Distribution of Road Segments"
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

with tab5:
    st.markdown("<h2 class='section-header'>Data Explorer</h2>", unsafe_allow_html=True)
    
    # Show filtered data
    st.dataframe(
        filtered_df.style.background_gradient(
            subset=['avg_raw_traffic'], 
            cmap='YlOrRd'
        ),
        use_container_width=True
    )
    
    # Download button for filtered data
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_traffic_data.csv",
        mime="text/csv"
    )

with tab6:
    # AI Assistant / Chatbot
    render_chatbot_widget('data/road_segment_traffic_clusters.csv')

# Add some insights with improved styling
st.markdown("---")
st.markdown("<h2 class='section-header'>Key Insights & Analysis</h2>", unsafe_allow_html=True)

insights_col1, insights_col2 = st.columns(2)

with insights_col1:
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem;'>
        <h3 style='color: #1f77b4;'>Traffic Patterns</h3>
        <ul>
            <li>Cluster 0 consistently shows low traffic across all segments</li>
            <li>Cluster 2 contains segments with the highest traffic volumes</li>
            <li>Medium traffic segments are primarily found in Cluster 1</li>
            <li>Clear separation between clusters based on traffic levels</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with insights_col2:
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem;'>
        <h3 style='color: #1f77b4;'>Notable Observations</h3>
        <ul>
            <li>Segment B1C1 has the highest traffic volume (2.84)</li>
            <li>The categorization aligns well with the cluster assignments</li>
            <li>Traffic distribution follows a clear pattern across segments</li>
            <li>Potential for traffic optimization in high-traffic segments</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6c757d;'>
    <p><strong>Road Segment Traffic Analysis Dashboard</strong> | Created with Streamlit</p>
    <p>Data Source: road_segment_traffic_clusters.csv</p>
</div>
""", unsafe_allow_html=True)