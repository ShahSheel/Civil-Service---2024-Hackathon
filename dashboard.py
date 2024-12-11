import streamlit as st
from streamlit_navigation_bar import st_navbar
import pandas as pd
import plotly.graph_objects as go

# Streamlit page configuration
st.set_page_config(page_title="EV Dashboard", layout="wide", initial_sidebar_state="expanded")

# Add GOV.UK CSS from CDN
govuk_css_url = 'https://cdn.jsdelivr.net/npm/govuk-frontend@5.7.1/dist/govuk/govuk-frontend.min.css'
st.markdown(f'<link rel="stylesheet" href="{govuk_css_url}" type="text/css">', unsafe_allow_html=True)

# Add custom CSS for styling
st.markdown("""
    <style>
        /* Plotly chart styling */
        .plotly-graph-div {
            max-width: 100%;
            margin: auto;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.title("Options")
checkbox_labels = ["EV", "Solar", "Wind", "Heat Pumps"]
selected_options = [label for label in checkbox_labels if st.sidebar.checkbox(label, value=(label == "EV"))]
st.sidebar.markdown("---")

st.header("Dashboard")
# Load CSV data
def load_csv_data(filepath):
    try:
        data = pd.read_csv(filepath, usecols=["datetime", "TSD", "DSR_EV"], parse_dates=["datetime"])
        return data.rename(columns={"TSD": "demand"})[["datetime", "demand", "DSR_EV"]]
    except Exception as e:
        st.error(f"Error loading CSV data: {e}")
        return pd.DataFrame({"datetime": [], "demand": [], "DSR_EV": []})

# Fetch data from CSV
csv_data = load_csv_data("csv/forecasted_demand.csv")

# Plot timeseries graph if data is available
if not csv_data.empty:
    st.subheader("Timeseries Graph")

    # Create the figure for demand and EV underlying demand
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=csv_data["datetime"], y=csv_data["demand"], mode='lines', name='Demand (MW)', line=dict(color='#005EA5')))
    fig.add_trace(go.Scatter(x=csv_data["datetime"], y=csv_data["demand"] - csv_data["DSR_EV"], mode='lines', name='EV Underlying Demand', line=dict(color='#007F3B', width=2)))

    # Update layout for the timeseries graph
    fig.update_layout(
        title="Timeseries Data Visualization",
        xaxis_title="Datetime",
        yaxis_title="Demand (MW)",
        legend_title="Legend",
        template="plotly_white",
        font=dict(family="Arial, sans-serif", size=14),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Time period selection for resampling
    time_period = st.radio("Select Time Period", ("Daily", "Monthly"), index=0, horizontal=True)

    # Resample data based on selected time period
    csv_data.set_index("datetime", inplace=True)
    resampled_data = csv_data.resample("D" if time_period == "Daily" else "M").mean().reset_index()
    csv_data.reset_index(inplace=True)

    # Create the bar chart for the resampled data
    bar_fig = go.Figure()
    resampled_data['component1'] = resampled_data['demand'] * 0.6  # 60% of the demand
    resampled_data['component2'] = resampled_data['demand'] * 0.4  # 40% of the demand
    bar_fig.add_trace(go.Bar(x=resampled_data["datetime"], y=resampled_data["component1"], name="Component 1", marker_color="#007F3B"))
    bar_fig.add_trace(go.Bar(x=resampled_data["datetime"], y=resampled_data["component2"], name="Component 2", marker_color="#005EA5"))

    # Update layout for the bar chart
    bar_fig.update_layout(
        title=f"{time_period} Average Demand",
        xaxis_title="Date",
        yaxis_title="Average Demand (MW)",
        legend_title="Legend",
        barmode='stack',
        font=dict(family="Arial, sans-serif", size=14),
        margin=dict(l=40, r=40, t=40, b=50)
    )
    st.plotly_chart(bar_fig, use_container_width=True)

else:
    st.write("No data available in the CSV file.")
