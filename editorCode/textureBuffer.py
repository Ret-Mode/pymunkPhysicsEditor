from typing import List
import math
from typing import List

from .config import pointConfig, physicsSetup
from .editorTypes import V2, EditorPoint, UnboundAngle
from .textureMapping import TextureMapping

class TextureBuffer:

    _instance: "TextureBuffer" = None

    @staticmethod
    def getInstance() -> "TextureBuffer":
        if TextureBuffer._instance == None:
            TextureBuffer._instance = TextureBuffer()
        return TextureBuffer._instance
    
    def __init__(self):
        # TODO - fix scaling
        self.drawScale:float = physicsSetup['pixelPerMeter']
        self.verts: List[float] = []
        self.uvs: List[float] = []
        self.indices: List[int] = []
        self.currentIndex: int = 0

    def reset(self):
        self.drawScale:float = physicsSetup['pixelPerMeter']
        self.verts: List[float] = []
        self.uvs: List[float] = []
        self.indices: List[int] = []
        self.currentIndex: int = 0

    def addBaseQuad(self, width, height):
        ind = self.currentIndex
        self.verts += [-width/(2*self.drawScale), -height/(2*self.drawScale), 
                       width/(2*self.drawScale), -height/(2*self.drawScale), 
                       -width/(2*self.drawScale), height/(2*self.drawScale), 
                       width/(2*self.drawScale), height/(2*self.drawScale)]
        self.uvs += [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0]
        self.indices += [ind, ind +1, ind +2, ind+1, ind+2, ind+3]
        self.currentIndex += 6

    def addMapping(self, mapping:TextureMapping):
        ind = self.currentIndex
        self.verts += mapping.getMappingPos()
        self.uvs += mapping.getMappingUvs()
        self.indices += [ind, ind +1, ind +2, ind+1, ind+2, ind+3]
        self.currentIndex += 4