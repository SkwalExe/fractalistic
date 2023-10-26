from abc import ABC, abstractmethod

class FractalBase(ABC):
    """Base class for fractals."""
    
    message: str

    @staticmethod
    @abstractmethod
    def get() -> int:
        """Returns the number of iterations required to classify a point as convergent (or -1 if it diverges)."""
        pass

