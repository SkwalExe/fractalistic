import os
from typing import Any

SRC_DIR = os.path.dirname(os.path.abspath(__file__))

class Vec():
    x: Any
    y: Any
    def __init__(self, x: Any, y: Any):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Vec({self.x}, {self.y})"