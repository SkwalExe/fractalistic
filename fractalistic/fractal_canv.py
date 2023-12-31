from textual_canvas import Canvas
from textual.binding import Binding
from textual.events import MouseEvent


class FractalCanv(Canvas):
    class CanvClick(MouseEvent):
        pass

    BINDINGS = [
        Binding("left", "go(-1, 0)", "Left"),
        Binding("right", "go(1, 0)", "Right"),
        Binding("up", "go(0, 1)", "Up"),
        Binding("down", "go(0, -1)", "Down"),
        Binding("d", "zoom('in')", "Zoom in"),
        Binding("s", "zoom('out')", "Zoom out"),
        Binding("r", "reset", "Rst pos/zoom"),
        Binding("c", "next_color", "Nxt Color Scheme"),
        Binding("f", "next_fractal", "Nxt Fractal"),
        Binding("p", "screenshot", "HD Screenshot"),
    ]

    def on_click(self, event):
        self.post_message(self.CanvClick.from_event(event))
