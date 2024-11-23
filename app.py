import streamlit as st
import base64
import os
from utils.weather_api import WeatherAPI
from utils.llm_analyzer import WeatherAnalyzer
from utils.pdf_generator import WeatherReportPDF
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Initialize services
weather_service = WeatherAPI()
analyzer = WeatherAnalyzer()
pdf_generator = WeatherReportPDF()

def get_weather_icon(condition: str) -> str:
    """Return appropriate weather emoji based on condition"""
    condition = condition.lower()
    if 'sun' in condition or 'clear' in condition:
        return "☀️"
    elif 'rain' in condition:
        return "🌧️"
    elif 'cloud' in condition:
        return "☁️"
    elif 'snow' in condition:
        return "❄️"
    elif 'thunder' in condition or 'storm' in condition:
        return "⛈️"
    elif 'mist' in condition or 'fog' in condition:
        return "🌫️"
    elif 'drizzle' in condition:
        return "🌦️"
    elif 'wind' in condition:
        return "💨"
    else:
        return "🌤️"

def create_temperature_chart(forecast_data):
    """Create temperature chart using plotly"""
    dates = []
    max_temps = []
    min_temps = []
    avg_temps = []

    for day in forecast_data:
        date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%b %d')
        dates.append(date)
        max_temps.append(day['day']['maxtemp_c'])
        min_temps.append(day['day']['mintemp_c'])
        avg_temps.append(day['day']['avgtemp_c'])

    fig = go.Figure()

    # Add traces
    fig.add_trace(go.Scatter(
        x=dates, y=max_temps,
        name='Max Temp',
        line=dict(color='#FF4B4B', width=2),
        mode='lines+markers'
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=min_temps,
        name='Min Temp',
        line=dict(color='#4B4BFF', width=2),
        mode='lines+markers'
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=avg_temps,
        name='Avg Temp',
        line=dict(color='#9D9D9D', width=2, dash='dash'),
        mode='lines'
    ))

    fig.update_layout(
        title='Temperature Forecast',
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        template='plotly_white',
        hovermode='x unified'
    )

    return fig

def create_precipitation_chart(forecast_data):
    """Create precipitation chart using plotly"""
    dates = []
    precip = []
    rain_chance = []

    for day in forecast_data:
        date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%b %d')
        dates.append(date)
        precip.append(day['day']['totalprecip_mm'])
        rain_chance.append(day['day']['daily_chance_of_rain'])

    fig = go.Figure()

    # Add bar chart for precipitation
    fig.add_trace(go.Bar(
        x=dates,
        y=precip,
        name='Precipitation (mm)',
        marker_color='#4B4BFF'
    ))

    # Add line chart for rain chance
    fig.add_trace(go.Scatter(
        x=dates,
        y=rain_chance,
        name='Chance of Rain (%)',
        line=dict(color='#FF4B4B', width=2),
        mode='lines+markers',
        yaxis='y2'
    ))

    fig.update_layout(
        title='Precipitation Forecast',
        xaxis_title='Date',
        yaxis_title='Precipitation (mm)',
        yaxis2=dict(
            title='Chance of Rain (%)',
            overlaying='y',
            side='right'
        ),
        template='plotly_white',
        hovermode='x unified'
    )

    return fig

