from typing import List
import math
from typing import List

from .config import pointConfig
from .editorTypes import V2, EditorPoint, UnboundAngle


class TextureBuffer:

    _instance: "TextureBuffer" = None

    @staticmethod
    def getInstance() -> "TextureBuffer":
        if TextureBuffer._instance == None:
            TextureBuffer._instance = TextureBuffer()
        return TextureBuffer._instance
    
    def __init__(self):
        self.drawScale:float = 1.0
        self.verts: List[float] = []
        self.uvs: List[float] = []
        self.indices: List[int] = []
        self.currentIndex: int = 0

    def reset(self):
        self.drawScale:float = 1.0
        self.verts: List[float] = []
        self.uvs: List[float] = []
        self.indices: List[int] = []
        self.currentIndex: int = 0

    def addBaseQuad(self, width, height):
        ind = self.currentIndex
        self.verts += [0.0, 0.0, width, 0.0, 0.0, height, width, height]
        self.uvs += [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0]
        self.indices += [ind, ind +1, ind +2, ind+1, ind+2, ind+3]
        self.currentIndex += 6