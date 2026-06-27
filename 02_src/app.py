from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import logic
import outbound_logic as obl

# --- PAGE SETUP ---
st.set_page_config(page_title="Supply Chain Resilience Engine", layout="wide")

# --- GLOBAL STICKY HEADER ---
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    div.element-container:has(#custom-sticky-header) {
        position: sticky;
        top: 0;
        z-index: 999;
        background-color: #0E1117; 
        padding-top: 1rem;
        padding-bottom: 2rem; /* Doubled the padding to push the line down */
        border-bottom: 1px solid #333;
    }
    </style>

    <div id="custom-sticky-header">
        <h1 style="margin: 0; padding-bottom: 5px;">📦 Supply Chain Resilience Engine</h1>
        <p style="margin: 0; color: #a5a5a5;">Evaluating Logistics Risk & Financial Mitigation Strategies.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 1. ARCHITECTURE NAVIGATION (Top Level) ---
st.sidebar.header("🧭 Architecture Navigation")
analytics_mode = st.sidebar.radio(
    "Select Analytics Engine:",
    ["Inbound Supply Operations", "Outbound Revenue Defense"]
)

st.sidebar.divider()

# --- 2. DATA INPUT & UX ONBOARDING ---
st.sidebar.header("📁 Data Input Pipeline")

# Dual-Option Ingestion Selector
data_source = st.sidebar.radio(
    "Select Data Source:",
    ("Use Sample Inventory Baseline", "Upload Custom Enterprise CSV")
)

raw_df = None

if data_source == "Use Sample Inventory Baseline":
    target_csv_path = "Unknown absolute path" 
    
    try:
        # 2. Resolve the absolute Windows path using the correct Path object
        current_dir = Path(__file__).resolve().parent
        target_csv_path = current_dir.parent / "01_data" / "sample_inventory.csv"
        
        # 3. Ingest natively
        raw_df = pd.read_csv(target_csv_path)
        st.sidebar.info("💡 Staging Mode: Loaded sample baseline natively.")
        
    except Exception as e:
        # Now safely prints the exact path if the file is missing
        st.error(f"⚠️ Baseline CSV not found. Windows searched at:\n`{target_csv_path}`\n\n**System Error:** {e}")
        st.stop()
else:
    # Mode B: Renders the custom file dropzone cleanly
    uploaded_file = st.sidebar.file_uploader("Upload Enterprise CSV", type=['csv'])
    
    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            st.sidebar.success("Enterprise CSV Ingested Successfully!")
        except Exception as e:
            st.error(f"Error reading the CSV file: {e}. Please ensure it is a valid 7-column layout.")
            st.stop()
    else:
        # Crucial Guardrail: Prevents downstream calculation errors when dropzone is empty
        st.info("👋 Welcome to the Resilience Engine. Please upload your enterprise inventory data in the sidebar, or switch back to the Sample Baseline to explore.")
        st.stop()

st.sidebar.divider()

if analytics_mode == "Inbound Supply Operations":
    st.subheader("🛡️ Inbound Supply Operations")
    st.markdown("Evaluating Logistics Risk & Financial Mitigation Strategies.")
    st.divider()

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

# --- 7. CARRYING COST CALCULATOR & SENSITIVITY MATRIX ---
    st.divider()

