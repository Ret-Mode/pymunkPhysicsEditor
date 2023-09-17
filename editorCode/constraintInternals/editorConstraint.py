from ..editorTypes import UnboundAngle, OffsetPoint
from ..bufferContainer import BufferContainer
from ..drawing import drawAnchor, drawGroove, drawAngleArm, drawSpring, drawAngleRatioArm, drawCapsule, drawPivot
from ..drawing import drawRatchetA, drawRatchetB, drawPhaseMinMaxA, drawPhaseMinMaxB, drawRateA, drawRateB, drawSlide

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

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.restAngle.cos, self.restAngle.sin)

    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)

    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
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

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addSpring(self.anchorA.final, self.anchorB.final, self.restLength)

    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)

    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)
            

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

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            buffer.addAngleRatioArm(self.bodyB.physics.cog.final, 
                              self.phase.cos, self.phase.sin, self.ratio)
            
    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)

    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            buffer.addAngleRatioArm(self.bodyB.physics.cog.final, 
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

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addGroove(self.grooveA.final, self.grooveB.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addCapsule(self.grooveA.final, self.grooveB.final, self.anchorB.final.distV(self.bodyB.physics.cog.final))

    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addGroove(self.grooveA.final, self.grooveB.final)
            buffer.addCapsule(self.grooveA.final, self.grooveB.final, self.anchorB.final.distV(self.bodyB.physics.cog.final))
    
    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)
      
            

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

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addGroove(self.anchorA.final, self.anchorB.final)
            
    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)

    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)


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

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addPivot(self.anchorA.final, self.anchorB.final)
            
    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)

    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)


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

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            buffer.addRatchetA(self.bodyA.physics.cog.final, self.ratchet)
            buffer.addRatchetB(self.bodyB.physics.cog.final, self.phase, self.ratchet)
            
    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            buffer.addRatchetA(self.bodyA.physics.cog.final, self.ratchet)

    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            buffer.addRatchetB(self.bodyB.physics.cog.final, self.phase, self.ratchet)


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

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addPhaseMinMaxA(self.bodyA.physics.cog.final, self.min, self.max)
            buffer.addPhaseMinMaxB(self.bodyB.physics.cog.final, self.min, self.max)
            
    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addPhaseMinMaxA(self.bodyA.physics.cog.final, self.min, self.max)

    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addPhaseMinMaxB(self.bodyB.physics.cog.final, self.min, self.max)


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

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addRateA(self.bodyA.physics.cog.final, self.rate)
            buffer.addRateB(self.bodyB.physics.cog.final, self.rate)
            
    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addRateA(self.bodyA.physics.cog.final, self.rate)

    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addRateB(self.bodyB.physics.cog.final, self.rate)


class SlideJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.SLIDEJOINT

        self.anchorA: OffsetPoint = OffsetPoint()
        self.anchorB: OffsetPoint = OffsetPoint()
        self.min: float = 1.0
        self.max: float = 2.0

    def updateInternals(self):
        if self.bodyA and self.bodyB:
            self.anchorA.calcOffset(self.bodyA.transform.getMat(), self.bodyA.physics.cog.final)
            self.anchorB.calcOffset(self.bodyB.transform.getMat(), self.bodyB.physics.cog.final)

    def drawInternals(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorA.final)
            drawAnchor(self.anchorB.final)
            drawSlide(self.anchorA.final, self.anchorB.final, self.min, self.max)

    def drawInternalA(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorA.final)
    
    def drawInternalB(self):
        if self.bodyA and self.bodyB:
            drawAnchor(self.anchorB.final)

    def bufferInternals(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addSlide(self.anchorA.final, self.anchorB.final, self.min, self.max)
            
    def bufferInternalA(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)

    def bufferInternalB(self, buffer:BufferContainer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)