# For bar plots: Only parameters that ax.bar() accepts
bar_styles = {
    "YCSB": {
        "label": "YCSB",
        "color": "None",        # Transparent fill for bar interiors
        "edgecolor": "grey",  # Academic-friendly blue
        "hatch": "///",            # No hatch pattern
        # "color": "grey",
    },
    "KVBench": {
        "label": "KVBench",
        "color": "None",
        "edgecolor": "tab:blue",  # Muted purple
        "hatch": "\\",
    },
    "Tectonic": {
        "label": "Tectonic",
        "color": "tab:red",
        "edgecolor": "tab:red",  # Warm, muted orange
        "hatch": "",
    }
}

# For line plots: Only parameters that ax.plot() accepts
line_styles = {
    "YCSB": {
        "label": "YCSB",
        "color": "black",
        "linestyle": "-",      # Solid line
        "marker": "^",         # Circle marker
        "markersize": 10,
        "markerfacecolor": "none",
    },
    "KVBench": {
        "label": "KVBench",
        "color": "tab:blue",
        "linestyle": "--",     # Dashed line (or any preferred style)
        "marker": "v",         # Triangle marker (downward)
        "markersize": 10,
        "markerfacecolor": "none",
    },
    "Tectonic": {
        "label": "Tectonic",
        "color": "tab:red",
        "linestyle": "-.",     # Dashed line
        "marker": "s",         # Square marker
        "markersize": 10,
        "markerfacecolor": "none",
    }
}

# # Bar styles per system 
# bar_styles = {
#     "YCSB": {
#         "label": "YCSB",
#         "color": "None",
#         "edgecolor": "grey",
#         "hatch": "///",      # forward‑slash hatch
#     },
#     "KVBench": {
#         "label": "KVBench",
#         "color": "None",
#         "edgecolor": "tab:blue",
#         "hatch": "//",
#     },
#     "Tectonic": {
#         "label": "Tectonic",
#         "color": "None",     # keep face transparent so hatch is clear
#         "edgecolor": "tab:red",
#         "hatch": "\\\\\\", 
#     },
# }


bar_hatches = ["///", "\\\\", "xx"]

# # Line styles 
# line_styles = {
#     "YCSB": {
#         "label": "YCSB",
#         "color": "grey",
#         "linestyle": "-",
#         "marker": "o",
#         "markersize": 12,
#         "markerfacecolor": "none",
#         # "linewidth": 2.6,
#     },
#     "Tectonic": {
#         "label": "Tectonic",
#         "color": "tab:red",
#         "linestyle": "-",
#         "marker": "^",
#         "markersize": 12,
#         "markerfacecolor": "none",
#         # "linewidth": 2.6,
#     },
# }

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
