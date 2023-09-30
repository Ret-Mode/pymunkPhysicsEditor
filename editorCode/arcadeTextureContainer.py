import arcade
from arcade.gl.texture import Texture

from typing import List, Tuple

from .textureContainerI import TextureContainerI
from .textureMapping import TextureMapping


class ArcadeTexture(TextureContainerI):

    @staticmethod
    def getInstance() -> TextureContainerI:
        if TextureContainerI._instance is None:
            TextureContainerI._instance = ArcadeTexture()
        return TextureContainerI._instance

    def __init__(self):
        self.elems = 16
        self.ctx = arcade.get_window().ctx
        self.paths: List[str] = [''] * self.elems
        self.textures: List[Texture] = [None] * self.elems
        self.sizes: List[Tuple[int]] = [(0,0)] * self.elems
        self.mappings: List[List[TextureMapping]] = [[]] * self.elems
        self.current = -1

    def load(self, path:str, textureIndex:int, size:Tuple[int]):
        if 0 <= textureIndex < self.elems:
            texture = self.ctx.load_texture(path)
            if texture:
                if self.textures[textureIndex] is not None:
                    self.textures[textureIndex].delete()
                self.paths[textureIndex] = path
                self.textures[textureIndex] = texture
                self.sizes[textureIndex] = size
                print('loaded', path, 'at index', textureIndex)

    def use(self, textureIndex:int, onChannel:int):
        
        if 0 <= textureIndex < self.elems:
            print('texture used')
            self.textures[textureIndex].use(onChannel)

    def setNext(self):
        if self.current < 0:
            for textureIndex in range(self.elems):
                if self.textures[textureIndex] is not None:
                    self.current = textureIndex
                    return
        else:
            for textureIndex in range(self.current + 1, self.elems):
                if self.textures[textureIndex] is not None:
                    self.current = textureIndex
                    return
            for textureIndex in range(self.current):
                if self.textures[textureIndex] is not None:
                    self.current = textureIndex
                    return
            
    def setPrev(self):
        if self.current < 0:
            for textureIndex in range(self.elems):
                if self.textures[self.elems - 1 - textureIndex] is not None:
                    self.current = self.elems - 1 - textureIndex
                    return
        else:
            for textureIndex in range(0, self.current):
                if self.textures[self.current - 1 - textureIndex] is not None:
                    self.current = self.current - 1 - textureIndex
                    return
            for textureIndex in range(self.current + 1, self.elems):
                if self.textures[self.elems - textureIndex + self.current] is not None:
                    self.current = self.elems - textureIndex + self.current
                    return
    
    def getCurrent(self):
        if 0 <= self.current <= self.elems:
            return self.current
        return None
    
    def getSize(self, textureIndex):
        if 0 <= self.current <= self.elems:
            return self.sizes[textureIndex]
        return None
            