import math
from typing import Tuple


class UserSettableFloat:

    def __init__(self, value:float):
        self.calc: float = value
        self.user: float = 0.0
        self.final: float = 0.0
        self.userDefined: bool = False
    
    def setFromUser(self, value: float):
        self.user = value
        self.userDefined = True

    def resetToCalc(self) -> None:
        self.userDefined = False

    def get(self) -> float:
        return self.final
    

class Angle:

    def _sanitize(self) -> None:
        while self.angle > math.pi:
            self.angle -= 2 * math.pi
        while self.angle < -math.pi:
            self.angle += 2 * math.pi

    def recalc(self):
        self._sanitize()
        self.sin = math.sin(self.angle)
        self.cos = math.cos(self.angle)

    def __init__(self, angle:float=0.0) -> None:
        self.set(angle)

    def add(self, angle: float) -> "Angle":
        self.angle += angle
        self.recalc()
        return self

    def sub(self, angle:float):
        self.angle -= angle
        self.recalc()
        return self
        

    def set(self, angle:float) -> "Angle":
        self.angle = angle
        self.recalc()
        return self
    
    def setA(self, angle:"Angle") -> "Angle":
        self.angle = angle.angle
        self.sin = angle.sin
        self.cos = angle.cos
        return self

    def atan2(self, dy:float, dx:float) -> "Angle":
        self.angle = math.atan2(dy, dx)
        self.recalc()
        return self

    def deg(self) -> float:
        return self.angle * 180.0 / math.pi
    
    def fromDeg(self, deg) -> "Angle":
        self.set(deg * math.pi / 180.0)
        return self

    def clone(self) -> "Angle":
        return Angle(self.angle)
    
    def __str__(self) -> str:
        return f'{self.angle}'


class UnboundAngle(Angle):

    def _sanitize(self) -> None:
        pass