def main():
    st.set_page_config(
        page_title="Weather Report Generator",
        page_icon="🌤️",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .weather-card {
            background-color: #14171f;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .weather-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
        }
        .metric-label {
            font-size: 14px;
            color: #666;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title and description
    st.title("🌤️ Weather Report Generator")
    st.write("Get personalized weather reports based on your activities!")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📝 Enter Details")
        
        # Location input
        location = st.text_input(
            "Location",
            placeholder="e.g., Delhi",
            key="location"
        )
        
        # Activity input
        activity = st.text_input(
            "Planned Activity",
            placeholder="e.g., Having a picnic, Going hiking",
            key="activity"
        )
        
        # Generate button
        generate_button = st.button("Generate Report", type="primary")
        
        # Add some information
        st.markdown("---")
        st.markdown("### How it works")
        st.markdown("""
        1. Enter your location 📍
        2. Specify your planned activity 🎯
        3. Get personalized weather analysis 🤖
        4. Download detailed PDF report 📄
        """)
    
    # Initialize session state
    if 'weather_report' not in st.session_state:
        st.session_state.weather_report = None
    
    # Process generation request
    if generate_button and location and activity:
        progress_placeholder = st.empty()
        
        try:
            with progress_placeholder.container():
                st.info("🌡️ Fetching weather data...")
                weather_data = weather_service.get_combined_weather_data(location)
            
            with progress_placeholder.container():
                st.info("🤖 Analyzing conditions and generating recommendations...")
                analysis = analyzer.analyze_weather(weather_data, activity)
            
            with progress_placeholder.container():
                st.info("📊 Preparing your report...")
                report = analyzer.format_report(analysis, weather_data)
                
            st.session_state.weather_report = report
            progress_placeholder.empty()
            
        except Exception as e:
            st.error(f"Error generating report: {str(e)}")
    
    # Display results
    if st.session_state.weather_report:
        report = st.session_state.weather_report
        
        # Current weather card
        st.header("Current Weather Conditions")
        cols = st.columns(5)
        
        # Temperature
        with cols[0]:
            st.markdown(f"""
            <div class="weather-card">
                <div class="weather-icon">{get_weather_icon(report['current_conditions']['condition'])}</div>
                <div class="metric-value">{report['current_conditions']['temperature']}°C</div>
                <div class="metric-label">Temperature</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Condition
        with cols[1]:
            st.markdown(f"""
            <div class="weather-card">
                <div class="weather-icon">🌡️</div>
                <div class="metric-value">{report['current_conditions']['condition']}</div>
                <div class="metric-label">Condition</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Humidity
        with cols[2]:
            st.markdown(f"""
            <div class="weather-card">
                <div class="weather-icon">💧</div>
                <div class="metric-value">{report['current_conditions']['humidity']}%</div>
                <div class="metric-label">Humidity</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Wind Speed
        with cols[3]:
            st.markdown(f"""
            <div class="weather-card">
                <div class="weather-icon">💨</div>
                <div class="metric-value">{report['current_conditions']['wind_speed']} km/h</div>
                <div class="metric-label">Wind Speed</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Analysis
        st.header("Weather Analysis")
        st.markdown(report['analysis'])
        
        # Forecast visualization
        st.header("Weather Forecast")
        
        # Temperature chart
        st.plotly_chart(create_temperature_chart(report['forecast_summary']), use_container_width=True)
        
        # Precipitation chart
        st.plotly_chart(create_precipitation_chart(report['forecast_summary']), use_container_width=True)
        
        # Detailed forecast table
        st.header("Detailed Forecast")
        forecast_data = []
        for day in report['forecast_summary']:
            date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%A, %b %d')
            forecast_data.append({
                'Date': date,
                'Weather': get_weather_icon(day['day']['condition']['text']),
                'Max Temp': f"{day['day']['maxtemp_c']}°C",
                'Min Temp': f"{day['day']['mintemp_c']}°C",
                'Condition': day['day']['condition']['text'],
                'Rain Chance': f"{day['day']['daily_chance_of_rain']}%",
                'Precipitation': f"{day['day']['totalprecip_mm']} mm"
            })
        
        st.table(forecast_data)
        
        # Generate and provide PDF download
        st.header("Download Report")
        try:
            pdf_path = pdf_generator.generate_report(report, activity)
            pdf_filename = f"weather_report_{report['location']}.pdf"
            
            with open(pdf_path, "rb") as pdf_file:
                btn = st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
            
            os.remove(pdf_path)
            
        except Exception as e:
            st.error(f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    main()