import arcade
from arcade.gl.texture import Texture

from typing import List

from .textureContainerI import TextureContainerI



class ArcadeTexture(TextureContainerI):

    _instance: TextureContainerI = None

    @staticmethod
    def getInstance() -> TextureContainerI:
        if ArcadeTexture._instance is None:
            ArcadeTexture._instance = ArcadeTexture()
        return ArcadeTexture._instance

    def __init__(self):
        self.ctx = arcade.get_window().ctx
        self.paths: List[str] = [''] * 16
        self.textures: List[Texture] = [None] * 16

    def load(self, path:str, textureIndex:int):
        if 0 <= textureIndex < 16:
            texture = self.ctx.load_texture(path)
            if texture:
                if self.textures[textureIndex] is not None:
                    self.textures[textureIndex].delete()
                self.paths[textureIndex] = path
                self.textures[textureIndex] = texture
                print('loaded', path, 'at index', textureIndex)

    def use(self, textureIndex:int, onChannel:int):
        if 0 <= textureIndex < 16:
            self.textures[textureIndex].use(onChannel)