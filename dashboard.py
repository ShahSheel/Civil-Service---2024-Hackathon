import streamlit as st
from streamlit_navigation_bar import st_navbar
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

st.set_page_config(page_title="EV Dashboard", layout="wide", initial_sidebar_state="expanded")

# Add GOV.UK CSS from the CDN
govuk_css_url = 'https://cdn.jsdelivr.net/npm/govuk-frontend@5.7.1/dist/govuk/govuk-frontend.min.css'
st.markdown(f'<link rel="stylesheet" href="{govuk_css_url}" type="text/css">', unsafe_allow_html=True)

st.markdown("""
    <style>
        /* Navbar style */
        .navbar {
        background-color: #000000; /* GOV.UK black */
            padding: 10px 20px;
            font-family: 'Arial', sans-serif;
            color: #ffffff;
            text-align: center;
            width: 100vw;  /* Full viewport width */
            position: relative;
            left: 50%;  /* Move it to the left */
            right: 50%;  /* Stretch it out to cover full width */
            margin-left: -50vw;  /* Adjust left margin to center */
            margin-right: -50vw;  /* Adjust right margin to center */
        }

        .navbar a {
            color: #ffffff;
            padding: 10px 20px;
            text-decoration: none;
            display: inline-block;
            font-weight: bold;
        }

        .navbar a:hover {
            background-color: #005ea5; /* GOV.UK blue on hover */
            border-radius: 4px;
        }

        /* GOV.UK header logo styling */
        .navbar .govuk-logo {
            display: inline-block;
            height: 30px;
            vertical-align: middle;
            margin-right: 20px;
        }

        .navbar .govuk-header__link {
            color: #ffffff;
        }
            
              /* Adjust the z-index of the sidebar and navbar */
        .css-1d391kg {
            z-index: 1;  /* Put sidebar behind the navigation bar */
        }
            
        /* Customize Plotly chart styling */
        .plotly-graph-div {
            max-width: 100%;
            margin: auto;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Add the GOV.UK-style navigation bar
st.markdown("""
    <div class="navbar">
        <div class="govuk-logo">
            <img src="img/govuk-apple-touch-icon.png" alt="GOV.UK Logo" style="height: 30px;">
        </div>
        <a href="#">Dashboard</a>
    </div>
""", unsafe_allow_html=True)


# Sidebar configuration
st.sidebar.title("Options")
checkbox_labels = ["EV", "Solar", "Wind", "Heat Pumps"]
selected_options = []
for label in checkbox_labels:
    if label == "EV":
        if st.sidebar.checkbox(label, value=True):  # Set EV checkbox as checked
            selected_options.append(label)
    else:
        if st.sidebar.checkbox(label):
            selected_options.append(label)

st.sidebar.markdown("---")

st.title("Electric Vehicle Dashboard with Real-Time Data")

# Add custom CSS for full-width layout and GOV.UK header/footer
st.markdown("""
    <style>
        /* Full-width header and footer */

        /* Plotly graph styling to make it responsive */
        .plotly-graph-div {
            max-width: 100%;
            margin: auto;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Load and filter data from CSV
def load_csv_data(filepath):
    try:
        # Load the CSV and select only the relevant columns
        data = pd.read_csv(filepath, usecols=["datetime", "TSD", "DSR_EV"], parse_dates=["datetime"])
        
        # Rename 'TSD' to 'demand' for consistency, if needed
        return data.rename(columns={"TSD": "demand"})[["datetime", "demand", "DSR_EV"]]
    except Exception as e:
        st.error(f"Error loading CSV data: {e}")
        return pd.DataFrame({"datetime": [], "demand": [], "DSR_EV": []})

# Fetch data
csv_data = load_csv_data("csv/forecasted_demand.csv")

# Main content
st.subheader("Timeseries Graph")

# Use only the CSV data for plotting
if not csv_data.empty:
  
    fig = go.Figure()

    # Add trace for the CSV demand data
    fig.add_trace(go.Scatter(x=csv_data["datetime"], y=csv_data["demand"], 
                            mode='lines', name='Demand (MW)', line=dict(color='#005EA5')))  # GOV.UK blue

    # Use 'DSR_EV' directly instead of calculating the ±10% range
    fig.add_trace(go.Scatter(x=csv_data["datetime"], y=csv_data["demand"] - csv_data["DSR_EV"], 
                            mode='lines', name='EV Underlying Demand', line=dict(color='#007F3B', width=2)))  # Solid green line for DSR_EV

    # Update layout
    fig.update_layout(
        title="Timeseries Data Visualization",
        xaxis_title="Datetime",
        yaxis_title="Demand",
        legend_title="Legend",
        template="plotly_white",  # White background for the chart
        font=dict(family="Arial, sans-serif", size=14),
        margin=dict(l=40, r=40, t=40, b=40)  # Ensure good margin around the chart
    )

    # Render the Plotly chart
    st.plotly_chart(fig, use_container_width=True)

    time_period = st.radio(
        "Select Time Period",
        ("Daily", "Monthly"),
        index=0,  # Default to "Daily"
        horizontal=True
    )

    # Ensure the 'datetime' column is set as an index for resampling
    csv_data.set_index("datetime", inplace=True)

    # Resample the data based on the selected time period
    if time_period == "Daily":
        resampled_data = csv_data.resample("D").mean().reset_index()
    else:
        resampled_data = csv_data.resample("M").mean().reset_index()

    # Reset the index for proper plotting
    csv_data.reset_index(inplace=True)

    # Bar chart for the selected time period
    bar_fig = go.Figure()

    # Calculate components of the demand (arbitrary percentages for demonstration)
    resampled_data['component1'] = resampled_data['demand'] * 0.6  # 60% of the demand
    resampled_data['component2'] = resampled_data['demand'] * 0.4  # 40% of the demand

    # Add the first component to the bar chart
    bar_fig.add_trace(go.Bar(
        x=resampled_data["datetime"],
        y=resampled_data["component1"],
        name="Component 1",
        marker_color="#007F3B"  # GOV.UK green
    ))

    # Add the second component on top of the first
    bar_fig.add_trace(go.Bar(
        x=resampled_data["datetime"],
        y=resampled_data["component2"],
        name="Component 2",
        marker_color="#005EA5"  # GOV.UK blue
    ))

    # Update layout for the bar chart
    bar_fig.update_layout(
        title=f"{time_period} Average Demand",
        xaxis_title="Date",
        yaxis_title="Average Demand (MW)",
        legend_title="Legend",
        barmode='stack',  # Set the bar mode to stack
        font=dict(family="Arial, sans-serif", size=14),
        margin=dict(l=40, r=40, t=40, b=50)  # Ensure good margin around the chart
    )

    # Render the Plotly bar chart
    st.plotly_chart(bar_fig, use_container_width=True)

else:
    st.write("No data available in the CSV file.")


