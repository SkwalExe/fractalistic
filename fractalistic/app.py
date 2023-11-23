##### Textual imports
from textual.app import App
from textual.widgets import Footer, ProgressBar, RichLog, Static, Input
from textual.binding import Binding
from textual.events import Click
from textual import log
from textual.color import Color
from textual import on
###### Local imports
from . import fractals
from .utils import *
from . import colors
from .vec import Vec
from .settings import Settings, RenderSettings
from . import __version__
from .command import Command, CommandIncrement, CommandIncrementArgParseResult
from .fractal_canv import FractalCanv
###### Other imports
import os
from PIL import Image
import asyncio
from typing import Any, Callable
from multiprocessing import Process, Pool, Queue, Manager
from rich.rule import Rule
from time import monotonic, sleep, time
from gmpy2 import mpc, digits, mpfr
from copy import deepcopy
import gmpy2
import toml
from math import ceil, floor
import itertools
#####################

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
    """[NOT REACTIVE], current zoom level, updated at each render and used to show the zoom level in the cavas border subtitle"""
   
    command_list: dict[str, Command | CommandIncrement]

    current_process_pool = None

    ###### DOM ELEMENTS #####
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
    
    ####### COMMANDS ###########

    def command_help(self, args):
        if len(args) == 0:
            command_desc = [f"- [blue]{name}[/blue]: {self.command_list[name].help}" for name in self.command_list]
            self.log_write([
                f"[on blue]Available commands",
                *command_desc,
                f"[green]Use 'help command_name' to get more info about a command"
            ])
        elif len(args) == 1:
            command = self.get_command(args[0])
            if command is None:
                return
            
            self.log_write([
                f"[on blue]{args[0]} command",
                command.help,
                command.extra_help
            ])

    def command_clear(self, args):
        self.rich_log.clear()
        self.print_log_bar = False

    def command_quit(self, args):
        self.log_write("Quitting...")
        self.exit()

    def command_version(self, args):
        self.log_write(f"Fractalistic version: [on blue]{__version__}")

    def command_capture(self, args):
        if len(args) == 0:
            self.action_screenshot()
        elif len(args) == 2:
            try:
                width = int(args[0])
                height = int(args[1])
            except ValueError:
                self.log_write("Width and height must be integers")
                return

            if width <= 0 or height <= 0:
                self.log_write("Width and height must be positive")
                return


            self.action_screenshot(Vec(width, height))

    def command_capture_fit(self, args):
        if len(args) == 0:
            self.action_screenshot(self.get_screenshot_size_fit())
        elif len(args) == 1:
            try:
                quality = int(args[0])
            except ValueError:
                self.log_write("Quality must be an integer")
                return

            if quality <= 0:
                self.log_write("Quality must be positive")
                return

            self.action_screenshot(self.get_screenshot_size_fit(quality))

    def command_max_iter(self, value: int):
                
        self.render_settings.max_iter = value

        self.log_write(f"max_iter set to [blue]{self.render_settings.max_iter}")
        self.update_canv()

    def command_zoom_lvl(self, value: int):
        self.settings.zoom_intensity = value
        self.log_write(f"Zoom level set to [blue]{self.settings.zoom_intensity}%")

    def command_move_dist(self, value: int):
        self.settings.move_distance = value
        self.log_write(f"Move distance set to [blue]{self.settings.move_distance}")

    def command_goto(self, args):
        if len(args) == 0:
            self.log_write(f"Current position: [blue]{self.render_settings.screen_pos_on_plane.real}+{self.render_settings.screen_pos_on_plane.imag}i")
            return

        real = None
        imag = None
        try:
            real = mpfr(args[0])
            imag = mpfr(args[1])
        except ValueError:
            self.log_write("Real and imaginary parts must be valid integers or floats")
            return

        self.render_settings.screen_pos_on_plane = mpc(real, imag)
        self.update_canv()

    def command_click_pos(self, args):
        if len(args) == 1:
            if not args[0] in ["off", "on"]:
                self.log_write(f"[red]Expected 'on' or 'off'.")
        
            self.settings.click_pos_enabled = args[0] == "on"

        self.log_write(f"Click pos mode is currently : {'enabled' if self.settings.click_pos_enabled else 'disabled'}.")
        return

    def command_precision(self, value: int):
        self.precision = value

        self.log_write(f"Numeric precision set to [blue]{value}")
        self.update_canv()

    def command_save_state(self, args):
        if len(args) == 0:
            filename = f"{self.selected_fractal.__name__}_state_{int(time())}.toml"
        else:
            filename = args[0]

        try:
            with open(filename, "w") as f:
                f.write(toml.dumps(self.get_state()))
        except OSError as e:
            self.log_write(f"Cannot write to file '{filename}'. [red]Errno {e.errno}: {e.strerror}.")
            return

        self.log_write(f"State saved to [blue]{filename}")

    def command_load_state(self, args):
        self.load_state(args[0])
        self.update_canv()

    def command_threads(self, value: int):
        self.settings.threads = value
        self.log_write(f"Rendering thread count set to [blue]{self.settings.threads}")

    def command_screenshot_threads(self, value: int):
        self.settings.screenshot_threads = value
        self.log_write(f"Screensdhot thread count set to [blue]{self.settings.threads}")

    # We cant directly set command_list because we couldn't reference command methods correctly
    def set_command_list(self):
        self.command_list = {
            "max_iter": CommandIncrement(
                funct=self.command_max_iter,
                help="Change the maximum number of iterations used to determine if a point converges or not.",
                app_attribute="settings.render_settings.max_iter",
                min_value=6,
            ),
            "move_dist": CommandIncrement(
                funct=self.command_move_dist,
                help="Change the distance to move when a key is pressed, in canvas cells.",
                app_attribute="settings.move_distance",
                min_value=1
            ),
            "precision": CommandIncrement(
                funct=self.command_precision,
                help="Fine-tune numeric precision by specifying the desired bit length for numeric values",
                app_attribute="precision",
                min_value=5
            ),
            "threads": CommandIncrement(
                funct=self.command_threads,
                help="Change the number of threads used for rendering",
                app_attribute="settings.threads",
                min_value=1
            ),
            "screenshot_threads": CommandIncrement(
                funct=self.command_screenshot_threads,
                help="Change the number of threads used for rendering screenshots",
                app_attribute="settings.screenshot_threads",
                min_value=1
            ),
            "zoom_lvl": CommandIncrement(
                funct=self.command_zoom_lvl,
                help="Change the zoom factor (intensity) when s or d is pressed, in percent.",
                app_attribute="settings.zoom_intensity",
                min_value=1,
                max_value=100
            ),
            "capture": Command(
                funct=self.command_capture, 
                help="Take a high quality screenshot",
                accepted_arg_counts=[0, 2], 
                extra_help="[green]Usage : \\[width] \\[height]\nUsage : no args[/green]\nIf no width and height are specified, the command line settings are used."
            ),
            "pos": Command(
                funct=self.command_goto,
                help="Set the position to a specific point in the complex plane.",
                accepted_arg_counts=[0, 2],
                extra_help="[green]Usage : \\[real] \\[imag]\nUsage : no args[/green]\nIf no arguments are given, just print out the current position. Else, go to the given position. \\[real] and \\[imag] must be valid integers or floats."
            ),
            "click_pos": Command(
                funct=self.command_click_pos,
                help="If enabled, set the current position to the position of RIGHT mouse clicks on the canvas.",
                accepted_arg_counts=[0, 1],
                extra_help="[green]Usage : on/off\nUsage : no args[/green]\nIf no argument is given, print out the current state. Else, enable or disable click_pos mode."
            ),
            "capture_fit": Command(
                funct=self.command_capture_fit, 
                help="Take a high quality screenshot that fits the size of the canvas.",
                accepted_arg_counts=[0, 1], 
                extra_help="[green]Usage : \\[quality]\nUsage : no arg.[/green]\nIf no quality is specified, the command line settings are used."
            ),
            "save_state": Command(
                funct=self.command_save_state,
                help="Save the current state of the app to a file (current fractal, color, position, zoom, etc).",
                accepted_arg_counts=[0, 1],
                extra_help="[green]Usage : \\[filename]\nUsage : no args[/green]\nIf no filename is specified, one will be generated automatically."
            ),
            "load_state": Command(
                funct=self.command_load_state,
                help="Load a state from a file.",
                accepted_arg_counts=[1],
                extra_help="[green]Usage : \\[filename][/green]"
            ),
            "version": Command(self.command_version, "Show the version number", [0]),
            "clear": Command(self.command_clear, "Clear the log panel", [0]),
            "quit": Command(self.command_quit, "Exit the app", [0]),
            "help": Command(self.command_help, "Show the help message", [0, 1])
        }

    ####### ACTIONS ###########
    def action_cancel_screenshot(self):
        self.cancel_screenshot = True
        self.log_write("Screenshot cancelled")


    def action_go(self, x, y):
        if not self.ready:
            return

        # Remove the marker when moving
        self.remove_marker()
        self.render_settings.screen_pos_on_plane += mpc(self.settings.move_distance * self.render_settings.cell_size * x, self.settings.move_distance * self.render_settings.cell_size * y)
        self.update_canv()

    def action_zoom(self, direction: str):
        if not self.ready:
            return

        # Remove the marker when zooming
        self.remove_marker()

        if not direction in ["in", "out"]:
            raise ValueError("zoom direction must be 'in' or 'out'")
        
        # 101 to avoid doind 1-1 and making a 0 zoom factor which would cause a div0 error
        zoom_factor = 1 - self.settings.zoom_intensity / 101
        self.render_settings.cell_size *= zoom_factor if direction == "in" else 1/zoom_factor
        
        self.update_canv()

    def action_next_color(self):
        if not self.ready:
            return
        
        self.render_settings.color_renderer_index = (self.render_settings.color_renderer_index + 1) % len(colors.color_renderers)
        self.update_canv()
        self.log_write(f"Now using the [purple]{self.selected_color.__name__}[/purple] color scheme")

    def action_next_fractal(self):
        if not self.ready:
            return
        
        # Remove the marker when changing fractal
        self.remove_marker()

        self.render_settings.fractal_index = (self.render_settings.fractal_index + 1) % len(fractals.fractal_list)
        self.update_canv()

        to_write = [f"Now viewing the [purple]{self.selected_fractal.__name__}[/purple] fractal."]
        if not self.selected_fractal.message is None:
            to_write.append(self.selected_fractal.message)
            
        self.log_write(to_write)

    def action_screenshot(self, screenshot_size: Vec | None = None):
        if not self.ready:
            return

        # I dont know why this is working
        # Execute action_screenshot_2 in a non-blocking way
        asyncio.get_event_loop().run_in_executor(None, self.action_screenshot_2, (screenshot_size))

    def action_screenshot_2(self, screenshot_size: Vec | None):
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
        result = self.get_divergence_matrix(cell_size=pixel_size, size=screenshot_size, update_loading_bar=True, threads=self.settings.screenshot_threads)
        
        # If the screenshot was cancelled, None is returned
        # If the screenshot wasn't cancelled, save the screenshot to a file, put a message in the log panel
        # And wait one second to allow the user to see that the operation is finished successfully.
        if not self.cancel_screenshot:
            for (y, line) in enumerate(result):
                for (x, divergence) in enumerate(line):
                    # Get a color from the result
                    color = Color.parse("black") if divergence == -1 else self.selected_color(divergence)
                    image.putpixel((x, y), color.rgb)
            save_to = f"{self.selected_fractal.__name__}_screenshot_{int(time())}.png"
            image.save(save_to)
            self.call_after_refresh(self.log_write, (f"Screenshot [{screenshot_width}x{screenshot_height}] saved to [on violet]{save_to}[/on violet]"))
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

    def action_quit_(self):
        """We don't use the builtin quit action because it doesn't work during screenshots"""

        # Cancel any ongoing screenshots before leaving
        self.action_cancel_screenshot()

        self.exit()

    def action_reset(self):
        """Reset position and zoom"""
        
        if not self.ready:
            return

        self.reset_position()
        self.update_canv()

    @on(Input.Submitted, "Input")
    def command_input_on_submitted(self, event: Input.Submitted):
        command = event.value.strip()
        self.command_input.value = ""

        if len(command) == 0:
            return

        self.parse_command(command)

    ###### TEXTUAL APP VARS ######

    BINDINGS = [
        Binding("ctrl+c", "quit_", "Quit", priority=True)
    ]

    CSS_PATH = os.path.join(SRC_DIR, "app.tcss")

    ####### UTILS ########

    def get_divergence_matrix(self, cell_size: mpc | None = None, size: Vec | None = None, threads: int | None = None, update_loading_bar: bool = False):
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
        divergence_matrices_async = self.current_process_pool.starmap_async(get_divergence_matrix, [(chunk[0], chunk[1], render_settings, size, queue) for chunk in chunks], chunksize=1)
        
        rendered_lines = 0
        while not divergence_matrices_async.ready():

            # Return None if the screenshot was cancelled, and terminate the processes
            if self.cancel_screenshot:
                self.current_process_pool.terminate()
                return None

            while not queue.empty():
                rendered_lines += 1

                # A message is added to the queue everytime a line is rendered
                queue.get()

                # Make the progress bar advance every 10 lines
                if rendered_lines % 10 == 0:
                    self.progress_bar.advance()

        # When the rendering is finished, get the result from each process
        divergence_matrices = divergence_matrices_async.get()

        # Flatten the array of each process result into one big array
        result = list(itertools.chain.from_iterable(divergence_matrices))

        # Close the pool of processes
        self.current_process_pool.close()
        self.current_process_pool = None

        return result

    def load_state(self, filename: str):
        try:
            with open(filename, "r") as f:
                try:
                    state = toml.loads(f.read())

                except toml.TomlDecodeError as e:
                    self.log_write(f"Cannot decode file '{filename}'. [red]{e}")
                    return

        except OSError as e:
            self.log_write(f"Cannot read file '{filename}'. [red]Errno {e.errno}: {e.strerror}.")
            return
        
        try:
            self.render_settings.fractal_index = get_fractal_index_from_name(state["fractal"])
            self.render_settings.color_renderer_index = get_color_index_from_name(state["color"])
            self.render_settings.max_iter = int(state["max_iter"])
            self.precision = self.render_settings.wanted_numeric_precision
            self.render_settings.cell_size = mpfr(state["cell_size"])
            screen_pos_on_plane_real = mpfr(state["screen_pos_on_plane_real"])
            screen_pos_on_plane_imag = mpfr(state["screen_pos_on_plane_imag"])
            self.settings.render_settings.screen_pos_on_plane = mpc(screen_pos_on_plane_real, screen_pos_on_plane_imag)
            julia_click_real = mpfr(state["julia_click_real"])
            julia_click_imag = mpfr(state["julia_click_imag"])
            self.render_settings.julia_click = mpc(julia_click_real, julia_click_imag)

        except KeyError as e:
            self.log_write(f"Cannot load state from file '{filename}'. [red]Missing key: {e}")
            return

        self.log_write(f"State loaded from [blue]{filename}[/blue]")

    def get_state(self):
        return {
            "fractal": self.selected_fractal.__name__,
            "color": self.selected_color.__name__,
            "max_iter": str(self.render_settings.max_iter),
            "precision": str(self.render_settings.wanted_numeric_precision),
            "cell_size": self.render_settings.cell_size.__format__(".2048g"),
            "screen_pos_on_plane_real": self.render_settings.screen_pos_on_plane.real.__format__(".2048g"),
            "screen_pos_on_plane_imag": self.render_settings.screen_pos_on_plane.imag.__format__(".2048g"),
            "julia_click_real": self.render_settings.julia_click.real.__format__(".2048g"),
            "julia_click_imag": self.render_settings.julia_click.imag.__format__(".2048g"),
            "version": __version__,
        }

    def reset_position(self):
        # remove the marker
        self.remove_marker()

        self.render_settings.cell_size = 4 / self.settings.canv_size.x
        self.render_settings.screen_pos_on_plane = mpc(0, 0)

    @property
    def precision(self):
        return gmpy2.get_context().precision

    @property
    def render_settings(self):
        return self.settings.render_settings

    @precision.setter
    def precision(self, value):
        set_precision(value)
        self.render_settings.wanted_numeric_precision = value

    def get_command(self, name: str) -> Command:
        if not name in self.command_list:
            self.log_write(f"[red]Cannot find command: [white on red]{name}")
            return None

        return self.command_list[name]

    def get_screenshot_size_fit(self, quality: int | None = None):
        """
        Return the size of the screenshot so that it fits the terminal
        """

        if quality is None:
            quality = self.settings.screenshot_quality

        screenshot_width = self.settings.canv_size.x * quality
        screenshot_height = self.settings.canv_size.y * quality
    
        return Vec(screenshot_width, screenshot_height)


    def get_screenshot_size_from_options(self, fit_quality: int | None = None):
        if self.settings.fit_screenshots:
            return self.get_screenshot_size_fit(fit_quality)
    
        return Vec(self.settings.screenshot_size.x, self.settings.screenshot_size.y)

    def remove_marker(self):
        self.settings.marker_pos = None

    def parse_command(self, text: str):
        args = list(filter(lambda x: len(x) > 0, text.split(" ")))
        
        command_name = args.pop(0)
        command = self.get_command(command_name)

        if command is None:
            return 

        if not len(args) in command.accepted_arg_count:
            self.log_write(f"[red]Command [white on red]{command_name}[/white on red] expects {', or '.join([str(x) for x in command.accepted_arg_count])} arguments, got {len(args)}")
            return

        if isinstance(command, CommandIncrement):
            attributes = command.app_attribute.split(".")
            current_attribute_value = self
            for attribute in attributes:
                current_attribute_value = current_attribute_value.__getattribute__(attribute)

            value = command.parse_args(current_attribute_value, args)
            if value.success:
                command.funct(value.new_value)                
            else:
                self.log_write(value.error_message)
                return
        else:
            command.funct(args)

    @property
    def selected_fractal(self): 
        return fractals.fractal_list[self.render_settings.fractal_index]

    @property
    def selected_color(self):
        return colors.color_renderers[self.render_settings.color_renderer_index]

    def rewrite_logs(self):
        """Rewrite the logs so that they fit the new log panel size when the terminal is resized"""
        self.print_log_bar = False
        self.rich_log.clear()
        for line in self.logs:
            self._log_write(line)

    def log_write(self, content: str | list[str]):
        self._log_write(content)
        self.logs.append(content)

    def _log_write(self, content):
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


    def get_divergence(self, point: mpc):
        """Get the divergence of a point using the current parameters"""
        return self.selected_fractal.get(point, self.render_settings)

    
    def pos_to_c(self, pos: Vec, cell_size = None, screen_pos_on_plane = None, screen_size: Vec | None = None) -> mpc:
        """Takes a position (x, y) of the canvas and converts it into the corresponding complex number on the plane"""
        if cell_size is None:
            cell_size = self.render_settings.cell_size

        if screen_pos_on_plane is None:
            screen_pos_on_plane = self.render_settings.screen_pos_on_plane

        if screen_size is None:
            screen_size = self.settings.canv_size

        return pos_to_c(pos, cell_size, screen_pos_on_plane, screen_size)
    
    def set_canv_size(self):
        """
        update self.canv_size
        """

        # Widget height and width of the previous canvas (automatically ajusted)
        height = self.canv.size.height
        width = self.canv.size.width

        # double the height because one char is two pixels in height
        self.settings.canv_size = Vec(width, height * 2)

    async def update_canvas_size(self):
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


    def update_canv(self):
        if not self.ready:
            return
            
        self.ready = False
        asyncio.get_event_loop().run_in_executor(None, self.update_canv_)

    def update_canv_(self):
        self.renders += 1
        start = monotonic()


        result = self.get_divergence_matrix()
        # If result is none, it means ctrl+c was pressed during the rendering
        # then the program is exiting and we don't care anymore about updating the canvas
        if result is None:
            return

        # Used to get the average divergence of the current render
        divergence_sum = 0
        term_count = 0

        with self.batch_update():
            for (y, line) in enumerate(result):
                for (x, divergence) in enumerate(line):

                    # If there is a marker and the current x and y corresponds the its position
                    # make the pixel red and go to the next pixel
                    if not self.settings.marker_pos is None and x == self.settings.marker_pos.x and y == self.settings.marker_pos.y:
                        self.canv.set_pixel(x, y, Color.parse("red"))
                        continue

                    if divergence != -1:
                        divergence_sum += divergence
                        term_count += 1

                    # Get a color from the result
                    color = Color.parse("black") if divergence == -1 else self.selected_color(divergence)
                    self.canv.set_pixel(x, y, color)


        self.average_divergence = divergence_sum / term_count if term_count > 0 else 0
        self.current_zoom_level = f"{4 / (self.render_settings.cell_size * self.settings.canv_size.x):.4e}"
        self.last_render_time = monotonic() - start

        self.update_border_info()
        self.ready = True
    

    def update_border_info(self):
        self.canv.border_title = f"Avg divergence: {self.average_divergence:.4f} | {self.settings.canv_size.x * self.settings.canv_size.y} pts | {self.renders} rndrs"
        self.canv.border_subtitle = f"Zoom: {self.current_zoom_level} | {self.last_render_time:.4f}s | {self.render_settings.max_iter} iter"
   
    
    ####### TEXTUAL APP METHODS ########

    def on_click(self, event: Click):
        if not self.ready:
            return
        # Right clicks
        if event.button == 3:
            click_pos = Vec(event.x, event.y * 2 - 1)
            c_num = self.pos_to_c(click_pos)


            if self.settings.click_pos_enabled:
                self.render_settings.screen_pos_on_plane = c_num
                self.update_canv()
                return
            else:
                self.marker_pos = click_pos
                divergence = self.get_divergence(c_num)

                self.log_write([
                    f"[on red] Click info ",
                    f"Clicked at (c): {digits(c_num)}",
                    f"Clicked at (pos): {self.marker_pos}",
                    f"Divergence: {divergence}",
                ])

        # [OTHER CLICKS]
        elif event.button == 1 and self.selected_fractal.__name__ == "Julia":
            # Hide the marker since the fractal has changed
            self.remove_marker()

            self.render_settings.julia_click = self.pos_to_c(Vec(event.x, event.y * 2))

            self.log_write([
                f"[on red] Current Julia Set ",
                f"{self.render_settings.julia_click:.4f}",
            ])

        self.update_canv()

    def compose(self):
        # Mount the footer and a progress bar
        yield Footer()
        yield self.progress_bar

        self.command_input.border_title = "Command Input"
        self.rich_log.border_title = "Logs Panel"

    async def on_ready(self):
        self.set_command_list()

        # Mount the log panel and the command input in the right container
        await self.right_container.mount(self.rich_log)
        await self.right_container.mount(self.command_input)
        
        # Mount the canvas and the right container in the container
        

        await self.container.mount(self.canv)
        await self.container.mount(self.right_container)

        # Mount the container
        await self.app.mount(self.container)

        # Call after a refresh because sometimes the canvas isn't mounted in time and its size is 0 which causes div0 error
        self.call_after_refresh(self.on_ready_)
    
    def on_ready_(self):
        

        self.precision = self.render_settings.wanted_numeric_precision
        self.set_canv_size()

        self.ready = True
        self.reset_position()

        self.canv.focus()
        

        self.log_write([
            f"[on blue]Welcome to Fractalistic {__version__}",
            f"Author: [purple]Léopold Koprivnik[/purple]",
            f"GitHub repo: [purple]SkwalExe/fractalistic[/purple]",
        ])
        self.log_write(f"If you are experiencing slow rendering, try to reduce the size of your terminal.")
        self.log_write(f"You can change focus between the canvas, the log panel and the command input using [blue]tab[/blue] or [blue]with your mouse[/blue].")

        if not self.settings.state_file is None: 
            self.load_state(self.settings.state_file)
        
        self.on_resize()

    def on_resize(self, event = None) -> None:
        if not self.first_resize:
            self.first_resize = True
            return

        self.call_after_refresh(self.after_resize)


    async def after_resize(self) -> None:
        self.set_canv_size()
        self.ready = True
        await self.update_canvas_size()
        self.rewrite_logs()
