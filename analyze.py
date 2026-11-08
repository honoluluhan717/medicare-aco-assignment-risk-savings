"""Three Medicare payment models: a small descriptive analysis of CMS data."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
FIG = BASE / "figures"
RESULTS = BASE / "results"
MSSP = DATA / "raw" / "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv"


def chart(x, y, title, ylabel, filename, errors=None):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(range(len(x)), y, color="#416b86")
    if errors is not None:
        ax.errorbar(range(len(x)), y, yerr=errors, fmt="none", color="black", capsize=4)
    ax.set_xticks(range(len(x)))
    ax.set_xticklabels([str(item) for item in x])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.axhline(0, color="#555555", linewidth=0.7)
    fig.tight_layout()
    fig.savefig(FIG / filename, dpi=150)
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)

    # Original CMS ACO-level financial and quality results, PY2024.
    mssp = pd.read_csv(MSSP, low_memory=False)
    required = {"ACO_ID", "Risk_Model", "BnchmkMinExp", "QualScore"}
    if not required.issubset(mssp.columns):
        raise ValueError(f"MSSP source is missing: {sorted(required - set(mssp.columns))}")
    if mssp["ACO_ID"].duplicated().any():
        raise ValueError("MSSP file has duplicate ACO IDs")
    for name in ["BnchmkMinExp", "QualScore"]:
        mssp[name] = pd.to_numeric(mssp[name].replace("-", pd.NA), errors="coerce")
    by_risk = (mssp.groupby("Risk_Model", dropna=False)
               .agg(acos=("ACO_ID", "count"),
                    mean_quality=("QualScore", "mean"),
                    benchmark_difference_usd=("BnchmkMinExp", "sum"))
               .reset_index())
    by_risk.to_csv(RESULTS / "mssp_by_risk.csv", index=False)
    chart(by_risk.Risk_Model, by_risk.acos, "MSSP 2024: ACOs by risk model",
          "Number of ACOs", "01_mssp_risk.png")

    # CMS REACH PY2023 fact sheet: published aggregate statistics.
    reach = pd.read_csv(DATA / "reach_cms.csv")
    assert len(reach) == 2 and reach.year.tolist() == [2022, 2023]
    reach.to_csv(RESULTS / "reach_summary.csv", index=False)
    chart(reach.year, reach.cms_net_savings_million,
          "ACO REACH / GPDC: CMS benchmark net savings",
          "USD millions", "02_reach_savings.png")
    chart(reach.year, reach.timely_followup_percent,
          "ACO REACH / GPDC: timely follow-up",
          "Percent", "03_reach_quality.png")

    # Independent CMS BPCI Advanced evaluation: DiD-based net savings.
    bpci = pd.read_csv(DATA / "bpci_cms.csv")
    assert len(bpci) == 4
    bpci.to_csv(RESULTS / "bpci_summary.csv", index=False)
    values = bpci.net_savings_million
    errors = [list(values - bpci.ci90_lower),
              list(bpci.ci90_upper - values)]
    chart(bpci.period, values, "BPCI Advanced: estimated net Medicare savings",
          "USD millions (90% CI)", "04_bpci_savings.png", errors=errors)

    print(f"MSSP ACOs: {len(mssp)}")
    print(f"REACH: {len(reach)} reported years; BPCI: {len(bpci)} evaluation periods")
    print("Wrote four charts and three summary CSVs.")


if __name__ == "__main__":
    main()
