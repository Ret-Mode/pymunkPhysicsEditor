import arcade
import pyglet
from pyglet.math import Mat4
import math

from .config import pointConfig, editorButtonSetup
from .editorTypes import V2, EditorPoint, UnboundAngle

from .shapeInternals.editorBodyI import BodyI
from .shapeInternals.editorShapeI import ShapeI
from typing import List, Tuple



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
        arcade.draw_circle_outline(point.x, point.y, pointConfig['armLength'], pointConfig['anchorColor'], _shaderScale, num_segments=32)
    else:
        circleParts = -rate.angle / 32.0
        sin = math.sin(circleParts)
        cos = math.cos(circleParts)
        x = pointConfig['armLength']
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
        arcade.draw_circle_outline(point.x, point.y, pointConfig['armLength'], pointConfig['anchorColor'], _shaderScale, num_segments=32)
    else:
        circleParts = rate.angle / 32.0
        sin = math.sin(circleParts)
        cos = math.cos(circleParts)
        x = pointConfig['armLength']
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
        x = pointConfig['armLength'] * minPhase.cos
        y = pointConfig['armLength'] * minPhase.sin
        
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
        arcade.draw_circle_outline(point.x, point.y, pointConfig['armLength'], pointConfig['anchorColor'], _shaderScale, num_segments=32)
    else:
        circleParts = angle / 32.0
        sin = math.sin(circleParts)
        cos = math.cos(circleParts)
        x = pointConfig['armLength'] * minPhase.cos
        y = - pointConfig['armLength'] * minPhase.sin
        
        for i in range(32):
            nX = x * cos + y * sin
            nY = -x * sin + y * cos
            arcade.draw_line(point.x + x, point.y + y,
                             point.x + nX, point.y + nY,
                             pointConfig['anchorColor'], _shaderScale)
            x, y = nX, nY


def drawSpring(frm:V2, to:V2, restLength:float):
    #drawEdge(frm, to, pointConfig['anchorColor'])
    realLength = frm.distV(to)
    if realLength != 0.0:
        diffLength = (realLength - restLength) / realLength
        diffX = (to.x - frm.x)*diffLength
        diffY = (to.y - frm.y)*diffLength
        drawEdgeXY(frm.x + diffX/2, frm.y + diffY/2, frm.x, frm.y,
                    pointConfig['anchorColor'])
        drawPointXY(frm.x + diffX/2, frm.y + diffY/2,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * _shaderScale)
        drawEdgeXY(to.x - diffX/2, to.y - diffY/2, to.x, to.y,
                    pointConfig['anchorColor'])
        drawPointXY(to.x - diffX/2, to.y - diffY/2,
                    pointConfig['anchorColor'], pointConfig['pointHalfWH'] * _shaderScale)
    else:
        arcade.draw_circle_outline(to.x, to.y, restLength/2.0, pointConfig['anchorColor'], _shaderScale, num_segments=32)

def drawRatchetA(posA:V2, ratchet:UnboundAngle):
    x = pointConfig['ratchetArmLength'] * ratchet.cos
    y = pointConfig['ratchetArmLength'] * ratchet.sin
    drawPointXY(posA.x + x, posA.y + y, pointConfig['secondaryBodyColor'], pointConfig['pointHalfWH'])

def drawRatchetB(posB:V2, phase:UnboundAngle, ratchet:UnboundAngle):
    x = pointConfig['ratchetArmLength'] * math.cos(phase.angle - ratchet.angle)
    y = pointConfig['ratchetArmLength'] * math.sin(phase.angle - ratchet.angle)
    drawPointXY(posB.x + x, posB.y + y, pointConfig['secondaryBodyColor'], pointConfig['pointHalfWH'])

def drawAngleArm(point:V2, dX:float, dY:float):
    armLength: float = pointConfig['armLength']
    arcade.draw_line(point.x, point.y, 
                     point.x + armLength*dX*_shaderScale, point.y + armLength*dY*_shaderScale, 
                     pointConfig['anchorColor'], _shaderScale)
    