class V2:

    def __init__(self, x:float = 0.0, y: float = 0.0) -> None:
        self.x: float = x
        self.y: float = y

    def rA(self, angle: Angle) -> "V2":
        x:float = self.x * angle.cos - self.y * angle.sin
        y:float = self.x * angle.sin + self.y * angle.cos
        self.x = x
        self.y = y
        return self

    def unRA(self, angle: Angle) -> "V2":
        x: float =   self.x * angle.cos + self.y * angle.sin
        y: float = - self.x * angle.sin + self.y * angle.cos
        self.x = x
        self.y = y
        return self

    def tD(self, dx: float, dy: float) -> "V2":
        x: float = self.x + dx
        y: float = self.y + dy
        self.x = x
        self.y = y
        return self
    
    def tV(self, v: "V2") -> "V2":
        x: float = self.x + v.x
        y: float = self.y + v.y
        self.x = x
        self.y = y
        return self
    
    def unTD(self, dx: float, dy: float) -> "V2":
        x: float = self.x - dx
        y: float = self.y - dy
        self.x = x
        self.y = y
        return self
    
    def unTV(self, v: "V2") -> "V2":
        x: float = self.x - v.x
        y: float = self.y - v.y
        self.x = x
        self.y = y
        return self

    def sD(self, sx: float, sy: float) -> "V2":
        x: float = self.x * sx
        y: float = self.y * sy
        self.x = x
        self.y = y
        return self
    
    def sS(self, s) -> "V2":
        x: float = self.x * s
        y: float = self.y * s
        self.x = x
        self.y = y
        return self
    
    def sV(self, v: "V2") -> "V2":
        x: float = self.x * v.x
        y: float = self.y * v.y
        self.x = x
        self.y = y
        return self

    def unSD(self, sx: float, sy: float) -> "V2":
        x: float = self.x / sx
        y: float = self.y / sy
        self.x = x
        self.y = y
        return self

    def unSS(self, s: float) -> "V2":
        x: float = self.x / s
        y: float = self.y / s
        self.x = x
        self.y = y
        return self

    def unSV(self, v: "V2") -> "V2":
        x: float = self.x / v.x
        y: float = self.y / v.y
        self.x = x
        self.y = y
        return self

    def setFromV(self, v: "V2") -> "V2":
        self.x = v.x
        self.y = v.y
        return self
    
    def setFromXY(self, x: float, y: float) -> "V2":
        self.x = x
        self.y = y
        return self

    def dotV(self, v: "V2") -> float:
        return self.x * v.x + self.y * v.y

    def dotVV(self, src:"V2", to:"V2") -> float:
        return (src.x - self.x) * (to.x - self.x) + (src.y - self.y) * (to.y - self.y)

    def crossV(self, v: "V2") -> float:
        return self.x * v.y - v.x * self.y

    def crossVV(self, src:"V2", to:"V2") -> float:
        return (src.x - self.x) * (to.y - self.y) - (src.y - self.y) * (to.x - self.x)

    def distV(self, v: "V2") -> float:
        return math.sqrt((self.x - v.x) * (self.x - v.x) + (self.y - v.y) * (self.y - v.y))

    def distXY(self, x: float, y: float) -> float:
        return math.sqrt((self.x - x) * (self.x - x) + (self.y - y) * (self.y - y))
    
    def distSqrV(self, v: "V2") -> float:
        return (self.x - v.x) * (self.x - v.x) + (self.y - v.y) * (self.y - v.y)

    def distSqrXY(self, x: float, y: float) -> float:
        return (self.x - x) * (self.x - x) + (self.y - y) * (self.y - y)
    
    def crossPerpV(self, v: "V2") -> float:
        return - self.x * v.y + v.x * self.y

    def crossPerpVV(self, src:"V2", to:"V2") -> float:
        return - (src.x - self.x) * (to.y - self.y) + (src.y - self.y) * (to.x - self.x)

    def perp(self) -> "V2":
        x = self.x
        y = self.y
        self.x = -y
        self.y = x
        return self

    def unPerp(self) -> "V2":
        x = self.x
        y = self.y
        self.x = y
        self.y = -x
        return self
    
    def atan2(self) -> float:
        return math.atan2(self.y, self.x)
    
    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def lengthSqr(self) -> float:
        return self.x * self.x + self.y * self.y

    def clone(self) -> "V2":
        return V2(self.x, self.y)
    
    def __str__(self) -> str:
        return f'{self.x} {self.y}'


class Radius:

    def __init__(self, value:float):
        self.final = value

    def get(self):
        return self.final
    
    def set(self, value:float):
        self.final = value


class CircleRadius(Radius):

    def __init__(self, value):
        super().__init__(value)
        self.base: float = value

    def update(self, final:"Mat"):
        vals = final.mulRSXY(self.base, 0.0)
        self.final = math.sqrt(vals[0] ** 2 + vals[1] ** 2)
    
    def set(self, value:float):
        self.base = value


