# 🏛️ ***Business Resilience Engine (BRE)***
**An Enterprise Decision Support System for Supply Chain & Financial Risk Optimization**

Built with **Python, Pandas, and Streamlit**, the Business Resilience Engine translates physical supply chain bottlenecks directly into executive-ready financial metrics: **Net Profit Impact (NPI), Revenue at Risk, and Liquidity Overhead**.

---

## ***Project Vision & North Star***

Global supply chains operate in constant tension between two massive financial liabilities:
1. **The Operational Panic:** Running out of raw materials halts production, bleeding daily revenue and forcing expensive emergency air-freight rescues.
2. **The Financial Overhead:** Hoarding massive "safety stock" buffers freezes millions in working capital while burning 20% to 30% of its value annually in warehousing rent, WACC interest, insurance, and obsolescence.

**The Solution:** The BRE bridges the gap between raw logistics feeds and corporate finance. It acts as an auditable, fault-tolerant logic desk that processes operational data and delivers definitive, CFO-ready action receipts—proving exactly when it is mathematically cheaper to run a lean operation versus holding a physical buffer.

---

## ***Development Ledger & Milestones***

### ***Phase 1: Ingestion & Fault-Tolerant Triage***
* Engineered a robust ingestion pipeline supporting multi-variable inventory CSV uploads.
* Built dynamic sanitation logic that safely intercepts unformatted inputs, null fields, and custom `"Not provided"` error flags without dropping execution.
* Established an automated, multi-tier operational risk classification system mapping SKUs from **Critical** to **Low Risk**.

### ***Phase 2: Disruption Runway & Landed Cost Simulator***
* Formulated deterministic runway modeling to project exact stockout horizons based on real-time consumption rates.
* Developed an interactive **Landed Cost Mitigation Desk** allowing decision-makers to model emergency air-freight premiums, emergency tariff exposures, and lead-time recoveries with full mathematical transparency.

### ***Phase 3: Total Cost of Ownership (TCO) & Sensitivity Matrix***
* Implemented progressive disclosure UI architecture by quarantining advanced financial models behind modular opt-in toggles.
* Built an accounting-standard input desk that ingests raw P&L spend (WACC, rent, labor, insurance, shrinkage) to auto-derive highly precise facility carrying percentages.
* Deployed a live **Sensitivity Matrix** comparing annual holding overhead directly against emergency expedite premiums to find the exact **Breakeven Delta**.
* *Detailed backend formulas and APIs available in [02_src/P3_README.md](02_src/P3_README.md).*

### ***Phase 4: Geopolitical & Macroeconomic Modeling (Next Up)***
* **Global Event Mapping:** Evaluating mechanisms to measure the direct and indirect financial impact of international geopolitical shifts, trade policy changes, and macroeconomic events specifically on Indian supply chains.
* **SME & Domestic Focus:** Translating global macro-volatility into localized, actionable decision intelligence tailored to the unique operational and financial realities of Indian Small and Medium Enterprises (SMEs) and local businesses.

---

## 🖥️ Local Execution Guide

To run the full suite locally, clone the repository and launch the application via your terminal:

```powershell
# 1. Clone the repository locally
git clone [https://github.com/tiwariakash198/business-resilience-engine.git](https://github.com/tiwariakash198/business-resilience-engine.git)

# 2. Navigate into the project root directory
### ***Phase 3: Dynamic Session Overrides (Upcoming)***
* **Objective:** Eliminate data friction by allowing users to manually patch incomplete SKU records live.
* **Implementation:** Build interactive input modules directly into the sidebar to let users manually type in missing stock counts or lead times, instantly clearing `"Not provided"` flags without requiring a fresh CSV upload.

### ***Phase 4: Inventory Carrying Costs & Sensitivity Modeling***
* **Objective:** Account for the hidden overhead of holding large safety buffers.
* **Implementation:** Integrate annual carrying cost benchmarks (warehousing, insurance, depreciation) to model the economic trade-offs between maintaining lean inventory with occasional air-freight rescues versus holding massive, capital-heavy safety stocks.

---

## ***Long-Term Vision: Macro & Geopolitical Resilience (North Star)***

While the current architecture resolves micro-financial and supplier-level bottlenecks, the ultimate vision for this DSS is to model systemic, top-down macro risks specifically tailored for **Indian enterprises**. Future iterations will expand the analytics engine to account for global geopolitical events, including:

* **Sanctions & Trade Disruptions:** Quantifying supply chain exposure to restricted maritime trade routes, choke points, and global conflicts.
* **Macro-Currency Shocks:** Real-time variance modeling for purchasing power parity and cross-border exchange rate volatility.
* **Dynamic Tariff Exposure:** Predictive landed-cost mapping for sudden localized trade duties and export-import policy shifts.

---

## ***Required CSV Format***

To utilize the core engine, upload a CSV containing these 7 foundational metrics per item:

`SKU`: Unique identifier for the material/part

`Current Stock`: Total physical units available

`Daily Consumption`: Units consumed per day of active production

`Total Lead Time`: Combined days required for production, transit, and safety buffer

`Regular Unit Cost`: Baseline purchase price per unit from the primary supplier

`Alt Unit Cost`: Emergency base price per unit from a secondary backup supplier

`Sales Price`: Finished product revenue dependent on this specific part

---

## ***Local Installation & Execution***

View the source repository on [GitHub](https://github.com/yourusername/business-resilience-engine). To run the resilience engine locally, follow these steps:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/business-resilience-engine.git
cd business-resilience-engine

# 3. Install the required dependencies
pip install pandas streamlit

# 3. Launch the dashboard locally
streamlit run src/app.py
