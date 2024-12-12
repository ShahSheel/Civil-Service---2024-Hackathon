import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Streamlit page configuration
st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="expanded")

# Add custom CSS for styling
st.markdown("""
    <style>
        .govuk-tag {
            display: inline-block;
            padding: 4px 12px;
            background-color: #1d70b8;
            border-radius: 10px;
            font-weight: bold;
            color: #ffffff;
            margin-bottom: 15px;
        }
        .govuk-tag--flex {
            background-color: #ff4b4b;
            color: #ffffff;
        }
        .govuk-tag--non-flex {
            background-color: #ff4b4b;
            color: #ffffff;
        }
         .date-picker-container {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: flex-start;
        }
            
        .tag-container {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 20px;
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
        # Read the CSV file, including the new columns
        data = pd.read_csv(
            filepath,
            usecols=["datetime", "TSD", "DSR_EV_LOWER", "DSR_EV_MID", "DSR_EV_UPPER"],
            parse_dates=["datetime"]
        )
        # Rename and return the required columns
        return data.rename(columns={"TSD": "demand"})
    except Exception as e:
        st.error(f"Error loading CSV data: {e}")
        # Return an empty DataFrame if there's an error
        return pd.DataFrame(columns=["datetime", "demand", "DSR_EV_LOWER", "DSR_EV_MID", "DSR_EV_UPPER"])

# Fetch data from CSV
csv_data = load_csv_data("csv/forecasted_demand (1).csv")

# Display a subheader for the graph
st.subheader("Timeseries Graph")

# Layout for date inputs
col1, col2 = st.columns([1, 3])  # Left column takes 1/4 space, right column takes 3/4 space

# Place the date inputs in the left column (col1)
with col1:
    start_date = st.date_input("Start Date", value=csv_data["datetime"].min().date())
    end_date = st.date_input("End Date", value=csv_data["datetime"].max().date())
    toggle_option = st.radio("Select Flexibility", ("Non-Flex", "Flex"), index=0)

# Filter the data based on the selected date range
filtered_data = csv_data[(csv_data["datetime"].dt.date >= start_date) & (csv_data["datetime"].dt.date <= end_date)]

# Plot timeseries graph if data is available
if not filtered_data.empty:
    with col2:
        # Display a tag based on toggle option
        st.markdown(f'<div class="tag-container"><span class="govuk-tag {"govuk-tag--flex" if toggle_option == "FLEX" else "govuk-tag--non-flex"}">{toggle_option}</span></div>', unsafe_allow_html=True)
        # Create the figure for demand and EV data with new columns
        fig = go.Figure()

        # Add existing demand and EV underlying demand traces
        fig.add_trace(go.Scatter(x=filtered_data["datetime"], y=filtered_data["demand"], mode='lines', name='Demand (MW)', line=dict(color='#005EA5')))

        # Add new traces for DSR_EV_LOWER, DSR_EV_MID, and DSR_EV_UPPER
        fig.add_trace(go.Scatter(x=filtered_data["datetime"], y=filtered_data["demand"] - filtered_data["DSR_EV_LOWER"], mode='lines', name='DSR EV Lower', line=dict(color='#FFA07A', dash='dash')))
        fig.add_trace(go.Scatter(x=filtered_data["datetime"], y=filtered_data["demand"] - filtered_data["DSR_EV_MID"], mode='lines', name='DSR EV Mid', line=dict(color='#FF6347')))
        fig.add_trace(go.Scatter(x=filtered_data["datetime"], y=filtered_data["demand"]- filtered_data["DSR_EV_UPPER"], mode='lines', name='DSR EV Upper', line=dict(color='#FF4500', dash='dot')))

        # Update layout for the timeseries graph with range slider and selector
        fig.update_layout(
            xaxis_title="Datetime",
            yaxis_title="Underlying Demand (MW)",
            legend_title="Legend",
            template="plotly_white",
            font=dict(family="Arial, sans-serif", size=14),
            margin=dict(l=40, r=40, t=40, b=40),
            autosize=True,
            xaxis=dict(
                rangeslider=dict(visible=True, bgcolor='rgba(0, 0, 0, 0.1)'),
                type="date",
                tickformat= "%Y-%m-%d %H:%M",
                showgrid=True
            )
        )

        # Plot the chart with the draggable time scale
        st.plotly_chart(fig, use_container_width=True)
else:
    st.write("No data available in the selected date range.")
