from typing import List, Tuple, Any

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

    def load(self, path:str, textureIndex:int, size:Tuple[int]):
        if 0 <= textureIndex < self.elems:
            texture = self.loadTexture(path)
            if texture:
                if self.textures[textureIndex] is not None:
                    self.deleteTexture(self.textures[textureIndex])
                self.paths[textureIndex] = path
                self.textures[textureIndex] = texture
                self.sizes[textureIndex] = size
    
    def getPath(self, textureIndex:int) -> str:
        if 0 <= textureIndex <= self.elems:
            return self.paths[textureIndex]
        return None

    def getTexture(self, textureIndex:int) -> Any:
        if 0 <= textureIndex <= self.elems:
            return self.textures[textureIndex]
        return None
    
    def getSize(self, textureIndex:int) -> Tuple[int]:
        if 0 <= textureIndex <= self.elems:
            return self.sizes[textureIndex]
        return None
            