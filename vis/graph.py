import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import numpy as np
    from scipy import stats
    import matplotlib.pyplot as plt
    from collections import Counter
    from sys import float_info
    import marimo as mo
    if mo.running_in_notebook():
        from tqdm.notebook import tqdm
    else:
        from tqdm import tqdm

    from enum import StrEnum
    from pathlib import Path

    return Counter, Path, StrEnum, float_info, mo, np, plt, stats, tqdm


@app.cell
def _(Path):
    def find_project_root(start: Path | None = None, marker: str = ".git") -> Path:
        """
        Search upwards from `start` (or current file) until a directory
        containing `marker` exists. Returns the root Path.
        Raises FileNotFoundError if not found.
        """
        if start is None:
            start = Path(__file__).resolve()

        # Start from the containing directory if it's a file
        current = start if start.is_dir() else start.parent

        for parent in [current, *current.parents]:
            if (parent / marker).exists():
                return parent

        raise FileNotFoundError(f"Could not find {marker} upwards from {start}")

    return (find_project_root,)


@app.cell
def _(np, stats):
    # Method 1: Method of Moments
    def estimate_beta_params_mom(samples):
        """Estimate Beta distribution parameters using method of moments"""
        mean = np.mean(samples)
        var = np.var(samples, ddof=1)  # Use sample variance

        # For Beta(α, β):
        # mean = α / (α + β)
        # var = (α * β) / ((α + β)² * (α + β + 1))

        # Solving for α and β:
        # Let s = α + β, then:
        # mean = α / s  =>  α = mean * s
        # β = s - α = s * (1 - mean)
        # var = (mean * (1-mean) * s) / (s² * (s + 1)) = (mean * (1-mean)) / (s * (s + 1))

        common_factor = (mean * (1 - mean) / var) - 1
        alpha_est = mean * common_factor
        beta_est = (1 - mean) * common_factor

        return alpha_est, beta_est

    # Method 2: Maximum Likelihood Estimation (using scipy)
    def estimate_beta_params_mle(samples):
        """Estimate Beta distribution parameters using MLE"""
        # scipy.stats.beta.fit returns (a, b, loc, scale)
        # For standard beta distribution, loc=0 and scale=1
        params = stats.beta.fit(samples, floc=0, fscale=1)
        return params[0], params[1]  # Return only alpha and beta
    return (estimate_beta_params_mle,)


