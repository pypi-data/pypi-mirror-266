import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import pandas as pd
import matplotlib.patches as patches
from matplotlib.path import Path
import plotly.graph_objects as go
from .config import Config

#scatterplot

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
        return scatterplot_plotly(df, xvar, yvar, color=color, size=10*size, marker=plotly_marker, save_path=save_path)



def scatterplot_plotly(df=None, xvar=None, yvar=None, color='blue', colormap='Viridis', size=10, marker='circle', save_path=None):
    xdata = df[xvar] if df is not None and isinstance(xvar, str) else xvar
    ydata = df[yvar] if df is not None and isinstance(yvar, str) else yvar

    fig = go.Figure()

    if df is not None and isinstance(color, str) and color in df.columns:
        fig.add_trace(go.Scatter(x=xdata, y=ydata, mode='markers',
                                 marker=dict(size=size, color=df[color], colorscale=colormap, showscale=True),
                                 name=''))
    else:
        fig.add_trace(go.Scatter(x=xdata, y=ydata, mode='markers',
                                 marker=dict(color=color, size=size, symbol=marker),
                                 name=''))

    xaxis_title = xvar if isinstance(xvar, str) else 'x-axis'
    yaxis_title = yvar if isinstance(yvar, str) else 'y-axis'
    fig.update_layout(title="Scatter Plot",
                      xaxis_title=xaxis_title,
                      yaxis_title=yaxis_title,
                      legend_title="Legend",
                      template="plotly_white")

    if save_path is not None:
        fig.write_html(save_path)
    else:
        fig.show()

    return fig


def scatterplot_matplotlib(df, xvar, yvar, color='k',colormap='viridis', size=1, marker='.', ax=None, save_path=None):
    # print('matplotlib')
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
    # print(x_patch_length)
    
    y_data_length = max(ydata) - min(ydata)
    y_patch_length = (y_data_length / len(ydata)) / 5
    # print(y_patch_length)
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

#line plot

def lineplot(df, xvar, yvar, color='black', colormap = None, size=6, style='-', marker=None, save_path=None):
    if Config.plot_backend == 'matplotlib':
        # print('matplotlib')
        # (df, x=[], y=[], color='k', size=1, style='-', marker=None, ax=None, save_path=None)
        matplotlib_marker = convert_marker(marker, to='matplotlib')
        return lineplot_matplotlib(df, xvar, yvar, color, size, style, marker=matplotlib_marker, save_path=save_path)
    elif Config.plot_backend == 'plotly':
        # print('plotly')
        plotly_marker = convert_marker(marker, to='plotly')
        return lineplot_plotly(df, xvar, yvar, color, size=size, style=style, marker=plotly_marker, save_path=save_path)



def lineplot_plotly(df, x=[], y=[], color='black', size=6, style='solid', marker=None, save_path=None):
    line_styles = {
        'solid': None,
        'dash': 'dash',
        'dot': 'dot',
        'dashdot': 'dashdot',
    }
    line_style = line_styles.get(style, None)

    if isinstance(x, str) and df is not None:
        xdata = df[x]
    else:
        xdata = x
    if isinstance(y, str):
        ydata = df[y]
    else:
        ydata = y

    fig = go.Figure(data=go.Scatter(x=xdata, y=ydata, 
                                    mode='lines+markers' if marker else 'lines',
                                    line=dict(color=color, dash=line_style),
                                    marker=dict(color=color, size=size, symbol=marker)))
    
    fig.update_layout(title="Line Plot",xaxis_title=str(x),yaxis_title=str(y),legend_title="Legend",template="plotly_white")

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

#barplot

def barplot(df, xvar, yvar, orientation='vertical', color='lightblue', save_path=None, axis=None):
    if Config.plot_backend == 'matplotlib':
        return barplot_matplotlib(df, xvar, yvar, orientation=orientation, color=color, axis=axis, save_path=save_path)
    elif Config.plot_backend == 'plotly':
        return barplot_plotly(df, xvar, yvar, orientation=orientation, color=color, save_path=save_path)

