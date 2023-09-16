from ..editorTypes import V2, Mat, Radius, EditorPoint, BoundingBox
from .editorShapeSpecI import ShapeSpec

from ..drawing import drawPolygon, drawCircle, drawBox, drawRect, drawLineShape

from typing import List, Optional, Tuple


class PolygonSpec(ShapeSpec):

    def __init__(self):
        # TODO correct all shapes internals - points to hold geometry only
        self.points: List[EditorPoint] = []
        self.currentPoint: Optional[EditorPoint] = None
        self.radius: Radius = Radius(1.0)

    def getJSONDict(self, parent:dict):
        points = []
        for point in self.points:
            points.append([point.final.x, point.final.y])
        this = {'points' : points,
                'radius' : self.radius.final}
        parent['internal'] = this
    
    def draw(self):
        drawPolygon(self.points)

    def addPoint(self, point:EditorPoint):
        if point not in self.points:
            self.points.append(point)

    def deletePoint(self, point:EditorPoint):
        if point in self.points:
            self.points.remove(point)

    def updatePos(self, final: Mat):
        for point in self.points:
            final.mulV(point.local, point.final)

    def getBounds(self, box: BoundingBox) -> Tuple[float]:
        if self.points:
            xs = [p.final.x for p in self.points]
            ys = [p.final.y for p in self.points]
            xMin = min(xs)
            xMax = max(xs)
            yMin = min(ys)
            yMax = max(ys)
            box.setFinal(xMin, yMin, xMax, yMax)
            return
        box.setFinal(0.0, 0.0, 0.0, 0.0)


class CircleSpec(ShapeSpec):

    def __init__(self):
        self.points: List[EditorPoint] = [EditorPoint(0.0, 0.0), EditorPoint(1.0, 0.0)]
        self.center: EditorPoint = EditorPoint(0.0, 0.0)
        # this is basically radius
        self.halfWH: EditorPoint = EditorPoint(0.0, 0.0)
        #user radius, unusable on circles
        self.radius: Radius = Radius(0.0)
        self.drawLines: int = 32

    def getJSONDict(self, parent:dict):
        center = self.points[0]
        halfWH = self.points[1]
        this = {'offset' : [center.final.x, center.final.y],
                'radius' : halfWH.final.length()}
        parent['internal'] = this

    def draw(self):
        center = self.points[0]
        halfWH = self.points[1]
        drawCircle(center.final, halfWH.final, self.drawLines)

    def addPoint(self, point:EditorPoint):
        assert False

    def resetWH(self, point:EditorPoint):
        center = self.points[0]
        halfWH = self.points[1]
        halfWH.local.setFromV(point.local).unTV(center.local)
        length = halfWH.local.length()
        halfWH.local.setFromXY(length, 0.0)

    def setWH(self, point:EditorPoint):
        halfWH = self.points[1]
        halfWH.local.setFromV(point.local)
        length = halfWH.local.length()
        halfWH.local.setFromXY(length, 0.0)

    def deletePoint(self, point:EditorPoint):
        pass

    def updatePos(self, final: Mat):
        center = self.points[0]
        halfWH = self.points[1]
        final.mulV(center.local, center.final)
        final.mulV(halfWH.local, halfWH.final).unTV(center.final)

    def getBounds(self, box: BoundingBox) -> Tuple[float]:
        center = self.points[0]
        halfWH = self.points[1]
        length = halfWH.final.length()
        box.setFinal(center.final.x - length, center.final.y - length, center.final.x + length, center.final.y + length)


class BoxSpec(ShapeSpec):

    def __init__(self):
        self.points: List[EditorPoint] = [EditorPoint(0.0, 0.0), EditorPoint(0.0, 0.0), EditorPoint(0.0, 0.0), EditorPoint(0.0, 0.0), EditorPoint(0.0, 0.0)]
        # TODO Cleanup halfWH use
        self.halfWH: EditorPoint = EditorPoint(1.0, 1.0)
        self.radius: Radius = Radius(1.0)
        self._setVerts()

    def _setVerts(self):
        center = self.points[0]
        self.points[1].final.setFromXY(center.final.x + self.halfWH.final.x, center.final.y + self.halfWH.final.y)
        self.points[2].final.setFromXY(center.final.x + self.halfWH.final.y, center.final.y - self.halfWH.final.x)
        self.points[3].final.setFromXY(center.final.x - self.halfWH.final.x, center.final.y - self.halfWH.final.y)
        self.points[4].final.setFromXY(center.final.x - self.halfWH.final.y, center.final.y + self.halfWH.final.x)

    def getJSONDict(self, parent:dict):
        center = self.points[0]
        #halfWH = self.points[1]
        this = {'points' : [(self.points[1].final.x, self.points[1].final.y),
                            (self.points[2].final.x, self.points[2].final.y),
                            (self.points[3].final.x, self.points[3].final.y),
                            (self.points[4].final.x, self.points[4].final.y)
                            ],
                'radius' : self.radius.final}
        parent['internal'] = this

    def draw(self):
        drawBox(self.points)
    
    def addPoint(self, point:EditorPoint):
        assert False

    def resetWH(self, point:EditorPoint):
        center = self.points[0]
        self.halfWH.local.setFromV(point.local).unTV(center.local)
        dist = max(abs(self.halfWH.local.x), abs(self.halfWH.local.y))
        self.halfWH.local.x = dist
        self.halfWH.local.y = dist

    def setWH(self, point:EditorPoint):
        #halfWH = self.points[1]
        self.halfWH.local.setFromV(point.local)
        dist = max(abs(self.halfWH.local.x), abs(self.halfWH.local.y))
        self.halfWH.local.x = dist
        self.halfWH.local.y = dist

    def setRadiusFromFloat(self, radius:float):
        assert False

    def deletePoint(self, point:EditorPoint):
        assert False
    
    def updatePos(self, final: Mat):
        center = self.points[0]
        #halfWH = self.points[1]
        final.mulV(center.local, center.final)
        final.mulV(self.halfWH.local, self.halfWH.final)
        self.halfWH.final.unTV(center.final)
        self._setVerts()
    
    def clone(self) -> 'ShapeSpec':
        raise NotImplementedError

    def getBounds(self, box: BoundingBox) -> Tuple[float]:
        center = self.points[0]
        xMax = xMin = center.final.x
        yMax = yMin = center.final.y
        for point in self.points[1:]:
            xMax = max(xMax, point.final.x)
            xMin = min(xMin, point.final.x)
            yMax = max(yMax, point.final.y)
            yMin = min(yMin, point.final.y)
        box.setFinal(xMin, yMin, xMax, yMax)


