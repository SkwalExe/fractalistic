# ---------- Textual imports
from textual.app import App
from textual.widgets import Footer, ProgressBar, RichLog, Static, Input
from textual.binding import Binding
from textual.events import Click
from textual.color import Color
from textual import on
from textual import log
# ---------- Local imports
from . import fractals, colors, __version__
from .utils import (
    SRC_DIR, get_divergence_matrix, set_precision, pos_to_c,
    get_fractal_index_from_name, get_color_index_from_name)
from .fractals.fractal_base import FractalBase
from .vec import Vec
from .click_modes import CLICK_MODES
from .settings import Settings, RenderSettings, StateInfo
from .command import Command, CommandIncrement, CommandIncrementArgParseResult
from .fractal_canv import FractalCanv
from .line_divergence_result import LineDivergenceResult
# ---------- Other imports
import os
from PIL import Image
from typing import Callable
import asyncio
from multiprocessing import Pool, Manager
from rich.rule import Rule
from time import monotonic, time, sleep
from gmpy2 import mpc, mpfr
from copy import deepcopy
import gmpy2
import pickle
from math import ceil
from typing import Generator
# --------------------


class FractalisticApp(App):
    settings: Settings = Settings()

    renders: int = 0
    """The number of times a fractal has been rendered"""

    last_render_time: float = 0
    """How long did it take to render the last frame"""

    ready: bool = False
    """Whether we should listen to events or not"""

    logs: list = []
    """List of log messages"""

    print_log_bar: bool = False
    """If we should print a log bar before showing the message in the log panel"""

    average_divergence: float = 0
    """Average divergence of the current canvas render"""

    cancel_screenshot: bool = False
    """True when the current screenshot operation must be cancelled as soon as possible"""

    current_zoom_level: str = "1"
    """[NOT REACTIVE], current zoom level, updated at each render and
    used to show the zoom level in the cavas border subtitle"""

    command_list: dict[str, Command | CommandIncrement]

    current_process_pool = None

    # ---------- DOM ELEMENTS
    container: Static = Static(id="container")
    """Container for the canvas and the right container"""

    right_container: Static = Static(id="right_container")
    """Container for the log panel and the command input"""

    progress_bar: ProgressBar = ProgressBar(classes="hidden")
    """Progress bar used when taking screenshots"""

    canv: FractalCanv = FractalCanv(0, 0)
    """The canvas widget"""

    rich_log: RichLog = RichLog(markup=True, auto_scroll=True, wrap=True, min_width=5)
    """The log panel widget"""

    command_input: Input = Input(placeholder="help")
    """Command input"""

    first_resize: bool = False
    """If the first resize event was already fired"""

    # ---------- COMMANDS

    # ========== increment type commands

    def command_max_iter(self, value: int) -> None:
        self.render_settings.max_iter = value

        self.log_success(f"max_iter set to [blue]{self.render_settings.max_iter}")
        self.update_canv()

    def command_move_dist(self, value: int) -> None:
        self.settings.move_distance = value
        self.log_success(f"Move distance set to [blue]{self.settings.move_distance}")

    def command_precision(self, value: int) -> None:
        self.precision = value

        self.log_success(f"Numeric precision set to [blue]{value}")
        self.update_canv()

    def command_screenshot_threads(self, value: int) -> None:
        self.settings.screenshot_threads = value
        self.log_success(f"Screenshot thread count set to [blue]{self.settings.screenshot_threads}")

    def command_threads(self, value: int) -> None:
        self.settings.threads = value
        self.log_success(f"Rendering thread count set to [blue]{self.settings.threads}")

    def command_zoom_lvl(self, value: int) -> None:
        self.settings.zoom_intensity = value
        self.log_success(f"Zoom level set to [blue]{self.settings.zoom_intensity}%")

    # ========== other commands
    def command_capture(self, args, argc: int) -> None:
        if argc == 0:
            self.action_screenshot()
        elif argc == 2:
            try:
                width = int(args[0])
                height = int(args[1])
            except ValueError:
                self.log_error("Width and height must be integers")
                return

            if width <= 0 or height <= 0:
                self.log_error("Width and height must be positive")
                return

            self.action_screenshot(Vec(width, height))

    def command_capture_fit(self, args, argc: int) -> None:
        if argc == 0:
            self.action_screenshot(self.get_screenshot_size_fit())
        elif argc == 1:
            try:
                quality = int(args[0])
            except ValueError:
                self.log_error("Quality must be an integer")
                return

            if quality <= 0:
                self.log_error("Quality must be positive")
                return

            self.action_screenshot(self.get_screenshot_size_fit(quality))

    def command_clear(self, args, argc: int) -> None:
        self.rich_log.clear()
        self.print_log_bar = False

    def command_click_mode(self, args: list[str], argc: int) -> None:
        # If no args are provided, print the current modes
        # and the available modes.
        if argc == 0:
            self.log_write([
                "[purple]Available modes:[/purple]"
                + ''.join([f'\n- [blue]{mode}[/blue]: {CLICK_MODES[mode].description}' for mode in CLICK_MODES]),
                f"\nCurrent left click mode: [blue]{self.settings.left_click_mode_name}[/blue]",
                f"Current right click mode: [blue]{self.settings.right_click_mode_name}[/blue]",
            ])
            return

        # If two args were provided
        if args[0] not in ["left", "right"]:
            self.log_error("[red]First argument must be 'left' or 'right'")
            return

        if args[1] not in CLICK_MODES:
            self.log_error(f"[red]Second argument must be one of: {', '.join([mode for mode in CLICK_MODES])}")
            return

        if args[0] == "left":
            self.settings.left_click_mode_name = args[1]
        else:
            self.settings.right_click_mode_name = args[1]

        self.log_success(f"{args[0].capitalize()} click mode set to [blue]{args[1]}")

    def command_color(self, args, argc: int) -> None:
        if argc == 0:
            self.log_write([
                f"Current color: [blue]{self.selected_color.__name__}[/blue]",
                "Available colors: "
                f"{', '.join([f'[violet]{color.__name__}[/violet]' for color in colors.color_renderers])}"
            ])
            return

        color_name = args[0]
        color_index = get_color_index_from_name(color_name)

        if color_index is None:
            self.log_error(f"Cannot find color [white on red]{color_name}")
            return

        self.render_settings.color_renderer_index = color_index
        self.log_success(f"Current color set to [blue]{self.selected_color.__name__}")
        self.update_canv()

    def command_exp_type(self, args, argc: int) -> None:
        if argc == 0:
            self.log_write([
                f"Julia exponent type: [blue]{type(self.render_settings.julia_exponent).__name__}[/blue]",
                f"Mandelbrot exponent type: [blue]{type(self.render_settings.mandelbrot_exponent).__name__}",
                f"Burning ship exponent type: [blue]{type(self.render_settings.burning_ship_exponent).__name__}"
            ])
            return

        fract = args[0]
        wanted_type = args[1]

        if fract not in ["julia", "mandel", "burning_ship"]:
            self.log_error("[red]First argument must be 'julia', 'mandel' or 'burning_ship'")
            return

        if wanted_type not in ["int", "float", "mpc"]:
            self.log_error("[red]Second argument must be 'int', 'float' or 'mpc'")
            return

        new_value = eval(args[1])(int(2))

        match fract:
            case "julia":
                self.render_settings.julia_exponent = new_value
            case "mandel":
                self.render_settings.mandelbrot_exponent = new_value
            case "burning_ship":
                self.render_settings.burning_ship_exponent = new_value

        self.log_info(
            f"{fract.capitalize()} exponent type set to [purple]{args[1]}[/purple] and reset to 2.")

        self.update_canv()

    def command_fractal(self, args, argc: int) -> None:
        if argc == 0:
            self.log_write([
                f"Current fractal: [blue]{self.selected_fractal.__name__}[/blue]",
                "Available fractals: "
                f"{', '.join([f'[violet]{fractal.__name__}[/violet]' for fractal in fractals.fractal_list])}"
            ])
            return

        fractal_name = args[0]

        fractal_index = get_fractal_index_from_name(fractal_name)

        if fractal_index is None:
            self.log_error(f"Cannot find fractal [white on red]{fractal_name}")
            return

        self.render_settings.fractal_index = fractal_index
        self.log_success(f"Current fractal set to [blue]{self.selected_fractal.__name__}")
        self.update_canv()

    def command_help(self, args, argc: int) -> None:
        if argc == 1:
            if args[0] == "+":
                command_desc = [
                    f"- [blue]{name}[/blue]: {self.command_list[name].help}"
                    for name in self.command_list
                ]

                self.log_write([
                    "[on blue]Available commands",
                    *command_desc,
                    "[green]Use 'help command_name' to get more info about a command"
                ])
                return

            command = self.get_command(args[0])
            if command is None:
                return

            self.log_write([
                f"[on blue]{args[0]} command",
                command.help,
                command.extra_help
            ])
            return

        # If no args were passed
        self.log_write([
            "[on blue]Available commands",
            ", ".join([f"[blue]{name}[/blue]" for name in self.command_list]),
            "[green]Use [bold]'help +'[/bold] to get a list of all commands and a basic description. "
            "[green]Use [bold]'help command_name'[/bold] to get more info about a command"
        ])

    def command_load_state(self, args, argc: int) -> None:
        self.load_state(args[0])
        self.update_canv()

    def command_pos(self, args, argc: int) -> None:
        # If no args are provided, just show the current position
        if argc == 0:
            self.log_info(f"Current position: [blue]{self.render_settings.screen_pos_on_plane}")
            return

        # If args are provided, go to the given x and y position
        real = None
        imag = None
        try:
            real = mpfr(args[0])
            imag = mpfr(args[1])
        except ValueError:
            self.log_error("Real and imaginary parts must be valid integers or floats")
            return

        self.render_settings.screen_pos_on_plane = mpc(real, imag)

        # Update canvas since we just moved
        self.update_canv()

    def command_quit(self, args, argc: int) -> None:
        self.log_info("Quitting...")
        self.exit()

    def command_save_state(self, args, argc: int) -> None:
        if argc == 0:
            filename = f"{self.selected_fractal.__name__}_state_{int(time())}.fc"
        else:
            filename = args[0]

        try:
            with open(filename, "wb") as f:
                state_info = StateInfo()
                state_info.render_settings = self.render_settings
                pickle.dump(state_info, f)
        except OSError as e:
            self.log_error(f"Cannot write to file '{filename}'. [red]Errno {e.errno}: {e.strerror}.")
            return

        self.log_success(f"State saved to [blue]{filename}")

    def command_set_exp(self, args, argc: int) -> None:
        if argc == 0:
            self.log_write([
                f"Julia exponent: [blue]{type(self.render_settings.julia_exponent).__name__}"
                f"({self.render_settings.julia_exponent})",
                f"Mandelbrot exponent: [blue]{type(self.render_settings.mandelbrot_exponent).__name__}"
                f"({self.render_settings.mandelbrot_exponent})",
                f"Burning ship exponent: [blue]{type(self.render_settings.burning_ship_exponent).__name__}"
                f"({self.render_settings.burning_ship_exponent})"
            ])
            return

        fract = args[0]
        real = args[1]
        imag = None if argc == 2 else args[2]

        if fract not in ["julia", "mandel", "burning_ship"]:
            self.log_error("[red]First argument must be 'julia', 'mandel' or 'burning_ship")
            return

        match fract:
            case "julia":
                exp_type = type(self.render_settings.julia_exponent)
            case "mandel":
                exp_type = type(self.render_settings.mandelbrot_exponent)
            case "burning_ship":
                exp_type = type(self.render_settings.burning_ship_exponent)

        try:
            real_parsed = mpfr(real)
        except ValueError:
            self.log_error(f"Real part must be a valid {exp_type.__name__}")
            return

        # If an imag part was provided
        if exp_type is mpc:
            if imag is None:
                self.log_write(
                    "Imaginary part is required because the exponent type is mpc. "
                    "If you don't want to use complex numbers, "
                    "change the exponent type to int or float with the [blue]exp_type[/blue] command.")
                return
            imag_parsed = mpfr(imag)
            match fract:
                case "julia":
                    self.render_settings.julia_exponent = mpc(real_parsed, imag_parsed)
                case "mandel":
                    self.render_settings.mandelbrot_exponent = mpc(real_parsed, imag_parsed)
                case "burning_ship":
                    self.render_settings.burning_ship_exponent = mpc(real_parsed, imag_parsed)
        else:
            if imag is not None:
                self.log_warning("Imaginary part ignored because the exponent type is not mpc")
            match fract:
                case "julia":
                    self.render_settings.julia_exponent = exp_type(real_parsed)
                case "mandel":
                    self.render_settings.mandelbrot_exponent = exp_type(real_parsed)
                case "burning_ship":
                    self.render_settings.burning_ship_exponent = exp_type(real_parsed)
        self.update_canv()

    def command_version(self, args, argc: int) -> None:
        self.log_info(f"Fractalistic version: [on blue]{__version__}")

    # We cant directly set command_list because we couldn't reference command methods correctly
    # Please order the commands alphabetically
    def set_command_list(self) -> None:
        self.command_list = {
            "capture": Command(
                funct=self.command_capture,
                help="Take a high quality screenshot",
                accepted_arg_counts=[0, 2],
                extra_help=(
                    "[green]Usage : \\[width] \\[height]\nUsage : no args[/green]\n"
                    "If no width and height are specified, the command line settings are used.")),
            "capture_fit": Command(
                funct=self.command_capture_fit,
                help="Take a high quality screenshot that fits the size of the canvas.",
                accepted_arg_counts=[0, 1],
                extra_help=(
                    "[green]Usage : \\[quality]\nUsage : no arg.[/green]\n"
                    "If no quality is specified, the command line settings are used.")),
            "clear": Command(
                funct=self.command_clear,
                help="Clear the log panel",
                accepted_arg_counts=[0]),
            "click_mode": Command(
                funct=self.command_click_mode,
                help="Set the action to take when left or right clicking on the canvas.",
                accepted_arg_counts=[0, 2],
                extra_help=(
                    "[green]Usage : \\[left/right] \\[mode]\nUsage : no args[/green]\n"
                    "If no argument is given, print out the current click modes and the available modes. "
                    "Else, set the left/right click action to \\[mode].")),
            "color": Command(
                funct=self.command_color,
                help="List all the available color schemes or select the specified one.",
                accepted_arg_counts=[0, 1],
                extra_help=(
                    "[green]Usage : \\[color]\nUsage : no args[/green]\n"
                    "If no argument is given, print out the current color and all the available colors. "
                    "Else, select the specified color.")),
            "exp_type": Command(
                funct=self.command_exp_type,
                help="Set the data type used for Julia and Mandelbrot exponents.",
                accepted_arg_counts=[0, 2],
                extra_help=(
                    "[green]Usage : \\[mandel/julia/burning_ship] \\[int/float/mpc]\nUsage : no args[/green]\n"
                    "If no argument is given, print out the current types. "
                    "Else, set the mandel/julia exponent type to \\[type].\n"
                    "- It is important to use the simplest type possible because it has a huge impact on performance.\n"
                    "- \\[mpc] is the complex type from the gmpy2 library.\n"
                    "- If you change the type, the exponent value will be reset to 2.\n"
                    "- [red]Be aware that using float or mpc types will make renders much slower.")),
            "fractal": Command(
                funct=self.command_fractal,
                help="List all the available fractals or select the specified one.",
                accepted_arg_counts=[0, 1],
                extra_help=(
                    "[green]Usage : \\[fract name]\nUsage : no args[/green]\n"
                    "If no argument is given, print out the available fractals. "
                    "Else, select the specified one. The fractal name is case insensitive.")),
            "help": Command(
                funct=self.command_help,
                help="Show the help message",
                accepted_arg_counts=[0, 1]),
            "load_state": Command(
                funct=self.command_load_state,
                help="Load a state from a file.",
                accepted_arg_counts=[1],
                extra_help="[green]Usage : \\[filename][/green]"),
            "max_iter": CommandIncrement(
                funct=self.command_max_iter,
                help="Change the maximum number of iterations used to determine if a point converges or not.",
                app_attribute="settings.render_settings.max_iter",
                min_value=6,),
            "move_dist": CommandIncrement(
                funct=self.command_move_dist,
                help="Change the distance to move when a key is pressed, in canvas cells.",
                app_attribute="settings.move_distance",
                min_value=1),
            "pos": Command(
                funct=self.command_pos,
                help="Set the position to a specific point in the complex plane.",
                accepted_arg_counts=[0, 2],
                extra_help=(
                    "[green]Usage : \\[real] \\[imag]\nUsage : no args[/green]\n"
                    "If no arguments are given, just print out the current position. "
                    "Else, go to the given position. \\[real] and \\[imag] must be valid integers or floats.")),
            "precision": CommandIncrement(
                funct=self.command_precision,
                help="Fine-tune numeric precision by specifying the desired bit length for numeric values",
                app_attribute="precision",
                min_value=5),
            "quit": Command(
                funct=self.command_quit,
                help="Exit the app",
                accepted_arg_counts=[0]),
            "screenshot_threads": CommandIncrement(
                funct=self.command_screenshot_threads,
                help="Change the number of threads used for rendering screenshots",
                app_attribute="settings.screenshot_threads",
                min_value=1),
            "save_state": Command(
                funct=self.command_save_state,
                help="Save the current state of the app to a file (current fractal, color, position, zoom, etc).",
                accepted_arg_counts=[0, 1],
                extra_help=(
                    "[green]Usage : \\[filename]\nUsage : no args[/green]\n"
                    "If no filename is specified, one will be generated automatically.")),
            "set_exp": Command(
                funct=self.command_set_exp,
                help="Set the julia/mandel exponent value.",
                accepted_arg_counts=[0, 2, 3],
                extra_help=(
                    "[green]Usage : \\[frac_name] \\[real] \\[?imag]\nUsage : no args[/green]\n"
                    "If no argument is given, print out the current exponent values. "
                    "Else, set the exponent value to \\[real] + \\[imag]j.\n"
                    "Providing the imaginary part is only required if the exponent type is \\[mpc].")),
            "threads": CommandIncrement(
                funct=self.command_threads,
                help="Change the number of threads used for rendering",
                app_attribute="settings.threads",
                min_value=1),
            "version": Command(
                funct=self.command_version,
                help="Show the version number",
                accepted_arg_counts=[0]),
            "zoom_lvl": CommandIncrement(
                funct=self.command_zoom_lvl,
                help="Change the zoom factor (intensity) when s or d is pressed, in percent.",
                app_attribute="settings.zoom_intensity",
                min_value=1,
                max_value=100),
        }

    # ---------- ACTIONS
    def action_cancel_screenshot(self) -> None:
        self.cancel_screenshot = True
        self.log_info("Screenshot cancelled")

    def action_go(self, x, y) -> None:
        if not self.ready:
            return

        # Remove the marker when moving
        self.remove_marker()
        self.render_settings.screen_pos_on_plane += mpc(
            self.settings.move_distance * self.render_settings.cell_size * x,
            self.settings.move_distance * self.render_settings.cell_size * y)

        self.update_canv()

    def action_zoom(self, direction: str) -> None:
        if not self.ready:
            return

        # Remove the marker when zooming
        self.remove_marker()

        if direction not in ["in", "out"]:
            raise ValueError("zoom direction must be 'in' or 'out'")

        # 101 to avoid doind 1-1 and making a 0 zoom factor which would cause a div0 error
        zoom_factor = 1 - self.settings.zoom_intensity / 101
        self.render_settings.cell_size *= zoom_factor if direction == "in" else 1/zoom_factor

        self.update_canv()

    def action_next_color(self) -> None:
        if not self.ready:
            return

        self.render_settings.color_renderer_index = (
            (self.render_settings.color_renderer_index + 1) % len(colors.color_renderers))

        self.update_canv()
        self.log_info(f"Now using the [purple]{self.selected_color.__name__}[/purple] color scheme")

    def action_next_fractal(self) -> None:
        if not self.ready:
            return

        # Remove the marker when changing fractal
        self.remove_marker()

        self.render_settings.fractal_index = (self.render_settings.fractal_index + 1) % len(fractals.fractal_list)
        self.update_canv()

        self.log_info(f"Now viewing the [purple]{self.selected_fractal.__name__}[/purple] fractal.")
        if self.selected_fractal.message is not None:
            self.log_info(self.selected_fractal.message)

    def action_screenshot(self, screenshot_size: Vec | None = None) -> None:
        if not self.ready:
            return

        # I dont know why this is working
        # Execute action_screenshot_2 in a non-blocking way
        asyncio.get_event_loop().run_in_executor(None, self.action_screenshot_2, (screenshot_size))

    def action_screenshot_2(self, screenshot_size: Vec | None) -> None:
        self.ready = False

        # Dynamically bind the escape key to the cancel_screenshot action
        self.app.bind("escape", "cancel_screenshot", description="Cancel Screenshot")

        if screenshot_size is None:
            screenshot_size = self.get_screenshot_size_from_options()

        screenshot_width = screenshot_size.x
        screenshot_height = screenshot_size.y

        self.container.add_class("hidden")
        self.progress_bar.remove_class("hidden")

        self.progress_bar.update(total=screenshot_height//10, progress=0)

        image = Image.new("RGB", (screenshot_width, screenshot_height), (0, 0, 0))

        # The size in the complex plane, of a pixel of the screenshot
        pixel_size = self.settings.canv_size.x * self.render_settings.cell_size / screenshot_width
        result = self.get_divergence_matrix(
            cell_size=pixel_size,
            size=screenshot_size,
            update_loading_bar=True,
            threads=self.settings.screenshot_threads)

        for line in result:
            # None is returned if the screenshot was cancelled
            if line is None:
                break

            for (x, divergence) in enumerate(line.values):
                # Get a color from the result
                if divergence == -1:
                    color = Color.parse("black")
                else:
                    color = self.selected_color(divergence)

                image.putpixel((x, line.y), color.rgb)

        # If the screenshot wasn't cancelled, save the screenshot to a file,
        # put a message in the log panel and wait one second to
        # allow the user to see that the operation is finished successfully.
        if not self.cancel_screenshot:
            save_to = f"{self.selected_fractal.__name__}_screenshot_{int(time())}.png"
            image.save(save_to)
            self.call_after_refresh(
                self.log_success,
                f"Screenshot [{screenshot_width}x{screenshot_height}] saved to [on violet]{save_to}")

            # Wait one second to allow the user to see that the operation is finished successfully
            sleep(1)

        self.progress_bar.add_class("hidden")
        self.container.remove_class("hidden")

        self.ready = True

        # Unbind the escape key by attrbuting a non-existing action
        self.app.bind("escape", "pass", show=False)

        # Re-focus the canvas will also update the footer, it means it will hide the previous
        # cancel screenshot binding, which is not removed when "unbinding"
        self.set_focus(self.canv)

        # Send the on_resize event, because the terminal could have been resized during the screenshot.
        # Resize events aren't parsed during non-ready states
        self.call_after_refresh(self.on_resize)

        # Set cancel_screenshot back to false so that the next screenshot isn't unwantedly cancelled
        self.cancel_screenshot = False

    def action_quit_(self) -> None:
        """We don't use the builtin quit action because it doesn't work during screenshots"""

        # Cancel any ongoing screenshots before leaving
        self.action_cancel_screenshot()

        self.exit()

    def action_reset(self) -> None:
        """Reset position and zoom"""

        if not self.ready:
            return

        self.reset_position()
        self.update_canv()

    @on(Input.Submitted, "Input")
    def command_input_on_submitted(self, event: Input.Submitted) -> None:
        # Get the command from the input and clear it
        command = event.value.strip()
        self.command_input.value = ""

        # Ignore empty commands
        if len(command) == 0:
            return

        self.parse_command(command)

    # ---------- TEXTUAL APP VARS

    BINDINGS = [
        Binding("ctrl+c", "quit_", "Quit", priority=True)
    ]

    CSS_PATH = os.path.join(SRC_DIR, "app.tcss")

    # ---------- UTILS

    def log_error(self, message: str, subject: str | None = None) -> None:
        self.log_write([
            f"[on red] Error{f': {subject}' if subject is not None else ''} ",
            f"[red]{message}"])

    def log_info(self, message: str, subject: str | None = None) -> None:
        self.log_write([
            f"[on blue] Info{f': {subject}' if subject is not None else ''} ",
            f"[blue]{message}"])

    def log_success(self, message: str, subject: str | None = None) -> None:
        self.log_write([
            f"[black on green] Success{f': {subject}' if subject is not None else ''} ",
            f"[green]{message}"])

    def log_warning(self, message: str, subject: str | None = None) -> None:
        self.log_write([
            f"[black on yellow] Warning{f': {subject}' if subject is not None else ''} ",
            f"[yellow]{message}"])

    def set_marker(self, pos):
        if self.settings.marker_pos is not None:
            c_num = self.pos_to_c(self.settings.marker_pos)
            divergence = self.get_divergence(c_num)
            color = Color.parse("black") if divergence == -1 else self.selected_color(divergence)
            self.canv.set_pixel(self.settings.marker_pos.x, self.settings.marker_pos.y, color)

        self.settings.marker_pos = pos
        self.canv.set_pixel(pos.x, pos.y, Color.parse("red"))

    def get_divergence_matrix(
            self, cell_size: mpc | None = None,
            size: Vec | None = None,
            threads: int | None = None,
            update_loading_bar: bool = False) -> Generator[LineDivergenceResult, None, None]:

        if threads is None:
            threads = self.settings.threads
        if cell_size is None:
            cell_size = self.render_settings.cell_size
        if size is None:
            size = self.settings.canv_size

        # Number of lines to render per thread
        chunk_size = ceil(size.y / threads)
        # List of tuples (start, end) of the lines to render for each thread
        # start is inclusive, end is exclusive
        chunks = [[x * chunk_size, min((x+1) * chunk_size, size.y)] for x in range(0, threads)]

        render_settings = deepcopy(self.render_settings)
        render_settings.cell_size = cell_size

        manager = Manager()
        queue = manager.Queue()

        self.current_process_pool = Pool(processes=threads)

        # Start the rendering processes
        self.current_process_pool.starmap_async(
            get_divergence_matrix,
            [(chunk[0], chunk[1], render_settings, size, queue) for chunk in chunks],
            chunksize=1)

        rendered_lines = 0
        finished_process_count = 0
        while not finished_process_count == threads:

            # Return None if the screenshot was cancelled, and terminate the processes
            if self.cancel_screenshot:
                self.current_process_pool.terminate()
                return None

            rendered_lines += 1

            # A message is added to the queue everytime a line is rendered
            line = queue.get()

            # None is added to the queue when a process is finished
            if line is None:
                finished_process_count += 1
                continue

            yield line

            # Make the progress bar advance every 10 lines
            if rendered_lines % 10 == 0 and update_loading_bar:
                self.progress_bar.advance()

        # Close the pool of processes
        self.current_process_pool.close()
        self.current_process_pool = None

    def load_state(self, filename: str) -> None:
        try:
            with open(filename, "rb") as f:
                try:
                    state_file: StateInfo = pickle.load(f)
                    self.settings.render_settings = state_file.render_settings
                except Exception as e:
                    self.log_error(
                        f"Cannot decode file '{filename}'. "
                        "After version 2.0.0, the state file format changed.[/red]"
                        f"\nError: {e}")
                    return

        except OSError as e:
            self.log_error(f"Cannot read file '{filename}'. [red]Errno {e.errno}: {e.strerror}.")
            return

        self.log_success(f"State loaded from [blue]{filename}[/blue]")

    def reset_position(self) -> None:
        # remove the marker
        self.remove_marker()

        self.render_settings.cell_size = 4 / self.settings.canv_size.x
        self.render_settings.screen_pos_on_plane = mpc(0, 0)

    @property
    def precision(self) -> int:
        return gmpy2.get_context().precision

    @property
    def render_settings(self) -> RenderSettings:
        return self.settings.render_settings

    @precision.setter
    def precision(self, value):
        set_precision(value)
        self.render_settings.wanted_numeric_precision = value

    def get_command(self, name: str) -> Command | CommandIncrement | None:
        if name not in self.command_list:
            self.log_error(f"[red]Cannot find command: [white on red]{name}")
            return None

        return self.command_list[name]

    def get_screenshot_size_fit(self, quality: int | None = None) -> Vec:
        """
        Return the size of the screenshot so that it fits the terminal
        """

        if quality is None:
            quality = self.settings.screenshot_quality

        screenshot_width = self.settings.canv_size.x * quality
        screenshot_height = self.settings.canv_size.y * quality

        return Vec(screenshot_width, screenshot_height)

    def get_screenshot_size_from_options(self, fit_quality: int | None = None) -> Vec:
        if self.settings.fit_screenshots:
            return self.get_screenshot_size_fit(fit_quality)

        return Vec(self.settings.screenshot_size.x, self.settings.screenshot_size.y)

    def remove_marker(self) -> None:
        self.settings.marker_pos = None

    def parse_command(self, text: str) -> None:
        """All executed commands are sent directly here."""

        # Extract non-empty arguments, including the command name
        args = list(filter(lambda x: len(x) > 0, text.split(" ")))

        command_name = args.pop(0)

        # Returns none if the command is not found
        # Else, returns Command() or CommandIncrement()
        command = self.get_command(command_name)

        # Error message in case the command is not found
        # is handled by get_command
        if command is None:
            return

        # Check if the number of arguments is accepted by the command
        if not len(args) in command.accepted_arg_count:
            self.log_error(
                f"Command [white on red]{command_name}[/white on red] expects "
                f"{', or '.join([str(x) for x in command.accepted_arg_count])} arguments, but got {len(args)}")

            return

        # CommandIncrement() is a special case
        # Else we just call the command with the arguments.
        if isinstance(command, CommandIncrement):

            # app_attribute example : "settings.render_settings.max_iter"
            # means that the command will increment (self).settings.render_settings.max_iter
            ############################################################
            # "attributes": ["settings", "render_settings", "max_iter"]
            # we recursively go through the path to get the wanted attribute's value
            attributes = command.app_attribute.split(".")
            current_attribute_value = self
            for attribute in attributes:
                current_attribute_value = current_attribute_value.__getattribute__(attribute)

            # If no args are provided, just print the current value here
            if len(args) == 0:
                self.log_info(f"The value is currently set to [blue]{current_attribute_value}")
                return

            # We pass the args and the current attribute value to CommandIncrement().parse_args()
            value: CommandIncrementArgParseResult = command.parse_args(current_attribute_value, args)
            if value.success:
                # If the new value was successfully parsed, we call the command's funct
                # which role is to set the new value, notice the user,
                # and update the canvas according to the new value, if needed.
                command.funct(value.new_value)
            else:
                # If the new value was not successfully parsed, we log the error message
                self.log_error(value.error_message)
                return
        else:
            command.funct(args, len(args))

    @property
    def selected_fractal(self) -> FractalBase:
        return fractals.fractal_list[self.render_settings.fractal_index]

    @property
    def selected_color(self) -> Callable:
        return colors.color_renderers[self.render_settings.color_renderer_index]

    def rewrite_logs(self) -> None:
        """Rewrite the logs so that they fit the new log panel size when the terminal is resized"""
        self.print_log_bar = False
        self.rich_log.clear()
        for line in self.logs:
            self._log_write(line)

    def log_write(self, content: str | list[str]) -> None:
        self._log_write(content)
        self.logs.append(content)

    def _log_write(self, content) -> None:
        if not isinstance(content, list):
            content = [content]

        if self.print_log_bar:
            self.rich_log.write(Rule(), expand=True)
        else:
            self.print_log_bar = True

        for line in content:
            if line is None:
                continue
            self.rich_log.write(line, shrink=True)

    def get_divergence(self, point: mpc) -> int:
        """Get the divergence of a point using the current parameters"""
        return self.selected_fractal.get(point, self.render_settings)

    def pos_to_c(
            self, pos: Vec, cell_size=None,
            screen_pos_on_plane=None, screen_size: Vec | None = None) -> mpc:
        """Takes a position (x, y) of the canvas and converts it
        into the corresponding complex number on the plane"""

        if cell_size is None:
            cell_size = self.render_settings.cell_size

        if screen_pos_on_plane is None:
            screen_pos_on_plane = self.render_settings.screen_pos_on_plane

        if screen_size is None:
            screen_size = self.settings.canv_size

        return pos_to_c(pos, cell_size, screen_pos_on_plane, screen_size)

    def zoom_at_pos(self, pos: Vec, direction: str) -> None:
        original_c_num = self.pos_to_c(pos)
        self.action_zoom(direction)
        new_c_num = self.pos_to_c(pos)

        self.render_settings.screen_pos_on_plane += original_c_num - new_c_num

    def set_canv_size(self) -> None:
        """
        update self.canv_size
        """

        # Widget height and width of the previous canvas (automatically ajusted)
        height = self.canv.size.height
        width = self.canv.size.width

        # double the height because one char is two pixels in height
        self.settings.canv_size = Vec(width, height * 2)

    async def update_canvas_size(self) -> None:
        """
        Remove the previous canvas and create a new one corresponding to self.canv_size
        """

        focused = isinstance(self.focused, FractalCanv)

        # Remove the previous canvas widget
        await self.canv.remove()

        # And create a new one
        self.canv = FractalCanv(int(self.settings.canv_size.x), int(self.settings.canv_size.y))

        await self.container.mount(self.canv, before=self.right_container)

        if focused:
            self.canv.focus()

        self.update_canv()

    def update_canv(self) -> None:
        if not self.ready:
            return

        self.ready = False
        asyncio.get_event_loop().run_in_executor(None, self.update_canv_)

    def update_canv_(self) -> None:
        self.renders += 1
        start = monotonic()

        # Used to get the average divergence of the current render
        divergence_sum = 0
        term_count = 0

        with self.batch_update():
            for line in self.get_divergence_matrix():
                # If none is returned, most likely the program is exiting
                if line is None:
                    return

                for (x, divergence) in enumerate(line.values):

                    # If there is a marker and the current x and y corresponds the its position
                    # make the pixel red and go to the next pixel
                    if self.settings.marker_pos is not None \
                            and x == self.settings.marker_pos.x \
                            and line.y == self.settings.marker_pos.y:
                        self.canv.set_pixel(x, line.y, Color.parse("red"))
                        continue

                    if divergence != -1:
                        divergence_sum += divergence
                        term_count += 1

                    # Get a color from the result
                    color = Color.parse("black") if divergence == -1 else self.selected_color(divergence)
                    self.canv.set_pixel(x, line.y, color)

        self.average_divergence = divergence_sum / term_count if term_count > 0 else 0
        self.current_zoom_level = f"{4 / (self.render_settings.cell_size * self.settings.canv_size.x):.4e}"
        self.last_render_time = monotonic() - start

        self.update_border_info()
        self.ready = True

    def update_border_info(self) -> None:
        self.canv.border_title = (
            f"Avg divergence: {self.average_divergence:.4f} | "
            f"{self.settings.canv_size.x * self.settings.canv_size.y} pts | "
            f"{self.renders} rndrs")

        self.canv.border_subtitle = (
            f"Zoom: {self.current_zoom_level} | "
            f"{self.last_render_time:.4f}s | {self.render_settings.max_iter} iter")

    # ---------- TEXTUAL APP METHODS

    @on(FractalCanv.CanvClick)
    def canvas_clicked(self, event: Click) -> None:
        if not self.ready:
            return

        if event.y < 0 or event.y >= self.settings.canv_size.y \
                or event.x < 0 or event.x >= self.settings.canv_size.x:
            return

        action = "none"

        # Right clicks
        if event.button == 3:
            action = self.settings.right_click_mode_name
        # Left clicks
        elif event.button == 1:
            action = self.settings.left_click_mode_name

        click_pos = Vec(event.x, event.y * 2 - 1)
        c_num = self.pos_to_c(click_pos)
        divergence = self.get_divergence(c_num)

        match action:
            case "info":
                self.set_marker(click_pos)

                self.log_write([
                    "[on red] Click info ",
                    f"Clicked at (c): {c_num}",
                    f"Clicked at (pos): {self.settings.marker_pos}",
                    f"Divergence: {divergence}",
                ])
            case "julia":
                # Hide the marker since the fractal has changed
                self.remove_marker()
                self.render_settings.julia_click = c_num
                self.log_info(
                    "Current Julia Set:\n"
                    f"{self.render_settings.julia_click:.4f}")
                self.update_canv()
            case "move":
                self.render_settings.screen_pos_on_plane = c_num
                self.update_canv()
            case "zoom_in":
                self.zoom_at_pos(click_pos, "in")
                self.update_canv()
            case "zoom_out":
                self.zoom_at_pos(click_pos, "out")
                self.update_canv()
            case "mb_start":
                self.render_settings.mandelbrot_starting_value = c_num
                self.log_info(
                    "Current Mandelbrot Set starting value:\n"
                    f"{self.render_settings.mandelbrot_starting_value:.4f}")
                self.update_canv()
            case "inv_mb_num":
                self.render_settings.inv_mandel_numerator = c_num
                self.log_info(
                    "Current Inverse Mandelbrot Set numerator:\n"
                    f"{self.render_settings.inv_mandel_numerator:.4f}")

                self.update_canv()

    def compose(self):
        # Mount the footer and a progress bar
        yield Footer()
        yield self.progress_bar

        self.command_input.border_title = "Command Input"
        self.rich_log.border_title = "Logs Panel"

    async def on_ready(self) -> None:
        # Just so that flake8 doesn't complain about log() being unused
        log("Hellooo <3")

        self.set_command_list()

        # Mount the log panel and the command input in the right container
        await self.right_container.mount(self.rich_log)
        await self.right_container.mount(self.command_input)

        # Mount the canvas and the right container in the container
        await self.container.mount(self.canv)
        await self.container.mount(self.right_container)

        # Mount the container
        await self.app.mount(self.container)

        # Call after a refresh because sometimes the canvas isn't mounted
        # in time and its size is 0 which causes div0 error
        self.call_after_refresh(self.on_ready_)

    def on_ready_(self) -> None:
        self.precision = self.render_settings.wanted_numeric_precision
        self.set_canv_size()

        self.ready = True
        self.reset_position()

        self.canv.focus()

        self.log_write([
            f"[on blue]Welcome to Fractalistic {__version__}",
            "Author: [purple]Léopold Koprivnik[/purple]",
            "GitHub repo: [purple]SkwalExe/fractalistic[/purple]",
        ])
        self.log_write("If you are experiencing slow rendering, try to reduce the size of your terminal.")
        self.log_write(
            "You can change focus between the canvas, "
            "the log panel and the command input using [blue]tab[/blue] or [blue]with your mouse[/blue].")

        if self.settings.state_file is not None:
            self.load_state(self.settings.state_file)

        self.on_resize()

    def on_resize(self, event=None) -> None:
        if not self.first_resize:
            self.first_resize = True
            return

        self.call_after_refresh(self.after_resize)

    async def after_resize(self) -> None:
        self.set_canv_size()
        self.ready = True
        await self.update_canvas_size()
        self.rewrite_logs()
