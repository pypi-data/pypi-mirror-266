from .functions import barplot, lineplot, scatterplot, jointplot, swarmplot
from .colormap import plot_colormap_gradient, plot_colormap_in_rgb_space, create_custom_colormap, delta_e, delta_e_lightness, convert_colormap_for_colorblindness, compare_colormaps
from .heatmap import gradient_heatmap, month_year_heatmap
from .config import Config, set_plot_backend

__version__ = '0.2.5'
__author__ = 'Molly Nelson'

print("Package Landborn 0.2.5 Successfully Imported")