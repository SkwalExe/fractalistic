#!/usr/bin/env python3
from click_extra import STRING, Choice, IntRange, extra_command, option

from . import __version__
from .app import FractalisticApp
from .colors import color_renderers
from .fractals import fractal_list
from .settings import Settings
from .utils import get_color_index_from_name, get_fractal_index_from_name
from .vec import Vec


@extra_command(params=[])
@option("-t", "--threads", help="Number of threads to use for rendering", type=IntRange(1), default=Settings.threads)
@option(
    "-st",
    "--screenshot-threads",
    help="Number of threads to use for rendering HQ screenshots",
    type=IntRange(1),
    default=Settings.screenshot_threads,
)
@option("-ls", "--load-state", help="Load state from a file", type=STRING)
@option(
    "-df",
    "--default-fractal",
    help="Default fractal to show when starting the program.",
    type=Choice([frac.__name__ for frac in fractal_list], False),
    default="Mandelbrot",
)
@option(
    "-dc",
    "--default-color",
    help="Default color to use when starting the program.",
    type=Choice([color.__name__ for color in color_renderers], False),
    default="blue_brown",
)
@option(
    "-p",
    "--decimal-precision",
    help="Fine-tune numeric precision by specifying the desired bit length for numeric values",
    type=IntRange(5),
    default=Settings.render_settings.wanted_numeric_precision,
)
@option(
    "-i",
    "--max-iter",
    help="This option defines the number of iterations required to classify a point as convergent",
    type=IntRange(5),
    default=Settings.render_settings.max_iter,
)
@option(
    "-s",
    "--size",
    nargs=2,
    help="Manually set the screenshots width and height. Wont work if you use -f.",
    type=IntRange(32),
    default=(Settings.screenshot_size.x, Settings.screenshot_size.y),
)
@option("-f", "--fit", help="Fit screenshots with the canvas.", is_flag=True)
@option(
    "-q",
    "--quality",
    help=(
        "Only when using --fit, set the quality of screenshots by "
        "multiplying the original size in the terminal by the specified scaling factor."
    ),
    type=IntRange(1),
    default=Settings.screenshot_quality,
)
@option("-v", "--version", help="Show version number and exit", is_flag=True)
@option("--debug", help="Enable debug mode for developers.", is_flag=True)
def main(
    fit: bool,
    quality: int,
    size: tuple[int, int],
    default_fractal: str,
    default_color: str,
    debug: bool,
    decimal_precision: int,
    max_iter: int,
    version: bool,
    load_state: str,
    threads: int,
    screenshot_threads: int,
) -> None:
    # If -v or --version is used, show version and exit
    if version:
        print(__version__)
        quit()

    app = FractalisticApp()

    # Set default fractal
    frac_i = get_fractal_index_from_name(default_fractal)
    if frac_i is not None:
        app.settings.render_settings.fractal_index = frac_i

    # Set default color
    color_i = get_color_index_from_name(default_color)
    if color_i is not None:
        app.settings.render_settings.color_renderer_index = color_i

    app.settings.fit_screenshots = fit
    app.settings.debug = debug
    app.settings.screenshot_quality = quality
    app.settings.screenshot_size = Vec(size[0], size[1])
    app.settings.render_settings.max_iter = max_iter
    app.settings.render_settings.wanted_numeric_precision = decimal_precision
    app.settings.state_file = load_state
    app.settings.threads = threads
    app.settings.screenshot_threads = screenshot_threads

    app.run()
