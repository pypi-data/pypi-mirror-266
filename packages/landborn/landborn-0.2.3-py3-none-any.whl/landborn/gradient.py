import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import ColorbarBase
from matplotlib.cm import viridis
from config import Config
import plotly.graph_objects as go
import pandas as pd

def custom_visualization_matplotlib(data):
    fig, ax = plt.subplots()
    # Normalize data for colormap
    norm = Normalize(vmin=min(data), vmax=max(data))
    cmap = viridis

    # Calculate optimal linewidth to make lines touch
    dpi = fig.get_dpi()
    fig_width_in_inches = fig.get_figwidth()
    total_points = len(data)
    linewidth = (fig_width_in_inches * dpi) / total_points

    # Create a set of lines
    lines = []
    for i, value in enumerate(data):
        color = cmap(norm(value))  # Map data value to colormap
        line = [(i, 0), (i, 1)]  # Vertical line from (i, 0) to (i, 1)
        lines.append((line, color))

    # Create a LineCollection from the lines
    line_segments = LineCollection([line for line, color in lines], colors=[color for line, color in lines], linewidths=(linewidth,))
    ax.add_collection(line_segments)

    # Add Colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax)

    # Set limits and labels
    ax.set_xlim(0, len(data))
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    plt.show()


def custom_visualization_plotly(data, x_label="Data Point Index", y_label="", title="Data Visualization with Viridis", save_path=None):
    # Prepare data for plotting
    x_data = list(range(len(data)))
    y_data = [1] * len(data)  # Constant height for all bars
    hover_texts = [f"Value: {value:.2f}" for value in data] 
    
    fig = go.Figure(data=go.Bar(
        x=x_data,
        y=y_data,
        # text=hover_texts,  # Assign hover text for each bar
        hoverinfo="text+x",
        marker=dict(
            color=data,  # Assign data values for color mapping
            colorscale='Viridis',  # Use the Viridis color scale
            colorbar=dict(title=y_label)  # Optional: customize the colorbar title
        ),
        width=np.full(len(data), 1.05)  # Make bars touch by setting width > 1
    ))

    # Update layout for axes, labels, and background
    fig.update_layout(
        xaxis=dict(
            title=x_label,
            showticklabels=False,
        ),
        yaxis=dict(
            showticklabels=False,  # Typically, no need for y-axis labels in this visualization
            title=y_label,
        ),
        title=title,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=40, r=40, t=40, b=40),
    )

    # fig.update_layout(width=800, height=300)
    if save_path:
        fig.write_html(save_path)
    else:
        fig.show()


import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Example DataFrame setup with random data
np.random.seed(0)  # For consistent random data
data = np.random.rand(12, 21)  # 12 months, 5 years of data

years = [2010,2011,2012,2013,2014,2015,2016, 2017, 2018, 2019, 2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030]  # Example years
months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

df = pd.DataFrame(data, index=months, columns=years)

def create_month_year_heatmap(df, title='Month-Year Heatmap', colormap='Viridis', save_path=None):
    """
    Create a heatmap with month names on the y-axis and years on the x-axis.
    
    Parameters:
    - df: DataFrame with years as columns, month names as the row index.
    - title: Title of the heatmap.
    """
    hover_texts = [f"Value: {value:.2f}" for value in data] 
    fig = go.Figure(data=go.Heatmap(
        z=df.values,  # Data values
        x=df.columns,  # Year on the x-axis
        y=df.index,  # Month names on the y-axis
        colorscale=colormap,  # Color scale
        colorbar=dict(title='Magnitude'),  # Colorbar configuration
    ))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis=dict(title='Year', type='category'),  # Treat years as categories
        yaxis=dict(title='Month'),  # No need for dtick here since we're using month names
    )
    
    if save_path:
        fig.write_html(save_path)
    else:
        fig.show()

create_month_year_heatmap(df, title='Month-Year Heatmap Test')









if __name__ == "__main__":
    li = np.concatenate([np.random.randint(0, 20, size=800), np.random.randint(20, 30, size=800), np.random.randint(30, 100, size=800)])
    # print(li)
    # custom_visualization_matplotlib(li)
    data = np.random.rand(100)  # Example data

    if Config.plot_backend == 'matplotlib':
        custom_visualization_matplotlib(data)
    elif Config.plot_backend == 'plotly':
        custom_visualization_plotly(li )
    
    # Example usage
    # Assuming 'data' is a pandas DataFrame with a DateTimeIndex
    data = pd.DataFrame({
        'Category 1': np.random.rand(10),
        'Category 2': np.random.rand(10),
        'Category 3': np.random.rand(10),
    }, index=pd.date_range(start='2021-01-01', periods=10, freq='D'))