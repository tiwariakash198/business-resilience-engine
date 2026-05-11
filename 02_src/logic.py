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

from typing import Any, Tuple, Dict # --- PHASE 3: CARRYING COST CALCULATOR AND SENSITIVITY MATRIX ---

def calculate_carrying_cost_rate(
    total_inventory_value: float,
    wacc_pct: float,
    annual_rent_utilities: float,
    warehouse_labor: float,
    annual_insurance: float,
    annual_taxes: float,
    estimated_shrinkage: float,
    obsolescence_scrap: float
) -> Dict[str, Any]:
    """
    Deconstructs carrying overhead into raw operational dollar inputs.
    Calculates absolute dollar spend and computes the definitive holding percentage safely.
    """
    try:
        val = float(total_inventory_value)
        if val <= 0:
            return {
                "rate_pct": 0.0, 
                "total_dollars": 0.0, 
                "error": "Total inventory value must be greater than $0 to derive a percentage."
            }

        # 1. Capital Cost ($) = Total Value * (WACC % / 100)
        capital_cost_dollars = val * (float(wacc_pct) / 100.0)
        
        # 2. Storage Overhead ($)
        storage_dollars = float(annual_rent_utilities) + float(warehouse_labor)
        
        # 3. Service Overhead ($)
        service_dollars = float(annual_insurance) + float(annual_taxes)
        
        # 4. Risk Overhead ($)
        risk_dollars = float(estimated_shrinkage) + float(obsolescence_scrap)
        
        # Summing total dollar overhead
        total_holding_dollars = capital_cost_dollars + storage_dollars + service_dollars + risk_dollars
        
        # Deriving the final auditable percentage
        final_rate_pct = (total_holding_dollars / val) * 100.0
        
        return {
            "rate_pct": round(final_rate_pct, 2),
            "total_dollars": round(total_holding_dollars, 2),
            "breakdown": {
                "capital": round(capital_cost_dollars, 2),
                "storage": round(storage_dollars, 2),
                "service": round(service_dollars, 2),
                "risk": round(risk_dollars, 2)
            }
        }
    except (ValueError, TypeError):
        return {"rate_pct": 0.0, "total_dollars": 0.0, "error": "Invalid numeric inputs provided."}

def calculate_sku_holding_cost(
    current_stock: Any, 
    unit_cost: Any, 
    carrying_rate_pct: float
) -> float:
    """
    Calculates the annual overhead burning on the shelves for a specific SKU row.
    Safely ignores 'Not provided' flags or corrupted string fields.
    """
    try:
        if str(current_stock).strip().lower() == "not provided" or str(unit_cost).strip().lower() == "not provided":
            return 0.0
            
        stock = float(current_stock)
        cost = float(unit_cost)
        
        if stock <= 0 or cost <= 0 or carrying_rate_pct <= 0:
            return 0.0
            
        return round(stock * cost * (carrying_rate_pct / 100.0), 2)
    except (ValueError, TypeError):
        return 0.0

def evaluate_breakeven_delta(
    annual_holding_cost: float, 
    mitigation_premium: float
) -> Tuple[float, str, str]:
    """
    Compares specific SKU holding overhead directly against the emergency expedite premium.
    Returns: (Delta amount, Actionable Recommendation string, Winning Strategy Tag)
    """
    try:
        delta = round(annual_holding_cost - mitigation_premium, 2)
        
        if delta > 0:
            rec = (
                f"Holding overhead exceeds emergency freight premium by ${delta:,.2f}. "
                "Recommendation: Pivot to a leaner buffer stock and absorb expedited shipping risks."
            )
            tag = "LEAN_FAVORED"
        elif delta < 0:
            rec = (
                f"Emergency premium exceeds annual storage overhead by ${abs(delta):,.2f}. "
                "Recommendation: Maintain physical safety stock buffer; local storage is highly cost-effective."
            )
            tag = "BUFFER_FAVORED"
        else:
            rec = "Perfect financial equilibrium. Current buffer overhead matches expedite exposure perfectly."
            tag = "NEUTRAL"
            
        return delta, rec, tag
    except (ValueError, TypeError):
        return 0.0, "Analysis unavailable due to computation error.", "ERROR"