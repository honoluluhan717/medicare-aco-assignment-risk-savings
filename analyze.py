"""Source-first Medicare APM analysis.

Quantitative outputs use only the original CMS MSSP PY2024 ACO-level CSV.
Other APMs are compared descriptively; no incompatible savings metrics are pooled.
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
    print("Saved CMS-source-derived results and figures.")

if __name__ == "__main__":
    main()
