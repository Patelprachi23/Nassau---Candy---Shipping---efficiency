# Nassau Candy Distributor — Shipping Route Efficiency Analysis

## Contents
- `app.py`: interactive Streamlit dashboard
- `analysis.py`: reproducible cleaning and aggregation pipeline (expects original CSV in the same folder)
- `cleaned_shipments.csv`: prepared shipment-level source records
- `route_efficiency_summary.csv`, `regional_summary.csv`, `ship_mode_summary.csv`, `state_summary.csv`: analysis outputs
- `Research_Paper.docx`: detailed research paper
- `Executive_Summary.docx`: stakeholder summary
- `Nassau Candy Distributor.csv`: original input dataset

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run `python -m venv .venv`
4. Activate it: Windows `\.venv\Scripts\activate`; macOS/Linux `source .venv/bin/activate`.
5. Run `pip install -r requirements.txt`.
6. Run `streamlit run app.py`.
7. Streamlit opens the dashboard in your browser.

## Important data-quality finding
The dataset has 10,194 rows and no missing cells, but its date intervals are unusually long. Dates are parsed as DD-MM-YYYY. Order dates: 02 Jan 2024 to 31 Dec 2025; ship dates: 30 Jun 2026 to 28 Jun 2030. Calculated lead time: mean 1320.8 days, minimum 904 days. Validate these dates with the data owner before treating results as real logistics performance.

## Method notes
Factory is inferred from Product Name using the mapping in the supplied technical documentation. Route efficiency score is a relative min-max score (higher is faster within this dataset), not an absolute SLA. Order volume counts distinct Order IDs. Dashboard delay frequency uses the threshold selected by the user.
