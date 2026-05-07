# 🏢_Commercial.py - Zambia Version
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
        page_title="Zambia Business Energy Dashboard | ",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# =============================================
# CUSTOM STYLES
# =============================================
def set_custom_styles():
    st.markdown("""
    <style>
        /* Zambia theme colors */
        :root {
            --primary-color: #078930; /* ZESCO green */
            --secondary-color: #f8d117; /* Zambia yellow */
            --accent-color: #ce1126; /* Zambia red */
            --light-color: #f8f9fa;
            --dark-color: #333333;
        }
        
        /* Rest of the styles remain the same */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        
        .stContainer {
            margin-bottom: 1.5rem;
        }
        
        /* ... (keep all other existing styles) ... */
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
            'Business_Name': 'Not Available',
            'Business_Address': 'Not Available',
            'Region': 'Not Available',
            'Contact_Number': 'Not Available',
            'Contact_Email': 'Not Available',
            'Tariff_Plan': 'Not Available',
            'Business_Type': 'Not Available',
            'Floor_Area': 'Not Available'
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
            st.title("Business Energy Dashboard")
            st.markdown("Understand and manage your business energy use in Zambia", unsafe_allow_html=True)
        
        with st.container():
            st.subheader("Sign In")
            st.write("Enter your commercial meter ID to access your business dashboard")
            
            with st.form("auth_form"):
                meter_id = st.text_input("Meter ID:", 
                                       placeholder="e.g. COM-00340",
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
                            if user_row.get('Usage_Type', '').lower() != 'commercial':
                                st.error("This meter ID is not registered for commercial use. Please access the appropriate portal.")
                                return
                            
                            st.session_state.meter_id = meter_id
                            st.session_state.user_data = data[data['Meter_ID'] == meter_id]
                            
                            profile_cols = ['Business_Name', 'Business_Address', 'Contact_Number', 
                                          'Business_Type', 'Tariff_Plan', 'Contact_Email',
                                          'Region', 'Floor_Area']
                            profile_data = {col: user_row[col] if col in user_row else "Not Available" 
                                          for col in profile_cols}
                            st.session_state.user_profile = profile_data
                            
                            st.session_state.authenticated = True
                            st.rerun()
                        else:
                            st.error("Invalid Meter ID. Please check your entry.")
                    except Exception as e:
                        st.error(f"Error loading data: {str(e)}")
            
            st.caption("Don't know your meter ID? Contact ZESCO Support at 0211-361000")

# =============================================
# BUSINESS PROFILE SECTION
# =============================================
def display_business_profile(profile):
    with st.container():
        st.markdown("""
        <div class="custom-header">
            <h1>Zambia Business Energy Dashboard</h1>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([4, 1])
        with cols[0]:
            st.subheader(f"🏢 {profile.get('Business_Name', 'My Business')}")
        with cols[1]:
            if st.button("Sign Out"):
                st.session_state.authenticated = False
                st.session_state.user_data = None
                st.session_state.meter_id = None
                st.rerun()
        
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**📍 Address**")
            st.info(profile.get('Business_Address', 'Not Available'))
            
            st.markdown("**🏘️ Region**")
            st.info(profile.get('Region', 'Not Available'))
            
            st.markdown("**📞 Contact**")
            st.info(profile.get('Contact_Number', 'Not Available'))
        
        with cols[1]:
            st.markdown("**🏭 Business Type**")
            st.info(profile.get('Business_Type', 'Not Available'))
            
            st.markdown("**📐 Floor Area**")
            st.info(f"{profile.get('Floor_Area', 'Not Available')} sqm")  # Changed to sqm for Zambia
            
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
    cost_estimate = avg_usage * 30 * 1.05  # Commercial rate in ZMW (~1.05/kWh)
    
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
        
    st.subheader("📈 Your Business Energy Patterns")
    
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
            st.write("This chart shows how much energy your business uses each day:")
            st.write("- **Operational days**: Higher energy usage (typical in Zambia's business hours)")
            st.write("- **Weekends/holidays**: Lower usage patterns")
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
            
            with st.expander("Peak Usage Times in Zambia"):
                st.write("This shows when your business uses the most energy:")
                st.write("- **Opening hours (8AM-10AM)**: Initial equipment startup")
                st.write("- **Peak operations (10AM-4PM)**: Highest energy demand")
                st.write("- **After-hours (after 6PM)**: Potential for energy savings during off-peak")
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
    potential_savings = avg_consumption * 30 * 1.05 * 0.25  # 25% of monthly cost in ZMW
    
    st.subheader("💰 Savings Opportunities")
    
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown("### You Could Save")
        st.success(f"~ZMW {potential_savings:,.2f}/Month")
        st.markdown("Based on similar Zambian businesses, try these tips:")
        
        tip_cols = st.columns(3)
        with tip_cols[0]:
            with st.container(border=True):
                st.markdown("**⏰ Shift Operations**")
                st.markdown("Run heavy equipment during ZESCO off-peak (10PM-6AM)")
        with tip_cols[1]:
            with st.container(border=True):
                st.markdown("**💡 LED Lighting**")
                st.markdown("Upgrade to energy-efficient lighting (common in Zambia)")
        with tip_cols[2]:
            with st.container(border=True):
                st.markdown("**🌡️ HVAC Optimization**")
                st.markdown("Set AC to 24°C (saves ~ZMW 300/month)")
    
    with cols[1]:
        with st.container(border=True):
            st.markdown("### Savings Calculator")
            st.markdown("See how small changes add up:")
            
            st.metric("Current Monthly Cost", f"ZMW {avg_consumption * 30 * 1.05:,.2f}")
            st.metric("Potential Savings (25%)", f"ZMW {potential_savings:,.2f}", delta="-25%")
            
            st.button("Get ZESCO Efficiency Plan", use_container_width=True)

# =============================================
# MAIN DASHBOARD LAYOUT
# =============================================
def generate_commercial_report():
    # Business profile
    display_business_profile(st.session_state.user_profile)
    
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
                    st.write("- Equipment left running (common issue in Zambia)")
                    st.write("- Faulty machinery")
                    st.write("- Increased operations")
                else:
                    st.success("✅ Normal Usage Patterns")
                    st.write(f"Your energy use follows expected patterns for Zambian businesses. Last check: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
            except Exception as e:
                st.error(f"Error detecting anomalies: {str(e)}")
    
    with tab2:
        display_savings_recommendations(st.session_state.user_data)
        
        # Regional comparison
        st.subheader("🏘️ Compare With Similar Zambian Businesses")
        with st.spinner("Loading regional data..."):
            try:
                plot_geospatial(st.session_state.user_data)
            except Exception as e:
                st.error(f"Error displaying regional comparison: {str(e)}")
        
        try:
            benchmarks = get_benchmarks(st.session_state.user_data, st.session_state.user_profile, 'commercial')
            if benchmarks.get('mean', 0) > 0:
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Your Business", f"{st.session_state.user_data['Energy_Consumption_kWh'].mean():.1f} kWh/day")
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
                        st.write(f"- 🚗 {co2/0.12:.1f} km driven (Lusaka to Livingstone is ~480km)")
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
                    "Business tariff options",
                    "Other"
                ])
                details = st.text_area("Tell us more")
                contact = st.text_input("How should we contact you?")
                
                if st.form_submit_button("Send Request"):
                    st.success("Thank you!  Our support will respond within 24 hours.")

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
            generate_commercial_report()
        else:
            st.error("No data available. Please try logging in again.")

if __name__ == "__main__":
    main()