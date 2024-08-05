import os
from multiprocessing import Queue

import gmpy2
from gmpy2 import mpc, mpfr  # type: ignore
from rich.rule import Rule
from rich.theme import Theme  # type: ignore

from .colors import color_renderers
from .fractals import fractal_list
from .line_divergence_result import LineDivergenceResult
from .settings import RenderSettings
from .vec import Vec

SRC_DIR = os.path.dirname(os.path.abspath(__file__))

rule = Rule(style="#666666", characters="-")
rich_theme = Theme(
    {
        "acc": "#a277ff",
        "bg_acc": "white on #a277ff",
        "red": "#ff6767",
        "bg_red": "white on #ff6767",
        "green": "#58e0b2",
        "bg_green": "black on #58e0b2"
    }
)


def get_fractal_index_from_name(name: str) -> int | None:
    try:
        return {frac.__name__.lower(): i for i, frac in enumerate(fractal_list)}[name.lower()]
    except KeyError:
        return None


def get_color_index_from_name(name: str) -> int | None:
    try:
        return {color.__name__.lower(): i for i, color in enumerate(color_renderers)}[name.lower()]
    except KeyError:
        return None


def pos_to_c(pos: Vec, cell_size: mpfr, screen_pos_on_plane: mpc, screen_size: Vec[int]) -> mpc:
    """Takes a position (x, y) of the canvas and converts it into the corresponding complex number on the plane"""
    result_real = (pos.x - screen_size.x // 2) * cell_size
    result_imag = (pos.y - screen_size.y // 2) * -cell_size
    result = mpc(result_real, result_imag) + screen_pos_on_plane

    return result


def set_precision(value: int) -> None:
    gmpy2.get_context().precision = value  # type: ignore


def get_divergence_matrix(start: int, stop: int, render_settings: RenderSettings, size: Vec, queue: Queue) -> None:
    set_precision(render_settings.wanted_numeric_precision)
    lines_to_render = stop - start
    pos_on_plane = render_settings.screen_pos_on_plane

    for y in range(lines_to_render):
        result = [0] * size.x
        for x in range(size.x):
            pos = Vec(x, y + start)
            c_num = pos_to_c(pos, render_settings.cell_size, pos_on_plane, size)
            result[x] = fractal_list[render_settings.fractal_index].get(c_num, render_settings)
        queue.put(LineDivergenceResult(y + start, result))

    queue.put(None)
