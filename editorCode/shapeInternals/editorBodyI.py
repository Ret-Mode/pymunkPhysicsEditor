from ..editorTypes import Mat, ContainerTransform, BoundingBox
from .editorBodyPhysics import BodyPhysics
from .editorShapeI import ShapeI

from typing import List


class BodyI:

    NONE = "NONE"
    DYNAMIC = "DYNAMIC"
    KINEMATIC = "KINEMATIC"
    STATIC = "STATIC"
    
    def __init__(self, label:str):
        
        self.label: str = label

        self.box = BoundingBox()
        self.transform = ContainerTransform()
        
        self.type :str
        self.shapes: List[ShapeI] = []

        self.physics : BodyPhysics

    def updatePos(self, transform:Mat):
        raise NotImplementedError

    def getJSONDict(self, parent:dict):
        raise NotImplementedError

    def recalcPhysics(self):
        raise NotImplementedError

    def clone(self, newLabel:str):
        raise NotImplementedError