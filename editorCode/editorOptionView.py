from .editorCamera import EditorCamera
from .editorCursor import Cursor
from .database import Database
from .commandExec import CommandExec

from ctypes import *


class EditorOptionView:

    def __init__(self, width, height, cursor:Cursor):
        self.cursor = cursor

    def update(self):
        pass

    def draw(self):
        pass