@app.cell
def _(Counter, StrEnum, float_info, np, tqdm):
    class OpChar(StrEnum):
        INSERT = "I"
        UPDATE = "U"
        MERGE = "M"
        DELETE_POINT = "D"
        DELETE_RANGE = "R"
        QUERY_POINT = "P"
        QUERY_RANGE = "S"

    def bytes_to_human(n_bytes: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB"]
        size = float(n_bytes)
        for unit in units:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def array_stats(arr: list[int]) -> dict:
        arr = np.asarray(arr)  # ensure it's a numpy array

        percentiles = np.percentile(arr, [25, 50, 75, 95, 99])

        return {
            "min": np.min(arr),
            "p25": percentiles[0],
            "p50": percentiles[1],  # median
            "p75": percentiles[2],
            "p95": percentiles[3],
            "p99": percentiles[4],
            "max": np.max(arr),
            "mean": np.mean(arr),
            "std": np.std(arr, ddof=1),  # sample std dev
        }


    def count_workload(filename: str):
        print(f"counting {filename}")
        with open(filename) as f:
            lines = f.readlines()

        db = {}
        keys = []
        key_to_idx = {}
        bytes_written = 0
        bytes_read = 0

        key_len = []
        insert_val_len = []
        insert_duplicates = 0

        update_idx = []
        update_counter = Counter()
        update_val_len = []

        point_query_idx = []
        point_query_counter = Counter()
        empty_point_query_count = 0

        pq_val_len = []


        for line in tqdm(lines):
            line = line.strip()
            if line.startswith(OpChar.INSERT):
                _, key, val = line.split(" ", maxsplit=2)
                if key in db:
                    insert_duplicates += 1

                db[key] = val
                keys.append(key)
                key_to_idx[key] = len(keys) - 1

                key_len.append(len(key))
                bytes_written += len(key) + len(val)
                insert_val_len.append(len(val))

            elif line.startswith(OpChar.UPDATE):
                _, key, value = line.split(" ", maxsplit=2)
                db[key] = val

                idx = key_to_idx[key]
                update_idx.append(max(idx / len(keys), float_info.epsilon))
                update_val_len.append(len(val))
                bytes_written += len(key) + len(val)
                update_counter[key] += 1
            elif line.startswith(OpChar.QUERY_POINT):
                _, key = line.split(" ", maxsplit=1)
                bytes_read += len(key) + len(val) 

                val = db.get(key)
                if val is None:
                    empty_point_query_count += 1
                    continue
                pq_val_len.append(len(val))
                point_query_counter[key] += 1
                idx = key_to_idx[key]
                point_query_idx.append(max(idx / len(keys), float_info.epsilon))

        print(f"{empty_point_query_count=}")
        print(f"bytes read {bytes_to_human(bytes_read)} ({bytes_read} B)")
        print(f"bytes written {bytes_to_human(bytes_written)} ({bytes_written} B)")

        print("key len", array_stats(key_len))
        print("insert", array_stats(insert_val_len))
        print("update", array_stats(update_val_len))
        print("pq", array_stats(pq_val_len))

        return keys, (("Update", update_counter, update_idx), ("Point Query", point_query_counter, point_query_idx))
    return (count_workload,)


@app.cell
def _(np, plt, stats):
    def plot_indices(indices, alpha, beta):
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 5))

        x = np.linspace(0, 1, 1000)
        ax1.hist(indices, bins=500, density=True, alpha=0.7, color='lightblue', 
                label='Sample data')
        ax1.plot(x, stats.beta.pdf(x, alpha, beta), 'b:', linewidth=2, 
                 label=f'MLE: $\\alpha$={alpha:.2f}, $\\beta$={beta:.2f}')
        ax1.set_xlabel('x')
        ax1.set_ylabel('Density')
        ax1.set_title('PDF Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)


        plt.tight_layout()
        plt.show()
    return (plot_indices,)


@app.cell
def _(np, plt):
    def plot_bar_sorted(data):
        counts, bin_edges = np.histogram(data, bins=1000, density=False)

        # Compute bin centers
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        # Sort bins by count (descending)
        order = np.argsort(counts)[::-1]
        counts_sorted = counts[order]
        centers_sorted = bin_centers[order]

        # Plot sorted histogram
        plt.bar(np.arange(len(counts_sorted)), counts_sorted, color="steelblue")
        plt.yscale("log")   # keep log scale
        plt.xlabel("Bins (sorted by frequency)")
        plt.ylabel("Count (log scale)")
        plt.show()
    return (plot_bar_sorted,)


@app.cell
def _(
    estimate_beta_params_mle,
    float_info,
    np,
    plot_bar_sorted,
    plot_indices,
    plt,
):
    # Updates
    def plot_op_stats(op_counter, op_idx):
        freq = np.array([freq for _, freq in op_counter.most_common()])

        indices = np.arange(len(freq))
        indices = np.repeat(indices, freq)
        indices = indices / (indices.max() + 1)
        indices = indices + float_info.epsilon

        alpha, beta = estimate_beta_params_mle(indices)
        print(f"α = {alpha}, β = {beta}")

        plot_indices(indices, alpha, beta)

        plt.hist(op_idx, bins=1000, density=True, color="steelblue")
        plt.xlabel("Value")
        plt.ylabel("Density")
        plt.yscale("log")
        plt.show()

        plot_bar_sorted(op_idx)
    return


@app.cell
def _(np):
    def plot_bar_sorted_ax(ax, data, color="tab:red"):
        counts, bin_edges = np.histogram(data, bins=1000, density=False)

        # Compute bin centers
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        # Sort bins by count (descending)
        order = np.argsort(counts)[::-1]
        counts_sorted = counts[order]
        centers_sorted = bin_centers[order]

        # Plot sorted histogram
        ax.bar(np.arange(len(counts_sorted)), counts_sorted, color=color, alpha=0.2)
        ax.set_yscale("log")   # keep log scale
        ax.set_xlabel("Bins (sorted by frequency)")
        ax.set_ylabel("Count (log scale)")
    return (plot_bar_sorted_ax,)


@app.cell
def _(mo):
    mo.md(r"""# Plots""")
    return


@app.cell
def _():
    import matplotlib
    import matplotlib.font_manager as font_manager
    import json
    return (font_manager,)


@app.cell
def _(find_project_root, font_manager, plt):
    PROJECT_ROOT_DIR = find_project_root()
    VIS_DIR = PROJECT_ROOT_DIR / "vis"
    EXPERIMENT_DIR = PROJECT_ROOT_DIR / "experiments" / "workload-similarity"
    PLOTS_DIR = PROJECT_ROOT_DIR / "plots"

    font = font_manager.FontProperties(fname=str(VIS_DIR / "LinLibertine_Mah.ttf"))
    plt.rcParams["font.family"] = font.get_name()
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.weight"] = "normal"
    plt.rcParams["font.size"] = 22
    return EXPERIMENT_DIR, PLOTS_DIR


@app.cell
def _(StrEnum):
    class Style(StrEnum):
        YCSB = "YCSB"
        Tectonic = "Tectonic"

    line_styles = {
        Style.YCSB: {
            "label": "YCSB",
            "color": "black",
            "linestyle": "-",
            "marker": "o",
            "markersize": 9,
            "markerfacecolor": "none",
            "linewidth": 2.6,
        },
        Style.Tectonic: {
            "label": "Tectonic",
            "color": "tab:red",
            "linestyle": "-",
            "marker": "^",
            "markersize": 9,
            "markerfacecolor": "none",
            "linewidth": 2.6,
        },
    }

    bar_styles = {
        Style.YCSB: {
            # "label": "YCSB",
            "color": "None",
            "edgecolor": "grey",
            "hatch": "///",      # forward‑slash hatch
        },
        Style.Tectonic: {
            # "label": "Tectonic",
            "color": "None",     # keep face transparent so hatch is clear
            "edgecolor": "tab:red",
            "hatch": "\\\\\\", 
        },
    }



    return Style, bar_styles


@app.cell
def _(count_workload):
    ycsb_keys, ycsb_op_stats = count_workload("../experiments/workload-similarity/ycsb-workload-a.txt")
    tec_keys, tec_op_stats = count_workload("../experiments/workload-similarity/tec-workload-a.txt")
    return tec_op_stats, ycsb_op_stats


@app.cell
def _(float_info, np):
    def calc_indices(counter):
        freq = np.array([freq for _, freq in counter.most_common()])

        indices = np.arange(len(freq))
        indices = np.repeat(indices, freq)
        indices = indices / (indices.max() + 1)
        indices = indices + float_info.epsilon

        return indices
    return (calc_indices,)


@app.cell
def _(
    PLOTS_DIR,
    Style,
    bar_styles,
    calc_indices,
    np,
    plt,
    tec_op_stats,
    ycsb_op_stats,
):
    def _():
        for (op, ycsb_counter, ycsb_idx), (_, tec_counter, tec_idx) in zip(ycsb_op_stats, tec_op_stats):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), dpi=150, constrained_layout=True)

            x = np.linspace(0, 1, 1000)

            ycsb_indices = calc_indices(ycsb_counter)
            ax1.hist(ycsb_indices, bins=500, density=True, alpha=0.7, 
                    label=f'YCSB {op}', **{**bar_styles[Style.YCSB],"color":"grey"} )
            ax1.set_xlabel('index (normalized + sorted)')
            ax1.set_ylabel('Frequency')
            ax1.set_title("YCSB")
            ax1.grid(True, alpha=0.3)

            tec_indices = calc_indices(tec_counter)

            ax2.hist(tec_indices, bins=500, density=True, alpha=0.7, 
                    label=f'Tectonic {op}', **{**bar_styles[Style.Tectonic],"color":"tab:red"})
            ax2.set_xlabel('index (normalized + sorted)')
            ax2.set_title("Tectonic")

            ax2.grid(True, alpha=0.3)

            handles, labels = ax1.get_legend_handles_labels()
            fig.suptitle(op)

            plt.suptitle(f"{op} request distribution index")
            plt.savefig(PLOTS_DIR / f"index-normal-sorted_{op}.pdf")
            plt.show()

    _()
    return


