from abc import ABC, abstractmethod
from gmpy2 import mpc
from ..settings import RenderSettings


class FractalBase(ABC):
    """Base class for fractals."""

    message: str | None

    @staticmethod
    @abstractmethod
    def get(point: mpc, settings: RenderSettings) -> int:
        """Returns the number of iterations required to classify a point as convergent (or -1 if it diverges)."""
        pass