def drawAngleRatioArm(point:V2, dX:float, dY:float, ratio:float):
    armLength: float = pointConfig['armLength']
    ratioLength = armLength / ratio
    offsetX = point.x + armLength*dX*_shaderScale
    offsetY = point.y + armLength*dY*_shaderScale
    
    arcade.draw_line(offsetX, offsetY, 
                     offsetX + ratioLength * dY*_shaderScale, offsetY - ratioLength * dX * _shaderScale, 
                     pointConfig['anchorColor'], _shaderScale)

def drawAngleArm(point:V2, dX:float, dY:float):
    armLength: float = pointConfig['armLength']
    arcade.draw_line(point.x, point.y, 
                     point.x + armLength*dX*_shaderScale, point.y + armLength*dY*_shaderScale, 
                     pointConfig['anchorColor'], _shaderScale)


def drawPivot(pointA:V2, pointB:V2):
    if pointA.distSqrV(pointB) != 0.0:
        drawEdge(pointA, pointB, pointConfig['anchorColor'])
        x = pointA.x + (pointB.x - pointA.x)/2.0
        y = pointA.y + (pointB.y - pointA.y)/2.0
        drawPointXY(x, y, pointConfig['anchorColor'], pointConfig['pointHalfWH'] * _shaderScale)

def drawGroove(pointA:V2, pointB:V2):
    drawPoint(pointA, pointConfig['grooveColor'], pointConfig['pointHalfWH'] * _shaderScale)   
    drawPoint(pointB, pointConfig['grooveColor'], pointConfig['pointHalfWH'] * _shaderScale)
    drawEdge(pointA, pointB, pointConfig['grooveColor'])
    

def drawAnchor(point:V2):
    drawPoint(point, pointConfig['anchorColor'], pointConfig['pointHalfWH'] * _shaderScale)    

def drawDiamond(point:V2, color, halfWH:float):
    arcade.draw_line(point.x + halfWH, point.y,          point.x,          point.y + halfWH, color, _shaderScale)
    arcade.draw_line(point.x,          point.y + halfWH, point.x - halfWH, point.y,          color, _shaderScale)
    arcade.draw_line(point.x - halfWH, point.y,          point.x,          point.y - halfWH, color, _shaderScale)
    arcade.draw_line(point.x,          point.y - halfWH, point.x + halfWH, point.y,          color, _shaderScale)

def drawPoint(point:V2, color, halfWH:float):
    arcade.draw_lrtb_rectangle_outline(point.x-halfWH, point.x+halfWH, 
                                       point.y+halfWH, point.y-halfWH, color, _shaderScale)

def drawPointXY(x:float, y:float, color, halfWH:float):
    arcade.draw_lrtb_rectangle_outline(x-halfWH, x+halfWH, 
                                       y+halfWH, y-halfWH, color, _shaderScale)
  

def drawEdge(frm:V2, to:V2, color):
    arcade.draw_line(frm.x, frm.y, to.x, to.y, color, _shaderScale)

def drawEdgeXY(frmX:float, frmY:float, toX:float, toY:float, color):
    arcade.draw_line(frmX, frmY, toX, toY, color, _shaderScale)

def drawBBox(center:V2, halfWH:V2, color, offset:float):
    arcade.draw_lrtb_rectangle_outline(center.x - halfWH.x - offset, center.x + halfWH.x + offset, 
                                       center.y + halfWH.y + offset, center.y - halfWH.y - offset, color, _shaderScale)
    
def drawBody(body: BodyI, isActive:bool, isUnderCursor:bool):
    color = pointConfig['activeEdgeColor'] if isActive else (pointConfig['underCursorEdgeColor'] if isUnderCursor else pointConfig['inactivePointColor'])
    for shape in body.shapes:
        shape.draw()

    drawBBox(body.box.center.final, body.box.halfWH.final, color, pointConfig['pointHalfWH'] * _shaderScale)

    drawPoint(body.physics.cog.final, pointConfig['cogColor'], pointConfig['cogHalfWH'] * _shaderScale)