@app.cell
def _(PLOTS_DIR, Style, bar_styles, np, plt, tec_op_stats, ycsb_op_stats):
    def process(idx):
        counts, bin_edges = np.histogram(idx, bins=1000, density=False)

        # Compute bin centers
        bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

        # Sort bins by count (descending)
        order = np.argsort(counts)[::-1]
        counts_sorted = counts[order]
        return counts_sorted

    def _():
        fig, axs = plt.subplots(1, len(ycsb_op_stats), figsize=(10, 4), dpi=150, constrained_layout=True)

        i = 0
        for (op, ycsb_counter, ycsb_idx), (_, tec_counter, tec_idx) in zip(ycsb_op_stats, tec_op_stats, strict=True):
            ax = axs[i]
            i += 1
            data_ycsb = process(ycsb_idx)
            data_tec = process(tec_idx)

            # Plot sorted histogram
            label = "YCSB" # if i == 0 else "_nolegend_"
            alpha = 0.1
            ax.bar(np.arange(len(data_ycsb)), data_ycsb,label=label, **{**bar_styles[Style.YCSB],"color":"grey", "alpha": alpha})
            label = "Tectonic"#  if i == 0 else "_nolegend_"
            ax.bar(np.arange(len(data_tec)), data_tec,label=label, **{**bar_styles[Style.Tectonic],"color":"grey", "alpha": alpha})
            ax.set_yscale("log") 
            ax.set_xlabel("Bins (sorted by frequency)")
            if i == 0:
                ax.set_ylabel("Count") 
            ax.set_title(f"{op} request distribution")

        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="outside lower center", ncol=2, frameon=False)

        plt.savefig(PLOTS_DIR / "index-bar-sorted.pdf")
        plt.show()

    _()
    return


