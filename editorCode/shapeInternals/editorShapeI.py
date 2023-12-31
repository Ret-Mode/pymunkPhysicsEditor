from ..editorTypes import Mat, ContainerTransform, BoundingBox
from ..shapeBuffer import ShapeBuffer
from .editorPhysicsI import PhysicsProp
from .editorShapeSpecI import ShapeSpec

from typing import List


class ShapeI:

    NONE = "NONE"
    POLYGON = "Polygon"
    CIRCLE = "Circle"
    BOX = "Box"
    RECT = "Rect"
    LINE = "Line"


    def __init__(self, label:str):

        self.box = BoundingBox()
        self.transform = ContainerTransform()

        self.type :str
        self.internal: ShapeSpec

        self.label: str = label
        
        self.physics: PhysicsProp

        self.elasticity: float = 0.0
        self.friction: float = 1.0
        self.isSensor:bool = False
        self.shapeFilterGroup:int = 0
        self.shapeFilterCategory:int = 0xFFFFFFFF
        self.shapeFilterMask:int = 0xFFFFFFFF

    def setRadius(self, radius:float):
        raise NotImplementedError

    def getRadius(self) -> float:
        return self.internal.radius.get()
    
    # untransformed physics
    def recalcPhysics(self) -> None:
        self.physics.recalcPhysics(self.internal, self.transform)

    def updatePos(self, transform: Mat):
        self.internal.updatePos(transform)
        self.internal.getBounds(self.box)

    def updateEye(self):
        self.internal.updatePos(Mat.Eye())
        self.internal.getBounds(self.box)

    def draw(self):
        self.internal.draw()

    def clone(self, source:"ShapeI"):
        self.box.clone(source.box)
        self.transform.clone(source.transform)
        self.internal.clone(source.internal)
        self.physics.clone(source.physics)
        self.elasticity = source.elasticity
        self.friction = source.friction
        self.isSensor = source.isSensor
        self.shapeFilterGroup = source.shapeFilterGroup
        self.shapeFilterCategory = source.shapeFilterCategory
        self.shapeFilterMask = source.shapeFilterMask

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['physics'] = {'hasCustomDensity' : self.physics.density.userDefined,
                           'hasCustomMass' : self.physics.mass.userDefined}

        this['physics']['customMass'] = self.physics.mass.final
        this['physics']['customDensity'] = self.physics.density.final
        this['physics']['customMoment'] = self.physics.moment.final
        this['physics']['cog'] = [self.physics.cog.final.x, self.physics.cog.final.y]
        this['physics']['elasticity'] = self.elasticity
        this['physics']['friction'] = self.friction
        this['physics']['isSensor'] = self.isSensor
        this['physics']['filterGroup'] = self.shapeFilterGroup
        this['physics']['filterCategory'] = self.shapeFilterCategory
        this['physics']['filterMask'] = self.shapeFilterMask


        this['type'] = self.type
        self.internal.getJSONDict(this)
        parent[self.label] = this

    def bufferData(self, buffer:ShapeBuffer):
        raise NotImplementedError

    @staticmethod
    def getTypes() -> List[str]:
        return [ShapeI.POLYGON, ShapeI.CIRCLE, ShapeI.BOX, ShapeI.RECT,
                    ShapeI.LINE]