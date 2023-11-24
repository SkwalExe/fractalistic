
class ClickMode():
    description: str

    def __init__(self, description: str):
        self.description = description


CLICK_MODES = {
    "julia": ClickMode("Set the Julia constant to the clicked point"),
    "zoom": ClickMode("Zoom in on the clicked point"),
    "move": ClickMode("Move the canvas to the clicked point"),
    "info": ClickMode("Show information about the clicked point"),
    "none": ClickMode("Do nothing")
}
