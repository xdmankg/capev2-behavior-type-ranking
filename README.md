# CAPEv2 Behavior Type Ranking

Companion data and verification code for *Ranking Subsequent Malware Behavior Types Using Type-Specific Logistic Regression with API Call Features*.

Download the release attachment **capev2-behavior-type-ranking-v1.0.0.zip**, extract it, and open a terminal in the extracted folder containing this README. The original [Avast-CTU Public CAPEv2 Dataset](https://github.com/avast/avast-ctu-cape-dataset) is distributed by its providers. This study used the full reports.

With Python 3.12.13 and pip:

```sh
python -m pip install -r requirements.txt
python scripts/verify.py
```

The script prints per-cell comparisons and ends with **PASS: Tables 6 and 7, evaluation populations, Figures 6, 8 and 10. Fixed-budget execution counts and nine MRR values checked against Section S4.** The fixed-budget comparison reads stored model metrics for the eligible population. A failed checksum, incomplete coverage, or numerical comparison failure returns a nonzero status.

- [Configuration, contrast and type names](docs/names.csv) and [frozen candidate order](configs/type_order.json)
- [Paper index](docs/paper_artifacts.csv) and [verification scope](docs/verification_scope.md)
- [Data dictionary](docs/file_schema.csv) and [evaluation settings](configs/evaluation.json)
- [Execution summaries](data/executions.parquet), [Table 6](results/main/table6_comparison.csv) and [Table 7](results/main/table7_comparison.csv)
- Post hoc [fixed-call budgets](results/posthoc/fixed_budgets.csv) with the [nine Section S4 comparisons](results/posthoc/section_s4_comparison.csv), and conditional frequency (Table 6)
- [Training reproduction](results/reproduction/training_records.json) and [indicator inputs](results/reproduction/indicator_inputs.csv)

**Rights.** Author-written scripts in `scripts/` use the [MIT License](LICENSE-CODE). Author-owned derived execution summaries, results, configuration and documentation use [CC BY 4.0](LICENSE-DATA). Please attribute HyoungJu Kim and Junho Choi, this package, and its version. Third-party source reports must be obtained directly from the providers. The package contains numerical evaluation summaries and verification code. See [CITATION.cff](CITATION.cff).
