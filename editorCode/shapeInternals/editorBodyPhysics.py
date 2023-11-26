from ..editorTypes import ContainerTransform
from ..config import physicsSetup
from .editorPhysicsI import PhysicsProp
from .editorShapeI import ShapeI

from typing import List


class BodyPhysics(PhysicsProp):

    def __init__(self):
        super().__init__()

    def recalcPhysics(self, internal: List[ShapeI], transform:ContainerTransform):
        self.recalcArea(internal)
        
        if self.cog.userDefined:
            transform.getMat().mulV(self.cog.user, self.cog.final)
        else:
            self.cog.final.setFromV(self.cog.calc)

        # TODO fix mass settings - for body it seems that only mass 
        # should be set by user
        if self.density.userDefined:
            self.density.final = self.density.user
            if self.mass.userDefined:
                self.mass.final = self.mass.user * self.density.final
            else:
                self.mass.final = self.mass.calc * self.density.final
        else:
            self.density.final = 1.0
            if self.mass.userDefined:
                self.mass.final = self.mass.user
            else:
                self.mass.final = self.mass.calc

        self.recalcMoment(internal)

        if self.moment.userDefined:
            # recalc moment if there's user center of gravity
            self.moment.final = self.moment.user * (transform.objectScale ** 4)
        else:
            self.moment.final = self.moment.calc

    def recalcMoment(self, internal: List[ShapeI]):
        cog = self.cog.final
        if internal:
            moment = 0.0
            for shape in internal:
                mass = shape.physics.mass.final
                cogShape = shape.physics.cog.final
                moment += shape.physics.moment.final + mass * (cog.distV(cogShape) ** 2)
            self.moment.calc = moment
            return
        self.moment.calc = 1.0

    def recalcArea(self, internal: List[ShapeI]):
        cummulativeMass = 0.0
        cummulativeArea = 0.0
        self.cog.calc.setFromXY(0.0, 0.0)
        if internal:
            prevMass = 0.0
            for shape in internal:
                shape.physics.recalcPhysics(shape.internal, shape.transform)
                area = shape.physics.area
                mass = shape.physics.mass.final
                prevMass = cummulativeMass
                cummulativeMass += mass
                cummulativeArea += area
                if mass:
                    self.cog.calc.sS(prevMass/mass).tV(shape.physics.cog.final).sS(mass/cummulativeMass)
            self.area = cummulativeArea
            self.mass.calc = cummulativeMass
            if self.area != 0.0:
                self.density.calc = self.mass.calc / self.area


class BodyStaticPhysics(PhysicsProp):

    def __init__(self):
        super().__init__()

    # TODO
    def recalcPhysics(self, internal: List[ShapeI], transform:ContainerTransform):
        self.recalcArea(internal)
        
        if self.cog.userDefined:
            transform.getMat().mulV(self.cog.user, self.cog.final)
        else:
            self.cog.final.setFromV(self.cog.calc)

        if self.density.userDefined:
            self.density.final = self.density.user
            if self.mass.userDefined:
                self.mass.final = self.mass.user * self.density.final
            else:
                self.mass.final = self.mass.calc * self.density.final
        else:
            self.density.final = 1.0
            if self.mass.userDefined:
                self.mass.final = self.mass.user
            else:
                self.mass.final = self.mass.calc

        self.recalcMoment(internal)

        if self.moment.userDefined:
            # recalc moment if there's user center of gravity
            self.moment.final = self.moment.user * (transform.objectScale ** 4)
        else:
            self.moment.final = self.moment.calc

    # TODO
    def recalcMoment(self, internal: List[ShapeI]):
        cog = self.cog.final
        if internal:
            moment = 0.0
            for shape in internal:
                mass = shape.physics.mass.final
                cogShape = shape.physics.cog.final
                moment += shape.physics.moment.final + mass * (cog.distV(cogShape) ** 2)
            self.moment.calc = moment
            return
        self.moment.calc = 1.0

    # TODO
    def recalcArea(self, internal: List[ShapeI]):
        cummulativeMass = 0.0
        cummulativeArea = 0.0
        self.cog.calc.setFromXY(0.0, 0.0)
        if internal:
            prevMass = 0.0
            for shape in internal:
                shape.physics.recalcPhysics(shape.internal, shape.transform)
                area = shape.physics.area
                mass = shape.physics.mass.final
                prevMass = cummulativeMass
                cummulativeMass += mass
                cummulativeArea += area
                if mass:
                    self.cog.calc.sS(prevMass/mass).tV(shape.physics.cog.final).sS(mass/cummulativeMass)
            self.area = cummulativeArea
            self.mass.calc = cummulativeMass
            if self.area != 0.0:
                self.density.calc = self.mass.calc / self.area
    