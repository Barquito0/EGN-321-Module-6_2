# Assignment 6.2 Submission Checklist

| # | Deliverable | File |
|---|---|---|
| 1 | Measured sensor data | `data/measured_temperature.csv` |
| 2 | Prediction output | `data/predicted_temperature.csv` (original-course-tool provenance not established) |
| 3 | Comparison table with signed/absolute differences | `outputs/comparison_table.csv` |
| 4 | Predicted versus measured plot | `outputs/plots/predicted_vs_measured.png` |
| 5 | Difference/residual plot | `outputs/plots/residual_difference.png` |
| 6 | Comparison report, two plausible causes | `REPORT_6_2.docx` / `REPORT_6_2.md` |
| 7 | Verification test for each cause | Report and `README.md` |
| 8 | Updated README | `README.md` |
| 9 | AI log | `AI_LOG.md` |
| 10 | Student GitHub URL | **Available:** https://github.com/Barquito0/EGN-321-Module-6_2 (separate from instructor `ivansuarez-AU` reference) |

**Important:** To fully satisfy the requirement that predictions originate from an earlier course tool, supply the original prediction-producing function, version, or documented tool export. Prediction CSV alone demonstrates deterministic output but not its lineage.

**Reproduce:** `python -m pip install -r requirements.txt && python run_analysis.py && python -m pytest`.
