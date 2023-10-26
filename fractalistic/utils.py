import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))

class Vec():
    x: float | int
    y: float | int
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Vec({self.x}, {self.y})"