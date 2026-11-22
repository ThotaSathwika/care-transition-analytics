import textwrap

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

from analysis import discharge_drops, kpis, load_data, monthly, stagnation_periods

st.set_page_config(page_title="UAC Care Pipeline · Analytics", page_icon="🌌", layout="wide")

# ------------------------------------------------------------------ theme
CYAN, VIOLET, PINK, LIME, AMBER, RED = "#22d3ee", "#a78bfa", "#f472b6", "#a3e635", "#fbbf24", "#fb7185"
PALETTE = [CYAN, VIOLET, PINK, LIME, AMBER, RED]

pio.templates["aurora"] = go.layout.Template(layout=dict(
    font=dict(family="Space Grotesk, Inter, sans-serif", color="#cbd5e1", size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", colorway=PALETTE,
    xaxis=dict(gridcolor="rgba(148,163,184,.08)", zeroline=False, linecolor="rgba(148,163,184,.2)"),
    yaxis=dict(gridcolor="rgba(148,163,184,.08)", zeroline=False, linecolor="rgba(148,163,184,.2)"),
    legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.08, x=0),
    hoverlabel=dict(bgcolor="#0f172a", bordercolor=VIOLET, font=dict(color="white")),
    margin=dict(l=10, r=10, t=40, b=10), title=dict(font=dict(size=16, color="#f1f5f9")),
))
pio.templates.default = "aurora"


def html(s):
    st.markdown(textwrap.dedent(s).replace("\n", " "), unsafe_allow_html=True)


