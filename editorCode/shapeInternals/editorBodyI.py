from ..editorTypes import Mat, ContainerTransform, BoundingBox
from ..shapeBuffer import ShapeBuffer
from .editorBodyPhysics import BodyPhysics
from .editorShapeI import ShapeI

from typing import List


class BodyI:

    NONE = "NONE"
    DYNAMIC = "Dynamic"
    KINEMATIC = "Kinematic"
    STATIC = "Static"
    
    def __init__(self, label:str):
        
        self.label: str = label

        self.box = BoundingBox()
        self.transform = ContainerTransform()
        
        self.type :str
        self.shapes: List[ShapeI] = []

        self.physics : BodyPhysics

    @staticmethod
    def getTypes() -> List[str]:
        return [BodyI.DYNAMIC, BodyI.KINEMATIC, BodyI.STATIC]

    def updatePos(self, transform:Mat):
        raise NotImplementedError

    def updateEye(self):
        self.updatePos(Mat.Eye())

    def getJSONDict(self, parent:dict):
        raise NotImplementedError

    def recalcPhysics(self):
        raise NotImplementedError

    def clone(self, source:"BodyI") -> "BodyI":
        self.box.clone(source.box)
        self.transform.clone(source.transform)
        self.physics.clone(source.physics)

    def bufferData(self, buffer:ShapeBuffer):
        for shape in self.shapes:
            shape.bufferData(buffer)
    
