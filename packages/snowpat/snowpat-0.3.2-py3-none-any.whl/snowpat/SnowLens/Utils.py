from enum import Enum
from datetime import datetime
from typing import Union, Dict, Callable, get_origin, get_args
from matplotlib.colors import Colormap, Normalize
from numpy import ndarray
from collections.abc import Callable as CallableType
import matplotlib.pyplot as plt
import numpy as np

class PlotType(Enum):
    PRO = 1
    SMET = 2
    PROFILE = 3

from typing import get_origin, get_args, Union, Callable

def show_figure(fig:plt.Figure):
    """
    A helper function, to easily make a figure available to be displayed with plt.show .

    Parameters:
    fig (matplotlib.figure.Figure): The figure to be displayed.

    """
    dummy = plt.figure()
    new_manager = dummy.canvas.manager
    new_manager.canvas.figure = fig
    fig.set_canvas(new_manager.canvas)


def _type_to_string(t):
    origin = get_origin(t)
    if origin is None:
        # t is a plain type
        return t.__name__
    elif origin is Union:
        # t is a Union type
        args = ", or ".join(_type_to_string(arg) for arg in get_args(t))
        return f"Either: {args}"
    elif origin is CallableType:
        # t is a Callable type
        arg_types = get_args(t)[:-1]
        return_type = get_args(t)[-1]
        arg_types_str = ", ".join(_type_to_string(arg) for arg in arg_types[0])
        return_type_str = _type_to_string(return_type)
        return f"function({arg_types_str}) -> {return_type_str}"
    else:
        # t is another kind of special type
        args = ", ".join(_type_to_string(arg) for arg in get_args(t))
        return f"{origin.__name__}[{args}]"
    
def _is_of_type(value, needed_type)->bool:
    v_origin = get_origin(value)
    n_origin = get_origin(needed_type)
    if n_origin is None:
        return isinstance(value, needed_type)
    elif n_origin is Union:
        return any(_is_of_type(value, arg) for arg in get_args(needed_type))
    elif n_origin is CallableType:
        return _check_function(value)        
    elif n_origin is list:
        if not isinstance(value, list):
            return False
        if not value:
            return True
        return all(_is_of_type(val, get_args(needed_type)[0]) for val in value)
    elif n_origin is dict:
        if not isinstance(value, dict):
            return False
        if not value:
            return True
        key_type, dval_type = get_args(needed_type)
        return all(_is_of_type(key, key_type) and _is_of_type(val, dval_type) for key, val in value.items())        
    else:
        return isinstance(value, needed_type)       
    
def _check_function(func)->bool:
    if not callable(func):
        return False
    code = "0501"
    data = np.array([0, 1, 2, 3, 4])
    try:
        res = func(code, data)
        if not isinstance(res, np.ndarray):
            print("The data editing function needs to return a numpy array")
            return False
        if res.shape != data.shape:
            print("the data editing function needs to return an array of the same shape as the input")
            return False
    except:
        return False
    return True
    
GENERAL_KWARGS = {
    "outfile": str
}
GENERAL_HELP_TEXT = {
    "outfile": "The path to save the plot to"
}
    
SMET_KWARGS = {}
SMET_HELP_TEXT = {}

PROFILE_KWARGS = {
    "ind_mfcrust": bool,
    "standardized_limits": bool
}
PROFILE_HELP_TEXT = {
    "ind_mfcrust": "If True, the MF crust will be indicated",
    "standardized_limits": "If True, the limits of the plot will be set as in niviz, otherwise depending on data"
}

SNOWPACK_KWARGS = {
    "start": datetime,
    "stop": datetime,
    "resolution": str,
    "num_ticks": int,
    "cmap": Union[Colormap, Dict[str, Colormap], Dict[str, str]],
    "norm": Union[Normalize, Dict[str, Normalize]],
    "cbar_label": Union[str, Dict[str, str], type(None)],
    "n_cols": int,
    "title": str,
    "vmin": Union[int, Dict[str, int]],
    "vmax": Union[int, Dict[str, int]],
    "adjust_data": Callable[[str, ndarray], ndarray],
    "single_ticks": bool,
    "set_ylabel": bool,
    "colorbar": bool,
    "ind_mfcrust": bool,
    "mfcrust_color": bool,
    "profile_on": datetime,
}

SNOWPACK_HELP_TEXT = {
    "start": "The start time of the plot",
    "stop": "The stop time of the plot",
    "resolution": "The resolution of dates of the plot",
    "num_ticks": "The number of ticks on the x-axis, if not set, the ticks will be formatted automatically",
    "cmap": "The colormap to use for the plot, either a single colormap or a dictionary with colormaps for each variable",
    "norm": "The normalization to use for the plot, either a single normalization or a dictionary with normalizations for each variable",
    "cbar_label": "The label of the colorbar, either a single label or a dictionary with labels for each variable",
    "n_cols": "The subplots to be plotted side by side",
    "title": "The title of the plot",
    "vmin": "The minimum value of the colorbar, either a single value or a dictionary with values for each variable",
    "vmax": "The maximum value of the colorbar, either a single value or a dictionary with values for each variable",
    "adjust_data": "A function to adjust the data before plotting: f(var_code, ndarray) -> ndarray, needs to handle parameter for a single profile",
    "single_ticks": "If True, ticks will only be plotted per profile will be plotted",
    "set_ylabel": "If True, the y-label will be set",
    "colorbar": "If True, a colorbar will be plotted",
    "ind_mfcrust": "If True, the MF crust will be indicated",
    "profile_on": "The date of the profile to be plotted"
}
    