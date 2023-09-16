import math
from typing import List

from .config import pointConfig
from .editorTypes import V2, EditorPoint, UnboundAngle
from .shapeInternals.editorBodyI import BodyI
from .shapeInternals.editorShapeI import ShapeI
from .bufferContainer import BufferContainer


def drawCapsule(buffer:BufferContainer, frm:V2, to:V2, dist: float):
    capLen = frm.distV(to)

    
    if capLen == 0.0:
        if dist == 0.0:
            return
        drawCircleXYFromXY(buffer, to.x, to.y, dist, 0.0, 32, pointConfig['grooveColor'])
        return
    
    circleParts = math.pi / 16.0
    sin = math.sin(circleParts)
    cos = math.cos(circleParts)

    startOffsetX = - dist * (to.y - frm.y) / capLen
    startOffsetY =   dist * (to.x - frm.x) / capLen

    # TODO add actual update of a buffer
    # arcade.draw_line(frm.x + startOffsetX, frm.y + startOffsetY, 
    #                  to.x + startOffsetX, to.y + startOffsetY, 
    #                  pointConfig['grooveColor'], _shaderScale)

    for i in range(16):
        endOffsetX = startOffsetX * cos - startOffsetY * sin
        endOffsetY = startOffsetX * sin + startOffsetY * cos
        # arcade.draw_line(to.x + startOffsetX, to.y + startOffsetY, 
        #                  to.x + endOffsetX, to.y + endOffsetY, 
        #                  pointConfig['grooveColor'], _shaderScale)
        startOffsetX = endOffsetX
        startOffsetY = endOffsetY

    # arcade.draw_line(to.x + startOffsetX, to.y + startOffsetY, 
    #                  frm.x + startOffsetX, frm.y + startOffsetY, 
    #                  pointConfig['grooveColor'], _shaderScale)
    
    for i in range(16):
        endOffsetX = startOffsetX * cos - startOffsetY * sin
        endOffsetY = startOffsetX * sin + startOffsetY * cos
        # arcade.draw_line(frm.x + startOffsetX, frm.y + startOffsetY, 
        #                  frm.x + endOffsetX, frm.y + endOffsetY, 
        #                  pointConfig['grooveColor'], _shaderScale)
        startOffsetX = endOffsetX
        startOffsetY = endOffsetY


def drawRateA(buffer:BufferContainer, point:V2, rate:UnboundAngle):
    if not (-2.0 * math.pi < rate.angle < 2.0 * math.pi):
        drawCircleXYFromXY(buffer, point.x, point.y, pointConfig['armLength'] * buffer.drawScale, 0.0, 32, pointConfig['anchorColor'])
    else:
        drawArcXYRad(buffer, point.x, point.y, pointConfig['armLength'] * buffer.drawScale, 0.0, -rate.angle, 32, pointConfig['anchorColor'])


def drawRateB(buffer:BufferContainer, point:V2, rate:UnboundAngle):
    if not (-2.0 * math.pi < rate.angle < 2.0 * math.pi):
        drawCircleXYFromXY(buffer, point.x, point.y, pointConfig['armLength'] * buffer.drawScale, 0.0, 32, pointConfig['anchorColor'])
    else:
        drawArcXYRad(buffer, point.x, point.y, pointConfig['armLength'] * buffer.drawScale, 0.0, rate.angle, 32, pointConfig['anchorColor'])


def drawPhaseMinMaxB(buffer:BufferContainer, point:V2, minPhase:UnboundAngle, maxPhase:UnboundAngle):
    angle = maxPhase.angle - minPhase.angle
    if not (-2.0 * math.pi < angle < 2.0 * math.pi):
        drawCircleXYFromXY(buffer, point.x, point.y, pointConfig['armLength'] * buffer.drawScale, 0.0, 32, pointConfig['anchorColor'])
    else:
        drawArcXYRad(buffer, point.x, point.y, pointConfig['armLength'] * buffer.drawScale, -minPhase.angle, -maxPhase.angle, 32, pointConfig['anchorColor'])
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


