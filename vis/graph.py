import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")


@app.cell
def _():
    import numpy as np
    from scipy import stats
    import matplotlib.pyplot as plt
    from collections import Counter
    from sys import float_info
    import marimo
    if marimo.running_in_notebook():
        from tqdm.notebook import tqdm
    else:
        from tqdm import tqdm

    return Counter, float_info, np, plt, stats, tqdm


@app.cell
def _(np, plt, stats):
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

    def _():
        # Your original setup
        alpha_true = 1.5
        beta_true = 3.3
        samples = np.random.beta(alpha_true, beta_true, size=100_000)
    
        # Estimate parameters
        alpha_mom, beta_mom = estimate_beta_params_mom(samples)
        alpha_mle, beta_mle = estimate_beta_params_mle(samples)
    
        print("True parameters:")
        print(f"α = {alpha_true}, β = {beta_true}")
        print()
        print("Method of Moments estimates:")
        print(f"α̂ = {alpha_mom:.4f}, β̂ = {beta_mom:.4f}")
        print()
        print("Maximum Likelihood estimates:")
        print(f"α̂ = {alpha_mle:.4f}, β̂ = {beta_mle:.4f}")
    
        # Visualize the results
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
        # Plot histogram of samples vs theoretical PDFs
        x = np.linspace(0, 1, 100)
        ax1.hist(samples, bins=30, density=True, alpha=0.7, color='lightblue', 
                 label='Sample data')
        ax1.plot(x, stats.beta.pdf(x, alpha_true, beta_true), 'r-', linewidth=2, 
                 label=f'True: α={alpha_true}, β={beta_true}')
        ax1.plot(x, stats.beta.pdf(x, alpha_mom, beta_mom), 'g--', linewidth=2, 
                 label=f'MoM: α={alpha_mom:.2f}, β={beta_mom:.2f}')
        ax1.plot(x, stats.beta.pdf(x, alpha_mle, beta_mle), 'b:', linewidth=2, 
                 label=f'MLE: α={alpha_mle:.2f}, β={beta_mle:.2f}')
        ax1.set_xlabel('x')
        ax1.set_ylabel('Density')
        ax1.set_title('PDF Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
        # Q-Q plot to check goodness of fit
        stats.probplot(samples, dist=stats.beta, sparams=(alpha_mle, beta_mle), 
                       plot=ax2)
        ax2.set_title('Q-Q Plot (MLE estimates)')
        ax2.grid(True, alpha=0.3)
    
        plt.tight_layout()
        plt.show()
    
        # Calculate some error metrics
        def calculate_errors(alpha_est, beta_est, alpha_true, beta_true):
            alpha_error = abs(alpha_est - alpha_true) / alpha_true * 100
            beta_error = abs(beta_est - beta_true) / beta_true * 100
            return alpha_error, beta_error
    
        mom_alpha_err, mom_beta_err = calculate_errors(alpha_mom, beta_mom, alpha_true, beta_true)
        mle_alpha_err, mle_beta_err = calculate_errors(alpha_mle, beta_mle, alpha_true, beta_true)
    
        print("\nPercentage errors:")
        print(f"Method of Moments: α error = {mom_alpha_err:.2f}%, β error = {mom_beta_err:.2f}%")
        print(f"Maximum Likelihood: α error = {mle_alpha_err:.2f}%, β error = {mle_beta_err:.2f}%")
    # _()
    return (estimate_beta_params_mle,)


@app.cell
def _(Counter, float_info, tqdm):
    from enum import StrEnum

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

    def count_workload(filename: str):
        with open(filename) as f:
            lines = f.readlines()

        keys = []
        db = {}
        key_to_idx = {}
        update_idx = []
        update_counter = Counter()
        update_bytes = 0.0

        point_query_idx = []
        point_query_counter = Counter()
        point_query_bytes = 0
        empty_point_query_count = 0

        for line in tqdm(lines):
            line = line.strip()
            if line.startswith(OpChar.INSERT):
                _, key, val = line.split(" ", maxsplit=2)
                keys.append(key)
                db[key] = val
                key_to_idx[key] = len(keys) - 1
            elif line.startswith(OpChar.UPDATE):
                _, key, value = line.split(" ", maxsplit=2)
                update_counter[key] += 1
                idx = key_to_idx[key]
                update_idx.append(max(idx / len(keys), float_info.epsilon))
            elif line.startswith(OpChar.QUERY_POINT):
                _, key = line.split(" ", maxsplit=1)
                val = db.get(key)
                point_query_counter[key] += 1
                idx = key_to_idx[key]
                point_query_idx.append(max(idx / len(keys), float_info.epsilon))
                if val is not None:
                    point_query_bytes += len(val)
                else:
                    empty_point_query_count += 1

        print(f"{empty_point_query_count=}")
        print(f"{bytes_to_human(point_query_bytes)} ({point_query_bytes} B)")

        return keys, ((update_counter, update_idx), (point_query_counter, point_query_idx))
    return (count_workload,)


@app.cell
def _(count_workload):
    keys, op_stats = count_workload("../experiments/workload-similarity/ycsb-workload-a.txt")
    return (op_stats,)


@app.cell
def _(np, plt, stats):
    def plot_indices(indices, alpha, beta):
        # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 5))

        x = np.linspace(0, 1, 1000)
        ax1.hist(indices, bins=500, density=True, alpha=0.7, color='lightblue', 
                 label='Sample data')
        # ax1.plot(x, stats.beta.pdf(x, alpha, beta), 'g--', linewidth=2, 
                 # label=f'MoM: α={alpha_mom:.2f}, β={beta_mom:.2f}')
        ax1.plot(x, stats.beta.pdf(x, alpha, beta), 'b:', linewidth=2, 
                 label=f'MLE: α={alpha:.2f}, β={beta:.2f}')
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
    return (plot_op_stats,)


@app.cell
def _(op_stats, plot_op_stats):
    for (op_counter, op_idx) in op_stats:
        plot_op_stats(op_counter, op_idx)
    return


@app.cell
def _(op_stats):
    def _():
        for (op_counter, _) in op_stats:
            print(op_counter.most_common(10))


    _()
    return


@app.cell
def _(count_workload):
    tec_keys, tec_op_stats = count_workload("../experiments/workload-similarity/tec-workload-a.txt")
    return (tec_op_stats,)


@app.cell
def _(plot_op_stats, tec_op_stats):
    for (tec_op_counter, tec_op_idx) in tec_op_stats:
        plot_op_stats(tec_op_counter, tec_op_idx)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
