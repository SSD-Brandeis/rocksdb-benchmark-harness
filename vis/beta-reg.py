import numpy as np
from collections import Counter
from scipy import stats

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
    ycsb_op, ycsb_i, ycsb_u, ycsb_pq = count_workload("../experiments/workload-similarity/ycsb-workload-a.txt")

    print(ycsb_u)




    # print(samples)
    #
    # sampled = [nums[int(i)] for i in samples]
    #
    # print(sampled)



# Example usage:
# indices = np.array([0, 0, 2, 1, 0, 2, 2, 3])  # chosen bin indices
# N = 5
# alpha_hat, beta_hat = fit_beta_from_indices(indices, N)
# print(alpha_hat, beta_hat)