html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, p, label { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(1200px 600px at 10% -10%, rgba(167,139,250,.25), transparent 60%),
  radial-gradient(900px 500px at 100% 0%, rgba(34,211,238,.18), transparent 60%),
  radial-gradient(800px 600px at 50% 120%, rgba(244,114,182,.15), transparent 60%), #070b1a; }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; max-width: 1400px; }
h1, h2, h3, h4 { font-family: 'Space Grotesk', sans-serif !important; color: #f8fafc !important; letter-spacing: -.02em; }

/* hero */
.hero { position: relative; padding: 30px 34px; border-radius: 28px; overflow: hidden;
  background: linear-gradient(135deg, rgba(30,27,75,.85), rgba(15,23,42,.85));
  border: 1px solid rgba(167,139,250,.25); box-shadow: 0 20px 60px -20px rgba(124,58,237,.45); }
.hero:before { content: ""; position: absolute; inset: -40%; z-index: 0;
  background: conic-gradient(from 0deg, transparent, rgba(34,211,238,.18), transparent, rgba(244,114,182,.18), transparent);
  animation: spin 14s linear infinite; }
.hero > * { position: relative; z-index: 1; }
@keyframes spin { to { transform: rotate(360deg); } }
.hero .eyebrow { font-size: 12px; letter-spacing: .25em; text-transform: uppercase; color: #a5b4fc; font-weight: 600; }
.hero h1 { font-size: 2.6rem; line-height: 1.05; margin: 8px 0 10px; padding: 0;
  background: linear-gradient(90deg, #67e8f9, #c4b5fd, #f9a8d4, #67e8f9); background-size: 300% 100%;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: shimmer 8s ease infinite; }
@keyframes shimmer { 0%,100% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } }
.hero p { color: #cbd5e1; font-size: 15px; max-width: 760px; margin: 0; }
.pills { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 18px; }
.pill { padding: 6px 14px; border-radius: 999px; font-size: 12.5px; font-weight: 600; color: #e2e8f0;
  background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12); backdrop-filter: blur(8px); }
.pill .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 7px; animation: pulse 1.6s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 currentColor; } 70% { box-shadow: 0 0 0 8px transparent; } 100% { box-shadow: 0 0 0 0 transparent; } }

/* kpi cards */
.kgrid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin: 22px 0 8px; }
@media (max-width: 1100px) { .kgrid { grid-template-columns: repeat(2, 1fr); } }
.kcard { position: relative; padding: 18px 18px 12px; border-radius: 22px; background: rgba(15,23,42,.65);
  border: 1px solid rgba(255,255,255,.08); backdrop-filter: blur(14px); overflow: hidden;
  transition: transform .25s ease, box-shadow .25s ease; }
.kcard:hover { transform: translateY(-4px); box-shadow: 0 18px 40px -18px var(--c); }
.kcard:after { content: ""; position: absolute; left: 0; top: 0; height: 3px; width: 100%;
  background: linear-gradient(90deg, var(--c), transparent); }
.kcard .ic { width: 36px; height: 36px; border-radius: 12px; display: grid; place-items: center; font-size: 18px;
  background: color-mix(in srgb, var(--c) 18%, transparent); }
.kcard .lb { color: #94a3b8; font-size: 12.5px; font-weight: 600; margin-top: 12px; text-transform: uppercase; letter-spacing: .06em; }
.kcard .vl { font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; font-size: 30px; font-weight: 700; color: #f8fafc; margin-top: 2px; }
.kcard .dl { font-size: 12.5px; font-weight: 600; }
.kcard svg { margin-top: 6px; width: 100%; height: 42px; }

/* pipeline stepper */
.pipe { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr auto 1fr; align-items: center; gap: 8px; margin: 10px 0 24px; }
.stage { text-align: center; padding: 20px 10px; border-radius: 22px; background: rgba(15,23,42,.6);
  border: 1px solid color-mix(in srgb, var(--c) 45%, transparent);
  box-shadow: inset 0 0 40px -18px var(--c), 0 0 30px -18px var(--c); }
.stage .em { font-size: 28px; }
.stage .nm { color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .1em; margin-top: 6px; }
.stage .nb { font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; font-size: 26px; font-weight: 700; color: #fff; }
.flow { width: 90px; text-align: center; }
.flow .ln { height: 4px; border-radius: 4px; background: repeating-linear-gradient(90deg, var(--c) 0 12px, transparent 12px 20px);
  background-size: 40px 4px; animation: dash 1s linear infinite; }
@keyframes dash { to { background-position: 40px 0; } }
.flow .pc { font-size: 12px; font-weight: 700; color: var(--c); margin-top: 6px; }

/* alerts */
.alert { display: flex; gap: 14px; align-items: center; padding: 14px 18px; border-radius: 16px; margin: 8px 0;
  background: linear-gradient(90deg, color-mix(in srgb, var(--c) 16%, transparent), rgba(15,23,42,.4));
  border: 1px solid color-mix(in srgb, var(--c) 45%, transparent); color: #f1f5f9; font-size: 14px; }
.alert b { color: var(--c); }
.alert .bd { font-size: 20px; animation: blink 1.4s infinite; }
@keyframes blink { 50% { opacity: .35; } }

/* insight cards */
.icard { padding: 18px 20px; border-radius: 20px; background: rgba(15,23,42,.6); border: 1px solid rgba(255,255,255,.08);
  border-left: 4px solid var(--c); height: 100%; }
.icard h4 { margin: 0 0 6px; font-size: 16px; }
.icard p { margin: 0; color: #cbd5e1; font-size: 13.5px; line-height: 1.5; }
.sec { display: flex; align-items: center; gap: 10px; margin: 26px 0 6px; }
.sec .bar { width: 6px; height: 26px; border-radius: 4px; background: linear-gradient(180deg, var(--c), transparent); }
.sec .tt { font-family: 'Space Grotesk', 'Inter', sans-serif; font-size: 1.35rem; font-weight: 700; color: #f8fafc; letter-spacing: -.01em; }
.sec span { color: #64748b; font-size: 13px; }

/* tabs (works for old baseweb and new stTab markup) */
.stTabs [role="tablist"] { gap: 8px; background: rgba(15,23,42,.6); padding: 6px; border-radius: 16px;
  border: 1px solid rgba(255,255,255,.08); border-bottom: 1px solid rgba(255,255,255,.08) !important; }
.stTabs [role="tab"] { height: 44px; border-radius: 12px !important; padding: 0 18px !important; color: #94a3b8; font-weight: 600;
  transition: background .2s ease; border: 0 !important; }
.stTabs [role="tab"]:hover { background: rgba(167,139,250,.12); color: #e2e8f0; }
.stTabs [role="tab"][aria-selected="true"] { background: linear-gradient(135deg, #7c3aed, #0891b2) !important; color: white !important;
  box-shadow: 0 8px 24px -10px #7c3aed; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"], .stTabs [role="tab"]:after { display: none; }
/* sidebar */
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0b1024, #0f0a2a); border-right: 1px solid rgba(167,139,250,.2); }
[data-testid="stSidebar"] h2 { background: linear-gradient(90deg, #67e8f9, #c4b5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] { background: rgba(15,23,42,.55); border-radius: 20px;
  border: 1px solid rgba(255,255,255,.07); padding: 8px; }
.stDownloadButton button { background: linear-gradient(135deg, #7c3aed, #db2777); color: white; border: 0; border-radius: 12px; font-weight: 600; }
.foot { text-align: center; color: #64748b; font-size: 12.5px; margin-top: 30px; }
.foot b { background: linear-gradient(90deg, #67e8f9, #f9a8d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""")


# ------------------------------------------------------------------ helpers
@st.cache_data
def get_data():
    return load_data()


def spark(series, color):
    """Inline SVG sparkline with a gradient fill."""
    y = pd.Series(series).dropna().to_numpy()
    if len(y) < 2:
        return ""
    y = y[-60:]
    lo, hi = y.min(), y.max()
    yy = 38 - (y - lo) / (hi - lo + 1e-9) * 34
    xx = np.linspace(0, 200, len(yy))
    pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in zip(xx, yy))
    gid = "g" + color[1:]
    return (f'<svg viewBox="0 0 200 42" preserveAspectRatio="none"><defs><linearGradient id="{gid}" x1="0" x2="0" y1="0" y2="1">'
            f'<stop offset="0" stop-color="{color}" stop-opacity=".45"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>'
            f'</linearGradient></defs><polygon points="0,42 {pts} 200,42" fill="url(#{gid})"/>'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/></svg>')


def section(title, sub, color=VIOLET):
    html(f'<div class="sec" style="--c:{color}"><div class="bar"></div><div class="tt">{title}</div><span>{sub}</span></div>')


def health_score(d):
    t = np.clip(d["transfer_eff"].median() / 0.77, 0, 1.2)
    e = np.clip(d["discharge_eff"].mean() / 3.07, 0, 1.2)
    s = np.clip(d["stability"].mean() / 76, 0, 1.2)
    return float(np.clip((t + e + s) / 3 * 100, 0, 100))


df = get_data()

# ------------------------------------------------------------------ sidebar
st.sidebar.markdown("## 🎛️ Control Deck")
dmin, dmax = df["date"].min().date(), df["date"].max().date()
preset = st.sidebar.radio("Quick range", ["All", "2023", "2024", "2025", "Custom"], horizontal=True)
if preset == "Custom":
    rng = st.sidebar.date_input("Date range", (dmin, dmax), min_value=dmin, max_value=dmax)
    start, end = (rng if isinstance(rng, tuple) and len(rng) == 2 else (dmin, dmax))
elif preset == "All":
    start, end = dmin, dmax
else:
    start, end = pd.Timestamp(f"{preset}-01-01").date(), min(pd.Timestamp(f"{preset}-12-31").date(), dmax)

METRICS = {
    "Transfer Efficiency Ratio": ("transfer_eff", CYAN),
    "Discharge Effectiveness (%)": ("discharge_eff", LIME),
    "Pipeline Throughput": ("throughput", VIOLET),
    "Backlog Accumulation Rate": ("backlog_rate", PINK),
    "Outcome Stability Score": ("stability", AMBER),
}
metric_label = st.sidebar.selectbox("📈 Ratio metric to explore", list(METRICS))
st.sidebar.markdown("### 🚨 Alert thresholds")
t_transfer = st.sidebar.slider("Min transfer efficiency", 0.0, 1.5, 0.5, 0.05)
t_discharge = st.sidebar.slider("Min discharge effectiveness (%)", 0.0, 5.0, 1.0, 0.1)
t_backlog = st.sidebar.slider("Max backlog growth / report", 0, 100, 0, 5)
smooth = st.sidebar.toggle("✨ Smooth with 7-report average", True)
st.sidebar.caption("Data: U.S. Dept. of Health & Human Services · UAC Program")

d = df[(df["date"].dt.date >= start) & (df["date"].dt.date <= end)]
if d.empty:
    st.warning("No data in the selected range.")
    st.stop()
# previous equal-length window for deltas
span = d["date"].max() - d["date"].min()
prev = df[(df["date"] < d["date"].min()) & (df["date"] >= d["date"].min() - span)]

# ------------------------------------------------------------------ hero
latest = d.tail(7)
alerts = []
if latest["transfer_eff"].median() < t_transfer:
    alerts.append((RED, "🛑", "Transfer slowdown", f"CBP → HHS transfer efficiency is <b>{latest['transfer_eff'].median():.2f}</b>, below {t_transfer:.2f}."))
if latest["discharge_eff"].mean() < t_discharge:
    alerts.append((AMBER, "⚠️", "Placement slowdown", f"Discharge effectiveness is <b>{latest['discharge_eff'].mean():.2f}%</b>, below {t_discharge:.1f}%."))
if latest["net_flow"].mean() > t_backlog:
    alerts.append((PINK, "📦", "Backlog building", f"Caseload growing by <b>{latest['net_flow'].mean():.1f}</b> children per report."))
status = ("#fb7185", f"{len(alerts)} active alert{'s' if len(alerts) != 1 else ''}") if alerts else ("#a3e635", "All systems healthy")

html(f"""
<div class="hero">
  <div class="eyebrow">HHS · Unaccompanied Alien Children Program</div>
  <h1>Care Transition Efficiency<br>& Placement Outcome Analytics</h1>
  <p>Tracking how quickly children move from CBP custody to HHS care and on to vetted sponsors,
  and where the pipeline slows down.</p>
  <div class="pills">
    <span class="pill" style="color:{status[0]}"><span class="dot" style="background:{status[0]}"></span>{status[1]}</span>
    <span class="pill">📅 {d['date'].min():%d %b %Y} → {d['date'].max():%d %b %Y}</span>
    <span class="pill">🧾 {len(d):,} reports</span>
    <span class="pill">🏠 {d['hhs_care'].iloc[-1]:,.0f} children in HHS care now</span>
  </div>
</div>
""")

# ------------------------------------------------------------------ KPI cards
k, kp = kpis(d), (kpis(prev) if len(prev) > 5 else None)
cards = [
    ("Transfer Efficiency Ratio", "Transfer Efficiency", "🚚", CYAN, "{:.2f}", "transfer_eff", True),
    ("Discharge Effectiveness Index (%)", "Discharge Effectiveness", "🏡", LIME, "{:.2f}%", "discharge_eff", True),
    ("Pipeline Throughput", "Pipeline Throughput", "🔄", VIOLET, "{:.2f}×", "throughput", True),
    ("Backlog Accumulation Rate (/day)", "Backlog Rate / report", "📦", PINK, "{:+.1f}", "backlog_rate", False),
    ("Outcome Stability Score", "Outcome Stability", "🎯", AMBER, "{:.0f}", "stability", True),
]
out = '<div class="kgrid">'
for key, label, icon, c, f, col, higher_good in cards:
    val = k[key]
    if kp and pd.notna(kp[key]) and kp[key] != 0:
        ch = (val - kp[key]) / abs(kp[key]) * 100
        good = (ch >= 0) == higher_good
        dl = f'<span class="dl" style="color:{LIME if good else RED}">{"▲" if ch >= 0 else "▼"} {abs(ch):.0f}% vs prev. period</span>'
    else:
        dl = '<span class="dl" style="color:#64748b">full history</span>'
    series = d[col].rolling(7, min_periods=1).mean()
    out += (f'<div class="kcard" style="--c:{c}"><div class="ic">{icon}</div><div class="lb">{label}</div>'
            f'<div class="vl">{f.format(val)}</div>{dl}{spark(series, c)}</div>')
html(out + "</div>")

for c, icon, title, msg in alerts:
    html(f'<div class="alert" style="--c:{c}"><span class="bd">{icon}</span><div><b>{title}</b> · {msg}</div></div>')
if not alerts:
    html(f'<div class="alert" style="--c:{LIME}"><span class="bd">✅</span><div><b>On track</b> · the latest 7 reports are within every threshold.</div></div>')

tabs = st.tabs(["🌊 Pipeline Flow", "⚡ Efficiency", "🧱 Bottlenecks", "📈 Outcomes", "💡 Insights", "🗂️ Data"])

# ------------------------------------------------------------------ 1. pipeline
with tabs[0]:
    a, t, dis = d["apprehended"].sum(), d["transferred"].sum(), d["discharged"].sum()
    section("The care pipeline", "children moving through each stage in the selected period", CYAN)
    html(f"""
    <div class="pipe">
      <div class="stage" style="--c:{CYAN}"><div class="em">🛂</div><div class="nm">Apprehended</div><div class="nb">{a:,.0f}</div></div>
      <div class="flow" style="--c:{CYAN}"><div class="ln"></div><div class="pc">avg {d['cbp_custody'].mean():,.0f} held</div></div>
      <div class="stage" style="--c:{AMBER}"><div class="em">🏢</div><div class="nm">CBP custody</div><div class="nb">{d['cbp_custody'].iloc[-1]:,.0f} now</div></div>
      <div class="flow" style="--c:{AMBER}"><div class="ln"></div><div class="pc">{t:,.0f} moved</div></div>
      <div class="stage" style="--c:{VIOLET}"><div class="em">🏥</div><div class="nm">HHS care</div><div class="nb">{d['hhs_care'].iloc[-1]:,.0f} now</div></div>
      <div class="flow" style="--c:{LIME}"><div class="ln"></div><div class="pc">{dis:,.0f} placed</div></div>
      <div class="stage" style="--c:{LIME}"><div class="em">👨‍👩‍👧</div><div class="nm">Sponsor placement</div><div class="nb">{dis:,.0f}</div></div>
    </div>""")

    c1, c2 = st.columns([1.35, 1])
    with c1:
        carry = max(dis - t, 0)  # placements drawn from children already in HHS care at the start
        labels = [f"Apprehended<br>{a:,.0f}", f"CBP custody<br>{t:,.0f} out", "HHS care",
                  f"Placed<br>{dis:,.0f}", f"Already in care<br>{carry:,.0f}"]
        fig = go.Figure(go.Sankey(
            arrangement="fixed",
            node=dict(label=labels, pad=40, thickness=24, line=dict(width=0),
                      color=[CYAN, AMBER, VIOLET, LIME, "#64748b"],
                      x=[0.02, 0.32, 0.6, 0.98, 0.32], y=[0.35, 0.35, 0.45, 0.5, 0.92]),
            link=dict(source=[0, 1, 2, 4], target=[1, 2, 3, 2], value=[a, t, dis, carry],
                      color=["rgba(34,211,238,.35)", "rgba(251,191,36,.35)", "rgba(163,230,53,.35)",
                             "rgba(100,116,139,.3)"])))
        fig.update_layout(title="Flow volumes", height=360, font=dict(color="#e2e8f0", size=12))
        st.plotly_chart(fig, width="stretch")
    with c2:
        hs = health_score(d)
        g = go.Figure(go.Indicator(
            mode="gauge+number", value=hs, number=dict(suffix="/100", font=dict(size=44, color="white")),
            title=dict(text="Pipeline Health Index", font=dict(size=16, color="#f1f5f9")),
            gauge=dict(axis=dict(range=[0, 100], tickcolor="#475569"), bar=dict(color=VIOLET, thickness=.28),
                       bgcolor="rgba(255,255,255,.03)", borderwidth=0,
                       steps=[dict(range=[0, 40], color="rgba(251,113,133,.25)"),
                              dict(range=[40, 70], color="rgba(251,191,36,.22)"),
                              dict(range=[70, 100], color="rgba(163,230,53,.22)")],
                       threshold=dict(line=dict(color=CYAN, width=4), value=hs))))
        g.update_layout(height=360)
        st.plotly_chart(g, width="stretch")
        st.caption("Blend of transfer speed, placement rate and stability, scored against the 2023–Feb 2025 baseline.")

    flows = d.set_index("date")[["apprehended", "transferred", "discharged"]]
    if smooth:
        flows = flows.rolling(7, min_periods=1).mean()
    fig = go.Figure()
    for col, c, nm in [("apprehended", CYAN, "Apprehended"), ("transferred", AMBER, "Transferred to HHS"),
                       ("discharged", LIME, "Discharged to sponsor")]:
        fig.add_scatter(x=flows.index, y=flows[col], name=nm, mode="lines", line=dict(color=c, width=2.5, shape="spline"))
    fig.update_layout(title="Daily movement between stages", height=380, hovermode="x unified")
    st.plotly_chart(fig, width="stretch")

    fig = go.Figure()
    fig.add_scatter(x=d["date"], y=d["hhs_care"], name="HHS care", fill="tozeroy", mode="lines",
                    line=dict(color=VIOLET, width=2), fillcolor="rgba(167,139,250,.25)")
    fig.add_scatter(x=d["date"], y=d["cbp_custody"], name="CBP custody", fill="tozeroy", mode="lines",
                    line=dict(color=AMBER, width=2), fillcolor="rgba(251,191,36,.3)")
    pk = d.loc[d["hhs_care"].idxmax()]
    fig.add_annotation(x=pk["date"], y=pk["hhs_care"], text=f"Peak {pk['hhs_care']:,.0f}", showarrow=True,
                       arrowcolor=PINK, font=dict(color=PINK), bgcolor="rgba(15,23,42,.8)")
    fig.update_layout(title="Active care load", height=360, hovermode="x unified")
    st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------------ 2. efficiency
with tabs[1]:
    col, c = METRICS[metric_label]
    section(metric_label, "pick a different metric in the Control Deck", c)
    s = d.set_index("date")[col]
    fig = go.Figure()
    fig.add_scatter(x=s.index, y=s, name="Per report", mode="lines", line=dict(color=c, width=1), opacity=.35)
    if smooth:
        fig.add_scatter(x=s.index, y=s.rolling(7, min_periods=1).mean(), name="7-report avg", mode="lines",
                        line=dict(color=c, width=3.5, shape="spline"), fill="tozeroy",
                        fillcolor=f"rgba({int(c[1:3], 16)},{int(c[3:5], 16)},{int(c[5:], 16)},.12)")
    th = {"transfer_eff": t_transfer, "discharge_eff": t_discharge, "backlog_rate": t_backlog}
    if col in th:
        fig.add_hline(y=th[col], line_dash="dot", line_color=RED, line_width=2,
                      annotation_text="alert threshold", annotation_font_color=RED)
    if d["date"].min() < pd.Timestamp("2025-03-07") < d["date"].max():
        fig.add_vline(x=pd.Timestamp("2025-03-07"), line_dash="dash", line_color=PINK)
        fig.add_annotation(x=pd.Timestamp("2025-03-07"), y=1, yref="paper", text="Mar 2025 vetting changes",
                           showarrow=False, font=dict(color=PINK), xanchor="left", bgcolor="rgba(15,23,42,.8)")
    fig.update_layout(height=430, hovermode="x unified")
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Sunday"]
    wd = d.groupby("weekday")[["discharge_eff", "transfer_eff"]].mean().reindex(order).dropna()
    with c1:
        fig = go.Figure(go.Barpolar(r=wd["discharge_eff"], theta=wd.index,
                                    marker=dict(color=wd["discharge_eff"], colorscale=[[0, VIOLET], [.5, CYAN], [1, LIME]],
                                                line=dict(color="#070b1a", width=2)), opacity=.9))
        fig.update_layout(title="Placement rhythm by report day (%)", height=380,
                          polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(gridcolor="rgba(148,163,184,.15)", showticklabels=False),
                                     angularaxis=dict(gridcolor="rgba(148,163,184,.15)")))
        st.plotly_chart(fig, width="stretch")
    with c2:
        wk = d.assign(t=d["is_weekend"].map({True: "Weekend (Sun)", False: "Weekday"}))
        g = wk.groupby("t")[["transfer_eff", "discharge_eff"]].mean().reset_index()
        fig = go.Figure()
        fig.add_bar(x=g["t"], y=g["transfer_eff"], name="Transfer efficiency", marker_color=CYAN, marker_cornerradius=10)
        fig.add_bar(x=g["t"], y=g["discharge_eff"], name="Discharge eff. (%)", marker_color=PINK, marker_cornerradius=10)
        fig.update_layout(title="Weekday vs weekend speed", barmode="group", height=380)
        st.plotly_chart(fig, width="stretch")
        st.caption("Sunday reports usually cover the whole weekend, so they carry higher counts.")

# ------------------------------------------------------------------ 3. bottlenecks
with tabs[2]:
    section("Inflow vs successful exits", "red = more children entering than leaving", PINK)
    b = d.set_index("date")[["apprehended", "discharged"]].rolling(7, min_periods=1).sum()
    b["gap"] = b["apprehended"] - b["discharged"]
    fig = go.Figure(go.Bar(x=b.index, y=b["gap"], marker_color=np.where(b["gap"] > 0, RED, LIME),
                           marker_line_width=0, name="Net inflow"))
    fig.update_layout(height=400, yaxis_title="Intake − discharges (7 reports)", bargap=0)
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns([1, 1.2])
    with c1:
        section("Sustained imbalance periods", "backlog growing ≥ 14 reports", AMBER)
        sp = stagnation_periods(d)
        if sp.empty:
            html(f'<div class="alert" style="--c:{LIME}"><span class="bd">✅</span><div>No sustained backlog periods in this range.</div></div>')
        else:
            for _, r in sp.iterrows():
                html(f'<div class="alert" style="--c:{AMBER}"><span class="bd">⏳</span><div><b>{r["start"]:%d %b %Y} → {r["end"]:%d %b %Y}</b>'
                     f' · {r["reports"]} reports · +{r["net_added"]} children</div></div>')
        hhs = d.set_index("date")["hhs_care"]
        low = hhs.idxmin()
        rise = hhs.iloc[-1] - hhs.min()
        if rise > 0 and low != hhs.index[-1]:
            html(f'<div class="alert" style="--c:{PINK}"><span class="bd">📈</span><div><b>Caseload rebound</b> · up {rise:,.0f} '
                 f'children since the low on {low:%d %b %Y}.</div></div>')
    with c2:
        fig = px.scatter(d, x="cbp_custody", y="transferred", color=d["date"].dt.year.astype(str),
                         size=d["apprehended"].clip(lower=1), size_max=18, opacity=.7,
                         color_discrete_sequence=[CYAN, VIOLET, PINK],
                         labels={"color": "Year", "cbp_custody": "Children in CBP custody", "transferred": "Transferred out"})
        fig.update_layout(title="CBP custody pressure vs transfers", height=400)
        st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------------ 4. outcomes
with tabs[3]:
    m = monthly(d)
    section("Month-over-month placements", "bars = discharges, line = discharge effectiveness", LIME)
    fig = go.Figure()
    fig.add_bar(x=m["month"], y=m["discharged"], name="Discharges", marker_cornerradius=6,
                marker=dict(color=m["discharged"], colorscale=[[0, "#4c1d95"], [.5, VIOLET], [1, CYAN]]))
    fig.add_scatter(x=m["month"], y=m["discharge_eff"], name="Discharge effectiveness (%)", yaxis="y2",
                    mode="lines+markers", line=dict(color=LIME, width=3, shape="spline"), marker=dict(size=7))
    fig.update_layout(yaxis=dict(title="Discharges"), yaxis2=dict(title="%", overlaying="y", side="right", showgrid=False, tickformat=".1f"),
                      height=420, hovermode="x unified")
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns([1.3, 1])
    with c1:
        hm = m.assign(y=m["month"].dt.year, mo=m["month"].dt.strftime("%b")).pivot(index="y", columns="mo", values="discharge_eff")
        hm = hm.reindex(columns=[pd.Timestamp(2000, i, 1).strftime("%b") for i in range(1, 13)])
        fig = go.Figure(go.Heatmap(z=hm.values, x=hm.columns, y=hm.index.astype(str), colorscale="Plasma",
                                   xgap=4, ygap=4, text=np.round(hm.values, 2), texttemplate="%{text}",
                                   colorbar=dict(title="%", thickness=12)))
        fig.update_layout(title="Placement heat calendar (discharge effectiveness %)", height=330, yaxis=dict(type="category"))
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig = go.Figure(go.Scatter(x=d["date"], y=d["stability"], mode="lines", line=dict(color=AMBER, width=2.5),
                                   fill="tozeroy", fillcolor="rgba(251,191,36,.12)"))
        fig.update_layout(title="Outcome Stability Score", height=330, yaxis_range=[0, 100])
        st.plotly_chart(fig, width="stretch")

    drops = discharge_drops(d)
    section("Sudden drops in reunification", f"{len(drops)} reports with discharges > 2σ below the norm", RED)
    fig = go.Figure()
    fig.add_scatter(x=d["date"], y=d["discharged"], mode="lines", name="Discharges", line=dict(color=VIOLET, width=1.5))
    fig.add_scatter(x=drops["date"], y=drops["discharged"], mode="markers", name="Sudden drop",
                    marker=dict(color=RED, size=13, symbol="x", line=dict(color="white", width=1)))
    fig.update_layout(height=340)
    st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------------ 5. insights
with tabs[4]:
    section("What the data says", "key findings for the selected period", VIOLET)
    pre, post = d[d["date"] < "2025-03-01"], d[d["date"] >= "2025-03-01"]
    stay = d["hhs_care"].mean() / max(d["discharged"].mean(), 1e-9)
    ins = [
        (CYAN, "🚚 Transfer speed", f"Median transfer efficiency is <b>{k['Transfer Efficiency Ratio']:.2f}</b>, so about "
         f"{k['Transfer Efficiency Ratio'] * 100:.0f}% of children in CBP custody move to HHS each report."),
        (LIME, "🏡 Placement rate", f"On average <b>{k['Discharge Effectiveness Index (%)']:.2f}%</b> of the HHS caseload is placed "
         f"with a sponsor per report, implying an average stay of about <b>{stay:.0f} report-days</b>."),
        (PINK, "📦 Backlog", f"Net flow averages <b>{k['Backlog Accumulation Rate (/day)']:+.1f}</b> children per report "
         f"({'caseload shrinking' if k['Backlog Accumulation Rate (/day)'] < 0 else 'caseload growing'})."),
        (AMBER, "🎯 Stability", f"Outcome Stability averages <b>{k['Outcome Stability Score']:.0f}/100</b>, with "
         f"{len(discharge_drops(d))} sudden drops detected."),
    ]
    if len(pre) > 10 and len(post) > 10:
        ins.append((RED, "⚡ March 2025 break", f"Transfer efficiency fell from <b>{pre['transfer_eff'].median():.2f}</b> to "
                    f"<b>{post['transfer_eff'].median():.2f}</b>, and discharge effectiveness from <b>{pre['discharge_eff'].mean():.2f}%</b> "
                    f"to <b>{post['discharge_eff'].mean():.2f}%</b>, in the same month ORR tightened sponsor ID and vetting rules."))
    ins.append((VIOLET, "🧭 Recommendation", "Publish process KPIs alongside daily counts, review the sponsor-vetting stage, "
                "adopt alert thresholds and report data for all seven days."))
    for i in range(0, len(ins), 2):
        cols = st.columns(2)
        for colw, (c, h, p) in zip(cols, ins[i:i + 2]):
            with colw:
                html(f'<div class="icard" style="--c:{c}"><h4>{h}</h4><p>{p}</p></div>')
        st.write("")

# ------------------------------------------------------------------ 6. data
with tabs[5]:
    section("Explore the data", "filtered reports with all derived metrics", CYAN)
    show = d.drop(columns=["month"]).assign(date=d["date"].dt.date).round(3)
    st.dataframe(show, width="stretch", height=460,
                 column_config={"discharge_eff": st.column_config.ProgressColumn("Discharge eff. %", min_value=0, max_value=5, format="%.2f"),
                                "stability": st.column_config.ProgressColumn("Stability", min_value=0, max_value=100, format="%.0f")})
    st.download_button("⬇️ Download filtered data (CSV)", show.to_csv(index=False), "uac_filtered.csv")

html('<div class="foot">Crafted by <b>Thota Sathwika</b> · Machine Learning Internship, Unified Mentor · '
     'Data: U.S. Department of Health &amp; Human Services</div>')
