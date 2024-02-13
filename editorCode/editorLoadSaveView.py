
from .editorCamera import EditorCamera
from .editorTypes import EditorPoint
from .editorCursor import Cursor
from .editorViewTransform import ContinuousTransform
from .database import Database
from .editorState import EditorState
from .shapeBuffer import ShapeBuffer

from .commandExec import CommandExec
from .commandExec import ComSetPivot, ComScaleView, ComResizeView, ComMoveCursor, ComMoveView
from .commandExec import ComStartTransform, ComCancelTransform,ComApplyTransform
from .lineShader import LineDraw

from .textureContainerI import TextureContainerI
from .textureBuffer import TextureBuffer
from .textureShader import TextureDraw
from .gridShader import GridDraw
from .glContext import GLContextI

from .config import toJSON

from .pymunkTester import testBodies

class EditorLoadSaveView:

    def __init__(self, width, height):
        self.viewOffset = EditorCamera(width, height)
        self.cursor = Cursor.getInstance()
        self.pivot = EditorPoint()

        self.objectsUnderCursor = []
        self.hideOthers = False

        self.transform = ContinuousTransform()
        self.shader = LineDraw()
        self.texShader = TextureDraw()
        self.gridShader = GridDraw()
        #self.moveView(-width/2, -height/2)


    def startMoveTransform(self):
        body = EditorState.getInstance().getCurrentBody()
        if body:
            CommandExec.addCommand(ComStartTransform(self.transform, body, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.MOVE))

    def startRotateTransform(self):
        body = EditorState.getInstance().getCurrentBody()
        if body:
            CommandExec.addCommand(ComStartTransform(self.transform, body, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.ROTATE))

    def startScaleTransform(self):
        body = EditorState.getInstance().getCurrentBody()
        if body:
            CommandExec.addCommand(ComStartTransform(self.transform, body, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.SCALE))

    def startRotateScaleTransform(self):
        body = EditorState.getInstance().getCurrentBody()
        if body:
            CommandExec.addCommand(ComStartTransform(self.transform, body, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.ROTATESCALE))

    def cancelTransform(self):
        CommandExec.addCommand(ComCancelTransform(self.transform))

    def applyTransform(self):
        CommandExec.addCommand(ComApplyTransform(self.transform))


    def pymunkTest(self):
        body = EditorState.getInstance().getCurrentBody()
        if body:
            tmp = {}
            body.getJSONDict(tmp)
            s = toJSON(tmp)
            testBodies(s)
            print(s)


    def setHelperPoint(self):
        CommandExec.addCommand(ComSetPivot(self.pivot.local, self.cursor.viewCoords))

    def resize(self, x:float, y:float):
        CommandExec.addCommand(ComResizeView(self.viewOffset, x, y))

    def moveView(self, dx:float, dy:float):
        CommandExec.addCommand(ComMoveView(self.viewOffset, dx, dy))

    def changeScale(self, dy:float):
        CommandExec.addCommand(ComScaleView(self.viewOffset, self.cursor.viewCoords, dy))

    def moveCursor(self, x:float, y:float):
        CommandExec.addCommand(ComMoveCursor(self.viewOffset, self.cursor, x, y))

    def clearCurrentOperations(self):
        pass

    def swapHideState(self):
        self.hideOthers = not self.hideOthers

    def update(self):
        CommandExec.process()
        # all body/shape state should be established after above call

        if self.transform.active:
            self.transform.update(self.cursor.viewCoords)

        database = Database.getInstance()

        for body in database.bodies:
                transform = body.transform.getMat()
                body.updatePos(transform)
                body.recalcPhysics()

        for constraint in database.constraints:
            # TODO remove update of bodies from constraint update
            constraint.updateInternals()

        for mapping in database.mappings:
            mapping.update()
        
    def draw(self):
        buffer = ShapeBuffer.getInstance()
        database = Database.getInstance()
        state = EditorState.getInstance()
        textures = TextureContainerI.getInstance()
        texBuffer = TextureBuffer.getInstance()
        
        context = GLContextI.getInstance()
        context.setProjectionAndViewportFromCamera(self.viewOffset)

        self.gridShader.drawGrid(self.viewOffset)

        for channel in range(16):
            texBuffer.reset()
            for mapping in database.getAllMappingLabelsOfChannel(channel): 
                texBuffer.addMapping(database.getMappingByLabel(mapping))
            if texBuffer.indices:
                textures.use(channel, 0)
                self.texShader.update(texBuffer.verts, texBuffer.uvs, texBuffer.indices)
                self.texShader.draw()

        buffer.reset()
        buffer.drawScale = self.viewOffset.scale

        currentBody = state.getCurrentBody()
        if self.hideOthers and currentBody:

            buffer.addBBox(currentBody.box.center.final, currentBody.box.halfWH.final, True, False)
            currentBody.bufferData(buffer)
            buffer.addCenterOfGravity(currentBody.physics.cog.final, True)

        else:
            for body in database.bodies:
                active = (currentBody == body)

                buffer.addBBox(body.box.center.final, body.box.halfWH.final, active, False)
                body.bufferData(buffer)
                buffer.addCenterOfGravity(body.physics.cog.final, True)

        for constraint in database.constraints:
            constraint.bufferInternals(buffer)

        buffer.addHelperPoint(self.pivot.local)

        self.shader.update(buffer.verts, buffer.colors, buffer.indices)

        self.shader.draw()

    def undo(self):
        self.clearCurrentOperations()
        CommandExec.undo()

    def redo(self):
        CommandExec.redo()