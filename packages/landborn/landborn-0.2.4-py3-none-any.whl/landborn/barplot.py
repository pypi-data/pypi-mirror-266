import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from config import Config

def barplot(df, xvar, yvar, orientation='vertical', color='lightblue', save_path=None, axis=None):
    if Config.plot_backend == 'matplotlib':
        return barplot_matplotlib(df, xvar, yvar, orientation=orientation, color=color, axis=axis, save_path=save_path)
    elif Config.plot_backend == 'plotly':
        return barplot_plotly(df, xvar, yvar, orientation=orientation, color=color, save_path=save_path)

def barplot_plotly(df, xvar, yvar, orientation='vertical', color='lightblue', save_path=None):
    # Calculate means and SEMs
    if orientation == 'vertical':
        means = df.groupby(yvar)[xvar].mean()
        sems = df.groupby(yvar)[xvar].sem()
    else:  # orientation == 'horizontal'
        means = df.groupby(yvar)[xvar].mean()
        sems = df.groupby(yvar)[xvar].sem()

    # Convert to lists for Plotly
    categories = means.index.tolist()
    means = means.tolist()
    sems = sems.tolist()

    if orientation == 'vertical':
        # Vertical bar plot
        fig = go.Figure(data=go.Bar(
            x=categories,
            y=means,
            marker_color=color,
            error_y=dict(type='data', array=sems, visible=True)  # Add vertical error bars
        ))
    elif orientation == 'horizontal':
        # Horizontal bar plot
        fig = go.Figure(data=go.Bar(
            y=categories,
            x=means,
            marker_color=color,
            orientation='h',
            error_x=dict(type='data', array=sems, visible=True)  # Add horizontal error bars
        ))
    else:
        raise ValueError("Invalid orientation. Choose 'vertical' or 'horizontal'.")

    # Customize layout
    fig.update_layout(
        title=f"{yvar} by {xvar}",
        xaxis_title=xvar if orientation == 'vertical' else yvar,
        yaxis_title=yvar if orientation == 'vertical' else xvar,
        template="plotly_white"
    )

    # Save or show the plot
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
        # Horizontal bar plot
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


if __name__ == "__main__":
    x = [1, 2, 3, 4, 5]
    y = [10, 15, 7, 10, 5]
    # plt = barplot(None, x, y, orientation="vertical" ,save_path="test_scatterplot.png")
    
    df = pd.DataFrame({
        'data values': np.random.normal(5,1,100),
        'categories': np.random.choice(['a','b','c'],replace=True, size=100)
    })
    # df.loc[df['categories'] == 'a','data values'] = df.loc[df['categories'] == 'a']['data values'] * 2 - 6
    ax = barplot(df ,'data values','categories', orientation='vertical', color='pink',save_path="test_barplot.html")
    