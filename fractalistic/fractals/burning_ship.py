from ..query_config import QueryConfig
from .fractal_base import FractalBase
from gmpy2 import mpc

class BurningShip(FractalBase):
    """
    With U0 = 0 and c being the point in the complex plane, 
    Un+1 = (|Re(Un)| + i|Im(Un)|)² + c
    """

    message = None

    @staticmethod
    def get(config: QueryConfig) -> int:
        i = 0
        z = mpc(0, 0)
        while abs(z) < 5 and i < config.max_iter:
            z = mpc(abs(z.real), abs(z.imag))
            z = z*z - config.point_in_plane
            i+=1

        if i == config.max_iter:
            return -1
        
        return i