def barplot_plotly(df, xvar, yvar, orientation='vertical', color='lightblue', save_path=None):
    if orientation == 'vertical':
        means = df.groupby(yvar)[xvar].mean()
        sems = df.groupby(yvar)[xvar].sem()
    else:  #orientation == 'horizontal'
        means = df.groupby(yvar)[xvar].mean()
        sems = df.groupby(yvar)[xvar].sem()

    categories = means.index.tolist()
    means = means.tolist()
    sems = sems.tolist()

    if orientation == 'vertical':
        fig = go.Figure(data=go.Bar(
            x=categories,
            y=means,
            marker_color=color,
            error_y=dict(type='data', array=sems, visible=True)  # Add vertical error bars
        ))
    elif orientation == 'horizontal':
        fig = go.Figure(data=go.Bar(
            y=categories,
            x=means,
            marker_color=color,
            orientation='h',
            error_x=dict(type='data', array=sems, visible=True)  # Add horizontal error bars
        ))
    else:
        raise ValueError("Invalid orientation. Choose 'vertical' or 'horizontal'.")

    fig.update_layout(
        title=f"{yvar} by {xvar}",
        xaxis_title=xvar if orientation == 'vertical' else yvar,
        yaxis_title=yvar if orientation == 'vertical' else xvar,
        template="plotly_white"
    )

    if save_path:
        fig.write_html(save_path)
    else:
        fig.show()

    return fig

def barplot_matplotlib(df, xvar, yvar, orientation='vertical', color='lightblue', axis=None, save_path=None):
    if axis is None:
        fig, axis = plt.subplots()

    if orientation == 'vertical':
        if isinstance(xvar, str):
            categories = df[xvar].unique()
            x = np.arange(len(categories))
            heights = df.groupby(xvar)[yvar].mean()
            errors = df.groupby(xvar)[yvar].sem()
        else:
            x = xvar
            heights = x.mean()
            errors = x.sem()
        bars = []
        for i, (category, height) in enumerate(zip(categories, heights)):
            error_line = mlines.Line2D([x[i], x[i]], [height-(errors[category]/2), height+(errors[category]/2)], color='black')
            error_line_top = mlines.Line2D([x[i] - 0.1, x[i] + 0.1], [height+(errors[category]/2), height+(errors[category]/2)], color='black')
            error_line_bottom = mlines.Line2D([x[i] - 0.1, x[i] + 0.1], [height-(errors[category]/2), height-(errors[category]/2)], color='black')
            rect = patches.Rectangle((x[i] - 0.4, 0), 0.8, height,facecolor=color, edgecolor='black')
            bars.append(rect)
            axis.add_patch(rect)
            axis.add_line(error_line)
            axis.add_line(error_line_top)
            axis.add_line(error_line_bottom)

        axis.set_xticks(x)
        axis.set_xticklabels(categories)
        axis.set_xlabel(xvar)
        axis.set_ylabel(yvar)
        axis.autoscale()
        axis.set_ylim(bottom=0)

    elif orientation == 'horizontal':
        temp = yvar
        yvar = xvar
        xvar = temp
        categories = df[yvar].unique()
        y = np.arange(len(categories))
        heights = df.groupby(yvar)[xvar].mean()
        errors = df.groupby(yvar)[xvar].sem()

        bars = []
        for i, (category, height) in enumerate(zip(categories, heights)):
            error_line = mlines.Line2D([height-(errors[category]/2), height+(errors[category]/2)], [y[i], y[i]],color='black')
            error_line_top = mlines.Line2D([height+(errors[category]/2), height+(errors[category]/2)], [y[i] - 0.1, y[i] + 0.1], color='black')
            error_line_bottom = mlines.Line2D([height-(errors[category]/2), height-(errors[category]/2)], [y[i] - 0.1, y[i] + 0.1], color='black')
            rect = patches.Rectangle((0, y[i] - 0.4), height, 0.8,facecolor=color, edgecolor='black')
            bars.append(rect)
            axis.add_patch(rect)
            axis.add_line(error_line)
            axis.add_line(error_line_top)
            axis.add_line(error_line_bottom)

        axis.set_yticks(y)
        axis.set_yticklabels(categories)
        axis.set_ylabel(yvar)
        axis.set_xlabel(xvar)
        axis.autoscale()
        axis.set_xlim(0)
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()

    return axis

