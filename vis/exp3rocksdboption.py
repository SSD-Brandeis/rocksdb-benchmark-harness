
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import os
import re
import json
import numpy as np
from glob import glob

from style import bar_styles, bar_hatches

convert_to_gib = 1024.0 * 1024.0 * 1024.0  # bytes → GiB

prop = font_manager.FontProperties(
    fname="../LinLibertine_Mah.ttf"
)


plt.rcParams['font.family'] = prop.get_name()
plt.rcParams['text.usetex'] = True
plt.rcParams['font.weight'] = 'normal'
plt.rcParams['font.size'] = 20

BASE = "../experiments/workload-similarity"
PLOTS_DIR = "../plots"
MiB = 1024.0 * 1024.0

def load_entry_size_bytes():
    spec_path = os.path.join(BASE, "workload-a.spec.json")
    default = 1123
    if not os.path.exists(spec_path):
        print(f"[warn] {spec_path} not found; default entry_size={default} bytes")
        return default
    try:
        with open(spec_path) as f:
            spec = json.load(f)
        for k in ["entry_size", "record_size", "value_size", "value_bytes", "valueLen", "value_len", "value_bytes_per_key"]:
            if k in spec and isinstance(spec[k], (int, float)) and spec[k] > 0:
                return float(spec[k])
        for container in spec.values():
            if isinstance(container, dict):
                for k in ["entry_size", "record_size", "value_size"]:
                    if k in container and isinstance(container[k], (int, float)) and container[k] > 0:
                        return float(container[k])
    except Exception as e:
        print(f"[warn] could not parse workload spec for entry size: {e}")
    print(f"[warn] entry size unknown; defaulting to {default} bytes")
    return default

COUNT_LINE = re.compile(r"^(rocksdb\.[A-Za-z0-9\.\-_]+)\s+COUNT\s*:\s*([0-9]+)\s*$")
COUNT_IN_METRIC = re.compile(r"^(rocksdb\.[A-Za-z0-9\.\-_]+)\s+.*?\bCOUNT\s*:\s*([0-9]+)\b")

def parse_stats_file(path):
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

def avg_metrics_for_system(system):
    paths = sorted(glob(os.path.join(BASE, f"stats.{system}.*.json")))
    if not paths:
        raise RuntimeError(f"No stats files for system '{system}'")
    acc, cnt = {}, 0
    for p in paths:
        m = parse_stats_file(p)
        if not m:
            continue
        cnt += 1
        for k, v in m.items():
            acc[k] = acc.get(k, 0) + v
    if cnt == 0:
        raise RuntimeError(f"No parsable stats for system '{system}'")
    for k in acc:
        acc[k] = acc[k] / cnt
    return acc

def bar_two_systems(title, y_vals, ylabel, outname, as_mib=False):
    labels = ["YCSB", "Tectonic"]
    x = np.arange(2)
    width = 0.6

    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    vals = [y_vals.get("ycsb", 0.0), y_vals.get("tectonic", 0.0)]
    if as_mib:
        vals = [v / MiB for v in vals]

    sY, sT = bar_styles["YCSB"], bar_styles["Tectonic"]
    ax.bar(x[0], vals[0], width, color=sY["color"], edgecolor=sY["edgecolor"], hatch=sY["hatch"], label="YCSB")
    ax.bar(x[1], vals[1], width, color=sT["color"], edgecolor=sT["edgecolor"], hatch=sT["hatch"], label="Tectonic")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    
    os.makedirs(PLOTS_DIR, exist_ok=True)
    out = os.path.join(PLOTS_DIR, outname)
    fig.savefig(out, bbox_inches='tight', pad_inches=0.03)
    print(f"Saved: {out}")
    plt.close(fig)

def grouped_two_bars_per_system(title, y_pairs, ylabel, outname, as_mib=False, names=("A","B")):
    systems = ["YCSB", "Tectonic"]
    x = np.arange(2)
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    ycsb_a, ycsb_b = y_pairs["ycsb"]
    tec_a, tec_b = y_pairs["tectonic"]
    if as_mib:
        ycsb_a, ycsb_b = ycsb_a / MiB, ycsb_b / MiB
        tec_a, tec_b = tec_a / MiB, tec_b / MiB

    sY, sT = bar_styles["YCSB"], bar_styles["Tectonic"]
    ax.bar(x[0]-width/2, ycsb_a, width, color=sY["color"], edgecolor=sY["edgecolor"], hatch=bar_hatches[0], label=f"YCSB {names[0]}")
    ax.bar(x[0]+width/2, ycsb_b, width, color=sY["color"], edgecolor=sY["edgecolor"], hatch=bar_hatches[1], label=f"YCSB {names[1]}")
    ax.bar(x[1]-width/2, tec_a, width, color=sT["color"], edgecolor=sT["edgecolor"], hatch=bar_hatches[0], label=f"Tectonic {names[0]}")
    ax.bar(x[1]+width/2, tec_b, width, color=sT["color"], edgecolor=sT["edgecolor"], hatch=bar_hatches[1], label=f"Tectonic {names[1]}")

    ax.set_xticks(x)
    ax.set_xticklabels(systems)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    ax.legend(frameon=False, ncol=2, loc='upper center', bbox_to_anchor=(0.5, -0.18))
    fig.subplots_adjust(bottom=0.22)

    os.makedirs(PLOTS_DIR, exist_ok=True)
    out = os.path.join(PLOTS_DIR, outname)
    fig.savefig(out, bbox_inches='tight', pad_inches=0.03)
    print(f"Saved: {out}")
    plt.close(fig)

