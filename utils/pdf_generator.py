from fpdf import FPDF
import tempfile
from typing import Dict, Any
from datetime import datetime
import re

class WeatherReportPDF:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        
    def clean_markdown(self, text: str) -> str:
        """Remove markdown formatting from text"""
        # Remove ** markdown
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # Remove * markdown
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        # Remove # markdown
        text = re.sub(r'#\s+(.*?)\n', r'\1\n', text)
        return text.strip()
    
    def set_title(self, title: str):
        """Add title to the PDF"""
        self.pdf.set_font("Arial", "B", 24)
        self.pdf.cell(0, 20, self.clean_markdown(title), ln=True, align="C")
        self.pdf.ln(10)
        
    def add_section(self, title: str, content: str):
        """Add a section with title and content"""
        # Add section title
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.cell(0, 10, self.clean_markdown(title), ln=True)
        
        # Add content with proper formatting
        self.pdf.set_font("Arial", "", 12)
        content = self.clean_markdown(content)
        
        # Split content into paragraphs and add them
        paragraphs = content.split('\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                self.pdf.multi_cell(0, 10, paragraph.strip())
                self.pdf.ln(5)
        
    def add_weather_table(self, forecast_data: list):
        """Add forecast table to the PDF"""
        self.pdf.set_font("Arial", "B", 12)
        
        # Calculate column widths to fit page
        page_width = self.pdf.w - 20  # 10mm margins on each side
        col_widths = {
            'date': page_width * 0.25,
            'temp': page_width * 0.2,
            'condition': page_width * 0.35,
            'precip': page_width * 0.2
        }
        
        # Table header
        self.pdf.cell(col_widths['date'], 10, "Date", 1)
        self.pdf.cell(col_widths['temp'], 10, "Temperature", 1)
        self.pdf.cell(col_widths['condition'], 10, "Condition", 1)
        self.pdf.cell(col_widths['precip'], 10, "Rain", 1)
        self.pdf.ln()
        
        # Table data
        self.pdf.set_font("Arial", "", 12)
        for day in forecast_data:
            # Format date
            date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%b %d')
            
            # Format temperature
            temp = f"{day['day']['avgtemp_c']}°C"
            
            # Handle long condition text
            condition = day['day']['condition']['text']
            if len(condition) > 20:  # If text is too long
                condition = condition[:17] + "..."
            
            # Format precipitation
            precip = f"{day['day']['daily_chance_of_rain']}%"
            
            # Add row
            self.pdf.cell(col_widths['date'], 10, date, 1)
            self.pdf.cell(col_widths['temp'], 10, temp, 1)
            self.pdf.cell(col_widths['condition'], 10, condition, 1)
            self.pdf.cell(col_widths['precip'], 10, precip, 1)
            self.pdf.ln()
            
    def generate_report(self, report_data: Dict[str, Any], activity: str) -> str:
        """Generate PDF report and return the filepath"""
        # Set title
        self.set_title(f"Weather Report for {report_data['location']}")
        
        # Add current conditions
        current = report_data['current_conditions']
        current_weather = (
            f"Temperature: {current['temperature']}°C\n"
            f"Condition: {current['condition']}\n"
            f"Humidity: {current['humidity']}%\n"
            f"Wind Speed: {current['wind_speed']} km/h"
        )
        self.add_section("Current Weather Conditions", current_weather)
        
        # Add activity analysis
        self.add_section(f"Analysis for {activity}", report_data['analysis'])
        
        # Add forecast table
        self.add_section("5-Day Forecast", "")
        self.add_weather_table(report_data['forecast_summary'])
        
        # Generate temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        self.pdf.output(temp_file.name)
        
        return temp_file.name