def drawShape(shape: ShapeI, isActive:bool, isUnderCursor:bool):
    color = pointConfig['activeEdgeColor'] if isActive else (pointConfig['underCursorEdgeColor'] if isUnderCursor else pointConfig['inactivePointColor'])
    shape.draw()

    drawBBox(shape.box.center.final, shape.box.halfWH.final, color, pointConfig['pointHalfWH'] * _shaderScale)

    drawPoint(shape.physics.cog.final, pointConfig['cogColor'], pointConfig['cogHalfWH'] * _shaderScale)
    #drawPoint(shape.transform.objectAnchor.final, pointConfig['anchorColor'], pointConfig['anchorHalfWH'])

def drawCircle(center:V2, halfWH:V2, elems:int):
    radius = halfWH.length()
    color = pointConfig['inactivePointColor']
    arcade.draw_circle_outline(center.x, center.y, radius, color, _shaderScale, num_segments=elems)
    arcade.draw_line(center.x, center.y, center.x + halfWH.x, center.y + halfWH.y, color, _shaderScale)

def drawLineShape(points: List[EditorPoint]):
    color = pointConfig['inactivePointColor']
    if points:
        point = points[0].final
        drawPoint(point, pointConfig['inactivePointColor'], pointConfig['pointHalfWH']* _shaderScale)
        for nextPoint in points[1:]:
            drawEdge(point, nextPoint.final, color)
            drawPoint(nextPoint.final, pointConfig['inactivePointColor'], pointConfig['pointHalfWH']* _shaderScale)
            point = nextPoint.final

def drawPolygon(points: List[EditorPoint]):
    color = pointConfig['inactivePointColor']
    if points:
        #prevPoint = poly.points[-1]
        prevPoint = points[-1].final
        for point in points:
            drawEdge(prevPoint, point.final, color)
            drawPoint(point.final, pointConfig['inactivePointColor'], pointConfig['pointHalfWH'] * _shaderScale)
            prevPoint = point.final

def drawBox(points: List[EditorPoint]):
    color = pointConfig['inactivePointColor']

    prevPoint = points[-1]
    for point in points[1:]:
        arcade.draw_line(prevPoint.final.x, prevPoint.final.y, 
                         point.final.x,     point.final.y, color, _shaderScale)
        drawPoint(prevPoint.final, color, pointConfig['pointHalfWH'] * _shaderScale)
        prevPoint = point

def drawRect(points: List[EditorPoint]):
    color = pointConfig['inactivePointColor']
    
    # TODO this to internal rect state
    prevPoint = points[-1]
    for point in points[1:]:
        arcade.draw_line(prevPoint.final.x, prevPoint.final.y, 
                         point.final.x,     point.final.y, color, _shaderScale)
        drawPoint(prevPoint.final, color, pointConfig['pointHalfWH'] * _shaderScale)
        prevPoint = point

    
def drawHelperPoint(point:V2):
    drawDiamond(point, pointConfig['helperColor'], pointConfig['helperHalfWH'] * _shaderScale)

def drawCursor(cursor:V2):
    color = pointConfig['cursorLineColor']
    if cursor.x >= _viewLimits.x - _menuDistance:
        color = pointConfig['cursorLineMenuColor']
    drawPoint(cursor, color, pointConfig['cursorHalfWH'] * _shaderScale)
    arcade.draw_line(_viewOffset.x, cursor.y, _viewOffset.x + _viewLimits.x + _menuDistance, cursor.y, color, _shaderScale)
    arcade.draw_line(cursor.x, _viewOffset.y, cursor.x, _viewOffset.y + _viewLimits.y, color, _shaderScale)

