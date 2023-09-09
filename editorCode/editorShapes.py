from .editorTypes import V2
from .shapeInternals.editorBodyI import BodyI

from typing import List


# TODO -> swap into this eventually
class BBox:

    def __init__(self) -> None:
        self.dl = V2()
        self.ur = V2()

    def setFromPoint(self, x:float, y:float):
        self.dl.x = x
        self.ur.x = x
        self.dl.y = y
        self.ur.y = y

    def update(self, xMin:float, yMin: float, xMax:float, yMax:float):
        self.dl.x = xMin
        self.dl.y = yMin
        self.ur.x = xMax
        self.ur.y = yMax

    def intersect(self, other: "BBox") -> bool:
        if self.dl.x > other.ur.x or other.dl.x > self.ur.x or self.dl.y > other.ur.y or other.dl.y > self.ur.y:
            return False
        return True

class Container(BodyI):
    pass
