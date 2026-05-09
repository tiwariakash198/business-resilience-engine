import streamlit as st
import pandas as pd
import logic  # Importing your backend engine

# --- PAGE SETUP ---
st.set_page_config(page_title="Supply Chain Resilience Engine", layout="wide")
st.title("📦 Supply Chain Resilience Engine")
st.markdown("Evaluating Logistics Risk & Financial Mitigation Strategies.")

# --- 1. DATA INPUT & UX ONBOARDING ---
st.sidebar.header("📁 Data Input")
uploaded_file = st.sidebar.file_uploader("Upload file", type=['csv'])

# Define the Template Data
template_data = {
    'SKU': ['Example Part A', 'Example Part B', 'Example Part C'],
    'Current Stock': [5000, 1200, 800],
    'Daily Consumption': [200, 50, 100],
    'Total Lead Time': [45, 25, 65],
    'Regular Unit Cost': [150.0, 85.0, 250.0],
    'Alt Unit Cost': [250.0, 130.0, 350.0],
    'Sales Price': [1200.0, 550.0, 4500.0]
}
template_df = pd.DataFrame(template_data)

raw_df = None

# The "Empty State" (When no file is uploaded)
if uploaded_file is None:
    st.info("👋 Welcome to the Resilience Engine. Please upload your inventory data in the sidebar to begin.")
    
    st.subheader("📋 Required CSV Format")
    st.markdown("To run the financial diagnostics, your file must contain these exact 7 columns:")
    st.dataframe(template_df, use_container_width=True)
    
    # Provide a download button for the template
    csv_template = template_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Template CSV",
        data=csv_template,
        file_name='inventory_template.csv',
        mime='text/csv',
    )
else:
    # Load the actual file once uploaded
    try:
        raw_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading the CSV file: {e}. Please ensure it is a valid CSV.")

