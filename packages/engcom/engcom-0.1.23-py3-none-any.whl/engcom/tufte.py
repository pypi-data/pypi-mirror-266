"""Tufte styling for matplotlib plots"""
import numpy as np
import matplotlib.ticker
import matplotlib.pyplot as plt
import importlib
import sys

params = {
    "pgf.texsystem": "lualatex",
    "font.family": "serif",  # use serif/main font for text elements
    "font.serif": ["Palatino Linotype", "Palatino", "Times New Roman"],
    "mathtext.fontset": "cm",
    "pgf.rcfonts": True,    # don't setup fonts from rc parameters
    "axes.formatter.use_mathtext": True,
    "savefig.bbox": "tight",
    "font.size": 8,
    "axes.labelsize": 8,            
    "axes.titlesize": 8,     
    "figure.labelsize": 8,        
    "legend.fontsize": 8,   
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xaxis.labellocation": "right",
    "xtick.direction": "in",
    "ytick.direction": "in",
    "text.usetex": False,     # use inline math for ticks
    "pgf.preamble": "\n".join([
         r"\RequirePackage[T1]{fontenc}%",
         r"\usepackage{newpxmath} % math font is Palatino compatible",
         r"\let\Bbbk\relax % so it doesn't clash with amssymb",
         r"\usepackage[no-math]{fontspec}",
         r"\setmainfont{Palatino}",
         r"\setmonofont{Latin Modern Mono}[%",
         r"Scale=1.05, % a touch smaller than MatchLowercase",
         r"BoldFont=*,",
         r"BoldFeatures={FakeBold=2}",
         r"]",
         r"\setsansfont{Helvetica}",
         r"\renewcommand{\mathdefault}[1][]{}",
    ])
}

def mpl_params_load():
    if "matplotlib" in sys.modules:
        # print("reloading mpl")
        importlib.reload(matplotlib)
        mpl = matplotlib
    else:
        import matplotlib as mpl
    mpl.use('pgf') # Use the pgf backend (must be set before pyplot imported)
    if "matplotlib.pyplot" in sys.modules:
        # print("reloading plt")
        importlib.reload(matplotlib.pyplot)
        plt = matplotlib.pyplot
    else:
        import matplotlib.pyplot as plt
    plt.rcParams.update(params)

mpl_params_load()  # Runs when module is loaded

def plot(x, y, 
    locator=None, 
    axis=0, 
    xlabel=None, 
    ylabel=None, 
    labels=None, 
    legend=None, 
    legendloc="outside right",
    save=False, 
    figsize=(4.8,4.8/1.618), 
    dotsize=10,
    color="black",
    points=True,
    cmap=plt.get_cmap('coolwarm'),
    xticks=None,
):
    if save:
        mpl_params_load(figsize)
    else:
        import matplotlib as mpl
        import matplotlib.pyplot as plt
    fig, ax = plt.subplots(layout="constrained")
    if len(y.shape) > 1:
        bxis = (axis+1)%2  # The axis we're not plotting along (i.e., the potentially multiple-trace axis)
        m = y.shape[bxis]  # Number of traces
    else:
        bxis = None
        m = 1
    if color == "map":
        colors = cmap(np.linspace(0, 1, m))
    else:
        colors = [color] * m  #  All the same color
    for i in range(m):
        if bxis is None:
            yi = y
        else:
            yi = y.take(indices=i,axis=bxis)
        if points:
            ax.plot(x, yi, linestyle="-", color=colors[i], linewidth=1, zorder=1)
            ax.scatter(x, yi, color="white", s=dotsize+30, zorder=2)
            ax.scatter(x, yi, color=colors[i], s=dotsize, zorder=3)
        else:
            ax.plot(x, yi, linestyle="-", color=colors[i], linewidth=1, zorder=1)
    ax.spines["bottom"].set_bounds(np.min(x), np.max(x))
    ax.spines["left"].set_bounds(np.min(y), np.max(y))
    if locator:
        ax.yaxis.set_major_locator(
            matplotlib.ticker.MultipleLocator(base=locator)
        )
    if xticks is not None:
        ax.set_xticks(xticks)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.text(ylabel)
    if labels:
        for i in range(y.shape[(axis+1)%2]):
            yi = y.take(indices=i,axis=(axis+1)%2).flatten()
            ax.annotate(f"{labels[i]}", xy=(x[-1], yi[-1]), xycoords="data", xytext=(3, 0), textcoords='offset points', horizontalalignment="left", verticalalignment="center")
    if legend:
        fig.legend(legend, loc=legendloc)
    if save:
        plt.savefig(save,bbox_inches='tight')
    return fig, ax

def bar(x, y,
    orientation="vertical",  # or "horizontal"
    xlabel=None, 
    ylabel=None, 
    labels=None,
    save=False, 
    figsize=(4.8,4.8/1.618), 
    barsize=0.6,
    align="center",
    color="black",
    histogram=False,
):
    if save:
        mpl_params_load(figsize)
    else:
        import matplotlib as mpl
        import matplotlib.pyplot as plt
    if histogram:
        barsize = 1  # Override barsize
    x = np.array(x)
    y = np.array(y)
    fig, ax = plt.subplots()
    if orientation == "vertical":
        ax.bar(x, y, color=color, width=barsize, align=align)
    elif orientation == "horizontal":
        ax.barh(y, x, color=color, height=barsize, align=align)
    else:
        raise(NotImplemented(f"Orientation {orientation} not implemented"))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    if orientation == "vertical":
        ax.spines['left'].set_visible(False)
        ax.set_xticks(x)
    elif orientation == "horizontal":
        ax.spines['bottom'].set_visible(False)
        ax.set_yticks(y)
    elif histogram:
        xf = x.flatten()
        dx = x[-1] - x[-2]
        xtra = np.concatenate((x, np.array([x[-1] + dx])))
        ax.set_xticks(xtra)
    if labels is not None:
        if orientation == "vertical":
            ax.set_xticklabels(labels)
        elif orientation == "horizontal":
            ax.set_yticklabels(labels)
    # ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(decimals=0))
    if ylabel:
        ax.text(x=0, y=1.0, s=ylabel, transform=ax.transAxes)
    if xlabel:
        ax.annotate(f"{xlabel}", xy=(1, 0), xycoords="axes fraction", xytext=(0, 3), textcoords='offset points', horizontalalignment="right", verticalalignment="bottom")
    ax.tick_params(bottom=False, left=False)
    if orientation == "vertical":
        ax.yaxis.grid(color='white', linewidth=1)
    elif orientation == "horizontal":
        ax.xaxis.grid(color='white', linewidth=1)
    if barsize == 1:
        if orientation == "vertical":
            ax.xaxis.grid(color='white', linewidth=2)
        elif orientation == "horizontal":
            ax.yaxis.grid(color='white', linewidth=2)
    if save:
        plt.savefig(save,bbox_inches='tight')
    return fig, ax