def triple_group(title, triples, ylabel, outname, bar_names):
    systems = ["YCSB", "Tectonic"]
    x = np.arange(2)
    width = 0.22
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    sY, sT = bar_styles["YCSB"], bar_styles["Tectonic"]
    print(f"[{title}] YCSB: {triples['ycsb']}, Tectonic: {triples['tectonic']}")

    # YCSB three bars
    a, b, c = triples["ycsb"]
    ax.bar(x[0]-width, a, width, color=sY["color"], edgecolor=sY["edgecolor"], hatch=bar_hatches[0], label=f"YCSB {bar_names[0]}")
    ax.bar(x[0],       b, width, color=sY["color"], edgecolor=sY["edgecolor"], hatch=bar_hatches[1], label=f"YCSB {bar_names[1]}")
    ax.bar(x[0]+width, c, width, color=sY["color"], edgecolor=sY["edgecolor"], hatch=bar_hatches[2], label=f"YCSB {bar_names[2]}")

    # Tectonic three bars
    a, b, c = triples["tectonic"]
    ax.bar(x[1]-width, a, width, color=sT["color"], edgecolor=sT["edgecolor"], hatch=bar_hatches[0], label=f"Tectonic {bar_names[0]}")
    ax.bar(x[1],       b, width, color=sT["color"], edgecolor=sT["edgecolor"], hatch=bar_hatches[1], label=f"Tectonic {bar_names[1]}")
    ax.bar(x[1]+width, c, width, color=sT["color"], edgecolor=sT["edgecolor"], hatch=bar_hatches[2], label=f"Tectonic {bar_names[2]}")

    ax.set_xticks(x)
    ax.set_xticklabels(systems)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    ax.legend(frameon=False, ncol=3, loc='upper center', bbox_to_anchor=(0.5, -0.18))
    fig.subplots_adjust(bottom=0.25)

    os.makedirs(PLOTS_DIR, exist_ok=True)
    out = os.path.join(PLOTS_DIR, outname)
    fig.savefig(out, bbox_inches='tight', pad_inches=0.03)
    print(f"Saved: {out}")
    plt.close(fig)

