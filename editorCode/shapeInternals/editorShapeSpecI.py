from ..editorTypes import Mat, EditorPoint, Radius, BoundingBox

from typing import Tuple, List


class ShapeSpec:

    def __init__(self):
        self.points: List[EditorPoint] = []
        self.radius: Radius = Radius(1.0)

    def draw(self):
        raise NotImplementedError
    
    def addPoint(self, point:EditorPoint):
        raise NotImplementedError

    def resetWH(self, point:EditorPoint):
        raise NotImplementedError

    def setWH(self, point:EditorPoint):
        raise NotImplementedError

    def setRadiusFromFloat(self, radius:float):
        assert False

    def deletePoint(self, point:EditorPoint):
        raise NotImplementedError
    
    def updatePos(self, final: Mat):
        raise NotImplementedError
    
    def clone(self, source:'ShapeSpec') -> 'ShapeSpec':
        raise NotImplementedError

    def getJSONDict(self, parent:dict):
        raise NotImplementedError
    
    def getBounds(self, box:BoundingBox) -> None:
        raise NotImplementedError
    
