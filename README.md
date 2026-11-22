# Care Transition Efficiency & Placement Outcome Analytics

Process-efficiency analytics for the U.S. HHS **Unaccompanied Alien Children (UAC) Program**: how quickly children move from CBP custody to HHS care, and how reliably they are discharged to vetted sponsors.

Unified Mentor Machine Learning internship project · **Thota Sathwika**

## Pipeline modelled

```
Apprehension ──► CBP custody ──► HHS care ──► Sponsor placement
 (intake)        (transfer out)   (discharge)
```

## KPIs

| KPI | Formula | Meaning |
|---|---|---|
| Transfer Efficiency Ratio | Transfers ÷ Children in CBP custody | Speed of CBP → HHS hand-off |
| Discharge Effectiveness Index | Discharges ÷ Children in HHS care × 100 | Share of caseload placed per report |
| Pipeline Throughput | Total discharges ÷ Total apprehensions | Overall system movement (>1 = caseload shrinking) |
| Backlog Accumulation Rate | Apprehensions − Discharges (avg per report) | Positive = backlog building |
| Outcome Stability Score | 100 × (1 − CV of discharges, 30-report window) | Consistency of placements |

## Key findings (Jan 2023 – Dec 2025, 720 reports)

- HHS caseload peaked at **11,516** (20 Dec 2023) and fell to **1,972** (21 Aug 2025), driven mainly by a ~90% fall in intake in 2025.
- From **March 2025** both efficiency ratios broke sharply: Transfer Efficiency fell from ~0.75 to ~0.2–0.4, and Discharge Effectiveness from ~3% to ~0.4–0.8% of caseload per report.
- Implied average stay in HHS care rose from about **30 report-days (2023)** to about **88 (2025)**.
- Since Aug 2025 the caseload has grown again (1,972 → 2,484) even though intake is low, a sign of a placement bottleneck.
- Outcome Stability fell from ~77 (2023–24) to ~53 (2025); the sharpest discharge drops cluster in Jan–Feb 2025 and Nov 2025.

## Dashboard features

A dark "aurora" theme with neon gradients, glass cards and animated touches:

- **Hero banner** with live alert status, date span and current caseload
- **KPI cards** with inline sparklines and change vs the previous equal-length period
- **Animated pipeline stepper** (Apprehended → CBP → HHS → Sponsor) plus a Sankey flow
- **Pipeline Health Index gauge** scored against the pre-March-2025 baseline
- **Efficiency explorer** with metric toggle, alert threshold line and a marker at the March 2025 policy change
- **Placement rhythm** polar chart and weekday vs weekend comparison
- **Bottleneck** net-inflow bars, sustained imbalance periods and caseload rebound alerts
- **Placement heat calendar**, stability score and sudden-drop markers
- **Insights tab** with auto-generated findings for any date range
- Quick-range presets (All / 2023 / 2024 / 2025 / Custom), threshold sliders, and CSV download

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
python eda.py        # regenerates figures/ used in the research paper
```

## Structure

```
app.py          Streamlit dashboard
analysis.py     Data cleaning + KPI functions
eda.py          Exploratory analysis and figures
data/           HHS UAC dataset (CSV)
figures/        EDA charts
docs/           Research paper, executive summary, video scripts
```

## Data notes

Reports are published on weekdays and Sundays; Sunday reports usually cover the weekend, so they show higher counts. Fridays and Saturdays are almost never reported, so flow totals understate true movement. Ratios are therefore compared within the same report type.

Data source: U.S. Department of Health and Human Services (hhs.gov).