def main():
    entry_size = load_entry_size_bytes()
    print(f"[info] entry_size assumed = {entry_size} bytes")

    m_y = avg_metrics_for_system("ycsb")
    m_t = avg_metrics_for_system("tectonic")
   
   
    
    # 1) Actual bytes written (avg)
    bytes_written = {
        "ycsb": float(m_y.get("rocksdb.wal.bytes",0 )+m_y.get("rocksdb.flush.write.bytes",0 )+m_y.get("rocksdb.compact.write.bytes",0 )),
        "tectonic": float(m_t.get("rocksdb.wal.bytes",0 )+m_t.get("rocksdb.flush.write.bytes",0 )+m_t.get("rocksdb.compact.write.bytes",0 )),
    }
    # bar_two_systems("Actual bytes written", bytes_written, "MiB", "stats_bytes_written.pdf", as_mib=True)
    # print (bytes_written)

    # 2) Write amplification = actual_written / (num_inserts * entry_size)
    num_inserts = {
        "ycsb": float(m_y.get("rocksdb.number.keys.written", 0)),
        "tectonic": float(m_t.get("rocksdb.number.keys.written", 0)),
    }
    # logical_written = {k: num_inserts[k] * entry_size for k in num_inserts}
    # print (logical_written)
    # write_amp = {k: (bytes_written[k] / logical_written[k]) if logical_written[k] > 0 else 0.0 for k in bytes_written}
    # bar_two_systems("Write amplification", write_amp, "amplification (x)", "stats_write_amplification.pdf", as_mib=False)

    # 3) Actual bytes read (avg)
 
    bytes_read = {
        "ycsb": float(m_y.get("rocksdb.bytes.read", 0) + m_y.get("rocksdb.compact.read.bytes", 0)),
        "tectonic": float(m_t.get("rocksdb.bytes.read", 0) + m_t.get("rocksdb.compact.read.bytes", 0)),
    }
    # bar_two_systems("Actual bytes read", bytes_read, "MiB", "stats_bytes_read.pdf", as_mib=True)


    # 5) Compaction read/write bytes (grouped 2 bars per system)
    comp_pairs = {
        "ycsb": (float(m_y.get("rocksdb.compact.read.bytes", 0)),
                 float(m_y.get("rocksdb.compact.write.bytes", 0))),
        "tectonic": (float(m_t.get("rocksdb.compact.read.bytes", 0)),
                     float(m_t.get("rocksdb.compact.write.bytes", 0))),
    }
    # grouped_two_bars_per_system("Compaction bytes", comp_pairs, "MiB", "stats_compaction_bytes.pdf", as_mib=True, names=("read","write"))


    # Prepare data
    categories = ["read", "write"]
    ycsb_vals = [bytes_read["ycsb"] / convert_to_gib, bytes_written["ycsb"] / convert_to_gib]
    tectonic_vals = [bytes_read["tectonic"] / convert_to_gib, bytes_written["tectonic"] / convert_to_gib]

    x = np.arange(len(categories))  # positions for categories
    width = 0.25  # width of each bar

    fig, ax = plt.subplots(figsize=(2.5, 3.5), dpi=150)

    # Bars
    ax.bar(x - width/2, ycsb_vals, width, **bar_styles["YCSB"])
    ax.bar(x + width/2, tectonic_vals, width, **bar_styles["Tectonic"])

    # Labels & formatting
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("bytes (GB)")
    ax.set_xlabel("operation")
    # ax.legend()
    ax.set_xlim(-0.3, 0.3)

    fig.savefig("../plots/read_write.pdf", bbox_inches='tight', pad_inches=0.03)



    # 4) Read amplification = actual_read / (num_point_queries * entry_size)
    num_reads = {
        "ycsb": float(m_y.get("rocksdb.number.keys.read", 0)),
        "tectonic": float(m_t.get("rocksdb.number.keys.read", 0)),
    }
    logical_read = {k: num_reads[k] * entry_size for k in num_reads}
    read_amp = {k: (bytes_read[k] / logical_read[k]) if logical_read[k] > 0 else 0.0 for k in bytes_read}
    bar_two_systems("Read amplification", read_amp, "amplification (×)", "stats_read_amplification.pdf", as_mib=False)

    # 6) Compaction vs Flush counts 
    comp_flush_pairs = {
        "ycsb": (float(m_y.get("rocksdb.compaction.times.micros", 0)),
                 float(m_y.get("rocksdb.db.flush.micros", 0))),
        "tectonic": (float(m_t.get("rocksdb.compaction.times.micros", 0)),
                     float(m_t.get("rocksdb.db.flush.micros", 0))),
    }
    grouped_two_bars_per_system("Event counts: compaction vs flush", comp_flush_pairs,
                                "count", "stats_compact_flush_counts.pdf", as_mib=False, names=("compaction","flush"))

    # 7) Block cache: cache miss / cache hit
    cache_pairs = {
    "ycsb": (
        float(m_y.get("rocksdb.block.cache.miss", 0)),
        float(m_y.get("rocksdb.block.cache.hit", 0)),
    ),
    "tectonic": (
        float(m_t.get("rocksdb.block.cache.miss", 0)),
        float(m_t.get("rocksdb.block.cache.hit", 0)),
    ),
    }

    convert_to_million = 1_000_000

    categories = [ "cache\nhit", "cache\nmiss"]
    ycsb_vals = [
        cache_pairs["ycsb"][1] / convert_to_million,
        cache_pairs["ycsb"][0] / convert_to_million,
    ]
    tectonic_vals = [
        cache_pairs["tectonic"][1] / convert_to_million,
        cache_pairs["tectonic"][0] / convert_to_million,
    ]


    x = np.arange(len(categories)) 
    # x = np.array([0, 0.8])  
    width = 0.25 
    fig, ax = plt.subplots(figsize=(2.8, 3.5), dpi=150)

    # Bars
    ax.bar(x - width/2, ycsb_vals, width, **bar_styles["YCSB"])
    ax.bar(x + width/2, tectonic_vals, width, **bar_styles["Tectonic"])

    # Labels & formatting
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("count (millions)")
    # ax.set_xlabel("cache")
    # ax.set_xlim(-0.5, 1) 
    
    ax.set_yticklabels([0] + [f"{tick}" for tick in ax.get_yticks()[1:]])


    ax.set_xlim(-0.5, len(categories)-0.5)


    fig.savefig("../plots/block_cache.pdf", bbox_inches='tight', pad_inches=0.03)


    # 8) SST level hits: L0 / L1 / L2+ 
    level_triples = {
        "ycsb": (float(m_y.get("rocksdb.l0.hit", 0)),
                 float(m_y.get("rocksdb.l1.hit", 0)),
                 float(m_y.get("rocksdb.l2andup.hit", 0))),
        "tectonic": (float(m_t.get("rocksdb.l0.hit", 0)),
                     float(m_t.get("rocksdb.l1.hit", 0)),
                     float(m_t.get("rocksdb.l2andup.hit", 0))),
    }
    triple_group("SST level hits: L0 / L1 / L2+", level_triples, "count", "stats_level_hits.pdf",
                 bar_names=["L0", "L1", "L2+"])

if __name__ == "__main__":
    main()
