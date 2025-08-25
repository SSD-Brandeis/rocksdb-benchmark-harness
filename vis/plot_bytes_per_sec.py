#!/usr/bin/env python3
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import numpy as np
from matplotlib.ticker import MaxNLocator
from style import line_styles

# Use non-interactive backend
matplotlib.use("Agg")

TAG = "100x"

# Constants
BASE_DIR = Path(f"../experiments/workload-similarity/{TAG}")
BYTE_TO_GB = 1024 * 1024 * 1024
KB_TO_BYTES = 1024

# Font setup
FONT_PATH = "../LinLibertine_Mah.ttf"
prop = font_manager.FontProperties(fname=FONT_PATH)
plt.rcParams["font.family"] = prop.get_name()
plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 22


def load_iostat(path):
    with open(path) as f:
        data = json.load(f)
    stats = data["sysstat"]["hosts"][0]["statistics"]

    reads = [
        float(s.get("disk", [{}])[0].get("kB_read/s", 0.0)) * KB_TO_BYTES / BYTE_TO_GB
        for s in stats
    ]
    writes = [
        float(s.get("disk", [{}])[0].get("kB_wrtn/s", 0.0)) * KB_TO_BYTES / BYTE_TO_GB
        for s in stats
    ]
    return np.array(reads), np.array(writes)


def collect_runs(system):
    paths = sorted(BASE_DIR.glob(f"iostat.{system}.*.json"))
    runs = [load_iostat(p) for p in paths]
    return runs[1:]


def average_runs(runs):
    if not runs:
        return np.array([]), np.array([])
    min_len = min(len(r) for r, _ in runs)
    avg_reads = np.mean([r[:min_len] for r, _ in runs], axis=0)
    avg_writes = np.mean([w[:min_len] for _, w in runs], axis=0)
    return avg_reads, avg_writes


def plot_iostat(runs_tec, runs_ycsb, plot_file, legend_file):
    r_tec, w_tec = average_runs(runs_tec)
    r_ycsb, w_ycsb = average_runs(runs_ycsb)
    n = min(len(r_tec), len(w_tec), len(r_ycsb), len(w_ycsb))
    step = 200

    x = np.arange(n) + 1
    x = x[::step]
    r_tec, w_tec = r_tec[:n:step], w_tec[:n:step]
    r_ycsb, w_ycsb = r_ycsb[:n:step], w_ycsb[:n:step]

    min_len = min(len(x), len(r_tec), len(w_tec), len(r_ycsb), len(w_ycsb))
    x, r_tec, w_tec, r_ycsb, w_ycsb = (
        x[:min_len],
        r_tec[:min_len],
        w_tec[:min_len],
        r_ycsb[:min_len],
        w_ycsb[:min_len],
    )

    fig, ax = plt.subplots(figsize=(5, 3.5))

    ax.plot(x, r_ycsb, **{**line_styles["YCSB"], "linestyle": "-", "label": "read (YCSB)"})
    ax.plot(x, w_ycsb, **{**line_styles["YCSB"], "linestyle": "--", "label": "write (YCSB)"})
    ax.plot(x, r_tec, **{**line_styles["Tectonic"], "linestyle": "-", "label": "read (Tectonic)"})
    ax.plot(x, w_tec, **{**line_styles["Tectonic"], "linestyle": "--", "label": "write (Tectonic)"})

    ax.set_xlabel("time (s)")
    ax.set_ylabel("GB/s")
    ax.set_ylim(0)
    ax.set_yticklabels([0] + [f"{tick:.1f}" for tick in ax.get_yticks()[1:]])

    fig.savefig(plot_file, bbox_inches="tight", pad_inches=0.03)

    # Save legend separately
    handles, labels = ax.get_legend_handles_labels()
    legend_fig = plt.figure(figsize=(4, 1))
    legend_fig.legend(
        handles[-4:], labels[-4:], loc="center", ncol=4,
        frameon=False, borderaxespad=0, labelspacing=0,
        borderpad=0, columnspacing=0.5, handletextpad=0.3,
    )
    legend_fig.savefig(legend_file, bbox_inches="tight", pad_inches=0.015)


def main():
    runs_tec = collect_runs("tectonic")
    runs_ycsb = collect_runs("ycsb")
    if not runs_tec or not runs_ycsb:
        raise RuntimeError("Missing iostat runs for one or both systems.")

    plot_iostat(
        runs_tec,
        runs_ycsb,
        plot_file="../plots/iostat_combined.pdf",
        legend_file="../plots/legend.pdf",
    )


if __name__ == "__main__":
    main()
