# 🏠_Residential.py - Zambia Version
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
        page_title="Home Energy Dashboard | ",
        page_icon="🏠",
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
            'Name': 'Not Available',
            'Address': 'Not Available',
            'Region': 'Not Available',
            'Contact_Number': 'Not Available',
            'Contact_Email': 'Not Available',
            'Tariff_Plan': 'Not Available',
            'Household_Size': 'Not Available'
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
            st.title("Home Energy Dashboard")
            st.markdown("Understand and manage your home energy use in Zambia", unsafe_allow_html=True)
        
        with st.container():
            st.subheader("Sign In")
            st.write("Enter your residential meter ID to access your personalized dashboard")
            
            with st.form("auth_form"):
                meter_id = st.text_input("Meter ID:", 
                                       placeholder="e.g. RES-00340",
                                       max_chars=15).strip().upper()
                
                if st.form_submit_button("Access My Dashboard"):
                    loading_spinner("Verifying your meter ID...")
                    data, _ = load_and_preprocess_data()
                    
                    if 'Meter_ID' not in data.columns:
                        st.error("Meter ID system not configured in dataset")
                        return
                    
                    if meter_id in data['Meter_ID'].values:
                        user_row = data[data['Meter_ID'] == meter_id].iloc[0]
                        if user_row.get('Usage_Type', '').lower() != 'residential':
                            st.error("This meter ID is not registered for residential use. Please access the appropriate portal.")
                            return
                        
                        st.session_state.meter_id = meter_id
                        st.session_state.user_data = data[data['Meter_ID'] == meter_id]
                        
                        profile_cols = ['Name', 'Address', 'Phone_Number', 'Region', 'Tariff_Plan', 'Email', 'Household_Size']
                        profile_data = {col: user_row[col] if col in user_row else "Not Available" 
                                      for col in profile_cols}
                        st.session_state.user_profile = profile_data
                        
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Invalid Meter ID. Please check your entry.")
        
        st.caption("Don't know your meter ID? Contact ZESCO Customer Care at 0211-361000")

