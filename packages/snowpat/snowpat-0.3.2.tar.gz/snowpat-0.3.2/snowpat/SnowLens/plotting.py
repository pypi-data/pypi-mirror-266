import matplotlib.pyplot as plt
from snowpat.snowpackreader import Snowpack
from numpy import ndarray, append
from typing import Dict
import matplotlib.colors as mcolors
import matplotlib as mpl

import numpy as np

from .plot_helpers_snowpack import grain_type_color, adjustData, _add_crust_lines

CMAP = mcolors.ListedColormap(grain_type_color)
NORM = mcolors.BoundaryNorm([0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5], 9)

# h, T, grain type, wl, hardness, ssif, layer_middle
NEEDED_VARS = ["0501", "0503", "0513", "0530", "0534", "0604", "layer middle", "layer thickness"]

def plotProfile(profile:Snowpack, out:str = None, ind_mfcrust = True, standardized_limits:bool=True)->plt.Figure:
    data = _aggregate_data(profile)
    if not data:
        return None
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")
    ax.set_ylabel("Height (cm)")

    if standardized_limits:
        ymax = 250 if data["0501"][-1] < 250 else data["0501"][-1]
        ax.set_ylim(0, ymax)
    
    mpl.rcParams['hatch.linewidth'] = 2.0
    
    _plot_hardness(ax, data, ind_mfcrust, profile.isNewton, profile.old_hardness)
    _plot_temperature(ax, data, standardized_limits)
    _plot_stability_index(ax, data)
    
    plt.close(fig)
    if out:
        fig.savefig(out)
    return fig

def _aggregate_data(profile:Snowpack) -> Dict[str, ndarray]:
    data:Dict[str,ndarray] = {}
    for var in NEEDED_VARS:
        data[var] = profile.get_param(var)
        if var == "0501" and data[var].size < 2:
            RuntimeWarning("Profile data is too small to plot")
            return None
    return data 

def _plot_temperature(ax:plt.Axes, data:Dict[str,ndarray], standardized_limits:bool):
    T = append(data["0503"], data["0503"][-1])

    ax2 = ax.twiny()
    ax2.plot(T, data["0501"], color="red", zorder=3)
    ax2.set_xlabel("Temperature (C)")
    
    if standardized_limits:
        Tmin = T.min()
        xmin = -20 if Tmin > -20 else Tmin
        ax2.set_xlim(xmin, 0)
    
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    ax2.xaxis.tick_bottom()
    ax2.xaxis.set_label_position("bottom")


    
def _plot_hardness(ax:plt.Axes, data:Dict[str,ndarray], ind_meltcrust:bool, isNewton:bool = False, old_hardness:bool = True):
    grain_type = data["0513"]
    hardness = data["0534"]
    
    grain_type = adjustData("0513", grain_type)
    
    if old_hardness:
        if all(hardness < 0): # TODO: possibly remove this, if change is accepted
            hardness = hardness*-1

    hatch_mask = ["///" if grain == 7.2 and ind_meltcrust else "" for grain in grain_type]
    # Plot the horizontal bar plot with hash lines when grain type is 7.2
    bars = ax.barh(data["layer middle"], hardness, data["layer thickness"]*2, color=CMAP(NORM(grain_type)), hatch=hatch_mask, zorder=1)
  
    if isNewton:
        ax.set_xlabel("Hardness (N)")
        ax.invert_xaxis()
    else:
        ax.set_xlabel("Hardness (Id)")
        ax.invert_xaxis()
        if np.abs(hardness).max() > 5:
            xticks = ["Fist", "4F", "1F", "Pencil", "Knife", "Ice"]
            ax.set_xticks([1, 2, 3, 4, 5, 6])
            ax.set_xticklabels(xticks)
        else:
            xticks = ["Fist", "4F", "1F", "Pencil", "Knife"]
            ax.set_xticks([1, 2, 3, 4, 5])
            ax.set_xticklabels(xticks)
            
        
            
    
    
def _plot_stability_index(ax:plt.Axes, data:Dict[str,ndarray]):
    ssi = data["0604"]
    wl = data["0530"]
    sk38 = wl[-1]
    z_sk38 = wl[-2]
    
    layer_boundaries = data["0501"]
    
    # find the index where z_sk38 is located
    layer = next((i for i, boundary in enumerate(layer_boundaries) if boundary > z_sk38), 0)
    
    SSI = ssi[layer]
    if sk38 < 0.45 and SSI < 1.32:
        stability = "cl: Poor"
    elif sk38 < 0.45 and SSI >= 1.32:
        stability = "cl: Fair"
    else:
        stability = "cl: Good"

    ymin, ymax = ax.get_ylim()
    
    z_sk38 = (z_sk38 - ymin) / (ymax - ymin)

    # Draw a horizontal arrow at height z
    ax.annotate('', xy=(1, z_sk38), xytext=(1.2, z_sk38),
                arrowprops=dict(facecolor='black', shrink=0.05, width=0.5, headwidth=5),
                xycoords='axes fraction', textcoords='axes fraction',
                horizontalalignment='right', verticalalignment='center',
                zorder=1)  # Add this line here
        
    # Add stability above the arrow
    ax.annotate(stability, xy=(1.1, z_sk38), xytext=(1.1, z_sk38+0.03),
                xycoords='axes fraction', textcoords='axes fraction',
                horizontalalignment='left', verticalalignment='center',
                zorder=1)  # Add this line here

    # Add sk38 value below the arrow
    ax.annotate("sk38: "+str(sk38), xy=(1.1, z_sk38), xytext=(1.1, z_sk38-0.03),
                xycoords='axes fraction', textcoords='axes fraction',
                horizontalalignment='left', verticalalignment='center',
                zorder=1)  # Add this line here
    
from os import getcwd
def show_logo():
    print(getcwd())
    path = "resources/snowpat.png"
    logo = plt.imread(path)
    plt.imshow(logo)
    plt.show()
    