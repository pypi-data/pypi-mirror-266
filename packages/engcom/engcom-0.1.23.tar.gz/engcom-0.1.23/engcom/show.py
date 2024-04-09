"""Show the most recent figure (for publication)"""
import matplotlib.pyplot as plt
import pathlib
from IPython.display import display, Markdown, Latex
import engcom.tufte

fignum = 0

def figure_markup(filename, caption, label, ext):
    return Markdown(f"![{caption}]({filename}){{#{label} .figure .{ext}}}")

def show(fig, filename=None, ext="pgf", caption="A caption.", label=None, figsize=(4, 4/1.618)):
    global fignum
    plt.figure(fig)
    ax = plt.gca()
    fig.set_size_inches(*figsize)
    if filename is None:
        filename = f"figure-{fignum}.{ext}"
        fignum += 1
    elif not filename[-4] == ("."):
        filename = filename + f".{ext}"
    filename = pathlib.Path(filename)
    parent = filename.resolve().parent.name
    grandparent = filename.resolve().parent.parent.name
    # ax.xaxis.set_label_coords(1.02, 0) # the label can get cut off
    # ax.xaxis.label.set(ha='left',) # the label can get cut off
    # ax.yaxis.set_label_coords(0, 1.02)
    # ax.yaxis.label.set(rotation='horizontal', ha='center',)
    plt.savefig(filename, bbox_inches='tight', dpi=600)
    if label is None:
        label = f"fig:{parent}-{filename.stem}"
    return figure_markup(f"{grandparent}/{parent}/{filename}", caption, label, ext)
