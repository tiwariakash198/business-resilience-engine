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
cd business-resilience-engine

# 3. Install the required dependencies
pip install pandas streamlit

# 4. Boot the Streamlit server using the clean relative path
streamlit run 02_src/app.py