def drawPhaseMinMaxA(buffer:BufferContainer, point:V2, minPhase:UnboundAngle, maxPhase:UnboundAngle):
    angle = maxPhase.angle - minPhase.angle
    if not (-2.0 * math.pi < angle < 2.0 * math.pi):
        drawCircleXYFromXY(buffer, point.x, point.y, pointConfig['armLength'] * buffer.drawScale, 0.0, 32, pointConfig['anchorColor'])
    else:
        drawArcXYRad(buffer, point.x, point.y, pointConfig['armLength'] * buffer.drawScale, minPhase.angle, maxPhase.angle, 32, pointConfig['anchorColor'])
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


def drawSlide(buffer:BufferContainer, frm:V2, to:V2, distMin:float, distMax:float):
    anchorLength = frm.distV(to)
    if anchorLength != 0.0:
        minLength = (anchorLength - distMin) / anchorLength
        minX = (to.x - frm.x)*minLength
        minY = (to.y - frm.y)*minLength

        maxLength = (anchorLength - distMax) / anchorLength
        maxX = (to.x - frm.x)*maxLength
        maxY = (to.y - frm.y)*maxLength

        drawEdgeXY(buffer, frm.x + minX/2, frm.y + minY/2, frm.x + maxX/2, frm.y + maxY/2,
                    pointConfig['anchorColor'])
        drawEdgeXY(buffer, to.x - minX/2, to.y - minY/2, to.x - maxX/2, to.y - maxY/2,
                    pointConfig['anchorColor'])
        drawPointXY(buffer, frm.x + minX/2, frm.y + minY/2, 
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
        drawPointXY(buffer, frm.x + maxX/2, frm.y + maxY/2,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
        drawPointXY(buffer, to.x - minX/2, to.y - minY/2,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
        drawPointXY(buffer, to.x - maxX/2, to.y - maxY/2,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
    else:
        if distMax != 0.0:
            drawCircleXYFromXY(buffer, frm.x, frm.y, distMax/2.0, 0.0, 32, pointConfig['anchorColor'])

            if distMin != 0.0:
                drawCircleXYFromXY(buffer, frm.x, frm.y, distMin/2.0, 0.0, 32, pointConfig['anchorColor'])


def drawSpring(buffer:BufferContainer, frm:V2, to:V2, restLength:float):
    currentLength = frm.distV(to)
    if currentLength != 0.0:
        diffLength = (currentLength - restLength) / currentLength
        diffX = (to.x - frm.x)*diffLength
        diffY = (to.y - frm.y)*diffLength
        drawEdgeXY(buffer, frm.x + diffX/2.0, frm.y + diffY/2.0, frm.x, frm.y,
                    pointConfig['anchorColor'])
        drawPointXY(buffer, frm.x + diffX/2.0, frm.y + diffY/2.0,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
        drawEdgeXY(buffer, to.x - diffX/2.0, to.y - diffY/2.0, to.x, to.y,
                    pointConfig['anchorColor'])
        drawPointXY(buffer, to.x - diffX/2.0, to.y - diffY/2.0,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
    
    elif restLength != 0.0:
        drawCircleXYFromXY(buffer, frm.x, frm.y, restLength/2.0, 0.0, 32, pointConfig['anchorColor'])


def drawRatchetA(buffer:BufferContainer, posA:V2, ratchet:UnboundAngle):
    x = pointConfig['ratchetArmLength'] * buffer.drawScale * ratchet.cos
    y = pointConfig['ratchetArmLength'] * buffer.drawScale * ratchet.sin
    drawPointXY(buffer, posA.x + x, posA.y + y, pointConfig['secondaryBodyColor'], pointConfig['pointHalfWH'] * buffer.drawScale)


def drawRatchetB(buffer:BufferContainer, posB:V2, phase:UnboundAngle, ratchet:UnboundAngle):
    x = pointConfig['ratchetArmLength'] * buffer.drawScale * math.cos(phase.angle - ratchet.angle)
    y = pointConfig['ratchetArmLength'] * buffer.drawScale * math.sin(phase.angle - ratchet.angle)
    drawPointXY(buffer, posB.x + x, posB.y + y, pointConfig['secondaryBodyColor'], pointConfig['pointHalfWH'] * buffer.drawScale)


def drawAngleArm(buffer:BufferContainer, point:V2, dX:float, dY:float):
    armLength: float = pointConfig['armLength']
    drawEdgeXY(buffer, point.x, point.y, 
               point.x + armLength*dX*buffer.drawScale, point.y + armLength*dY*buffer.drawScale, 
               pointConfig['anchorColor'])


def drawAngleRatioArm(buffer:BufferContainer, point:V2, dX:float, dY:float, ratio:float):
    if ratio != 0.0:
        armLength: float = pointConfig['armLength']
        ratioLength = armLength / ratio
        offsetX = point.x + armLength*dX*buffer.drawScale
        offsetY = point.y + armLength*dY*buffer.drawScale
        drawEdgeXY(buffer, offsetX, offsetY, 
                        offsetX + ratioLength * dY*buffer.drawScale, offsetY - ratioLength * dX * buffer.drawScale, 
                        pointConfig['anchorColor'])


def drawAngleArm(buffer:BufferContainer, point:V2, dX:float, dY:float):
    armLength: float = pointConfig['armLength']
    drawEdgeXY(buffer, 
               point.x, point.y, 
               point.x + armLength*dX*buffer.drawScale, point.y + armLength*dY*buffer.drawScale, 
               pointConfig['anchorColor'])


def drawPivot(buffer:BufferContainer, pointA:V2, pointB:V2):
    if pointA.distSqrV(pointB) != 0.0:
        drawEdge(buffer, pointA, pointB, pointConfig['anchorColor'])
        x = pointA.x + (pointB.x - pointA.x)/2.0
        y = pointA.y + (pointB.y - pointA.y)/2.0
        drawPointXY(buffer, x, y, pointConfig['anchorColor'], pointConfig['pointHalfWH'] * buffer.drawScale)


def drawGroove(buffer:BufferContainer, pointA:V2, pointB:V2):
    drawPoint(buffer, pointA, pointConfig['grooveColor'], pointConfig['pointHalfWH'] * buffer.drawScale)   
    drawPoint(buffer, pointB, pointConfig['grooveColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
    drawEdge(buffer, pointA, pointB, pointConfig['grooveColor'])
    

def drawAnchor(buffer:BufferContainer, point:V2):
    drawPoint(buffer, point, pointConfig['anchorColor'], pointConfig['pointHalfWH'] * buffer.drawScale)    


def drawArcXYRad(buffer:BufferContainer, centerX:float, centerY:float, radius:float, fromAngle:float, toAngle:float, elems:int, color):
    circleELemAngle = (toAngle - fromAngle) / elems
    cos = math.cos(circleELemAngle)
    sin = math.sin(circleELemAngle)

    prevX = radius * math.cos(fromAngle)
    prevY = radius * math.sin(fromAngle)

    ind = buffer.currentIndex
    buffer.verts += [centerX + prevX, centerY + prevY] 
    for i in range(elems):
        postX = prevX * cos - prevY * sin
        postY = prevX * sin + prevY * cos

        buffer.verts += [centerX + postX, centerY + postY]
        buffer.indices += [ind + i, ind + i + 1]

        prevX = postX
        prevY = postY

    buffer.colors += elems * color
    buffer.currentIndex += elems


def drawCircleXYFromXY(buffer:BufferContainer, centerX:float, centerY:float, halfWHX:float, halfWHY:float, elems:int, color):
    circleELemAngle = math.pi * 2.0 / elems
    cos = math.cos(circleELemAngle)
    sin = math.sin(circleELemAngle)

    prevX = halfWHX
    prevY = halfWHY

    ind = buffer.currentIndex
    buffer.verts += [centerX + prevX, centerY + prevY] 
    for i in range(elems - 1):
        postX = prevX * cos - prevY * sin
        postY = prevX * sin + prevY * cos

        buffer.verts += [centerX + postX, centerY + postY]
        buffer.indices += [ind + i, ind + i + 1]

        prevX = postX
        prevY = postY

    buffer.indices += [ind + elems - 1, ind]

    buffer.colors += elems * color
    buffer.currentIndex += elems


def drawDiamond(buffer:BufferContainer, point:V2, color, halfWH:float):
    ind = buffer.currentIndex

    buffer.verts += [point.x + halfWH, point.y,          
                     point.x,          point.y + halfWH,
                     point.x - halfWH, point.y,
                     point.x,          point.y - halfWH]
    buffer.colors += 4 * color
    buffer.indices += [ind, ind +1, ind +1, ind +2, ind +2, ind +3, ind +3, ind]
    buffer.currentIndex += 4


def drawPoint(buffer:BufferContainer, point:V2, color, halfWH:float):

    ind = buffer.currentIndex
    buffer.verts += [point.x-halfWH, point.y-halfWH, point.x-halfWH, point.y+halfWH,
                     point.x+halfWH, point.y+halfWH, point.x-halfWH, point.y+halfWH]
    
    buffer.colors += 4 * color
    buffer.indices += [ind, ind +1, ind +1, ind +2, ind +2, ind +3, ind +3, ind]
    buffer.currentIndex += 4


def drawPointXY(buffer:BufferContainer, x:float, y:float, color, halfWH:float):

    ind = buffer.currentIndex
    buffer.verts += [x-halfWH, y-halfWH, x-halfWH, y+halfWH,
                     x+halfWH, y+halfWH, x-halfWH, y+halfWH]
    
    buffer.colors += 4 * color
    buffer.indices += [ind, ind +1, ind +1, ind +2, ind +2, ind +3, ind +3, ind]
    buffer.currentIndex += 4


def drawEdge(buffer:BufferContainer, frm:V2, to:V2, color):

    ind = buffer.currentIndex
    buffer.verts += [frm.x, frm.y, to.x, to.y]
    buffer.colors += 2 * color
    buffer.indices += [ind, ind +1]
    buffer.currentIndex += 2


def drawEdgeXY(buffer:BufferContainer, frmX:float, frmY:float, toX:float, toY:float, color):

    ind = buffer.currentIndex
    buffer.verts += [frmX, frmY, toX, toY]
    buffer.colors += 2 * color
    buffer.indices += [ind, ind +1]
    buffer.currentIndex += 2


def drawBBox(buffer: BufferContainer, center:V2, halfWH:V2, color, offset:float):

    ind = buffer.currentIndex
    buffer.verts += [center.x-halfWH, center.y-halfWH, center.x-halfWH, center.y+halfWH,
                     center.x+halfWH, center.y+halfWH, center.x-halfWH, center.y+halfWH]
    
    buffer.colors += 4 * color
    buffer.indices += [ind, ind +1, ind +1, ind +2, ind +2, ind +3, ind +3, ind]
    buffer.currentIndex += 4


def drawBody(buffer:BufferContainer, body: BodyI, isActive:bool, isUnderCursor:bool):
    color = pointConfig['activeEdgeColor'] if isActive else (pointConfig['underCursorEdgeColor'] if isUnderCursor else pointConfig['inactivePointColor'])
    for shape in body.shapes:
        shape.draw()

    drawBBox(buffer, body.box.center.final, body.box.halfWH.final, color, pointConfig['pointHalfWH'] * buffer.drawScale)

    drawPoint(buffer, body.physics.cog.final, pointConfig['cogColor'], pointConfig['cogHalfWH'] * buffer.drawScale)


def drawShape(buffer:BufferContainer, shape: ShapeI, isActive:bool, isUnderCursor:bool):
    color = pointConfig['activeEdgeColor'] if isActive else (pointConfig['underCursorEdgeColor'] if isUnderCursor else pointConfig['inactivePointColor'])
    shape.draw()

    drawBBox(buffer, shape.box.center.final, shape.box.halfWH.final, color, pointConfig['pointHalfWH'] * buffer.drawScale)

    drawPoint(buffer, shape.physics.cog.final, pointConfig['cogColor'], pointConfig['cogHalfWH'] * buffer.drawScale)


def drawCircle(buffer:BufferContainer, center:V2, halfWH:V2, elems:int):
    color = pointConfig['inactivePointColor']

    circleELemAngle = math.pi * 2.0 / elems
    cos = math.cos(circleELemAngle)
    sin = math.sin(circleELemAngle)

    prevX = halfWH.x
    prevY = halfWH.y

    ind = buffer.currentIndex
    buffer.verts += [center.x + prevX, center.y + prevY] 
    for i in range(elems - 1):
        postX = prevX * cos - prevY * sin
        postY = prevX * sin + prevY * cos

        buffer.verts += [center.x + postX, center.y + postY]
        buffer.indices += [ind + i, ind + i + 1]

        prevX = postX
        prevY = postY

    buffer.indices += [ind + elems - 1, ind]

    buffer.colors += elems * color
    buffer.currentIndex += elems

    # add arm
    buffer.verts += [center.x, center.y]
    buffer.colors +=  color
    buffer.indices += [ind, ind + elems]

    buffer.currentIndex += 1


def drawLineShape(buffer:BufferContainer, points: List[EditorPoint]):
    color = pointConfig['inactivePointColor']
    if points:
        point = points[0].final
        drawPoint(buffer, point, pointConfig['inactivePointColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
        for nextPoint in points[1:]:
            drawEdge(buffer, point, nextPoint.final, color)
            drawPoint(buffer, nextPoint.final, pointConfig['inactivePointColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
            point = nextPoint.final


def drawPolygon(buffer:BufferContainer, points: List[EditorPoint]):
    color = pointConfig['inactivePointColor']
    if points:
        #prevPoint = poly.points[-1]
        prevPoint = points[-1].final
        for point in points:
            drawEdge(buffer, prevPoint, point.final, color)
            drawPoint(buffer, point.final, pointConfig['inactivePointColor'], pointConfig['pointHalfWH'] * buffer.drawScale)
            prevPoint = point.final


def drawBox(buffer:BufferContainer, points: List[EditorPoint]):
    color = pointConfig['inactivePointColor']

    prevPoint = points[-1].final
    for point in points[1:]:
        drawEdge(buffer, prevPoint, point.final, color)
        # arcade.draw_line(prevPoint.final.x, prevPoint.final.y, 
        #                  point.final.x,     point.final.y, color, _shaderScale)
        drawPoint(buffer, prevPoint, color, pointConfig['pointHalfWH'] * buffer.drawScale)
        prevPoint = point.final


def drawRect(buffer:BufferContainer, points: List[EditorPoint]):
    color = pointConfig['inactivePointColor']
    
    # TODO this to internal rect state
    prevPoint = points[-1].final
    for point in points[1:]:
        drawEdge(buffer, prevPoint, point.final, color)
        # arcade.draw_line(prevPoint.final.x, prevPoint.final.y, 
        #                  point.final.x,     point.final.y, color, _shaderScale)
        drawPoint(buffer, prevPoint, color, pointConfig['pointHalfWH'] * buffer.drawScale)
        prevPoint = point.final

    
def drawHelperPoint(buffer:BufferContainer, point:V2):
    drawDiamond(buffer, point, pointConfig['helperColor'], pointConfig['helperHalfWH'] * buffer.drawScale)


def drawCursor(buffer:BufferContainer, cursor:V2, viewLimits:V2, viewOffset:V2, menuDistance:float):
    color = pointConfig['cursorLineColor']
    if cursor.x >= viewLimits.x - menuDistance:
        color = pointConfig['cursorLineMenuColor']
    
    drawPoint(buffer, cursor, color, pointConfig['cursorHalfWH'] * buffer.drawScale)
    
    ind = buffer.currentIndex
    buffer.verts += [viewOffset.x, cursor.y,
                     viewOffset.x + viewLimits.x + menuDistance, cursor.y,
                     cursor.x, viewOffset.y, 
                     cursor.x, viewOffset.y + viewLimits.y] 
    buffer.colors += 4 * color
    buffer.indices += [ind, ind +1, ind+2, ind+3]
    buffer.currentIndex += 4
