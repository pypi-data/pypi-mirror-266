import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

from dataclasses import dataclass

import numpy as np
import datetime

from typing import List, Dict, Optional, Callable, Union


grain_type_color = ['greenyellow', 'darkgreen', 'pink', 'lightblue', 'blue', 'magenta', 'red', 'cyan', 'lightblue']

# the default mapping to color maps
def getColorMap(var_code) -> mcolors.Colormap:
    if var_code == "0513":
        cmap = mcolors.ListedColormap(grain_type_color)
    elif var_code == "0503":
        cmap = "coolwarm"
        cmap = cm.get_cmap(cmap)
    elif var_code == "0502":
        cmap = "Greys"
        cmap = cm.get_cmap(cmap)
    elif var_code == "0535":
        cmap = "viridis"
        cmap = cm.get_cmap(cmap)
    elif var_code == "0506":
        cmap = "viridis"
        cmap = cm.get_cmap(cmap)
    else:
        cmap = "viridis"
        cmap = cm.get_cmap(cmap)
    return cmap

# the default mapping to normalizations
def getNorm(var_code) -> mcolors.Normalize:
    if var_code == "0513":
        norm = mcolors.BoundaryNorm([0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5,9.5], 9)
    elif var_code == "0503":
        norm = mcolors.Normalize(vmin=-20, vmax=0)
    elif var_code == "0506":
        norm = mcolors.Normalize(vmin=0, vmax=5)
    elif var_code == "0502":
        norm = mcolors.Normalize(vmin=0, vmax=600)
    elif var_code == "0535":
        norm = mcolors.Normalize(vmin=0, vmax=60)
    else:
        norm = mcolors.LogNorm(vmin=10 ** -1, vmax=1)
    return norm

# the default handling of special var codes
def adjustData(var_code:str, data:np.ndarray)->np.ndarray:
    new_data = data.copy()
    new_data = np.where(np.isnan(new_data), -999, new_data)
    if var_code == "0513":
        new_data = np.where(new_data == 772, -100, new_data)
        new_data = (divmod(new_data, 100)[0]).astype(int)
        new_data = np.where(new_data == -10, -999, new_data)
        new_data = np.where(new_data == -1, 7.2, new_data)
    if var_code == "0535": # TODO: is this needed?
        ice_density = 917
        new_data = 6 / (ice_density * new_data/1000)   
    return new_data
        
# contains all the kwargs, and options for the plot
@dataclass
class PlotHelper:
    set_ylabel : bool = True
    single_ticks : bool = True
    colorbar : bool = True
    set_cbar_label : bool = True
    ind_mfcrust : bool = True
    mfcrust_color : bool = False
    n_cols : int = 1
    start : Optional[datetime.datetime] = None
    stop : Optional[datetime.datetime] = None
    resolution : Optional[str] = None
    num_ticks : Optional[int] = None
    cmap : Optional[mcolors.Colormap] = None
    norm : Optional[mcolors.Normalize] = None
    cmap_dict : Optional[Dict[str, mcolors.Colormap]] = None
    norm_dict : Optional[Dict[str, mcolors.Normalize]] = None
    cbar_label : Optional[Union[str, Dict[str,str]]] = None
    title : Optional[str] = None
    subtitle : Optional[Dict[str,str]] = None
    adjust_data : Optional[Callable[[str,np.ndarray],np.ndarray]] = None
    
    def getCbarLabel(self, var_code:str)->str:
        is_available = False
        cbar_label = None
        if self.cbar_label:
            try:
                cbar_label = self.cbar_label[var_code]
                is_available = True
            except KeyError:
                pass
        return cbar_label, is_available
    
    def getSubtitle(self, var_code:str)->str:
        is_available = False
        subtitle = None
        if self.subtitle:
            try:
                subtitle = self.subtitle[var_code]
                is_available = True
            except KeyError:
                pass
        return subtitle, is_available
    
    
    def getNorm(self, var_code) -> mcolors.Normalize:
        if self.norm_dict:
            try:
                norm = self.norm_dict[var_code]
            except KeyError:
                norm = getNorm(var_code)
        elif self.norm:
            norm = self._plot_info.norm 
        else:
            norm = getNorm(var_code)
        return norm
    
    def getCmap(self, var_code)->mcolors.Colormap:
        if self.cmap_dict:
            try:
                cmap = self.cmap_dict[var_code]
            except KeyError:
                cmap = getColorMap(var_code)
        elif self.cmap:
            cmap = self.cmap 
        else:
            cmap = getColorMap(var_code)
        if isinstance(cmap, str):
            cmap = cm.get_cmap(cmap)
        return cmap
    
    def handleData(self, var_code:str, data:np.ndarray)->np.ndarray:
        if self.adjust_data:
            res = self.adjust_data(var_code, data)
            if var_code == "0513" or var_code == "0503":
                if np.array_equal(res, data): 
                    res = adjustData(var_code, data) 
        else:
            res = adjustData(var_code, data)
        return res

# formats, so that months and years are only printed, when they change
class CustomFormatter(mdates.DateFormatter):
    def __init__(self, month_fmt, year_fmt):
        self.month_fmt = month_fmt
        self.year_fmt = year_fmt
        super().__init__(month_fmt)

    def __call__(self, x, pos=0):
        # Convert the current x value to a date
        current_date = mdates.num2date(x)

        # If this is the first date, there's no previous date to compare to
        if pos == 0:
            self.prev_date = current_date
            return current_date.strftime(self.year_fmt)

        # If the current date and the previous one have the same year, return the month format
        if current_date.year == self.prev_date.year:
            if current_date.month == self.prev_date.month:
                return ''
            else:
                self.prev_date = current_date
                return current_date.strftime(self.month_fmt)

        # Otherwise, update the previous date and return the year format
        self.prev_date = current_date
        return current_date.strftime(self.year_fmt)
    
def _add_crust_lines(ax:plt.Axes, x:list, h:np.ndarray, mesh:np.ndarray, ind_mfcrust:bool = True,new_color:bool = False):
    crust_mesh = np.ma.masked_where(mesh != 7.2, mesh)
    if new_color and not ind_mfcrust:
        ax.pcolor(x,h, crust_mesh.transpose(), color='orange')
    elif ind_mfcrust and not new_color:
        ax.pcolor(x,h, crust_mesh.transpose(), hatch="///", alpha=0.)
    elif new_color and ind_mfcrust:
        ax.pcolor(x, h, crust_mesh.transpose(), color='orange', hatch='///', alpha=0.)
    else:
        pass