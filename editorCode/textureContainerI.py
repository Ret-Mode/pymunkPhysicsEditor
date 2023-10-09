from typing import List, Tuple

from .textureMapping import TextureMapping

class TextureContainerI:

    _instance: "TextureContainerI" = None

    @staticmethod
    def getInstance() -> "TextureContainerI":
        assert TextureContainerI._instance is not None
        return TextureContainerI._instance

    def deleteTexture(self, texture):
        raise NotImplementedError
    
    def loadTexture(self, path:str) -> any:
        raise NotImplementedError

    def use(self, textureIndex:int, onChannel:int):
        raise NotImplementedError

    def __init__(self, elems):
        self.elems = elems
        self.paths: List[str] = ['' for i in range(self.elems)]
        self.textures: List[any] = [None for i in range(self.elems)]
        self.sizes: List[Tuple[int]] = [(0,0) for i in range(self.elems)] 
        self.current = -1

    def load(self, path:str, textureIndex:int, size:Tuple[int]):
        if 0 <= textureIndex < self.elems:
            texture = self.loadTexture(path)
            if texture:
                if self.textures[textureIndex] is not None:
                    self.deleteTexture(self.textures[textureIndex])
                self.paths[textureIndex] = path
                self.textures[textureIndex] = texture
                self.sizes[textureIndex] = size

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
    
    def getCurrent(self) -> int:
        if 0 <= self.current <= self.elems:
            return self.current
        return None
    
    def getCurrentPath(self) -> str:
        if 0 <= self.current <= self.elems:
            return self.paths[self.current]
        return None

    def getSize(self, textureIndex) -> Tuple[int]:
        if 0 <= self.current <= self.elems:
            return self.sizes[textureIndex]
        return None
            