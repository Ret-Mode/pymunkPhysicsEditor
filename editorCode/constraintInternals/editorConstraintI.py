from typing import List
from ..shapeInternals.editorBodyI import BodyI
from ..editorTypes import UserSettableFloat
from ..bufferContainer import BufferContainer

class ConstraintI:

    NONE = "NONE"
    DAMPEDROTARYSPRING = "DAMPEDROTARYSPRING"
    DAMPEDSPRING = "DAMPEDSPRING"
    GEARJOINT = "GEARJOINT"
    GROOVEJOINT = "GROOVEJOINT"
    PINJOINT = "PINJOINT"
    PIVOTJOINT = "PIVOTJOINT"
    RATCHETJOINT = "RATCHETJOINT"
    ROTARYLIMITJOINT = "ROTARYLIMITJOINT"
    SIMPLEMOTOR = "SIMPLEMOTOR"
    SLIDEJOINT = "SLIDEJOINT"

    def __init__(self, label:str):
        self.label: str = label
        self.type: str = None

        self.bodyA: BodyI = None
        self.bodyB: BodyI = None

        self.collideBodies: bool = False
        self.max_force: float = 1.0

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

    def bufferInternals(self, buffer:BufferContainer):
        pass

    def bufferInternalA(self, buffer:BufferContainer):
        pass

    def bufferInternalB(self, buffer:BufferContainer):
        pass

    def bufferBodies(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            self.bodyA.bufferData(buffer)
            self.bodyB.bufferData(buffer)

    def bufferBodyA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            self.bodyA.bufferData(buffer)

    def bufferBodyB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            self.bodyB.bufferData(buffer)

    @staticmethod
    def getTypes() -> List[str]:
        return [ConstraintI.DAMPEDROTARYSPRING, ConstraintI.DAMPEDSPRING, ConstraintI.GEARJOINT,
                ConstraintI.GROOVEJOINT, ConstraintI.PINJOINT, ConstraintI.PIVOTJOINT, 
                ConstraintI.RATCHETJOINT, ConstraintI.ROTARYLIMITJOINT, ConstraintI.SIMPLEMOTOR,
                ConstraintI.SLIDEJOINT]