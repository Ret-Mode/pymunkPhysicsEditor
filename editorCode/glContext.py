from typing import Tuple

class GLContextI:

    _instance: "GLContextI" = None

    @staticmethod
    def getInstance() -> "GLContextI":
        assert GLContextI._instance is not None
        return GLContextI._instance

    def setProjection(self, projection:Tuple[float]):
        raise NotImplementedError
    
    def setViewport(self, viewport: Tuple[float]):
        raise NotImplementedError