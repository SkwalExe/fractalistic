from textual.binding import Binding
from textual.events import MouseEvent
from textual_canvas import Canvas


class FractalCanv(Canvas):
    class CanvClick(MouseEvent):
        pass

    BINDINGS = [
        Binding("left, h", "go(-1, 0)", "Left", False),
        Binding("right, l", "go(1, 0)", "Right", False),
        Binding("up, k", "go(0, 1)", "Up", False),
        Binding("down, j", "go(0, -1)", "Down", False),
        Binding("d", "zoom('in')", "Zoom +"),
        Binding("s", "zoom('out')", "Zoom -"),
        Binding("r", "reset", "Rst pos/zoom"),
        Binding("c", "next_color", "Nxt Color Scheme"),
        Binding("f", "next_fractal", "Nxt Fractal"),
        Binding("p", "capture", "HD Screenshot"),
    ]

    def on_click(self, event: MouseEvent) -> None:
        self.post_message(self.CanvClick.from_event(event))
