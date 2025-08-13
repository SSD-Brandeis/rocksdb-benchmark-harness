from collections import defaultdict
import json
import typing as t
import matplotlib.pyplot as plt
from glob import glob
from collections import Counter
import numpy as np
import statsmodels.api as sm
from statsmodels.genmod import families
from statsmodels.genmod.families.links import logit
from statsmodels.genmod.generalized_linear_model import GLM

from statsmodels.othermod.betareg import BetaModel

def main():
    # workload_similarity_iostat()
    # workload_similarity_op_latency()
    workload_similarity_counting()


def workload_similarity_op_latency():
    def load_data(path: str):
        with open(path) as f:
            data_raw = json.load(f)

        return [d["latency"] for d in data_raw]

    data = load_data("../experiments/workload-similarity/ops.json")
    plt.figure(figsize=(10, 6), dpi=150)
    plt.plot(list(range(len(data))), data, label="latency")
    plt.yscale("log")
    plt.savefig("../workload-similarity-op-latency.png")


def workload_similarity_iostat():
    def load_data(path: str):
        with open(path) as f:
            iostat_data_raw = json.load(f)

        iostat_data = []
        for stat in iostat_data_raw["sysstat"]["hosts"][0]["statistics"]:
            dat: dict[str, t.Any] = stat["disk"][0]
            # iostat_data.append({"kB_read": dat["kB_read"], "kB_wrtn": dat["kB_wrtn"]})
            iostat_data.append({"kB_read": dat["kB_read/s"], "kB_wrtn": dat["kB_wrtn/s"]})
        return iostat_data


    datas_tec = [
        load_data(path)
        for path in glob("../experiments/workload-similarity/iostat.tectonic.*.json")
    ]
    datas_ycsb = [
        load_data(path)
        for path in glob("../experiments/workload-similarity/iostat.yscb.*.json")
    ]


    def plot_datas(datas, name: str):
        plt.figure(figsize=(10, 6), dpi=150)
        for i, iostat_data in enumerate(datas):
            keys = iostat_data[0].keys()
            x = list(range(len(iostat_data)))

            for key in keys:
                y = [d[key] for d in iostat_data]
                plt.plot(x, y, label=f"{key}-{i}", alpha=0.25)

        max_len = max(len(iostat_data) for iostat_data in datas)
        avgs = []
        for i in range(max_len):
            cols = [data[i] for data in datas if i < len(data)]
            keys = cols[0].keys()
            data_avg = defaultdict(float)
            for col in cols:
                for key in keys:
                    data_avg[key] += col[key]

            for key in keys:
                data_avg[key] /= len(cols)

            avgs.append(data_avg)

        for key in avgs[0].keys():
            x = list(range(max_len))
            y = [d[key] for d in avgs]
            plt.plot(x, y, label=f"{key}-avg")

        # plt.yscale("log")
        plt.legend()
        plt.ylim(top=800_000)
        plt.savefig(f"../iostat.{name}-ps.png")

    plot_datas(datas_tec, "tectonic")
    plot_datas(datas_ycsb, "ycsb")

def workload_similarity_counting():
    def count_workload(filename: str) -> tuple[Counter, ...]:
        with open(filename) as f:
            counter_op = Counter()
            counter_i = Counter()
            counter_u = Counter()
            counter_pq = Counter()
            for line in f.readlines():
                parts = line.strip().split(" ")
                op = parts[0]
                key = parts[1]

                counter_op[op] += 1

                if op == "I":
                    counter_i[key] += 1
                elif op == "U":
                    counter_u[key] += 1
                elif op == "P":
                    counter_pq[key] += 1


        return counter_op, counter_i, counter_u, counter_pq

    tec_op, tec_i, tec_u, tec_pq = count_workload("../experiments/workload-similarity/tec-workload-a.txt")
    ycsb_op, ycsb_i, ycsb_u, ycsb_pq = count_workload("../experiments/workload-similarity/ycsb-workload-a.txt")
    print("tec", tec_op)
    print("ycsb", ycsb_op)

    print(f"{tec_u.total()=} {len(set(tec_u.keys()))=}")
    # for x in tec_u.most_common(100):
    #     print(x)

    print(f"{ycsb_u.total()=} {len(set(ycsb_u.keys()))=}")

    POINTS = 100
    tec_u_counts = [count for _, count in tec_u.most_common(POINTS)]
    tec_u_counts = np.array(tec_u_counts)
    ycsb_u_counts = [count for _, count in ycsb_u.most_common(POINTS)]
    ycsb_u_counts = np.array(ycsb_u_counts)

    data = {
        "tec": tec_u_counts,
        "ycsb": ycsb_u_counts,
    }
    bottom = np.zeros(POINTS)
    for label, counts in data.items():
        plt.bar(list(range(POINTS)), counts, label=label, bottom=bottom)
        bottom += counts
    plt.legend()
    plt.savefig("../workload-similarity-count.png")



    # def plot_bar(keys: Counter):
    #     # pruned_counts = Counter({key: count for key, count in keys.items() if count > 1})
    #     # print(pruned_counts.total())
    #     pruned_counts = keys
    #     # keys, counts = zip(*pruned_counts.most_common())
    #
    #     # Create bar chart
    #     plt.bar(keys, counts)
    #     plt.xlabel("keys")
    #     plt.ylabel("Count")
    #     plt.title("Key Frequency Histogram")
    #     plt.savefig("../workload-similarity-count.png")

    # plot_bar(tec_key)

if __name__ == "__main__":
    main()
