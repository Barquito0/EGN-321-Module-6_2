# EGN 321 — Assignment 6.2: Predicted Against Measured

## Purpose

Reproducibly compare a **supplied deterministic temperature-prediction output** with its paired **virtual-temperature-sensor measurement output**. Both files cover the same recorded sample IDs and UTC timestamps, and both use degrees Celsius (°C). The project's claim is about this paired classroom evidence; it is **not** a verification of the model's physical assumptions or calibration.

**Important provenance limitation:** The uploaded predictions CSV supplies deterministic predictions but does **not identify or contain the original Module 1–4 model function** that produced them. The provided class notebook expressly permits using an exported prediction CSV. This project does not invent a model or falsely attribute its predictions to a previously verified course tool. For a strict interpretation of the assignment's "earlier tool" requirement, attach the original model function or documented export source before submission.

The GitHub repository supplied with the assignment, [ivansuarez-AU/EGN321_Module6_Assignment6_2](https://github.com/ivansuarez-AU/EGN321_Module6_Assignment6_2), is an instructor example **with read-only access**. This student project is maintained at [https://github.com/Barquito0/EGN-321-Module-6_2](https://github.com/Barquito0/EGN-321-Module-6_2).

## Data and provenance

| File | Source evidence | Quantity and units |
|---|---|---|
| `data/measured_temperature.csv` | User-uploaded `EGN321_Module6_Assignment6_2_1800_Measured.csv` | Virtual temperature sensor measurement in °C, accepted temperature in °C, status, reason, timestamp |
| `data/predicted_temperature.csv` | User-uploaded `EGN321_Module6_Assignment6_2_1800_Predictions.csv` | Supplied deterministic temperature prediction in °C, sample, timestamp |

Records are UTC timestamped, with `expected_interval_seconds = 2` in the measurement CSV. Neither file identifies a physical device, calibration procedure, sensor placement, prediction-equation coefficients, or the exact prior course tool that exported the predictions. Same-situation pairing is therefore supported by **common variable, units, sample numbers and matching timestamps**, but cannot be physically validated further using these files alone.

## Deterministic workflow

```text
Measured CSV (raw/accepted/status)         Prediction CSV (original output)
                     \                   /
                      \                 /
                  Exact sample+UTC timestamp alignment
                                  |
                         Status validation
                                  |
                   Use only status = OK and finite
                         accepted °C values
                                  |
                   signed = accepted - predicted
                   absolute = abs(signed)
                                  |
                       Comparison table + metrics
                                  |
                     Gap-aware plots and report
```

**Predictions remain unchanged.** `run_analysis.py` reads both existing source files and writes deterministic comparison outputs. Original measurements, accepted measurements, statuses, and exclusion reasons remain separate columns. No model, measurement, or timestamp is invented.

## Alignment and exclusions

Both files contain 1,800 rows; **all 1,800 pairs match on BOTH sample number and timezone-aware timestamp**. The pipeline rejects duplicate rows or timestamp mismatches rather than performing an unsafe nearest-neighbor merge.

- `OK` with a finite accepted temperature: included in comparison.
- `MISSING`: excluded (33 rows).
- `REJECTED`: excluded (14 rows).
- `SUSPICIOUS`: excluded (6 rows), even if a numeric accepted temperature is present.
- Excluded rows remain in `outputs/comparison_table.csv` with original source data and no calculated residual.

## Summary of comparable evidence

| Statistic | Result |
|---|---:|
| Source rows per CSV | 1,800 |
| Comparable (`OK`) points | **1,747** |
| Recorded rows excluded | 53 |
| Mean signed difference (measured − predicted) | **+1.734865 °C** |
| Mean absolute difference | **1.734865 °C** |
| Median signed difference | 1.745 °C |
| Maximum absolute difference | 2.603 °C |
| Smallest signed difference | 0.539 °C |
| Positive residuals | 100% of comparable points |

All included residuals are positive, indicating a **systematic positive difference** in this dataset. That does not establish a calibration fault or prove model bias as a physical cause.

## Timing gaps and honest plotting

**Four separate time gaps** occur in the original timestamp columns. The expected interval is 2 seconds:

| Last observed UTC | Next observed UTC | Separation | Absent timestamp slots |
|---|---|---:|---:|
| 18:11:56 | 18:12:32 | 36 s | 17 |
| 18:27:40 | 18:29:14 | 94 s | 46 |
| 18:42:22 | 18:45:24 | 182 s | 90 |
| 18:56:32 | 18:57:22 | 50 s | 24 |
| **Total** | | | **177** |

Across the full observation span, **1,977 two-second slots** are expected. There are 1,800 paired rows and 177 timestamp slots absent from **both** files. These 177 absent time slots are **different from the 53 recorded rows excluded for sensor status**. Thus 230 time slots cannot contribute a comparable sensor result.

Plots use an evenly spaced display grid with missing values set to **NaN/None** only; this creates visible discontinuities. It does **not** add rows to the evidence CSV, estimate sensor values, interpolate residuals, or imply knowledge of events inside the gaps.

## Two plausible causes (hypotheses, not proven)

### Hypothesis 1 — Sensor offset or calibration/reference error

**Evidence:** Every accepted measurement exceeds its paired prediction. Mean signed error is +1.735 °C and the residual mean is fairly stable across five sample regions (about +1.708 to +1.771 °C).

**Missing evidence:** Traceable thermometer readings under identical conditions, calibration certificate, hardware details, and calibration response versus temperature.

**Verification test:** At three or more stabilized temperature reference setpoints, colocate the virtual/real sensor and an independently calibrated reference sensor. Log synchronized readings. A near-constant sensor–reference offset would support this hypothesis; agreement with the reference would argue against it.

### Hypothesis 2 — Simplified model baseline or unrecorded environmental condition / sensor placement

**Evidence:** Measured temperatures follow the broad predicted shape but are persistently higher. The prediction source includes no recorded air flow, heating, local sensor position, setpoint, enclosure, or boundary-condition inputs.

**Missing evidence:** Actual model equation, source code/parameters, environmental log, and exact sensor placement/thermal coupling.

**Verification test:** Record the original model inputs, ambient/setpoint conditions and two co-located temperature sensors during a repeat run. Hold the conditions constant; compare new predictions and sensor values under those same conditions. A reduction in residual when model conditions match reality supports an assumption/placement explanation.

**Other factors:** UTC timestamps are exactly aligned for each *recorded* pair, so no row-level join offset was observed. Four timestamp gaps and 53 excluded rows restrict inferences; sensor status filtering changes the analyzed population. Units are explicitly °C; no conversion was required. A changing timing lag or incorrect unit metadata remains unverified without hardware/model documentation.

## Run locally / Colab

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m pytest
```

`run_analysis.py` creates:

- `outputs/comparison_table.csv` — **all 1,800** source rows, raw/accepted/predicted, status, signed/absolute residuals only where valid.
- `outputs/metrics.json` — deterministic evidence and timestamp gaps.
- `outputs/plots/predicted_vs_measured.png` — both temperature curves, status holes and missing intervals.
- `outputs/plots/residual_difference.png` — signed difference curve with gaps preserved.

`REPORT_6_2.docx` and `REPORT_6_2.md` summarize the evidence, uncertainty, and proposed tests.

## Tests

`tests/test_comparison.py` covers exact alignment, numeric arithmetic, status exclusions, preservation of source values, duplicates, timestamp mismatch, four detected gaps, plot-grid NaN slots, and the supplied reference metrics. All calculations are produced in Python, not AI.

## Limitations and responsible AI use

The source files do not reveal which earlier-course model produced the predictions, sensor calibration/placement or underlying physical setup; the actual causes of residuals **remain hypotheses**. The raw measurement data and prediction values are unchanged. **No Ollama service was run**. ChatGPT helped assemble code, run reproducible tests, and draft hypotheses and verification tests. Every numerical claim can be recomputed by `run_analysis.py`; see `AI_LOG.md`.

## GitHub

**Student submission repository:** [https://github.com/Barquito0/EGN-321-Module-6_2](https://github.com/Barquito0/EGN-321-Module-6_2). The linked `ivansuarez-AU` example remains a separate instructor-owned reference.
