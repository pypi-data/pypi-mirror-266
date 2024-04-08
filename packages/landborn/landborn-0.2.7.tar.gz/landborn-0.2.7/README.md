# Landborn: Data Visualization Package

Landborn is a comprehensive Python library designed for creating visually appealing, informative data visualizations with ease. It bridges the complexity of matplotlib and Plotly, providing a simple interface to generate complex graphs suitable for a wide array of data analysis applications. This document provides an overview of Landborn's primary functions, usage examples, and guidance on how to effectively utilize the library to enhance your data visualization tasks.

## Core Functions

### Scatter Plot

- `scatterplot(df, xvar, yvar, color, colormap, size, marker, ax, save_path)`: Generates scatter plots using either matplotlib or Plotly based on the global backend setting in `Config.plot_backend`. It supports customization of color, size, and marker type.

### Line Plot

- `lineplot(df, xvar, yvar, color, colormap, size, style, marker, save_path)`: Draws line plots connecting data points in sequence, ideal for visualizing time series or continuous data. Style and marker customization is available.

### Bar Plot

- `barplot(df, xvar, yvar, orientation, color, save_path, axis)`: Creates vertical or horizontal bar plots. The orientation parameter controls the bar direction.

### Joint Plot

- `jointplot(x, y, ax, color, title, save_path)`: Combines scatter and line plots on shared axes to display both individual data points and their sequential connections.

### Swarm Plot

- `swarmplot(df, categorical_data, numerical_data, r, ax, save_path)`: Positions data points to avoid overlap, making it ideal for visualizing distributions across categories.

## Colormap Functions

### Plot Colormap Gradient

- `plot_colormap_gradient(colormap_name, save_path)`: Displays the gradient of a specified colormap, aiding in colormap selection and comparison.

### Plot Colormap in RGB Space

- `plot_colormap_in_rgb_space(colormap_name, num_samples, save_path)`: Visualizes the color space distribution of a colormap by plotting its colors in RGB space.

### Create Custom Colormap

- `create_custom_colormap(num_points, title)`: Generates a custom colormap based on specified RGB functions, allowing for personalized visualizations.

### Delta E and Lightness

- `delta_e(colormap_name, num_points, save_path)`: Calculates the perceptual difference (ΔE) across a colormap, providing insights into its perceptual uniformity.

- `delta_e_lightness(colormap_name, num_points, save_path)`: Focuses on the lightness variation in ΔE calculations, highlighting changes in perceived brightness across a colormap.

### Convert Colormap for Colorblindness

- `convert_colormap_for_colorblindness(colormap, cvd_type, num_points)`: Adapts a colormap to be more accessible for viewers with color vision deficiencies (CVD), ensuring inclusivity in visualizations.

### Compare Colormaps

- `compare_colormaps(cmap1, cmap2, save_path)`: Places two colormaps side by side for direct comparison, aiding in the selection process.

## Heatmap Functions

### Gradient Heatmap

- `gradient_heatmap(data, colormap, title, x_label, save_path)`: Creates a heatmap representing the distribution of a single variable, with color intensity corresponding to value magnitude.

### Month-Year Heatmap

- `month_year_heatmap(df, title, colormap, save_path)`: Visualizes data across months and years, with each cell's color intensity reflecting the data's magnitude. Suitable for tracking trends and patterns over time.

## Plotly vs Matplotlib

All functions default to 'matplotlib'
### The following functions support both backends:
- scatterplot
- lineplot
- barplot
- gradient_heatmap
- month_year_heatmap

### To switch backends:

`set_plot_backend('plotly')`
or
`set_plot_backend('matplotlib')`


## Installation

Install Landborn directly from PyPI using pip:

```
pip install landborn
```

## Testing

To run the tests, inside main dir, run pytest tests/tests.py