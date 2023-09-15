import arcade
import pyglet
from pyglet.math import Mat4
import math
from typing import List, Tuple

from .config import pointConfig, editorButtonSetup
from .editorTypes import V2, EditorPoint, UnboundAngle
from .shapeInternals.editorBodyI import BodyI
from .shapeInternals.editorShapeI import ShapeI
from .bufferContainer import BufferContainer


# temporary global state for builtin shader
# to del when shader will be changed
_shaderScale: float = 1.0
_viewOffset:V2 = V2()
_viewLimits:V2 = V2()
_menuDistance: float = 1.0

def finishDrawing():
    pyglet.gl.glFinish()

def setContext(viewport: Tuple[float], mat: Mat4):
    ctx = arcade.get_window().ctx
    ctx.viewport = viewport
    ctx.projection_2d_matrix = mat

def setDrawingParams(scale: float, offset: V2, limits: V2, menuDist:float):
    global _shaderScale
    global _menuDistance
    global _viewOffset
    global _viewLimits
    _shaderScale = scale
    _viewOffset.setFromV(offset)
    _viewLimits.setFromV(limits).sS(scale)
    _menuDistance = menuDist * scale


def drawCapsule(frm:V2, to:V2, dist: float):
    circleParts = math.pi / 16.0
    capLen = frm.distV(to)

    
    if capLen == 0.0:
        if dist == 0.0:
            return
        arcade.draw_circle_outline(to.x, to.y, dist, pointConfig['grooveColor'], _shaderScale)
        return
    
    dx = (to.x - frm.x) / capLen
    dy = (to.y - frm.y) / capLen

    arcade.draw_line(frm.x - dy * dist, frm.y + dx * dist, 
                     to.x - dy * dist, to.y + dx * dist, 
                     pointConfig['grooveColor'], _shaderScale)

    arcade.draw_line(frm.x + dy * dist, frm.y - dx * dist, 
                     to.x + dy * dist, to.y - dx * dist, 
                     pointConfig['grooveColor'], _shaderScale)
    
    sin = math.sin(circleParts)
    cos = math.cos(circleParts)
    angX = -dy * dist
    angY = dx * dist
    for i in range(16):
        nextAngX = angX * cos + angY * sin
        nextAngY = -angX * sin + angY * cos
        arcade.draw_line(frm.x - angX, frm.y - angY,
                         frm.x - nextAngX, frm.y - nextAngY,
                         pointConfig['grooveColor'], _shaderScale)
        arcade.draw_line(to.x + angX, to.y + angY,
                         to.x + nextAngX, to.y + nextAngY,
                         pointConfig['grooveColor'], _shaderScale)
        angX = nextAngX
        angY = nextAngY


def drawRateA(point:V2, rate:UnboundAngle):
    if not (-2.0 * math.pi < rate.angle < 2.0 * math.pi):
        arcade.draw_circle_outline(point.x, point.y, pointConfig['armLength'] * _shaderScale, pointConfig['anchorColor'], _shaderScale, num_segments=32)
    else:
        circleParts = -rate.angle / 32.0
        sin = math.sin(circleParts)
        cos = math.cos(circleParts)
        x = pointConfig['armLength'] * _shaderScale
        y = 0.0
        
        for i in range(32):
            nX = x * cos - y * sin
            nY = x * sin + y * cos
            arcade.draw_line(point.x + x, point.y + y,
                             point.x + nX, point.y + nY,
                             pointConfig['anchorColor'], _shaderScale)
            x, y = nX, nY


def drawRateB(point:V2, rate:UnboundAngle):
    if not (-2.0 * math.pi < rate.angle < 2.0 * math.pi):
        arcade.draw_circle_outline(point.x, point.y, pointConfig['armLength'] * _shaderScale, pointConfig['anchorColor'], _shaderScale, num_segments=32)
    else:
        circleParts = rate.angle / 32.0
        sin = math.sin(circleParts)
        cos = math.cos(circleParts)
        x = pointConfig['armLength'] * _shaderScale
        y = 0.0
        
        for i in range(32):
            nX = x * cos - y * sin
            nY = x * sin + y * cos
            arcade.draw_line(point.x + x, point.y + y,
                             point.x + nX, point.y + nY,
                             pointConfig['anchorColor'], _shaderScale)
            x, y = nX, nY


def drawPhaseMinMaxB(point:V2, minPhase:UnboundAngle, maxPhase:UnboundAngle):
    angle = maxPhase.angle - minPhase.angle
    if not (-2.0 * math.pi < angle < 2.0 * math.pi):
        arcade.draw_circle_outline(point.x, point.y, pointConfig['armLength'], pointConfig['anchorColor'], _shaderScale, num_segments=32)
    else:
        circleParts = -angle / 32.0
        sin = math.sin(circleParts)
        cos = math.cos(circleParts)
        x = pointConfig['armLength'] * _shaderScale * minPhase.cos
        y = pointConfig['armLength'] * _shaderScale * minPhase.sin
        
        for i in range(32):
            nX = x * cos + y * sin
            nY = -x * sin + y * cos
            arcade.draw_line(point.x + x, point.y + y,
                             point.x + nX, point.y + nY,
                             pointConfig['anchorColor'], _shaderScale)
            x, y = nX, nY


