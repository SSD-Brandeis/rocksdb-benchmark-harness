import json
def spec_from_alpha_beta(alpha: float, beta: float):
    return {
    "$schema": "../../../vendor/tectonic/workload_schema.json",
    "sections": [
        {
            "groups": [
                {
                    "inserts": {
                        "op_count": 1000000,
                        "key": {
                            "segmented": {
                                "segments": [
                                    "usertable:user",
                                    { "uniform": { "len": 19, "character_set": "numeric" } }
                                ],
                                "separator": ""
                            }
                        },
                        "val": {
                            "uniform": { "len": 1090 }
                        }
                    }
                },
                {
                    "point_queries": {
                        "op_count": 500000,
                        "selection": {
                            "beta": {
                                "alpha": alpha,
                                "beta": beta,
                            }
                        }
                    },
                    "updates": {
                        "op_count": 500000,
                        "val": {
                            "uniform": { "len": 128 }
                        },
                        "selection": {
                            "beta": {
                                "alpha": alpha,
                                "beta": beta,
                            }
                        }
                    }
                }
            ]
        }
    ]
}


for alpha in range(10, 30, 5):
    alpha = alpha / 100
    for beta in range(50, 70, 5):
        beta = beta / 100

        spec = spec_from_alpha_beta(alpha, beta)

        with open(f"{alpha:.2f}-{beta:.2f}.spec.json", "w") as f:
            json.dump(spec, f)