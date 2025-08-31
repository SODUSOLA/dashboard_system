import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio
from typing import List, Dict, Optional
import io
import base64
import random
from datetime import datetime
from utils.gemini_client import generate_chart_insights


def generate_meaningful_chart_name(chart_spec: Dict, index: int) -> str:
    """Generate a more meaningful chart name instead of generic numbering."""
    kpi = chart_spec.get('kpi', 'Unknown KPI')
    chart_type = chart_spec.get('chart_type', 'Chart')
    group_by = chart_spec.get('group_by', None)
    color_by = chart_spec.get('color_by', None)

    # Create descriptive name based on chart properties
    if group_by and color_by:
        name = f"{kpi} Analysis: {chart_type} by {group_by} (colored by {color_by})"
    elif group_by:
        name = f"{kpi} Distribution: {chart_type} by {group_by}"
    elif color_by:
        name = f"{kpi} Comparison: {chart_type} by {color_by}"
    else:
        name = f"{kpi} Overview: {chart_type} Chart"

    return name


def export_chart(fig: go.Figure, format: str = "png") -> str:
    """Export a single Plotly figure to base64 encoded image string."""
    buffer = io.BytesIO()
    try:
        fig.write_image(buffer, format=format, width=800, height=600)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode()
    except Exception as e:
        st.error(f"Failed to export image: {e}")
        return ""


