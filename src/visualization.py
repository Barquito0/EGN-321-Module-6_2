"""Gap-preserving temperature and residual visualizations."""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
from pathlib import Path
from src.comparison import make_time_grid, detect_time_gaps


def generate_plots(rows, target_dir):
    out=Path(target_dir)
    out.mkdir(parents=True,exist_ok=True)
    grid=make_time_grid(rows)
    times=[r["timestamp"] for r in grid]
    predicted=[float("nan") if r["predicted"] is None else r["predicted"] for r in grid]
    measured=[float("nan") if r["measured"] is None else r["measured"] for r in grid]
    residual=[float("nan") if r["residual"] is None else r["residual"] for r in grid]
    gaps=detect_time_gaps(rows)

    plt.rcParams.update({"font.size":10})
    fig, ax=plt.subplots(figsize=(14,5.3))
    ax.plot(times,predicted,label="Deterministic prediction",linewidth=1.6,color="#266b9e",alpha=0.95)
    ax.plot(times,measured,label="Accepted sensor measurement",linewidth=1.25,color="#e27736",alpha=0.9)
    for i,g in enumerate(gaps):
        from datetime import datetime
        ax.axvspan(datetime.fromisoformat(g["last_observed_timestamp"]),datetime.fromisoformat(g["next_observed_timestamp"]),alpha=0.16,color="#df4a44",label="Absent timestamp interval" if i==0 else None)
    ax.set_ylabel("Temperature (°C)")
    ax.set_xlabel("UTC time on 2026-10-08")
    ax.set_title("Predicted vs. accepted measured temperature — evidence gaps preserved",weight="semibold")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M",tz=times[0].tzinfo))
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    p1=out/"predicted_vs_measured.png"
    fig.savefig(p1,dpi=170)
    plt.close(fig)

    fig,ax=plt.subplots(figsize=(14,4.8))
    ax.axhline(0,color="#666",linestyle="--",linewidth=1,label="Zero difference")
    ax.plot(times,residual,linewidth=1.25,color="#196b68",label="Measured minus predicted")
    for i,g in enumerate(gaps):
        from datetime import datetime
        ax.axvspan(datetime.fromisoformat(g["last_observed_timestamp"]),datetime.fromisoformat(g["next_observed_timestamp"]),alpha=0.16,color="#df4a44",label="Absent timestamp interval" if i==0 else None)
    ax.set_xlabel("UTC time on 2026-10-08")
    ax.set_ylabel("Signed difference (°C)")
    ax.set_title("Temperature residuals — no interpolation across excluded or missing intervals",weight="semibold")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M",tz=times[0].tzinfo))
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    p2=out/"residual_difference.png"
    fig.savefig(p2,dpi=170)
    plt.close(fig)
    return p1,p2