class Mat:

    _eye: "Mat" = None

    @staticmethod
    def Eye() -> "Mat":
        if Mat._eye is None:
            Mat._eye = Mat()
        return Mat._eye

    def __init__(self):
        self.r0c0 = 1.0
        self.r0c1 = 0.0
        self.r0c2 = 0.0
        self.r1c0 = 0.0
        self.r1c1 = 1.0
        self.r1c2 = 0.0

    def mulBy(self, by: "Mat") -> "Mat":
        r0c0 = self.r0c0 * by.r0c0 + self.r0c1 * by.r1c0
        r0c1 = self.r0c0 * by.r0c1 + self.r0c1 * by.r1c1
        r0c2 = self.r0c0 * by.r0c2 + self.r0c1 * by.r1c2 + self.r0c2
        r1c0 = self.r1c0 * by.r0c0 + self.r1c1 * by.r1c0
        r1c1 = self.r1c0 * by.r0c1 + self.r1c1 * by.r1c1
        r1c2 = self.r1c0 * by.r0c2 + self.r1c1 * by.r1c2 + self.r1c2
        self.r0c0 = r0c0
        self.r0c1 = r0c1
        self.r0c2 = r0c2
        self.r1c0 = r1c0
        self.r1c1 = r1c1
        self.r1c2 = r1c2
        return self

    def mulPre(self, by: "Mat") -> "Mat":
        r0c0 = by.r0c0 * self.r0c0 + by.r0c1 * self.r1c0
        r0c1 = by.r0c0 * self.r0c1 + by.r0c1 * self.r1c1
        r0c2 = by.r0c0 * self.r0c2 + by.r0c1 * self.r1c2 + by.r0c2
        r1c0 = by.r1c0 * self.r0c0 + by.r1c1 * self.r1c0
        r1c1 = by.r1c0 * self.r0c1 + by.r1c1 * self.r1c1
        r1c2 = by.r1c0 * self.r0c2 + by.r1c1 * self.r1c2 + by.r1c2
        self.r0c0 = r0c0
        self.r0c1 = r0c1
        self.r0c2 = r0c2
        self.r1c0 = r1c0
        self.r1c1 = r1c1
        self.r1c2 = r1c2
        return self

    def set(self, frm: "Mat") -> "Mat":
        self.r0c0 = frm.r0c0
        self.r0c1 = frm.r0c1
        self.r0c2 = frm.r0c2
        self.r1c0 = frm.r1c0
        self.r1c1 = frm.r1c1
        self.r1c2 = frm.r1c2
        return self

    def mulV(self, src:V2, dest:V2):
        x = self.r0c0 * src.x + self.r0c1 * src.y + self.r0c2
        y = self.r1c0 * src.x + self.r1c1 * src.y + self.r1c2
        dest.setFromXY(x,y)
        return dest

    def mulRSV(self, src:V2, dest:V2):
        x = self.r0c0 * src.x + self.r0c1 * src.y
        y = self.r1c0 * src.x + self.r1c1 * src.y
        dest.setFromXY(x,y)
        return dest

    def mulXY(self, x: float, y: float) -> Tuple[float]:
        dx = self.r0c0 * x + self.r0c1 * y + self.r0c2
        dy = self.r1c0 * x + self.r1c1 * y + self.r1c2
        return (dx, dy)
    
    def mulRSXY(self, x: float, y: float) -> Tuple[float]:
        dx = self.r0c0 * x + self.r0c1 * y
        dy = self.r1c0 * x + self.r1c1 * y
        return (dx, dy)

    def setFromAAS(self, anchor:V2, angle:Angle, scale:float) -> "Mat":
        self.r0c0 =   angle.cos * scale
        self.r0c1 = - angle.sin * scale
        self.r0c2 =   anchor.x
        self.r1c0 =   angle.sin * scale
        self.r1c1 =   angle.cos * scale
        self.r1c2 =   anchor.y
        return self
    
    def setFromAASInv(self, anchor:V2, angle:Angle, scale:float) -> "Mat":
        if scale == 0.0:
            scale = 0.0000001
        self.r0c0 =   angle.cos / scale
        self.r0c1 =   angle.sin / scale
        self.r0c2 = - anchor.x * self.r0c0 - anchor.y * self.r0c1
        self.r1c0 = - angle.sin / scale
        self.r1c1 =   angle.cos / scale
        self.r1c2 = - anchor.x * self.r1c0 - anchor.y * self.r1c1
        return self
    
    def setFromView(self, offset:V2, scale:float) -> "Mat":
        self.r0c0 =  1.0/scale
        self.r0c1 = 0.0
        self.r0c2 = - offset.x * 1.0/scale
        self.r1c0 = 0.0
        self.r1c1 = 1.0/scale
        self.r1c2 = - offset.y * 1.0/scale
        return self
    

