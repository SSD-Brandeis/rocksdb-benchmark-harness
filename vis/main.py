import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import os
import json
import numpy as np
from glob import glob
from matplotlib.ticker import MaxNLocator

from style import line_styles

prop = font_manager.FontProperties(
    fname="../LinLibertine_Mah.ttf"
)
plt.rcParams['font.family'] = prop.get_name()
plt.rcParams['text.usetex'] = True
plt.rcParams['font.weight'] = 'normal'
plt.rcParams['font.size'] = 22

BASE = "../experiments/workload-similarity"
BYTE_TO_MB = 1024.0 * 1024.0  # bytes → MB (MiB)
KB_TO_BYTES = 1024.0          # KB → bytes

def load_iostat_series(path):
    with open(path) as f:
        raw = json.load(f)
    stats = raw["sysstat"]["hosts"][0]["statistics"]
    reads_b, writes_b = [], []
    for st in stats:
        d0 = st.get("disk", [{}])[0]
    
        reads_b.append(float(d0.get("kB_read/s", 0.0)) * KB_TO_BYTES)
        writes_b.append(float(d0.get("kB_wrtn/s", 0.0)) * KB_TO_BYTES)

    reads_mb = np.array(reads_b, dtype=float) / BYTE_TO_MB
    writes_mb = np.array(writes_b, dtype=float) / BYTE_TO_MB
    return reads_mb, writes_mb

def collect_runs(system):
    paths = sorted(glob(os.path.join(BASE, f"iostat.{system}.*.json")))
    runs = []
    for p in paths:
        r_mb, w_mb = load_iostat_series(p)
        runs.append((r_mb, w_mb))
    return runs[1:]

def average_runs(runs):
    if not runs:
        return np.array([]), np.array([])
    L = min(len(r) for (r, _) in runs)
    R = np.stack([r[:L] for (r, _) in runs]).mean(axis=0)
    W = np.stack([w[:L] for (_, w) in runs]).mean(axis=0)
    return R, W

def main():
    runs_tec = collect_runs("tectonic")
    runs_ycsb = collect_runs("ycsb")
    if not runs_tec or not runs_ycsb:
        raise RuntimeError("Missing iostat runs for one or both systems.")
    r_tec_avg, w_tec_avg = average_runs(runs_tec)
    r_ycsb_avg, w_ycsb_avg = average_runs(runs_ycsb)
    n = min(len(r_tec_avg), len(w_tec_avg), len(r_ycsb_avg), len(w_ycsb_avg))
    if n == 0:
        raise RuntimeError("No overlapping length after averaging.")
    x = np.arange(n)

    fig, ax = plt.subplots(figsize=(5, 3.5))

    ycsb_read = line_styles["YCSB"].copy()
    ycsb_read["linestyle"] = "-"
    ycsb_read["label"] = "read (YCSB)"
    ycsb_write = line_styles["YCSB"].copy()
    ycsb_write["linestyle"] = "--"
    ycsb_write["label"] = "write (YCSB)"
    tec_read = line_styles["Tectonic"].copy()
    tec_read["linestyle"] = "-"
    tec_read["label"] = "read (Tectonic)"
    tec_write = line_styles["Tectonic"].copy()
    tec_write["linestyle"] = "--"
    tec_write["label"] = "write (Tectonic)"


    # for r, w in runs_ycsb:
    #     m = min(len(r), n)
    #     ax.plot(np.arange(m), r[:m], alpha=0.10, linewidth=1.0, **ycsb_read)
    #     ax.plot(np.arange(m), w[:m], alpha=0.10, linewidth=1.0, **ycsb_write)
    # for r, w in runs_tec:
    #     m = min(len(r), n)
    #     ax.plot(np.arange(m), r[:m], alpha=0.10, linewidth=1.0, **tec_read)
    #     ax.plot(np.arange(m), w[:m], alpha=0.10, linewidth=1.0, **tec_write)

    l1, = ax.plot(x, r_ycsb_avg[:n], **ycsb_read)
    l2, = ax.plot(x, w_ycsb_avg[:n], **ycsb_write)
    l3, = ax.plot(x, r_tec_avg[:n],  **tec_read)
    l4, = ax.plot(x, w_tec_avg[:n],  **tec_write)

    ax.set_xlabel("time (s)")
    ax.set_ylabel("MB/s")

    ymax = float(
        max(
            r_ycsb_avg[:n].max(),
            w_ycsb_avg[:n].max(),
            r_tec_avg[:n].max(),
            w_tec_avg[:n].max(),
        )
    )
    ax.set_ylim(0, 300)

    # enforce integer ticks on x-axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # labels = ["YCSB (read)", "YCSB (write)", "Tectonic (read)", "Tectonic (write)"]
    # ax.legend([l1, l2, l3, l4], labels, frameon=False, ncol=2,
    #           loc='upper center', bbox_to_anchor=(0.5, -0.22))
    # fig.subplots_adjust(bottom=0.28)

    # os.makedirs("../plots", exist_ok=True)
    out = "../plots/iostat_combined.pdf"
    fig.savefig(out, bbox_inches='tight', pad_inches=0.03)
    handles, labels = ax.get_legend_handles_labels()
    legend_fig = plt.figure(figsize=(4, 1))
    legend_fig.legend(handles[-4:], labels[-4:], loc="center", ncol=4, frameon=False, borderaxespad=0, labelspacing=0, borderpad=0, columnspacing=1.0)
    legend_fig.savefig('../plots/legend.pdf', bbox_inches='tight', pad_inches=0.015)
    print(f"Saved: {out}")

if __name__ == "__main__":
    main()