@app.cell
def _(PLOTS_DIR, Style, bar_styles, plt, tec_op_stats, ycsb_op_stats):
    def _():
        for (op, ycsb_counter, ycsb_idx), (_, tec_counter, tec_idx) in zip(ycsb_op_stats, tec_op_stats):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), dpi=150, constrained_layout=True)

            # x = np.linspace(0, 1, 1000)

            # ycsb_indices = calc_indices(ycsb_counter)
            # ax1.hist(ycsb_indices, bins=500, density=True, alpha=0.7, 
            #         label=f'YCSB {op}', **{**bar_styles[Style.YCSB],"color":"grey"} )
            # ax1.set_xlabel('index (normalized + sorted)')
            # ax1.set_ylabel('Frequency')
            # ax1.set_title("YCSB")
            # ax1.grid(True, alpha=0.3)

            # tec_indices = calc_indices(tec_counter)

            # ax2.hist(tec_indices, bins=500, density=True, alpha=0.7, 
            #         label=f'Tectonic {op}', **{**bar_styles[Style.Tectonic],"color":"tab:red"})
            # ax2.set_xlabel('index (normalized + sorted)')
            # ax2.set_title("Tectonic")
            # ax2.grid(True, alpha=0.3)
            ax1.hist(ycsb_idx, bins=1000, density=True,label="YCSB", **{**bar_styles[Style.YCSB],"color":"grey"})
            ax1.set_xlabel(f"index (normalized)")
            ax1.set_ylabel("Frequency")
            ax1.set_yscale("log")
            ax1.set_ylim(top=500)
        
            ax2.hist(tec_idx, bins=1000, density=True,label="Tectonic", **{**bar_styles[Style.Tectonic],"color":"tab:red"})
            ax2.set_xlabel(f"index (normalized)")
            ax2.set_ylabel("Frequency")
            ax2.set_yscale("log")
            ax2.set_ylim(top=500)
        
            fig.legend(loc="outside lower center", ncol=2, frameon=False)

            plt.suptitle(f"{op} request distribution index")
            plt.savefig(PLOTS_DIR / f"index-normal_{op}.pdf")
            plt.show()

    _()


    return


@app.cell
def _(mo):
    mo.md(r"""## $\alpha$ - $\beta$ experiments. DO NOT INCLUDE IN PAPER""")
    return


@app.cell
def _(EXPERIMENT_DIR):
    raise Exception("Don't run")
    multi_dir = EXPERIMENT_DIR / "multi"
    tec_stats_multi = {}
    for path in multi_dir.glob("*.txt"):
        print(path)
        # _, op_stats = count_workload(str(path))
        # tec_stats_multi[path] = op_stats

    return (tec_stats_multi,)


@app.cell(hide_code=True)
def _(Style, bar_styles, plt, tec_stats_multi):
    def _():
        items = list(sorted(tec_stats_multi.items(), key=lambda x: x[0].stem))
        fig, axes = plt.subplots(4, 4, figsize=(25, 25), dpi=150, constrained_layout=True)
        axes = axes.flatten()  # so we can index linearly
        for i, (path, tec_op_stats) in enumerate(items):
            (op, tec_counter, tec_idx) = tec_op_stats[0]
            # print([x for x in tec_counter.most_common(10)])
            ax = axes[i]
            # fig, ax = plt.subplots(1, 1, figsize=(15, 6), dpi=150)


            ax.hist(tec_idx, bins=1000, density=True, **{**bar_styles[Style.Tectonic],"color":"tab:red"})
            ax.set_xlabel(f"index (normalized)")
            ax.set_ylabel("Frequency")
            ax.set_yscale("log")
            ax.set_ylim(top=500)
            ax.set_title(path.stem)
            # ax.set_ylim(100)

            fig.suptitle(f"Request index frequency: {op}")
        plt.savefig("alpha-beta.pdf")
        plt.show()

    _()
    return


