from typing import Any


def generate_meta_dict() -> dict[str, Any]:
    """Generates a dictionary with all possible keys accepted by the Fit class as meta data and sets the values
    to none."""
    return {
        "plotting_style": None,
        "file": None,
        "x": None,
        "y": None,
        "fits": {
            "generic fit name": {
                "plotting_style": None,
                "fit_type": "odr",
                "function": "m * x + b",
                "x_min_limit": None,
                "x_max_limit": None,
                "plot_x_min_limit": None,
                "plot_x_max_limit": None,
                "start_parameters": None,
                "fit_points": None,
                "absolute_sigma": None,
                "check_finite": None,
                "label": None
            }
        },
        "x_min_limit": None,
        "x_max_limit": None,
        "y_min_limit": None,
        "y_max_limit": None,
        "figure_style": None,
        "figure_dpi": None,
        "figure_size": None,
        "label": None
    }
