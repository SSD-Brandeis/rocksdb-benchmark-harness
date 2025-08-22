## User facing
| Current                          | Alternative                        |
|----------------------------------|------------------------------------|
| **Uniform(min, max)**            |                                    | 
| **Normal(mean, std_dev)**        | Normal(mu, sigma)                  |
| **Exponential(lambda)**          |                                    |
| **Beta(alpha, beta)**            |                                    |
| **Zipf(n, s)**                   |                                    |
| **LogNormal(mean, std_dev)**     | LogNormal(mu, sigma)               |
| **Poisson(lambda)**              |                                    |
| **Weibull(scale, shape)**        |                                    |
| **Pareto(scale, shape)**         |                                    |
| ---                              | ---                                |
| StringExpr::**Uniform**          | UniformRandom, Random              |
| StringExpr::Uniform::**len**     | length                             |
| StringExpr::**Weighted**         |                                    |
| StringExpr::Weighted::**weight** | freq, frequency                    |
| StringExpr::Weighted::**value**  | expr, expression                   |
| StringExpr::**Segmented**        | Joined, Separated                  |
| StringExpr::**HotRange**         | HotPrefix, PrefixDistribution      |
| ---                              | ---                                |
| RangeFormat::**StartCount**      |                                    |
| RangeFormat::**StartEnd**        |                                    |
| ---                              | ---                                |
| **Inserts**                      | Insert                             |
| **Updates**                      | Update                             |
| **Merges**                       | Merge, ReadModifyWrite, Rmw        |
| **PointDeletes**                 | PointDelete, DeletePoint           |
| **EmptyPointDeletes**            | DeletePointEmpty, DeletePointEmpty |
| **amount**                       | count                              |
| **key**                          | key_expr                           |
| **val**                          | value, val_expr                    |
| **selection**                    | selection_distr, request_distr     |
| **selectivity**                  | sel, range                         |
| **range_format**                 | range_output_format                |
| **character_set**                | char_set                           |


## Internal

| Current              | Alternative                      |
|----------------------|----------------------------------|
| NumberExpr           |                                  |
| NumberExpr::Constant | Literal                          |
| NumberExpr::Sampled  | Distribution, RandomDistribution |
| StringExpr           |                                  |



