#!/usr/bin/env python3
import json
import re
from pathlib import Path
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from style import bar_styles

# Use non-interactive backend
matplotlib.use("Agg")

TAG = "100x"

# Constants
BASE_DIR = Path(f"../experiments/workload-similarity/{TAG}")
PLOTS_DIR = Path("../plots")
PLOTS_DIR.mkdir(exist_ok=True)
CONVERT_TO_TIB = 1024**4  # bytes → TiB
CONVERT_TO_MILLION = 1_000_000

# Font setup
FONT_PATH = "../LinLibertine_Mah.ttf"
prop = font_manager.FontProperties(fname=FONT_PATH)
plt.rcParams["font.family"] = prop.get_name()
plt.rcParams["text.usetex"] = True
plt.rcParams["font.size"] = 20

COUNT_LINE = re.compile(r"^(rocksdb\.[A-Za-z0-9\.\-_]+)\s+COUNT\s*:\s*([0-9]+)\s*$")
COUNT_IN_METRIC = re.compile(
    r"^(rocksdb\.[A-Za-z0-9\.\-_]+)\s+.*?\bCOUNT\s*:\s*([0-9]+)\b"
)


def parse_stats_file(path: Path) -> dict:
    metrics = {}
    with open(path, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            m = COUNT_LINE.match(line)
            if m:
                metrics[m.group(1)] = int(m.group(2))
                continue
            m2 = COUNT_IN_METRIC.match(line)
            if m2:
                metrics[m2.group(1)] = int(m2.group(2))
    return metrics


def avg_metrics(system: str) -> dict:
    files = sorted(BASE_DIR.glob(f"stats.{system}.*.json"))
    if not files:
        raise RuntimeError(f"No stats files for system '{system}'")
    acc = {}
    count = 0
    for f in files:
        metrics = parse_stats_file(f)
        if not metrics:
            continue
        count += 1
        for k, v in metrics.items():
            acc[k] = acc.get(k, 0) + v
    if count == 0:
        raise RuntimeError(f"No parsable stats for system '{system}'")
    return {k: v / count for k, v in acc.items()}


def plot_read_write(m_y, m_t):
    bytes_read = m_y.get("rocksdb.bytes.read", 0) + m_y.get(
        "rocksdb.compact.read.bytes", 0
    )
    bytes_written = (
        m_y.get("rocksdb.wal.bytes", 0)
        + m_y.get("rocksdb.flush.write.bytes", 0)
        + m_y.get("rocksdb.compact.write.bytes", 0)
    )
    ycsb_vals = np.array([bytes_read, bytes_written]) / CONVERT_TO_TIB

    bytes_read_t = m_t.get("rocksdb.bytes.read", 0) + m_t.get(
        "rocksdb.compact.read.bytes", 0
    )
    bytes_written_t = (
        m_t.get("rocksdb.wal.bytes", 0)
        + m_t.get("rocksdb.flush.write.bytes", 0)
        + m_t.get("rocksdb.compact.write.bytes", 0)
    )
    tectonic_vals = np.array([bytes_read_t, bytes_written_t]) / CONVERT_TO_TIB

    categories = ["read", "write"]
    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(2.5, 3.5), dpi=150)
    ax.bar(x - width / 2, ycsb_vals, width, **bar_styles["YCSB"])
    ax.bar(x + width / 2, tectonic_vals, width, **bar_styles["Tectonic"])

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("bytes (TB)")
    ax.set_yticklabels([0] + [f"{tick}" for tick in ax.get_yticks()[1:]])
    fig.savefig(PLOTS_DIR / "read_write.pdf", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"Saved: {PLOTS_DIR / 'read_write.pdf'}")


def plot_block_cache(m_y, m_t):
    ycsb_vals = (
        np.array(
            [
                m_y.get("rocksdb.block.cache.hit", 0),
                m_y.get("rocksdb.block.cache.miss", 0),
            ]
        )
        / CONVERT_TO_MILLION
    )
    tectonic_vals = (
        np.array(
            [
                m_t.get("rocksdb.block.cache.hit", 0),
                m_t.get("rocksdb.block.cache.miss", 0),
            ]
        )
        / CONVERT_TO_MILLION
    )

    categories = ["cache\nhit", "cache\nmiss"]
    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(2.5, 3.5), dpi=150)
    ax.bar(x - width / 2, ycsb_vals, width, **bar_styles["YCSB"])
    ax.bar(x + width / 2, tectonic_vals, width, **bar_styles["Tectonic"])

    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("count (millions)")

    ax.set_yticklabels([0] + [f"{int(tick) if tick/tick > 0 else tick}" for tick in ax.get_yticks()[1:]])

    fig.savefig(PLOTS_DIR / "block_cache.pdf", bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"Saved: {PLOTS_DIR / 'block_cache.pdf'}")


def main():
    m_y = avg_metrics("ycsb")
    m_t = avg_metrics("tectonic")
    plot_read_write(m_y, m_t)
    plot_block_cache(m_y, m_t)


if __name__ == "__main__":
    main()
