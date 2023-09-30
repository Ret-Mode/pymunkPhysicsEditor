from typing import Tuple

class TextureContainerI:

    _instance: "TextureContainerI" = None

    @staticmethod
    def getInstance() -> "TextureContainerI":
        raise NotImplementedError
    
    def load(self, path:str, textureIndex:int, size:Tuple[int]):
        raise NotImplementedError

    def use(self, textureIndex:int, onChannel:int):
        raise NotImplementedError
    
    def setNext(self):
        raise NotImplementedError
            
    def setPrev(self):
        raise NotImplementedError
    
    def getCurrent(self):
        raise NotImplementedError
    
    def getSize(self, textureIndex):
        raise NotImplementedError
    