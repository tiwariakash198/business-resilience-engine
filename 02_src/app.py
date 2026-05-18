from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import logic
from outbound_logic import evaluate_outbound_resilience

# --- PAGE SETUP ---
st.set_page_config(page_title="Supply Chain Resilience Engine", layout="wide")
st.title("📦 Supply Chain Resilience Engine")
st.markdown("Evaluating Logistics Risk & Financial Mitigation Strategies.")

# --- 1. DATA INPUT & UX ONBOARDING ---
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

st.markdown("---")
st.header("📦 Phase 4: Outbound Revenue Defense Engine")
st.write("Simulate fulfillment latency, dynamic stockout thresholds, and evaluate SLA penalties vs. client retention trade-offs.")

col_inputs, col_outputs = st.columns([1.2, 1.8])

# ==========================================
# LEFT COLUMN: INPUTS
# ==========================================
with col_inputs:
    st.subheader("1. Logistics & SLA Stress")
    standard_delay = st.slider("Projected Standard Ocean Delay (Days)", min_value=1, max_value=60, value=35)
    order_val = st.number_input("Current Order Value (USD)", value=40000, step=5000)
    std_freight = st.number_input("Standard Carrier Freight (USD)", value=3500, step=500)
    
    st.markdown("##### ✈️ Mitigation Strategy")
    prem_freight = st.number_input("Expedited Air Premium (USD)", value=15000, step=1000)
    
    max_savable = standard_delay - 1 if standard_delay > 1 else 0
    days_saved = st.slider(
        "Days Saved by Premium Freight", min_value=0, max_value=max_savable, value=min(27, max_savable),
        help="How many days of transit time are you buying back by paying the premium?"
    )
    premium_delay = standard_delay - days_saved
    
    st.markdown("---")
    daily_penalty = st.number_input("Contractual Daily SLA Penalty (USD)", value=1000, step=100)
    
    st.markdown("---")
    st.subheader("2. Operational Runway")
    buf_days = st.slider("Client Buffer Stock Reserves (Days)", min_value=0, max_value=30, value=12)
    grace_days = st.slider("Contractual Grace Period (Days)", min_value=0, max_value=10, value=3)
    
    threshold_cliff = buf_days + grace_days
    
    st.markdown("---")
    st.subheader("3. Strategic Pivot Parameters")
    
    # === CASCADING UI LOGIC ===
    if standard_delay <= threshold_cliff:
        st.info(f"💡 **Operational Safety:** Standard delay ({standard_delay} days) is within the client's runway ({threshold_cliff} days). Strategic parameters inactive.")
        ann_clv = 300000; friction = 0.15; alt_mkt_val = 32000
        
    else:
        st.warning(f"⚠️ **Standard Baseline Breached!** Doing nothing results in a stockout. Evaluate CLV exposure:")
        ann_clv = st.number_input("Annualized Account CLV (USD)", value=300000, step=25000, help="The total yearly revenue expected from this client relationship. Used to calculate potential churn exposure in a stockout scenario.")
        
        if premium_delay <= threshold_cliff:
            st.success(f"✨ **Mitigation Viable!** Premium freight reduces delay to {premium_delay} days, preventing stockout. Pivot disabled.")
            friction = 0.15; alt_mkt_val = 0.0
        else:
            st.error(f"🚨 **Mitigation Fails!** Premium freight still results in a {premium_delay - threshold_cliff}-day stockout. Evaluate Pivot:")
            friction = st.slider("Client Switching Friction (CSF)", min_value=0.0, max_value=1.0, value=0.15)
            st.info("📊 **CSF:** 0.0 (High Flight Risk) to 1.0 (Captive Client)")
            alt_mkt_val = st.number_input("Alternative Client/Market Demand (USD)", value=32000, step=2000)

# ==========================================
# ENGINE EXECUTION
# ==========================================
result = evaluate_outbound_resilience(
    order_value=order_val, annualized_clv=ann_clv, standard_freight=std_freight, premium_freight=prem_freight,
    standard_delay_days=standard_delay, premium_delay_days=premium_delay, daily_sla_penalty=daily_penalty,
    client_buffer_days=buf_days, grace_period_days=grace_days, switching_friction=friction, alt_market_recovery=alt_mkt_val
)

# ==========================================
# RIGHT COLUMN: OUTPUTS
# ==========================================
with col_outputs:
    st.subheader("Rescue Decision Desk")
    if "horizon" in result:
        st.caption(f"**Operational Status:** `{result['horizon']}`")
        
    if result["color"] == "success": st.success(f"### 🟢 {result['action']}")
    elif result["color"] == "warning": st.warning(f"### 🟡 {result['action']}")
    else: st.error(f"### 🔴 {result['action']}")
        
    st.markdown(f"**Strategic Rationale:** {result['rationale']}")
    st.markdown("#### Impact & Financial Exposure")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Incurred Premium", f"USD {result['freight_premium']:,.2f}", help="Freight premium actually spent based on the final decision.")
    m2.metric("Capital at Risk", f"USD {result['value_at_risk']:,.2f}")
    m3.metric("Net Preserved Value", f"USD {abs(result['net_benefit']):,.2f}", delta=float(result['net_benefit']))
    
    st.markdown("---")
    st.markdown("#### Elasticity Telemetry")
    d1, d2, d3 = st.columns(3)
    d1.metric("Calculated Churn Risk", f"{result['calculated_churn'] * 100:.1f}%")
    d2.metric("Stockout Cliff", f"{result['threshold_days']} Days", help="The point at which the client runs out of buffer stock and experiences a service disruption.")
    
    if "PIVOT" in result["action"]:
        d3.metric("Alternative Yield", f"USD {alt_mkt_val:,.2f}")
    else:
        d3.metric("Residual SLA Fines", f"USD {result.get('residual_penalty', 0.0):,.2f}", help="The remaining SLA penalties after considering all mitigations.")