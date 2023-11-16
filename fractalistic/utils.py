import os
from typing import Any
from .fractals import *
from .colors import *

SRC_DIR = os.path.dirname(os.path.abspath(__file__))

class Vec():
    x: Any
    y: Any
    def __init__(self, x: Any, y: Any):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Vec({self.x}, {self.y})"

def get_fractal_index_from_name(name: str):
    return {frac.__name__: i for i, frac in enumerate(fractal_list)}[name]

def get_color_index_from_name(name: str):
    return {color.__name__: i for i, color in enumerate(color_renderers)}[name]