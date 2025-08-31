import streamlit as st
from utils.kpi_engine import KPIEngine
from exports.html_exporter import export_dashboard_html
from exports.live_server import serve_dashboard_live
from utils.session_manager import SessionManager


st.set_page_config(page_title="Dashboard View (DIS)", layout="wide")
st.title("Dashboard Insights System (DIS)")

# Validate session data
if not SessionManager.has_data():
    st.error("No data loaded. Please return to the home page to upload data.")
    if st.button("Home"):
        st.switch_page("app.py")
    st.stop()

df = SessionManager.get_cleaned_data()
selected_charts = SessionManager.get_selected_charts()

if not selected_charts:
    st.info("No charts added yet. Go to Dashboard Configuration to set up charts.")
    if st.button("Open Dashboard Config"):
        st.switch_page("pages/dashboard_config.py")
    st.stop()

# Initialize engine with color mode from session
color_mode = st.session_state.get("color_mode", "randomized")
plain_color = st.session_state.get("plain_color", "#1f77b4")
engine = KPIEngine(df, color_mode=color_mode, plain_color=plain_color)

# Header Navigation
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown("### Dashboard Insights System")
with col2:
    if st.button("Home"):
        st.switch_page("app.py")
with col3:
    if st.button("Config"):
        st.switch_page("pages/dashboard_config.py")

# Key Stats
st.markdown("### Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", len(df))
col2.metric("Numerical KPIs", len(df.select_dtypes(include='number').columns))
col3.metric("Active Charts", len(selected_charts))
col4.metric("Total Columns", len(df.columns))

# Chart Display
st.markdown("### Your Selected Charts")
st.markdown("---")

chart_metadata = []

for i, chart_spec in enumerate(selected_charts):
    with st.container():
        st.markdown(f"**Chart {i+1}: {chart_spec['chart_type']} - {chart_spec['kpi']}**")
        fig = engine.create_chart(**chart_spec)
        st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")

        # Save PNG + Info buttons
        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                label=f"Save {i+1}",
                data=fig.to_image(format="png"),
                file_name=f"chart_{i+1}_{chart_spec['kpi']}.png",
                mime="image/png"
            )
        with col_b:
            if st.button(f"Info {i+1}", key=f"info_{i}"):
                with st.spinner("Loading Chart Info"):
                    st.info(
                        f"**Chart Type:** {chart_spec['chart_type']} chart\n"
                        f"**KPI:** {chart_spec['kpi']}\n"
                        f"**Group By:** {chart_spec.get('group_by', 'None')}\n"
                        f"**Color By:** {chart_spec.get('color_by', 'None')}"
                    )

        # Append chart metadata for export
        summary_stats = df[chart_spec["kpi"]].describe().to_dict()
        chart_metadata.append({
            "title": f"{chart_spec['chart_type']} of {chart_spec['kpi']}",
            "kpi": chart_spec['kpi'],
            "group_by": chart_spec.get("group_by", None),
            "summary": summary_stats
        })

        st.markdown("---")

# Data Summary
st.markdown("### Data Summary")
tab1, tab2, tab3 = st.tabs(["Summary", "Review", "Correlation"])
with tab1:
    st.dataframe(df.describe())
with tab2:
    st.dataframe(df.head(50))
with tab3:
    numeric_df = df.select_dtypes(include='number')
    if not numeric_df.empty:
        st.dataframe(numeric_df.corr())

# Export Dashboard UI
st.markdown("---")
st.subheader("Export Dashboard")

# Export Settings
with st.expander("Export Settings", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Dashboard Information**")
        dashboard_title = st.text_input("Dashboard Title", "Business Intelligence Dashboard")
        company_name = st.text_input("Company Name", "Your Company")
        description = st.text_area("Description", "Comprehensive data insights and performance metrics")

    with col2:
        st.markdown("**Customization Options**")
        watermark_text = st.text_input("Watermark Text", "", help="Optional watermark to display on the dashboard")
        footer_text = st.text_input("Footer Text", "", help="Custom footer message")
        footer_contact = st.text_input("Footer Contact", "", help="Custom contact information")

# Export Options
col1, col2 = st.columns(2)

with col1:
    if st.button("Download as HTML File", use_container_width=True):
        figures = {}
        for i, chart_spec in enumerate(selected_charts):
            fig = engine.create_chart(**chart_spec)
            figures[f"Chart {i+1}: {chart_spec['chart_type']} - {chart_spec['kpi']}"] = fig

        filename = export_dashboard_html(
            figures=figures,
            dashboard_title=dashboard_title,
            company_name=company_name,
            description=description,
            watermark_text=watermark_text,
            footer_text=footer_text,
            footer_contact=footer_contact,
            chart_specs=selected_charts,
            df=df,
            include_insights=True,
            include_data_summary=True
        )
        with open(filename, "rb") as f:
            st.download_button(
                label="Download Dashboard HTML",
                data=f,
                file_name=filename,
                mime="text/html",
                use_container_width=True
            )

with col2:
    if st.button("Open Live Website", use_container_width=True):
        figures = {}
        for i, chart_spec in enumerate(selected_charts):
            fig = engine.create_chart(**chart_spec)
            figures[f"Chart {i+1}: {chart_spec['chart_type']} - {chart_spec['kpi']}"] = fig

        serve_dashboard_live(
            figures=figures,
            dashboard_title=dashboard_title,
            company_name=company_name,
            description=description,
            watermark_text=watermark_text,
            footer_text=footer_text,
            footer_contact=footer_contact,
            chart_specs=selected_charts,
            df=df
        )
