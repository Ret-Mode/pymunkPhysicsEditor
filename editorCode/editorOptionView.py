from .editorCamera import EditorCamera
from .editorCursor import Cursor
from .database import Database
from .commandExec import CommandExec, ComMoveCursor

from ctypes import *


class EditorOptionView:

    def __init__(self, width, height, cursor:Cursor):
        self.cursor = cursor
        self.view = EditorCamera(width, height)

    def update(self):
        CommandExec.process()

    def draw(self):
        pass

    def moveView(self, dx:float, dy:float):
        pass

    def changeScale(self, dy:float):
        pass

    def moveCursor(self, x:float, y:float):
        CommandExec.addCommand(ComMoveCursor(self.view, self.cursor, x, y))