# 🏭_Industrial.py
import streamlit as st
import pandas as pd
import plotly.express as px
import time
from utils.preprocessing import load_and_preprocess_data
from utils.visualization import plot_consumption_trends, plot_daily_pattern, plot_anomalies, plot_geospatial
from utils.analysis import calculate_carbon, detect_anomalies, get_benchmarks, predict_consumption
from utils.streaming import StreamManager

# Initialize stream manager
stream_manager = StreamManager()

# =============================================
# PAGE CONFIGURATION
# =============================================
def set_page_config():
    st.set_page_config(
        page_title="Zambia Industrial Energy Dashboard | ",
        page_icon="🏭",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# =============================================
# CUSTOM STYLES
# =============================================
def set_custom_styles():
    st.markdown("""
    <style>
        /* Main colors */
        :root {
            --primary-color: #3498db;
            --secondary-color: #2c3e50;
            --accent-color: #e74c3c;
            --light-color: #f8f9fa;
            --dark-color: #333333;
        }
        
        /* Main padding adjustment */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        
        /* Consistent spacing between sections */
        .stContainer {
            margin-bottom: 1.5rem;
        }
        
        /* Header styles */
        .stApp header {
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Button styles */
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #2980b9;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        /* Metric cards */
        .stMetric {
            border-left: 4px solid var(--primary-color);
            padding-left: 1rem;
        }
        
        /* Tab styles */
        .stTabs [role="tablist"] {
            border-bottom: 2px solid var(--primary-color);
        }
        
        .stTabs [aria-selected="true"] {
            color: var(--primary-color) !important;
            font-weight: 600;
        }
        
        /* Loading spinner */
        .stSpinner>div>div {
            border-color: var(--primary-color) transparent transparent transparent !important;
        }
        
        /* Footer styles */
        footer {
            background-color: var(--dark-color);
            color: white;
            padding: 1rem 0;
            margin-top: 3rem;
        }
        
        /* Custom header */
        .custom-header {
            display: flex;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid #eee;
            margin-bottom: 2rem;
        }
        
        .custom-header h1 {
            color: var(--secondary-color);
            margin-bottom: 0;
        }
        
        /* Info boxes */
        .info-box {
            background-color: #f0f8ff;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid var(--primary-color);
        }
        
        /* Feature icons */
        .feature-icon {
            color: var(--primary-color);
            margin-right: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# =============================================
# LOADING MECHANISM
# =============================================
def loading_spinner(text="Loading..."):
    with st.spinner(text):
        time.sleep(0.5)

# =============================================
# INITIALIZE SESSION STATE
# =============================================
def initialize_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'meter_id' not in st.session_state:
        st.session_state.meter_id = None
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'Facility_Name': 'Not Available',
            'Facility_Address': 'Not Available',
            'Region': 'Not Available',
            'Contact_Number': 'Not Available',
            'Contact_Email': 'Not Available',
            'Tariff_Plan': 'Not Available',
            'Industry_Type': 'Not Available',
            'Production_Capacity': 'Not Available'
        }

# =============================================
# AUTHENTICATION
# =============================================
def authenticate_user():
    if not st.session_state.authenticated:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://www.zesco.co.zm/wp-content/uploads/2020/09/cropped-zesco-logo-32x32.png", width=80)
        with col2:
            st.title("Industrial Energy Dashboard")
            st.markdown("Monitor and optimize your industrial energy consumption with us", unsafe_allow_html=True)
        
        with st.container():
            st.subheader("Sign In")
            st.write("Enter your industrial meter ID to access your facility dashboard")
            
            with st.form("auth_form"):
                meter_id = st.text_input("Meter ID:", 
                                       placeholder="e.g. IND-00340",
                                       max_chars=15).strip().upper()
                
                if st.form_submit_button("Access My Dashboard"):
                    loading_spinner("Verifying your meter ID...")
                    try:
                        data, _ = load_and_preprocess_data()
                        
                        if 'Meter_ID' not in data.columns:
                            st.error("Meter ID system not configured in dataset")
                            return
                        
                        if meter_id in data['Meter_ID'].values:
                            user_row = data[data['Meter_ID'] == meter_id].iloc[0]
                            if user_row.get('Usage_Type', '').lower() != 'industrial':
                                st.error("This meter ID is not registered for industrial use. Please access the appropriate portal.")
                                return
                            
                            st.session_state.meter_id = meter_id
                            st.session_state.user_data = data[data['Meter_ID'] == meter_id]
                            
                            profile_cols = ['Facility_Name', 'Facility_Address', 'Contact_Number', 
                                          'Industry_Type', 'Tariff_Plan', 'Contact_Email',
                                          'Region', 'Production_Capacity']
                            profile_data = {col: user_row[col] if col in user_row else "Not Available" 
                                          for col in profile_cols}
                            st.session_state.user_profile = profile_data
                            
                            st.session_state.authenticated = True
                            st.rerun()
                        else:
                            st.error("Invalid Meter ID. Please check your entry.")
                    except Exception as e:
                        st.error(f"Error loading data: {str(e)}")
            
            st.caption("Don't know your meter ID? Contact ZESCO Industrial Support at 0211-361000")

# =============================================
# FACILITY PROFILE SECTION
# =============================================
def display_facility_profile(profile):
    with st.container():
        st.markdown("""
        <div class="custom-header">
            <h1>Zambia Industrial Energy Dashboard</h1>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([4, 1])
        with cols[0]:
            st.subheader(f"🏭 {profile.get('Facility_Name', 'My Facility')}")
        with cols[1]:
            if st.button("Sign Out"):
                st.session_state.authenticated = False
                st.session_state.user_data = None
                st.session_state.meter_id = None
                st.rerun()
        
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**📍 Address**")
            st.info(profile.get('Facility_Address', 'Not Available'))
            
            st.markdown("**🏘️ Region**")
            st.info(profile.get('Region', 'Not Available'))
            
            st.markdown("**📞 Contact**")
            st.info(profile.get('Contact_Number', 'Not Available'))
        
        with cols[1]:
            st.markdown("**🏭 Industry Type**")
            st.info(profile.get('Industry_Type', 'Not Available'))
            
            st.markdown("**📦 Production Capacity**")
            st.info(f"{profile.get('Production_Capacity', 'Not Available')} units")
            
            st.markdown("**💳 Tariff Plan**")
            st.info(profile.get('Tariff_Plan', 'Not Available'))

# =============================================
# KEY METRICS SECTION
# =============================================
def display_key_metrics(user_data):
    if user_data is None or 'Energy_Consumption_kWh' not in user_data.columns:
        st.warning("Energy consumption data not available")
        return
    
    current_usage = user_data['Energy_Consumption_kWh'].iloc[-1] if len(user_data) > 0 else 0
    avg_usage = user_data['Energy_Consumption_kWh'].mean() if len(user_data) > 0 else 0
    # Zambia industrial electricity rate ~ ZMW 1.20 per kWh
    cost_estimate = avg_usage * 30 * 1.20  # Industrial rate in ZMW
    
    cols = st.columns(3)
    with cols[0]:
        st.metric(label="Current Usage", value=f"{current_usage:.1f} kWh", delta="Today", delta_color="off")
    with cols[1]:
        st.metric(label="Daily Average", value=f"{avg_usage:.1f} kWh", delta_color="off")
    with cols[2]:
        st.metric(label="Estimated Monthly Cost", value=f"ZMW {cost_estimate:,.2f}", delta_color="off")

# =============================================
# CONSUMPTION ANALYSIS
# =============================================
def display_consumption_analysis(user_data):
    if user_data is None or 'Energy_Consumption_kWh' not in user_data.columns:
        st.warning("Energy consumption data not available")
        return
        
    st.subheader("📈 Your Facility Energy Patterns")
    
    tab1, tab2 = st.tabs(["Daily Trends", "Hourly Patterns"])
    
    with tab1:
        st.write("### Your Daily Energy Use")
        with st.spinner("Generating daily trends..."):
            try:
                fig1 = plot_consumption_trends(user_data)
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.warning("Could not generate consumption trends")
            except Exception as e:
                st.error(f"Error displaying consumption trends: {str(e)}")
        
        with st.expander("Understanding Your Daily Use"):
            st.write("This chart shows how much energy your facility uses each day:")
            st.write("- **Production days**: Higher energy usage (typical for Zambia's mining operations)")
            st.write("- **Non-production days**: Lower usage patterns")
            st.write("- **Unexpected spikes**: May indicate equipment issues or power factor problems")
    
    with tab2:
        if 'Timestamp' in user_data.columns:
            st.write("### When You Use Energy During the Day")
            with st.spinner("Analyzing hourly patterns..."):
                try:
                    fig2 = plot_daily_pattern(user_data)
                    if fig2:
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.warning("Could not generate hourly patterns")
                except Exception as e:
                    st.error(f"Error displaying hourly patterns: {str(e)}")
            
            with st.expander("Peak Usage Times"):
                st.write("This shows when your facility uses the most energy:")
                st.write("- **Shift changes**: Equipment startup/shutdown (common in Zambia's mining sector)")
                st.write("- **Peak production**: Highest energy demand (typically 8AM-4PM in Zambia)")
                st.write("- **Maintenance periods**: Potential for energy savings during off-peak hours")
        else:
            st.warning("Timestamp data not available for hourly analysis")

# =============================================
# SAVINGS RECOMMENDATIONS
# =============================================
def display_savings_recommendations(user_data):
    if user_data is None or 'Energy_Consumption_kWh' not in user_data.columns:
        st.warning("Energy consumption data not available")
        return
        
    avg_consumption = user_data['Energy_Consumption_kWh'].mean() if len(user_data) > 0 else 0
    # Zambia industrial electricity rate ~ ZMW 1.20 per kWh
    potential_savings = avg_consumption * 30 * 1.20 * 0.30  # 30% of monthly cost in ZMW
    
    st.subheader("💰 Savings Opportunities")
    
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown("### You Could Save")
        st.success(f"~ZMW {potential_savings:,.2f}/Month")
        st.markdown("Based on similar facilities in Zambia, try these tips:")
        
        tip_cols = st.columns(3)
        with tip_cols[0]:
            with st.container(border=True):
                st.markdown("**⏰ Shift Scheduling**")
                st.markdown("Optimize production shifts for ZESCO off-peak rates (10PM-6AM)")
        with tip_cols[1]:
            with st.container(border=True):
                st.markdown("**⚡ Power Factor Correction**")
                st.markdown("Improve equipment efficiency (common issue in Zambia's industries)")
        with tip_cols[2]:
            with st.container(border=True):
                st.markdown("**🏭 Process Optimization**")
                st.markdown("Reduce energy-intensive operations during peak hours")
    
    with cols[1]:
        with st.container(border=True):
            st.markdown("### Savings Calculator")
            st.markdown("See how efficiency improvements add up:")
            
            st.metric("Current Monthly Cost", f"ZMW {avg_consumption * 30 * 1.20:,.2f}")
            st.metric("Potential Savings (30%)", f"ZMW {potential_savings:,.2f}", delta="-30%")
            
            st.button("Get ZESCO Efficiency Plan", use_container_width=True)

# =============================================
# MAIN DASHBOARD LAYOUT
# =============================================
def generate_industrial_report():
    # Facility profile
    display_facility_profile(st.session_state.user_profile)
    
    # Key metrics at the top
    display_key_metrics(st.session_state.user_data)
    
    # Main content sections
    tab1, tab2, tab3 = st.tabs(["Usage", "Savings", "Tools"])
    
    with tab1:
        display_consumption_analysis(st.session_state.user_data)
        
        # Anomaly detection
        st.subheader("⚠️ Usage Alerts")
        with st.spinner("Checking for unusual patterns..."):
            try:
                anomalies = detect_anomalies(st.session_state.user_data)
                if not anomalies.empty:
                    st.plotly_chart(plot_anomalies(anomalies), use_container_width=True)
                    st.warning(f"We found {len(anomalies)} days with significantly higher than normal energy use.")
                    st.write("**Possible causes:**")
                    st.write("- Equipment malfunctions (common in Zambia's aging infrastructure)")
                    st.write("- Production surges (especially in mining sector)")
                    st.write("- Meter reading errors (report to ZESCO if suspected)")
                else:
                    st.success("✅ Normal Usage Patterns")
                    st.write(f"Your energy use follows expected patterns for Zambian industrial facilities. Last check: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
            except Exception as e:
                st.error(f"Error detecting anomalies: {str(e)}")
    
    with tab2:
        display_savings_recommendations(st.session_state.user_data)
        
        # Regional comparison
        st.subheader("🏭 Compare With Similar Zambian Facilities")
        with st.spinner("Loading regional data..."):
            try:
                plot_geospatial(st.session_state.user_data)
            except Exception as e:
                st.error(f"Error displaying regional comparison: {str(e)}")
        
        try:
            benchmarks = get_benchmarks(st.session_state.user_data, st.session_state.user_profile, 'industrial')
            if benchmarks.get('mean', 0) > 0:
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Your Facility", f"{st.session_state.user_data['Energy_Consumption_kWh'].mean():.1f} kWh/day")
                with cols[1]:
                    st.metric("Zambia Industry Avg", f"{benchmarks['mean']:.1f} kWh/day")
                with cols[2]:
                    st.metric("Most Efficient", f"{benchmarks['top_quartile']:.1f} kWh/day")
        except Exception as e:
            st.error(f"Error getting benchmarks: {str(e)}")
    
    with tab3:
        # Carbon footprint
        st.subheader("🌱 Environmental Impact")
        with st.spinner("Calculating environmental impact..."):
            try:
                co2 = calculate_carbon(
                    st.session_state.user_data['Energy_Consumption_kWh'].sum(), 
                    st.session_state.user_profile['Region']
                )
                
                cols = st.columns(2)
                with cols[0]:
                    with st.container(border=True):
                        st.markdown("### Your Carbon Footprint")
                        st.metric("From your electricity use", f"{co2:.1f} kg CO₂")
                
                with cols[1]:
                    with st.container(border=True):
                        st.markdown("### What This Means")
                        st.write("Equivalent to:")
                        st.write(f"- 🚗 {co2/0.12:.1f} km driven in a car (Lusaka to Ndola is ~320km)")
                        st.write(f"- 🌳 Offset by {int(co2/21)} Zambian teak trees")
            except Exception as e:
                st.error(f"Error calculating carbon footprint: {str(e)}")
        
        # Support section
        st.subheader("📞 Need Help?")
        with st.expander("Contact Support"):
            with st.form("support_form"):
                issue = st.selectbox("What do you need help with?", [
                    "High bill questions",
                    "Meter reading",
                    "Power outage",
                    "Energy efficiency advice",
                    "Industrial tariff options",
                    "Other"
                ])
                details = st.text_area("Tell us more")
                contact = st.text_input("How should we contact you?")
                
                if st.form_submit_button("Send Request"):
                    st.success("Thank you! Our support team will respond within 24 hours.")

# =============================================
# APP EXECUTION
# =============================================
def main():
    set_page_config()
    set_custom_styles()
    initialize_session_state()
    
    if not st.session_state.authenticated:
        authenticate_user()
    else:
        if st.session_state.user_data is not None:
            generate_industrial_report()
        else:
            st.error("No data available. Please try logging in again.")

if __name__ == "__main__":
    main()