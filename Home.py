# Home.py - Hydro Electrical Energy Consumption Analysis System for Lusaka, Zambia
import streamlit as st
from PIL import Image
import os
import time
import base64
from datetime import datetime

# =============================================
# PAGE CONFIGURATION
# =============================================
def set_page_config():
    st.set_page_config(
        page_title="Lusaka Hydro Energy Analysis System | NIPA",
        page_icon="💧",  # Water droplet for hydro power
        layout="wide",
        initial_sidebar_state="expanded"
    )

# =============================================
# CUSTOM STYLES WITH ZAMBIA/LUSAKA THEME
# =============================================
def set_custom_styles():
    st.markdown("""
    <style>
        /* Zambia-inspired color palette */
        :root {
            --primary-color: #198754;  /* Green - Zambia's landscape */
            --secondary-color: #0d6efd; /* Blue - Water/hydro power */
            --accent-color: #ffc107;    /* Gold - Zambia's copper/resources */
            --light-color: #f8f9fa;
            --dark-color: #1a1e21;
            --copper-color: #b87333;    /* Copper accent */
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
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
        }

        /* Button styles - Zambia theme */
        .stButton>button {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s;
            border: 1px solid transparent;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }

        .stButton>button:hover {
            background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0,123,85,0.3);
            border-color: var(--copper-color);
        }

        /* Metric cards - Hydro theme */
        .stMetric {
            border-left: 4px solid var(--secondary-color);
            padding-left: 1rem;
            background: linear-gradient(to right, rgba(13,110,253,0.05), transparent);
        }

        /* Tab styles */
        .stTabs [role="tablist"] {
            border-bottom: 2px solid var(--secondary-color);
        }

        .stTabs [aria-selected="true"] {
            color: var(--primary-color) !important;
            font-weight: 600;
            border-bottom: 3px solid var(--primary-color);
        }

        /* Loading spinner */
        .stSpinner>div>div {
            border-color: var(--secondary-color) transparent transparent transparent !important;
        }

        /* Footer styles */
        footer {
            background: linear-gradient(to right, var(--dark-color), #2c3e50);
            color: white;
            padding: 1.5rem 0;
            margin-top: 3rem;
            border-top: 3px solid var(--copper-color);
        }

        /* NIPA Header */
        .nipa-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.5rem 0;
            margin-bottom: 1rem;
            border-bottom: 2px solid var(--copper-color);
        }

        .nipa-title {
            color: var(--primary-color);
            font-size: 1.1rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .nipa-badge {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 0.3rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        /* Info boxes - Research context */
        .research-box {
            background-color: #f0f9ff;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            border-left: 6px solid var(--secondary-color);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }

        .research-box h4 {
            color: var(--dark-color);
            margin-bottom: 10px;
            font-weight: 600;
        }

        .research-box p {
            color: #495057;
            margin-bottom: 8px;
        }

        /* Data source badges */
        .data-badge {
            display: inline-block;
            background-color: var(--light-color);
            border: 1px solid #dee2e6;
            border-radius: 20px;
            padding: 5px 15px;
            margin: 5px;
            font-size: 0.9rem;
            color: var(--dark-color);
            border-left: 3px solid var(--copper-color);
        }

        /* Zambia map placeholder style */
        .map-placeholder {
            background: linear-gradient(135deg, #e9ecef, #dee2e6);
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            border: 2px dashed var(--secondary-color);
            margin: 20px 0;
        }

        .map-placeholder p {
            color: var(--secondary-color);
            font-size: 1.1rem;
            margin: 0;
        }

        /* Key stats */
        .key-stat {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-bottom: 3px solid var(--primary-color);
        }

        .key-stat .number {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--secondary-color);
            line-height: 1;
        }

        .key-stat .label {
            color: #6c757d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Feature cards */
        .feature-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            height: 100%;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s;
            border: 1px solid #eee;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0,123,85,0.1);
            border-color: var(--primary-color);
        }

        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }

        .feature-title {
            color: var(--dark-color);
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .feature-desc {
            color: #6c757d;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* Sector badges */
        .sector-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 25px;
            font-weight: 500;
            margin: 5px;
            font-size: 0.9rem;
        }

        .sector-residential {
            background: rgba(25, 135, 84, 0.1);
            color: var(--primary-color);
            border: 1px solid var(--primary-color);
        }

        .sector-commercial {
            background: rgba(13, 110, 253, 0.1);
            color: var(--secondary-color);
            border: 1px solid var(--secondary-color);
        }

        .sector-industrial {
            background: rgba(184, 115, 51, 0.1);
            color: var(--copper-color);
            border: 1px solid var(--copper-color);
        }

        /* Hero section */
        .hero-section {
            background: linear-gradient(135deg, #1a472a, #0d6efd);
            color: white;
            padding: 3rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }

        .hero-section::before {
            content: "⚡";
            position: absolute;
            top: -20px;
            right: -20px;
            font-size: 10rem;
            opacity: 0.1;
            transform: rotate(15deg);
        }

        .hero-title {
            font-size: 3.2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }

        .hero-subtitle {
            font-size: 1.3rem;
            opacity: 0.95;
            margin-bottom: 0.5rem;
            position: relative;
            z-index: 1;
        }

        .hero-academic {
            font-size: 1rem;
            opacity: 0.8;
            margin-top: 1.5rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255,255,255,0.2);
        }

        /* Loading overlay */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(25,135,84,0.95), rgba(13,110,253,0.95));
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            backdrop-filter: blur(5px);
        }

        .loading-spinner {
            border: 5px solid rgba(255,255,255,0.2);
            border-top: 5px solid white;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }

        .loading-text {
            color: white;
            font-size: 1.3rem;
            font-weight: 500;
            text-align: center;
        }

        .loading-small {
            color: rgba(255,255,255,0.8);
            font-size: 0.9rem;
            margin-top: 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Quote box */
        .quote-box {
            background: #f8f9fa;
            border-left: 4px solid var(--copper-color);
            padding: 20px;
            margin: 20px 0;
            font-style: italic;
            color: #495057;
            border-radius: 0 8px 8px 0;
        }

        /* Metadata footer */
        .metadata-footer {
            margin-top: 2rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 0.8rem;
            color: #6c757d;
            text-align: center;
            border: 1px solid #dee2e6;
        }
    </style>
    """, unsafe_allow_html=True)

