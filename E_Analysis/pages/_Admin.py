import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from utils.preprocessing import load_and_preprocess_data
from utils.utility_analysis import calculate_region_metrics
from utils.visualization import plot_consumption_trends, plot_anomalies
import plotly.graph_objects as go
import time

# =============================================
# PAGE CONFIGURATION
# =============================================
def set_page_config():
    st.set_page_config(
        page_title="Zambia EnergyTracker Admin Dashboard",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background-color: #f8f9fa;
        max-width: 100%;
        margin: 0;
        padding: 0;
    }
    
    .header {
        text-align: center;
        padding: 1rem 1rem;
        background: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .title {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #666;
        font-size: 1rem;
        font-weight: 300;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-top: 4px solid #3498db;
    }
    
    .section-title {
        color: #2c3e50;
        margin-bottom: 15px;
        font-size: 1.6rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 8px;
    }
    
    .stTabs [role=tablist] {
        gap: 10px;
    }
    
    .stTabs [role=tab] {
        border-radius: 8px 8px 0 0 !important;
        padding: 8px 16px !important;
        background-color: #f8f9fa;
    }
    
    .stTabs [aria-selected=true] {
        background-color: #3498db !important;
        color: white !important;
    }
    
    .info-box {
        background-color: #f0f8ff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #3498db;
    }
    
    .stButton>button:first-child {
        background-color: #3498db !important;
        color: white !important;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:first-child:hover {
        background-color: #2980b9 !important;
        transform: translateY(-2px);
    }
    
    .stMetric {
        border-left: 4px solid #3498db;
        padding-left: 1rem;
    }
    
    .stMetricLabel {
        font-size: 0.9rem;
        color: #666;
    }
    
    .stMetricValue {
        font-size: 1.5rem;
        font-weight: 700;
        color: #2c3e50;
    }
    
    .stMetricDelta {
        font-size: 1rem;
    }
    
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        border-right: 1px solid #eee;
    }
    
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        color: #666;
        font-size: 0.9rem;
        border-top: 1px solid #eee;
    }
    
    .feature-icon {
        color: #3498db;
        font-size: 1.5rem;
        margin-right: 10px;
    }
    
    .logo {
        font-weight: 700;
        font-size: 1.5rem;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================
# AUTHENTICATION
# =============================================
def authenticate():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="header">
            <h1 class="title">Zambia EnergyTracker Admin Portal</h1>
            <p class="subtitle">Administrative dashboard for Zambia energy analytics</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("auth_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                if password == "ZambiaEnergy2024":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect credentials")
        return False
    return True

# =============================================
# DATA LOADING
# =============================================
@st.cache_data
def load_data():
    try:
        with st.spinner("Loading data..."):
            time.sleep(1)  # Simulate loading time
            data = pd.read_csv("data/energy_data.csv")
            data['Timestamp'] = pd.to_datetime(data['Timestamp'])
            
            if data['Energy_Consumption_kWh'].isnull().any():
                data['Energy_Consumption_kWh'].fillna(data['Energy_Consumption_kWh'].mean(), inplace=True)
            
            # Convert costs to Zambian Kwacha (ZMW)
            if 'Cost' in data.columns:
                data['Cost'] = data['Cost'] * 18.5  # Example conversion rate (adjust as needed)
                data.rename(columns={'Cost': 'Cost_ZMW'}, inplace=True)
                
            return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# =============================================
# MAIN DASHBOARD
# =============================================
def show_dashboard():
    set_page_config()
    
    if not authenticate():
        return
    
    # Header with branding
    st.markdown("""
    <div class="header">
        <h1 class="title">Zambia EnergyTracker Analytics Dashboard</h1>
        <p class="subtitle">Monitor and optimize energy consumption patterns in Zambia</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Log Out", type="primary", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    # Load data with loading indicator
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        st.markdown("""
        <div class="loading-container">
            <div class="loading-spinner"></div>
        </div>
        """, unsafe_allow_html=True)
        data = load_data()
    
    loading_placeholder.empty()
    
    if data.empty:
        st.error("Failed to load energy data")
        return
    
    # Sidebar filters - Zambia specific regions
    with st.sidebar:
        st.markdown("### <i class='fas fa-filter feature-icon'></i> Filters", unsafe_allow_html=True)
        regions = ['Lusaka', 'Copperbelt', 'Southern', 'Northern', 'Eastern', 'Western', 'North-Western', 'Luapula', 'Muchinga'] if 'Region' not in data.columns else data['Region'].unique()
        usage_types = ['Residential', 'Commercial', 'Industrial', 'Agricultural', 'Mining'] if 'Usage_Type' not in data.columns else data['Usage_Type'].unique()
        
        selected_region = st.selectbox("Select Region", regions)
        selected_usage = st.selectbox("Select Usage Type", usage_types)
        time_range = st.date_input("Date Range", 
                                 [data['Timestamp'].min().date(), 
                                  data['Timestamp'].max().date()])
    
    # Filter data
    filtered_data = data[
        (data['Region'] == selected_region) &
        (data['Usage_Type'] == selected_usage) &
        (data['Timestamp'].dt.date >= time_range[0]) &
        (data['Timestamp'].dt.date <= time_range[1])
    ]
    
    if filtered_data.empty:
        st.warning("No data available for selected filters")
        return
    
    # Dashboard layout with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Usage Patterns", "Anomalies", "Regional Insights"])
    
    with tab1:
        display_overview(filtered_data)
        st.divider()
        display_trends(filtered_data, selected_region, selected_usage)
    
    with tab2:
        st.markdown("### <i class='fas fa-chart-line feature-icon'></i> Peak Hours Analysis", unsafe_allow_html=True)
        peak_hours_chart = plot_peak_hours(filtered_data)
        if peak_hours_chart:
            st.plotly_chart(peak_hours_chart, use_container_width=True)
        else:
            st.warning("Could not generate peak hours analysis")
        
        st.divider()
        display_clusters(filtered_data)
    
    with tab3:
        display_anomaly_detection(filtered_data)
        st.divider()
        display_recommendations(filtered_data)
    
    with tab4:
        display_regional_analysis()
    
    # Footer with Zambia-specific information
    st.markdown("""
    <div class="footer">
        <p>© 2025 Zambia Energy Consumption Analysis. All rights reserved.</p>
        <p>Support: support@zambiaenergytracker.com | ZESCO Contact: 0211-361000</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================
# IMPROVED DASHBOARD COMPONENTS
# =============================================
def display_overview(data):
    st.markdown("### <i class='fas fa-chart-bar feature-icon'></i> Key Metrics", unsafe_allow_html=True)
    
    daily_data = data.resample('D', on='Timestamp')['Energy_Consumption_kWh'].mean().reset_index()
    weekly_change = calculate_weekly_change(data)
    
    cols = st.columns(4)
    with cols[0]:
        st.metric(
            "Total Consumption", 
            f"{data['Energy_Consumption_kWh'].sum():,.0f} kWh",
            help="Sum of all energy consumption in selected period"
        )
    with cols[1]:
        st.metric(
            "Avg. Daily Use", 
            f"{daily_data['Energy_Consumption_kWh'].mean():,.0f} kWh/day",
            help="Average daily energy consumption"
        )
    with cols[2]:
        st.metric(
            "Peak Demand", 
            f"{data['Energy_Consumption_kWh'].max():,.0f} kWh",
            help="Highest instantaneous power demand"
        )
    with cols[3]:
        delta_color = "inverse" if weekly_change < 0 else "normal"
        st.metric(
            "Weekly Change",
            f"{abs(weekly_change):.1f}% {'↑' if weekly_change >=0 else '↓'}",
            delta=f"{weekly_change:.1f}%",
            delta_color=delta_color,
            help="Change compared to previous week"
        )
    
    # Add cost metrics if available (in ZMW)
    if 'Cost_ZMW' in data.columns:
        st.divider()
        st.markdown("### <i class='fas fa-money-bill-wave feature-icon'></i> Cost Metrics (ZMW)", unsafe_allow_html=True)
        cost_cols = st.columns(3)
        with cost_cols[0]:
            st.metric(
                "Total Cost", 
                f"ZMW {data['Cost_ZMW'].sum():,.2f}",
                help="Total energy cost in Zambian Kwacha"
            )
        with cost_cols[1]:
            st.metric(
                "Avg. Cost per kWh", 
                f"ZMW {data['Cost_ZMW'].sum()/data['Energy_Consumption_kWh'].sum():,.4f}",
                help="Average cost per kilowatt-hour"
            )
        with cost_cols[2]:
            st.metric(
                "Peak Hour Cost", 
                f"ZMW {data['Cost_ZMW'].max():,.2f}",
                help="Highest instantaneous cost"
            )

def display_trends(data, region, usage_type):
    with st.spinner("Generating consumption trends..."):
        st.markdown("### <i class='fas fa-chart-line feature-icon'></i> Consumption Trends", unsafe_allow_html=True)
        
        daily_data = data.resample('D', on='Timestamp')['Energy_Consumption_kWh'].mean().reset_index()
        daily_data['Energy_Consumption_kWh'] = daily_data['Energy_Consumption_kWh'].round(1)
        
        fig = px.area(
            daily_data,
            x='Timestamp',
            y='Energy_Consumption_kWh',
            title=f"Daily Energy Consumption - {region} ({usage_type})",
            labels={'Energy_Consumption_kWh': 'Consumption (kWh)', 'Timestamp': ''},
            color_discrete_sequence=['#3498db']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True, key="trend_chart")
        
        # Export option
        col1, col2 = st.columns([4, 1])
        with col2:
            st.download_button(
                "Export Chart Data",
                daily_data.to_csv(index=False),
                file_name=f"zambia_consumption_trends_{region}_{usage_type}.csv",
                mime="text/csv"
            )

def display_clusters(data):
    with st.spinner("Analyzing customer segments..."):
        st.markdown("### <i class='fas fa-users feature-icon'></i> Customer Segments", unsafe_allow_html=True)
        
        if 'Month' in data.columns:
            monthly_usage = data.groupby(['Meter_ID', 'Month'])['Energy_Consumption_kWh'].mean()
            usage_consistency = monthly_usage.groupby('Meter_ID').std().fillna(0)
            data = data.merge(usage_consistency.rename('Usage_Consistency'), on='Meter_ID')
        else:
            data['Usage_Consistency'] = 0
        
        data['Peak_Ratio'] = data['Energy_Consumption_kWh'] / data['Energy_Consumption_kWh'].max()
        
        # Clustering
        features = data[['Peak_Ratio', 'Usage_Consistency']]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        kmeans = KMeans(n_clusters=3, random_state=42)
        data['Cluster'] = kmeans.fit_predict(scaled_features)
        
        # Simplified visualization
        fig = plot_simplified_clusters(data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Simple explanation with Zambia context
        with st.expander("Understanding Customer Segments"):
            st.markdown("""
            **Segment Explanation for Zambia:**
            
            - **Typical Households (Blue)**:  
              Represent the majority of residential customers with normal, predictable energy usage patterns.
              
            - **Variable Commercial (Orange)**:  
              Businesses with unpredictable usage that fluctuates significantly (e.g., shops, small industries).
              
            - **High Consumers (Red)**:  
              Mining operations and large industries that consistently use more energy than average.
            """)

def display_anomaly_detection(data):
    with st.spinner("Detecting anomalies..."):
        st.markdown("### <i class='fas fa-exclamation-triangle feature-icon'></i> Anomaly Detection", unsafe_allow_html=True)
        
        if data.empty or 'Energy_Consumption_kWh' not in data.columns:
            st.warning("Insufficient data for anomaly detection")
            return
        
        features = data[['Energy_Consumption_kWh']].values
        iso_forest = IsolationForest(contamination=0.05, random_state=42)
        data['Anomaly'] = iso_forest.fit_predict(features)
        anomalies = data[data['Anomaly'] == -1]
        
        cols = st.columns(3)
        cols[0].metric("Total Anomalies", f"{len(anomalies):,}")
        anomaly_rate = (len(anomalies)/len(data)*100) if len(data) > 0 else 0
        cols[1].metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
        cols[2].metric("Highest Anomaly", 
                      f"{anomalies['Energy_Consumption_kWh'].max():,.0f} kWh" if not anomalies.empty else "N/A")
        
        plot_anomalies(data, key="admin_anomalies")
        
        if not anomalies.empty:
            st.markdown("#### Anomaly Details")
            top_anomalies = anomalies.nlargest(5, 'Energy_Consumption_kWh')
            st.dataframe(
                top_anomalies[['Timestamp', 'Meter_ID', 'Energy_Consumption_kWh', 'Region']]
                .style.format({'Energy_Consumption_kWh': '{:,.0f} kWh'})
            )

def display_regional_analysis():
    with st.spinner("Loading regional data..."):
        st.markdown("### <i class='fas fa-globe feature-icon'></i> Zambia Regional Comparison", unsafe_allow_html=True)
        st.markdown("""
        <div class='info-box'>
        Compare energy usage patterns across Zambia's regions to identify:
        - Areas with highest demand (e.g., Copperbelt, Lusaka)
        - Regions needing infrastructure upgrades
        - Opportunities for targeted energy programs
        </div>
        """, unsafe_allow_html=True)
        
        try:
            data = load_and_preprocess_data()
            
            if isinstance(data, tuple):
                data = data[0]
                
            if not isinstance(data, pd.DataFrame) or data.empty:
                st.warning("No regional data available")
                return
                
            plot_consumption_trends(data)
            
            region_metrics = calculate_region_metrics(data)
            
            if not region_metrics.empty:
                st.markdown("#### Regional Statistics")
                
                max_region = region_metrics['Total_Consumption'].idxmax()
                min_region = region_metrics['Total_Consumption'].idxmin()
                variance = region_metrics['Total_Consumption'].max()/region_metrics['Total_Consumption'].min()
                
                cols = st.columns(3)
                cols[0].metric("Highest Consumption", max_region)
                cols[1].metric("Lowest Consumption", min_region)
                cols[2].metric("Variance Between Regions", f"{variance:.1f}x")
                
                st.dataframe(
                    region_metrics.style
                    .background_gradient(subset=['Total_Consumption'], cmap='Blues')
                    .format({'Total_Consumption': '{:,.0f} kWh'})
                    .set_caption("Detailed regional metrics for Zambia")
                )
                
                with st.expander("Regional Insights for Zambia"):
                    st.markdown(f"""
                    **Key Observations:**
                    - **{max_region}** has the highest energy demand (likely due to mining/industrial activity)
                    - **{min_region}** has the lowest consumption (possibly rural areas)
                    - The difference between highest and lowest regions is **{variance:.1f}x**
                    
                    **Recommendations for ZESCO:**
                    - Investigate high-demand causes in {max_region}
                    - Check for underserved needs in {min_region}
                    - Consider regional demand when planning infrastructure
                    - Focus on rural electrification programs for low-consumption regions
                    """)
            else:
                st.warning("No regional metrics calculated")
                
        except Exception as e:
            st.error(f"Error in regional analysis: {str(e)}")

def display_recommendations(data):
    st.markdown("### <i class='fas fa-lightbulb feature-icon'></i> Optimization Insights for Zambia", unsafe_allow_html=True)
    
    avg_consumption = data['Energy_Consumption_kWh'].mean()
    peak_consumption = data['Energy_Consumption_kWh'].max()
    
    st.markdown(f"""
    **Consumption Analysis:**
    - Average daily use: **{avg_consumption:,.0f} kWh**
    - Peak demand: **{peak_consumption:,.0f} kWh** ({peak_consumption/avg_consumption:.1f}x average)
    """)
    
    with st.expander("Recommended Actions for Zambia"):
        st.markdown("""
        - **Peak Demand Management**:
          - Implement time-of-use pricing specific to Zambia's consumption patterns
          - Encourage load shifting for mining operations and large industries
          
        - **Energy Efficiency**:
          - Target audits for high-consumption customers (mining, manufacturing)
          - Promote energy-saving technologies suitable for Zambia's climate
          
        - **Infrastructure Planning**:
          - Identify areas needing capacity upgrades (especially Copperbelt and Lusaka)
          - Plan maintenance during low-demand periods
          - Expand rural electrification programs
          
        - **Renewable Energy Integration**:
          - Increase solar energy utilization given Zambia's high solar potential
          - Explore mini-grid solutions for remote areas
        """)

def plot_peak_hours(data):
    if 'Timestamp' not in data.columns:
        return None
    
    data['Hour'] = data['Timestamp'].dt.hour
    hourly_data = data.groupby('Hour')['Energy_Consumption_kWh'].mean().reset_index()
    hourly_data['Energy_Consumption_kWh'] = hourly_data['Energy_Consumption_kWh'].round(1)
    
    fig = px.bar(
        hourly_data,
        x='Hour',
        y='Energy_Consumption_kWh',
        title="Average Consumption by Hour (kWh) - Zambia",
        labels={'Energy_Consumption_kWh': 'Consumption (kWh)', 'Hour': 'Hour of Day'},
        color='Energy_Consumption_kWh',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear', dtick=1),
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        uniformtext_minsize=8,
        uniformtext_mode='hide'
    )
    return fig

def plot_simplified_clusters(data):
    if 'Cluster' not in data.columns:
        return None
    
    cluster_counts = data['Cluster'].value_counts().reset_index()
    cluster_counts.columns = ['Cluster', 'Count']
    cluster_counts['Percentage'] = (cluster_counts['Count'] / cluster_counts['Count'].sum() * 100).round(1)
    
    cluster_names = {
        0: 'Typical Households',
        1: 'Variable Commercial',
        2: 'Mining/Industries'
    }
    
    cluster_counts['Segment'] = cluster_counts['Cluster'].map(cluster_names)
    cluster_counts['Label'] = cluster_counts['Segment'] + ' (' + cluster_counts['Percentage'].astype(str) + '%)'
    
    fig = px.pie(
        cluster_counts,
        names='Label',
        values='Count',
        title="Zambia Customer Segmentation",
        color='Segment',
        color_discrete_sequence=['#3498db', '#e67e22', '#e74c3c']
    )
    fig.update_traces(textposition='inside', textinfo='label')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', showlegend=False)
    return fig

def calculate_weekly_change(data):
    if len(data) < 1:
        return 0.0
    
    if not pd.api.types.is_datetime64_any_dtype(data['Timestamp']):
        data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    
    daily_data = data.resample('D', on='Timestamp')['Energy_Consumption_kWh'].mean().reset_index()
    
    if len(daily_data) < 14:
        return 0.0
    
    current_week = daily_data['Energy_Consumption_kWh'].iloc[-7:].mean()
    prev_week = daily_data['Energy_Consumption_kWh'].iloc[-14:-7].mean()
    
    if prev_week == 0:
        return 0.0
    
    return ((current_week - prev_week) / prev_week) * 100

if __name__ == "__main__":
    show_dashboard()