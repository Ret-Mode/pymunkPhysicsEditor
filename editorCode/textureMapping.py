from .shapeInternals.editorBodyI import BodyI
from .editorTypes import V2, ContainerTransform, EditorPoint, Selection
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
        self.anchor: List[float] = None
        self.mappingSize: List[int] = None
        self.mappingOffset: List[int] = None
        self.uv: List[V2] = [V2() for i in range(4)]
        self.cog:V2 = V2()

        self.initialize(textureSize)

    def initialize(self, textureSize: Tuple[int]):
        self.textureSize = list(textureSize)
        self.anchor: List[float] = [textureSize[0]/(2.0), textureSize[1]/(2.0)]
        self.mappingOffset = [0,0]
        self.mappingSize = list(textureSize)
        #self.updateUVs()
        pixelPerMeter = physicsSetup['pixelPerMeter']
        offX = (1.0 * self.mappingOffset[0])
        offY = (1.0 * self.mappingOffset[1])
        endX = (1.0 * self.mappingOffset[0] + self.mappingSize[0])
        endY = (1.0 * self.mappingOffset[1] + self.mappingSize[1])
        self.uv[0].setFromXY(offX/self.textureSize[0], offY/self.textureSize[1])
        self.uv[1].setFromXY(endX/self.textureSize[0], offY/self.textureSize[1])
        self.uv[2].setFromXY(offX/self.textureSize[0], endY/self.textureSize[1])
        self.uv[3].setFromXY(endX/self.textureSize[0], endY/self.textureSize[1])

        self.mappingRect[0].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
        self.mappingRect[1].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
        self.mappingRect[2].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)
        self.mappingRect[3].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)

    # def updateUVs(self):
    #     pixelPerMeter = physicsSetup['pixelPerMeter']
    #     offX = (1.0 * self.mappingOffset[0])
    #     offY = (1.0 * self.mappingOffset[1])
    #     endX = (1.0 * self.mappingOffset[0] + self.mappingSize[0])
    #     endY = (1.0 * self.mappingOffset[1] + self.mappingSize[1])
    #     self.uv[0].setFromXY(offX/self.textureSize[0], offY/self.textureSize[1])
    #     self.uv[1].setFromXY(endX/self.textureSize[0], offY/self.textureSize[1])
    #     self.uv[2].setFromXY(offX/self.textureSize[0], endY/self.textureSize[1])
    #     self.uv[3].setFromXY(endX/self.textureSize[0], endY/self.textureSize[1])

    #     self.mappingRect[0].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
    #     self.mappingRect[1].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
    #     self.mappingRect[2].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)
    #     self.mappingRect[3].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)

    def setAnchor(self, x:float, y:float):
        diffX = x - self.anchor[0]
        diffY = y - self.anchor[1]
        
        self.anchor = [x, y]
        #self.updateUVs()
        pixelPerMeter = physicsSetup['pixelPerMeter']
        offX = (1.0 * self.mappingOffset[0])
        offY = (1.0 * self.mappingOffset[1])
        endX = (1.0 * self.mappingOffset[0] + self.mappingSize[0])
        endY = (1.0 * self.mappingOffset[1] + self.mappingSize[1])
        self.uv[0].setFromXY(offX/self.textureSize[0], offY/self.textureSize[1])
        self.uv[1].setFromXY(endX/self.textureSize[0], offY/self.textureSize[1])
        self.uv[2].setFromXY(offX/self.textureSize[0], endY/self.textureSize[1])
        self.uv[3].setFromXY(endX/self.textureSize[0], endY/self.textureSize[1])

        self.mappingRect[0].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
        self.mappingRect[1].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
        self.mappingRect[2].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)
        self.mappingRect[3].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)

    def setMappingFromSelection(self, selection:Selection):
        minX, minY = int(max(min(selection.start.x, selection.end.x),0.0)), int(max(min(selection.start.y, selection.end.y), 0.0))
        maxX, maxY = int(min(max(selection.start.x, selection.end.x)+1, self.textureSize[0])), int(min(max(selection.start.y, selection.end.y)+1, self.textureSize[1]))
        if minX < maxX and minY < maxY:
            self.mappingOffset[0] = minX
            self.mappingOffset[1] = minY
            self.mappingSize[0] = maxX - minX   
            self.mappingSize[1] = maxY - minY 
            #self.updateUVs()
            pixelPerMeter = physicsSetup['pixelPerMeter']
            offX = (1.0 * self.mappingOffset[0])
            offY = (1.0 * self.mappingOffset[1])
            endX = (1.0 * self.mappingOffset[0] + self.mappingSize[0])
            endY = (1.0 * self.mappingOffset[1] + self.mappingSize[1])
            self.uv[0].setFromXY(offX/self.textureSize[0], offY/self.textureSize[1])
            self.uv[1].setFromXY(endX/self.textureSize[0], offY/self.textureSize[1])
            self.uv[2].setFromXY(offX/self.textureSize[0], endY/self.textureSize[1])
            self.uv[3].setFromXY(endX/self.textureSize[0], endY/self.textureSize[1])

            self.mappingRect[0].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
            self.mappingRect[1].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
            self.mappingRect[2].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)
            self.mappingRect[3].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)

    def reloadTexture(self, textureSize: Tuple[int]):
        oldTextureSize = self.textureSize
        oldMappingOffset = self.mappingOffset
        oldMappingSize = self.mappingSize

        self.textureSize = list(textureSize)
        self.anchor: List[float] = [textureSize[0]/(2.0), textureSize[1]/(2.0)]
        
        newOffX = int(float(textureSize[0] * oldMappingOffset[0]) / oldTextureSize[0])
        newOffY = int(float(textureSize[1] * oldMappingOffset[1]) / oldTextureSize[1])
        self.mappingOffset = [newOffX,newOffY]
        
        newSizeX = int(float(textureSize[0] * oldMappingSize[0]) / oldTextureSize[0])
        newSizeY = int(float(textureSize[1] * oldMappingSize[1]) / oldTextureSize[1])
        self.mappingSize = [newSizeX, newSizeY]
        #self.updateUVs()
        pixelPerMeter = physicsSetup['pixelPerMeter']
        offX = (1.0 * self.mappingOffset[0])
        offY = (1.0 * self.mappingOffset[1])
        endX = (1.0 * self.mappingOffset[0] + self.mappingSize[0])
        endY = (1.0 * self.mappingOffset[1] + self.mappingSize[1])
        self.uv[0].setFromXY(offX/self.textureSize[0], offY/self.textureSize[1])
        self.uv[1].setFromXY(endX/self.textureSize[0], offY/self.textureSize[1])
        self.uv[2].setFromXY(offX/self.textureSize[0], endY/self.textureSize[1])
        self.uv[3].setFromXY(endX/self.textureSize[0], endY/self.textureSize[1])

        self.mappingRect[0].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
        self.mappingRect[1].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(offY-self.anchor[1])/pixelPerMeter)
        self.mappingRect[2].local.setFromXY((offX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)
        self.mappingRect[3].local.setFromXY((endX-self.anchor[0])/pixelPerMeter,(endY-self.anchor[1])/pixelPerMeter)

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

    def updateShapeView(self):
        if self.body:
            mappingBaseMat = self.transform.getInvMat()
            for point in self.mappingRect:
                mappingBaseMat.mulV(point.local, point.final)

    def recalcCog(self):
        if self.body:
            bodyInvMat = self.transform.getMat()
            bodyInvMat.mulV(self.body.physics.cog.final, self.cog)
            self.cog.sS(physicsSetup['pixelPerMeter']).tD(self.anchor[0], self.anchor[1])

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['textureChannel'] = str(self.channel)
        this['offset'] = [self.mappingOffset[0], self.mappingOffset[1]]
        this['size'] = [self.mappingSize[0], self.mappingSize[1]]
        this['anchor'] = [self.anchor[0], self.anchor[1]]
        this['body'] = self.body.label
        parent[self.label] = this
    
