from gmpy2 import mpc

class QueryConfig():
    point_in_plane: mpc
    max_iter: int

    def __init__(self, point_in_plane: mpc, max_iter: int, julia_click: mpc):
        self.point_in_plane = point_in_plane
        self.max_iter = max_iter
        self.julia_click = julia_click
