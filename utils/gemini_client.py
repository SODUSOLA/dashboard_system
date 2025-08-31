import os
import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv


load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")

def infer_kpis_from_Dataframe(df: pd.DataFrame) -> str:
    prompt = f"""
    You are an expert Data Analyst specializing in business intelligence reporting.

    Given the preview and structure of the uploaded dataset below, infer 5–10 meaningful and actionable Key Performance Indicators (KPIs) that a business could track.

    - Group KPIs by category where possible (e.g., Sales, Customer Behavior, Financial Health, Operations)
    - Prioritize KPIs that can be calculated directly from this data
    - Mention the relevant columns used to compute each KPI
    - If applicable, suggest a formula or brief logic for computing the KPI

    ### Dataset Preview
    {df.head().to_markdown()}

    ### Available Columns
    {list(df.columns)}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating KPIs: {str(e)}"


def generate_chart_insights(chart_spec: dict, df: pd.DataFrame) -> str:
    """Generate AI-powered insights for a specific chart."""
    try:
        kpi = chart_spec.get('kpi', '')
        chart_type = chart_spec.get('chart_type', '')
        group_by = chart_spec.get('group_by', None)
        color_by = chart_spec.get('color_by', None)

        # Get basic statistics for the KPI
        if kpi in df.columns:
            kpi_stats = df[kpi].describe().to_dict()
            kpi_stats_str = "\n".join([f"- {k}: {v:.2f}" for k, v in kpi_stats.items()])
        else:
            kpi_stats_str = "Statistics not available"

        prompt = f"""
        You are an expert business analyst. Analyze this chart configuration and provide 2-3 key insights:

        Chart Details:
        - KPI: {kpi}
        - Chart Type: {chart_type}
        - Grouped by: {group_by if group_by else 'None'}
        - Colored by: {color_by if color_by else 'None'}

        KPI Statistics:
        {kpi_stats_str}

        Provide actionable business insights based on this chart. Keep it concise (2-3 bullet points).
        Focus on trends, patterns, or recommendations that would be valuable for business decision-making.
        """

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Unable to generate insights: {str(e)}"
