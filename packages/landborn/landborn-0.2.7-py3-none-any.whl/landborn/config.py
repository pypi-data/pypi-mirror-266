# In config.py

class Config:
    # Default to 'matplotlib'
    plot_backend = 'matplotlib'

def set_plot_backend(backend_name):
    if backend_name not in ['matplotlib', 'plotly']:
        raise ValueError("Backend not supported. Choose 'matplotlib' or 'plotly'.")
    else:
        Config.plot_backend = backend_name
