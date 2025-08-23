import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import os
import json
import numpy as np

prop = font_manager.FontProperties(
    fname="../LinLibertine_Mah.ttf"
)
plt.rcParams['font.family'] = prop.get_name()
plt.rcParams['text.usetex'] = True
plt.rcParams['font.weight'] = 'normal'
plt.rcParams['font.size'] = 20

BASE = "../experiments/workload-similarity"
convert_to_ms = 1000.0  # nanoseconds → microseconds

def load_op_latency(system: str):
    ops = {"insert": [], "pointquery": [], "update": []}
    for i in range(1, 6):
        p = os.path.join(BASE, f"op-latency.{system}.{i}.json")
        if not os.path.exists(p):
            continue
        with open(p) as f:
            arr = json.load(f)
        for d in arr:
            op = str(d.get("operation", "")).lower().replace(" ", "")
            if op in ("insert", "update", "pointquery"):
                ops[op].append(float(d["latency"]))
    return {k: np.array(v, dtype=float) for k, v in ops.items() if len(v) > 0}

# def stats_str(x: np.ndarray):
#     q = np.percentile(x, [25, 50, 75, 95])
#     return (
#         f"min={np.min(x):.3f}  "
#         f"p25={q[0]:.3f}  p50={q[1]:.3f}  p75={q[2]:.3f}  "
#         f"p95={q[3]:.3f}  "
#         # f"p95={q[3]:.3f}  p99={q[4]:.3f}  max={np.max(x):.3f}"
#     )

def plot_system():
    ycsb_data = load_op_latency("ycsb")
    tectonic_data = load_op_latency("tectonic")
    order = [op for op in ["insert", "pointquery", "update"] if op in ycsb_data]
    if not order:
        raise RuntimeError(f"No op-latency ycsb_data found.")
    ycsb_X = [ycsb_data[op] / convert_to_ms for op in order]
    tectonic_X = [tectonic_data[op] / convert_to_ms for op in order if op in tectonic_data]

    labels = [op if op != "pointquery" else "point query" for op in order]

    fig, ax = plt.subplots(figsize=(5, 3.5), dpi=150)
    positions = np.arange(len(order))  # x-axis positions
    width = 0.35  # spacing between the two systems

    # YCSB boxplots
    bp1 = ax.boxplot(
        ycsb_X,
        positions=positions - width/2,
        widths=0.25,
        patch_artist=True,
        showfliers=False,
        whis=[0, 99]
    )
    # Style YCSB (hatching + solid line)
    for patch in bp1['boxes']:
        patch.set_facecolor("white")
        patch.set_edgecolor("grey")
        patch.set_hatch("///")   # diagonal lines
    for whisker in bp1['whiskers']:
        whisker.set_color("black")
        whisker.set_linestyle("-")
    for cap in bp1['caps']:
        cap.set_color("black")
    for median in bp1['medians']:
        median.set_color("black")
        # median.set_linewidth(2)

    # Tectonic boxplots
    bp2 = ax.boxplot(
        tectonic_X,
        positions=positions + width/2,
        widths=0.25,
        patch_artist=True,
        showfliers=False,
        whis=[0, 99]
    )
    # Style Tectonic (different hatch + dashed lines)
    for patch in bp2['boxes']:
        patch.set_facecolor("tab:red")
        patch.set_edgecolor("tab:red")
        patch.set_hatch("")  # opposite diagonal lines
    for whisker in bp2['whiskers']:
        whisker.set_color("black")
        whisker.set_linestyle("-")
    for cap in bp2['caps']:
        cap.set_color("black")
    for median in bp2['medians']:
        median.set_color("black")
        # median.set_linewidth(2)

    # Axis labels
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    # ax.set_xlabel("operation type")
    ax.set_ylim(0)
    # latex version of micro seconds
    ax.set_ylabel("latency ($\\mu$s)")

    # # Legend (use the boxes directly as handles)
    # handles, labels = ax.get_legend_handles_labels()
    legend_fig = plt.figure(figsize=(2.5, 1.2))
    legend_fig.legend([bp1["boxes"][0], bp2["boxes"][0]], ["YCSB", "Tectonic"], loc="center", ncol=2, frameon=False,  borderaxespad=0, labelspacing=0, borderpad=0, columnspacing=1.0)
    legend_fig.savefig('../plots/legend2.pdf', bbox_inches='tight', pad_inches=0.015)


    # ax.legend([bp1["boxes"][0], bp2["boxes"][0]], ["YCSB", "Tectonic"], loc="upper right", ncol=2, frameon=False)

    os.makedirs("../plots", exist_ok=True)
    out = f"../plots/op_latency_box.pdf"
    fig.savefig(out, bbox_inches='tight', pad_inches=0.03)
    print(f"Saved: {out}")

    # for op in order:
    #     print(f"{system} :: {op}: {stats_str(ycsb_data[op])}")

def main():
    plot_system()

if __name__ == "__main__":
    main()
