import random

color_maps = ['gnuplot2', 'terrain', 'flag', 'prism', 'brg', 'gist_stern', 'turbo', 'jet', 'seismic', 'tab20b', 'Pastel2']

def get_color_map():
    # Pick a random color map for fun animations
    return random.choice(color_maps)