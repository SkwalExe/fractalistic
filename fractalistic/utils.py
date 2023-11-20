import os
from typing import Any
from .fractals import *
from .colors import *
from .vec import Vec
from gmpy2 import mpc

SRC_DIR = os.path.dirname(os.path.abspath(__file__))

def get_fractal_index_from_name(name: str):
    return {frac.__name__: i for i, frac in enumerate(fractal_list)}[name]

def get_color_index_from_name(name: str):
    return {color.__name__: i for i, color in enumerate(color_renderers)}[name]

def pos_to_c(pos: Vec, cell_size, screen_pos_on_plane, screen_size) -> mpc:
    """Takes a position (x, y) of the canvas and converts it into the corresponding complex number on the plane"""
    result_real = (pos.x - screen_size.x//2) * cell_size
    result_imag = (pos.y - screen_size.y//2) * -cell_size 
    result = mpc(result_real, result_imag) + screen_pos_on_plane
        
    return result