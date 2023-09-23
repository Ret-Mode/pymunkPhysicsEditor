
from .editorCursor import Cursor
from .editorCamera import EditorCamera
from .editorTypes import EditorPoint
from .editorViewTransform import ContinuousTransform

from .commandExec import CommandExec
from .commandExec import ComResizeView, ComMoveCursor, ComMoveView, ComScaleView

class EditorTextureView:

    def __init__(self, width, height, cursor:Cursor):
        self.viewOffset = EditorCamera(width, height)
        self.cursor = cursor
        self.pivot = EditorPoint()

        self.transform = ContinuousTransform()

    def resize(self, x:float, y:float):
        CommandExec.addCommand(ComResizeView(self.viewOffset, x, y))

    def moveView(self, dx:float, dy:float):
        CommandExec.addCommand(ComMoveView(self.viewOffset, dx, dy))

    def changeScale(self, dy:float):
        CommandExec.addCommand(ComScaleView(self.viewOffset, self.cursor.viewCoords, dy))

    def moveCursor(self, x:float, y:float):
        CommandExec.addCommand(ComMoveCursor(self.viewOffset, self.cursor, x, y))

    def update(self):
        CommandExec.process()

    def draw(self):
        pass