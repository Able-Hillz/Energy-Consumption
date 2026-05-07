# visualization.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
#from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

class ZESCOVisualizer:
    """
    Advanced visualization class for ZESCO energy data with custom styling
    """
    def __init__(self, theme='zesco'):
        self.theme = theme
        self.colors = {
            'zesco': {
                'primary': '#F59D33',  # ZESCO orange
                'secondary': '#1C9953',  # ZESCO green
                'background': '#FFFFFF',
                'text': '#333333'
            },
            'dark': {
                'primary': '#2A9DF4',
                'secondary': '#FAA916',
                'background': '#121212',
                'text': '#FFFFFF'
            }
        }
    
    def _apply_theme(self, fig):
        """Apply theme styling to plotly figure"""
        theme = self.colors.get(self.theme, self.colors['zesco'])
        
        fig.update_layout(
            plot_bgcolor=theme['background'],
            paper_bgcolor=theme['background'],
            font_color=theme['text'],
            title_font_color=theme['primary'],
            hoverlabel=dict(
                bgcolor=theme['secondary'],
                font_size=12,
                font_family="Arial"
            )
        )
        return fig
    
    def create_dashboard(self, data):
        """
        Create a complete dashboard visualization
        
        Args:
            data: DataFrame containing energy data
            
        Returns:
            Plotly figure containing dashboard
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "choropleth"}, {"type": "pie"}]
            ],
            subplot_titles=(
                "Consumption Trends",
                "Daily Consumption",
                "Regional Distribution",
                "Usage Type Breakdown"
            )
        )
        
        # Add consumption trends
        trends = px.line(
            data,
            x='Timestamp',
            y='Energy_Consumption_kWh'
        )
        for trace in trends.data:
            fig.add_trace(trace, row=1, col=1)
        
        # Add daily consumption
        if 'Hour' in data.columns:
            daily = data.groupby('Hour')['Energy_Consumption_kWh'].mean().reset_index()
            fig.add_trace(
                go.Bar(
                    x=daily['Hour'],
                    y=daily['Energy_Consumption_kWh'],
                    name='Hourly Avg'
                ),
                row=1, col=2
            )
        
        # Add regional distribution
        if 'Region' in data.columns:
            regions = data.groupby('Region')['Energy_Consumption_kWh'].mean().reset_index()
            fig.add_trace(
                go.Choropleth(
                    locations=regions['Region'],
                    z=regions['Energy_Consumption_kWh'],
                    locationmode='country names',
                    colorscale='Viridis'
                ),
                row=2, col=1
            )
        
        # Add usage breakdown
        if 'Usage_Type' in data.columns:
            usage = data['Usage_Type'].value_counts().reset_index()
            fig.add_trace(
                go.Pie(
                    labels=usage['index'],
                    values=usage['Usage_Type'],
                    name='Usage Types'
                ),
                row=2, col=2
            )
        
        # Apply theme and update layout
        fig = self._apply_theme(fig)
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="ZESCO Energy Dashboard",
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        return fig

def plot_consumption_trends(user_data, title="Daily Energy Consumption"):
    """
    Creates a simple bar chart of daily energy consumption
    Args:
        user_data: DataFrame containing 'Timestamp' and 'Energy_Consumption_kWh'
        title: Chart title
    Returns:
        Plotly figure or None if data is invalid
    """
    try:
        # Validate input
        if user_data.empty or 'Energy_Consumption_kWh' not in user_data.columns:
            st.warning("⚠️ No energy consumption data found")
            return None

        # Create working copy
        df = user_data.copy()
        
        # Ensure we have timestamps
        if 'Timestamp' not in df.columns:
            if isinstance(df.index, pd.DatetimeIndex):
                df['Timestamp'] = df.index
            else:
                st.warning("⏱️ No timestamp data available")
                return None

        # Convert and extract dates
        df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
        df['Energy_Consumption_kWh'] = pd.to_numeric(df['Energy_Consumption_kWh'], errors='coerce')
        df = df.dropna(subset=['Date', 'Energy_Consumption_kWh'])
        
        if df.empty:
            st.warning("📊 No valid data points after processing")
            return None

        # Aggregate daily consumption
        daily = df.groupby('Date')['Energy_Consumption_kWh'].sum().reset_index()
        
        # Create bar chart
        fig = px.bar(
            daily,
            x='Date',
            y='Energy_Consumption_kWh',
            title=title,
            labels={'Energy_Consumption_kWh': 'Energy (kWh)'},
            color_discrete_sequence=['#1C9953']  # ZESCO green
        )
        
        # Clean styling
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_title='Date',
            yaxis_title='Energy (kWh)',
            hovermode='x unified'
        )
        
        # Add average reference line
        avg = daily['Energy_Consumption_kWh'].mean()
        fig.add_hline(
            y=avg,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Average: {avg:.1f} kWh",
            annotation_position="bottom right"
        )
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Error creating daily chart: {str(e)}")
        return None


def plot_daily_pattern(user_data, title="Hourly Energy Pattern"):
    """
    Creates a simple bar chart of hourly energy consumption pattern
    Args:
        user_data: DataFrame containing 'Timestamp' and 'Energy_Consumption_kWh'
        title: Chart title
    Returns:
        Plotly figure or None if data is invalid
    """
    try:
        # Validate input
        if user_data.empty or 'Timestamp' not in user_data.columns:
            st.warning("⚠️ No timestamp data available")
            return None

        # Create working copy
        df = user_data.copy()
        
        # Extract hour and validate
        df['Hour'] = pd.to_datetime(df['Timestamp']).dt.hour
        df['Energy_Consumption_kWh'] = pd.to_numeric(df['Energy_Consumption_kWh'], errors='coerce')
        df = df.dropna(subset=['Hour', 'Energy_Consumption_kWh'])
        
        if df.empty:
            st.warning("⏳ No valid hourly data points")
            return None

        # Calculate hourly averages
        hourly = df.groupby('Hour')['Energy_Consumption_kWh'].mean().reset_index()
        
        # Create bar chart
        fig = px.bar(
            hourly,
            x='Hour',
            y='Energy_Consumption_kWh',
            title=title,
            labels={'Energy_Consumption_kWh': 'Energy (kWh)'},
            color_discrete_sequence=['#F59D33']  # ZESCO orange
        )
        
        # Style the chart
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                tickvals=list(range(24)),
                title='Hour of Day'
            ),
            yaxis_title='Energy (kWh)'
        )
        
        # Add peak hour annotation
        peak_hour = hourly.loc[hourly['Energy_Consumption_kWh'].idxmax()]
        fig.add_annotation(
            x=peak_hour['Hour'],
            y=peak_hour['Energy_Consumption_kWh'],
            text=f"Peak: {peak_hour['Energy_Consumption_kWh']:.1f} kWh",
            showarrow=True,
            arrowhead=1
        )
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Error creating hourly chart: {str(e)}")
        return None

def plot_anomalies(anomalies, title="Unusual Usage Detected", key=None):
    """Visualize energy consumption anomalies"""
    if anomalies.empty or 'Energy_Consumption_kWh' not in anomalies.columns:
        st.warning("No unusual usage patterns found")
        return None
    
    try:
        # Prepare data
        df = anomalies.copy()
        if 'Timestamp' in df.columns:
            df['Date'] = pd.to_datetime(df['Timestamp']).dt.date
        else:
            df['Date'] = df.index.date if hasattr(df.index, 'date') else pd.to_datetime(df.index).date
        
        # Create visualization
        fig = px.scatter(
            df,
            x='Date',
            y='Energy_Consumption_kWh',
            color='Anomaly_Score' if 'Anomaly_Score' in df.columns else None,
            title=title,
            labels={'Energy_Consumption_kWh': 'Energy (kWh)'},
            color_continuous_scale=['#1C9953', '#F59D33', '#E74C3C']
        )
        
        # Style improvements
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        fig.update_traces(
            marker=dict(size=10, line=dict(width=1, color='DarkSlateGrey')),
            hovertemplate='<b>%{x|%b %d}</b><br>%{y:.1f} kWh<extra></extra>'
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error showing anomalies: {str(e)}")
        return None

def plot_geospatial(data, region_col='Region', key=None):
    """Show regional consumption patterns"""
    if data.empty or region_col not in data.columns:
        st.warning("No regional data available")
        return None
        
    try:
        # Create Zambia map centered
        m = folium.Map(location=[-13.133897, 27.849332], zoom_start=6, tiles='CartoDB positron')
        
        # Add region consumption data
        folium.Choropleth(
            geo_data="https://raw.githubusercontent.com/johan/world.geo.json/master/countries/ZMB.geo.json",
            name="Regional Usage",
            data=data,
            columns=[region_col, 'Energy_Consumption_kWh'],
            key_on="feature.properties.name",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Energy Use (kWh)"
        ).add_to(m)
        
        folium.LayerControl().add_to(m)
        
        return m
        
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        return None