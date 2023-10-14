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
        self.textureMid: List[int] = None
        self.mappingSize: List[int] = None
        self.mappingOffset: List[int] = None
        self.uv: List[V2] = [V2() for i in range(4)]
        self.initialize(textureSize)

    def _updateUVs(self):
        offX = (1.0 * self.mappingOffset[0])/self.textureSize[0]
        offY = (1.0 * self.mappingOffset[1])/self.textureSize[1]
        endX = (1.0 * self.mappingOffset[0] + self.mappingSize[0])/self.textureSize[0]
        endY = (1.0 * self.mappingOffset[1] + self.mappingSize[1])/self.textureSize[1]
        self.uv[0].setFromXY(offX, offY)
        self.uv[1].setFromXY(endX, offY)
        self.uv[2].setFromXY(offX, endY)
        self.uv[3].setFromXY(endX, endY)

        self.mappingRect[0].local.setFromXY(2*offX-self.textureMid[0],2*offY-self.textureMid[1])
        self.mappingRect[1].local.setFromXY(2*endX-self.textureMid[0],2*offY-self.textureMid[1])
        self.mappingRect[2].local.setFromXY(2*offX-self.textureMid[0],2*endY-self.textureMid[1])
        self.mappingRect[3].local.setFromXY(2*endX-self.textureMid[0],2*endY-self.textureMid[1])

    def setMappingOffset(self, newOffset:Tuple[int, int]):
        offX = max(min(newOffset[0], self.textureSize[0] - 1), 0)
        offY = max(min(newOffset[1], self.textureSize[1] - 1), 0)
        xCoord = max(min(offX + self.mappingSize[0], self.textureSize[0]), 0)
        yCoord = max(min(offY + self.mappingSize[1], self.textureSize[1]), 0)
        if xCoord == offX or yCoord == offY:
            return
        if offX < xCoord:
            self.mappingOffset[0] = offX
            self.mappingSize[0] = xCoord - offX
        else:
            self.mappingOffset[0] = xCoord
            self.mappingSize[0] = offX - xCoord    
        if offY < yCoord:
            self.mappingOffset[1] = offY
            self.mappingSize[1] = yCoord - offY
        else:
            self.mappingOffset[1] = yCoord
            self.mappingSize[1] = offY - yCoord
        self._updateUVs()

    def setMappingSize(self, newSize:Tuple[int, int]):
        offX = self.mappingOffset[0]
        offY = self.mappingOffset[1]
        xCoord = max(min(offX + newSize[0], self.textureSize[0]), 0)
        yCoord = max(min(offY + newSize[1], self.textureSize[1]), 0)
        if xCoord == offX or yCoord == offY:
            return
        if offX < xCoord:
            self.mappingOffset[0] = offX
            self.mappingSize[0] = xCoord - offX
        else:
            self.mappingOffset[0] = xCoord
            self.mappingSize[0] = offX - xCoord    
        if offY < yCoord:
            self.mappingOffset[1] = offY
            self.mappingSize[1] = yCoord - offY
        else:
            self.mappingOffset[1] = yCoord
            self.mappingSize[1] = offY - yCoord
        self._updateUVs()



    def getTextureSize(self) -> Tuple[int]:
        if self.textureSize:
            return tuple(self.textureSize)
        return (0,0)

    def getMappingOffset(self) -> Tuple[int]:
        if self.mappingOffset:
            return tuple(self.mappingOffset)
        return (0,0)
    
    def getMappingSize(self) -> Tuple[int]:
        if self.mappingSize:
            return tuple(self.mappingSize)
        return (0,0)
    
    def initialize(self, textureSize: Tuple[int]):
        pixelPerMeter = physicsSetup['pixelPerMeter']
        self.textureSize = list(textureSize)
        self.textureMid: List[int] = [textureSize[0]/(2.0*pixelPerMeter), textureSize[1]/(2.0*pixelPerMeter)]
        self.mappingOffset = [0,0]
        self.mappingSize = list(textureSize)
        #self.transform.objectAnchor.setFromXY(textureSize[0]/(2.0*pixelPerMeter), textureSize[1]/(2.0*pixelPerMeter))

        self.uv[0].setFromXY(0.0, 0.0)
        self.uv[1].setFromXY(1.0, 0.0)
        self.uv[2].setFromXY(0.0, 1.0)
        self.uv[3].setFromXY(1.0, 1.0)

        self.mappingRect[0].local.setFromXY(-self.textureMid[0],-self.textureMid[1])
        self.mappingRect[1].local.setFromXY(self.textureMid[0],-self.textureMid[1])
        self.mappingRect[2].local.setFromXY(-self.textureMid[0],self.textureMid[1])
        self.mappingRect[3].local.setFromXY(self.textureMid[0], self.textureMid[1])

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
    
    def changeMappingSize(self, offset:Tuple[int], newSize:Tuple[int]) -> None:
        assert offset[0] + newSize[0] <= self.textureSize[0]
        assert offset[0] >= 0
        assert newSize[0] > 0
        assert offset[1] + newSize[1] <= self.textureSize[1]
        assert offset[1] >= 0
        assert newSize[1] > 0
        self.mappingOffset = offset
        self.mappingSize = newSize
        self.uv[0].setFromXY(0.0, 0.0)
