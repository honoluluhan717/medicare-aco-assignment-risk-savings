"""Source-first Medicare APM analysis.

MSSP uses the original CMS PY2024 ACO-level CSV.
ACO REACH and BPCI Advanced use source-extracted published CMS figures.
Incompatible financial measures are not pooled.
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv"
OUT = ROOT / "results"
FIG = ROOT / "figures"
FIELDS = ["ACO_ID", "ACO_Name", "Current_Track", "Risk_Model", "N_AB",
          "BnchmkMinExp", "EarnSaveLoss", "Sav_rate", "QualScore"]

def numeric(series):
    return pd.to_numeric(series.astype("string").str.replace(r"[$,%]", "", regex=True)
                         .str.replace(",", "", regex=False).replace("-", pd.NA), errors="coerce")

def save_bar(df, x, y, filename, title, ylabel):
    ax = df.plot.bar(x=x, y=y, legend=False, figsize=(9, 5))
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(FIG / filename, dpi=160)
    plt.close()

def main():
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    df = pd.read_csv(RAW, low_memory=False)
    missing = set(FIELDS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected CMS columns: {sorted(missing)}")
    if df["ACO_ID"].duplicated().any():
        raise ValueError("Duplicate ACO IDs in CMS source file")
    for field in ["N_AB", "BnchmkMinExp", "EarnSaveLoss", "Sav_rate", "QualScore"]:
        df[field] = numeric(df[field])
    df["benchmark_result"] = "Not reported"
    df.loc[df.BnchmkMinExp > 0, "benchmark_result"] = "Savings"
    df.loc[df.BnchmkMinExp < 0, "benchmark_result"] = "Losses"
    df.loc[df.BnchmkMinExp == 0, "benchmark_result"] = "Break-even"

    summary = pd.DataFrame([{
        "acos": len(df),
        "beneficiaries_sum_reported": df.N_AB.sum(min_count=1),
        "benchmark_difference_usd": df.BnchmkMinExp.sum(min_count=1),
        "earned_savings_minus_owed_usd": df.EarnSaveLoss.sum(min_count=1),
        "mean_quality_score": df.QualScore.mean(),
        "mean_savings_rate": df.Sav_rate.mean(),
        "n_savings": (df.BnchmkMinExp > 0).sum(),
        "n_losses": (df.BnchmkMinExp < 0).sum(),
        "n_break_even": (df.BnchmkMinExp == 0).sum(),
        "n_missing_benchmark_result": df.BnchmkMinExp.isna().sum(),
    }])
    summary.to_csv(OUT / "mssp_2024_summary.csv", index=False)
    df[FIELDS + ["benchmark_result"]].to_csv(OUT / "mssp_2024_aco_level.csv", index=False)
    df[FIELDS].isna().sum().rename("missing_count").to_csv(OUT / "missingness.csv")

    for col, slug in [("Risk_Model", "risk_model"), ("Current_Track", "track")]:
        group = df.groupby(col, dropna=False).agg(
            acos=("ACO_ID", "nunique"),
            beneficiaries=("N_AB", "sum"),
            benchmark_difference_usd=("BnchmkMinExp", "sum"),
            earned_minus_owed_usd=("EarnSaveLoss", "sum"),
            mean_quality_score=("QualScore", "mean"),
            mean_savings_rate=("Sav_rate", "mean"),
        ).reset_index()
        group.to_csv(OUT / f"mssp_by_{slug}.csv", index=False)
        save_bar(group, col, "acos", f"mssp_by_{slug}.png",
                 f"2024 MSSP ACOs by {col}", "Number of ACOs")

    status = df.benchmark_result.value_counts().rename_axis("status").reset_index(name="acos")
    status.to_csv(OUT / "mssp_financial_status.csv", index=False)
    save_bar(status, "status", "acos", "mssp_financial_status.png",
             "2024 MSSP: benchmark financial status", "Number of ACOs")

    paired = df[["Sav_rate", "QualScore"]].dropna()
    ax = paired.plot.scatter(x="Sav_rate", y="QualScore", figsize=(8, 5), alpha=0.55)
    ax.set_title("2024 MSSP: reported savings rate and quality score")
    plt.tight_layout()
    plt.savefig(FIG / "mssp_savings_quality.png", dpi=160)
    plt.close()
    pd.DataFrame([{"complete_pairs": len(paired),
                   "pearson_r": paired.Sav_rate.corr(paired.QualScore)}]).to_csv(
        OUT / "savings_quality_correlation.csv", index=False)

    df.nlargest(10, "BnchmkMinExp")[["ACO_ID", "ACO_Name", "BnchmkMinExp"]].to_csv(
        OUT / "top_10_benchmark_difference.csv", index=False)
    print(summary.to_string(index=False))
    analyze_reach()
    analyze_bpci()
    print("Saved MSSP, ACO REACH, and BPCI Advanced source-based results.")

def analyze_reach():
    """Descriptive CMS fact-sheet measures, not participant-level microdata."""
    data = pd.read_csv(ROOT / "data/source_extracted/aco_reach_2023_cms_fact_sheet.csv")
    if data["source_url"].isna().any():
        raise ValueError("Missing REACH source URL")
    data.to_csv(OUT / "aco_reach_published_measures.csv", index=False)
    for metric, filename, title, ylabel in [
        ("cms_net_benchmark_savings", "reach_benchmark_savings.png",
         "ACO REACH / GPDC: CMS benchmark net savings", "USD millions"),
        ("timely_followup_standard_new_entrant", "reach_timely_followup.png",
         "ACO REACH / GPDC: timely follow-up", "Percent")]:
        subset = data[data.metric.eq(metric)].copy()
        save_bar(subset, "year", "value", filename, title, ylabel)
    totals = data[(data.year == 2023) & data.metric.isin(
        ["acos_with_net_savings", "acos_with_net_losses"])]
    save_bar(totals, "metric", "value", "reach_2023_financial_status.png",
             "ACO REACH: 2023 financial settlement status", "ACOs")

def analyze_bpci():
    """Evaluation-based DiD net savings; not comparable to benchmark settlements."""
    data = pd.read_csv(ROOT / "data/source_extracted/bpci_advanced_final_evaluation.csv")
    if data["source_url"].isna().any():
        raise ValueError("Missing BPCI source URL")
    data.to_csv(OUT / "bpci_evaluation_estimates.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 5))
    x = list(range(len(data)))
    vals = data.net_medicare_savings_millions
    errors = [list(vals - data.ci90_lower_millions),
              list(data.ci90_upper_millions - vals)]
    ax.bar(x, vals)
    ax.errorbar(x, vals, yerr=errors, fmt="none", capsize=5, color="black")
    ax.set_xticks(x)
    ax.set_xticklabels(data.period)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("BPCI Advanced: estimated net Medicare savings (90% CI)")
    ax.set_ylabel("USD millions")
    plt.tight_layout()
    plt.savefig(FIG / "bpci_evaluation_net_savings.png", dpi=160)
    plt.close()
    pd.DataFrame([{"model": "BPCI Advanced",
                   "total_estimated_net_savings_millions": vals.sum(),
                   "note": "Sum of reported model-year period estimates; not a pooled CI"}]
                 ).to_csv(OUT / "bpci_summary.csv", index=False)

if __name__ == "__main__":
    main()
