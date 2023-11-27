from gmpy2 import mpfr, mpc
from .vec import Vec
from .click_modes import ClickMode, CLICK_MODES
from . import __version__


class RenderSettings():
    """A class to store all settings for renders."""

    cell_size: mpfr | None = None
    """The height and width of one pixel in the complex plane"""

    screen_pos_on_plane: mpc = mpc(0, 0)
    """The position of the of the canvas in the plane"""

    fractal_index: int = 0
    """Index of the selected fractal"""

    julia_click: mpc = mpc(1, 0)
    """The complex number corresponding to the Julia set to show when a point is clicked on the canvas,
    the name is a bit misleading, but it will be kept for state files backward compatibility

    -> C in the julia formula:
    Un+1 = Un² - C
    """

    mandelbrot_starting_value: mpc = mpc(0, 0)
    """The starting value of the Mandelbrot set,
    -> U0 in the formula:
    Un+1 = Un² + C
    """

    julia_exponent: float | int | mpc = int(2)
    """-> P in the julia formula:
    Un+1 = (Un)^p - C
    """

    mandelbrot_exponent: float | int | mpc = int(2)
    """-> P in the mandelbrot formula:
    Un+1 = (Un)^p + C
    """

    color_renderer_index: int = 0
    """Index of the current color renderer"""

    wanted_numeric_precision: int = 64
    """The wanted numeric precision"""

    max_iter: int = 128


class Settings():
    render_settings: RenderSettings = RenderSettings()

    canv_size: Vec | None = None
    """The number of rows and cols of the canvas"""

    marker_pos: Vec | None = None
    """Position of the red marker on the screen"""

    move_distance: int = 10
    """How many cells far should we move when an arrow key is pressed"""

    zoom_intensity: int = 20
    """How much should we zoom/unzoom in percentage"""

    left_click_mode_name: str = "zoom_in"
    """The action to take when left clicking on the canvas"""

    right_click_mode_name: str = "zoom_out"
    """The action to take when right clicking on the canvas"""

    @property
    def left_click_mode(self) -> ClickMode:
        return CLICK_MODES[self.left_click_mode_name]

    @property
    def right_click_mode(self) -> ClickMode:
        return CLICK_MODES[self.right_click_mode_name]

    threads: int = 5
    """number of threads used for rendering"""

    screenshot_threads: int = 10
    """number of threads used for taking screenshots"""

    state_file: str | None = None
    """If not none, the path of the file to load the state from"""

    debug: bool = False
    """Enable debug mode for developers."""

    screenshot_size: Vec = Vec(1920, 1080)

    screenshot_quality: int = 20

    fit_screenshots: bool = False


class StateInfo():
    version = __version__
    render_settings: RenderSettings
