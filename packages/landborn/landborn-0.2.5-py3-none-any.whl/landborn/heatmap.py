import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from config import Config
import plotly.graph_objects as go
import pandas as pd
from matplotlib.colors import Normalize

def gradient_heatmap(data, colormap='viridis', title="Gradient HeatMap", x_label="Data Point Index", save_path=None):
    if Config.plot_backend == 'matplotlib':
        gradient_heatmap_matplotlib(data, colormap=colormap, title=title, x_label=x_label,save_path=save_path)
    elif Config.plot_backend == 'plotly':
        gradient_heatmap_plotly(data, colormap=colormap, title=title, x_label=x_label,save_path=save_path)


def gradient_heatmap_matplotlib(data, colormap='viridis', title="Data Visualization", x_label="testing x",save_path=None):
    fig, ax = plt.subplots()
    
    norm = Normalize(vmin=min(data), vmax=max(data))
    cmap_name = colormap + '_r'
    cmap = matplotlib.colormaps[cmap_name]

    dpi = fig.get_dpi()
    fig_width_in_inches = fig.get_figwidth()
    total_points = len(data)
    linewidth = (fig_width_in_inches * dpi) / total_points

    lines = []
    for i, value in enumerate(data):
        color = cmap(norm(value))
        line = [(i, 0), (i, 1)]
        lines.append((line, color))

    line_segments = LineCollection([line for line, color in lines], colors=[color for line, color in lines], linewidths=(linewidth,))
    ax.add_collection(line_segments)

    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax)

    ax.set_xlim(0, len(data))
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel(x_label)
    ax.set_title(title)
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def gradient_heatmap_plotly(data, colormap='Viridis', title="Data Visualization", x_label="Data Point Index", save_path=None):
    x_data = list(range(len(data)))
    y_data = [1] * len(data)
    hover_texts = [f"Value: {value:.2f}" for value in data]
    
    colorscale_name = colormap + "_r"
    
    fig = go.Figure(data=go.Bar(
        x=x_data,
        y=y_data,
        text=hover_texts,
        hoverinfo="text+x",
        marker=dict(
            color=data,
            colorscale=colorscale_name,
            # colorbar=dict(title=y_label)
        ),
        width=np.full(len(data), 1.05)
    ))

    fig.update_layout(
        xaxis=dict(
            title=x_label,
            showticklabels=True,
        ),
        yaxis=dict(
            showticklabels=False,
            title="",
        ),
        title=title,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=40, b=40),
    )

    if save_path:
        fig.write_html(save_path)
    else:
        fig.show()


def month_year_heatmap(df, title="", colormap='viridis', save_path=None):
    if Config.plot_backend == 'matplotlib':
        month_year_heatmap_matplotlib(df=df, title=title, colormap=colormap, save_path=save_path)
    elif Config.plot_backend == 'plotly':
        month_year_heatmap_plotly(df=df, title=title, colormap=colormap, save_path=save_path)

def month_year_heatmap_matplotlib(df, title='Month-Year Heatmap', colormap='viridis', save_path=None):
    norm = Normalize(vmin=df.min().min(), vmax=df.max().max())
    cmap = matplotlib.colormaps[colormap + "_r"]

    fig, ax = plt.subplots()
    cax = ax.imshow(df.values, cmap=cmap, norm=norm, aspect='auto')

    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_xticklabels(df.columns)
    ax.set_yticklabels(df.index)
    
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    cbar = plt.colorbar(cax, ax=ax)
    cbar.ax.set_ylabel('Magnitude', rotation=-90, va="bottom")
    ax.set_title(title)

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()

def month_year_heatmap_plotly(df, title='Month-Year Heatmap', colormap='Viridis', save_path=None):

    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=colormap + "_r",
        colorbar=dict(title='Magnitude'),
    ))

    fig.update_layout(
        title=title,
        xaxis=dict(title='Year', type='category'),
        yaxis=dict(title='Month'),
    )
    if save_path:
        fig.write_html(save_path)
    else:
        fig.show()





if __name__ == "__main__":
    li = np.concatenate([np.random.randint(0, 20, size=400), np.random.randint(20, 30, size=400), np.random.randint(30, 100, size=400)])
    # print(li)
    gradient_heatmap(li)
    # data = np.random.rand(100)

    # data = pd.DataFrame({
    #     'Category 1': np.random.rand(10),
    #     'Category 2': np.random.rand(10),
    #     'Category 3': np.random.rand(10),
    # }, index=pd.date_range(start='2021-01-01', periods=10, freq='D'))
    
    np.random.seed(0)
    data = np.random.rand(12, 31)  #12 months, 5 years of data

    years = [2010,2011,2012,2013,2014,2015,2016, 2017, 2018, 2019, 2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,2035,2036,2037,2038,2039,2040]
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    df = pd.DataFrame(data, index=months, columns=years)
    # month_year_heatmap(df, title='Month-Year Heatmap Test', colormap="magma")