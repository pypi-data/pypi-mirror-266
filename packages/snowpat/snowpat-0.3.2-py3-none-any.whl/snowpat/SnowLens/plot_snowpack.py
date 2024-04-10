import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.collections import QuadMesh
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib as mpl

import pandas as pd
import datetime
import numpy as np
from typing import Optional, List

from .plot_helpers_snowpack import PlotHelper, CustomFormatter, _add_crust_lines
from .plotting import plotProfile
from snowpat.snowpackreader import SnowpackReader
from .Utils import show_figure


class SnowpackPlotter:
    def __init__(self, snowpack: SnowpackReader, savefile=None):
        """
        Initializes an instance of the SnowpackPlotter class.

        Args:
            snowpack (SnowpackReader): The snowpack reader object.
            savefile (str, optional): The path to save the plot. Defaults to None.
        """
        if not isinstance(snowpack, SnowpackReader):
            raise ValueError(f"A SnowpackReader object has to be provided, got {type(snowpack).__name__}")
        
        self.savefile = savefile
        self.snowpack = snowpack
        self.latest_fig: Optional[plt.Figure] = None
        self.plot_helper = PlotHelper()
        
        # internal variables
        self.n_cols = 1
                    
    def plot(self, var_codes:List[str] = ["0513"],**kwargs) -> plt.Figure:
        """
        Plots the data for the given variable codes.

        A figure is created with subplots for each variable code.

        Args:
            var_codes (list): A list of variable codes to plot.
            **kwargs: Arbitrary keyword arguments for additional configuration.

        Returns:
            matplotlib.pyplot.Figure: The created figure.
            
        Optional keyword arguments:
        - start (datetime): The start date for the plot.
        - stop (datetime): The stop date for the plot.
        - resolution (str): The resolution for the plot.
        - num_ticks (int): The number of ticks on the x-axis.
        - cmap (Union[mcolors.Colormap, Dict[str, mcolors.Colormap]]): The colormap for the plot.
        - norm (Union[mcolors.Normalize, Dict[str, mcolors.Normalize]]): The normalization for the plot.
        - cbar_label (Union[str, Dict[str,str]]): The colorbar label for the plot.
        - n_cols (int): The number of columns for the subplots.
        - title (str): The title for the plot.
        - vmin (Union[int, Dict[str,int]]): The minimum value for the colormap.
        - vmax (Union[int, Dict[str,int]]): The maximum value for the colormap.
        - adjust_data (Callable[[str,np.ndarray],np.ndarray]): A function for adjusting the data.
        - single_ticks (bool): Whether to use a single x-axis/y-axis for all subplots. (default: True)
        - set_ylabel (bool): Whether to set the y-axis label. (default: True)
        - colorbar (bool): Whether to display the colorbar. (default: True)
        - ind_mfcrust (bool): Whether to indicate the MFCrust specifically. (default: True)
        - mfcrust_color (bool): Plot the meltcrust in orange instead of read. (default: False)
        - subtitle (Dict[str,str]): A dictionary with subtitles for each variable code.

        All other keyword arguments are passed to the pcolormesh function.


        Raises:
            ValueError: If any of the variable codes are not valid.
            RuntimeError: If there is a problem during plotting.
        """
        dates = self._init_data(var_codes)
        
        kwargs = self._parse_kwargs(**kwargs)

        plot_dates, tick_dates = self._aggregateData(var_codes, dates)


        # calculate the number of rows and cols for the subplots
        n_subplots = len(var_codes)
        n_rows = n_subplots // self.plot_helper.n_cols
        if n_subplots % self.plot_helper.n_cols != 0:
            n_rows += 1
        
        # adjust the figure size so it stays nicely looking within a grid
        fig_x = 6.4 * (1+ 2.0 * (self.plot_helper.n_cols-1)) if self.plot_helper.n_cols > 1 else 6.4
        fig_y = 4.8 * (1 + 1.0* (n_rows - 1)) if n_rows > 1 and self.plot_helper.n_cols > 1 else 4.8 * (1 + 0.2* (n_rows - 1))
        fig, axes = plt.subplots(n_rows, self.plot_helper.n_cols, figsize=(fig_x,fig_y), sharex=self.plot_helper.single_ticks, sharey=self.plot_helper.single_ticks)
        
        # add some space between the subplots, to make space for ticks and cbars
        wspace = 0.4 if self.plot_helper.n_cols > 1 and not self.plot_helper.single_ticks else 0.3
        hspace = 0.4 if n_rows > 1 else 0.2
        fig.subplots_adjust(hspace=hspace, wspace=wspace)
        
        if self.plot_helper.title:
            fig.suptitle(self.plot_helper.title, fontsize=16)
        
        # set the indexes at which subplot the x/y labels should be set
        if self.plot_helper.n_cols > 1 and n_rows > 1:
            ids_ylabels = [i for i in range(1, n_subplots+1) if i % self.plot_helper.n_cols == 1]
            ids_xlabels = [i for i in range(n_subplots-self.plot_helper.n_cols+1, n_subplots+1)]
        elif self.plot_helper.n_cols == 1 and n_rows > 1:
            ids_ylabels = [i for i in range(1, n_subplots+1)]
            ids_xlabels = [n_subplots]
        elif self.plot_helper.n_cols > 1 and n_rows == 1:
            ids_ylabels = [1]
            ids_xlabels = [i for i in range(1, n_subplots+1)]
        else:
            ids_xlabels = [1]
            ids_ylabels = [1]

        row = 0
        col = 0
        for sub_id in range(1, n_subplots+1):
            var_code = var_codes[sub_id-1]

            # if it is only one subplot, axes is not an array
            if isinstance(axes, mpl.axes.Axes):
                ax = axes
            else:
                # we need to get the correct axes object, whether it is a 1D or 2D array
                ax = axes[row, col] if self.plot_helper.n_cols > 1 and n_rows > 1 else axes[row]            
            row += 1 if (sub_id % self.plot_helper.n_cols == 1) or (self.plot_helper.n_cols == 1 or n_rows == 1) else 0
            col = (col+1) % self.plot_helper.n_cols           
            
            cmap = self.plot_helper.getCmap(var_code)
            norm = self.plot_helper.getNorm(var_code)
            cmap.set_bad(ax.get_facecolor())
            
            mpl.rcParams['hatch.linewidth'] = 3.0
            plot_dates_len = len(plot_dates)

            for date_id, plot_date in enumerate(plot_dates):
                # set the bar to the correct date, i.e. the x boundaries
                x = [plot_date, plot_dates[date_id+1]] if date_id < plot_dates_len-1 else [plot_date, plot_date + pd.Timedelta(days=1)]
                profile = self.snowpack.get_profile_on(plot_date)
                # get the layer boundaries, which will be the y boundaries
                h = profile.get_param("0501") # "0501" are the layer boundaries
                # the data in the cells
                data = profile.get_param(var_code)
                data = self.plot_helper.handleData(var_code, data)
                if h.size == 1: continue

                # we need to handle missing values
                mesh = np.array([data,])
                conditions = mesh== -999
                masked_mesh = np.ma.masked_where(conditions, mesh)     

                cplot = ax.pcolormesh(x, h, masked_mesh.transpose(), norm=norm, cmap=cmap, **kwargs)
                if var_code == "0513":
                    # this function will add the crust lines to the plot, if it any is set to true
                    _add_crust_lines(ax, x, h, mesh, self.plot_helper.ind_mfcrust, self.plot_helper.mfcrust_color)
           
            # set the x and y limits, for better visualization
            ax.set_xlim(self.plot_helper.start, self.plot_helper.stop)
            hmax = self.snowpack.get_profile_on(self.plot_helper.stop).get_param("0501")[-1]
            ymax = hmax if hmax > 250 else 250
            ymin,_ = ax.get_ylim()
            ax.set_ylim(ymin, ymax)            
            
                
            self._setColorbar(ax, cplot, var_code, fig)
            self._set_title(ax, var_code)
                        
            # set xticks
            if (self.plot_helper.single_ticks and sub_id in ids_xlabels) or not self.plot_helper.single_ticks:
                if self.plot_helper.num_ticks:
                    ax.set_xticks(tick_dates)
                    labels = [mdates.num2date(label).strftime('%Y-%m-%d') for label in ax.get_xticks()]
                    ax.set_xticklabels(labels, rotation=30)
                else:
                    custom_formatter = CustomFormatter('%m-%d', '%m-%d\n%Y')
                    ax.xaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))
                ax.set_xlabel("Date")
            if (self.plot_helper.single_ticks and sub_id in ids_ylabels) or not self.plot_helper.single_ticks and self.plot_helper.set_ylabel:
                ax.set_ylabel("HS [cm]")

                    
        self.latest_fig = fig   
        plt.close(fig)
        return self.latest_fig
        
    def save(self, outfile: str = None):
        """
        Save the latest figure to an output file.

        Args:
            outfile (str, optional): The path to the output file. If not provided,
                the figure will be saved to the default savefile specified during
                object initialization.

        Raises:
            ValueError: If no output file is provided.
        """
        if outfile:
            self.latest_fig.savefig(outfile)
        elif self.savefile:
            self.latest_fig.savefig(self.savefile)
        else:
            raise ValueError("No output file provided")
        
    def getSubplot(self, index: int) -> plt.Axes:
        """
        Retrieve a subplot from the latest figure.

        Parameters:
            index (int): The index of the subplot to retrieve.

        Returns:
            plt.Axes: The requested subplot.

        """
        n_cols = self.plot_helper.n_cols
        row = (index-1) // n_cols if n_cols > 1 else index
        col = (index-1) % n_cols if n_cols > 1 else 0
        return self.latest_fig.get_axes()[row] if n_cols == 1 else self.latest_fig.get_axes()[row, col]
    
    def getLatestFigure(self)->plt.Figure:
        return self.latest_fig

    def plotProfileOn(self, date:datetime, **kwargs):
        profile = self.snowpack.get_profile_on(date)
        self.latest_fig =  plotProfile(profile, **kwargs)
        return self.latest_fig
        
    def show(self):
            """
            Displays the latest figure of the snowpack.

            """
            show_figure(self.latest_fig)

    def _parse_kwargs(self, **kwargs):
        if "start" in kwargs:
            self.plot_helper.start = kwargs.pop("start")
        if "stop" in kwargs:
            self.plot_helper.stop = kwargs.pop("stop")
        if "resolution" in kwargs:
            self.plot_helper.resolution = kwargs.pop("resolution")
        if "cbar_label" in kwargs:
            cbar_label = kwargs.pop("cbar_label")
            if cbar_label is None:
                self.plot_helper.set_cbar_label = False
            else:
                self.plot_helper.cbar_label = cbar_label
        if "n_cols" in kwargs:
            self.plot_helper.n_cols = kwargs.pop("n_cols")
        if "num_ticks" in kwargs:
            self.plot_helper.num_ticks = kwargs.pop("num_ticks")      
        if "cmap" in kwargs:
            cmap = kwargs.pop("cmap")
            if isinstance(cmap, mcolors.Colormap):
                self.plot_helper.cmap = cmap
            elif isinstance(cmap, dict):
                self.plot_helper.cmap_dict = cmap
            else:
                raise ValueError("cmap must be a mcolors.Colormap object or a dict with var_codes as keys and mcolors.Colormap objects as values")
        if "norm" in kwargs:
            norm = kwargs.pop("norm")
            if isinstance(norm, mcolors.Normalize):
                self.plot_helper.norm = norm
            elif isinstance(norm, dict):
                self.plot_helper.norm_dict = norm
            else:
                raise ValueError("norm must be a mcolors.Normalize object or a dict with var_codes as keys and mcolors.Normalize objects as values")
        if "title" in kwargs:
            self.plot_helper.title = kwargs.pop("title")
        if "vmin" in kwargs and "vmax" in kwargs:
            vmin = kwargs.pop("vmin")
            vmax = kwargs.pop("vmax")
            if isinstance(vmin, int) and isinstance(vmax, int):
                self.plot_helper.norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
            elif isinstance(vmin, dict) and isinstance(vmax, dict):
                self.plot_helper.norm_dict = {var_code: mcolors.Normalize(vmin=vmin[var_code], vmax=vmax[var_code]) for var_code in vmin.keys()}
        elif ("vmin" in kwargs and not "vmax" in kwargs) or (not "vmin" in kwargs and "vmax" in kwargs):
            raise ValueError("Both vmin and vmax must be provided")
        if "adjust_data" in kwargs:
            self.plot_helper.adjust_data = kwargs.pop("adjust_data")
        if "subtitle" in kwargs:
            self.plot_helper.subtitle = kwargs.pop("subtitle")
            
        self.plot_helper.single_ticks = kwargs.pop("single_ticks", True)
        self.plot_helper.set_ylabel = kwargs.pop("set_ylabel", True)
        self.plot_helper.colorbar = kwargs.pop("colorbar", True)
        self.plot_helper.ind_mfcrust = kwargs.pop("ind_mfcrust", True)
        self.plot_helper.mfcrust_color = kwargs.pop("mfcrust_color", False)
        
        return kwargs
                   
    
    def _init_data(self, var_codes):
        for var_code in var_codes:
            if not self.snowpack.DataCodes.get(var_code):
                raise ValueError(f"Invalid variable code: {var_code}")
        dates = self.snowpack.get_all_dates()
        self.plot_helper.start = dates[0]
        self.plot_helper.stop = dates[-1]
        return dates
        
    def _aggregateData(self, var_codes, dates):
        start = self.plot_helper.start
        stop = self.plot_helper.stop
        if self.plot_helper.resolution:
            dates = pd.date_range(start, stop, freq=self.plot_helper.resolution)
            
        plot_dates = []
        for date in dates:
            profile = self.snowpack.get_profile_on(date)
            if profile:
                plot_dates.append(date)

                    
        tick_dates = None
        if self.plot_helper.num_ticks:
            tick_dates = pd.date_range(start, stop, freq=(stop-start)/self.plot_helper.num_ticks)
            if (stop-start) > pd.Timedelta(days=1):
                tick_dates = tick_dates.floor("D")
            else:
                tick_dates = tick_dates.floor("H")
        
        return plot_dates, tick_dates

    def _setColorbar(self, ax:plt.Axes, cplot:QuadMesh, var_code:str, fig:plt.Figure):
        if self.plot_helper.colorbar:
            ax_pos = ax.get_position()
            cax = fig.add_axes([ax_pos.x1+0.01, ax_pos.y0, 0.02, ax_pos.height])
            cbar = plt.colorbar(cplot, cax=cax)
            
            label, is_available = self.plot_helper.getCbarLabel(var_code)
            
            if is_available:
                cbar.set_label(label, fontsize=10)
            else:
                name = self.snowpack.DataCodes.get(var_code, var_code)
                unit = self.snowpack.units.get(var_code, "b.E.")
                label = name + "\n[" + unit + "]"
                cbar.set_label(label, fontsize=10)
                
            if var_code == "0513":
                cbar.set_ticks([1,2,3,4,5,6,7,8,9])
                cbar.set_ticklabels(['PP', 'DF', 'RG', 'FC', 'DH', 'SH', 'MF', 'IF', 'FCxr'])
                cbar.minorticks_off()

    def _set_title(self, ax:plt.Axes, var_code:str):
        title, is_available = self.plot_helper.getSubtitle(var_code)
        if is_available:
            ax.set_title(title)
        
