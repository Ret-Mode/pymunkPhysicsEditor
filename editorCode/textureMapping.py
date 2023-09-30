from .shapeInternals.editorBodyI import BodyI
from .editorTypes import ContainerTransform, EditorPoint

from typing import List

class TextureMapping:

    def __init__(self):
        self.body:BodyI = None
        self.transform = ContainerTransform()
        self.textureRect: List[EditorPoint] = [EditorPoint()] * 4
        self.uv: List[EditorPoint] = [EditorPoint()] * 4

