from typing import List
import math
from typing import List

from .config import pointConfig
from .editorTypes import V2, EditorPoint, UnboundAngle


class ShapeBuffer:

    _instance: "ShapeBuffer" = None

    @staticmethod
    def getInstance() -> "ShapeBuffer":
        if ShapeBuffer._instance == None:
            ShapeBuffer._instance = ShapeBuffer()
        return ShapeBuffer._instance
    
    def __init__(self):
        self.drawScale:float = 1.0
        self.verts: List[float] = []
        self.colors: List[int] = []
        self.indices: List[int] = []
        self.currentIndex: int = 0

    def reset(self):
        self.drawScale:float = 1.0
        self.verts: List[float] = []
        self.colors: List[int] = []
        self.indices: List[int] = []
        self.currentIndex: int = 0

    def addCapsule(self, frm:V2, to:V2, dist: float):
        capLen = frm.distV(to)

        if capLen == 0.0:
            if dist == 0.0:
                return
            self.addCircleXYFromXY(to.x, to.y, dist, 0.0, 32, pointConfig['grooveColor'])
            return
        
        circleParts = math.pi / 16.0
        sin = math.sin(circleParts)
        cos = math.cos(circleParts)

        startOffsetX =   dist * (to.y - frm.y) / capLen
        startOffsetY = - dist * (to.x - frm.x) / capLen

        # TODO add actual update of a buffer
        self.addEdgeXY(frm.x + startOffsetX, frm.y + startOffsetY, 
                         to.x + startOffsetX, to.y + startOffsetY, 
                         pointConfig['grooveColor'])

        for i in range(16):
            endOffsetX = startOffsetX * cos - startOffsetY * sin
            endOffsetY = startOffsetX * sin + startOffsetY * cos
            self.addEdgeXY(to.x + startOffsetX, to.y + startOffsetY, 
                             to.x + endOffsetX, to.y + endOffsetY, 
                             pointConfig['grooveColor'])
            startOffsetX = endOffsetX
            startOffsetY = endOffsetY

        self.addEdgeXY(to.x + startOffsetX, to.y + startOffsetY, 
                         frm.x + startOffsetX, frm.y + startOffsetY, 
                         pointConfig['grooveColor'])
        
        for i in range(16):
            endOffsetX = startOffsetX * cos - startOffsetY * sin
            endOffsetY = startOffsetX * sin + startOffsetY * cos
            self.addEdgeXY(frm.x + startOffsetX, frm.y + startOffsetY, 
                             frm.x + endOffsetX, frm.y + endOffsetY, 
                             pointConfig['grooveColor'])
            startOffsetX = endOffsetX
            startOffsetY = endOffsetY


    # TODO Add functions below to above class as methods
    def addRateA(self, point:V2, rate:UnboundAngle):
        if not (-2.0 * math.pi < rate.angle < 2.0 * math.pi):
            self.addCircleXYFromXY(point.x, point.y, pointConfig['armLength'] * self.drawScale, 0.0, 32, pointConfig['anchorColor'])
        else:
            self.addArcXYRad(point.x, point.y, pointConfig['armLength'] * self.drawScale, 0.0, -rate.angle, 32, pointConfig['anchorColor'])


    def addRateB(self, point:V2, rate:UnboundAngle):
        if not (-2.0 * math.pi < rate.angle < 2.0 * math.pi):
            self.addCircleXYFromXY(point.x, point.y, pointConfig['armLength'] * self.drawScale, 0.0, 32, pointConfig['anchorColor'])
        else:
            self.addArcXYRad(point.x, point.y, pointConfig['armLength'] * self.drawScale, 0.0, rate.angle, 32, pointConfig['anchorColor'])


    def addPhaseMinMaxB(self, point:V2, minPhase:UnboundAngle, maxPhase:UnboundAngle):
        angle = maxPhase.angle - minPhase.angle
        if not (-2.0 * math.pi < angle < 2.0 * math.pi):
            self.addCircleXYFromXY(point.x, point.y, pointConfig['armLength'] * self.drawScale, 0.0, 32, pointConfig['anchorColor'])
        else:
            self.addArcXYRad(point.x, point.y, pointConfig['armLength'] * self.drawScale, -minPhase.angle, -maxPhase.angle, 32, pointConfig['anchorColor'])
            # circleParts = -angle / 32.0
            # sin = math.sin(circleParts)
            # cos = math.cos(circleParts)
            # x = pointConfig['armLength'] * _shaderScale * minPhase.cos
            # y = pointConfig['armLength'] * _shaderScale * minPhase.sin
            
            # for i in range(32):
            #     nX = x * cos + y * sin
            #     nY = -x * sin + y * cos
            #     arcade.draw_line(point.x + x, point.y + y,
            #                      point.x + nX, point.y + nY,
            #                      pointConfig['anchorColor'], _shaderScale)
            #     x, y = nX, nY


    def addPhaseMinMaxA(self, point:V2, minPhase:UnboundAngle, maxPhase:UnboundAngle):
        angle = maxPhase.angle - minPhase.angle
        if not (-2.0 * math.pi < angle < 2.0 * math.pi):
            self.addCircleXYFromXY(point.x, point.y, pointConfig['armLength'] * self.drawScale, 0.0, 32, pointConfig['anchorColor'])
        else:
            self.addArcXYRad(point.x, point.y, pointConfig['armLength'] * self.drawScale, minPhase.angle, maxPhase.angle, 32, pointConfig['anchorColor'])
            # circleParts = angle / 32.0
            # sin = math.sin(circleParts)
            # cos = math.cos(circleParts)
            # x = pointConfig['armLength'] * _shaderScale * minPhase.cos
            # y = - pointConfig['armLength']* _shaderScale * minPhase.sin
            
            # for i in range(32):
            #     nX = x * cos + y * sin
            #     nY = -x * sin + y * cos
            #     arcade.draw_line(point.x + x, point.y + y,
            #                      point.x + nX, point.y + nY,
            #                      pointConfig['anchorColor'], _shaderScale)
            #     x, y = nX, nY


    def addSlide(self, frm:V2, to:V2, distMin:float, distMax:float):
        anchorLength = frm.distV(to)
        if anchorLength != 0.0:
            minLength = (anchorLength - distMin) / anchorLength
            minX = (to.x - frm.x)*minLength
            minY = (to.y - frm.y)*minLength

            maxLength = (anchorLength - distMax) / anchorLength
            maxX = (to.x - frm.x)*maxLength
            maxY = (to.y - frm.y)*maxLength

            self.addEdgeXY(frm.x + minX/2, frm.y + minY/2, frm.x + maxX/2, frm.y + maxY/2,
                        pointConfig['anchorColor'])
            self.addEdgeXY(to.x - minX/2, to.y - minY/2, to.x - maxX/2, to.y - maxY/2,
                        pointConfig['anchorColor'])
            self.addPointXY(frm.x + minX/2, frm.y + minY/2, 
                        pointConfig['anchorColor'], pointConfig['pointHalfWH'] * self.drawScale)
            self.addPointXY(frm.x + maxX/2, frm.y + maxY/2,
                        pointConfig['anchorColor'], pointConfig['pointHalfWH'] * self.drawScale)
            self.addPointXY(to.x - minX/2, to.y - minY/2,
                        pointConfig['anchorColor'], pointConfig['pointHalfWH'] * self.drawScale)
            self.addPointXY(to.x - maxX/2, to.y - maxY/2,
                        pointConfig['anchorColor'], pointConfig['pointHalfWH'] * self.drawScale)
        else:
            if distMax != 0.0:
                self.addCircleXYFromXY(frm.x, frm.y, distMax/2.0, 0.0, 32, pointConfig['anchorColor'])

                if distMin != 0.0:
                    self.addCircleXYFromXY(frm.x, frm.y, distMin/2.0, 0.0, 32, pointConfig['anchorColor'])


    def addSpring(self, frm:V2, to:V2, restLength:float):
        currentLength = frm.distV(to)
        if currentLength != 0.0:
            diffLength = (currentLength - restLength) / currentLength
            diffX = (to.x - frm.x)*diffLength
            diffY = (to.y - frm.y)*diffLength
            self.addEdgeXY(frm.x + diffX/2.0, frm.y + diffY/2.0, frm.x, frm.y,
                        pointConfig['anchorColor'])
            self.addPointXY(frm.x + diffX/2.0, frm.y + diffY/2.0,
                        pointConfig['anchorColor'], pointConfig['pointHalfWH'] * self.drawScale)
            self.addEdgeXY(to.x - diffX/2.0, to.y - diffY/2.0, to.x, to.y,
                        pointConfig['anchorColor'])
            self.addPointXY(to.x - diffX/2.0, to.y - diffY/2.0,
                        pointConfig['anchorColor'], pointConfig['pointHalfWH'] * self.drawScale)
        
        elif restLength != 0.0:
            self.addCircleXYFromXY(frm.x, frm.y, restLength/2.0, 0.0, 32, pointConfig['anchorColor'])


    def addRatchetA(self, posA:V2, ratchet:UnboundAngle):
        x = pointConfig['ratchetArmLength'] * self.drawScale * ratchet.cos
        y = pointConfig['ratchetArmLength'] * self.drawScale * ratchet.sin
        self.addPointXY(posA.x + x, posA.y + y, pointConfig['secondaryBodyColor'], pointConfig['pointHalfWH'] * self.drawScale)


    def addRatchetB(self, posB:V2, phase:UnboundAngle, ratchet:UnboundAngle):
        x = pointConfig['ratchetArmLength'] * self.drawScale * math.cos(phase.angle - ratchet.angle)
        y = pointConfig['ratchetArmLength'] * self.drawScale * math.sin(phase.angle - ratchet.angle)
        self.addPointXY(posB.x + x, posB.y + y, pointConfig['secondaryBodyColor'], pointConfig['pointHalfWH'] * self.drawScale)


    def addAngleArm(self, point:V2, dX:float, dY:float):
        armLength: float = pointConfig['armLength']
        self.addEdgeXY(point.x, point.y, 
                point.x + armLength*dX*self.drawScale, point.y + armLength*dY*self.drawScale, 
                pointConfig['anchorColor'])


    def addAngleRatioArm(self, point:V2, dX:float, dY:float, ratio:float):
        if ratio != 0.0:
            armLength: float = pointConfig['armLength']
            ratioLength = armLength / ratio
            offsetX = point.x + armLength*dX*self.drawScale
            offsetY = point.y + armLength*dY*self.drawScale
            self.addEdgeXY(offsetX, offsetY, 
                            offsetX + ratioLength * dY*self.drawScale, offsetY - ratioLength * dX * self.drawScale, 
                            pointConfig['anchorColor'])


    def addAngleArm(self, point:V2, dX:float, dY:float):
        armLength: float = pointConfig['armLength']
        self.addEdgeXY(
                point.x, point.y, 
                point.x + armLength*dX*self.drawScale, point.y + armLength*dY*self.drawScale, 
                pointConfig['anchorColor'])


    def addPivot(self, pointA:V2, pointB:V2):
        if pointA.distSqrV(pointB) != 0.0:
            self.addEdge(pointA, pointB, pointConfig['anchorColor'])
            x = pointA.x + (pointB.x - pointA.x)/2.0
            y = pointA.y + (pointB.y - pointA.y)/2.0
            self.addPointXY(x, y, pointConfig['anchorColor'], pointConfig['pointHalfWH'] * self.drawScale)


    def addGroove(self, pointA:V2, pointB:V2):
        self.addPoint(pointA, pointConfig['grooveColor'], pointConfig['pointHalfWH'] * self.drawScale)   
        self.addPoint(pointB, pointConfig['grooveColor'], pointConfig['pointHalfWH'] * self.drawScale)
        self.addEdge(pointA, pointB, pointConfig['grooveColor'])
        

    def addAnchor(self, point:V2):
        self.addPoint(point, pointConfig['anchorColor'], pointConfig['pointHalfWH'] * self.drawScale)    


    def addArcXYRad(self, centerX:float, centerY:float, radius:float, fromAngle:float, toAngle:float, elems:int, color):
        circleELemAngle = (toAngle - fromAngle) / elems
        cos = math.cos(circleELemAngle)
        sin = math.sin(circleELemAngle)

        prevX = radius * math.cos(fromAngle)
        prevY = radius * math.sin(fromAngle)

        ind = self.currentIndex
        self.verts += [centerX + prevX, centerY + prevY] 
        for i in range(elems):
            postX = prevX * cos - prevY * sin
            postY = prevX * sin + prevY * cos

            self.verts += [centerX + postX, centerY + postY]
            self.indices += [ind + i, ind + i + 1]

            prevX = postX
            prevY = postY

        self.colors += (elems+1) * color
        self.currentIndex += elems + 1


    def addCircleXYFromXY(self, centerX:float, centerY:float, halfWHX:float, halfWHY:float, elems:int, color):
        circleELemAngle = math.pi * 2.0 / elems
        cos = math.cos(circleELemAngle)
        sin = math.sin(circleELemAngle)

        prevX = halfWHX
        prevY = halfWHY

        ind = self.currentIndex
        self.verts += [centerX + prevX, centerY + prevY] 
        for i in range(elems - 1):
            postX = prevX * cos - prevY * sin
            postY = prevX * sin + prevY * cos

            self.verts += [centerX + postX, centerY + postY]
            self.indices += [ind + i, ind + i + 1]

            prevX = postX
            prevY = postY

        self.indices += [ind + elems - 1, ind]

        self.colors += elems * color
        self.currentIndex += elems


    def addDiamond(self, point:V2, color, halfWH:float):
        ind = self.currentIndex

        self.verts += [point.x + halfWH, point.y,          
                        point.x,          point.y + halfWH,
                        point.x - halfWH, point.y,
                        point.x,          point.y - halfWH]
        self.colors += 4 * color
        self.indices += [ind, ind +1, ind +1, ind +2, ind +2, ind +3, ind +3, ind]
        self.currentIndex += 4


    def addPoint(self, point:V2, color, halfWH:float):

        ind = self.currentIndex
        self.verts += [point.x-halfWH, point.y-halfWH, point.x-halfWH, point.y+halfWH,
                        point.x+halfWH, point.y+halfWH, point.x+halfWH, point.y-halfWH]
        
        self.colors += 4 * color
        self.indices += [ind, ind +1, ind +1, ind +2, ind +2, ind +3, ind +3, ind]
        self.currentIndex += 4


    def addPointXY(self, x:float, y:float, color, halfWH:float):

        ind = self.currentIndex
        self.verts += [x-halfWH, y-halfWH, x-halfWH, y+halfWH,
                        x+halfWH, y+halfWH, x+halfWH, y-halfWH]
        
        self.colors += 4 * color
        self.indices += [ind, ind +1, ind +1, ind +2, ind +2, ind +3, ind +3, ind]
        self.currentIndex += 4


    def addEdge(self, frm:V2, to:V2, color):

        ind = self.currentIndex
        self.verts += [frm.x, frm.y, to.x, to.y]
        self.colors += 2 * color
        self.indices += [ind, ind +1]
        self.currentIndex += 2


    def addEdgeXY(self, frmX:float, frmY:float, toX:float, toY:float, color):

        ind = self.currentIndex
        self.verts += [frmX, frmY, toX, toY]
        self.colors += 2 * color
        self.indices += [ind, ind +1]
        self.currentIndex += 2


    def addBBox(self, center:V2, halfWH:V2, isActive:bool, isUnderCursor:bool):
        color = pointConfig['activeEdgeColor'] if isActive else (pointConfig['underCursorEdgeColor'] if isUnderCursor else pointConfig['inactivePointColor'])
        offset = pointConfig['pointHalfWH'] * self.drawScale
        offsetX = halfWH.x + offset
        offsetY = halfWH.y + offset
        ind = self.currentIndex
        self.verts += [center.x-offsetX, center.y-offsetY, center.x-offsetX, center.y+offsetY,
                        center.x+offsetX, center.y+offsetY, center.x+offsetX, center.y-offsetY]
        
        self.colors += 4 * color
        self.indices += [ind, ind +1, ind +1, ind +2, ind +2, ind +3, ind +3, ind]
        self.currentIndex += 4


    def addCenterOfGravity(self, cog:V2, isChildCog:bool):
        self.addPoint(cog, pointConfig['cogColor'], pointConfig['cogHalfWH'] * self.drawScale)


    def addCircle(self, center:V2, halfWH:V2, elems:int):
        color = pointConfig['inactivePointColor']

        circleELemAngle = math.pi * 2.0 / elems
        cos = math.cos(circleELemAngle)
        sin = math.sin(circleELemAngle)

        prevX = halfWH.x
        prevY = halfWH.y

        ind = self.currentIndex
        self.verts += [center.x + prevX, center.y + prevY] 
        for i in range(elems - 1):
            postX = prevX * cos - prevY * sin
            postY = prevX * sin + prevY * cos

            self.verts += [center.x + postX, center.y + postY]
            self.indices += [ind + i, ind + i + 1]

            prevX = postX
            prevY = postY

        self.indices += [ind + elems - 1, ind]

        self.colors += elems * color
        self.currentIndex += elems

        # add arm
        self.verts += [center.x, center.y]
        self.colors +=  color
        self.indices += [ind, ind + elems]

        self.currentIndex += 1


    def addLineShape(self, points: List[EditorPoint]):
        color = pointConfig['inactivePointColor']
        if points:
            point = points[0].final
            self.addPoint(point, pointConfig['inactivePointColor'], pointConfig['pointHalfWH'] * self.drawScale)
            for nextPoint in points[1:]:
                self.addEdge(point, nextPoint.final, color)
                self.addPoint(nextPoint.final, pointConfig['inactivePointColor'], pointConfig['pointHalfWH'] * self.drawScale)
                point = nextPoint.final


    def addPolygon(self, points: List[EditorPoint]):
        color = pointConfig['inactivePointColor']
        if points:
            #prevPoint = poly.points[-1]
            prevPoint = points[-1].final
            for point in points:
                self.addEdge(prevPoint, point.final, color)
                self.addPoint(point.final, pointConfig['inactivePointColor'], pointConfig['pointHalfWH'] * self.drawScale)
                prevPoint = point.final


    def addBox(self, points: List[EditorPoint]):
        color = pointConfig['inactivePointColor']

        prevPoint = points[-1].final
        for point in points[1:]:
            self.addEdge(prevPoint, point.final, color)
            # arcade.draw_line(prevPoint.final.x, prevPoint.final.y, 
            #                  point.final.x,     point.final.y, color, _shaderScale)
            self.addPoint(prevPoint, color, pointConfig['pointHalfWH'] * self.drawScale)
            prevPoint = point.final


    def addRect(self, points: List[EditorPoint]):
        color = pointConfig['inactivePointColor']
        
        # TODO this to internal rect state
        prevPoint = points[-1].final
        for point in points[1:]:
            self.addEdge(prevPoint, point.final, color)
            # arcade.draw_line(prevPoint.final.x, prevPoint.final.y, 
            #                  point.final.x,     point.final.y, color, _shaderScale)
            self.addPoint(prevPoint, color, pointConfig['pointHalfWH'] * self.drawScale)
            prevPoint = point.final

        
    def addHelperPoint(self, point:V2):
        self.addDiamond(point, pointConfig['helperColor'], pointConfig['helperHalfWH'] * self.drawScale)


    def addCursor(self, cursor:V2, viewLimits:V2, viewOffset:V2, menuDistance:float):
        color = pointConfig['cursorLineColor']
        if cursor.x >= viewLimits.x - menuDistance:
            color = pointConfig['cursorLineMenuColor']
        
        self.addPoint(cursor, color, pointConfig['cursorHalfWH'] * self.drawScale)
        
        ind = self.currentIndex
        self.verts += [viewOffset.x, cursor.y,
                        viewOffset.x + viewLimits.x + menuDistance, cursor.y,
                        cursor.x, viewOffset.y, 
                        cursor.x, viewOffset.y + viewLimits.y] 
        self.colors += 4 * color
        self.indices += [ind, ind +1, ind+2, ind+3]
        self.currentIndex += 4


    # TODO move to geometry shader
    def addGridLayer(self, minX, minY, maxX, maxY, gridSize, armLength, roundFactor, color):
        xLower = round(minX, roundFactor)
        yStart = round(minY, roundFactor)
        xUpper = round(maxX, roundFactor)
        yUpper = round(maxY, roundFactor)
        if xLower < 0.0:
            xLower -= gridSize
        if yStart < 0.0:
            yStart -= gridSize
        if xUpper > 0.0:
            xUpper += gridSize
        if yUpper + 0.0:
            yUpper += gridSize

        while xLower <= xUpper:
            yLower = yStart
            while yLower <= yUpper:
                ind = self.currentIndex
                self.verts += [xLower - armLength, yLower, xLower + armLength, yLower, xLower, yLower - armLength, xLower , yLower + armLength]
                self.colors += 4 * color
                self.indices += [ind, ind +1, ind +2 , ind +3]
                self.currentIndex += 4
                #self.addEdgeXY(xLower - armLength, yLower, xLower + armLength, yLower, color)
                #self.addEdgeXY(xLower, yLower - armLength, xLower , yLower + armLength, color)
                yLower += gridSize
            xLower += gridSize

    def addGrid(self, viewLowerBounds:V2, viewSize:V2):
        
        xBoundsMin = viewLowerBounds.x
        yBoundsMin = viewLowerBounds.y
        xBoundsMax = xBoundsMin + viewSize.x
        yBoundsMax = yBoundsMin + viewSize.y

        gridNormalView = 60.0
        gridDisappear = 20.0
        gridColor = 50.0
        # 10 cm grid
        gridSize = 0.1
        gridSizeInPixels:float = gridSize / self.drawScale
        armLength = 1.0 * self.drawScale
        if gridSizeInPixels > gridDisappear:
            colorLerp = int( gridColor * max(gridDisappear, min(gridNormalView, gridSizeInPixels)) / (gridNormalView - gridDisappear))
            self.addGridLayer(xBoundsMin, yBoundsMin, xBoundsMax, yBoundsMax, gridSize, armLength, 1, (colorLerp, colorLerp, colorLerp, 255))

        # 1m grid
        gridSize = 1.0
        gridSizeInPixels:float = gridSize / self.drawScale
        armLength = 3.0 * self.drawScale
        if gridSizeInPixels > gridDisappear:
            colorLerp = int( gridColor * max(gridDisappear, min(gridNormalView, gridSizeInPixels)) / (gridNormalView - gridDisappear))
            self.addGridLayer(xBoundsMin, yBoundsMin, xBoundsMax, yBoundsMax, gridSize, armLength, 0, (colorLerp, colorLerp, colorLerp, 255))

        # 10m grid
        gridSize = 10.0
        gridSizeInPixels:float = gridSize / self.drawScale
        armLength = 5.0 * self.drawScale
        if gridSizeInPixels > gridDisappear:
            colorLerp = int( gridColor * max(gridDisappear, min(gridNormalView, gridSizeInPixels)) / (gridNormalView - gridDisappear))
            self.addGridLayer(xBoundsMin, yBoundsMin, xBoundsMax, yBoundsMax, gridSize, armLength, -1, (colorLerp, colorLerp, colorLerp, 255))

        # 100m grid
        gridSize = 100.0
        gridSizeInPixels:float = gridSize / self.drawScale
        armLength = 7.0 * self.drawScale
        if gridSizeInPixels > gridDisappear:
            colorLerp = int( gridColor * max(gridDisappear, min(gridNormalView, gridSizeInPixels)) / (gridNormalView - gridDisappear))
            self.addGridLayer(xBoundsMin, yBoundsMin, xBoundsMax, yBoundsMax, gridSize, armLength, -2, (colorLerp, colorLerp, colorLerp, 255))

        ind = self.currentIndex

        if xBoundsMin <= 0.0 <= xBoundsMax:
            self.verts += [0.0, yBoundsMin, 0.0, yBoundsMax]
            self.colors += 2 * [70, 70, 70, 255]
            self.indices += [ind, ind +1]
            self.currentIndex += 2
            ind += 2

        if yBoundsMin <= 0.0 <= yBoundsMax:
            self.verts += [xBoundsMin, 0.0, xBoundsMax, 0.0]
            self.colors += 2 * [70, 70, 70, 255]
            self.indices += [ind, ind +1]
            self.currentIndex += 2