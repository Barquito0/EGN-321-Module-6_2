"""Replay existing deterministic predictions against recorded virtual sensor measurements."""
from pathlib import Path
import json
from src.comparison import read_csv, verify_and_align, compute_metrics, write_comparison_csv
from src.visualization import generate_plots

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"data"
OUT=ROOT/"outputs"
OUT.mkdir(exist_ok=True)

measured=read_csv(SOURCE/"measured_temperature.csv")
predicted=read_csv(SOURCE/"predicted_temperature.csv")
comparison=verify_and_align(measured,predicted)
metrics=compute_metrics(comparison)
write_comparison_csv(comparison, OUT/"comparison_table.csv")
(OUT/"metrics.json").write_text(json.dumps(metrics,indent=2),encoding="utf-8")
generate_plots(comparison, OUT/"plots")
print(json.dumps({k:metrics[k] for k in ["comparable_points","excluded_measurement_rows","mean_signed_difference_c","mean_absolute_difference_c","maximum_absolute_difference_c","missing_timestamp_slots","largest_timestamp_gap_seconds"]},indent=2))
print("Wrote outputs/comparison_table.csv, outputs/metrics.json, and plots.")
