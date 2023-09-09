from .editorTypes import V2, ContainerTransform
from .shapeInternals.editorShapeI import ShapeI
from .shapeInternals.editorBodyI import BodyI

from .editorMousePivot import MousePivotParams
from typing import ClassVar, Literal, Sequence, Union


class ContinuousTransform:

    ROTATE: ClassVar[Literal[0]]     = 0
    MOVE: ClassVar[Literal[1]]       = 1
    SCALE: ClassVar[Literal[2]]      = 2
    ROTATESCALE: ClassVar[Literal[2]] = 3
    modes: Sequence[Literal[0, 1, 2]] = {ROTATE, MOVE, SCALE, ROTATESCALE}

    def __init__(self):
        self.transform = ContainerTransform()
        self.mouseParam = MousePivotParams()
        self.mode: Literal[0, 1, 2] = ContinuousTransform.MOVE
        self.active: bool        = False
        self.obj: Union[ShapeI, BodyI] = None

    def init(self, obj: Union[ShapeI, BodyI], startPoint: V2, pivot: V2):
        self.obj = obj
        if self.obj:
            self.transform.objectAnchor.setFromV(self.obj.transform.objectAnchor)
            self.transform.objectAngle.setA(self.obj.transform.objectAngle)
            self.transform.objectScale = self.obj.transform.objectScale
            self.mouseParam.set(pivot, startPoint)

    def resetParams(self):
        if self.obj:
            self.obj.transform.objectAnchor.setFromV(self.transform.objectAnchor)
            self.obj.transform.objectAngle.setA(self.transform.objectAngle)
            self.obj.transform.objectScale = self.transform.objectScale

    def update(self, point:V2):
        if self.active and self.obj:
            self.mouseParam.update(point)
            self.obj.transform.objectAnchor.setFromV(self.transform.objectAnchor)
            self.obj.transform.objectAngle.setA(self.transform.objectAngle)
            self.obj.transform.objectScale = self.transform.objectScale
            self.recalc()

    def setMode(self, mode: Union[Literal[0], Literal[1], Literal[2], Literal[3]]) -> None:
        if mode in ContinuousTransform.modes:
            self.mode = mode

    def recalc(self) -> None:
        if self.mode == ContinuousTransform.ROTATE:
            self.obj.transform.rotate(self.mouseParam.dA, self.mouseParam.pivot)
        if self.mode == ContinuousTransform.MOVE:
            self.obj.transform.move(self.mouseParam.dEnd)
        if self.mode == ContinuousTransform.SCALE:
            self.obj.transform.scale(self.mouseParam.dS, self.mouseParam.pivot)
        if self.mode == ContinuousTransform.ROTATESCALE:
            self.obj.transform.rotate(self.mouseParam.dA, self.mouseParam.pivot)
            self.obj.transform.scale(self.mouseParam.dS, self.mouseParam.pivot)