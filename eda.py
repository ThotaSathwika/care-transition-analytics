"""Exploratory analysis: saves figures to figures/ and prints key numbers."""
import os

import matplotlib.pyplot as plt

from analysis import discharge_drops, kpis, load_data, monthly, stagnation_periods

os.makedirs("figures", exist_ok=True)
plt.rcParams.update({"figure.figsize": (10, 4.5), "axes.grid": True, "grid.alpha": 0.3})
d = load_data()
m = monthly(d)


def save(name):
    plt.tight_layout()
    plt.savefig(f"figures/{name}.png", dpi=150)
    plt.close()


# 1. Care load
plt.stackplot(d["date"], d["hhs_care"], d["cbp_custody"], labels=["HHS care", "CBP custody"],
              colors=["#82b366", "#d79b00"])
plt.title("Children in care by stage")
plt.legend(loc="upper right")
save("01_care_load")

# 2. Flows (7-report average)
for c, lab in [("apprehended", "Apprehended"), ("transferred", "Transferred to HHS"),
               ("discharged", "Discharged to sponsor")]:
    plt.plot(d["date"], d[c].rolling(7, min_periods=1).mean(), label=lab)
plt.title("Daily pipeline flows (7-report moving average)")
plt.legend()
save("02_flows")

# 3. Transfer efficiency & discharge effectiveness
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].plot(m["month"], m["transfer_eff"], marker="o")
ax[0].set_title("Transfer Efficiency Ratio (monthly median)")
ax[1].plot(m["month"], m["discharge_eff"], marker="o", color="green")
ax[1].set_title("Discharge Effectiveness % (monthly mean)")
fig.autofmt_xdate()
save("03_efficiency")

# 4. Backlog: net inflow
gap = (d["apprehended"] - d["discharged"]).rolling(7, min_periods=1).sum()
plt.bar(d["date"], gap, color=["#d62728" if v > 0 else "#2ca02c" for v in gap], width=2)
plt.title("Net inflow, 7-report window (red = backlog building)")
save("04_backlog")

# 5. Monthly discharges
plt.bar(m["month"], m["discharged"], width=20)
plt.title("Monthly sponsor placements (discharges)")
save("05_monthly_discharges")

# 6. Stability
plt.plot(d["date"], d["stability"], color="purple")
plt.title("Outcome Stability Score (30-report window)")
save("06_stability")

# 7. Weekday profile
order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Sunday"]
d.groupby("weekday")["discharge_eff"].mean().reindex(order).plot.bar(color="teal")
plt.title("Discharge effectiveness by report day (%)")
save("07_weekday")

if __name__ == "__main__":
    print("Overall KPIs:", {k: round(v, 3) for k, v in kpis(d).items()})
    for y in sorted(d["date"].dt.year.unique()):
        print(y, {k: round(v, 3) for k, v in kpis(d[d["date"].dt.year == y]).items()})
    print(stagnation_periods(d))
    print(discharge_drops(d))
    print("Figures saved to figures/")
