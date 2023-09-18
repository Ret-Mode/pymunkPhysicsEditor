
from .editorViewOffset import ViewOffset
from .editorTypes import EditorPoint
from .editorCursor import Cursor
from .editorViewTransform import ContinuousTransform
from .database import Database
from .bufferContainer import BufferContainer

from .commandExec import CommandExec
from .commandExec import ComSetPivot, ComScaleView, ComResizeView, ComMoveCursor, ComMoveView
from .commandExec import ComStartTransform, ComCancelTransform,ComApplyTransform
from .lineShader import LineDraw

from .config import toJSON

from .pymunkTester import testBodies

class EditorBodyView:

    def __init__(self, width, height, cursor:Cursor):
        self.viewOffset = ViewOffset(width, height)
        self.cursor = cursor
        self.pivot = EditorPoint()

        self.objectsUnderCursor = []
        self.hideOthers = False

        self.transform = ContinuousTransform()
        self.shader = LineDraw()
        #self.moveView(-width/2, -height/2)


    def startMoveTransform(self):
        body = Database.getInstance().getCurrentBody()
        if body:
            CommandExec.addCommand(ComStartTransform(self.transform, body, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.MOVE))

    def startRotateTransform(self):
        body = Database.getInstance().getCurrentBody()
        if body:
            CommandExec.addCommand(ComStartTransform(self.transform, body, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.ROTATE))

    def startScaleTransform(self):
        body = Database.getInstance().getCurrentBody()
        if body:
            CommandExec.addCommand(ComStartTransform(self.transform, body, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.SCALE))

    def startRotateScaleTransform(self):
        body = Database.getInstance().getCurrentBody()
        if body:
            CommandExec.addCommand(ComStartTransform(self.transform, body, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.ROTATESCALE))

    def cancelTransform(self):
        CommandExec.addCommand(ComCancelTransform(self.transform))

    def applyTransform(self):
        CommandExec.addCommand(ComApplyTransform(self.transform))


    def pymunkTest(self):
        body = Database.getInstance().getCurrentBody()
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
        
    def draw(self):
        buffer = BufferContainer.getInstance()
        database = Database.getInstance()

        buffer.reset()
        buffer.drawScale = self.viewOffset.scale

        currentBody = database.getCurrentBody()
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
        self.shader.setProjection((self.viewOffset.offsetInPixels.x, 
                            self.viewOffset.offsetInPixels.y, 
                            self.viewOffset.sizeInPixels.x, 
                            self.viewOffset.sizeInPixels.y), 
                            self.viewOffset.mat)

        self.shader.draw()

    def undo(self):
        self.clearCurrentOperations()
        CommandExec.undo()

    def redo(self):
        CommandExec.redo()