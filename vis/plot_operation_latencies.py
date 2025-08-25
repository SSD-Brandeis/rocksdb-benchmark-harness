#!/usr/bin/env python3
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import numpy as np

# Use non-interactive backend
matplotlib.use("Agg")

TAG = "100x"

# Constants
BASE_DIR = Path(f"../experiments/workload-similarity/{TAG}")
OUTPUT_DIR = Path("../plots")
OUTPUT_DIR.mkdir(exist_ok=True)
CONVERT_TO_MS = 1000.0  # nanoseconds → microseconds

# Font setup
FONT_PATH = "../LinLibertine_Mah.ttf"
prop = font_manager.FontProperties(fname=FONT_PATH)
plt.rcParams["font.family"] = prop.get_name()
plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 20


def load_op_latency(system: str):
    ops = {"insert": [], "pointquery": [], "update": []}
    for i in range(1, 6):
        path = BASE_DIR / f"op-latency.{system}.{i}.json"
        if not path.exists():
            continue
        with path.open() as f:
            arr = json.load(f)
        for d in arr:
            op = str(d.get("operation", "")).lower().replace(" ", "")
            if op in ops:
                ops[op].append(float(d["latency"]))
    return {k: np.array(v, dtype=float) for k, v in ops.items() if len(v) > 0}


def plot_latency_boxplot():
    ycsb_data = load_op_latency("ycsb")
    tectonic_data = load_op_latency("tectonic")

    operations = [op for op in ["insert", "pointquery", "update"] if op in ycsb_data]
    if not operations:
        raise RuntimeError("No op-latency data found for YCSB.")

    ycsb_X = [ycsb_data[op] / CONVERT_TO_MS for op in operations]
    tectonic_X = [
        tectonic_data[op] / CONVERT_TO_MS for op in operations if op in tectonic_data
    ]

    labels = [op if op != "pointquery" else "point\nquery" for op in operations]

    fig, ax = plt.subplots(figsize=(4, 3.5), dpi=150)
    positions = np.arange(len(operations))
    width = 0.4

    # YCSB boxplots
    bp_ycsb = ax.boxplot(
        ycsb_X,
        positions=positions - width / 2,
        widths=0.25,
        patch_artist=True,
        showfliers=False,
        whis=[0, 99],
    )
    for patch in bp_ycsb["boxes"]:
        patch.set_facecolor("white")
        patch.set_edgecolor("grey")
        patch.set_hatch("///")
    for element in ["whiskers", "caps", "medians"]:
        for item in bp_ycsb[element]:
            item.set_color("black")

    # Tectonic boxplots
    bp_tec = ax.boxplot(
        tectonic_X,
        positions=positions + width / 2,
        widths=0.25,
        patch_artist=True,
        showfliers=False,
        whis=[0, 99],
    )
    for patch in bp_tec["boxes"]:
        patch.set_facecolor("tab:red")
        patch.set_edgecolor("tab:red")
    for element in ["whiskers", "caps", "medians"]:
        for item in bp_tec[element]:
            item.set_color("black")

    ax.set_yscale("log")
    ax.set_ylim(1e0)
    # Axis labels
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.set_ylabel("latency ($\\mu$s)")
    # ax.set_ylim(0)

    # Save main plot
    output_file = OUTPUT_DIR / "op_latency_box.pdf"
    fig.savefig(output_file, bbox_inches="tight", pad_inches=0.03)
    print(f"Saved: {output_file}")

    # Save legend separately
    legend_fig = plt.figure(figsize=(2.5, 1.2))
    legend_fig.legend(
        [bp_ycsb["boxes"][0], bp_tec["boxes"][0]],
        ["YCSB", "Tectonic"],
        loc="center",
        ncol=2,
        frameon=False,
        borderaxespad=0,
        labelspacing=0,
        borderpad=0,
        columnspacing=0.5,
        handletextpad=0.3,
    )
    legend_file = OUTPUT_DIR / "legend2.pdf"
    legend_fig.savefig(legend_file, bbox_inches="tight", pad_inches=0.015)
    print(f"Saved: {legend_file}")


def main():
    plot_latency_boxplot()


if __name__ == "__main__":
    main()