# --- 2. BACKEND PROCESSING & DASHBOARD ---
if raw_df is not None:
    # Sanitize the data and calculate baselines
    clean_df = logic.sanitize_inventory_data(raw_df)
    processed_df = logic.calculate_base_metrics(clean_df)

    # --- 3. DATA QUALITY UI ---
    if not processed_df['is_valid'].all():
        st.warning("⚠️ Some rows have missing or corrupted data and were excluded from financial calculations.")
        with st.expander("View Incomplete Data"):
            invalid_rows = processed_df[~processed_df['is_valid']][['SKU', 'Current Stock', 'Daily Consumption', 'Total Lead Time']]
            st.dataframe(invalid_rows)

        # --- 4. BASELINE DASHBOARD ---
    st.subheader("Current Logistics & Financial Exposure")

    display_df = processed_df.copy()        #-- We create a copy to avoid modifying the original processed_df when we format it for display.

   
    if 'is_valid' in display_df.columns:
        display_df.drop(columns=['is_valid'], inplace=True)

    # 2. Handle missing Raw Inputs
    input_cols = [
        'Current Stock', 'Daily Consumption', 'Total Lead Time', 
        'Regular Unit Cost', 'Alt Unit Cost', 'Sales Price'
    ]
    for col in input_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].fillna("Not provided")

    # 3. Handle missing Calculated Outputs
    if 'Inventory Runway' in display_df.columns:
        display_df['Inventory Runway'] = display_df['Inventory Runway'].apply(
            lambda x: f"{x:,.1f}" if pd.notnull(x) else "Insufficient info"
        )
        
    if 'Stoppage Gap' in display_df.columns:
        display_df['Stoppage Gap'] = display_df['Stoppage Gap'].apply(
            lambda x: f"{x:,.1f}" if pd.notnull(x) else "Insufficient info"
        )

    if 'Capital Locked ($)' in display_df.columns:
        display_df['Capital Locked ($)'] = display_df['Capital Locked ($)'].apply(
            lambda x: f"${x:,.2f}" if pd.notnull(x) else "Insufficient info"
        )
        
    if 'Baseline Loss ($)' in display_df.columns:
        display_df['Baseline Loss ($)'] = display_df['Baseline Loss ($)'].apply(
            lambda x: f"${x:,.2f}" if pd.notnull(x) else "Insufficient info"
        )

    # Highlight CRITICAL rows cleanly
    def highlight_risk(val):
        color = '#ff4b4b' if val == 'CRITICAL' else '#ffa421' if val == 'WARNING' else '#00c04b' if val == 'SAFE' else 'grey'
        return f'color: {color}'

    st.dataframe(display_df.style.map(highlight_risk, subset=['Risk Status']), use_container_width=True)

    # --- 5. THE MITIGATION SIMULATOR (SIDEBAR) ---
    st.sidebar.header("🛠️ Mitigation Simulator")
    st.sidebar.markdown("Test alternate supply scenarios for critical items.")

    # Filter to only show CRITICAL items in the dropdown
    critical_items = processed_df[processed_df['Risk Status'] == 'CRITICAL']['SKU'].tolist()

    if not critical_items:
        st.sidebar.success("No Critical SKUs detected. Operations are nominal.")
    else:
        selected_sku = st.sidebar.selectbox("Select Critical SKU to Rescue:", critical_items)
        
        st.sidebar.divider()
        
        # Sliders for "What-If" Analysis
        st.sidebar.markdown("**Alternate Supplier Terms:**")
        freight_premium = st.sidebar.slider("Emergency Freight Cost ($/unit)", min_value=0, max_value=500, value=100, step=10)
        tariff_pct = st.sidebar.slider("Tariff Exposure (%)", min_value=0, max_value=50, value=15, step=1)
        days_saved = st.sidebar.slider("Lead Time Saved (Days)", min_value=0, max_value=30, value=10, step=1)
        
        # --- 6. RUN SIMULATION & DISPLAY RESULTS ---
        # Get the row data for the selected SKU
        sku_data = processed_df[processed_df['SKU'] == selected_sku].iloc[0]
        
        st.markdown("---")
        st.subheader(f"Simulation Results: Rescuing {selected_sku}")
        
        # Run the calculator from logic.py
        sim_results = logic.simulate_mitigation_scenario(sku_data, freight_premium, tariff_pct, days_saved)
        
        # THE COST BREAKDOWN CALCULATOR
        with st.expander(f"🔍 View Landed Cost Breakdown for {selected_sku}"):
            tariff_cost = sku_data['Alt Unit Cost'] * (tariff_pct / 100)
            
            st.markdown(f"""
            **Regular Supplier:** ${sku_data['Regular Unit Cost']:,.2f} per unit
            
            **Emergency Supplier (Landed Cost): ${sim_results['Alt Landed Cost']:,.2f} per unit**
            * **Base Price:** ${sku_data['Alt Unit Cost']:,.2f}
            * **Freight Premium:** +${freight_premium:,.2f}
            * **Tariff Tax ({tariff_pct}%):** +${tariff_cost:,.2f}
            
            *Mitigation Cost represents the difference between Regular and Emergency Landed Cost, multiplied by the units needed during the stoppage gap.*
            """)
        
        st.write("") # Visual spacing
        
        # Display visually using columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Revenue Saved (Loss Avoided)", value=f"${sim_results['Revenue Saved']:,.2f}")
        with col2:
            st.metric(label="Cost to Mitigate (Premium)", value=f"${sim_results['Mitigation Cost']:,.2f}")
        with col3:
            # NPI Formatting
            npi = sim_results['Net Profit Impact']
            if npi > 0:
                st.metric(label="Net Profit Impact (NPI)", value=f"+${npi:,.2f}")
                st.success("**RECOMMENDED ACTION:** Expedite Supply. The revenue saved justifies the premium.")
            else:
                st.metric(label="Net Profit Impact (NPI)", value=f"${npi:,.2f}")
                st.error("**RECOMMENDED ACTION:** Halt Production. Expediting costs more than the lost revenue.")