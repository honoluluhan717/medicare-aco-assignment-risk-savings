# Three Medicare payment models

A short descriptive comparison of the Medicare Shared Savings Program (MSSP), ACO REACH, and BPCI Advanced.

I wanted to understand how these programs differ in who takes financial risk, how CMS measures performance, and what the published results can actually tell us. I kept the analysis small: one original ACO-level file, two tables transcribed from CMS publications, and four figures. This is not a causal comparison of the three programs.

## Data

| Program | Period | File | What it contains |
| --- | --- | --- | --- |
| MSSP | 2024 | `data/raw/PY_Financial_and_Quality_Results_2024_revised 2026_07_17.csv` | Original CMS ACO-level financial and quality results; revised July 17, 2026 |
| ACO REACH / GPDC | 2022–2023 | `data/reach_cms.csv` | ACO counts, CMS net benchmark savings, and mean timely follow-up percentages, copied from the CMS PY2023 fact sheet |
| BPCI Advanced | Model years 1–8 | `data/bpci_cms.csv` | Net Medicare savings estimates and 90% confidence intervals from the final independent evaluation |

**Original publications**

- [CMS MSSP performance-year data](https://www.cms.gov/medicare/payment/fee-for-service-providers/shared-savings-program-ssp-acos/data). The original 2024 CSV is included in this repository.
- [CMS ACO REACH PY2023 financial and quality fact sheet](https://www.cms.gov/priorities/innovation/aco-reach-py2023-financial-and-quality-performance-results-fact-sheet), sections “Comparing REACH ACO Quality Performance to PY 2022” and “PY 2023 Financial Results Highlights.” The two figures for 2022 refer to the GPDC predecessor model. These are published summary statistics, **not** an original ACO-level data file.
- [CMS BPCI Advanced final evaluation, expenditures and savings](https://www.cms.gov/priorities/innovation/data-and-reports/2026/bpci-adv-ar7), “Medicare Program Savings,” Exhibit 5. These are evaluation estimates, **not** raw claims.

The two small CSVs include the publication URL on each row. All amounts in those files are reported by CMS, not simulated. The BPCI periods cover different numbers of model years.

## Analysis

`analyze.py` reads the three data files and saves four PNG figures and three CSV summaries to `figures/` and `results/`. It uses pandas and matplotlib.

1. **MSSP:** Count ACOs by the CMS risk-model field, and summarize their reported benchmark differences and mean quality scores. This is a within-program, ACO-level analysis.
2. **ACO REACH:** Plot CMS net savings relative to financial benchmarks in 2022 and 2023, and the mean timely follow-up measure reported for Standard/New Entrant ACOs.
3. **BPCI Advanced:** Plot independent evaluation estimates of net Medicare savings with their reported 90% confidence intervals.

## Notes on interpretation

MSSP and ACO REACH results are reported relative to program-specific financial benchmarks. BPCI Advanced estimates come from a difference-in-differences evaluation. They are not interchangeable measures of savings, and the three programs cover different populations and time periods. I therefore do not rank the programs by dollar savings or combine their quality measures into a common score.

The REACH quality measure shown is a group average, not a beneficiary-level rate calculated here. The BPCI confidence intervals reflect the evaluation's uncertainty estimates; they are not computed from the four published rows. The final evaluation cautions that its model years 7–8 savings may be overestimated because of differences in the data used.

## Files

- `analyze.py` — one analysis script
- `data/raw/` — original CMS MSSP CSV
- `data/reach_cms.csv`, `data/bpci_cms.csv` — source-transcribed CMS results
- `figures/`, `results/` — generated charts and tables

The script is also configured to run in GitHub Actions when code or data changes. Outputs should be checked against the linked publications before being used in a formal report.
