from ..editorTypes import UnboundAngle, OffsetPoint
from ..shapeBuffer import ShapeBuffer

from .editorConstraintI import ConstraintI


class DampedRotarySpring(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.DAMPEDROTARYSPRING

        self.restAngle: UnboundAngle = UnboundAngle(0.0)
        self.stiffness: float = 0.5
        self.damping: float = 0.5

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.restAngle.cos, self.restAngle.sin)

    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)

    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.restAngle.cos, self.restAngle.sin)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['restAngle'] = self.restAngle.angle
        this['stiffness'] = self.stiffness
        this['damping'] = self.damping
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this

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

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addSpring(self.anchorA.final, self.anchorB.final, self.restLength)

    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)

    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)
            
    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['restLength'] = self.restLength
        this['stiffness'] = self.stiffness
        this['damping'] = self.damping
        this['anchorA'] = [self.anchorA.final.x, self.anchorA.final.y]
        this['anchorB'] = [self.anchorB.final.x, self.anchorB.final.y]
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this
    

class GearJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.GEARJOINT

        self.phase: UnboundAngle = UnboundAngle(0.0)
        self.ratio: float = 1.0

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            buffer.addAngleRatioArm(self.bodyB.physics.cog.final, 
                              self.phase.cos, self.phase.sin, self.ratio)
            
    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)

    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            buffer.addAngleRatioArm(self.bodyB.physics.cog.final, 
                              self.phase.cos, self.phase.sin, self.ratio)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['phase'] = self.phase.angle
        this['ratio'] = self.ratio
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this
    

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

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addGroove(self.grooveA.final, self.grooveB.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addCapsule(self.grooveA.final, self.grooveB.final, self.anchorB.final.distV(self.bodyB.physics.cog.final))

    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addGroove(self.grooveA.final, self.grooveB.final)
            buffer.addCapsule(self.grooveA.final, self.grooveB.final, self.anchorB.final.distV(self.bodyB.physics.cog.final))
    
    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)
      
    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['grooveA'] = [self.grooveA.final.x, self.grooveA.final.y]
        this['grooveB'] = [self.grooveB.final.x, self.grooveB.final.y]
        this['anchorB'] = [self.anchorB.final.x, self.anchorB.final.y]
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this


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

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addGroove(self.anchorA.final, self.anchorB.final)
            
    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)

    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['anchorA'] = [self.anchorA.final.x, self.anchorA.final.y]
        this['anchorB'] = [self.anchorB.final.x, self.anchorB.final.y]
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this
    

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

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addPivot(self.anchorA.final, self.anchorB.final)
            
    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)

    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['anchorA'] = [self.anchorA.final.x, self.anchorA.final.y]
        this['anchorB'] = [self.anchorB.final.x, self.anchorB.final.y]
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this


class RatchetJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.RATCHETJOINT

        self.phase: UnboundAngle = UnboundAngle(0.5)
        self.ratchet: UnboundAngle = UnboundAngle(0.5)

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            buffer.addRatchetA(self.bodyA.physics.cog.final, self.ratchet)
            buffer.addRatchetB(self.bodyB.physics.cog.final, self.phase, self.ratchet)
            
    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyA.physics.cog.final, 1.0, 0.0)
            buffer.addRatchetA(self.bodyA.physics.cog.final, self.ratchet)

    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAngleArm(self.bodyB.physics.cog.final, 
                         self.phase.cos, self.phase.sin)
            buffer.addRatchetB(self.bodyB.physics.cog.final, self.phase, self.ratchet)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['phase'] = self.phase.angle
        this['ratchet'] = self.ratchet.angle
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this


class RotaryLimitJoint(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.ROTARYLIMITJOINT

        self.min: UnboundAngle = UnboundAngle(0.2)
        self.max: UnboundAngle = UnboundAngle(0.5)

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addPhaseMinMaxA(self.bodyA.physics.cog.final, self.min, self.max)
            buffer.addPhaseMinMaxB(self.bodyB.physics.cog.final, self.min, self.max)
            
    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addPhaseMinMaxA(self.bodyA.physics.cog.final, self.min, self.max)

    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addPhaseMinMaxB(self.bodyB.physics.cog.final, self.min, self.max)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['min'] = self.min.angle
        this['max'] = self.max.angle
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this
    

class SimpleMotor(ConstraintI):

    def __init__(self, label:str):
        super().__init__(label)
        self.type = ConstraintI.SIMPLEMOTOR

        self.rate: UnboundAngle = UnboundAngle(1.0)

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addRateA(self.bodyA.physics.cog.final, self.rate)
            buffer.addRateB(self.bodyB.physics.cog.final, self.rate)
            
    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addRateA(self.bodyA.physics.cog.final, self.rate)

    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addRateB(self.bodyB.physics.cog.final, self.rate)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['rate'] = self.rate.angle
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this
    

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

    def bufferInternals(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)
            buffer.addAnchor(self.anchorB.final)
            buffer.addSlide(self.anchorA.final, self.anchorB.final, self.min, self.max)
            
    def bufferInternalA(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorA.final)

    def bufferInternalB(self, buffer:ShapeBuffer):
        if self.bodyA and self.bodyB:
            buffer.addAnchor(self.anchorB.final)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['maxBias'] = self.maxBias
        this['maxForce'] = self.maxForce
        this['errorBias'] = self.errorBias
        this['selfCollide'] = self.selfCollide
        this['min'] = self.min
        this['max'] = self.max
        this['type'] = self.type
        this['bodyA'] = self.bodyA.label
        this['bodyB'] = self.bodyB.label
        parent[self.label] = this