# =============================================
# LOADING ANIMATION WITH CONTEXT
# =============================================
def show_loading_animation(page_name):
    st.markdown(f"""
    <div class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">Loading {page_name} Dashboard...</div>
        <div class="loading-small">Analyzing Lusaka's hydro energy patterns</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================
# SESSION STATE INITIALIZATION
# ======================================
def init_session_state():
    if 'page_visits' not in st.session_state:
        st.session_state.page_visits = 1
    else:
        st.session_state.page_visits += 1

# =============================================
# MAIN HOME PAGE CONTENT
# =============================================
def main():
    set_page_config()
    set_custom_styles()
    init_session_state()

    # NIPA Header
    st.markdown(f"""
        <div class="nipa-header">
            <span class="nipa-title">🏛️ NATIONAL INSTITUTE OF PUBLIC ADMINISTRATION (NIPA)</span>
            <span class="nipa-badge">Bachelor of Computer Science • Project 2025</span>
        </div>
    """, unsafe_allow_html=True)

    # Hero Section with Zambia/Lusaka focus
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">💧 Hydro Electrical Energy Analysis System</h1>
            <p class="hero-subtitle">Lusaka, Zambia • Urban Energy Intelligence</p>
            <p class="hero-academic">Student: MUTINTA ESTHER MWEENE (2022150900) • Supervisor: HUNRY T NJOVU</p>
        </div>
    """, unsafe_allow_html=True)

    # Project Overview - Aligned with Proposal
    st.markdown("""
        <div class="research-box">
            <h4>🎯 Research Context</h4>
            <p>This system addresses the critical need for accessible hydro electrical energy analysis in Lusaka, where 85% of electricity comes from hydropower and rapid urbanization strains existing infrastructure. The prototype transforms conventional consumption data into actionable insights for urban stakeholders.</p>
        </div>
    """, unsafe_allow_html=True)

    # Key Urban Statistics - Lusaka Context
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class="key-stat">
                <div class="number">85%</div>
                <div class="label">Hydropower Reliance</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="key-stat">
                <div class="number">3</div>
                <div class="label">Urban Sectors Analyzed</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="key-stat">
                <div class="number">12</div>
                <div class="label">Monthly Data Points</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="key-stat">
                <div class="number">2025</div>
                <div class="label">Prototype Launch</div>
            </div>
        """, unsafe_allow_html=True)

    # Data Sources Section (from proposal section 3.3)
    st.markdown("<h3 style='margin-top: 2rem;'>📊 Data Sources & Methodology</h3>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 2rem;">
            <span class="data-badge">📍 ZESCO Lusaka Regional Reports</span>
            <span class="data-badge">📍 Lusaka City Council Energy Statistics</span>
            <span class="data-badge">📍 Monthly Billing Aggregates</span>
            <span class="data-badge">📍 Synthetic Urban Validation Data</span>
            <span class="data-badge">📍 Conventional Meter Readings</span>
        </div>
    """, unsafe_allow_html=True)

    # Main Navigation - Sector Dashboards (from proposal section 3.6)
    st.markdown("<h2 style='text-align: center; margin: 3rem 0 2rem;'>🔍 Lusaka Sector Analysis Dashboards</h2>", unsafe_allow_html=True)

    # Create three columns for sector cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🏠</div>
                <div class="feature-title">Residential Sector Analysis</div>
                <span class="sector-badge sector-residential">High-density areas</span>
                <span class="sector-badge sector-residential">Evening peak loads</span>
                <div class="feature-desc" style="margin-top: 15px;">
                    Monitor consumption patterns across Lusaka's residential zones. 
                    Identify evening peak loads and neighborhood-specific usage trends 
                    using conventional monthly data.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Access Residential Dashboard", key="residential_btn", use_container_width=True):
            show_loading_animation("Residential")
            time.sleep(0.8)
            st.switch_page("pages/🏠_Residential.py")

    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🏢</div>
                <div class="feature-title">Commercial Sector Analysis</div>
                <span class="sector-badge sector-commercial">CBD & Shopping malls</span>
                <span class="sector-badge sector-commercial">Business hours demand</span>
                <div class="feature-desc" style="margin-top: 15px;">
                    Analyze commercial energy patterns in Lusaka's Central Business District.
                    Track peak business hours consumption and identify optimization opportunities.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Access Commercial Dashboard", key="commercial_btn", use_container_width=True):
            show_loading_animation("Commercial")
            time.sleep(0.8)
            st.switch_page("pages/🏢_Commercial.py")

    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🏭</div>
                <div class="feature-title">Light Industrial Analysis</div>
                <span class="sector-badge sector-industrial">Industrial zones</span>
                <span class="sector-badge sector-industrial">Consistent high demand</span>
                <div class="feature-desc" style="margin-top: 15px;">
                    Evaluate energy usage in Lusaka's light industrial areas.
                    Monitor operational peaks and support efficiency improvements 
                    for manufacturing and processing facilities.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 Access Industrial Dashboard", key="industrial_btn", use_container_width=True):
            show_loading_animation("Industrial")
            time.sleep(0.8)
            st.switch_page("pages/🏭_Industrial.py")

    # Research Objectives (from proposal section 1.3)
    st.markdown("---")
    st.markdown("<h3 style='margin: 2rem 0 1rem;'>🎯 Research Objectives</h3>", unsafe_allow_html=True)
    
    obj1, obj2, obj3 = st.columns(3)
    
    with obj1:
        st.info("**Objective 1**\n\nDevelop functional prototype using Python and Streamlit for processing Lusaka's conventional hydro energy data", icon="1️⃣")
    
    with obj2:
        st.info("**Objective 2**\n\nTest prototype functionality with Lusaka-specific datasets and validate with urban stakeholders", icon="2️⃣")
    
    with obj3:
        st.info("**Objective 3**\n\nPropose evidence-based recommendations for hydro energy conservation in Lusaka", icon="3️⃣")

    # Research Questions (from proposal section 1.4)
    with st.expander("📚 Research Questions (Click to expand)"):
        st.markdown("""
        **RQ1:** How can an interactive visualization system improve understanding of hydro energy usage trends in Lusaka's urban context?
        
        **RQ2:** What are the technical requirements for a user-friendly analysis tool tailored to Lusaka's specific energy challenges?
        
        **RQ3:** To what extent can the prototype identify inefficiencies in Lusaka's hydro energy consumption data?
        """)

    # Expected Outcomes (from proposal section 6.1)
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f6f9fc, #ffffff); padding: 2rem; border-radius: 12px; margin: 2rem 0;">
            <h4>📈 Expected Outcomes</h4>
            <ul>
                <li>Fully functional prototype for Lusaka's urban energy analysis</li>
                <li>Identification of sector-specific consumption patterns</li>
                <li>Stakeholder engagement framework for energy management</li>
                <li>Scalable foundation for future AMR system integration</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Quote from proposal
    st.markdown("""
        <div class="quote-box">
            "Hydro electrical energy is the lifeblood of modern economies, powering industries, homes, 
            and essential services. In Lusaka, economic growth is intimately tied to hydro energy availability."
        </div>
    """, unsafe_allow_html=True)

    # Future Expansion (from proposal appendix)
    with st.expander("🔮 Future Expansion Possibilities"):
        st.markdown("""
        - **Phase 2:** Automated Meter Reading (AMR) system integration
        - **Phase 3:** Real-time data processing capabilities
        - **Phase 4:** Mobile data collection for field technicians
        - **Phase 5:** Integration with ZESCO's existing infrastructure
        """)

    # Footer with academic context
    st.markdown("---")
    st.markdown(f"""
        <div style="text-align: center;">
            <p style="color: #666; font-size: 0.9rem;">
                © 2025 National Institute of Public Administration (NIPA) • Bachelor of Computer Science<br>
                Project: Hydro Electrical Energy Consumption Analysis System for Lusaka, Zambia<br>
                Student: MUTINTA ESTHER MWEENE (2022150900) | Supervisor: HUNRY T NJOVO
            </p>
            <p style="color: #999; font-size: 0.8rem; margin-top: 1rem;">
                This prototype utilizes conventional data sources as outlined in the project proposal.<br>
                For administrative and research use only. Last updated: {datetime.now().strftime('%B %d, %Y')}
            </p>
        </div>
        
        <div class="metadata-footer">
            <span>📊 Data Sources: ZESCO Lusaka Region | Lusaka City Council | Energy Regulation Board</span><br>
            <span>⚡ System Version: 1.0.0 (Research Prototype) | Page Visits: {st.session_state.page_visits}</span>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()