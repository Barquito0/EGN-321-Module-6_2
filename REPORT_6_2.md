# Assignment 6.2 — Prediction versus Measurement

## 1. Prediction

The uploaded deterministic prediction file contains 1,800 predicted temperatures in Celsius, indexed by sample number and UTC timestamp. No temperature unit conversion was required. It is a supplied prediction output; the underlying Module 1–4 model source or equation was not provided, so the model's assumptions cannot be verified independently.

## 2. Measurement

The paired classroom virtual temperature sensor dataset contains 1,800 timestamped records, also in Celsius. It preserves measured values, accepted values, status, and exclusion reasons. The expected sampling interval is two seconds. The device model, physical placement, and calibration details were not supplied.

## 3. Alignment

All 1,800 pairs align on **both** sample number and timezone-aware UTC timestamp. Only the 1,747 records with status `OK` and a finite accepted temperature were included. The 33 `MISSING`, 14 `REJECTED`, and 6 `SUSPICIOUS` rows remain traceable but have no calculated residual.

## 4. Comparison results

For comparable rows, **signed difference = accepted measured − predicted** and **absolute difference = |signed difference|**, without altering either source.

| Metric | Value |
|---|---:|
| Comparable rows | **1,747** |
| Mean signed difference | **+1.734865 °C** |
| Mean absolute difference | **1.734865 °C** |
| Median signed difference | 1.745 °C |
| Largest absolute difference | 2.603 °C |
| Minimum signed difference | +0.539 °C |
| Positive differences | 100% |

## 5. Pattern

The accepted sensor readings are consistently higher than predictions. The residual means across five consecutive sample regions range from about +1.708 to +1.771 °C, consistent with a mostly stable positive offset rather than purely random, zero-centered disagreement. **This pattern does not establish a specific physical cause.**

## 6. Hypothesis 1 — Sensor calibration or reference offset

**Supporting evidence:** Every accepted residual is positive. The average difference is ~+1.735 °C and its sign is consistent across regions.

**Missing evidence:** An independently calibrated instrument reading the same conditions, temperature sweep, calibration record, and device specifications.

**Verification test:** Measure several stabilized reference temperatures simultaneously with the sensor and a calibrated thermometer. A persistent sensor–reference difference would support calibration offset; good agreement would weaken it.

## 7. Hypothesis 2 — Simplified model assumptions or sensor placement

**Supporting evidence:** The measured profile follows the predicted general changes but is persistently higher. No record of model inputs, local heat sources, airflow, boundary conditions, or sensor placement accompanies the supplied files.

**Missing evidence:** Model equation/configuration, position of the sensor, environmental conditions, and reference temperatures at the model's assumed location.

**Verification test:** Re-run the model and sensor together under recorded stable conditions, with synchronized co-located sensors. Test whether updating the model's boundary conditions or moving the sensor to the model reference location reduces the residual.

## 8. Gaps, status filtering, timing, units

There are four genuine timestamp gaps of 36, 94, 182 and 50 seconds, representing **177 absent two-second timestamps**. Separately, **53 recorded sensor-status rows** are excluded. Thus the full 1,977-slot observation span has 1,747 comparable readings; it would be false to calculate differences at the 230 unavailable/noncomparable slots. Both plots leave gaps visibly blank; no smoothing, joining across missing slots, or interpolation is performed. Paired timestamps match exactly where rows exist, but unknown sensor lag and environmental factors remain possible. Both values are in Celsius.

## 9. Conclusion and AI verification

The available evidence supports the narrow conclusion that measured temperatures exceed supplied predictions by an average of ~1.735 °C at the 1,747 comparable timestamps. The data do **not** establish whether the disagreement comes from sensor calibration, model assumptions, placement, or another cause. Controlled reference testing and original model provenance are needed. ChatGPT assisted with hypotheses and review, but deterministic Python calculations and untouched source CSVs establish the numerical evidence. No Ollama run was performed; see `AI_LOG.md`.
