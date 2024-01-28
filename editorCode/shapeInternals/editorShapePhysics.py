from ..editorTypes import ContainerTransform, EditorPoint
from .editorPhysicsI import PhysicsProp
from .editorShapeSpecI import ShapeSpec
from .editorShapeSpec import RectSpec, BoxSpec

import math


class ShapePhysics(PhysicsProp):

    def __init__(self):
        super().__init__()

    def recalcPhysics(self, internal: ShapeSpec, transform:ContainerTransform):
        self.recalcArea(internal)
        
        if self.cog.userDefined:
            transform.getMat().mulV(self.cog.user, self.cog.final)
        else:
            self.cog.final.setFromV(self.cog.calc)

        if self.density.userDefined:
            self.density.final = self.density.user
        else:
            self.density.final = 1.0

        if self.mass.userDefined:
            self.mass.final = self.mass.user * transform.objectScale * transform.objectScale
        else:
            self.mass.final = self.density.final * self.area

        self.recalcMoment(internal)

        if self.moment.userDefined:
            # recalc moment if there's user center of gravity
            self.moment.final = self.moment.user * (transform.objectScale**4) # * transform.objectScale * transform.objectScale * transform.objectScale
        else:
            self.moment.final = self.moment.calc

    def recalcArea(self, internal):
        raise NotImplementedError
    
    def recalcMoment(self, internal):
        raise NotImplementedError


class PolygonPhysics(ShapePhysics):

    def __init__(self):
        super().__init__()

    def recalcMoment(self, internal: ShapeSpec):
        points = internal.points
        pointsNumber: int = len(points)
        mass = self.mass.final
        radius = internal.radius.get()
        if pointsNumber == 1:
            self.moment.calc = mass * (radius * radius) / 2
            return
        elif pointsNumber == 2:
            point = points[1]
            prevPoint = points[0]
            length = point.final.distV(prevPoint.final) + 2 * radius
            offsetSqr = self.cog.final.distSqrXY((point.final.x + prevPoint.final.x) / 2.0, (point.final.y + prevPoint.final.y) / 2.0)
            self.moment.calc = mass * ((4 * radius * radius + length * length) / 12.0 + offsetSqr)
            return
        elif pointsNumber > 2:
            prevPoint = points[-1]
            m2 = 0.0
            m1 = 0.0
            for point in points:
                cross = prevPoint.final.crossV(point.final)
                m1 += (cross * (prevPoint.final.dotV(prevPoint.final) + prevPoint.final.dotV(point.final) + point.final.dotV(point.final)))
                m2 += cross
                prevPoint = point
            self.moment.calc = (self.mass.final * (m1 / (6.0 * m2) - self.cog.final.lengthSqr()))
            return
        self.moment.calc = 1.0
        
    def recalcArea(self, internal: ShapeSpec):
        points = internal.points
        radius = internal.radius.get()
        pointsNumber: int = len(points)
        if pointsNumber == 0:
            self.cog.calc.setFromXY(0.0, 0.0)
            self.area = 1.0
            return
        elif pointsNumber == 1:
            self.cog.calc.setFromV(points[0].final)
            self.area = math.pi * radius * radius
            return
        elif pointsNumber == 2:
            calc = self.cog.calc.setFromV(points[1].final).unTV(points[0].final)
            lineArea = calc.length() * 2 * radius
            calc.sS(0.5).tV(points[0].final)
            self.area = lineArea + math.pi * radius * radius
            return
        
        radArea: float = 0.0
        prevPoint: EditorPoint = points[-1]
        areaSum: float = 0.0
        areaPrev: float = 0.0
        self.cog.calc.setFromXY(0.0, 0.0)
        for point in points:
            areaCurrent = point.final.crossV(prevPoint.final)
            radArea += point.final.distV(prevPoint.final)
            if areaCurrent != 0.0:
                areaPrev = areaSum
                areaSum += areaCurrent
                if areaSum != 0.0:
                    self.cog.calc.sS(areaPrev/areaCurrent).sS(3.0).tV(prevPoint.final).tV(point.final).sS(1.0/3.0).sS(areaCurrent/(areaSum))
            prevPoint = point
        self.area = (radArea * radius) + math.pi * radius * radius + areaSum / 2.0


