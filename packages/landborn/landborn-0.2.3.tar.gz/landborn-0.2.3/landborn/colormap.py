import numpy as np
import pylab
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
import matplotlib.cm as cm
from skimage.color import rgb2lab
from matplotlib.colors import LinearSegmentedColormap
from colorspacious import cspace_convert
from matplotlib.cm import get_cmap


def plot_colormap_gradient(colormap_name, save_path=None):
    if not isinstance(colormap_name, str):
        title = colormap_name.name
    else:
        title = colormap_name

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    fig, ax = plt.subplots(figsize=(6, 2))
    ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(colormap_name))
    ax.set_axis_off()
    plt.title(f"Gradient of the '{title}' colormap")
    
    if save_path:
        plt.savefig(save_path)
    return ax
    


def plot_colormap_in_rgb_space(colormap_name, num_samples=500, save_path=None):
    if not isinstance(colormap_name, str):
        title = colormap_name.name
    else:
        title = colormap_name

    cmap = plt.get_cmap(colormap_name)
    colors = cmap(np.linspace(0, 1, num_samples))

    #get rgb values
    r = colors[:, 0]
    g = colors[:, 1]
    b = colors[:, 2]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    for i in range(num_samples):
        ax.scatter(r[i], g[i], b[i], color=[r[i], g[i], b[i]], s=10)

    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')
    ax.set_title(f'Colormap "{title}" in RGB Space')
    ax.set_facecolor('white')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    if save_path:
        plt.savefig(save_path)
        
    return ax


def create_custom_colormap(num_points=256, title="CustomColormap"):
    t = np.linspace(0, 1, num_points)

    #parametric functions for R, G, and B
    R = 0.3 * np.sin(2 * np.pi * t) + 0.3
    G = 0.3 * np.cos(2 * np.pi * t + np.pi / 3) + 0.2
    B = 0.2 * np.cos(2 * np.pi * t + 2 * np.pi / 3) + 0.6

    colors = np.stack([R, G, B], axis=1)

    #ensure colors are within valid RGB range (0-1)
    colors = np.clip(colors, 0, 1)

    return LinearSegmentedColormap.from_list(title, colors)



def delta_e(colormap_name, num_points=256, save_path=None):
    if isinstance(colormap_name, str):
        cmap = plt.get_cmap(colormap_name)
        title = colormap_name
    else:
        cmap = colormap_name
        title = colormap_name.name
    colors = cmap(np.linspace(0, 1, num_points))
    colors_rgb = colors[:, :3].reshape((num_points, 1, 3))
    colors_lab = rgb2lab(colors_rgb).reshape(num_points, 3)

    delta_es = []
    for i in range(len(colors_lab)-1):
        calc = abs(colors_lab[i][0] - colors_lab[i+1][0]) ** 2
        calc2 = abs(colors_lab[i][1] - colors_lab[i+1][1]) ** 2
        calc3 = abs(colors_lab[i][2] - colors_lab[i+1][2]) ** 2
        delta_es.append(np.sqrt(calc + calc2 + calc3))

    data_steps = np.linspace(0, 1, num_points)
    step_sizes = np.diff(data_steps)
    normalized_delta_es = delta_es / step_sizes

    #plotting
    # fig, ax = plt.figure(figsize=(10, 6))
    fig, ax = plt.subplots(figsize=(10, 6))
    x_values = (data_steps[:-1] + data_steps[1:]) / 2
    plt.plot(x_values, normalized_delta_es, marker='', linestyle='-')
    plt.plot([0,1], [200,200], marker='', linestyle='dashed', color='grey')
    plt.plot([0,1], [100,100], marker='', linestyle='dashed', color='grey')
    plt.xlabel('Data Value')
    plt.ylabel('ΔE (Perceptual Difference)')
    plt.title(f'ΔE Across "{title}" Colormap')
    plt.grid(True)
    
    if save_path:
        plt.savefig(save_path)
    return ax