class RectSpec(ShapeSpec):

    def __init__(self):
        self.points: List[EditorPoint] = [EditorPoint(0.0, 0.0), EditorPoint(0.0, 0.0), EditorPoint(0.0, 0.0), EditorPoint(0.0, 0.0), EditorPoint(0.0, 0.0)]
        # TODO Cleanup halfWH use
        self.halfWH = EditorPoint(1.0, 1.0)
        self.right: V2 = V2()
        self.up: V2 = V2()
        self.radius: Radius = Radius(1.0)
        self._setVerts()

    def _setVerts(self):
        center = self.points[0]
        self.points[1].final.setFromXY(center.final.x + self.right.x + self.up.x, center.final.y + self.right.y + self.up.y)
        self.points[2].final.setFromXY(center.final.x + self.right.x - self.up.x, center.final.y + self.right.y - self.up.y)
        self.points[3].final.setFromXY(center.final.x - self.right.x - self.up.x, center.final.y - self.right.y - self.up.y)
        self.points[4].final.setFromXY(center.final.x - self.right.x + self.up.x, center.final.y - self.right.y + self.up.y)

    def getJSONDict(self, parent:dict):
        center = self.points[0]
        this = {'points' : [(self.points[1].final.x, self.points[1].final.y),
                            (self.points[2].final.x, self.points[2].final.y),
                            (self.points[3].final.x, self.points[3].final.y),
                            (self.points[4].final.x, self.points[4].final.y)
                            ],
                'radius' : self.radius.final}
        parent['internal'] = this

    def draw(self):
        center = self.points[0]
        drawRect(self.points)
    
    def addPoint(self, point:EditorPoint):
        assert False

    def updatePos(self, final: Mat):
        center = self.points[0]
        #halfWH = self.points[1]
        self.right.setFromXY(self.halfWH.local.x, 0.0)
        self.up.setFromXY(0.0, self.halfWH.local.y)
        final.mulV(center.local, center.final)
        final.mulV(self.right, self.right).unTV(center.final)
        final.mulV(self.up, self.up).unTV(center.final)
        self.halfWH.final.setFromXY(self.right.length(), self.up.length())
        self._setVerts()
        
    def resetWH(self, point:EditorPoint):
        center = self.points[0]
        self.halfWH.local.setFromXY(abs(point.local.x), abs(point.local.y)).unTV(center.local)

    def setWH(self, point:EditorPoint):
        self.halfWH.local.setFromV(point.local)

    def setRadiusFromPoint(self, point:EditorPoint):
        assert False

    def setRadiusFromFloat(self, radius:float):
        assert False

    def deletePoint(self, point:EditorPoint):
        assert False
    
    def clone(self) -> 'ShapeSpec':
        raise NotImplementedError

    def getBounds(self, box: BoundingBox) -> Tuple[float]:
        center = self.points[0]
        xMax = xMin = center.final.x
        yMax = yMin = center.final.y
        for point in self.points[1:]:
            xMax = max(xMax, point.final.x)
            xMin = min(xMin, point.final.x)
            yMax = max(yMax, point.final.y)
            yMin = min(yMin, point.final.y)
        box.setFinal(xMin, yMin, xMax, yMax)


class LineSpec(ShapeSpec):

    def __init__(self):
        # TODO correct all shapes internals - points to hold geometry only
        self.points: List[EditorPoint] = []
        self.currentPoint: Optional[EditorPoint] = None
        self.radius: Radius = Radius(1.0)

    def getJSONDict(self, parent:dict):
        prevPoint = self.points[0]
        points = []
        for point in self.points[1:]:
            points.append([prevPoint.final.x, prevPoint.final.y, point.final.x, point.final.y])
            prevPoint = point
        this = {'points' : points,
                'radius' : self.radius.final}
        parent['internal'] = this

    def draw(self):
        drawLineShape(self.points)

    def addPoint(self, point:EditorPoint):
        if point not in self.points:
            self.points.append(point)

    def deletePoint(self, point:EditorPoint):
        if point in self.points:
            self.points.remove(point)

    def updatePos(self, final: Mat):
        for point in self.points:
            final.mulV(point.local, point.final)

    def getBounds(self, box: BoundingBox) -> Tuple[float]:
        if self.points:
            xs = [p.final.x for p in self.points]
            ys = [p.final.y for p in self.points]
            xMin = min(xs)
            xMax = max(xs)
            yMin = min(ys)
            yMax = max(ys)
            box.setFinal(xMin, yMin, xMax, yMax)
            return
        box.setFinal(0.0, 0.0, 0.0, 0.0)
