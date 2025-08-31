import streamlit as st
from utils.kpi_engine import KPIEngine
from utils.session_manager import SessionManager

st.set_page_config(page_title="Dashboard Configuration", layout="wide")
st.title("Dashboard Configuration")

# Initialize session state
SessionManager.initialize_session()

# Load data
if SessionManager.has_data():
    df = SessionManager.get_cleaned_data()
    st.success("Data loaded from Home Page.")
else:
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    if uploaded_file:
        from utils.file_handler import read_file
        from utils.data_cleaner import clean_data

        df = clean_data(read_file(uploaded_file))
        SessionManager.store_data(df, {
            'name': uploaded_file.name,
            'type': uploaded_file.type,
            'size': len(uploaded_file.getvalue())
        })
        st.success("Data loaded.")
    else:
        st.info("Please upload a file to configure the dashboard.")
        st.stop()

# Global Color Customization
st.sidebar.subheader("Chart Color Settings")
color_mode = st.sidebar.selectbox("Color Mode", ["plain", "randomized"])

plain_color = "#1f77b4"  # default blue
if color_mode == "plain":
    plain_color = st.sidebar.color_picker("Pick a color", "#1f77b4")

# Chart config options
CHART_TYPES = ["Bar", "Line", "Area", "Scatter", "Pie", "Histogram", "Box", "Violin", "Heatmap", "Bubble"]
kpi_options = df.select_dtypes(include='number').columns.tolist()
group_by_options = df.columns.tolist()
selected_charts = SessionManager.get_selected_charts()

# Add Chart Section
st.divider()
st.subheader("Add Charts to Dashboard")

chart_form = st.form("chart_form")
with chart_form:
    chart_type = st.selectbox("Chart Type", CHART_TYPES)
    kpi = st.selectbox("Select KPI", kpi_options)
    group_by = st.selectbox("Group By", group_by_options)

    size_col = None
    if chart_type == "Bubble":
        size_col = st.selectbox("Bubble Size Column", kpi_options)
        if kpi == size_col:
            st.warning("KPI and bubble size column must differ.")
            st.stop()

    label = st.text_input("Chart Label (Optional)")

    submitted = st.form_submit_button("Add Chart")

if submitted:
    try:
        # Prevent duplicate chart configurations
        chart_label = label or f"{chart_type} of {kpi} by {group_by}"
        existing_labels = [chart.get('label') for chart in selected_charts]
        if chart_label in existing_labels:
            st.error("A chart with this label already exists. Please choose a different label.")
            st.stop()

        chart_config = {
            "chart_type": chart_type,
            "kpi": kpi,
            "group_by": group_by,
            "label": label or f"{chart_type} of {kpi} by {group_by}"
        }
        if size_col:
            chart_config["size"] = size_col

        selected_charts.append(chart_config)
        SessionManager.store_selected_charts(selected_charts)
        st.success(f"Added: {chart_config['label']}")
        st.rerun()
    except Exception as e:
        st.error(f"Error adding chart: {str(e)}")
        st.info("Please check your chart configuration and try again.")

# Show Added Charts
if selected_charts:
    st.divider()
    st.subheader("Charts Added")

    # Pass color settings globally
    engine = KPIEngine(df, color_mode=color_mode, plain_color=plain_color)

    for idx, chart in enumerate(selected_charts):
        with st.container():
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown(f"**{idx + 1}. {chart.get('label')}**")
                try:
                    fig = engine.create_chart(
                        chart['kpi'],
                        chart['chart_type'],
                        chart['group_by'],
                        chart.get('size')
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"chart_{idx}")
                except Exception as e:
                    st.error(f"Error creating chart: {str(e)}")
                    st.info("This might be due to data type issues. Try selecting different columns or chart types.")

            with col2:
                if st.button("❌", key=f"remove_{idx}"):
                    selected_charts.pop(idx)
                    SessionManager.store_selected_charts(selected_charts)
                    st.rerun()
else:
    st.info("No charts added yet.")

# Final Navigation 
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Home", use_container_width=True):
        st.switch_page("app.py")
with col2:
    if st.button("View Dashboard", use_container_width=True):
        st.switch_page("pages/dis_view.py")
with col3:
    if st.button("Reset", use_container_width=True):
        SessionManager.clear_selected_charts()
        st.rerun()
