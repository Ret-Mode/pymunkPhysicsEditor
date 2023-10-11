from .shapeInternals.editorBodyI import BodyI
from .editorTypes import V2, ContainerTransform, EditorPoint
from .config import physicsSetup
from typing import List, Tuple

class TextureMapping:

    def __init__(self, label:str, channel:int, textureSize: Tuple[int]):
        self.label:str = label
        self.channel = channel
        self.body:BodyI = None
        self.transform = ContainerTransform()
        self.mappingRect: List[EditorPoint] = [EditorPoint() for i in range(4)]
        self.textureSize: List[int] = None
        self.uv: List[V2] = [V2() for i in range(4)]
        self.initialize(textureSize)

    def initialize(self, textureSize: Tuple[int]):
        pixelPerMeter = physicsSetup['pixelPerMeter']
        self.textureSize = [textureSize[0], textureSize[1]]
        #self.transform.objectAnchor.setFromXY(textureSize[0]/(2.0*pixelPerMeter), textureSize[1]/(2.0*pixelPerMeter))

        self.uv[0].setFromXY(0.0, 0.0)
        self.uv[1].setFromXY(1.0, 0.0)
        self.uv[2].setFromXY(0.0, 1.0)
        self.uv[3].setFromXY(1.0, 1.0)

        self.mappingRect[0].local.setFromXY(-textureSize[0]/(2.0*pixelPerMeter),-textureSize[1]/(2.0*pixelPerMeter))
        self.mappingRect[1].local.setFromXY(textureSize[0]/(2.0*pixelPerMeter),-textureSize[1]/(2.0*pixelPerMeter))
        self.mappingRect[2].local.setFromXY(-textureSize[0]/(2.0*pixelPerMeter),textureSize[1]/(2.0*pixelPerMeter))
        self.mappingRect[3].local.setFromXY(textureSize[0]/(2.0*pixelPerMeter),textureSize[1]/(2.0*pixelPerMeter))

    def setBody(self, body:BodyI):
        if body:
            self.body = body
            # TODO update

    def update(self):
        if self.body:
            mappingBaseMat = self.transform.getInvMat()
            mappingBaseMat.mulPre(self.body.transform.getMat())
            for point in self.mappingRect:
                mappingBaseMat.mulV(point.local, point.final)
                pass

    def updateShapeView(self):
        if self.body:
            mappingBaseMat = self.transform.getInvMat()
            for point in self.mappingRect:
                mappingBaseMat.mulV(point.local, point.final)
                pass

    def getMappingPos(self) -> List[float]:
        result = []
        for point in self.mappingRect:
            result += [point.final.x, point.final.y]
        return result


    def getMappingUvs(self) -> List[float]:
        result = []
        for point in self.uv:
            result += [point.x, point.y]
        return result