# The explicit toggle-in choice to access the TCO module and sensitivity matrix
    activate_tco_module = st.toggle(
    "SKU Carrying Cost & Breakeven Analysis",
    value=False,
    help="Toggle ON to unlock custom inventory carrying overhead models and lean vs. buffer breakeven analytics."
)

    if activate_tco_module:
        st.subheader("Inventory Carrying Cost Rate Calculator")
        st.markdown("Input your baseline operational expenses to derive your auditable annual holding percentage.")

    # 1. Safely locate your active dataframe
    active_df = None
    for var_name in ['df', 'my_dataframe', 'inventory_df', 'data', 'raw_df']:
        if var_name in locals() and locals()[var_name] is not None:
            active_df = locals()[var_name]
            break

    # Calculate CSV Baseline Safely
    csv_total_value = 0.0
    if active_df is not None:
        try:
            valid_rows = active_df[
                (active_df['Current Stock'].astype(str).str.lower() != 'not provided') & 
                (active_df['Regular Unit Cost'].astype(str).str.lower() != 'not provided')
            ]
            csv_total_value = (valid_rows['Current Stock'].astype(float) * valid_rows['Regular Unit Cost'].astype(float)).sum()
        except Exception:
            csv_total_value = 0.0

    st.markdown("##### 📦 Warehouse Baseline Valuation")
    
    baseline_option = st.radio(
        "Select Inventory Valuation Basis:",
        options=["Auto-Calculate from Uploaded CSV", "Override with Total Facility Baseline"],
        index=0,
        horizontal=True
    )

    if baseline_option == "Auto-Calculate from Uploaded CSV" and active_df is not None:
        st.info(f"Using uploaded dataset baseline: **${csv_total_value:,.2f}**")
        total_inv_value = csv_total_value
        if total_inv_value == 0:
            st.warning("Uploaded CSV yielded $0 valuation. Please use the Override option below.")
    else:
        total_inv_value = st.number_input(
            "Total Facility Inventory Baseline ($)", 
            min_value=0.0, 
            value=1000000.0, 
            step=50000.0,
            help="The total average dollar value of all stock sitting across your entire facility."
        )

    st.markdown("##### 💸 Granular Annual Overhead Spend")
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    
    with col_c1:
        st.markdown("**1. Capital Cost**")
        wacc_val = st.number_input("Corporate WACC (%)", min_value=0.0, max_value=40.0, value=10.0, step=0.5,
                                   help="Weighted Average Cost of Capital (Opportunity cost of tied-up cash).")
    
    with col_c2:
        st.markdown("**2. Storage Overhead**")
        rent_val = st.number_input("Annual Rent & Utilities ($)", min_value=0.0, value=50000.0, step=5000.0)
        labor_val = st.number_input("Warehouse Labor & Sec. ($)", min_value=0.0, value=40000.0, step=5000.0)
        
    with col_c3:
        st.markdown("**3. Service Overhead**")
        ins_val = st.number_input("Annual Insurance Premium ($)", min_value=0.0, value=15000.0, step=1000.0)
        tax_val = st.number_input("Localized Inventory Taxes ($)", min_value=0.0, value=5000.0, step=1000.0)
        
    with col_c4:
        st.markdown("**4. Risk Exposure**")
        shrink_val = st.number_input("Est. Annual Shrinkage ($)", min_value=0.0, value=10000.0, step=1000.0, help="Loss via theft, damage, or misplacement.")
        scrap_val = st.number_input("Scrap & Obsolescence ($)", min_value=0.0, value=20000.0, step=2000.0, help="Written-off inventory that expired or rusted.")

    tco_results = logic.calculate_carrying_cost_rate(
        total_inv_value, wacc_val, rent_val, labor_val, ins_val, tax_val, shrink_val, scrap_val
    )

    if tco_results.get("error"):
        st.error(tco_results["error"])
        custom_rate = 0.0
    else:
        custom_rate = tco_results["rate_pct"]
        st.success(f"### 📊 Derived Annual Holding Rate: {custom_rate}%")
        st.caption(f"Total Facility Overhead Spend: **${tco_results['total_dollars']:,.2f}** per year.")

    # --- MODULE 2: SENSITIVITY MATRIX & TRADE-OFF ---
    if custom_rate > 0 and 'sim_results' in locals() and active_df is not None:
        st.subheader("⚖️ Holding Overhead vs. Emergency Mitigation Breakeven")
        st.markdown("Select a specific SKU from your dataset to evaluate its storage vs. expedite trade-off:")
        
        clean_sku_df = active_df[
            (active_df['Current Stock'].astype(str).str.lower() != 'not provided') & 
            (active_df['Regular Unit Cost'].astype(str).str.lower() != 'not provided')
        ]
        
        if not clean_sku_df.empty:
            sku_list = clean_sku_df['SKU'].tolist()
            selected_sku_id = st.selectbox("🎯 Select Target SKU for Breakeven Analysis:", options=sku_list)
            
            active_row = clean_sku_df[clean_sku_df['SKU'] == selected_sku_id].iloc[0]
            
            current_stock_val = float(active_row['Current Stock'])
            unit_cost_val = float(active_row['Regular Unit Cost'])
            
            sku_annual_overhead = logic.calculate_sku_holding_cost(current_stock_val, unit_cost_val, custom_rate)
            mitigation_cost_dollars = sim_results['Mitigation Cost']   # From your P2 emergency simulator
            
            delta_val, rec_text, tag = logic.evaluate_breakeven_delta(sku_annual_overhead, mitigation_cost_dollars)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric(f"SKU ({selected_sku_id}) Annual Overhead", f"${sku_annual_overhead:,.2f}")
            with col_m2:
                st.metric("Emergency Expedite Premium", f"${mitigation_cost_dollars:,.2f}")
            with col_m3:
                if tag == "LEAN_FAVORED":
                    st.metric("Breakeven Delta", f"${delta_val:,.2f}", delta="Cheaper to Expedite")
                else:
                    st.metric("Breakeven Delta", f"${delta_val:,.2f}", delta="-Cheaper to Hold Buffer", delta_color="inverse")
                    
            st.info(f"**Executive Action Receipt:** {rec_text}")
        else:
            st.warning("No valid numeric SKU rows available to run the sensitivity matrix.")


# --- 8. OUTBOUND REVENUE DEFENSE ENGINE ---

elif analytics_mode == "Outbound Revenue Defense":
    st.subheader("🚀 Outbound Revenue Defense")
    st.markdown("Evaluating Logistics Escalation, Financial Exposure, and Mitigation Viability.")
    st.divider()

# --- PAGE SETUP ---
    st.set_page_config(page_title="Outbound Resilience Engine", layout="wide")

# --- DUAL-COLUMN ARCHITECTURE ---
# Left column takes 30% of the screen, Right column takes 70%
    col_inputs, col_outputs = st.columns([3, 7], gap="large")

