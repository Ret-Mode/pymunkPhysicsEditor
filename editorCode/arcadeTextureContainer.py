import arcade
from arcade.gl.texture import Texture

from typing import List, Tuple

from .textureContainerI import TextureContainerI


class ArcadeTexture(TextureContainerI):

    @staticmethod
    def getInstance() -> TextureContainerI:
        if TextureContainerI._instance is None:
            TextureContainerI._instance = ArcadeTexture()
        return TextureContainerI._instance

    def __init__(self, elems=16):
        self.ctx = arcade.get_window().ctx
        super().__init__(elems)

    def _loadTexture(self, path:str) -> Texture:
        return self.ctx.load_texture(path)

    def _deleteTexture(self, texture:Texture):
        texture.delete()
    
    def use(self, textureIndex:int, onChannel:int):
        if 0 <= textureIndex < self.elems:
            texture:Texture = self.textures[textureIndex]
            texture.use(onChannel)