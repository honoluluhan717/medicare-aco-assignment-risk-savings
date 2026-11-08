# Medicare Alternative Payment Models: CMS Data Analysis

## Objective

This project examines Medicare alternative payment models (APMs), focusing on how financial accountability, quality reporting, and program design differ across the Medicare Shared Savings Program (MSSP), ACO REACH, and Bundled Payments for Care Improvement Advanced (BPCI Advanced).

The **quantitative analysis currently covers MSSP performance year 2024** using an original CMS ACO-level public-use file. The other two programs are included as contextual comparisons, not pooled into a single financial ranking.

## Data source

**Original CMS dataset:** [MSSP Performance Year 2024 Financial and Quality Results](https://www.cms.gov/medicare/payment/fee-for-service-providers/shared-savings-program-ssp-acos/data), revised July 17, 2026.

The original CSV is included under [`data/raw/`](data/raw/). It contains ACO-level records, including agreement characteristics, beneficiary counts, financial reconciliation, and quality measures. No synthetic data or manually transcribed figures are used by the current quantitative analysis.

For program context, see the CMS pages for [ACO REACH](https://www.cms.gov/priorities/innovation/innovation-models/aco-reach) and [BPCI Advanced](https://www.cms.gov/priorities/innovation/innovation-models/bpci-advanced).

## Methods

The Python script `analyze.py` reads the original CMS CSV directly, validates the expected columns and ACO identifiers, and produces:

- ACO counts and financial status (positive, negative, or zero benchmark difference)
- Aggregate benchmark differences and earned shared savings minus owed losses
- Financial and quality summaries by risk model and participation track
- ACO-level missingness checks
- Savings-rate versus quality-score scatterplot and Pearson correlation
- Ten ACOs with the largest positive benchmark differences

The outputs are saved to `results/` (CSV tables) and `figures/` (PNG charts) when the script is executed. Results are computed from the source file rather than hard-coded in this README.

## Interpreting the measures

`BnchmkMinExp` represents a reported financial difference relative to an MSSP benchmark; it is **not** a causal estimate of savings attributable to the program. `EarnSaveLoss` represents earned savings minus losses owed. The mean quality score is a descriptive average across ACOs with nonmissing scores. These figures should not be compared directly with ACO REACH settlements or BPCI Advanced evaluation impact estimates.

## Cross-model context

| Model | Unit of accountability | Core payment approach | Evidence needed for a quantitative comparison |
| --- | --- | --- | --- |
| MSSP | Assigned beneficiary population within an ACO | Shared savings and, for some arrangements, downside risk | Original ACO-level CMS financial and quality data (included) |
| ACO REACH | Aligned beneficiary population within an ACO | Population-based accountability with risk options | Original CMS REACH performance data (not yet incorporated) |
| BPCI Advanced | Defined clinical episodes | Episode-based target prices and reconciliation | Original CMS evaluation tables and methods (not yet incorporated) |

## Scope and limitations

This rebuild removes the previous hand-assembled indicator tables and their figures because they had not been fully independently verified against the source publications. It **does not claim** to have completed a numerical three-model comparison. The currently supported quantitative findings are limited to the original MSSP 2024 CMS data.

The updated analysis code and raw source file are committed. The new outputs have **not yet been executed and checked** in this environment, so the repository does not yet contain regenerated charts or result tables.
