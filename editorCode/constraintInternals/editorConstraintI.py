from typing import List
from ..shapeInternals.editorBodyI import BodyI
from ..editorTypes import UserSettableFloat

from ..drawing import drawBody

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

    def drawBodies(self):
        if self.bodyA and self.bodyB:
            drawBody(self.bodyA, True, False)
            drawBody(self.bodyB, True, False)

    def drawBodyA(self):
        if self.bodyA and self.bodyB:
            drawBody(self.bodyA, True, False)
    
    def drawBodyB(self):
        if self.bodyA and self.bodyB:
            drawBody(self.bodyB, True, False)

    @staticmethod
    def getTypes() -> List[str]:
        return [ConstraintI.DAMPEDROTARYSPRING, ConstraintI.DAMPEDSPRING, ConstraintI.GEARJOINT,
                ConstraintI.GROOVEJOINT, ConstraintI.PINJOINT, ConstraintI.PIVOTJOINT, 
                ConstraintI.RATCHETJOINT, ConstraintI.ROTARYLIMITJOINT, ConstraintI.SIMPLEMOTOR,
                ConstraintI.SLIDEJOINT]