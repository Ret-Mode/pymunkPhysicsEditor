from ..editorTypes import Mat, ContainerTransform, BoundingBox
from .editorPhysicsI import PhysicsProp
from .editorShapeSpecI import ShapeSpec

from typing import List


class ShapeI:

    NONE = "NONE"
    POLYGON = "POLYGON"
    CIRCLE = "CIRCLE"
    BOX = "BOX"
    RECT = "RECT"
    LINE = "LINE"


    def __init__(self, label:str):

        self.box = BoundingBox()
        self.transform = ContainerTransform()

        self.type :str
        self.internal: ShapeSpec

        self.label: str = label
        
        self.physics: PhysicsProp

    # untransformed physics
    def recalcPhysics(self) -> None:
        self.physics.recalcPhysics(self.internal, self.transform)

    def updatePos(self, transform: Mat):
        self.internal.updatePos(transform)
        self.internal.getBounds(self.box)


    def draw(self):
        self.internal.draw()

    def clone(self, newLabel:str):
        pass

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['physics'] = {'hasCustomDensity' : self.physics.density.userDefined,
                           'hasCustomMass' : self.physics.mass.userDefined}

        this['physics']['customMass'] = self.physics.mass.final
        this['physics']['customDensity'] = self.physics.density.final
        this['physics']['customMoment'] = self.physics.moment.final
        this['physics']['cog'] = [self.physics.cog.final.x, self.physics.cog.final.y]

        this['type'] = self.type
        self.internal.getJSONDict(this)
        parent[self.label] = this

    @staticmethod
    def getTypes() -> List[str]:
        return [ShapeI.POLYGON, ShapeI.CIRCLE, ShapeI.BOX, ShapeI.RECT,
                    ShapeI.LINE]