from .. import snowpackreader as spr
from .. import pysmet as smet
from typing import Optional, List
import matplotlib.pyplot as plt

from .plot_snowpack import SnowpackPlotter, plotProfile
from .Utils import PlotType, SNOWPACK_KWARGS, SNOWPACK_HELP_TEXT, _type_to_string, PROFILE_HELP_TEXT, PROFILE_KWARGS, GENERAL_HELP_TEXT, GENERAL_KWARGS, _is_of_type

from .plotting import show_logo

def plot(snowpack_file: Optional[spr.SnowpackReader] = None, smetfile: Optional[smet.SMETFile] = None, profile:Optional[spr.Snowpack] = None, **kwargs):
    """
    Plot function for visualizing Snowpack or SMET data.
    Only one of snowpack, smet, or profile should be provided.

    Parameters:
    - snowpack: Optional[spr.SnowpackReader], the snowpack data to plot.
    - smet: Optional[smet.SMETFile], the SMET file to plot.
    - profile: Optional[spr.Snowpack], the snowpack profile to plot.
    - **kwargs: Additional keyword arguments for customizing the plot.

    Returns:
    - fig: matplotlib.figure.Figure, the generated plot figure.
    - plotter: SnowpackPlotter, the plotter object used for generating the plot. (None if profile is provided)


    use plot("snowpat") to show the snowpat logo
    """
    if snowpack_file == "snowpat": 
        show_logo()
        return None, None
    
    def assign_arg(arg):
        nonlocal snowpack_file, smetfile, profile
        if isinstance(arg, spr.SnowpackReader):
            snowpack_file = arg
            smetfile = None
            profile = None            
        elif isinstance(arg, smet.SMETFile):
            smetfile = arg  
            snowpack_file = None
            profile = None
        elif isinstance(arg, spr.Snowpack):
            profile = arg
            snowpack_file = None    
            smetfile = None
        elif arg is None:
            pass
        else:
            raise TypeError(f"Arguments need to be one of: [SNOWPACK, SMET, PROFILE]; got: {type(arg).__name__}")
    
    assign_arg(snowpack_file)
    assign_arg(smetfile)
    assign_arg(profile)
    _check_args(snowpack_file, smetfile, profile)
    
    outfile = None
    if "outfile" in kwargs:
        outfile = kwargs.pop("outfile")
    
    if snowpack_file:
        _check_kwargs(PlotType.PRO, **kwargs)
        plotter = SnowpackPlotter(snowpack_file)
        if "profile_on" in kwargs:
            date = kwargs.pop("profile_on")
            plotter.plotProfileOn(date, **kwargs)
        else:
            plotter.plot(**kwargs)
        if outfile:
            plotter.save(outfile)
    elif smetfile:
        _check_kwargs(PlotType.SMET, **kwargs)
        raise NotImplementedError("Plotting from SMET files is not yet implemented")
    elif profile:
        _check_kwargs(PlotType.PROFILE, **kwargs)
        return plotProfile(profile, out=outfile, **kwargs), None
    else:
        raise ValueError("Either snowpack, smet or profile must be provided")   
    return plotter.latest_fig, plotter     


def help(snowpack_file: Optional[spr.SnowpackReader] = None, smetfile: Optional[smet.SMETFile] = None, profile:Optional[spr.Snowpack] = None, **kwargs):
    """
    Display help information for different plot types based on the input.

    Parameters:
    - snowpack: Optional[spr.SnowpackReader] (default: None) - A snowpack reader object.
    - smet: Optional[smet.SMETFile] (default: None) - A SMET file object.
    - profile: Optional[spr.Snowpack] (default: None) - A snowpack object.
    - **kwargs: Additional keyword arguments.

    Returns:
    None
    """
    def assign_arg(arg):
        nonlocal snowpack_file, smetfile, profile
        if isinstance(arg, spr.SnowpackReader):
            snowpack_file = arg
            smetfile = None
            profile = None            
        elif isinstance(arg, smet.SMETFile):
            smetfile = arg  
            snowpack_file = None
            profile = None
        elif isinstance(arg, spr.Snowpack):
            profile = arg
            snowpack_file = None    
            smetfile = None
        elif arg is None:
            pass
        else:
            raise TypeError(f"Arguments need to be one of: [SNOWPACK, SMET, PROFILE]; got: {type(arg).__name__}")
        
    if sum(x is not None for x in [snowpack_file, smetfile, profile]) != 1:
        raise ValueError("Only one of snowpack, smet, or profile should be provided")
    

    assign_arg(snowpack_file)
    assign_arg(smetfile)
    assign_arg(profile)
    _check_args(snowpack_file, smetfile, profile)

    plot_type = None
    if snowpack_file: plot_type = PlotType.PRO
    elif smetfile: plot_type = PlotType.SMET
    elif profile: plot_type = PlotType.PROFILE
    if plot_type:
        _check_kwargs(plot_type,help=True, **kwargs)
    else:
        _print_help(PlotType.PRO)
        _print_help(PlotType.SMET)
        _print_help(PlotType.PROFILE)    


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


