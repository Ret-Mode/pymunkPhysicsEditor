class TextureContainerI:

    def load(self, path:str, textureIndex:int):
        raise NotImplementedError

    def use(self, textureIndex:int, onChannel:int):
        raise NotImplementedError