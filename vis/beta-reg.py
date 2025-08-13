import numpy as np
from scipy.stats import beta as beta_dist
from scipy.optimize import minimize
from collections import Counter
from scipy.stats import beta

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


if __name__ == "__main__":
    N = 10

    ycsb_op, ycsb_i, ycsb_u, ycsb_pq = count_workload("../experiments/workload-similarity/ycsb-workload-a.txt")

    # alpha_true, beta_true = 2.5, 5.0
    # indices = generate_indices(alpha_true, beta_true, N, num_samples=50, seed=42)
    counts = [count for _, count in ycsb_u.most_common()]
    n = len(counts)

    midpoints = (np.arange(n) + 0.5) / n
    print(midpoints)
    samples = np.repeat(midpoints, counts)
    print(samples)
    a_hat, b_hat, loc, scale = beta.fit(samples, floc=0, fscale=1)
    print(a_hat, b_hat, loc, scale)



# Example usage:
# indices = np.array([0, 0, 2, 1, 0, 2, 2, 3])  # chosen bin indices
# N = 5
# alpha_hat, beta_hat = fit_beta_from_indices(indices, N)
# print(alpha_hat, beta_hat)
