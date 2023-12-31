from typing import List
from ..shapeInternals.editorBodyI import BodyI
from ..editorTypes import UserSettableFloat
from ..shapeBuffer import ShapeBuffer

class ConstraintI:

    NONE = "NONE"
    DAMPEDROTARYSPRING = "Rotary Spring"
    DAMPEDSPRING = "Damped Spring"
    GEARJOINT = "Gear"
    GROOVEJOINT = "Groove"
    PINJOINT = "Pin"
    PIVOTJOINT = "Pivot"
    RATCHETJOINT = "Ratchet"
    ROTARYLIMITJOINT = "Rotary Limit"
    SIMPLEMOTOR = "Motor"
    SLIDEJOINT = "Slide"

    def __init__(self, label:str):
        self.label: str = label
        self.type: str = None

        self.bodyA: BodyI = None
        self.bodyB: BodyI = None

        self.selfCollide: bool = False
        self.maxForce: float = float("inf")
        self.maxBias:float = float("inf")
        self.errorBias:float = pow(0.9, 60)

    def updateBodies(self):
        if self.bodyA and self.bodyB:
            self.bodyA.updatePos(self.bodyA.transform.getMat())
            self.bodyA.recalcPhysics()
            self.bodyB.updatePos(self.bodyB.transform.getMat())
            self.bodyB.recalcPhysics()

    def updateInternals(self):
        pass

    def drawInternals(self):
        pass

    def drawInternalA(self):
        pass

    def drawInternalB(self):
        pass

    def bufferInternals(self, buffer:ShapeBuffer):
        pass

    def bufferInternalA(self, buffer:ShapeBuffer):
        pass

    def bufferInternalB(self, buffer:ShapeBuffer):
        pass

    def bufferBodies(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            self.bodyA.bufferData(buffer)
            self.bodyB.bufferData(buffer)

    def bufferBodyA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            self.bodyA.bufferData(buffer)

    def bufferBodyB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            self.bodyB.bufferData(buffer)

    def getJSONDict(self, parent:dict):
        raise NotImplementedError
    
    def clone(self, source:"ConstraintI") -> "ConstraintI":
        raise NotImplementedError

    @staticmethod
    def getTypes() -> List[str]:
        return [ConstraintI.DAMPEDROTARYSPRING, ConstraintI.DAMPEDSPRING, ConstraintI.GEARJOINT,
                ConstraintI.GROOVEJOINT, ConstraintI.PINJOINT, ConstraintI.PIVOTJOINT, 
                ConstraintI.RATCHETJOINT, ConstraintI.ROTARYLIMITJOINT, ConstraintI.SIMPLEMOTOR,
                ConstraintI.SLIDEJOINT]