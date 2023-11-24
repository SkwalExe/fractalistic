import os
from .fractals import fractal_list
from .colors import color_renderers
from .vec import Vec
from .settings import RenderSettings
from multiprocessing import Queue
from .line_divergence_result import LineDivergenceResult
from gmpy2 import mpc
import gmpy2

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


def set_precision(value) -> None:
    gmpy2.get_context().precision = value


def get_divergence_matrix(start: int, stop: int, render_settings: RenderSettings, size: Vec, queue: Queue) -> None:
    set_precision(render_settings.wanted_numeric_precision)
    lines_to_render = stop - start
    pos_on_plane = render_settings.screen_pos_on_plane

    for y in range(lines_to_render):
        result = [0] * size.x
        for x in range(size.x):
            pos = Vec(x, y+start)
            c_num = pos_to_c(pos, render_settings.cell_size, pos_on_plane, size)
            result[x] = fractal_list[render_settings.fractal_index].get(c_num, render_settings)
        queue.put(LineDivergenceResult(y+start, result))

    queue.put(None)
