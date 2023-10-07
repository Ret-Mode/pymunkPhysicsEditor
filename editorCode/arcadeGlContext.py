import arcade
from pyglet.math import Mat4

from typing import Union

from .glContext import GLContextI
from .editorCamera import EditorCamera, CursorCamera

class ArcadeGLContext(GLContextI):

    @staticmethod
    def getInstance() -> GLContextI:
        if GLContextI._instance is None:
            GLContextI._instance = ArcadeGLContext()
        return GLContextI._instance

    def __init__(self):
        self.ctx = arcade.get_window().ctx

    def setProjectionAndViewportFromCamera(self, camera:Union[CursorCamera, EditorCamera]):
        self.ctx.projection_2d_matrix = Mat4(values=camera.mat)
        self.ctx.viewport = camera.viewport
