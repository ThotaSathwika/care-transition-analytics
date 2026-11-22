"""Builds the research paper and executive summary PDFs (run from repo root: python docs/build_docs.py)."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=13, spaceBefore=10, spaceAfter=4)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=11, spaceBefore=6, spaceAfter=2)
P = ParagraphStyle("P", parent=ss["BodyText"], fontSize=10, leading=14, alignment=TA_JUSTIFY)
C = ParagraphStyle("C", parent=P, alignment=TA_CENTER)
CAP = ParagraphStyle("CAP", parent=P, fontSize=8.5, alignment=TA_CENTER, textColor=colors.grey)
TITLE = ParagraphStyle("T", parent=ss["Title"], fontSize=17, leading=21)

AUTHOR = "Thota Sathwika<br/>Machine Learning Intern, Unified Mentor"


def table(rows, widths=None):
    t = Table(rows, colWidths=widths, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f4f6f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef2f6")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def fig(path, caption, w=16):
    return [Image(path, width=w * cm, height=w * cm * 0.45), Paragraph(caption, CAP), Spacer(1, 6)]


def para(*texts):
    return [Paragraph(t, P) for t in texts]


KPI_ROWS = [
    ["KPI", "2023", "2024", "2025", "Overall"],
    ["Transfer Efficiency Ratio (median)", "0.78", "0.75", "0.39", "0.70"],
    ["Discharge Effectiveness Index (%)", "3.34", "2.90", "0.90", "2.37"],
    ["Pipeline Throughput (exits / entries)", "2.45", "1.39", "2.22", "1.85"],
    ["Backlog Accumulation Rate (per report)", "-170.4", "-57.9", "-15.9", "-79.9"],
    ["Outcome Stability Score (0-100)", "77.0", "77.1", "53.2", "69.0"],
    ["Implied stay in HHS care (report-days)", "30.0", "34.2", "87.8", "-"],
]


def paper():
    s = [Paragraph("Care Transition Efficiency and Placement Outcome Analytics for the "
                   "U.S. Unaccompanied Alien Children Program", TITLE),
         Paragraph(AUTHOR, C), Spacer(1, 10)]

    s += [Paragraph("Abstract", H1)] + para(
        "Monitoring of the U.S. Unaccompanied Alien Children (UAC) Program has focused on how many "
        "children are in custody, not on how efficiently they move through care. This study treats the "
        "program as a three-stage pipeline (CBP custody, HHS care, sponsor placement) and analyses 720 "
        "daily HHS reports from January 2023 to December 2025. Five process KPIs are defined: Transfer "
        "Efficiency Ratio, Discharge Effectiveness Index, Pipeline Throughput, Backlog Accumulation Rate "
        "and Outcome Stability Score. The HHS caseload fell from a peak of 11,516 children (December 2023) "
        "to 1,972 (August 2025), but this fall was driven by lower intake rather than faster placement. From "
        "March 2025 the median Transfer Efficiency Ratio fell from 0.77 to 0.34 and the share of the "
        "caseload discharged per report fell from 3.07% to 0.55%. The implied time a child spends in HHS "
        "care nearly tripled, placement consistency dropped, and the caseload has been growing again since "
        "August 2025 despite very low intake. An interactive Streamlit dashboard was built to monitor these "
        "metrics with date filters and threshold alerts.")
    s += [Paragraph("<b>Keywords:</b> process analytics, care pipeline, KPI design, child welfare, "
                    "exploratory data analysis, Streamlit", P)]

    s += [Paragraph("1. Introduction", H1)] + para(
        "Children who arrive at the U.S. border without a parent or legal guardian are taken into the custody "
        "of U.S. Customs and Border Protection (CBP), transferred to the Office of Refugee Resettlement within "
        "the Department of Health and Human Services (HHS), screened and sheltered, and finally released to a "
        "vetted sponsor, usually a family member. Each hand-off is a point where delays can occur, and long "
        "stays in congregate care are known to be harmful to children.",
        "Public reporting gives daily counts for each stage, but counts alone do not show whether the system is "
        "moving well. A falling caseload can mean faster reunification, or simply fewer arrivals. This project "
        "reframes the data from a capacity view to a process-efficiency view and asks four questions: how "
        "efficiently are children transferred from CBP to HHS; are discharges keeping pace with inflows; when "
        "do backlogs accumulate; and are placement outcomes improving or deteriorating over time?")

    s += [Paragraph("2. Dataset", H1)] + para(
        "The dataset is published by HHS and contains one row per report with six fields: reporting date, "
        "children apprehended and placed in CBP custody, children in CBP custody, children transferred out of "
        "CBP custody, children in HHS care, and children discharged from HHS care. After removing blank rows "
        "and converting thousand-separated strings to numbers, 720 reports remain (12 Jan 2023 to 21 Dec 2025) "
        "with no missing values and no duplicate dates.",
        "An important property of the data is its reporting calendar: reports are issued Monday to Thursday "
        "and on Sunday, while Friday and Saturday are almost never reported (2 Friday reports in total). "
        "Sunday reports appear to cover the weekend and therefore carry higher counts. Flow totals therefore "
        "understate true movement, so the analysis relies mainly on ratios and on comparisons within the same "
        "report type.")

    s += [Paragraph("3. Methodology", H1), Paragraph("3.1 Pipeline model", H2)] + para(
        "The program is modelled as Apprehension → CBP custody → HHS care → Sponsor placement. Stocks are the "
        "children in CBP custody and in HHS care; flows are apprehensions (entries), transfers (CBP → HHS) and "
        "discharges (exits).")
    s += [Paragraph("3.2 KPI definitions", H2),
          table([["KPI", "Formula", "Interpretation"],
                 ["Transfer Efficiency Ratio", "Transfers ÷ CBP custody", "Higher = faster CBP hand-off"],
                 ["Discharge Effectiveness Index", "Discharges ÷ HHS care × 100", "% of caseload placed per report"],
                 ["Pipeline Throughput", "Σ Discharges ÷ Σ Apprehensions", ">1 means caseload is shrinking"],
                 ["Backlog Accumulation Rate", "Mean(Apprehensions − Discharges)", ">0 means backlog building"],
                 ["Outcome Stability Score", "100 × (1 − CV of discharges, 30 reports)", "Higher = steadier placements"]],
                [4.5 * cm, 5.5 * cm, 5.5 * cm]), Spacer(1, 6)]
    s += [Paragraph("3.3 Backlog, temporal and stability analysis", H2)] + para(
        "Sustained imbalance periods are runs of at least 14 consecutive reports where the 7-report average "
        "net inflow is positive. Sudden drops in reunification are reports where discharges fall more than two "
        "standard deviations below the previous 30-report mean. Implied average stay is the mean HHS caseload "
        "divided by mean discharges per report (Little's Law). Weekday and Sunday reports are compared "
        "separately, and all metrics are aggregated by month for trend analysis. The analysis was written in "
        "Python using Pandas, NumPy, Matplotlib and Plotly.")

    s += [PageBreak(), Paragraph("4. Exploratory Data Analysis", H1)]
    s += fig("figures/01_care_load.png", "Figure 1. Children in care by stage, Jan 2023 – Dec 2025.")
    s += para(
        "Figure 1 shows the HHS caseload rising to a peak of 11,516 on 20 December 2023 and then falling "
        "steadily through 2024 before a steep drop in early 2025, reaching a low of 1,972 on 21 August 2025. "
        "CBP custody is small in comparison (average 226 children before March 2025, 28 after) but is the "
        "entry point for nearly every child.")
    s += fig("figures/02_flows.png", "Figure 2. Daily pipeline flows (7-report moving average).")
    s += para(
        "Figure 2 shows that for most of 2023 and 2024 discharges ran well above apprehensions, which is why "
        "the caseload shrank. In early 2025 apprehensions collapsed (from an average of 148 per report in 2024 "
        "to 13 in 2025), and discharges fell by almost the same proportion.")

    s += [Paragraph("5. Results", H1), Paragraph("5.1 Yearly KPI summary", H2),
          table(KPI_ROWS, [6.3 * cm, 2 * cm, 2 * cm, 2 * cm, 2.2 * cm]), Spacer(1, 6)]
    s += [Paragraph("5.2 Transition efficiency", H2)]
    s += fig("figures/03_efficiency.png", "Figure 3. Monthly Transfer Efficiency Ratio and Discharge Effectiveness.")
    s += para(
        "Both ratios were stable from January 2023 to February 2025 (transfer efficiency about 0.70–0.85, "
        "discharge effectiveness about 2.5–3.5%). In March 2025 both broke sharply. Transfer efficiency fell "
        "to 0.38 and kept sliding to about 0.21 by December 2025, meaning that each day only around one in five "
        "children in CBP custody is transferred out. Discharge effectiveness fell to 0.39–0.86%. This is a "
        "structural change in how the pipeline operates, not a seasonal effect.")
    s += [Paragraph("5.3 Backlog and bottlenecks", H2)]
    s += fig("figures/04_backlog.png", "Figure 4. Net inflow over a 7-report window (red = backlog building).")
    s += para(
        "Across the full period the system cleared children faster than they arrived (Backlog Accumulation "
        "Rate of −79.9 per report), but the margin narrowed every year: −170 in 2023, −58 in 2024 and −16 in "
        "2025. One sustained imbalance period was detected, from 23 March to 16 April 2025, when 59 more "
        "children entered than left over 20 reports. More importantly, the HHS caseload grew from 1,972 to "
        "2,484 between August and December 2025 while intake was very low. With a smaller caseload, this "
        "growth signals that children are staying longer, i.e. the bottleneck has moved to the sponsor "
        "vetting and placement stage.")
    s += [Paragraph("5.4 Temporal patterns", H2)]
    s += fig("figures/07_weekday.png", "Figure 5. Mean discharge effectiveness by report day.", 13)
    s += para(
        "Sunday reports show the highest discharge effectiveness (2.84%) and Thursday the next highest "
        "(2.79%), while Tuesday is lowest (1.87%). The Sunday value reflects weekend aggregation. The Thursday "
        "peak and Tuesday trough suggest placements are batched later in the working week. Transfer efficiency "
        "differs little between weekday (0.69) and Sunday (0.70) reports, so CBP transfers run steadily "
        "through the week.")
    s += [Paragraph("5.5 Outcome stability", H2)]
    s += fig("figures/06_stability.png", "Figure 6. Outcome Stability Score (30-report rolling window).")
    s += para(
        "The stability score averaged 76 before March 2025 and 50 afterwards. Twelve sudden discharge drops "
        "were detected; seven of them fall between July 2024 and February 2025, including 15 and 9 discharges "
        "on 17–18 February 2025, and two more occur in late November 2025 (1 and 0 discharges). Placements "
        "have become both lower and less predictable.")
    s += fig("figures/05_monthly_discharges.png", "Figure 7. Monthly sponsor placements.")

    s += [Paragraph("6. Discussion", H1)] + para(
        "The headline caseload reduction, viewed alone, looks like a success. The process metrics tell a "
        "different story. Before March 2025 the pipeline moved children quickly: roughly three-quarters of the "
        "CBP population was transferred each day and about 3% of the HHS caseload was placed with sponsors per "
        "report, implying an average stay of around 30 report-days. After March 2025 the implied stay rose to "
        "about 88 report-days. The break lines up with documented changes to sponsor requirements: on "
        "7 March 2025 ORR narrowed the list of identity documents accepted from sponsors, and on 25 March "
        "2025 it published an Interim Final Rule updating the Unaccompanied Children Program Foundational "
        "Rule [2, 5]. ORR describes these as enhanced vetting to protect children; child-welfare groups argue "
        "they delay release [5, 6]. The near-zero discharges in late November 2025 also coincide with media "
        "reports of a pause in releases [6]. The dataset alone cannot prove cause, but the size and timing of "
        "the change point to a procedural shift rather than a capacity shortage, since shelter capacity was "
        "plentiful at the time.",
        "Limitations: the data has no Friday/Saturday reports, no case-level information (age, country, length "
        "of stay), and no breakdown by facility, so delays cannot be traced to specific shelters. The Transfer "
        "Efficiency Ratio uses same-day stock as its denominator and so is sensitive to small CBP populations.")

    s += [Paragraph("7. Recommendations", H1)] + para(
        "1. <b>Adopt process KPIs alongside counts.</b> Publish Discharge Effectiveness and implied length of "
        "stay with the daily figures so slowdowns are visible early.",
        "2. <b>Review the sponsor-vetting stage.</b> The 2025 drop in discharge effectiveness is the largest "
        "bottleneck in the pipeline; streamlining document checks and adding case managers would raise it.",
        "3. <b>Set alert thresholds.</b> For example, flag when transfer efficiency falls below 0.5 or "
        "discharge effectiveness below 1% for seven consecutive reports, as implemented in the dashboard.",
        "4. <b>Smooth weekly placement batching.</b> Spreading discharges across the week would reduce "
        "Tuesday lows and shorten stays.",
        "5. <b>Improve data reporting.</b> Daily reports for all seven days, plus length-of-stay and "
        "facility-level fields, would allow exact bottleneck tracing.")

    s += [Paragraph("8. Dashboard", H1)] + para(
        "A Streamlit web application provides: a Sankey view of the care pipeline; transfer and discharge "
        "efficiency panels with a metric toggle; bottleneck charts showing net inflow and sustained imbalance "
        "periods; month-over-month outcome trends, stability score and sudden-drop tables; a date-range "
        "filter; threshold sliders that raise visual alerts; and CSV download of filtered data.")

    s += [Paragraph("9. Conclusion", H1)] + para(
        "Reframing the UAC dataset as a care pipeline shows that the program's smaller caseload hides a much "
        "slower system. Transfers and placements both slowed sharply from March 2025, children now stay in "
        "care roughly three times longer, and placements are less consistent. Tracking the five KPIs defined "
        "here, and acting on the sponsor placement stage, would support faster and more reliable "
        "reunification.")
    s += [Paragraph("References", H1)] + para(
        "[1] U.S. Department of Health and Human Services, Unaccompanied Alien Children Program data, hhs.gov.",
        "[2] Office of Refugee Resettlement, Unaccompanied Children Program Policy Guide.",
        "[3] J. D. C. Little, \"A Proof for the Queuing Formula L = λW,\" Operations Research, 9(3), 1961.",
        "[4] Unified Mentor, Care Transition Efficiency &amp; Placement Outcome Analytics project brief.",
        "[5] Federal Register, Unaccompanied Children Program Foundational Rule; Update to Accord with Statutory "
        "Requirements, 90 FR, 25 March 2025; National Center for Youth Law, The Unraveling of ORR, Sept 2025.",
        "[6] NPR / KERA News, reporting on reunification of detained migrant children, 19 December 2025.")
    return s


def summary():
    s = [Paragraph("Executive Summary: UAC Care Pipeline Efficiency", TITLE),
         Paragraph("For government stakeholders · Prepared by Thota Sathwika · Data: HHS, Jan 2023 – Dec 2025", C),
         Spacer(1, 8), Paragraph("Purpose", H1)]
    s += para("This summary reports how efficiently unaccompanied children move from CBP custody to HHS care "
              "and on to sponsors, using five process KPIs computed from 720 HHS daily reports.")
    s += [Paragraph("Key findings", H1)] + para(
        "• <b>Smaller caseload, slower system.</b> HHS care fell from 11,516 (Dec 2023) to about 2,000 (2025), "
        "mainly because arrivals fell by about 90%.",
        "• <b>Structural slowdown since March 2025.</b> Transfer Efficiency fell from 0.77 to 0.34; the share "
        "of the caseload placed per report fell from 3.07% to 0.55%.",
        "• <b>Longer stays.</b> Implied time in HHS care rose from about 30 to about 88 report-days.",
        "• <b>New backlog.</b> The caseload rose from 1,972 to 2,484 (Aug – Dec 2025) despite very low intake.",
        "• <b>Less reliable placements.</b> The Outcome Stability Score fell from 76 to 50.",
        "• <b>Timing.</b> The slowdown began in March 2025, when ORR tightened sponsor identity and vetting requirements.")
    s += [Spacer(1, 4), table(KPI_ROWS, [6.3 * cm, 2 * cm, 2 * cm, 2 * cm, 2.2 * cm]), Spacer(1, 6)]
    s += [Paragraph("Recommended actions", H1)] + para(
        "1. Publish discharge effectiveness and length of stay with daily counts.",
        "2. Review and streamline the sponsor-vetting stage, the main bottleneck since 2025.",
        "3. Adopt alert thresholds (transfer efficiency &lt; 0.5, discharge effectiveness &lt; 1%).",
        "4. Spread placements evenly across the week.",
        "5. Report all seven days and add facility-level and length-of-stay data.")
    s += [Paragraph("Tool", H1)] + para(
        "An interactive Streamlit dashboard tracks all KPIs with date filters and threshold alerts.")
    return s


if __name__ == "__main__":
    for name, fn in [("docs/Research_Paper.pdf", paper), ("docs/Executive_Summary.pdf", summary)]:
        SimpleDocTemplate(name, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                          topMargin=1.8 * cm, bottomMargin=1.8 * cm, title=name).build(fn())
        print("built", name)
