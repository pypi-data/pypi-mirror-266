import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.pyplot as plt
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
    }
}

def convert_marker(marker, to='plotly'):
    if to == 'plotly':
        return marker_conversion_map['matplotlib_to_plotly'].get(marker, marker)
    elif to == 'matplotlib':
        return marker_conversion_map['plotly_to_matplotlib'].get(marker, marker)
    else:
        return marker

def scatterplot(df, xvar, yvar, color='#ff0000', colormap='viridis', size=1, marker='.', ax=None, save_path=None):
    if Config.plot_backend == 'matplotlib':
        matplotlib_marker = convert_marker(marker, to='matplotlib')
        return scatterplot_matplotlib(df, xvar, yvar, color=color, colormap=colormap, size=size, marker=matplotlib_marker, ax=ax, save_path=save_path)
    elif Config.plot_backend == 'plotly':
        plotly_marker = convert_marker(marker, to='plotly')
        return scatterplot_plotly(df, xvar, yvar, color=color, size=10*size, marker=plotly_marker, save_path=save_path)  # Adjust size as an example



def scatterplot_plotly(df=None, xvar=None, yvar=None, color='blue', colormap='Viridis', size=10, marker='circle', save_path=None):
    # Handle xvar and yvar when they are column names or lists directly
    xdata = df[xvar] if df is not None and isinstance(xvar, str) else xvar
    ydata = df[yvar] if df is not None and isinstance(yvar, str) else yvar

    # Initialize the figure
    fig = go.Figure()

    # Check if color needs to be applied as a colormap from the DataFrame
    if df is not None and isinstance(color, str) and color in df.columns:
        fig.add_trace(go.Scatter(x=xdata, y=ydata, mode='markers',
                                 marker=dict(size=size, color=df[color], colorscale=colormap, showscale=True),
                                 name=''))
    else:
        # Apply a single color to all markers if color is not a column name
        fig.add_trace(go.Scatter(x=xdata, y=ydata, mode='markers',
                                 marker=dict(color=color, size=size, symbol=marker),
                                 name=''))

    # Optional: Customize layout (title, axis labels, etc.)
    xaxis_title = xvar if isinstance(xvar, str) else 'x-axis'
    yaxis_title = yvar if isinstance(yvar, str) else 'y-axis'
    fig.update_layout(title="Scatter Plot",
                      xaxis_title=xaxis_title,
                      yaxis_title=yaxis_title,
                      legend_title="Legend",
                      template="plotly_white")

    # Save the plot if a save_path is provided
    if save_path is not None:
        fig.write_html(save_path)
    else:
        fig.show()

    return fig


def scatterplot_matplotlib(df, xvar, yvar, color='k',colormap='viridis', size=1, marker='.', ax=None, save_path=None):
    print('marplotlib')
    if ax is None:
        fig, ax = plt.subplots()
    if isinstance(xvar, str):
        xdata = df[xvar]
    else:
        xdata = xvar
        
    if isinstance(yvar, str):
        ydata = df[yvar]
    else:
        ydata = yvar
    x_data_length = max(xdata) - min(xdata)
    x_patch_length = (x_data_length / len(xdata)) / 5
    print(x_patch_length)
    
    y_data_length = max(ydata) - min(ydata)
    y_patch_length = (y_data_length / len(ydata)) / 5
    print(y_patch_length)
    patches_li = []
    for i, (x, y) in enumerate(zip(xdata, ydata)):
        #creating small square for "point"
        verts = [
        (x - x_patch_length, y - y_patch_length),  #left, bottom
        (x - x_patch_length, y + y_patch_length),  #left, top
        (x + x_patch_length, y + y_patch_length),  #right, top
        (x + x_patch_length, y - y_patch_length),  #right, bottom
        (x, y),  #back to start
        ]

        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.LINETO,
            Path.LINETO,
            Path.CLOSEPOLY,
        ]
        path = Path(verts, codes)
        patch = patches.PathPatch(path, lw=1, color=color)
        patches_li.append(patch)
    
    for patch in patches_li:
        ax.add_patch(patch)
    ax.set_xlim(min(xdata), max(xdata))
    ax.set_ylim(min(ydata), max(ydata))
    # ax.autoscale()
    ax.legend()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    return ax

if __name__ == "__main__":
    x = [1, 2, 3, 4, 5]
    y = [10, 15, 7, 10, 5]
    data = pd.DataFrame({
    'Category': np.concatenate([np.random.randint(0, 20, size=80), np.random.randint(20, 30, size=80), np.random.randint(30, 50, size=80)]),
    'Value': np.concatenate([np.random.randint(0, 20, size=80), np.random.randint(20, 30, size=80), np.random.randint(30, 50, size=80)])
    })
    # Config.set_plot_backend('plotly')
    plt = scatterplot(None,x, y, color='purple',marker="circle", save_path="test_scatterplot.png")