def delta_e_lightness(colormap_name, num_points=256, save_path=None):
    if isinstance(colormap_name, str):
        cmap = plt.get_cmap(colormap_name)
        title = colormap_name
    else:
        cmap = colormap_name
        title = colormap_name.name

    colors = cmap(np.linspace(0, 1, num_points))
    colors_rgb = colors[:, :3].reshape((num_points, 1, 3))
    colors_lab = rgb2lab(colors_rgb).reshape(num_points, 3)

    delta_es = []
    for i in range(len(colors_lab)-1):
        calc = abs(colors_lab[i][0] - colors_lab[i+1][0]) ** 2
        delta_es.append(np.sqrt(calc))

    data_steps = np.linspace(0, 1, num_points)
    step_sizes = np.diff(data_steps)
    # print(step_sizes)
    normalized_delta_es = delta_es / step_sizes

    #plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    x_values = (data_steps[:-1] + data_steps[1:]) / 2
    plt.plot(x_values, normalized_delta_es, marker='', linestyle='-')
    plt.plot([0,1], [200,200], marker='', linestyle='dashed', color='grey')
    plt.plot([0,1], [100,100], marker='', linestyle='dashed', color='grey')
    plt.ylim(0,600)
    plt.xlabel('Data Value')
    plt.ylabel('ΔE for Lightness')
    plt.title(f'ΔE Lightness "{title}" Colormap')
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
    return ax


def convert_colormap_for_colorblindness(colormap, cvd_type='deuteranomaly', num_points=256):
    # Get the colormap if provided by name
    if isinstance(colormap, str):
        cmap = plt.get_cmap(colormap)
        title = colormap
    else:
        cmap = colormap
        title = colormap.name
    
    original_colors = cmap(np.linspace(0, 1, num_points))
    original_colors_rgb = original_colors[:, :3]
    
    cvd_space = {"name": "sRGB1+CVD","cvd_type": cvd_type,"severity": 100}
    cvd_colors = cspace_convert(original_colors_rgb, cvd_space, "sRGB1")
    cvd_colors = np.clip(cvd_colors, 0, 1)
    
    new_cmap = LinearSegmentedColormap.from_list(f"{cvd_type}_{title}", cvd_colors, N=num_points)
    return new_cmap



def compare_colormaps(cmap1, cmap2, save_path=None):
    if isinstance(cmap1, str):
        title1 = cmap1
    else:
        title1 = cmap1.name
    if isinstance(cmap2, str):
        title2 = cmap2
    else:
        title2 = cmap2.name

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    fig, axs = plt.subplots(1, 2, figsize=(12, 6), constrained_layout=True)
    
    axs[0].imshow(gradient, aspect='auto', cmap=plt.get_cmap(cmap1))
    axs[0].set_title(title1)
    axs[0].axis('off')
    axs[1].imshow(gradient, aspect='auto', cmap=plt.get_cmap(cmap2))
    axs[1].set_title(title2)
    axs[1].axis('off')
    
    if save_path:
        plt.savefig(save_path)
    return axs



if __name__ == "__main__":
    gradient = plot_colormap_gradient('viridis', save_path="viridis_gradient.png")
    plot_colormap_in_rgb_space('viridis', save_path="viridis_rgb.png")
    compare_colormaps('viridis', 'rainbow')
    
    # #delta e
    delta_e('rainbow', save_path="rainbow_delta_e.png")
    delta_e('viridis')
    lightness = delta_e_lightness('viridis', save_path="viridis_lightness.png")

    # #colorblindness
    deuter_colormap = convert_colormap_for_colorblindness('viridis', cvd_type='deuteranomaly')
    delta_e(deuter_colormap)
    compare_colormaps('viridis', deuter_colormap, save_path="viridis_vs_colorblind.png")
    
    # #custom c map
    custom_cmap = create_custom_colormap(title='Molly')
    plot_colormap_gradient(custom_cmap)
    plot_colormap_in_rgb_space(custom_cmap)
    deuter_colormap = convert_colormap_for_colorblindness(custom_cmap, cvd_type='deuteranomaly')
    ax = compare_colormaps(custom_cmap, deuter_colormap, save_path="comparison.png")
    delta_e(custom_cmap)
    delta_e_lightness(custom_cmap)