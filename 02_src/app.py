import streamlit as st
import pandas as pd
from logic import analyze_inventory_portfolio

# 1. Page Configuration
st.set_page_config(page_title="Supply Shock Matrix", page_icon="📦", layout="wide")

# 2. Main Header
st.title("📦 Module 2: Portfolio Risk Analysis")
st.markdown("Diagnose systemic logistical impact across an entire supply chain portfolio.")
st.divider()

# 3. Sidebar - Data Ingestion Placeholder
st.sidebar.header("Data Ingestion")
st.sidebar.info("Upload your current inventory snapshot to run the resilience matrix.")

uploaded_file = st.sidebar.file_uploader("Upload Inventory CSV", type=['csv'])

# 4. Load the Dataset (Dynamic Logic)
# If the user uploads a file, pandas reads it instantly.
if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ Custom dataset loaded successfully!")
else:
    # If no file is uploaded, we provide our mock corporate dataset so the page isn't blank
    st.sidebar.info("Notice: Engine is currently running in Demo Mode. Please upload a client inventory CSV to begin live risk diagnostics.")
    mock_dataset = {
        'SKU': ['Microchips', 'Steel Chassis', 'Lithium Batteries', 'Rubber Tires', 'Glass Windshields'],
        'Current Stock': [10000, 500, 2000, 8000, 1500],
        'Daily Consumption': [500, 50, 150, 400, 100],
        'Production Time': [20, 10, 25, 5, 12],
        'Transit Time': [15, 5, 20, 10, 8],
        'Risk Buffer': [5, 2, 7, 3, 4]
    }
    df_raw = pd.DataFrame(mock_dataset)

st.markdown("### 1. Raw Inventory Feed")
st.dataframe(df_raw, use_container_width=True)

# 5. Connect to the Backend Engine (logic.py)
processed_portfolio = analyze_inventory_portfolio(df_raw)

st.divider()
st.markdown("### 📊 2. Risk Diagnostics Output")

# 6. Apply Visual Formatting for the Executive View
def highlight_risk(val):
    """Applies color coding based on risk severity."""
    if val == 'CRITICAL':
        return 'background-color: rgba(255, 75, 75, 0.2)' # Light Red
    elif val == 'WARNING':
        return 'background-color: rgba(255, 164, 33, 0.2)' # Light Yellow
    elif val == 'SAFE':
        return 'background-color: rgba(0, 192, 75, 0.2)' # Light Green
    return ''

# Display the final styled dataframe
st.dataframe(
    processed_portfolio.style.map(highlight_risk, subset=['Risk Status']), 
    use_container_width=True
)