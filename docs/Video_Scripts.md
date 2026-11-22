# Video Scripts

## 1. Project Explanation Video (about 5 minutes)

Record your screen with the live dashboard open. Keep your camera in a corner if you can.

**[0:00 – 0:30] Introduction**
"Hello, I'm Thota Sathwika, a final-year B.Tech CSE student at BVRIT Narsapur. During my Unified Mentor internship I built a project called *Care Transition Efficiency and Placement Outcome Analytics*. It uses HHS data on the Unaccompanied Alien Children Program to measure how efficiently children move through the care system."

**[0:30 – 1:15] Problem**
"Children who arrive at the U.S. border alone go through a pipeline: CBP custody, then transfer to HHS care, then release to a vetted sponsor. Officials track how many children are in custody, but not how fast they move through each stage. A smaller caseload can mean faster reunification, or just fewer arrivals. My project measures the speed and reliability of the pipeline itself."

**[1:15 – 2:00] Data and method** *(show GitHub repo: analysis.py)*
"The dataset has 720 daily reports from January 2023 to December 2025, with intake, CBP custody, transfers, HHS care and discharges. I cleaned it in Pandas, removing blank rows and converting comma-formatted numbers. I found reports are only issued Monday to Thursday and Sunday, so I focused on ratios rather than raw totals. I defined five KPIs: Transfer Efficiency Ratio, Discharge Effectiveness Index, Pipeline Throughput, Backlog Accumulation Rate and Outcome Stability Score."

**[2:00 – 4:00] Dashboard demo** *(switch to the Streamlit app)*
- "At the top are the five KPIs, and below them threshold alerts. Right now two alerts are red: transfer efficiency and discharge effectiveness are both below their thresholds."
- "In the sidebar I can change the date range, pick which ratio to plot, and move the alert thresholds." *(move a slider)*
- "Pipeline Flow tab: this Sankey diagram shows children moving from apprehension to CBP, to HHS, to sponsors, and the area chart shows the caseload peaking at 11,516 in December 2023."
- "Efficiency Panels: here you can clearly see the drop in March 2025. Transfer efficiency fell from about 0.77 to 0.34, and discharge effectiveness fell from about 3% to about half a percent."
- "Bottlenecks tab: red bars mean more children entering than leaving. The caseload has been rising again since August 2025."
- "Outcome Trends: monthly placements, the stability score which dropped from 76 to 50, and a table of sudden drops in discharges."
- "Finally, the Data tab lets users download the filtered data."

**[4:00 – 4:45] Insights and recommendations**
"The main insight is that a smaller caseload hid a much slower system. The time children spend in HHS care nearly tripled after March 2025, which matches the month ORR tightened sponsor identity and vetting rules. I recommend publishing process KPIs alongside daily counts, reviewing the sponsor vetting stage, using alert thresholds, and reporting data for all seven days."

**[4:45 – 5:00] Closing**
"The code, research paper and executive summary are in my GitHub repository. Thank you for watching."

---

## 2. Internship Experience & Feedback Video (about 2–3 minutes)

Speak to the camera. Adjust the lines so they sound like you, and add your own real experiences.

**[0:00 – 0:20] Introduction**
"Hi, I'm Thota Sathwika, a final-year Computer Science student at B V Raju Institute of Technology, Narsapur. I recently completed my Machine Learning internship with Unified Mentor, and I'd like to share my experience."

**[0:20 – 1:00] What I worked on**
"My project was Care Transition Efficiency and Placement Outcome Analytics, using real U.S. Department of Health and Human Services data. I did the full workflow myself: data cleaning, exploratory analysis, KPI design, a research paper, an executive summary, and a live Streamlit dashboard."

**[1:00 – 1:45] What I learned**
- "Technically, I got much stronger at Pandas, time-series analysis like rolling windows, and building interactive dashboards with Streamlit and Plotly, and deploying them."
- "I learned to design KPIs from a business problem instead of just plotting columns."
- "I learned to check data quality carefully. For example, finding that Fridays and Saturdays were missing changed how I compared numbers."
- "I also learned to write findings for non-technical readers, like government stakeholders."

**[1:45 – 2:15] Challenges**
"The biggest challenge was interpreting ratios correctly when the data had reporting gaps, and explaining a sudden structural change in the data responsibly without overclaiming the cause."

**[2:15 – 2:45] Feedback**
"The project was well structured, with clear objectives and deliverables, and working on real public data made it meaningful. One suggestion: more mid-project check-ins or mentor reviews would help interns get feedback earlier. Overall, it was a valuable experience that prepared me for data and machine learning roles."

**[2:45 – 3:00] Closing**
"Thank you to the Unified Mentor team for this opportunity."

---

### Recording and upload tips

1. Record with OBS Studio, Loom, or the Windows Game Bar (Win + G).
2. Upload to YouTube as **Unlisted** (or to Google Drive with "Anyone with the link can view").
3. Copy the share link. It will start with `https://`.