def drawPhaseMinMaxA(point:V2, minPhase:UnboundAngle, maxPhase:UnboundAngle):
    angle = maxPhase.angle - minPhase.angle
    if not (-2.0 * math.pi < angle < 2.0 * math.pi):
        arcade.draw_circle_outline(point.x, point.y, pointConfig['armLength'] * _shaderScale, pointConfig['anchorColor'], _shaderScale, num_segments=32)
    else:
        circleParts = angle / 32.0
        sin = math.sin(circleParts)
        cos = math.cos(circleParts)
        x = pointConfig['armLength'] * _shaderScale * minPhase.cos
        y = - pointConfig['armLength']* _shaderScale * minPhase.sin
        
        for i in range(32):
            nX = x * cos + y * sin
            nY = -x * sin + y * cos
            arcade.draw_line(point.x + x, point.y + y,
                             point.x + nX, point.y + nY,
                             pointConfig['anchorColor'], _shaderScale)
            x, y = nX, nY


def drawSlide(frm:V2, to:V2, distMin:float, distMax:float):
    #drawEdge(frm, to, pointConfig['anchorColor'])
    anchorLength = frm.distV(to)
    if anchorLength != 0.0:
        minLength = (anchorLength - distMin) / anchorLength
        minX = (to.x - frm.x)*minLength
        minY = (to.y - frm.y)*minLength

        maxLength = (anchorLength - distMax) / anchorLength
        maxX = (to.x - frm.x)*maxLength
        maxY = (to.y - frm.y)*maxLength

        drawEdgeXY(frm.x + minX/2, frm.y + minY/2, frm.x + maxX/2, frm.y + maxY/2,
                    pointConfig['anchorColor'])
        drawEdgeXY(to.x - minX/2, to.y - minY/2, to.x - maxX/2, to.y - maxY/2,
                    pointConfig['anchorColor'])
        drawPointXY(frm.x + minX/2, frm.y + minY/2, 
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * _shaderScale)
        drawPointXY(frm.x + maxX/2, frm.y + maxY/2,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * _shaderScale)
        drawPointXY(to.x - minX/2, to.y - minY/2,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * _shaderScale)
        drawPointXY(to.x - maxX/2, to.y - maxY/2,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * _shaderScale)
    else:
        arcade.draw_circle_outline(to.x, to.y, distMin/2.0, pointConfig['anchorColor'], _shaderScale, num_segments=32)
        arcade.draw_circle_outline(to.x, to.y, distMax/2.0, pointConfig['anchorColor'], _shaderScale, num_segments=32)


def drawSpring(buffer:BufferContainer, frm:V2, to:V2, restLength:float):
    realLength = frm.distV(to)
    if realLength != 0.0:
        diffLength = (realLength - restLength) / realLength
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
    else:
        arcade.draw_circle_outline(to.x, to.y, restLength/2.0, pointConfig['anchorColor'], buffer.drawScale, num_segments=32)


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

    for i in range(elems - 1):
        postX = prevX * cos - prevY * sin
        postY = prevX * sin + prevY * cos

        buffer.verts += [center.x + prevX, center.y + prevY, center.x + postX, center.y + postY]
        buffer.indices += [ind + i, ind + i + 1]

        prevX = postX
        prevY = postY

    buffer.verts += [center.x + prevX, center.y + prevY, center.x + halfWH.x, center.y + halfWH.y]
    
    buffer.colors += elems * color
    buffer.indices += [ind + elems-1, ind]

    #arcade.draw_circle_outline(center.x, center.y, radius, color, _shaderScale, num_segments=elems)

    # add arm
    buffer.verts += [center.x, center.y]
    buffer.colors +=  color
    buffer.indices += [ind, ind + elems]

    buffer.currentIndex += elems + 2

    #arcade.draw_line(center.x, center.y, center.x + halfWH.x, center.y + halfWH.y, color, _shaderScale)


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


def drawCursor(buffer:BufferContainer, cursor:V2):
    color = pointConfig['cursorLineColor']
    if cursor.x >= _viewLimits.x - _menuDistance:
        color = pointConfig['cursorLineMenuColor']
    
    drawPoint(buffer, cursor, color, pointConfig['cursorHalfWH'] * buffer.drawScale)
    
    ind = buffer.currentIndex
    buffer.verts += [_viewOffset.x, cursor.y,
                     _viewOffset.x + _viewLimits.x + _menuDistance, cursor.y,
                     cursor.x, _viewOffset.y, 
                     cursor.x, _viewOffset.y + _viewLimits.y] 
    buffer.colors += 4 * color
    buffer.indices += [ind, ind +1, ind+2, ind+3]
    buffer.currentIndex += 4


