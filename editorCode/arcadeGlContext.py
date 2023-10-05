import arcade
from pyglet.math import Mat4

from typing import Tuple

from .glContext import GLContextI

class ArcadeGLContext(GLContextI):

    @staticmethod
    def getInstance() -> GLContextI:
        if GLContextI._instance is None:
            GLContextI._instance = ArcadeGLContext()
        return GLContextI._instance

    def __init__(self):
        self.ctx = arcade.get_window().ctx

    def setProjection(self, projection:Tuple[float]):  
        self.ctx.projection_2d_matrix = Mat4(values=projection)
    
    def setViewport(self, viewport: Tuple[float]):
        self.ctx.viewport = viewport