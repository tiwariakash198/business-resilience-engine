# ***Business Resilience Engine***

An enterprise-grade Decision Support System (DSS) built to detect inventory bottlenecks, quantify financial exposure, and simulate landed-cost mitigation strategies in real-time.

---

## ***Strategic Objectives***

Supply chain disruptions are traditionally tracked purely through operational metrics like days of delay. The primary objective of this engine is to bridge the gap between **Logistics** and **Corporate Finance**. 

By translating physical material stockouts directly into **Net Profit Impact (NPI)** and **Revenue at Risk**, this tool empowers executives to make immediate, defensible decisions on whether to pay hefty premiums for emergency freight or halt production lines entirely.

---

## ***Current Capabilities (V2 Baseline)***

The engine currently operates as a fully interactive simulation dashboard with robust backend data processing:

### ***1. Fault-Tolerant Data Architecture***
* **Automated Sanitization:** Safely coerces raw input types, handles missing values, and gracefully isolates corrupted rows without crashing the application.
* **Contextual Onboarding (Empty State):** Provides an immediate visual template and downloadable sample CSV for first-time users when no file is active.

### ***2. Operational Bottleneck Mapping***
* **Runway & Gap Calculations:** Computes exact inventory runway against daily consumption rates and evaluates total lead times (Production + Transit + Buffer).
* **Automated Triage:** Classifies materials dynamically into clear risk tiers (`CRITICAL`, `WARNING`, `SAFE`).

### ***3. Financial Exposure Diagnostics***
* **Capital Locked:** Quantifies the exact dollar volume tied up in physical warehouse stock.
* **Baseline Revenue Loss:** Calculates the total value of finished-product sales lost per day if an unmitigated stockout halts the factory.

### ***4. Landed-Cost Mitigation Simulator***
A live negotiation desk allowing decision-makers to test alternative supply routes by adjusting real-time parameters:
* **Emergency Freight Premiums:** Model the cost impact of expedited air freight versus standard sea freight.
* **Variable Tariff Exposure:** Dynamically apply cross-border tax percentages to evaluate international supplier viability.
* **Lead Time Recovery:** Calculate the financial return of "buying back" production days via faster delivery routes.
* **Transparent Auditability:** Generates a one-click, fully expanded landed cost breakdown (Base + Freight + Duties) to justify executive action.

---

## ***Planned Next Phases (Immediate Roadmap)***

This mechanism is developed iteratively to ensure continuous enhancement of both backend logic and user experience:

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

## 🛠️ Local Installation & Execution

```bash
# 1. Clone the repository
git clone [https://github.com/tiwariakash198/business-resilience-engine.git](https://github.com/tiwariakash198/business-resilience-engine.git)
cd business-resilience-engine

# 2. Install required dependencies
pip install pandas numpy streamlit

# 3. Launch the dashboard locally
streamlit run src/app.py