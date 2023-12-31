from typing import List, Tuple, Any

from .textureMapping import TextureMapping

class TextureI:

    def read(self, level: int = 0, alignment: int = 1) -> bytearray:
        raise NotImplementedError

class TextureContainerI:

    _instance: "TextureContainerI" = None

    @staticmethod
    def getInstance() -> "TextureContainerI":
        assert TextureContainerI._instance is not None
        return TextureContainerI._instance

    def _deleteTexture(self, texture):
        raise NotImplementedError
    
    def _loadTexture(self, path:str) -> any:
        raise NotImplementedError

    def use(self, textureIndex:int, onChannel:int):
        raise NotImplementedError

    def __init__(self, elems):
        self.elems = elems
        self.nonEmptyChannels:List[int] = []
        self.paths: List[str] = ['' for i in range(self.elems)]
        self.textures: List[TextureI] = [None for i in range(self.elems)]
        self.sizes: List[Tuple[int]] = [(0,0) for i in range(self.elems)] 

    def updateNonEmptyList(self):
        self.nonEmptyChannels = list(filter(lambda x: self.paths[x], range(self.elems)))

    def deleteAll(self):
        for i in range(self.elems):
            self.delete(i)

    def delete(self, textureIndex:int):
        if 0 <= textureIndex < self.elems:
            if self.textures[textureIndex] is not None:
                self._deleteTexture(self.textures[textureIndex])
                self.sizes[textureIndex] = (0,0)
                self.paths[textureIndex] = ''
            self.updateNonEmptyList()

    def load(self, path:str, textureIndex:int, size:Tuple[int]):
        path = path.replace('\\\\','/').replace('\\','/')
        if 0 <= textureIndex < self.elems:
            texture = self._loadTexture(path)
            if texture:
                if self.textures[textureIndex] is not None:
                    self._deleteTexture(self.textures[textureIndex])
                self.paths[textureIndex] = path
                self.textures[textureIndex] = texture
                self.sizes[textureIndex] = size
        self.updateNonEmptyList()
    
    def getPath(self, textureIndex:int) -> str:
        if 0 <= textureIndex <= self.elems:
            return self.paths[textureIndex]
        return None

    def getTexture(self, textureIndex:int) -> TextureI:
        if 0 <= textureIndex <= self.elems:
            return self.textures[textureIndex]
        return None
    
    def getSize(self, textureIndex:int) -> Tuple[int]:
        if 0 <= textureIndex <= self.elems:
            return self.sizes[textureIndex]
        return None

    def getJSONDict(self, parent:dict):
        for i in range(self.elems):
            if self.paths[i]:
                tmp = {}
                tmp['path'] = self.paths[i].replace('\\\\','/').replace('\\','/')
                tmp['size'] = [self.sizes[i][0], self.sizes[i][1]]
                parent[str(i)] = tmp