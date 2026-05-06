import pandas as pd
import numpy as np

def calculate_stoppage_gap(current_stock, daily_consumption, production_time, transit_time, risk_buffer):
    """
    Module 1: Calculates the exact line-stoppage gap for a single localized supply shock.
    Used primarily for single-scenario interactive UI testing.
    """
    inventory_runway = round(current_stock / daily_consumption, 1)
    total_lead_time = production_time + transit_time + risk_buffer
    stoppage_gap = round(total_lead_time - inventory_runway, 1)
    
    return {
        "Inventory Runway (Days)": inventory_runway,
        "Total Lead Time (Days)": total_lead_time,
        "Stoppage Gap (Days)": stoppage_gap
    }

def analyze_inventory_portfolio(df):
    """
    Module 2 Core: Ingests a DataFrame of inventory lines and applies vectorized 
    mathematics to identify systemic risk across an entire supply chain portfolio.
    """
    # Create a copy to avoid altering the original ingested data
    analysis_df = df.copy()
    
    # 1. Vectorized Math (Calculates all rows instantly instead of using slow loops)
    analysis_df['Inventory Runway'] = (analysis_df['Current Stock'] / analysis_df['Daily Consumption']).round(1)
    analysis_df['Total Lead Time'] = analysis_df['Production Time'] + analysis_df['Transit Time'] + analysis_df['Risk Buffer']
    analysis_df['Stoppage Gap'] = (analysis_df['Total Lead Time'] - analysis_df['Inventory Runway']).round(1)
    
    # 2. Automated Risk Categorization (Business Logic)
    conditions = [
        (analysis_df['Stoppage Gap'] > 0),
        (analysis_df['Stoppage Gap'] == 0),
        (analysis_df['Stoppage Gap'] < 0)
    ]
    choices = ['CRITICAL', 'WARNING', 'SAFE']
    
    # Apply the categorization based on the conditions above
    analysis_df['Risk Status'] = np.select(conditions, choices, default='UNKNOWN')
    
    return analysis_df

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("\n--- Module 2: Bulk Data Ingestion & Risk Analysis Test ---")
    
    # Simulating data ingested from a corporate database or CSV upload
    mock_dataset = {
        'SKU': ['Microchips', 'Steel Chassis', 'Lithium Batteries', 'Rubber Tires'],
        'Current Stock': [10000, 500, 2000, 8000],
        'Daily Consumption': [500, 50, 150, 400],
        'Production Time': [20, 10, 25, 5],
        'Transit Time': [15, 5, 20, 10],
        'Risk Buffer': [5, 2, 7, 3]
    }
    
    # Convert dictionary to a pandas DataFrame
    df_raw = pd.DataFrame(mock_dataset)
    
    print("\n1. Raw Data Ingested (First 2 Columns):")
    print(df_raw[['SKU', 'Current Stock']])
    print("-" * 50)
    
    # Run the analytical engine on the entire dataset
    processed_portfolio = analyze_inventory_portfolio(df_raw)
    
    print("\n2. Processed Risk Portfolio (Output):")
    print(processed_portfolio[['SKU', 'Stoppage Gap', 'Risk Status']])
    print("-" * 50)
    print("Test Complete. Engine is ready for scale.\n")