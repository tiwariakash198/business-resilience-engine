# ***PHASE 3: TOTAL COST OF OWNERSHIP AND SENSITIVITY MATRIX ENGINE***

This directory contains the core frontend application and deterministic backend logic for the **Business Resilience Engine (BRE)**. The system is engineered to ingest multi-variable inventory feeds, triage supply chain vulnerabilities, and output auditable financial receipts.

## ***Module Inventory***

* **`app.py`**: The interactive Streamlit interface. Handles progressive disclosure UI, CSV ingestion, dynamic parameter updates, and conditional rendering of action receipts.
* **`logic.py`**: The deterministic analytical backend. Contains type-sanitized mathematical loops for disruption runway, landed cost mitigations, and carrying overhead.

---

## ***TCO Engine and Breakeven Analysis Modeling***

The Phase 3 module shifts the engine from a purely emergency-response tool to a continuous financial optimization mechanism. It deconstructs raw ledger spend into an absolute facility carrying rate, comparing local holding costs directly against emergency expedite premiums.

### ***The Four Financial Pillars (Granular Spend Ingestion)***
The engine avoids arbitrary default percentages by ingesting granular, accounting-standard operational expenses:
1. **Capital Cost ($):** Computed directly from the corporate Weighted Average Cost of Capital (`wacc_pct`), representing the lost opportunity cost of frozen liquidity.
2. **Storage Overhead ($):** Sum of annual warehouse rent, facility utilities, and physical security/labor.
3. **Service Overhead ($):** Localized municipal inventory taxes and asset protection insurance premiums.
4. **Risk Exposure ($):** Annual written-off capital due to physical shrinkage (theft/misplacement) and obsolescence (rust/expiration).

### ***System Formulas***

#### ***Facility Carrying Rate Derivation***
$$\text{Carrying Rate (\%)} = \left( \frac{\text{Capital Cost} + \text{Storage} + \text{Service} + \text{Risk}}{\text{Total Average Inventory Baseline}} \right) \times 100$$

#### ***SKU-Level Annual Overhead Allocation***
$$\text{Annual Overhead (USD)} = \text{Current Stock} \times \text{Regular Unit Cost} \times \left( \frac{\text{Carrying Rate} \, (\%)}{100} \right)$$

#### ***Sensitivity Matrix (Breakeven Delta)***
$$\text{Delta} = \text{Annual Holding Overhead} - \text{Emergency Mitigation Premium}$$

* **$\text{Delta} > 0$ (`LEAN_FAVORED`)**: Storing the physical buffer burns more cash annually than paying emergency air freight during an isolated stoppage. **Action:** Absorb disruption risk; run a leaner warehouse.
* **$\text{Delta} < 0$ (`BUFFER_FAVORED`)**: Emergency air-freight premiums exceed annual local warehousing overhead. **Action:** Expand physical safety stock buffers; local storage is highly cost-effective.

---

## ***Defensive Engineering Standards***
* **Subset Ingestion Resolution:** Incorporates an override mechanism preventing skewed percentage allocations when analyzing localized or filtered SKU subsets instead of total facility-wide balance sheets.
* **Fault-Tolerant Sanitation:** Programmatically intercepts `"Not provided"` string flags, missing fields, and corrupted CSV cells, coercing invalid entries to safe zero-states to guarantee zero-division protection during runtime compilation.
