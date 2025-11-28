# index.py - EnergyTracker Home Page
import streamlit as st
from PIL import Image
import os
import time

# =============================================
# PAGE CONFIGURATION
# =============================================
def set_page_config():
    st.set_page_config(
        page_title="Energy Consumption Analysis System",
        page_icon="💡", # A generic energy-related icon
        layout="wide",
        initial_sidebar_state="expanded"
    )

# =============================================
# CUSTOM STYLES (Copied from Residential.py, Commercial.py, Industrial.py for uniformity)
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
        
        /* Loading animation */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(255, 255, 255, 0.9);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        
        .loading-spinner {
            border: 5px solid #f3f3f3;
            border-top: 5px solid var(--primary-color);
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        .loading-text {
            color: var(--secondary-color);
            font-size: 1.2em;
            font-weight: 500;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)

# =============================================
# LOADING ANIMATION
# =============================================
def show_loading_animation():
    st.markdown("""
    <div class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">Loading Dashboard...</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================
# MAIN HOME PAGE CONTENT
# =============================================
def main():
    set_page_config()
    set_custom_styles()

    st.markdown("""
        <style>
        .full-width-header {
            width: 100%;
            text-align: center;
            padding: 30px 0;
            background: linear-gradient(to right, #3498db, #2c3e50);
            color: white;
            border-radius: 10px;
            margin-bottom: 40px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        .full-width-header h1 {
            font-size: 3.5em;
            margin-bottom: 10px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .full-width-header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        .section-title {
            color: var(--secondary-color);
            font-size: 2em;
            margin-top: 30px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 600;
        }
        .card-container {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        .nav-card {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            padding: 30px;
            text-align: center;
            width: 280px;
            transition: all 0.3s ease-in-out;
            border: 2px solid transparent;
        }
        .nav-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            border-color: var(--primary-color);
        }
        .nav-card .icon {
            font-size: 3em;
            color: var(--primary-color);
            margin-bottom: 15px;
        }
        .nav-card h3 {
            color: var(--secondary-color);
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        .nav-card p {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
        .nav-card .stButton button {
            width: 100%;
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 12px 0;
            font-size: 1.1em;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .nav-card .stButton button:hover {
            background-color: #2980b9;
        }
        </style>
    """, unsafe_allow_html=True)


    st.markdown("""
        <div class="full-width-header">
            <h1>Welcome to EnergyTracker</h1>
            <p>Your Comprehensive Energy Consumption Analysis System</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='section-title'>Explore Your Energy Insights</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="nav-card">
                <div class="icon">🏠</div>
                <h3>Residential Energy</h3>
                <p>Monitor and optimize energy usage for your home.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Access Residential Dashboard", key="residential_button"):
            show_loading_animation()
            time.sleep(1)  # Give time for the loading animation to show
            st.switch_page("pages/🏠_Residential.py")

    with col2:
        st.markdown("""
            <div class="nav-card">
                <div class="icon">🏢</div>
                <h3>Commercial Energy</h3>
                <p>Gain insights into energy patterns for your business.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Access Commercial Dashboard", key="commercial_button"):
            show_loading_animation()
            time.sleep(1)  # Give time for the loading animation to show
            st.switch_page("pages/🏢_Commercial.py")

    with col3:
        st.markdown("""
            <div class="nav-card">
                <div class="icon">🏭</div>
                <h3>Industrial Energy</h3>
                <p>Analyze and improve energy efficiency for industrial facilities.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Access Industrial Dashboard", key="industrial_button"):
            show_loading_animation()
            time.sleep(1)  # Give time for the loading animation to show
            st.switch_page("pages/🏭_Industrial.py")

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #666;">
            <p>© 2025 Energy Consumption Analysis. All rights reserved.</p>
            <p>For administrative access, please use the direct Admin portal link.</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()