class CirclePhysics(ShapePhysics):

    def __init__(self):
        super().__init__()

    def recalcMoment(self, internal: ShapeSpec):
        radius = internal.radius.get()
        offset = self.cog.final.distSqrV(internal.points[0].final)
        self.moment.calc = self.mass.final * (offset + radius * radius / 2.0)

    def recalcArea(self, internal:ShapeSpec):
        radius = internal.radius.get()
        self.cog.calc.setFromV(internal.points[0].final)
        self.area = math.pi * radius * radius


class BoxPhysics(ShapePhysics):

    def __init__(self):
        super().__init__()

    def recalcMoment(self, internal: BoxSpec):
        radius = 0.0 #internal.radius.final                              # chipmunk ignores radius in moment calculations
        edge = internal.halfWH.final.length() * math.sqrt(2.0) + 2 * radius
        self.moment.calc = self.mass.final * (2 * ((edge)**2)) / 12.0

    def recalcArea(self,internal: BoxSpec):
        point = internal.halfWH.final
        
        radius = internal.radius.get()
        self.cog.calc.setFromV(internal.points[0].final)
        a = point.length() * math.sqrt(2.0)
        self.area = a * a + 4 * a * radius + math.pi * radius * radius


class RectPhysics(ShapePhysics):

    def __init__(self):
        super().__init__()

    def recalcMoment(self, internal: RectSpec):
        point = internal.halfWH.final
        radius = 0.0 #internal.radius.final
        # chipmunk ignores radius in moment calculations
        x = 2 * (point.x + radius)
        y = 2 * (point.y + radius)
        self.moment.calc = self.mass.final * ((x)**2 + (y)**2) / 12.0

    def recalcArea(self, internal: RectSpec):
        point = internal.halfWH.final
        radius = internal.radius.get()
        self.cog.calc.setFromV(internal.points[0].final)
        point.x * point.y
        self.area = point.x * point.y * 4 + (point.x + point.y) * 4 * radius + math.pi * radius * radius


class LinePhysics(ShapePhysics):

    def __init__(self):
        super().__init__()

    def recalcMoment(self, internal: ShapeSpec):
        points = internal.points
        radius = internal.radius.get()
        pointsNumber: int = len(points)
        # TODO correct mass to fragment of mass per line
        mass = self.mass.final
        if pointsNumber == 1:
            self.moment.calc = mass * (radius * radius) / 2
            return
        elif pointsNumber > 1:
            prevPoint = points[0]
            moment = 0.0
            for point in points[1:]:
                areaProportion = (point.final.distV(prevPoint.final) * 2 * radius + math.pi * radius * radius) / self.area
                length = point.final.distV(prevPoint.final) + 2 * radius
                offsetSqr = self.cog.final.distSqrXY((point.final.x + prevPoint.final.x) / 2.0, (point.final.y + prevPoint.final.y) / 2.0)
                moment += areaProportion * mass * ((4 * radius * radius + length * length) / 12.0 + offsetSqr)
                prevPoint = point
            self.moment.calc = moment
            return
        self.moment.calc = 1.0

    def recalcArea(self, internal: ShapeSpec):
        points = internal.points
        radius = internal.radius.get()
        pointsNumber: int = len(points)
        if pointsNumber == 0:
            self.cog.calc.setFromXY(0.0, 0.0)
            self.area = 1.0
            return
        elif pointsNumber == 1:
            self.cog.calc.setFromV(points[0].final)
            self.area = math.pi * radius * radius
            return
        
        prevPoint: "EditorPoint" = points[0]
        areaSum: float = 0.0
        areaPrev: float = 0.0

        self.cog.calc.setFromXY(0.0, 0.0)
        for point in points[1:]:
            areaCurrent = point.final.distV(prevPoint.final) * 2 * radius + math.pi * radius * radius
            if areaCurrent != 0.0:
                areaPrev = areaSum
                areaSum += areaCurrent
                self.cog.calc.sS(areaPrev/areaCurrent).sS(2.0).tV(point.final).tV(prevPoint.final).sS(0.5).sS(areaCurrent/(areaSum))
            prevPoint = point
        self.area = areaSum