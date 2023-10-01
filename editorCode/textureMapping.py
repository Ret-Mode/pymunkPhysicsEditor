from .shapeInternals.editorBodyI import BodyI
from .editorTypes import V2, ContainerTransform, EditorPoint

from typing import List, Tuple

class TextureMapping:

    def __init__(self, label:str, channel:int, textureSize: Tuple[int]):
        self.label:str = label
        self.channel = channel
        self.body:BodyI = None
        self.bodyTransform = ContainerTransform()
        self.mappingTransform = ContainerTransform()
        self.textureRect: List[EditorPoint] = [EditorPoint() for i in range(4)]
        self.uv: List[V2] = [V2() for i in range(4)]
        self.initialize(textureSize)

    def initialize(self, textureSize: Tuple[int]):
        self.mappingTransform.objectScale = 32.0
        x, y = textureSize
        self.mappingTransform.objectAnchor.setFromXY(x/2.0, y/(2.0))

        self.uv[0].setFromXY(0.0, 0.0)
        self.uv[1].setFromXY(1.0, 0.0)
        self.uv[2].setFromXY(0.0, 1.0)
        self.uv[3].setFromXY(1.0, 1.0)

        self.textureRect[0].local.setFromXY(0.0,0.0)
        self.textureRect[1].local.setFromXY(float(textureSize[0]),0.0)
        self.textureRect[2].local.setFromXY(0.0,float(textureSize[1]))
        self.textureRect[3].local.setFromXY(float(textureSize[0]),float(textureSize[1]))

    def setBody(self, body:BodyI):
        if body:
            self.body = body
            # TODO update

    def update(self):
        if self.body:
            mappingBaseMat = self.mappingTransform.getInvMat()
            mappingBaseMat.mulPre(self.bodyTransform.getMat()).mulPre(self.body.transform.getMat())
            for point in self.textureRect:
                mappingBaseMat.mulV(point.local, point.final)
                pass

    def getTexPos(self) -> List[float]:
        result = []
        for point in self.textureRect:
            result += [point.final.x, point.final.y]
        return result


    def getTexUvs(self) -> List[float]:
        result = []
        for point in self.uv:
            result += [point.x, point.y]
        return result