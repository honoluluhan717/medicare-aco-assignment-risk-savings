# Medicare Alternative Payment Models: CMS Data Analysis

## Objective

This project examines Medicare alternative payment models (APMs), focusing on how financial accountability, quality reporting, and program design differ across the Medicare Shared Savings Program (MSSP), ACO REACH, and Bundled Payments for Care Improvement Advanced (BPCI Advanced).

The quantitative analysis covers **MSSP 2024**, **ACO REACH 2022–2023**, and **BPCI Advanced model years 1–8**, using distinct source types. These programs are compared in design and interpretation, not ranked by incompatible dollar totals.

## Data source

**Original CMS dataset:** [MSSP Performance Year 2024 Financial and Quality Results](https://www.cms.gov/medicare/payment/fee-for-service-providers/shared-savings-program-ssp-acos/data), revised July 17, 2026.

The original CSV is included under [`data/raw/`](data/raw/). It contains ACO-level records, including agreement characteristics, beneficiary counts, financial reconciliation, and quality measures. The MSSP analysis uses the original CMS ACO-level CSV. For ACO REACH and BPCI Advanced, the analysis uses small **source-extracted tables** whose published figures were checked against the CMS fact sheet and final evaluation. These are explicitly not original participant-level raw files. They are stored in [\`data/source_extracted/\`](data/source_extracted/).

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

| Model | Quantitative evidence | Financial measure |
| --- | --- | --- |
| MSSP (2024) | Original CMS ACO-level public-use file | Benchmark difference and shared savings/losses |
| ACO REACH (2022–2023) | Verified published CMS fact-sheet figures | Savings relative to financial benchmarks |
| BPCI Advanced (MY1–8) | Verified CMS final evaluation estimates | Estimated net Medicare savings, with 90% confidence intervals |

These estimates have different populations, denominators, model years, and methods. They should not be pooled or interpreted as a head-to-head evaluation.

## Scope and limitations

This rebuild removes the earlier unverified indicator tables and figures. The new three-model analysis is source-based, but the ACO REACH and BPCI Advanced portions use selected published summary results, not full underlying participant-level files. Consequently, the project does not estimate causal cross-model differences.

The source files and updated analysis code are committed. New outputs must be executed and checked before they are described as validated results.