def export_dashboard_html(figures: Dict[str, go.Figure], filename: str = "dashboard_export.html",
                        dashboard_title: str = "Business Intelligence Dashboard",
                        company_name: str = "Your Company",
                        description: str = "Comprehensive data insights and performance metrics",
                        watermark_text: str = "",
                        footer_text: str = "",
                        footer_contact: str = "",
                        chart_specs: Optional[List[Dict]] = None,
                        df: Optional[pd.DataFrame] = None,
                        include_insights: bool = True,
                        include_data_summary: bool = True) -> str:
    """Export multiple Plotly figures into a professional HTML dashboard with hero section and business-ready design."""
    html_parts = []
    for idx, (title, fig) in enumerate(figures.items()):
        fig_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
        chart_name = title
        chart_insight_html = ""

        if chart_specs and idx < len(chart_specs):
            chart_name = generate_meaningful_chart_name(chart_specs[idx], idx)

            # Generate AI insights
            if include_insights and df is not None:
                insight_text = generate_chart_insights(chart_specs[idx], df)
                chart_insight_html = f'<div class="chart-insights"><strong>Insights:</strong><p>{insight_text}</p></div>'

        html_parts.append(f"""
        <div class="chart-card">
            <div class="chart-header">
                <h3>{chart_name}</h3>
            </div>
            <div class="chart-content">
                {fig_html}
                {chart_insight_html}
            </div>
        </div>
        """)

    # Watermark styling
    watermark_style = ""
    watermark_html = ""
    if watermark_text:
        watermark_style = """
        .watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 72px;
            color: rgba(0, 0, 0, 0.1);
            z-index: -1;
            pointer-events: none;
            user-select: none;
            font-weight: bold;
        }
        """
        watermark_html = f'<div class="watermark">{watermark_text}</div>'

    data_summary_html = ""
    if include_data_summary and df is not None:
        
        summary_html = df.describe().to_html(classes='data-table', index=True)

        numeric_df = df.select_dtypes(include='number')
        correlation_html = ""
        if not numeric_df.empty and len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            correlation_html = corr_matrix.to_html(classes='data-table', index=True, float_format='%.2f')

        data_summary_html = f"""
        <!-- Data Summary Section -->
        <section class="data-summary-section">
            <div class="section-header">
                <h2>Data Summary & Analytics</h2>
            </div>

            <div class="summary-tabs">
                <div class="tab-content">
                    <h3>Summary Statistics</h3>
                    <div class="table-container">
                        {summary_html}
                    </div>
                </div>

                {"<div class='tab-content'><h3>Correlation Matrix</h3><div class='table-container'>" + correlation_html + "</div></div>" if correlation_html else ""}
            </div>
        </section>
        """

    #Professional HTML template with hero section
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{dashboard_title} - {company_name}</title>
        <meta name="description" content="{description}">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {{
                --primary-color: #2c3e50;
                --secondary-color: #3498db;
                --accent-color: #e74c3c;
                --light-bg: #f8f9fa;
                --dark-text: #2c3e50;
                --light-text: #ffffff;
                --border-color: #e1e8ed;
                --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }}

            {watermark_style}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: var(--dark-text);
                background: var(--light-bg);
            }}

            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
            }}

            /* Hero Section */
            .hero {{
                background: var(--gradient);
                color: var(--light-text);
                padding: 60px 0;
                text-align: center;
                margin-bottom: 40px;
            }}

            .hero-content {{
                max-width: 800px;
                margin: 0 auto;
            }}

            .hero h1 {{
                font-size: 3rem;
                font-weight: 700;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}

            .hero p {{
                font-size: 1.2rem;
                margin-bottom: 30px;
                opacity: 0.9;
            }}

            .hero-meta {{
                display: flex;
                justify-content: center;
                gap: 30px;
                margin-top: 20px;
                flex-wrap: wrap;
            }}

            .meta-item {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .meta-item i {{
                font-size: 1.5rem;
            }}

            /* Dashboard Grid - Single column for better chart visibility */
            .dashboard-grid {{
                display: flex;
                flex-direction: column;
                gap: 40px;
                margin: 40px 0;
            }}

            /* Chart Cards */
            .chart-card {{
                background: white;
                border-radius: 12px;
                box-shadow: var(--shadow);
                overflow: hidden;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}

            .chart-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            }}

            .chart-header {{
                background: var(--primary-color);
                color: var(--light-text);
                padding: 20px;
                border-bottom: 1px solid var(--border-color);
            }}

            .chart-header h3 {{
                font-size: 1.3rem;
                font-weight: 600;
                margin: 0;
            }}

            .chart-content {{
                padding: 20px;
            }}

            /* Chart Insights */
            .chart-insights {{
                margin-top: 15px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid var(--secondary-color);
            }}

            .chart-insights strong {{
                color: var(--primary-color);
                display: block;
                margin-bottom: 8px;
            }}

            .chart-insights p {{
                margin: 0;
                line-height: 1.5;
                color: var(--dark-text);
            }}

            /* Data Summary Section */
            .data-summary-section {{
                margin-top: 60px;
                padding: 40px 0;
                background: white;
                border-radius: 12px;
                box-shadow: var(--shadow);
            }}

            .section-header {{
                text-align: center;
                margin-bottom: 40px;
            }}

            .section-header h2 {{
                font-size: 2.5rem;
                color: var(--primary-color);
                margin: 0;
            }}

            .summary-tabs {{
                display: flex;
                flex-direction: column;
                gap: 30px;
            }}

            .tab-content {{
                background: var(--light-bg);
                border-radius: 8px;
                padding: 20px;
            }}

            .tab-content h3 {{
                color: var(--primary-color);
                margin-bottom: 15px;
                font-size: 1.3rem;
            }}

            .table-container {{
                overflow-x: auto;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}

            .data-table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                font-size: 0.9rem;
            }}

            .data-table th {{
                background: var(--primary-color);
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }}

            .data-table td {{
                padding: 10px 12px;
                border-bottom: 1px solid var(--border-color);
            }}

            .data-table tr:nth-child(even) {{
                background: #f8f9fa;
            }}

            .data-table tr:hover {{
                background: #e8f4fd;
            }}

            /* Footer */
            .footer {{
                background: var(--primary-color);
                color: var(--light-text);
                text-align: center;
                padding: 30px 0;
                margin-top: 60px;
            }}

            .footer-content {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 20px;
            }}

            .brand {{
                font-size: 1.5rem;
                font-weight: 700;
            }}

            .contact-info {{
                text-align: right;
            }}

            /* Responsive Design */
            @media (max-width: 768px) {{
                .dashboard-grid {{
                    gap: 20px;
                }}

                .hero h1 {{
                    font-size: 2rem;
                }}

                .hero-meta {{
                    flex-direction: column;
                    gap: 15px;
                }}

                .footer-content {{
                    flex-direction: column;
                    text-align: center;
                }}

                .contact-info {{
                    text-align: center;
                }}
            }}
        </style>
    </head>
    <body>
        {watermark_html}
        <!-- Hero Section -->
        <header class="hero">
            <div class="container">
                <div class="hero-content">
                    <h1>{dashboard_title}</h1>
                    <p>{description}</p>
                    <div class="hero-meta">
                        <div class="meta-item">
                            <i class="fas fa-chart-line"></i>
                            <span>{len(figures)} Interactive Charts</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-clock"></i>
                            <span>Generated on {datetime.now().strftime('%B %d, %Y')}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-building"></i>
                            <span>{company_name}</span>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="container">
            <div class="dashboard-grid">
                {''.join(html_parts)}
            </div>

            {data_summary_html}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <div class="brand">
                    {company_name} Analytics
                </div>
                <div class="contact-info">
                    <p>{footer_text if footer_text else "Professional Business Intelligence Solutions"}</p>
                    <p>{footer_contact if footer_contact else f"Contact: analytics@{company_name.lower().replace(' ', '')}.com"}</p>
                </div>
            </div>
        </div>
    </footer>
    </body>
    </html>
    """


    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_html)
        return filename
    else:
        return full_html