def jointplot(x, y, ax=None, color='black', title='Joint Plot', save_path=None):
    fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    #top line plot
    axs[0].set_title(title)
    axs[0].tick_params(axis='x',which='both', bottom=False,top=False,labelbottom=False)
    axs[0].spines['bottom'].set_visible(False)
    axs[0].spines['right'].set_visible(False)
    axs[0].spines['top'].set_visible(False)
    lineplot(None,x,y, color=color, ax=axs[0])

    #bottom scatterplot
    axs[1].spines['top'].set_visible(False)
    axs[1].spines['right'].set_visible(False)
    axs[1].set_xlabel('X axis')
    scatterplot(None, x,y, color=color, ax=axs[1])
    
    if save_path:
        plt.savefig(save_path)


def collides(x1,y1,x2,y2, r):
    return np.sqrt((x1-x2)**2 + (y1-y2)**2) < 2 * r

def check_collisions(candidate_ys, collisions, x, r):
    candidate_ys = sorted(candidate_ys, key=np.abs)
    for y in candidate_ys:
        has_collision = False
        for (x_prime, y_prime) in collisions:
            if collides(x, y, x_prime, y_prime, r): 
                has_collision = True
                break
        if not has_collision:
            return y

def swarmplot_inner(X, C, y_offset = 0, r=0.05, ax=None):
    Y = np.zeros_like(X)
    if ax == None:
        fig, ax = plt.subplots()
    for i in range(len(X)):
        collisions = []
        for j in range(i-1,0,-1):
            if X[i] - X[j] > 2 * r:
                break
            else:
                collisions.append((X[j], Y[j]))

        candidate_ys = [0]
        for (x_prime, y_prime) in collisions:
            candidate_ys.append(y_prime + np.sqrt(np.abs((2 * r) ** 2 - (X[i] - x_prime) ** 2)))
            candidate_ys.append(y_prime - np.sqrt(np.abs((2 * r) ** 2 - (X[i] - x_prime) ** 2)))
        
        Y[i] = check_collisions(candidate_ys, collisions, X[i], r)

    scatterplot(None, X, y_offset + Y, color=C, ax=ax)
    
def swarmplot(df, categorical_data, numerical_data, r=0.5, ax=None, save_path=None):
    if ax == None:
        fig, ax = plt.subplots()
    categories = df[categorical_data].unique()
    counter = 0
    colors = ['red', 'green', 'blue']
    for category in categories:
        passed_data = list(df.loc[df[categorical_data] == category][numerical_data])
        swarmplot_inner(passed_data, colors[counter], y_offset=counter,r=r, ax=ax)
        counter += 1
    ax.set_ylabel(categorical_data)
    ax.set_xlabel(numerical_data)
    plt.gca().set_aspect('equal', adjustable='box')
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()

if __name__ == '__main__':
    np.random.seed(120)
    data = pd.DataFrame({
    'Category': ['A']*80 + ['B']*80 + ['C']*80,
    'Value': np.concatenate([np.random.randint(0, 20, size=80), np.random.randint(20, 30, size=80), np.random.randint(30, 50, size=80)])
    })
    x = [1, 2, 3, 4, 5]
    y = [10, 15, 7, 10, 5]

    # lineplot(None,x,y, color='b',save_path="matplottest.png")
    set_plot_backend('plotly')
    scatterplot(None, x, y, color="red", save_path="scatter.html")
    # swarmplot(data, 'Category', 'Value', r=0.8, save_path='test_swarmplot_confirmed.png')
    # Config.set_plot_backend('plotly')
    # lineplot(data,'Category', 'Value', color='purple')