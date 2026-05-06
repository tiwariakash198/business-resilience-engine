# ***Business Resilience Engine***

*An interactive Decision Support System (DSS) for supply chain auditors and operations managers.*

## ***Project Status***
- **Phase 1: Logistics Matrix** - ✅ Completed
- **Phase 2: Financial Burn & Liquidity Tracker** - 🔄 In Progress
- **Phase 3: Geopolitical Risk & Tariff Modeling** - 📅 Planned

## ***Phase 1: Logistics Matrix (Completed)***
Built an interactive dashboard to ingest corporate inventory data and instantly categorize systemic logistical risks. 
* **Data Ingestion:** Supports dynamic CSV uploads for custom portfolio analysis.
* **Vectorized Processing:** Utilizes `pandas` to process bulk SKU data instantly without loop delays.
* **Risk Categorization:** Automatically flags inventory lines as CRITICAL, WARNING, or SAFE based on the calculated Stoppage Gap (Lead Time vs. Inventory Runway).

## ***Scope for Improvements and Next Steps***
* **Phase 2 Integration:** Upgrading the mathematical engine (`logic.py`) to calculate Capital Locked and Daily Financial Burn Rate by introducing Unit Cost metrics.
* **Data Validation:** Implement automated data cleaning to handle missing or corrupted cells in user-uploaded CSV files.
* **Visual Analytics:** Add interactive charts to visually map the highest-risk SKUs.

## ***Tech Stack***
* **Backend Engine:** Python, Pandas, NumPy
* **Frontend UI:** Streamlit
* **Architecture:** Enterprise `src/` directory pattern with strict separation of logic and user interface.