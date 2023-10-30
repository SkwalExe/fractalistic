##### Textual imports
from textual.app import App
from textual.widgets import Footer, ProgressBar, RichLog, Static, Input
from textual.binding import Binding
from textual.events import Click, Key
from textual import log
from textual.color import Color
from textual import on
###### Local imports
from . import fractals
from .utils import *
from . import colors
from . import __version__
from .query_config import QueryConfig
from .command import Command
from .fractal_canv import FractalCanv
###### Other imports
import os
from PIL import Image
import asyncio
from typing import Any, Callable
from rich.rule import Rule
from time import monotonic, sleep, time
from gmpy2 import mpc, digits, mpfr
#####################

class FractalisticApp(App):
    cell_size: mpfr
    """The height and width of one pixel in the complex plane"""

    screen_pos_on_plane: mpc
    """The position of the top left corner in the plane"""

    canv_size: Vec
    """The number of rows and cols of the canvas"""

    renders: int = 0
    """The number of times a fractal has been rendered"""

    marker_pos: Vec | None = None
    """Position of the red marker on the screen"""

    move_distance: int = 10
    """How many cells far should we move when an arrow key is pressed"""

    zoom_intensity: float = .2
    """How much should we zoom/unzoom"""

    last_render_time: float = 0
    """How long did it take to render the last frame"""

    color_renderer_index: int = 0
    """Index of the current color renderer"""

    fractal_index: int = 0
    """Index of the current fractal"""

    ready: bool = False
    """Whether we should listen to events or not"""

    logs: list = []
    """List of log messages"""

    options: dict[str, Any]
    """Options set by main.py corresponding to the command line arguments"""

    julia_click: mpc = mpc(1, 0)
    """The complex number corresponding to the Julia set to show when a point is clicked on the canvas"""

    print_log_bar: bool = False
    """If we should print a log bar before showing the message in the log panel"""

    command_list: dict[str, Callable]
    """List of commands"""

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

    ####### COMMANDS ###########
    def command_help(self, args):
        command_desc = [f"- [blue]{name}[/blue]: {self.command_list[name].help}" for name in self.command_list]
        self.log_write([
            f"[on blue]Available commands",
            *command_desc
        ])

    def command_clear(self, args):
        self.rich_log.clear()
        self.print_log_bar = False

    def command_quit(self, args):
        self.log_write("Quitting...")
        self.exit()

    def command_version(self, args):
        self.log_write(f"Fractalistic version: [on blue]{__version__}")

    # Cannot set command_list directly because for some obscure
    # reason the quit command doesn't work if you do so
    def set_command_list(self):
        self.command_list = {
            "version": Command(self.command_version, "Show the version number"),
            "clear": Command(self.command_clear, "Clear the log panel"),
            "quit": Command(self.command_quit, "Exit the app"),
            "help": Command(self.command_help, "Show this message")
        }

    ####### ACTIONS ###########
    def action_go(self, x, y):
        if not self.ready:
            return

        # Remove the marker when moving
        self.marker_pos = None

        self.screen_pos_on_plane += mpc(self.move_distance * self.cell_size * x, self.move_distance * self.cell_size * y)
        self.update_canv()

    def action_zoom(self, direction: str):
        if not self.ready:
            return

        # Remove the marker when zooming
        self.marker_pos = None

        if not direction in ["in", "out"]:
            raise ValueError("zoom direction must be 'in' or 'out'")
        
        prev_height = self.canv_size.y * self.cell_size
        prev_width = self.canv_size.x * self.cell_size

        self.cell_size *= 1 + self.zoom_intensity * (1 if direction == "out" else -1)
        new_height = self.canv_size.y * self.cell_size
        new_width = self.canv_size.x * self.cell_size

        diff_h = (prev_height - new_height) if direction == "in" else (new_height - prev_height)
        diff_w = (prev_width - new_width) if direction == "in" else (new_width - prev_width)

        if direction == "in":
            self.screen_pos_on_plane += mpc(diff_w / 2, -diff_h / 2)
        else:
            self.screen_pos_on_plane += mpc(-diff_w / 2, diff_h / 2)

        self.update_canv()

    def action_next_color(self):
        if not self.ready:
            return
        
        self.color_renderer_index = (self.color_renderer_index + 1) % len(colors.color_renderers)
        self.update_canv()
        self.log_write(f"Now using the [purple]{self.selected_color.__name__}[/purple] color scheme")

    def action_next_fractal(self):
        if not self.ready:
            return
        
        # Remove the marker when changing fractal
        self.marker_pos = None

        self.fractal_index = (self.fractal_index + 1) % len(fractals.fractal_list)
        self.update_canv()

        to_write = [f"Now viewing the [purple]{self.selected_fractal.__name__}[/purple] fractal."]
        if not self.selected_fractal.message is None:
            to_write.append(self.selected_fractal.message)
            
        self.log_write(to_write)

    def action_screenshot(self):
        if not self.ready:
            return

        # I dont know why this is working
        # Execute action_screenshot_2 in a non-blocking way
        asyncio.get_event_loop().run_in_executor(None, self.action_screenshot_2)

    def action_screenshot_2(self):
        self.ready = False

        if self.options["fit_screenshots"]:
            screenshot_width = self.canv_size.x * self.options["screenshot_quality"]
            screenshot_height = self.canv_size.y * self.options["screenshot_quality"]
        else:
            screenshot_width = self.options["size"].x
            screenshot_height = self.options["size"].y

        self.container.add_class("hidden")
        self.progress_bar.remove_class("hidden")
        self.progress_bar.update(total=screenshot_height//10, progress=0)

        image = Image.new("RGB", (screenshot_width, screenshot_height), (0, 0, 0))

        # The complex number corresponding to the center of the canvas
        center_on_plane = self.get_center_on_plane()

        # The size in the complex plane, of a pixel of the screenshot
        pixel_size = self.canv_size.x * self.cell_size / screenshot_width

        # the position of the top left hand corner of the screenshot in the complex plane
        screenshot_pos_on_plane = center_on_plane + mpc(-pixel_size*screenshot_width/2, pixel_size*screenshot_height/2)
        

        for y in range(screenshot_height):
            for x in range(screenshot_width):
                c_num = self.pos_to_c(Vec(x, y), pixel_size, screenshot_pos_on_plane)
                result = self.get_divergence(c_num)

                # Get a color from the result
                color = Color.parse("black") if result == -1 else self.selected_color(result)
                image.putpixel((x, y), color.rgb)

            if y % 10 == 0:
                # Make the progress bar advance every 10 rows
                self.progress_bar.advance()


        sleep(1)

        self.progress_bar.add_class("hidden")
        self.container.remove_class("hidden")
        
        save_to = f"{self.selected_fractal.__name__}_screenshot_{int(time())}.png"
        image.save(save_to)
        
        if self.options["debug"]:
            self.call_after_refresh(
                self.log_write, ([
                    f"Center on plane: [blue]{digits(center_on_plane)}",
                    f"Pixel size: [blue]{digits(pixel_size)}",
                    f"Screenshot pos on plane: [blue]{digits(screenshot_pos_on_plane)}"
                ])
            )


        self.call_after_refresh(self.log_write, (f"Screenshot saved to [on violet]{save_to}[/on violet]"))
        
        self.ready = True
        self.call_after_refresh(self.on_resize)
        self.call_after_refresh(self.rewrite_logs)

    def action_reset(self):
        """Reset position and zoom"""
        
        if not self.ready:
            return

        # remove the marker
        self.marker_pos = None

        self.cell_size = 4 / self.canv_size.x
        self.screen_pos_on_plane = mpc(-self.canv_size.x / 2 * self.cell_size, self.canv_size.y / 2 * self.cell_size)
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
        Binding("ctrl+c", "quit", "Quit")
    ]

    CSS_PATH = os.path.join(SRC_DIR, "app.tcss")

    ####### UTILS ########

    def parse_command(self, text):
        args = list(filter(lambda x: len(x) > 0, text.split(" ")))
        
        command = args.pop(0)
        
        if not command in self.command_list:
            self.log_write(f"[red]Cannot find command: [white on red]{command}")
            return 

        self.command_list[command].funct(args)

    @property
    def selected_fractal(self): 
        return fractals.fractal_list[self.fractal_index]

    @property
    def selected_color(self):
        return colors.color_renderers[self.color_renderer_index]

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
        if isinstance(content, str):
            content = [content]

        if self.print_log_bar:
            self.rich_log.write(Rule(), expand=True)
        else:
            self.print_log_bar = True

        for line in content:
            self.rich_log.write(line, shrink=True)


    def get_divergence(self, point: mpc):
        """Get the divergence of a point using the current parameters"""
        query_config = QueryConfig(point, self.options["max_iter"], self.julia_click)
        return self.selected_fractal.get(query_config)

    
    def pos_to_c(self, pos: Vec, cell_size = None, screen_pos_on_plane = None) -> mpc:
        """Takes a position (x, y) of the canvas and converts it into the corresponding complex number on the plane"""
        if cell_size is None:
            cell_size = self.cell_size

        if screen_pos_on_plane is None:
            screen_pos_on_plane = self.screen_pos_on_plane


        return mpc(pos.x * cell_size, pos.y * -cell_size) + screen_pos_on_plane

    def get_center_on_plane(self) -> mpc:
        """Return the center of the canvas in the complex plane"""
        return self.screen_pos_on_plane + mpc(self.canv_size.x // 2 * self.cell_size, -self.canv_size.y // 2 * self.cell_size)

    def set_canv_size(self):
        """
        update self.canv_size
        """

        # Widget height and width of the previous canvas (automatically ajusted)
        height = self.canv.size.height
        width = self.canv.size.width

        # double the height because one char is two pixels in height
        self.canv_size = Vec(width, height * 2)

    async def update_canvas_size(self):
        """
        Remove the previous canvas and create a new one corresponding to self.canv_size
        """
        
        focused = isinstance(self.focused, FractalCanv)

        # Remove the previous canvas widget 
        await self.canv.remove()

        # And create a new one
        self.canv = FractalCanv(self.canv_size.x, self.canv_size.y)

        await self.container.mount(self.canv, before=self.right_container)
        
        if focused:
            self.canv.focus()
            
        self.update_canv()


    def update_canv(self):
        self.ready = False
        asyncio.get_event_loop().run_in_executor(None, self.update_canv_)
        
    def update_canv_(self):
        self.renders += 1
        start = monotonic()

        with self.app.batch_update():
            # y : [0; height[
            for y in range(self.canv.height):
                # x : [0; width[
                for x in range(self.canv.width):

                    # If there is a marker and the current x and y corresponds the its position
                    # make the pixel red and go to the next pixel
                    if not self.marker_pos is None and x == self.marker_pos.x and y == self.marker_pos.y:
                        self.canv.set_pixel(x, y, Color.parse("red"))
                        continue

                    # The position of the pixel in the complex plane
                    c_num = self.pos_to_c(Vec(x, y))
                    # the result is -1 or the number of iteration it took for the series to diverge
                    result = self.get_divergence(c_num)
                    # Get a color from the result
                    color = Color.parse("black") if result == -1 else self.selected_color(result)
                    self.canv.set_pixel(x, y, color)
                 
        self.last_render_time = monotonic() - start

        self.update_border_info()

        self.ready = True

    def update_border_info(self):
        self.canv.border_title = f"{self.renders} renders | {self.canv_size.x * self.canv_size.y} points"
        self.canv.border_subtitle = f"{self.last_render_time:.4f} seconds"
    
   
    
    ####### TEXTUAL APP METHODS ########

    def on_click(self, event: Click):
        if not self.ready:
            return
            
        if event.button == 3:
            self.marker_pos = Vec(event.x-2, event.y * 2 - (3 if event.button == 1 else 2))
            c_num = self.pos_to_c(self.marker_pos)
            divergence = self.get_divergence(c_num)

            self.log_write(
                [
                    f"[on red] Click info ",
                    f"Clicked at (c): {c_num:.4f}",
                    f"Clicked at (pos): {self.marker_pos}",
                    f"Divergence: {divergence}",
                ]
            )


        elif event.button == 1 and self.selected_fractal.__name__ == "Julia":
            # Hide the marker since the fractal has changed
            self.marker_pos = None

            self.julia_click = self.pos_to_c(Vec(event.x, event.y * 2))

            self.log_write(
                [
                    f"[on red] Current Julia Set ",
                    f"{self.julia_click:.4f}",
                ]
            )

        self.update_canv()

    def compose(self):
        # Mount the footer and a progress bar
        yield Footer()
        yield self.progress_bar

        self.set_command_list()

        self.command_input.border_title = "Command Input"
        self.rich_log.border_title = "Logs Panel"


    async def on_ready(self):
        # Mount the log panel and the command input in the right container
        await self.right_container.mount(self.rich_log)
        await self.right_container.mount(self.command_input)
        
        # Mount the canvas and the right container in the container
        

        await self.container.mount(self.canv)
        await self.container.mount(self.right_container)

        # Mount the container
        await self.app.mount(self.container)

        
        self.set_canv_size()

        self.ready = True
        self.action_reset()

        self.canv.focus()
        

        self.log_write([
            f"[on blue]Welcome to Fractalistic {__version__}",
            f"Author: [purple]Léopold Koprivnik[/purple]",
            f"GitHub repo: [purple]SkwalExe/fractalistic[/purple]",
        ])
        self.log_write(f"If you are experiencing slow rendering, try to reduce the size of your terminal.")
    

    def on_resize(self, event = None) -> None:
        self.call_after_refresh(self.after_resize)


    async def after_resize(self) -> None:
        self.set_canv_size()
        await self.update_canvas_size()
        self.rewrite_logs()
