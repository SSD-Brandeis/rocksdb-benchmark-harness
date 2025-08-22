

# Bar styles per system 
bar_styles = {
    "YCSB": {
        "label": "YCSB",
        "color": "None",
        "edgecolor": "grey",
        "hatch": "///",      # forward‑slash hatch
    },
    "KVBench": {
        "label": "KVBench",
        "color": "None",
        "edgecolor": "tab:blue",
        "hatch": "//",
    },
    "Tectonic": {
        "label": "Tectonic",
        "color": "None",     # keep face transparent so hatch is clear
        "edgecolor": "tab:red",
        "hatch": "\\\\\\", 
    },
}


bar_hatches = ["///", "\\\\", "xx"]

# Line styles 
line_styles = {
    "YCSB": {
        "label": "YCSB",
        "color": "black",
        "linestyle": "-",
        "marker": "o",
        "markersize": 9,
        "markerfacecolor": "none",
        "linewidth": 2.6,
    },
    "Tectonic": {
        "label": "Tectonic",
        "color": "tab:red",
        "linestyle": "-",
        "marker": "^",
        "markersize": 9,
        "markerfacecolor": "none",
        "linewidth": 2.6,
    },
}

# CPU usage
cpu_line_styles = {
    "YCSB": {
        "label": "YCSB (CPU usage)",
        "color": "black",
        "linestyle": "--",
        "marker": None,
        "linewidth": 1.8,
        "alpha": 0.9,
    },
    "Tectonic": {
        "label": "Tectonic (CPU usage)",
        "color": "tab:red",
        "linestyle": "--",
        "marker": None,
        "linewidth": 1.8,
        "alpha": 0.9,
    },
}
