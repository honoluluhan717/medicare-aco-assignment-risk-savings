"""MSSP 2024: assigned beneficiaries, risk scores, and savings rates."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

root = Path(__file__).resolve().parent
source = root / "data/raw/PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv"
figures = root / "figures"
results = root / "results"
figures.mkdir(exist_ok=True)
results.mkdir(exist_ok=True)

# CMS reports ACO-level results, not individual beneficiary records.
df = pd.read_csv(source, low_memory=False)
columns = ["ACO_ID", "N_AB", "Assign_Type", "Sav_rate", "CMS_HCC_RiskScore_AGND_PY"]
missing = set(columns) - set(df.columns)
if missing:
    raise ValueError(f"Missing CMS fields: {sorted(missing)}")
if df["ACO_ID"].isna().any() or df["ACO_ID"].duplicated().any():
    raise ValueError("Missing or duplicate ACO identifiers")

for name in ["N_AB", "Sav_rate", "CMS_HCC_RiskScore_AGND_PY"]:
    df[name] = pd.to_numeric(df[name].replace("-", pd.NA), errors="coerce")

# 1. ACO size and savings rate
size = df.dropna(subset=["N_AB", "Sav_rate"])
size = size[size["N_AB"] > 0]
plt.figure(figsize=(7, 4))
plt.scatter(size["N_AB"], size["Sav_rate"], alpha=0.45)
plt.xlabel("Assigned beneficiaries (N_AB)")
plt.ylabel("CMS-reported savings rate (%)")
plt.title("ACO size and savings rate")
plt.tight_layout()
plt.savefig(figures / "01_size_and_savings.png", dpi=150)
plt.close()

# 2. Risk score and savings rate for aged, non-dual beneficiaries.
# This is a subgroup risk score, NOT an overall ACO risk score.
risk_col = "CMS_HCC_RiskScore_AGND_PY"
risk = df.dropna(subset=[risk_col, "Sav_rate"])
plt.figure(figsize=(7, 4))
plt.scatter(risk[risk_col], risk["Sav_rate"], alpha=0.45)
plt.xlabel("CMS-HCC risk score: aged, non-dual beneficiaries")
plt.ylabel("CMS-reported savings rate (%)")
plt.title("Reported risk score and savings rate")
plt.tight_layout()
plt.savefig(figures / "02_risk_and_savings.png", dpi=150)
plt.close()

# 3. Compare assignment methods (descriptive, not causal).
assignment = (df.dropna(subset=["Assign_Type", "Sav_rate"])
              .groupby("Assign_Type", as_index=False)
              .agg(acos=("ACO_ID", "count"),
                   mean_savings_rate=("Sav_rate", "mean")))
assignment.to_csv(results / "assignment_summary.csv", index=False)
plt.figure(figsize=(7, 4))
plt.bar(assignment["Assign_Type"], assignment["mean_savings_rate"])
plt.xlabel("CMS assignment method")
plt.ylabel("Mean ACO savings rate (%)")
plt.title("Savings rate by assignment method")
plt.tight_layout()
plt.savefig(figures / "03_assignment_and_savings.png", dpi=150)
plt.close()

# A small audit table makes missingness and sample sizes visible.
audit = pd.DataFrame([
    {"analysis": "ACO size", "acos": len(size)},
    {"analysis": "Aged non-dual risk score", "acos": len(risk)},
    {"analysis": "Assignment method", "acos": int(assignment["acos"].sum())},
])
audit.to_csv(results / "sample_sizes.csv", index=False)
print(f"Total ACO records: {len(df)}")
print(audit.to_string(index=False))
print(assignment.to_string(index=False))
print("Saved three charts and two CSV tables.")
