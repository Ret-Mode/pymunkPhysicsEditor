
from .editorCursor import Cursor
from .editorCamera import EditorCamera
from .editorTypes import EditorPoint
from .editorViewTransform import ContinuousTransform

from .shapeBuffer import ShapeBuffer
from .textureBuffer import TextureBuffer
from .textureShader import TextureDraw
from .lineShader import LineDraw
from .database import Database

from .commandExec import CommandExec
from .commandExec import ComResizeView, ComMoveCursor, ComMoveView, ComScaleView

from .arcadeTextureContainer import ArcadeTexture

class EditorTextureView:

    def __init__(self, width, height, cursor:Cursor):
        self.viewOffset = EditorCamera(width//2, height)
        self.textureView = EditorCamera(width//2, height, width//2)
        self.cursor = cursor
        self.pivot = EditorPoint()

        self.texShader = TextureDraw()
        self.bodyShader = LineDraw()
        self.transform = ContinuousTransform()

    def _selectView(self):
        if self.viewOffset.coordsInView(self.cursor.screenCoords.x, self.cursor.screenCoords.y):
                return self.viewOffset
        elif self.textureView.coordsInView(self.cursor.screenCoords.x, self.cursor.screenCoords.y):
                return self.textureView
        return None
    
    def resize(self, x:float, y:float):
        CommandExec.addCommand(ComResizeView(self.viewOffset, x//2, y))
        CommandExec.addCommand(ComResizeView(self.textureView, x//2, y, x//2))

    def moveView(self, dx:float, dy:float):
        view = self._selectView()
        if view:
            CommandExec.addCommand(ComMoveView(view, dx, dy))

    def changeScale(self, dy:float):
        view = self._selectView()
        if view:
            CommandExec.addCommand(ComScaleView(view, self.cursor.viewCoords, dy))

    def moveCursor(self, x:float, y:float):
        view = self._selectView()
        CommandExec.addCommand(ComMoveCursor(view, self.cursor, x, y))


    def update(self):
        CommandExec.process()
        database = Database.getInstance()
        mapping = database.getCurrentMapping()
        if mapping and mapping.body:
            mapping.update()


    def draw(self):
        database = Database.getInstance()
        buffer = ShapeBuffer.getInstance()
        textures = ArcadeTexture.getInstance()
        currentTexture = textures.getCurrent()
        texBuffer = TextureBuffer.getInstance()

        # draw mappings
        buffer.reset()
        buffer.drawScale = self.viewOffset.scale

        buffer.addGrid(self.viewOffset.offsetScaled, self.viewOffset.sizeScaled)

        mapping = database.getCurrentMapping()

        if mapping and mapping.body:
            
            texBuffer.reset()
            texBuffer.addMapping(mapping)
            textures.use(mapping.channel, 0)
            self.texShader.update(texBuffer.verts, texBuffer.uvs, texBuffer.indices)
            self.texShader.setProjection((self.viewOffset.offsetInPixels.x, 
                                        self.viewOffset.offsetInPixels.y, 
                                        self.viewOffset.sizeInPixels.x, 
                                        self.viewOffset.sizeInPixels.y), 
                                        self.viewOffset.mat)
            self.texShader.draw()

            currentBody = mapping.body
            buffer.addBBox(currentBody.box.center.final, currentBody.box.halfWH.final, True, False)
            currentBody.bufferData(buffer)
            buffer.addTextureOutline(mapping.textureRect)
            buffer.addCenterOfGravity(currentBody.physics.cog.final, True)

        self.bodyShader.update(buffer.verts, buffer.colors, buffer.indices)
        self.bodyShader.setProjection((self.viewOffset.offsetInPixels.x, 
                            self.viewOffset.offsetInPixels.y, 
                            self.viewOffset.sizeInPixels.x, 
                            self.viewOffset.sizeInPixels.y), 
                            self.viewOffset.mat)

        self.bodyShader.draw()
        

        # draw texture channel


        if currentTexture is not None:
            buffer.reset()
            buffer.drawScale = self.textureView.scale

            buffer.addGrid(self.textureView.offsetScaled, self.textureView.sizeScaled)

            self.bodyShader.update(buffer.verts, buffer.colors, buffer.indices)
            self.bodyShader.setProjection((self.textureView.offsetInPixels.x, 
                                self.textureView.offsetInPixels.y, 
                                self.textureView.sizeInPixels.x, 
                                self.textureView.sizeInPixels.y), 
                                self.textureView.mat)

            self.bodyShader.draw()


            texBuffer.reset()
            
            
            width, height = textures.getSize(currentTexture)
            
            texBuffer.addBaseQuad(width, height)

            textures.use(currentTexture, 0)
            self.texShader.update(texBuffer.verts, texBuffer.uvs, texBuffer.indices)
            self.texShader.setProjection((self.textureView.offsetInPixels.x, 
                                        self.textureView.offsetInPixels.y, 
                                        self.textureView.sizeInPixels.x, 
                                        self.textureView.sizeInPixels.y), 
                                        self.textureView.mat)
            self.texShader.draw()