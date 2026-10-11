"""Evidence chain and adversarial checks for Module 6 Assignment 6.2."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.comparison import (
    read_csv,
    verify_and_align,
    compute_metrics,
    detect_time_gaps,
    make_time_grid,
    write_comparison_csv,
)

ROOT=Path(__file__).resolve().parents[1]


def source_files():
    return (read_csv(ROOT/"data/measured_temperature.csv"),
            read_csv(ROOT/"data/predicted_temperature.csv"))


def pair(sample=1, timestamp="2026-10-08T18:00:00+00:00", pred=22.0, measured=23.5, accepted=23.5, status="OK"):
    m={"sample_number":str(sample),"timestamp":timestamp,"measured_temperature_c":str(measured) if measured is not None else "", "accepted_temperature_c":str(accepted) if accepted is not None else "", "sensor_status":status,"status_reason":"test condition" if status != "OK" else "", "expected_interval_seconds":"2"}
    p={"sample_number":str(sample),"timestamp":timestamp,"predicted_temperature_c":str(pred)}
    return m,p


def test_real_csvs_exactly_align_and_exclude_non_ok():
    measured,predicted=source_files()
    rows=verify_and_align(measured,predicted)
    assert len(rows)==1800
    result=compute_metrics(rows)
    assert result['comparable_points']==1747
    assert result['excluded_measurement_rows']==53
    assert result['status_counts']=={'OK':1747,'MISSING':33,'REJECTED':14,'SUSPICIOUS':6}


def test_signed_and_absolute_arithmetic():
    m,p=pair(pred=22, measured=20, accepted=20)
    row=verify_and_align([m],[p])[0]
    assert row['signed_difference_c']==-2
    assert row['absolute_difference_c']==2


def test_real_metrics_equal_independent_reference_values():
    m,p=source_files()
    metrics=compute_metrics(verify_and_align(m,p))
    assert metrics['mean_signed_difference_c']==pytest.approx(1.7348654836863193)
    assert metrics['mean_absolute_difference_c']==pytest.approx(1.7348654836863193)
    assert metrics['maximum_absolute_difference_c']==pytest.approx(2.603)
    assert metrics['positive_residual_fraction']==1


@pytest.mark.parametrize('status',["MISSING","REJECTED","SUSPICIOUS"])
def test_untrusted_sensor_status_never_calculated(status):
    m,p=pair(measured=None if status=='MISSING' else 65,accepted=None,status=status)
    row=verify_and_align([m],[p])[0]
    assert row['comparison_status']=="EXCLUDED"
    assert row['signed_difference_c'] is None
    assert row['absolute_difference_c'] is None


def test_suspicious_accepted_numeric_not_used():
    m,p=pair(measured=40,accepted=40,status="SUSPICIOUS")
    row=verify_and_align([m],[p])[0]
    assert row['accepted_measured_temperature_c']==40
    assert row['signed_difference_c'] is None


def test_missing_prediction_rejected_rather_than_invented():
    m,p=pair();p['predicted_temperature_c']=''
    with pytest.raises(ValueError,match="prediction"):
        verify_and_align([m],[p])


def test_wrong_timestamp_cannot_be_joined_by_sample_alone():
    m,p=pair();p['timestamp']="2026-10-08T18:00:02+00:00"
    with pytest.raises(ValueError,match="do not align"):
        verify_and_align([m],[p])


def test_duplicate_sample_rejected():
    m,p=pair();m2=deepcopy(m);m2['timestamp']="2026-10-08T18:00:02+00:00"
    with pytest.raises(ValueError,match="Duplicate measured sample"):
        verify_and_align([m,m2],[p])


def test_four_real_timestamp_gaps_and_177_empty_slots():
    m,p=source_files();rows=verify_and_align(m,p)
    gaps=detect_time_gaps(rows)
    assert len(gaps)==4
    assert [g['gap_seconds'] for g in gaps]==[36,94,182,50]
    assert [g['missing_timestamp_slots'] for g in gaps]==[17,46,90,24]
    assert sum(x['missing_timestamp_slots'] for x in gaps)==177
    assert compute_metrics(rows)['expected_grid_slots_across_span']==1977


def test_plot_grid_uses_none_not_fabricated_temperatures():
    t0=datetime(2026,10,8,18,0,tzinfo=timezone.utc)
    m1,p1=pair(1,t0.isoformat())
    m2,p2=pair(2,(t0+timedelta(seconds=6)).isoformat())
    rows=verify_and_align([m1,m2],[p1,p2]);grid=make_time_grid(rows)
    assert len(grid)==4
    assert grid[1]['measured'] is None and grid[2]['measured'] is None
    assert grid[1]['predicted'] is None and grid[2]['residual'] is None


def test_excluded_status_appears_as_empty_plot_measurement():
    m1,p1=pair(1,"2026-10-08T18:00:00+00:00")
    m2,p2=pair(2,"2026-10-08T18:00:02+00:00",measured=None,accepted=None,status="MISSING")
    rows=verify_and_align([m1,m2],[p1,p2]);grid=make_time_grid(rows)
    assert grid[1]['predicted']==22.0
    assert grid[1]['measured'] is None
    assert grid[1]['residual'] is None


def test_outputs_preserve_raw_value_and_reason(tmp_path):
    m,p=pair(status="REJECTED",accepted=None,measured=60)
    rows=verify_and_align([m],[p]);path=tmp_path/"comparison.csv"
    write_comparison_csv(rows,path)
    text=path.read_text()
    assert '60.0' in text or ',60,' in text
    assert 'REJECTED' in text
    assert 'test condition' in text


def test_nonfinite_value_never_becomes_comparable():
    m,p=pair(measured=float('nan'),accepted=float('nan'))
    with pytest.raises(ValueError,match="no accepted reading"):
        verify_and_align([m],[p])