@app.cell(hide_code=True)
def _(Style, bar_styles, plt, tec_stats_multi):
    def _():
        items = list(sorted(tec_stats_multi.items(), key=lambda x: x[0].stem))
        fig, axes = plt.subplots(4, 4, figsize=(25, 25), dpi=150, constrained_layout=True)
        axes = axes.flatten()  # so we can index linearly
        for i, (path, tec_op_stats) in enumerate(items):
            (op, tec_counter, tec_idx) = tec_op_stats[0]
            # print([x for x in tec_counter.most_common(10)])
            ax = axes[i]
            # fig, ax = plt.subplots(1, 1, figsize=(15, 6), dpi=150)


            ax.hist(tec_idx, bins=1000, density=True, **{**bar_styles[Style.Tectonic],"color":"tab:red"})
            ax.set_xlabel(f"index (normalized)")
            ax.set_ylabel("Frequency")
            ax.set_yscale("log")
            ax.set_ylim(top=300)
            ax.set_title(path.stem)
            # ax.set_ylim(100)

            fig.suptitle(f"Request index frequency: {op}")
        plt.savefig("alpha-beta.pdf")
        plt.show()

    _()
    return


@app.cell
def _(ycsb_op_stats):
    _, ycsb_counter, ycsb_idx = ycsb_op_stats[0]
    return ycsb_counter, ycsb_idx


@app.cell(hide_code=True)
def _(plot_bar_sorted_ax, plt, tec_stats_multi, ycsb_idx):
    def _():
        items = list(sorted(tec_stats_multi.items(), key=lambda x: x[0].stem))
        fig, axes = plt.subplots(4, 4, figsize=(25, 25), dpi=150, constrained_layout=True)
        axes = axes.flatten()  # so we can index linearly
        for i, (path, tec_op_stats) in enumerate(items):
            (op, tec_counter, tec_idx) = tec_op_stats[0]
            # print([x for x in tec_counter.most_common(10)])
            ax = axes[i]
            # fig, ax = plt.subplots(1, 1, figsize=(15, 6), dpi=150)

            plot_bar_sorted_ax(ax, tec_idx)
            plot_bar_sorted_ax(ax, ycsb_idx, color="grey")

            # ax.hist(tec_idx, bins=1000, density=True, **{**bar_styles[Style.Tectonic],"color":"tab:red"})
            # ax.set_xlabel(f"index (normalized)")
            # ax.set_ylabel("Frequency")
            # ax.set_yscale("log")
            ax.set_title(path.stem)
            ax.set_ylim(top=10**5)

            fig.suptitle(f"Request index frequency: {op}")

        # plt.savefig("alpha-beta-bins.pdf")
        plt.show()

    _()
    return


@app.cell(hide_code=True)
def _(Style, bar_styles, calc_indices, np, plt, tec_stats_multi, ycsb_counter):
    def _():
        items = list(sorted(tec_stats_multi.items(), key=lambda x: x[0].stem))
        fig, axes = plt.subplots(4, 4, figsize=(25, 25), dpi=150, constrained_layout=True)
        axes = axes.flatten()  # so we can index linearly
        ycsb_indices = calc_indices(ycsb_counter)

        for i, (path, tec_op_stats) in enumerate(items):
            (op, tec_counter, tec_idx) = tec_op_stats[0]
            # print([x for x in tec_counter.most_common(10)])
            ax = axes[i]
            # fig, ax = plt.subplots(1, 1, figsize=(15, 6), dpi=150)

            # plot_bar_sorted_ax(ax, tec_idx)
            # plot_bar_sorted_ax(ax, ycsb_idx, color="grey")

            # # ax.hist(tec_idx, bins=1000, density=True, **{**bar_styles[Style.Tectonic],"color":"tab:red"})
            # # ax.set_xlabel(f"index (normalized)")
            # # ax.set_ylabel("Frequency")
            # # ax.set_yscale("log")
            # ax.set_title(path.stem)
            # ax.set_ylim(top=10**5)
            x = np.linspace(0, 1, 1000)

            tec_indices = calc_indices(tec_counter)
            ax.hist(tec_indices, bins=500, density=True, alpha=0.2, 
                    label=f'T {op}', **{**bar_styles[Style.Tectonic],"color":"tab:red"} )
            ax.hist(ycsb_indices, bins=500, density=True, alpha=0.2, 
                    label=f'Y {op}', **{**bar_styles[Style.Tectonic],"color":"grey"} )
            ax.set_xlabel('index (normalized + sorted)')
            ax.set_ylabel('Frequency')
            ax.set_title(path.stem)
            ax.set_yscale("log")
            ax.legend()
            ax.grid(True, alpha=0.3)

        fig.suptitle(f"Request index frequency: {op}")

        # plt.savefig("alpha-beta-bins.pdf")
        plt.show()

    _()
    return


if __name__ == "__main__":
    app.run()
