import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Streamlit page configuration
st.set_page_config(page_title="EV Dashboard", layout="wide", initial_sidebar_state="expanded")

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
        
       .govuk-tag {
            display: inline-block;
            padding: 4px 12px;
            background-color: #1d70b8;
            border-radius: 10px;
            font-weight: bold;
            color: #fffff;
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
        data = pd.read_csv(filepath, usecols=["datetime", "TSD", "DSR_EV"], parse_dates=["datetime"])
        return data.rename(columns={"TSD": "demand"})[["datetime", "demand", "DSR_EV"]]
    except Exception as e:
        st.error(f"Error loading CSV data: {e}")
        return pd.DataFrame({"datetime": [], "demand": [], "DSR_EV": []})

# Fetch data from CSV
csv_data = load_csv_data("csv/forecasted_demand.csv")
st.subheader("Timeseries Graph")



col1, col2 = st.columns([1, 3])  # Left column takes 1/4 space, right column takes 3/4 space

# Place the date inputs in the left column (col1)
with col1:
    start_date = st.date_input("Start Date", value=csv_data["datetime"].min().date())
    end_date = st.date_input("End Date", value=csv_data["datetime"].max().date())
    toggle_option = st.radio("Select Flexibility", ("Non-Flex", "Flex"), index=0)




# Filter the data based on the selected date range
filtered_data = csv_data[(csv_data["datetime"].dt.date >= start_date) & (csv_data["datetime"].dt.date <= end_date)]


# Plot timeseries graph if data is available
if not csv_data.empty:
    with col2:
        st.markdown(f'<div class="tag-container"><span class="govuk-tag {"govuk-tag--flex" if toggle_option == "FLEX" else "govuk-tag--non-flex"}">{toggle_option}</span></div>', unsafe_allow_html=True)

        # Create the figure for demand and EV underlying demand
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=filtered_data["datetime"], y=filtered_data["demand"], mode='lines', name='Demand (MW)', line=dict(color='#005EA5')))
        fig.add_trace(go.Scatter(x=filtered_data["datetime"], y=filtered_data["demand"] - filtered_data["DSR_EV"], mode='lines', name='EV Underlying Demand', line=dict(color='#007F3B', width=2)))

        # Update layout for the timeseries graph with range slider and selector
        fig.update_layout(
            # title="Timeseries Data Visualization",
            xaxis_title="Datetime",
            yaxis_title="Demand (MW)",
            legend_title="Legend",
            template="plotly_white",
            font=dict(family="Arial, sans-serif", size=14),
            margin=dict(l=40, r=40, t=40, b=40),
            autosize=True,
            xaxis=dict(
                rangeslider=dict(visible=True, bgcolor='rgba(0, 0, 0, 0.1)'),  # Semi-transparent background for range slider
                type="date",  # Date type axis
                tickformat="%b %d, %Y",  # Format the ticks
                showgrid=True
            )
        )
        
        # Plot the chart with the draggable time scale
        st.plotly_chart(fig, use_container_width=True)


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
    
    # Plot the bar chart
    st.plotly_chart(bar_fig, use_container_width=True)



else:
    st.write("No data available in the CSV file.")
