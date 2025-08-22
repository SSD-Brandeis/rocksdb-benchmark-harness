import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import os
import json
import numpy as np

prop = font_manager.FontProperties(
    fname="/Users/cba/Desktop/tectonic/LinLibertine_Mah.ttf"
)
plt.rcParams['font.family'] = prop.get_name()
plt.rcParams['text.usetex'] = True
plt.rcParams['font.weight'] = 'normal'
plt.rcParams['font.size'] = 22

BASE = "/Users/cba/Desktop/rocksdb-benchmark-harness/experiments/workload-similarity"

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

def stats_str(x: np.ndarray):
    q = np.percentile(x, [25, 50, 75, 95])
    return (
        f"min={np.min(x):.3f}  "
        f"p25={q[0]:.3f}  p50={q[1]:.3f}  p75={q[2]:.3f}  "
        f"p95={q[3]:.3f}  "
        # f"p95={q[3]:.3f}  p99={q[4]:.3f}  max={np.max(x):.3f}"
    )

def plot_system(system: str):
    data = load_op_latency(system)
    order = [op for op in ["insert", "pointquery", "update"] if op in data]
    if not order:
        raise RuntimeError(f"No op-latency data found for {system}.")
    X = [data[op] for op in order]
    labels = [op.capitalize() if op != "pointquery" else "PointQuery" for op in order]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
    ax.boxplot(X, tick_labels=labels, showfliers=False, whis=[0, 95])
    ax.set_xlabel("operation type")
    ax.set_ylabel("latency")
    ax.set_ylim(0, 45000)  # Adjust as needed based on expected latencies
    ax.set_title(f"{system.capitalize()}")

    # ---- draw p95
    first = True
    for i, op in enumerate(order, start=1):
        p95 = np.percentile(data[op], 95)
        ax.scatter(i, p95, marker="x", s=60, color="tab:blue",
                   linewidths=2, label="p95" if first else "_nolegend_")
        first = False

    # ---- draw p60
    # first = True
    for i, op in enumerate(order, start=1):
        p60 = np.percentile(data[op], 60)
        ax.scatter(i, p60, marker="x", s=60, color="tab:orange",
                   linewidths=2, label="p60" if first else "_nolegend_")
        # first = False
    # ---- draw p70
    # first = True
    for i, op in enumerate(order, start=1):
        p70 = np.percentile(data[op], 70)
        ax.scatter(i, p70, marker="x", s=60, color="tab:red",
                   linewidths=2, label="p70" if first else "_nolegend_")
    # ---- draw p99 
    # first = True
    # for i, op in enumerate(order, start=1):
    #     p99 = np.percentile(data[op], 99)
    #     ax.scatter(i, p99, marker="*", s=120, color="tab:red",
    #                linewidths=1.5, label="p99" if first else "_nolegend_")
    #     first = False

    ax.legend(frameon=False, loc="upper right")

    os.makedirs("../plots", exist_ok=True)
    out = f"../plots/op_latency_box_{system}.pdf"
    fig.savefig(out, bbox_inches='tight', pad_inches=0.03)
    print(f"Saved: {out}")

    for op in order:
        print(f"{system} :: {op}: {stats_str(data[op])}")

def main():
    plot_system("ycsb")
    plot_system("tectonic")

if __name__ == "__main__":
    main()
