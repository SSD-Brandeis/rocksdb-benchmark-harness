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
    return Counter, float_info, np, plt, stats


@app.cell
def _(np, plt):
    def _():
        alpha = 2
        beta = 5
        samples = np.random.beta(alpha, beta, size=1000)
        plt.hist(samples)
        plt.show()
    _()
    return


@app.cell
def _(np, plt, stats):
    # Your original setup
    alpha_true = 1.5
    beta_true = 3.3
    samples = np.random.beta(alpha_true, beta_true, size=100_000)

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
    return estimate_beta_params_mle, samples


@app.cell
def _(samples):
    samples
    return


@app.cell
def _(Counter, float_info):
    def count_workload(filename: str):
        with open(filename) as f:
            keys = []
            key_to_idx = {}
            update_idx = []
            update_counter = Counter()
            for line in f.readlines():
                line = line.strip()
                if line.startswith("I"):
                    key = line.split(" ")[1]
                    keys.append(key)
                    key_to_idx[key] = len(keys) - 1
                elif line.startswith("U"):
                    key = line.split(" ")[1]
                    update_counter[key] += 1
                    idx = key_to_idx[key]
                    update_idx.append(max(idx / len(keys), float_info.epsilon))

                
        return keys, update_idx, update_counter
    return (count_workload,)


@app.cell
def _(count_workload):
    # ycsb_op, ycsb_i, ycsb_u, ycsb_pq = count_workload("../experiments/workload-similarity/ycsb-workload-a.txt")
    keys, update_idx, update_counter = count_workload("../experiments/workload-similarity/ycsb-workload-a.txt")
    print(len(update_idx))
    update_idx[:100]
    return (update_counter,)


@app.cell
def _(np, update_counter):
    update_freq = np.array([freq for _, freq in update_counter.most_common()])
    update_freq
    return (update_freq,)


@app.cell
def _(float_info, np, update_freq):
    indices = np.arange(len(update_freq))
    indices = np.repeat(indices, update_freq)
    indices = indices / (indices.max() + 1)
    indices = indices + float_info.epsilon
    indices
    return (indices,)


@app.cell
def _(estimate_beta_params_mle, indices):
    alpha, beta = estimate_beta_params_mle(indices)
    print(f"α = {alpha}, β = {beta}")
    return alpha, beta


@app.cell
def _(alpha, beta, indices, np, plt, stats):
    def _():
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
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
    _()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
