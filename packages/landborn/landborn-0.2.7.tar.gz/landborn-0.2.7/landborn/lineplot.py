import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from config import Config

marker_conversion_map = {
    'matplotlib_to_plotly': {
        '.': 'circle',
        'o': 'circle',
        'v': 'triangle-down',
        '^': 'triangle-up',
        '<': 'triangle-left',
        '>': 'triangle-right',
        '1': 'triangle-up',
        '2': 'triangle-down',
        '3': 'triangle-left',
        '4': 'triangle-right',
        's': 'square',
        'p': 'pentagon',
        '*': 'star',
        'h': 'hexagon',
        'H': 'hexagon',
        '+': 'cross',
        'x': 'x',
        'D': 'diamond',
        'd': 'diamond',
        '|': 'line-ns',
        '_': 'line-ew',
    },
    'plotly_to_matplotlib': {
        'circle': 'o',
        'square': 's',
        'diamond': 'D',
        'cross': '+',
        'x': 'x',
        'triangle-up': '^',
        'triangle-down': 'v',
        'triangle-left': '<',
        'triangle-right': '>',
        'pentagon': 'p',
        'hexagon': 'h',
        'hexagon2': 'H',
        'star': '*',
        'line-ns': '|',
        'line-ew': '_',
        # Note: Some Plotly markers don't have direct Matplotlib equivalents
    }
}

def convert_marker(marker, to='plotly'):
    """
    Converts a marker style from Matplotlib to Plotly or vice versa.
    
    Parameters:
    - marker: The marker style to convert.
    - to: The target library ('plotly' or 'matplotlib').
    
    Returns:
    - The converted marker style, if a conversion is found; otherwise, the original marker.
    """
    if to == 'plotly':
        return marker_conversion_map['matplotlib_to_plotly'].get(marker, marker)
    elif to == 'matplotlib':
        return marker_conversion_map['plotly_to_matplotlib'].get(marker, marker)
    else:
        return marker

def lineplot(df, xvar, yvar, color='black', colormap = None, size=6, style='-', marker=None, save_path=None):
    if Config.plot_backend == 'matplotlib':
        print('matplotlib')
        # (df, x=[], y=[], color='k', size=1, style='-', marker=None, ax=None, save_path=None)
        matplotlib_marker = convert_marker(marker, to='matplotlib')
        return lineplot_matplotlib(df, xvar, yvar, color, size, style, marker=matplotlib_marker, save_path=save_path)
    elif Config.plot_backend == 'plotly':
        print('plotly')
        plotly_marker = convert_marker(marker, to='plotly')
        return lineplot_plotly(df, xvar, yvar, color, size=size, style=style, marker=plotly_marker, save_path=save_path)



def lineplot_plotly(df, x=[], y=[], color='black', size=6, style='solid', marker=None, save_path=None):
    # Define the line style
    line_styles = {
        'solid': None,
        'dash': 'dash',
        'dot': 'dot',
        'dashdot': 'dashdot',
    }
    line_style = line_styles.get(style, None)

    # Determine x and y data
    if isinstance(x, str) and df is not None:
        xdata = df[x]
    else:
        xdata = x
    if isinstance(y, str):
        ydata = df[y]
    else:
        ydata = y

    # Create the Plotly figure
    fig = go.Figure(data=go.Scatter(x=xdata, y=ydata, 
                                    mode='lines+markers' if marker else 'lines',
                                    line=dict(color=color, dash=line_style),
                                    marker=dict(color=color, size=size, symbol=marker)))
    
    # Optional: Customize the layout
    fig.update_layout(title="Line Plot",xaxis_title=str(x),yaxis_title=str(y),legend_title="Legend",template="plotly_white")

    # Save the plot if a save_path is provided
    if save_path:
        fig.write_html(save_path)
    else:
        fig.show()

    return fig



def lineplot_matplotlib(df, x=[], y=[], color='k', size=1, style='-', marker=None, ax=None, save_path=None):
    if ax is None:
        fig, ax = plt.subplots()

    if isinstance(x, str) and df is not None:
        xdata = df[x]
    else:
        xdata = x
    if isinstance(y, str):
        ydata = df[y]
    else:
        ydata = y

    line = mlines.Line2D(xdata, ydata, color=color, linestyle=style, marker=marker, markersize=size)
    ax.add_line(line)
    ax.autoscale()
    
    if save_path:
        plt.savefig(save_path)

    return ax

if __name__ == "__main__":
    x = [1, 2, 3, 4, 5]
    y = [10, 15, 7, 10, 5]
    data = pd.DataFrame({
    'Category': np.concatenate([np.random.randint(0, 20, size=80), np.random.randint(20, 30, size=80), np.random.randint(30, 50, size=80)]),
    'Value': np.concatenate([np.random.randint(0, 20, size=80), np.random.randint(20, 30, size=80), np.random.randint(30, 50, size=80)])
    })
    plt = lineplot(data, 'Category', 'Value', color='yellow',save_path="test_lineplot.html")