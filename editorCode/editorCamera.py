from .editorTypes import V2, BoundingBox
from .editorCursor import Cursor

from typing import Tuple


# TODO cleanup cursor view
class CursorCamera:

    def __init__(self, width: float, height: float):
        self.sizeInPixels: V2 = V2(width, height)
        self.offset: V2 = V2(0.0, 0.0)
        self.mat: Tuple[float] = None
        self.viewport: Tuple[float] = None
        self.setMatrix(width, height)
        self.setViewport()
    
    def setMatrix(self, realWidth, realHeight) -> None:
        self.mat = (2.0/(realWidth), 0.0,   0.0, 0.0,
                            0.0, 2.0/(realHeight), 0.0, 0.0,
                            0.0, 0.0, -2.0 / (200.0)           , 0.0,
                            - (realWidth) / realWidth, - (realHeight) / realHeight, 0.0, 1.0)

    def setViewport(self):
        self.viewport = (0.0, 
                         0.0, 
                         self.sizeInPixels.x, 
                         self.sizeInPixels.y)

    def resize(self, x: int, y: int) -> None:
        self.sizeInPixels.x = x
        self.sizeInPixels.y = y
        self.setMatrix(x, y)
        self.setViewport()
        

class EditorCamera:

    def __init__(self, width: float, height: float, offsetX:float = 0.0, offsetY:float = 0.0) -> None:
        self.scaleLimit = 0.0001
        self.viewportSize: V2 = V2(width, height)
        self.viewportOffset: V2 = V2(offsetX, offsetY)
        self.sizeScaled: V2 = V2(width, height)
        self.scale: float = 2.0 / min(width, height)
        self.offsetScaled: V2 = V2(-width/2, -height/2).sS(self.scale)
        self.mat: Tuple[float] = None
        self.viewport: Tuple[float] = None
        
        self.setMatrix(width, height)
        self.setViewport()

    def setViewport(self):
        self.viewport = (self.viewportOffset.x, 
                         self.viewportOffset.y, 
                         self.viewportSize.x, 
                         self.viewportSize.y)

    def setMatrix(self, realWidth, realHeight) -> None:
        self.mat = (2.0/(realWidth), 0.0,   0.0, 0.0,
                            0.0, 2.0/(realHeight), 0.0, 0.0,
                            0.0, 0.0, -2.0 / (200.0)           , 0.0,
                            - (2.0 * self.offsetScaled.x + realWidth) / realWidth, - (2.0 * self.offsetScaled.y + realHeight) / realHeight, 0.0, 1.0)

    def changeScale(self, dy:float, cursorWorld: V2) -> None:
        scaleOld: float = self.scale
        if dy > 0.0:
            newScale: float = self.scale * 0.9
        else:
            newScale: float = self.scale * 1.0 / 0.9
        if newScale > self.scaleLimit:
            self.scale = newScale
            self.offsetScaled.unTV(cursorWorld).unSS(scaleOld).sS(self.scale).tV(cursorWorld)
            self.sizeScaled.setFromV(self.viewportSize).sS(self.scale)
        self.setMatrix(self.sizeScaled.x, self.sizeScaled.y)
        self.setViewport()

    def resize(self, x: int, y: int,  offsetX:float = 0.0, offsetY:float = 0.0) -> None:
        dx: float = self.scale * (self.viewportSize.x - x) / 2.0
        dy: float = self.scale * (self.viewportSize.y - y) / 2.0
        self.offsetScaled.tD(dx, dy)
        self.viewportSize.x = x
        self.viewportSize.y = y
        self.viewportOffset.x = offsetX
        self.viewportOffset.y = offsetY
        self.sizeScaled.setFromV(self.viewportSize).sS(self.scale)
        self.setMatrix(self.sizeScaled.x, self.sizeScaled.y)
        self.setViewport()

    def move(self, dx:float, dy:float) -> None:
        self.offsetScaled.tD(dx * self.scale, dy * self.scale)
        self.setMatrix(self.sizeScaled.x, self.sizeScaled.y)
        self.setViewport()

    def cusorToView(self, cursor: Cursor) -> None:
        cursor.viewCoords.setFromV(cursor.screenCoords).unTV(self.viewportOffset).sS(self.scale).tV(self.offsetScaled)

    def coordsInView(self, x:float, y:float):
        return (self.viewportOffset.x < x < self.viewportOffset.x + self.viewportSize.x) and (self.viewportOffset.y < y < self.viewportOffset.y + self.viewportSize.y)
    
    def fitToBox(self, box:BoundingBox):
        boxWidth = box.halfWH.final.x * 2.1
        boxHeight = box.halfWH.final.y * 2.1
        scale = max(boxWidth / self.viewportSize.x, boxHeight / self.viewportSize.y, self.scaleLimit)
        self.scale = scale
        self.sizeScaled.setFromV(self.viewportSize).sS(self.scale)

        dx:float = box.center.final.x - self.sizeScaled.x/2.0 
        dy:float = box.center.final.y - self.sizeScaled.y/2.0
        self.offsetScaled.setFromXY(dx, dy)

        self.setMatrix(self.sizeScaled.x, self.sizeScaled.y)
        self.setViewport()