class ContainerTransform:
    
    def __init__(self):
        self.mat: Mat = Mat()
        self.objectAnchor = V2()
        self.objectAngle = Angle()
        self.objectScale = 1.0

    def rotate(self, angle: Angle, pivot: V2):
        self.objectAngle.add(angle.angle)
        self.objectAnchor.unTV(pivot).rA(angle).tV(pivot)

    def rotateScale(self, angle: Angle, scale:float, pivot: V2):
        self.objectAngle.add(angle.angle)
        self.objectScale *=  scale
        self.objectAnchor.unTV(pivot).rA(angle).sS(scale).tV(pivot)

    def move(self, dV:V2) -> None:
        self.objectAnchor.tV(dV)

    def scale(self, scale:float, pivot:V2) -> None:
        self.objectScale *=  scale
        self.objectAnchor.unTV(pivot).sS(scale).tV(pivot)

    def invRotate(self, angle: Angle, pivot: V2):
        self.objectAngle.sub(angle.angle)
        self.objectAnchor.unTV(pivot).unRA(angle).tV(pivot)

    def invRotateScale(self, angle: Angle, scale:float, pivot: V2):
        self.objectAngle.sub(angle.angle)
        self.objectScale /=  scale
        self.objectAnchor.unTV(pivot).unRA(angle).unSS(scale).tV(pivot)

    def invMove(self, dV:V2) -> None:
        self.objectAnchor.unTV(dV)

    def invScale(self, scale:float, pivot:V2) -> None:
        self.objectScale /=  scale
        self.objectAnchor.unTV(pivot).unSS(scale).tV(pivot)

    def getMat(self) -> Mat:
        return self.mat.setFromAAS(self.objectAnchor, self.objectAngle, self.objectScale)
    
    def getInvMat(self) -> Mat:
        return self.mat.setFromAASInv(self.objectAnchor, self.objectAngle, self.objectScale)
    

class EditorPoint:

    def __init__(self, x:float = 0,  y:float = 0) -> None:
        self.local: V2 = V2(x, y)
        self.final: V2 = V2()

    def toScreen(self, viewOffset:V2, viewScale:float) -> None:
        self.final.setFromV(self.local).unTV(viewOffset).unSS(viewScale)

    def closeToWorldXY(self, wx:float, wy:float, distance:float) -> bool:
        dx: float = wx - self.local.x
        dy: float = wy - self.local.y
        return (dx*dx < distance*distance) and (dy*dy < distance*distance)

    def closeToScreenXY(self, sx:float, sy:float, distance:float) -> bool:
        dx: float = sx - self.final.x
        dy: float = sy - self.final.y
        return (dx*dx < distance*distance) and (dy*dy < distance*distance)
    
    def setFromEP(self, editorPoint: "EditorPoint") -> None:
        self.local.setFromV(editorPoint.local)
        self.final.setFromV(editorPoint.final)
        return self


class OffsetPoint:

    def __init__(self):
        self.offset:V2 = V2()
        self.local: V2 = V2()
        self.final: V2 = V2()

    def calcOffset(self, mat:Mat, center:V2):
        mat.mulRSV(self.offset, self.local)
        self.final.setFromV(self.local).tV(center)
    

class BoundingBox:

    def __init__(self) -> None:
        self.center = EditorPoint()
        self.halfWH = EditorPoint()

    def setFinal(self, xMin:float, yMin:float, xMax:float, yMax:float) -> None:
        self.halfWH.final.setFromXY((xMax-xMin)/2.0, (yMax-yMin)/2.0)
        self.center.final.setFromXY((xMax-xMin)/2 + xMin, (yMax-yMin)/2.0 + yMin)


class CenterOfGravity:

    def __init__(self) -> None:
        self.calc: V2 = V2()
        self.user: V2 = V2()
        self.final: V2 = V2()
        self.userDefined: bool = False
    
    def setFromUserXY(self, x: float, y:float):
        self.userDefined = True
        self.user.x = x
        self.user.y = y

    def setFromUserV(self, value:V2):
        self.userDefined = True
        self.user.setFromV(value)

    def resetToCalc(self) -> None:
        self.userDefined = False

    def get(self) -> V2:
        return self.final


class Selection:

    def __init__(self):
        self.start:V2 = V2()
        self.end:V2 = V2()
        self.active: bool = False

    def isActive(self) -> bool:
        return self.active
    
    def begin(self, point:V2):
        self.start.setFromV(point)
        self.end.setFromV(point)
        self.active = True

    def update(self, point:V2):
        self.end.setFromV(point)

    def stop(self):
        self.active = False