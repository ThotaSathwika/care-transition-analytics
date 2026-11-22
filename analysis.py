"""Data loading and KPI calculations for the UAC care pipeline."""
import numpy as np
import pandas as pd

COLS = ["date", "apprehended", "cbp_custody", "transferred", "hhs_care", "discharged"]


def load_data(path="data/HHS_Unaccompanied_Alien_Children_Program.csv"):
    df = pd.read_csv(path, thousands=",").dropna(how="all")
    df.columns = COLS
    df["date"] = pd.to_datetime(df["date"].str.strip(), errors="coerce")
    df = df.dropna(subset=["date"]).drop_duplicates("date").sort_values("date")
    for c in COLS[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    return add_metrics(df.reset_index(drop=True))


def add_metrics(df):
    d = df.copy()
    # Stage-level ratios (daily)
    d["transfer_eff"] = d["transferred"] / d["cbp_custody"].replace(0, np.nan)
    d["discharge_eff"] = d["discharged"] / d["hhs_care"].replace(0, np.nan) * 100
    # Pipeline throughput: exits / entries over a 7-report rolling window
    entries = d["apprehended"].rolling(7, min_periods=1).sum()
    exits = d["discharged"].rolling(7, min_periods=1).sum()
    d["throughput"] = exits / entries.replace(0, np.nan)
    # Backlog: net inflow and change in total children in care
    d["total_load"] = d["cbp_custody"] + d["hhs_care"]
    d["net_flow"] = d["apprehended"] - d["discharged"]
    d["backlog_rate"] = d["net_flow"].rolling(7, min_periods=1).mean()
    # Outcome stability: 100 * (1 - coefficient of variation) of discharges, 30-report window
    roll = d["discharged"].rolling(30, min_periods=10)
    cv = roll.std() / roll.mean().replace(0, np.nan)
    d["stability"] = (100 * (1 - cv)).clip(0, 100)
    # Calendar fields
    d["weekday"] = d["date"].dt.day_name()
    d["is_weekend"] = d["date"].dt.dayofweek >= 5
    d["month"] = d["date"].dt.to_period("M").dt.to_timestamp()
    return d


def kpis(d):
    """Headline KPIs for a filtered period."""
    tot_in, tot_out = d["apprehended"].sum(), d["discharged"].sum()
    return {
        "Transfer Efficiency Ratio": d["transfer_eff"].median(),
        "Discharge Effectiveness Index (%)": d["discharge_eff"].mean(),
        "Pipeline Throughput": tot_out / tot_in if tot_in else np.nan,
        "Backlog Accumulation Rate (/day)": d["net_flow"].mean(),
        "Outcome Stability Score": d["stability"].mean(),
    }


def monthly(d):
    m = d.groupby("month").agg(
        apprehended=("apprehended", "sum"), transferred=("transferred", "sum"),
        discharged=("discharged", "sum"), hhs_care=("hhs_care", "mean"),
        cbp_custody=("cbp_custody", "mean"), transfer_eff=("transfer_eff", "median"),
        discharge_eff=("discharge_eff", "mean"), reports=("date", "count"),
    )
    m["throughput"] = m["discharged"] / m["apprehended"].replace(0, np.nan)
    m["discharge_mom_%"] = m["discharged"].pct_change() * 100
    return m.reset_index()


def stagnation_periods(d, min_len=14):
    """Runs of consecutive reports where 7-day net flow > 0 (care load growing)."""
    flag = d["backlog_rate"] > 0
    runs, start = [], None
    for i, f in enumerate(flag):
        if f and start is None:
            start = i
        if (not f or i == len(flag) - 1) and start is not None:
            end = i if f else i - 1
            if end - start + 1 >= min_len:
                seg = d.iloc[start:end + 1]
                runs.append({"start": seg["date"].iloc[0].date(), "end": seg["date"].iloc[-1].date(),
                             "reports": len(seg), "net_added": int(seg["net_flow"].sum())})
            start = None
    return pd.DataFrame(runs)


def discharge_drops(d, z=-2.0):
    """Reports where discharges fall sharply below their 30-report norm."""
    roll = d["discharged"].rolling(30, min_periods=10)
    score = (d["discharged"] - roll.mean().shift(1)) / roll.std().shift(1)
    out = d.assign(z_score=score)
    return out.loc[out["z_score"] < z, ["date", "discharged", "z_score"]]
