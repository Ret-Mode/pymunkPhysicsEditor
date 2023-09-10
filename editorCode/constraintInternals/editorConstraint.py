from ..editorTypes import EditorPoint, Angle, UnboundAngle, OffsetPoint
from ..drawing import drawAnchor, drawGroove, drawAngleArm, drawSpring, drawAngleRatioArm, drawCapsule, drawPivot
from ..drawing import drawRatchetA, drawRatchetB, drawPhaseMinMaxA, drawPhaseMinMaxB, drawRateA, drawRateB

from .editorConstraintI import ConstraintI


class DampedRotarySpring(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.DAMPEDROTARYSPRING

        self.restAngle: UnboundAngle = UnboundAngle(0.0)
        self.stiffness: float = 0.5
        self.damping: float = 0.5

    def drawInternals(self):
        if self.bodyA and self.bodyB:
            drawAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            drawAngleArm(self.bodyB.physics.cog.final, 
                         self.restAngle.cos, self.restAngle.sin)

    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawAngleArm(self.bodyB.physics.cog.final, 
                         self.restAngle.cos, self.restAngle.sin)

class DampedSpring(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.DAMPEDSPRING

        self.restLength: float = 0.5
        self.stiffness: float = 0.5
        self.damping: float = 0.5
        self.anchorA: OffsetPoint = OffsetPoint()
        self.anchorB: OffsetPoint = OffsetPoint()

    def updateInternals(self):
        if self.bodyA and self.bodyB:
            self.anchorA.calcOffset(self.bodyA.transform.getMat(), self.bodyA.physics.cog.final)
            self.anchorB.calcOffset(self.bodyB.transform.getMat(), self.bodyB.physics.cog.final)

    def drawInternals(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorA.final)
            drawAnchor(self.anchorB.final)
            drawSpring(self.anchorA.final, self.anchorB.final, self.restLength)

    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorA.final)
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorB.final)
        

class GearJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.GEARJOINT

        self.phase: UnboundAngle = UnboundAngle(0.0)
        self.ratio: float = 1.0

    def drawInternals(self):
        if self.bodyA and self.bodyB: 
            drawAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            drawAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            drawAngleRatioArm(self.bodyB.physics.cog.final, 
                              self.phase.cos, self.phase.sin, self.ratio)

    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            drawAngleRatioArm(self.bodyB.physics.cog.final, 
                              self.phase.cos, self.phase.sin, self.ratio)


class GrooveJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.GROOVEJOINT

        self.grooveA: OffsetPoint = OffsetPoint()
        self.grooveB: OffsetPoint = OffsetPoint()
        self.anchorB: OffsetPoint = OffsetPoint()

    def updateInternals(self):
        if self.bodyA and self.bodyB:
            mat = self.bodyA.transform.getMat()
            cog = self.bodyA.physics.cog.final
            self.grooveA.calcOffset(mat, cog)
            self.grooveB.calcOffset(mat, cog) 
            self.anchorB.calcOffset(self.bodyB.transform.getMat(), self.bodyB.physics.cog.final)

    def drawInternals(self):
        if self.bodyA and self.bodyB:
            drawGroove(self.grooveA.final, self.grooveB.final)
            drawAnchor(self.anchorB.final)
            drawCapsule(self.grooveA.final, self.grooveB.final, self.anchorB.final.distV(self.bodyB.physics.cog.final))

    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawGroove(self.grooveA.final, self.grooveB.final)
            drawCapsule(self.grooveA.final, self.grooveB.final, self.anchorB.final.distV(self.bodyB.physics.cog.final))
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorB.final)


class PinJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.PINJOINT

        self.anchorA: OffsetPoint = OffsetPoint()
        self.anchorB: OffsetPoint = OffsetPoint()

    def updateInternals(self):
        if self.bodyA and self.bodyB:
            self.anchorA.calcOffset(self.bodyA.transform.getMat(), self.bodyA.physics.cog.final)
            self.anchorB.calcOffset(self.bodyB.transform.getMat(), self.bodyB.physics.cog.final)

    def drawInternals(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorA.final)
            drawAnchor(self.anchorB.final)
            drawGroove(self.anchorA.final, self.anchorB.final)

    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorA.final)
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorB.final)


class PivotJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.PIVOTJOINT

        self.anchorA: OffsetPoint = OffsetPoint()
        self.anchorB: OffsetPoint = OffsetPoint()

    def updateInternals(self):
        if self.bodyA and self.bodyB:
            self.anchorA.calcOffset(self.bodyA.transform.getMat(), self.bodyA.physics.cog.final)
            self.anchorB.calcOffset(self.bodyB.transform.getMat(), self.bodyB.physics.cog.final)

    def drawInternals(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorA.final)
            drawAnchor(self.anchorB.final)
            drawPivot(self.anchorA.final, self.anchorB.final)


    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorA.final)
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorB.final)


class RatchetJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.RATCHETJOINT

        self.phase: UnboundAngle = UnboundAngle(0.5)
        self.ratchet: UnboundAngle = UnboundAngle(0.5)

    def drawInternals(self):
        if self.bodyA and self.bodyB: 
            drawAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            drawAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            drawRatchetA(self.bodyA.physics.cog.final, self.ratchet)
            drawRatchetB(self.bodyB.physics.cog.final, self.phase, self.ratchet)

    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            drawRatchetA(self.bodyA.physics.cog.final, self.ratchet)
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            drawRatchetB(self.bodyB.physics.cog.final, self.phase, self.ratchet)


class RotaryLimitJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.ROTARYLIMITJOINT

        self.min: UnboundAngle = UnboundAngle(0.2)
        self.max: UnboundAngle = UnboundAngle(0.5)

    def drawInternals(self):
        if self.bodyA and self.bodyB: 
            drawPhaseMinMaxA(self.bodyA.physics.cog.final, self.min, self.max)
            drawPhaseMinMaxB(self.bodyB.physics.cog.final, self.min, self.max)

    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawPhaseMinMaxA(self.bodyA.physics.cog.final, self.min, self.max)
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawPhaseMinMaxB(self.bodyB.physics.cog.final, self.min, self.max)

class SimpleMotor(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.SIMPLEMOTOR

        self.rate: UnboundAngle = UnboundAngle(1.0)

    def drawInternals(self):
        if self.bodyA and self.bodyB: 
            drawRateA(self.bodyA.physics.cog.final, self.rate)
            drawRateB(self.bodyB.physics.cog.final, self.rate)

    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawRateA(self.bodyA.physics.cog.final, self.rate)
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawRateB(self.bodyB.physics.cog.final, self.rate)

class SlideJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.SLIDEJOINT

        self.anchorA: OffsetPoint = OffsetPoint()
        self.anchorB: OffsetPoint = OffsetPoint()
        self.min: float = 1.0
        self.max: float = 2.0

    def updateInternals(self):
        if self.bodyA:
            self.anchorA.calcOffset(self.bodyA.transform.getMat(), self.bodyA.physics.cog.final)
        if self.bodyB:
            self.anchorB.calcOffset(self.bodyB.transform.getMat(), self.bodyB.physics.cog.final)

    def drawInternals(self):
        drawAnchor(self.anchorA.final)
        drawAnchor(self.anchorB.final)

    def drawInternalA(self):
        drawAnchor(self.anchorA.final)
    
    def drawInternalB(self):
        drawAnchor(self.anchorB.final)