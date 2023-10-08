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
        print('Opengl context:', self.ctx.info.VENDOR, self.ctx.info.MAJOR_VERSION ,self.ctx.info.MINOR_VERSION)
        print('Texture image units:', self.ctx.info.MAX_TEXTURE_IMAGE_UNITS)
        print('Framebuffer size:', self.getFramebufferSize())

    def setProjectionAndViewportFromCamera(self, camera:Union[CursorCamera, EditorCamera]):
        self.ctx.projection_2d_matrix = Mat4(values=camera.mat)
        self.ctx.viewport = camera.viewport

    def getFramebufferSize(self):
        return self.ctx.active_framebuffer.size
