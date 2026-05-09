import pandas as pd
import numpy as np

def sanitize_inventory_data(df):
    """
    Module 1: Cleans data and forces numeric types to prevent app crashes.
    """
    clean_df = df.copy()
    
    # Force numeric types (turns bad strings into NaN)
    numeric_cols = [
        'Current Stock', 'Daily Consumption', 'Total Lead Time', 
        'Regular Unit Cost', 'Alt Unit Cost', 'Sales Price'
    ]
    
    for col in numeric_cols:
        if col in clean_df.columns:
            clean_df[col] = pd.to_numeric(clean_df[col], errors='coerce')

    # Identify rows missing math-critical columns
    critical_cols = ['Current Stock', 'Daily Consumption', 'Total Lead Time']
    if all(col in clean_df.columns for col in critical_cols):
        clean_df['is_valid'] = clean_df[critical_cols].notnull().all(axis=1)
    else:
        clean_df['is_valid'] = False
        
    return clean_df

def calculate_base_metrics(df):
    """
    Module 2: Calculates Logistics Risk and Static Financial Exposure.
    """
    if df.empty or not df['is_valid'].any():
        return df

    valid = df['is_valid'] == True
    
    # --- LOGISTICS CALCULATIONS ---
    df.loc[valid, 'Inventory Runway'] = df.loc[valid, 'Current Stock'] / df.loc[valid, 'Daily Consumption']
    df.loc[valid, 'Stoppage Gap'] = df.loc[valid, 'Total Lead Time'] - df.loc[valid, 'Inventory Runway']

    # Assign Risk Status
    conditions = [
        (~df['is_valid']),
        (df['Stoppage Gap'] > 0),
        (df['Stoppage Gap'] > -5) & (df['Stoppage Gap'] <= 0)
    ]
    choices = ['⚠️ INCOMPLETE', 'CRITICAL', 'WARNING']
    df['Risk Status'] = np.select(conditions, choices, default='SAFE')
    
    # --- FINANCIAL BASELINE CALCULATIONS ---
    # 1. Capital Locked (Money stuck in warehouse)
    df.loc[valid, 'Capital Locked ($)'] = df.loc[valid, 'Current Stock'] * df.loc[valid, 'Regular Unit Cost']
    
    # 2. Baseline Loss (Revenue lost during stoppage gap)
    # We clip to 0 so we don't show "negative loss" for SAFE items
    raw_loss = (df.loc[valid, 'Stoppage Gap'] * df.loc[valid, 'Daily Consumption']) * df.loc[valid, 'Sales Price']
    df.loc[valid, 'Baseline Loss ($)'] = raw_loss.clip(lower=0)
    
    return df

def simulate_mitigation_scenario(row, freight_premium, tariff_pct, days_saved):
    """
    Module 3: The dynamic calculator for the Streamlit UI.
    Takes a single SKU row and UI slider inputs to calculate Net Profit Impact.
    """
    # Recalculate stoppage gap based on faster shipping
    new_stoppage_gap = max(0, row['Stoppage Gap'] - days_saved)
    units_needed = new_stoppage_gap * row['Daily Consumption']
    
    # Alternate Landed Cost = Base + Freight + Tariffs
    alt_landed_cost = row['Alt Unit Cost'] + freight_premium + (row['Alt Unit Cost'] * (tariff_pct / 100))
    
    # Cost to mitigate vs Revenue Saved
    mitigation_cost = (alt_landed_cost - row['Regular Unit Cost']) * units_needed
    revenue_saved = row['Baseline Loss ($)'] - (new_stoppage_gap * row['Daily Consumption'] * row['Sales Price'])
    
    npi = revenue_saved - mitigation_cost
    
    return {
        'Alt Landed Cost': alt_landed_cost,
        'Mitigation Cost': mitigation_cost,
        'Revenue Saved': revenue_saved,
        'Net Profit Impact': npi
    }