
from .editorCursor import Cursor
from .editorCamera import EditorCamera
from .editorTypes import EditorPoint, V2, Mat, Selection
from .editorViewTransform import ContinuousTransform

from .shapeBuffer import ShapeBuffer
from .textureBuffer import TextureBuffer
from .textureShader import TextureDraw
from .lineShader import LineDraw
from .gridShader import GridDraw
from .glContext import GLContextI

from .editorState import EditorState
from .commandExec import CommandExec
from .commandExec import ComResizeView, ComMoveCursor, ComMoveView, ComScaleView, ComSetPivot, ComSetMappingAnchor
from .commandExec import ComStartTransform, ComCancelTransform,ComApplyTransform, ComSetMappingFromSelection

from .textureContainerI import TextureContainerI

class EditorTextureView:

    def __init__(self, width, height):
        self.viewOffset = EditorCamera(width//2, height)
        self.textureView = EditorCamera(width//2, height, width//2)
        self.cursor = Cursor.getInstance()
        self.pivot = EditorState.getInstance().getPivot()
        self.texPivot = V2()
        self.texCursor = V2()

        self.texShader = TextureDraw()
        self.gridShader = GridDraw()
        self.bodyShader = LineDraw()
        self.transform = ContinuousTransform()
        self.invTransformMat = Mat()
        self.selection = Selection()
        self.hideOthers = False

    def startSelection(self):
        if self._selectView() == self.textureView and not self.selection.isActive():
            self.selection.begin(self.cursor.viewCoords)

    def stopSelection(self):
        self.selection.stop()
        state = EditorState.getInstance()
        mapping = state.getCurrentMapping()
        if mapping:
            CommandExec.addCommand(ComSetMappingFromSelection(mapping, self.selection))
        

    def _selectView(self):
        if self.viewOffset.coordsInView(self.cursor.screenCoords.x, self.cursor.screenCoords.y):
                return self.viewOffset
        elif self.textureView.coordsInView(self.cursor.screenCoords.x, self.cursor.screenCoords.y):
                return self.textureView
        return None

    def setHelperPoint(self):
        state = EditorState.getInstance()
        mapping = state.getCurrentMapping()
        if self._selectView() == self.textureView and mapping:
            CommandExec.addCommand(ComSetMappingAnchor(mapping, self.cursor.viewCoords))
        else:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.cursor.viewCoords))

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



    def startMoveTransform(self):
        entity = EditorState.getInstance().getCurrentMapping()
        view = self._selectView()
        if entity and view == self.viewOffset:
            self.invTransformMat.set(entity.transform.getMat())
            self.invTransformMat.mulV(self.pivot, self.texPivot)
            self.invTransformMat.mulV(self.cursor.viewCoords, self.texCursor)
            mode = ContinuousTransform.MOVE if view == self.textureView else ContinuousTransform.INVMOVE
            CommandExec.addCommand(ComStartTransform(self.transform, entity, self.texCursor, self.texPivot, mode))

    def startRotateTransform(self):
        entity = EditorState.getInstance().getCurrentMapping()
        view = self._selectView()
        if entity and view == self.viewOffset:
            self.invTransformMat.set(entity.transform.getMat())
            self.invTransformMat.mulV(self.pivot, self.texPivot)
            self.invTransformMat.mulV(self.cursor.viewCoords, self.texCursor)
            mode = ContinuousTransform.ROTATE if view == self.textureView else ContinuousTransform.INVROTATE
            CommandExec.addCommand(ComStartTransform(self.transform, entity, self.texCursor, self.texPivot, mode))

    def startScaleTransform(self):
        entity = EditorState.getInstance().getCurrentMapping()
        view = self._selectView()
        if entity and view == self.viewOffset:
            self.invTransformMat.set(entity.transform.getMat())
            self.invTransformMat.mulV(self.pivot, self.texPivot)
            self.invTransformMat.mulV(self.cursor.viewCoords, self.texCursor)
            mode = ContinuousTransform.SCALE if view == self.textureView else ContinuousTransform.INVSCALE
            CommandExec.addCommand(ComStartTransform(self.transform, entity, self.texCursor, self.texPivot, mode))
            

    def startRotateScaleTransform(self):
        entity = EditorState.getInstance().getCurrentMapping()
        view = self._selectView()
        if entity and view == self.viewOffset:
            self.invTransformMat.set(entity.transform.getMat())
            self.invTransformMat.mulV(self.pivot, self.texPivot)
            self.invTransformMat.mulV(self.cursor.viewCoords, self.texCursor)
            mode = ContinuousTransform.ROTATESCALE if view == self.textureView else ContinuousTransform.INVROTATESCALE
            CommandExec.addCommand(ComStartTransform(self.transform, entity, self.texCursor, self.texPivot, mode))

    def cancelTransform(self):
        CommandExec.addCommand(ComCancelTransform(self.transform))

    def applyTransform(self):
        CommandExec.addCommand(ComApplyTransform(self.transform))




    def update(self):
        CommandExec.process()
        state = EditorState.getInstance()

        mapping = state.getCurrentMapping()

        if self.selection.isActive():
            self.selection.update(self.cursor.viewCoords)

        if self.transform.active:
            self.invTransformMat.mulV(self.cursor.viewCoords, self.texCursor)
            self.transform.update(self.texCursor)
        
        if mapping and mapping.body:
            mapping.body.updateEye()
            mapping.body.recalcPhysics()
            mapping.updateShapeView()
            mapping.recalcCog()


    def draw(self):
        state = EditorState.getInstance()
        buffer = ShapeBuffer.getInstance()
        textures = TextureContainerI.getInstance()
        currentChannel = state.getCurrentMappingChannel()
        currentTexture = textures.getTexture(currentChannel)
        texBuffer = TextureBuffer.getInstance()

        # draw mappings
        context = GLContextI.getInstance()
        context.setProjectionAndViewportFromCamera(self.viewOffset)

        self.gridShader.drawGrid(self.viewOffset)

        mapping = state.getCurrentMapping()

        buffer.reset()
        buffer.drawScale = self.viewOffset.scale
        
        if mapping and mapping.body:
            
            texBuffer.reset()
            texBuffer.addMapping(mapping)
            textures.use(mapping.channel, 0)
            self.texShader.update(texBuffer.verts, texBuffer.uvs, texBuffer.indices)
            self.texShader.draw()


            currentBody = mapping.body
            buffer.addBBox(currentBody.box.center.final, currentBody.box.halfWH.final, True, False)
            currentBody.bufferData(buffer)
            buffer.addTextureOutline(mapping.mappingRect)
            buffer.addTexturePivot(mapping.subAnchor.final)
            buffer.addCenterOfGravity(currentBody.physics.cog.final, True)

        
        buffer.addHelperPoint(self.pivot)
        self.bodyShader.update(buffer.verts, buffer.colors, buffer.indices)
        self.bodyShader.draw()
        # draw texture channel

        context.setProjectionAndViewportFromCamera(self.textureView)

        #self.gridShader.drawGrid(self.textureView)

        if currentTexture is not None:

            texBuffer.reset()
            width, height = textures.getSize(currentChannel)
            texBuffer.addBaseQuad(width, height)
            textures.use(currentChannel, 0)
            self.texShader.update(texBuffer.verts, texBuffer.uvs, texBuffer.indices)
            self.texShader.draw()

        buffer.reset()
        buffer.drawScale = self.textureView.scale
        if mapping and mapping.body:
            #buffer.addTextureOutline(mapping.mappingRect)
            width, height = textures.getSize(currentChannel)
            if width and height:
                buffer.addBaseWH(width, height)
                buffer.addBaseUV(mapping.getMappingUvs(), width, height)
            if self.selection.isActive():
                buffer.addSelection(self.selection.start, self.selection.end)
            buffer.addCenterOfGravity(mapping.cog, False)
        #buffer.addHelperPoint(self.texPivot)
        self.bodyShader.update(buffer.verts, buffer.colors, buffer.indices)
        self.bodyShader.draw()

    def swapHideState(self):
        self.hideOthers = not self.hideOthers

    def undo(self):
        CommandExec.undo()

    def redo(self):
        CommandExec.redo()