# ***🏛️ Business Resilience Engine (BRE)***

**An Enterprise Decision Support System for Supply Chain & Financial Risk Optimization**

Built with Python, Pandas, and Streamlit, the Business Resilience Engine translates physical supply chain bottlenecks directly into executive-ready financial metrics: Net Profit Impact (NPI), Revenue at Risk, and Liquidity Overhead.

## ***🧭 Project Vision & North Star***
Global supply chains operate in constant tension between two massive financial liabilities:
* **The Operational Panic:** Running out of raw materials halts production, bleeding daily revenue and forcing expensive emergency air-freight rescues.
* **The Financial Overhead:** Hoarding massive "safety stock" buffers freezes millions in working capital while burning 20% to 30% of its value annually in warehousing rent, WACC interest, insurance, and obsolescence.

**The Solution:** The BRE bridges the gap between raw logistics feeds and corporate finance. It acts as an auditable, fault-tolerant logic desk that processes operational data and delivers definitive, CFO-ready action receipts—proving exactly when it is mathematically cheaper to run a lean operation versus holding a physical buffer.

---

## ***🏗️ Core Architecture & Modules***

### ***Phase 1: Ingestion & Fault-Tolerant Triage***
* Engineered a robust ingestion pipeline supporting multi-variable inventory CSV uploads.
* Built dynamic sanitation logic that safely intercepts unformatted inputs, null fields, and custom `"Not provided"` error flags without dropping execution.

### ***Phase 2: Disruption Runway & Mitigation Simulator***
* Formulated deterministic runway modeling to project exact stockout horizons based on real-time consumption rates.
* Developed an interactive Landed Cost Mitigation Desk allowing decision-makers to model emergency air-freight premiums, alternate supplier terms, and lead-time recoveries.

### ***Phase 3: Total Cost of Ownership (TCO) & Sensitivity Matrix***
* Implemented progressive disclosure UI architecture by quarantining advanced financial models behind modular opt-in toggles.
* Built an accounting-standard input desk that ingests raw P&L spend to auto-derive highly precise facility carrying percentages.
* Deployed a live Sensitivity Matrix comparing annual holding overhead directly against emergency expedite premiums to find the exact Breakeven Delta.

### ***Phase 4: Outbound Revenue Defense (Fulfillment)*** - *[Currently in Development]*
* Evaluating pending customer orders against active warehouse stock to identify fulfillment capacity and calculate total revenue leakage from stockouts.

---

## ***📊 Required CSV Format***
To utilize the core engine, upload a CSV containing these 7 foundational metrics per item:


 `SKU`: Unique identifier for the material/part
 `Current Stock`: Total physical units currently available
 `Daily Consumption`: Units consumed per day of active production
 `Total Lead Time`: Combined days required for production, transit, and safety buffer
 `Regular Unit Cost`: Baseline purchase price per unit from the primary supplier
 `Alt Unit Cost`: Emergency base price per unit from a secondary backup supplier
 `Sales Price`: Finished product revenue dependent on this specific part

---

## ***🚀 Local Installation & Execution***

To run the resilience engine locally, follow these steps in your terminal:

# 1. Clone the repository
git clone https://github.com/tiwariakash198/business-resilience-engine.git
cd business-resilience-engine

# 2. Install the required dependencies
pip install pandas streamlit

# 3. Launch the dashboard locally
streamlit run app.py