# =============================================
# USER PROFILE SECTION
# =============================================
def display_user_profile(profile):
    with st.container():
        st.markdown("""
        <div class="custom-header">
            <h1>Home Energy Dashboard</h1>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([4, 1])
        with cols[0]:
            st.subheader(f"👋 Hello, {profile.get('Name', 'Customer')}")
        with cols[1]:
            if st.button("Sign Out"):
                st.session_state.authenticated = False
                st.session_state.user_data = None
                st.session_state.meter_id = None
                st.rerun()
        
        cols = st.columns(4)
        with cols[0]:
            st.markdown("**📍 Address**")
            st.info(profile.get('Address', 'Not Available'))
        with cols[1]:
            st.markdown("**🏘️ Region**")
            st.info(profile.get('Region', 'Not Available'))
        with cols[2]:
            st.markdown("**📞 Contact**")
            st.info(profile.get('Phone_Number', 'Not Available'))
        with cols[3]:
            st.markdown("**💳 Tariff Plan**")
            st.info(profile.get('Tariff_Plan', 'Not Available'))

# =============================================
# KEY METRICS SECTION
# =============================================
def display_key_metrics(user_data):
    if 'Energy_Consumption_kWh' not in user_data.columns:
        return
    
    current_usage = user_data['Energy_Consumption_kWh'].iloc[-1] if not user_data.empty else 0
    avg_usage = user_data['Energy_Consumption_kWh'].mean() if not user_data.empty else 0
    cost_estimate = avg_usage * 30 * 0.75  # Residential rate in ZMW (~0.75/kWh)
    
    cols = st.columns(3)
    with cols[0]:
        st.metric("Current Usage (kWh)", f"{current_usage:.1f}", delta_color="off")
    with cols[1]:
        st.metric("Daily Average (kWh)", f"{avg_usage:.1f}", delta_color="off")
    with cols[2]:
        st.metric("Estimated Monthly Cost", f"ZMW {cost_estimate:,.2f}", delta_color="off")

# =============================================
# REAL-TIME CONSUMPTION MONITORING
# =============================================
def display_real_time_consumption(meter_id):
    st.subheader("🔌 Live Energy Use")
    
    if st.checkbox("Turn on live monitoring", help="See your current energy use in real-time"):
        stream = stream_manager.get_stream(meter_id)
        stream_placeholder = st.empty()
        chart_placeholder = st.empty()
        
        if 'stream_data' not in st.session_state:
            st.session_state.stream_data = pd.DataFrame(columns=['timestamp', 'consumption_kwh'])
        
        for data_point in stream.start_stream():
            new_row = pd.DataFrame([{
                'timestamp': pd.to_datetime(data_point['timestamp']),
                'consumption_kwh': data_point['consumption_kwh']
            }])
            st.session_state.stream_data = pd.concat([st.session_state.stream_data, new_row])
            
            usage = data_point['consumption_kwh']
            if usage > 2.0:
                status = "⚠️ High"
            elif usage > 1.0:
                status = "🔵 Medium"
            else:
                status = "🟢 Low"
            
            with stream_placeholder.container():
                st.metric("Right now", 
                          f"{status} {usage:.2f} kWh",
                          help=f"Last update: {data_point['timestamp']}")
            
            if len(st.session_state.stream_data) > 1:
                fig = px.line(
                    st.session_state.stream_data.set_index('timestamp'),
                    title="Live Consumption Trend (Last 30 Minutes)",
                    labels={'value': 'Energy (kWh)', 'timestamp': 'Time'}
                )
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    margin=dict(l=20, r=20, t=30, b=20),
                    height=300
                )
                chart_placeholder.plotly_chart(fig, use_container_width=True)
            
            if not st.checkbox("Keep monitoring", value=True, key="live_monitoring"):
                stream.stop_stream()
                break

# =============================================
# CONSUMPTION ANALYSIS
# =============================================
def display_consumption_analysis(user_data):
    st.subheader("📈 Your Energy Patterns")
    
    if 'Energy_Consumption_kWh' not in user_data.columns:
        st.warning("Energy consumption data not available")
        return
        
    tab1, tab2 = st.tabs(["Daily Trends", "Hourly Patterns"])
    
    with tab1:
        st.write("### Your Daily Energy Use")
        with st.spinner("Generating daily trends..."):
            fig1 = plot_consumption_trends(user_data)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.warning("Could not display daily trends")
        
        with st.expander("Understanding Your Daily Use in Zambia"):
            st.write("This chart shows how much energy you use each day:")
            st.write("- **High spikes** - These might be days with extra appliance use (common during load shedding)")
            st.write("- **Consistent patterns** - Your baseline energy needs")
            st.write("- **Changes over time** - Effects of new appliances or habits")
    
    with tab2:
        if 'Timestamp' in user_data.columns:
            st.write("### When You Use Energy During the Day")
            with st.spinner("Analyzing hourly patterns..."):
                fig2 = plot_daily_pattern(user_data)
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("Could not display daily pattern")
            
            with st.expander("Peak Usage Times in Zambia"):
                st.write("This shows when you use the most energy each day:")
                st.write("- **Morning peaks (6AM-9AM)** - Likely from cooking, showers, and appliances")
                st.write("- **Evening peaks (6PM-9PM)** - Often from lighting, TV, and cooking")
                st.write("- **Off-peak times (10PM-6AM)** - When you could shift some usage to save money")
        else:
            st.warning("Hourly data not available")

# =============================================
# SAVINGS RECOMMENDATIONS
# =============================================
def display_savings_recommendations(user_data):
    if 'Energy_Consumption_kWh' not in user_data.columns:
        return
        
    avg_consumption = user_data['Energy_Consumption_kWh'].mean()
    potential_savings = avg_consumption * 30 * 0.75 * 0.20  # 20% of monthly cost in ZMW
    
    st.subheader("💰 Savings Opportunities")
    
    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"#### You Could Save ~ZMW {potential_savings:,.2f}/Month")
        st.markdown("Based on similar Zambian homes, try these tips:")
        
        savings_cols = st.columns(3)
        with savings_cols[0]:
            with st.container(border=True):
                st.markdown("**⏰ Shift Usage**")
                st.markdown("Run appliances after 8pm (ZESCO off-peak)")
        with savings_cols[1]:
            with st.container(border=True):
                st.markdown("**💡 LED Bulbs**")
                st.markdown("Replace 5 bulbs to save ~ZMW 100/month")
        with savings_cols[2]:
            with st.container(border=True):
                st.markdown("**❄️ Fridge Settings**")
                st.markdown("Set to 4°C saves ~ZMW 50/month")
    
    with cols[1]:
        with st.container(border=True):
            st.markdown("#### Savings Calculator")
            st.markdown("See how small changes add up:")
            
            st.metric("Current Monthly Cost", f"ZMW {avg_consumption * 30 * 0.75:,.2f}")
            st.metric("Potential Savings (20%)", f"ZMW {potential_savings:,.2f}")
            
            if st.button("Get ZESCO Savings Plan", use_container_width=True):
                st.session_state.show_savings_plan = True

# =============================================
# ANOMALY DETECTION
# =============================================
def display_anomalies(user_data):
    st.subheader("⚠️ Usage Alerts")
    
    with st.spinner("Checking for unusual patterns..."):
        anomalies = detect_anomalies(user_data)
    
    if not anomalies.empty:
        cols = st.columns([1, 2])
        with cols[0]:
            st.warning(f"""
            **Unusual Usage Detected**  
            We found {len(anomalies)} days with significantly higher than normal energy use.
            
            Possible causes:
            - Extra guests
            - Faulty appliance
            - Left devices on during load shedding
            """)
        
        with cols[1]:
            plot_anomalies(anomalies)
    else:
        st.success(f"""
        **✅ Normal Usage Patterns**  
        Your energy use follows expected patterns for Zambian households.
        
        Last check: {pd.Timestamp.now().strftime("%Y-%m-%d")}
        """)

# =============================================
# MAIN DASHBOARD LAYOUT
# =============================================
def generate_personal_report():
    # User profile
    display_user_profile(st.session_state.user_profile)
    
    # Key metrics at the top
    display_key_metrics(st.session_state.user_data)
    
    # Main content sections
    tab1, tab2, tab3 = st.tabs(["Usage", "Savings", "Tools"])
    
    with tab1:
        display_real_time_consumption(st.session_state.meter_id)
        display_consumption_analysis(st.session_state.user_data)
        display_anomalies(st.session_state.user_data)
    
    with tab2:
        display_savings_recommendations(st.session_state.user_data)
        
        # Regional comparison
        st.subheader("🏘️ Compare With Neighbors")
        with st.spinner("Loading regional data..."):
            plot_geospatial(st.session_state.user_data)
        
        benchmarks = get_benchmarks(st.session_state.user_data, st.session_state.user_profile, 'residential')
        if benchmarks.get('mean', 0) > 0:
            cols = st.columns(3)
            with cols[0]:
                st.metric("Your Home", f"{st.session_state.user_data['Energy_Consumption_kWh'].mean():.1f} kWh/day")
            with cols[1]:
                st.metric("Area Average", f"{benchmarks['mean']:.1f} kWh/day")
            with cols[2]:
                st.metric("Efficient Homes", f"{benchmarks['top_quartile']:.1f} kWh/day")
    
    with tab3:
        # Carbon footprint
        st.subheader("🌱 Environmental Impact")
        with st.spinner("Calculating environmental impact..."):
            co2 = calculate_carbon(
                st.session_state.user_data['Energy_Consumption_kWh'].sum(), 
                st.session_state.user_profile['Region']
            )
        
        cols = st.columns(2)
        with cols[0]:
            st.metric("Your Carbon Footprint", f"{co2:.1f} kg CO₂", "From your electricity use this period")
        
        with cols[1]:
            with st.container(border=True):
                st.markdown("**What This Means**")
                st.markdown("Equivalent to:")
                st.markdown(f"- 🚗 {co2/0.12:.1f} km driven in a car")
                st.markdown(f"- 🌳 Offset by {int(co2/21)} Zambian teak trees")
        
        # Support section
        st.subheader("📞 Need Help?")
        with st.expander("Contact ZESCO Support"):
            with st.form("support_form"):
                issue = st.selectbox("What do you need help with?", [
                    "High bill questions",
                    "Meter reading",
                    "Power outage",
                    "Energy saving advice",
                    "Other"
                ])
                details = st.text_area("Tell us more")
                contact = st.text_input("How should we contact you?")
                
                if st.form_submit_button("Send Request"):
                    st.success("Thank you! ZESCO will respond within 24 hours.")

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
        generate_personal_report()

if __name__ == "__main__":
    main()