# ==========================================
#        LEFT COLUMN: INPUT PARAMETERS
# ==========================================
    with col_inputs:
        st.subheader("⚙️ Scenario Configurations")
    
    with st.expander("1. Core Financials", expanded=True):
        order_value = st.number_input("Order Value ($)", value=40000, step=1000)
        clv = st.number_input("Total Account CLV ($)", value=300000, step=10000)
        daily_penalty = st.number_input("Daily SLA Penalty ($)", value=1000, step=100)
        
    with st.expander("2. Timeline & Mitigation", expanded=True):
        buffer_days = st.number_input("Client Buffer (Days)", value=10, step=1)
        grace_period = st.number_input("SLA Grace Period (Days)", value=3, step=1)
        std_delay = st.number_input("Standard Delay (Days)", value=35, step=1)
        days_saved = st.number_input("Days Saved (by Premium Freight)", value=23, step=1)
        
    with st.expander("3. Freight & Thresholds", expanded=True):
        standard_freight = st.number_input("Standard Freight Cost ($)", value=5000, step=500)
        premium_freight = st.number_input("Premium Freight Cost ($)", value=20000, step=1000)
        user_mam = st.slider("Minimum Acceptable Margin (MAM)", 0.0, 0.50, 0.05, 0.01)

# --- Data Translation for Backend ---
    derived_premium_delay = max(0, std_delay - days_saved)
    derived_premium_upgrade = max(0, premium_freight - standard_freight)

# --- Execute Backend Engine ---
    freight_results = obl.evaluate_freight_strategy(
    order_value, clv, std_delay, derived_premium_delay, 
    grace_period, buffer_days, daily_penalty, 
    standard_freight, derived_premium_upgrade
)

    viability = obl.evaluate_mitigation_viability(
    freight_results["premium"]["net_revenue"],
    freight_results["premium"]["margin"],
    freight_results["premium"]["churn_risk"],
    user_mam
)

# ==========================================
#        RIGHT COLUMN: THE DECISION DESK
# ==========================================
    with col_outputs:
    
    # --- ESCALATION PROTOCOL (PIVOT RECOMMENDATION) ---
        if viability["requires_escalation"]:
            reasons = []
            if viability["alerts"]["churn_critical"]: reasons.append("Critical Churn (>50%)")
            if viability["alerts"]["margin_breach"]: reasons.append(f"Margin Breach (<{user_mam*100:.0f}%)")
            if viability["alerts"]["absolute_loss"]: reasons.append("Absolute Financial Loss")
        
            st.error(f"⚠️ **CRITICAL LOGISTICS FAILURE DETECTED:** {', '.join(reasons)}. Logistical mitigation is mathematically unviable. **Strategic Pivot evaluation recommended.**")
        else:
            st.success("✅ **Logistics Strategy Viable:** Premium margin and churn risk are operating within acceptable corporate thresholds.")

    # --- DECISION RESCUE DESK: LOGISTICS DEFENSE ---
    st.subheader("Decision Rescue Desk: Operational Freight Defense")
    
    d1_col1, d1_col2, d1_col3 = st.columns(3)
    std = freight_results["standard"]
    prem = freight_results["premium"]

    with d1_col1:
        st.markdown("**Standard Operations**")
        st.metric("Total Delivery Cost", f"${std['delivery_cost']:,.0f}")
        st.metric("Net Earned Revenue", f"${std['net_revenue']:,.0f}")
        st.metric("Margin Retention", f"{std['margin']*100:.1f}%")
        st.metric("Account Churn Risk", f"{std['churn_risk']*100:.1f}%")

    with d1_col2:
        st.markdown("**Premium Freight Operations**")
        st.metric("Total Delivery Cost", f"${prem['delivery_cost']:,.0f}", delta=f"${prem['delivery_cost'] - std['delivery_cost']:,.0f}", delta_color="inverse")
        st.metric("Net Earned Revenue", f"${prem['net_revenue']:,.0f}", delta=f"${prem['net_revenue'] - std['net_revenue']:,.0f}")
        st.metric("Margin Retention", f"{prem['margin']*100:.1f}%", delta=f"{(prem['margin'] - std['margin'])*100:.1f}%")
        st.metric("Account Churn Risk", f"{prem['churn_risk']*100:.1f}%", delta=f"{(prem['churn_risk'] - std['churn_risk'])*100:.1f}%", delta_color="inverse")

    with d1_col3:
        st.markdown("**Mitigation Viability**")
        roi_color = "normal" if freight_results["roi"] >= 0 else "inverse"
        st.metric("Net Impact (ROI)", f"${freight_results['roi']:,.0f}", delta=f"${freight_results['roi']:,.0f}", delta_color=roi_color)
        
        break_even_days = derived_premium_upgrade / daily_penalty if daily_penalty > 0 else 0
        st.info(f"💡 **Break-Even Horizon:** The premium flight must save > {break_even_days:.1f} days to mathematically pay for the ${derived_premium_upgrade:,.0f} cost difference.")