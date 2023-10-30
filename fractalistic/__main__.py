#!/usr/bin/env python3


###### Click Extra
from click_extra import extra_command, option
from click_extra import IntRange, Choice
###### Local imports
from .utils import *
from .app import FractalisticApp
from . import __version__
from .colors import color_renderers
from .fractals import fractal_list
###### Others
import gmpy2
###############
  



@extra_command(params=[])
@option("-df", "--default-fractal", help="Default fractal to show when starting the program.", type=Choice([frac.__name__ for frac in fractal_list], False), default="Mandelbrot")
@option("-dc", "--default-color", help="Default color to use when starting the program.", type=Choice([color.__name__ for color in color_renderers], False), default="blue_brown")
@option("-p", "--decimal-precision", help="Fine-tune numeric precision by specifying the desired bit length for numeric values", type=IntRange(5), default=64)
@option("-i", "--max-iter", help="This option defines the number of iterations required to classify a point as convergent", type=IntRange(5), default=128)
@option("-s", "--size", nargs=2, help="Manually set the screenshots width and height. Wont work if you use -f.", type=IntRange(32), default=(1920, 1080))
@option("-f", "--fit", help="Fit screenshots with the canvas.", is_flag=True)
@option("-q", "--quality", help="Only when using --fit, set the quality of screenshots by multiplying the original size in the terminal by the specified scaling factor.", type=IntRange(1), default=20)
@option("-v", "--version", help="Show version number and exit", is_flag=True)
@option("--debug", help="Enable debug mode for developers.", is_flag=True)
def main(fit: bool, quality: float, size: tuple[int, int], default_fractal: str, default_color: str, debug: bool, decimal_precision: int, max_iter: int, version: bool):

    # If -v or --version is used, show version and exit
    if version:
        print(__version__)
        quit()

    # Set gmpy2 decimal precision
    gmpy2.set_context(gmpy2.context(precision=decimal_precision))
    
    app = FractalisticApp()

    # Set default fractal
    app.fractal_index = {frac.__name__: i for i, frac in enumerate(fractal_list)}[default_fractal]
    
    # Set default color
    app.color_renderer_index = {color.__name__: i for i, color in enumerate(color_renderers)}[default_color]

    app.options = {
        "fit_screenshots": fit,
        "screenshot_quality": quality,
        "size": None if size is None else Vec(size[0], size[1]),
        "max_iter": max_iter,
        "debug": debug,
    }

    app.run()

if __name__ == "__main__":
    main()