def _print_help(plot_type:PlotType):
    if plot_type == PlotType.PRO:
        print(f"Keyword arguments for plotting from .pro files are:")
        for key, val in SNOWPACK_KWARGS.items():
            print(f"\t{key} ({_type_to_string(val)}) : {SNOWPACK_HELP_TEXT[key]}")
        print("And any keyword arguments that are not in the list above will be passed to the pyplot function")
    elif plot_type == PlotType.SMET:
        print(f"Keyword arguments for plotting from .smet files are:")
        print("Not yet implemented")
    elif plot_type == PlotType.PROFILE:
        print(f"Keyword arguments for plotting profiles are:")
        for key, val in PROFILE_KWARGS.items():
            print(f"\t{key} ({_type_to_string(val)}) : {PROFILE_HELP_TEXT[key]}")
        

def _check_kwargs(plot_type:PlotType, help=False,**kwargs):
    if plot_type == PlotType.PRO:
        USED_KWARGS = SNOWPACK_KWARGS
    elif plot_type == PlotType.SMET:
        raise NotImplementedError("Plotting from SMET files is not yet implemented")
    elif plot_type == PlotType.PROFILE:
        USED_KWARGS = PROFILE_KWARGS
    else:
        raise ValueError(f"Unexpected plot type {plot_type}")
    
    outfile = kwargs.pop("outfile", None)
    if not isinstance(outfile, (str, type(None))):
        raise TypeError(f"Unexpected type for outfile {type(outfile).__name__}")
    
    known_kwargs = []
    if outfile: known_kwargs.append("outfile")
    unknown_kwargs = []
    wrong_kwargs = []
    
    # .pro needs var codes
    if plot_type == PlotType.PRO:
        var_codes = kwargs.pop("var_codes", None)
        if not var_codes:
            print("No var_codes provided, only plotting grain types")
        elif not isinstance(var_codes, list) or not all(isinstance(code, str) for code in var_codes):
            raise TypeError("var_codes needs to be a list of strings")
        known_kwargs.append("var_codes")
        
    # check all the rest of the kwargs
    for key, val in kwargs.items():
        if key in USED_KWARGS:
            if not _is_of_type(val, USED_KWARGS[key]):
                wrong_kwargs.append(key)
            else:
                known_kwargs.append(key)
        else:
            unknown_kwargs.append(key)

    if known_kwargs and help:
        print(f"These keyword arguments will be used directly:")
        for key in known_kwargs:
            print(f"\t{key}")
        print("\n")
    if unknown_kwargs:
        print(f"These keyword aruments will be passed to the pyplot function:\n\t {unknown_kwargs}")
        print("\n")
    if wrong_kwargs:
        print(f"These keyword arguments have the wrong type:\n\t {wrong_kwargs}")
        print(f"Expected types are:")
        print(f"{[f'{key}: ({_type_to_string(USED_KWARGS[key])})' for key in wrong_kwargs]}")
        print(f"Got types: {[type(kwargs[key]).__name__ for key in wrong_kwargs]}")
        if type(kwargs[key]).__name__ == "dict":
            print("Please check the dictionary values")
        print("\n")
        _print_help(plot_type)
        raise TypeError(f"Unexpected type for keyword arguments")
    if help:
        _print_help(plot_type)

def _check_args(snowpack_file, smetfile, profile):
    if sum(x is not None for x in [snowpack_file, smetfile, profile]) != 1:
        raise ValueError("Only one of snowpack, smet, or profile should be provided")
    if snowpack_file:
        if not isinstance(snowpack_file, spr.SnowpackReader):
            raise TypeError(f"Unexpected type for .pro file {type(snowpack_file).__name__}")
    elif smetfile:
        if not isinstance(smetfile, smet.SMETFile):
            raise TypeError(f"Unexpected type for .smet file {type(smetfile).__name__}")
    elif profile:
        if not isinstance(profile, spr.Snowpack):
            raise TypeError(f"Unexpected type for profile {type(profile).__name__}")
        