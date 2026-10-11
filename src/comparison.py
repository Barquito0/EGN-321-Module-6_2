"""Deterministic evidence processing for EGN 321 Assignment 6.2.

The supplied prediction CSV is authoritative. No prediction is synthesized,
modified, or attributed to a previous course function without provenance.
"""
from __future__ import annotations

import csv
import math
import statistics
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

EXPECTED_INTERVAL_SECONDS = 2
VALID_STATUS = "OK"


def read_csv(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_timestamp(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError(f"Timestamp lacks timezone: {value!r}")
    return dt


def finite_float(value: str | None) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        val = float(value)
    except (ValueError, TypeError):
        return None
    return val if math.isfinite(val) else None


def verify_and_align(measured: list[dict], predicted: list[dict]) -> list[dict]:
    """Align strictly on BOTH keys, rejecting duplicate/mismatched source rows."""
    def index(rows, kind):
        result = {}
        for row in rows:
            try:
                key = int(row["sample_number"])
                stamp = parse_timestamp(row["timestamp"])
            except (ValueError, KeyError, TypeError) as exc:
                raise ValueError(f"Invalid {kind} alignment key") from exc
            if (key, stamp) in result:
                raise ValueError(f"Duplicate {kind} sample and timestamp: {key}")
            if any(other == key for other, _ in result):
                raise ValueError(f"Duplicate {kind} sample number: {key}")
            result[(key, stamp)] = row
        return result

    m_by_key = index(measured, "measured")
    p_by_key = index(predicted, "predicted")
    if m_by_key.keys() != p_by_key.keys():
        only_m = sorted(set(m_by_key) - set(p_by_key))[:3]
        only_p = sorted(set(p_by_key) - set(m_by_key))[:3]
        raise ValueError(f"Prediction / measurement keys do not align: measured-only={only_m}, predicted-only={only_p}")
    aligned = []
    for (sample, timestamp), m in sorted(m_by_key.items()):
        p = p_by_key[(sample, timestamp)]
        interval = int(m["expected_interval_seconds"])
        if interval != EXPECTED_INTERVAL_SECONDS:
            raise ValueError(f"Expected interval changed at sample {sample}: {interval}")
        prediction = finite_float(p["predicted_temperature_c"])
        if prediction is None:
            raise ValueError(f"Missing/nonfinite deterministic prediction at sample {sample}")
        raw_measurement = finite_float(m["measured_temperature_c"])
        accepted = finite_float(m["accepted_temperature_c"])
        status = m["sensor_status"].strip().upper()
        included = status == VALID_STATUS and accepted is not None
        if included and raw_measurement is None:
            raise ValueError(f"OK sample {sample} has no raw reading")
        if status == "OK" and not included:
            raise ValueError(f"OK sample {sample} has no accepted reading")
        if included and abs(raw_measurement - accepted) > 1e-9:
            raise ValueError(f"Accepted value does not match raw OK reading: sample {sample}")
        if status not in ("OK", "MISSING", "REJECTED", "SUSPICIOUS"):
            raise ValueError(f"Unrecognized sensor status {status!r}")
        signed = accepted - prediction if included else None
        aligned.append({
            "sample_number": sample,
            "timestamp": timestamp.isoformat(),
            "predicted_temperature_c": prediction,
            "raw_measured_temperature_c": raw_measurement,
            "accepted_measured_temperature_c": accepted,
            "sensor_status": status,
            "sensor_status_reason": m.get("status_reason", "").strip(),
            "comparison_status": "COMPARABLE" if included else "EXCLUDED",
            "exclusion_reason": "" if included else f"{status}: {m.get('status_reason', '').strip()}".strip(": "),
            "signed_difference_c": signed,
            "absolute_difference_c": abs(signed) if signed is not None else None,
        })
    if any(parse_timestamp(b["timestamp"]) <= parse_timestamp(a["timestamp"]) for a,b in zip(aligned,aligned[1:])):
        raise ValueError("Samples do not have monotonically increasing timestamps")
    return aligned


def detect_time_gaps(rows: list[dict], expected_seconds: int = EXPECTED_INTERVAL_SECONDS) -> list[dict]:
    """Find missing timestamp slots; do not reconstruct reading values."""
    if expected_seconds <= 0:
        raise ValueError("expected_seconds must be positive")
    gaps = []
    for prev, cur in zip(rows, rows[1:]):
        p = parse_timestamp(prev["timestamp"])
        c = parse_timestamp(cur["timestamp"])
        delta = (c - p).total_seconds()
        if delta <= 0:
            raise ValueError("Timestamps must strictly increase")
        if abs(delta / expected_seconds - round(delta / expected_seconds)) > 1e-6:
            raise ValueError(f"Non-grid sampling step: {delta} seconds")
        if delta > expected_seconds:
            gaps.append({
                "after_sample": prev["sample_number"],
                "before_sample": cur["sample_number"],
                "last_observed_timestamp": p.isoformat(),
                "next_observed_timestamp": c.isoformat(),
                "gap_seconds": int(delta),
                "missing_timestamp_slots": int(round(delta / expected_seconds)) - 1,
            })
    return gaps


def compute_metrics(rows: list[dict]) -> dict:
    comparable = [r for r in rows if r["comparison_status"] == "COMPARABLE"]
    if not comparable:
        raise ValueError("No comparable sensor measurements")
    diffs = [r["signed_difference_c"] for r in comparable]
    gaps = detect_time_gaps(rows)
    start, end = parse_timestamp(rows[0]["timestamp"]), parse_timestamp(rows[-1]["timestamp"])
    expected_grid = int(round((end - start).total_seconds() / EXPECTED_INTERVAL_SECONDS)) + 1
    missing_time_slots = sum(x["missing_timestamp_slots"] for x in gaps)
    assert expected_grid == len(rows) + missing_time_slots
    return {
        "source_measured_rows": len(rows),
        "source_prediction_rows": len(rows),
        "comparable_points": len(comparable),
        "excluded_measurement_rows": len(rows) - len(comparable),
        "status_counts": dict(Counter(r["sensor_status"] for r in rows)),
        "predicted_unit": "degC",
        "measured_unit": "degC",
        "alignment": "exact sample_number AND timezone-aware timestamp",
        "timestamp_start_utc": start.isoformat(),
        "timestamp_end_utc": end.isoformat(),
        "expected_interval_seconds": EXPECTED_INTERVAL_SECONDS,
        "expected_grid_slots_across_span": expected_grid,
        "received_timestamp_slots": len(rows),
        "missing_timestamp_slots": missing_time_slots,
        "time_gaps": gaps,
        "largest_timestamp_gap_seconds": max((x["gap_seconds"] for x in gaps), default=0),
        "mean_signed_difference_c": statistics.mean(diffs),
        "mean_absolute_difference_c": statistics.mean(abs(x) for x in diffs),
        "median_signed_difference_c": statistics.median(diffs),
        "min_signed_difference_c": min(diffs),
        "max_signed_difference_c": max(diffs),
        "maximum_absolute_difference_c": max(abs(x) for x in diffs),
        "positive_residual_fraction": sum(x > 0 for x in diffs) / len(diffs),
        "residual_standard_deviation_c": statistics.stdev(diffs) if len(diffs) > 1 else 0,
        "region_summary": [
            {
                "sample_region": f"{a}-{b}",
                "count": len(subset := [r["signed_difference_c"] for r in comparable if a <= r["sample_number"] <= b]),
                "mean_signed_difference_c": statistics.mean(subset) if subset else None,
                "mean_absolute_difference_c": statistics.mean(abs(x) for x in subset) if subset else None,
            }
            for a,b in ((1,450),(451,800),(801,1180),(1181,1500),(1501,1800))
        ],
    }


def write_comparison_csv(rows: list[dict], filepath: str | Path) -> None:
    fields = ["sample_number", "timestamp", "predicted_temperature_c", "raw_measured_temperature_c", "accepted_measured_temperature_c", "sensor_status", "sensor_status_reason", "comparison_status", "exclusion_reason", "signed_difference_c", "absolute_difference_c"]
    with open(filepath,"w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{k: ("" if row[k] is None else row[k]) for k in fields} for row in rows])


def make_time_grid(rows: list[dict]) -> list[dict]:
    """Build visualization-only timeline; new missing slots contain None, not imputed measurements."""
    keyed = {parse_timestamp(row["timestamp"]):row for row in rows}
    start, end = min(keyed), max(keyed)
    grid=[]
    t=start
    while t<=end:
        existing=keyed.get(t)
        grid.append({
            "timestamp":t,
            "sample_number":existing["sample_number"] if existing else None,
            "predicted":existing["predicted_temperature_c"] if existing else None,
            "measured":existing["accepted_measured_temperature_c"] if existing and existing["comparison_status"]=="COMPARABLE" else None,
            "residual":existing["signed_difference_c"] if existing else None,
            "present_in_source":existing is not None,
        })
        t += timedelta(seconds=EXPECTED_INTERVAL_SECONDS)
    return grid
