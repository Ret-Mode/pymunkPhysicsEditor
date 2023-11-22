from .editorTypes import EditorPoint
from .editorCursor import Cursor
from .editorShapes import Container
from .shapeInternals.editorShapeI import ShapeI
from .editorCamera import EditorCamera
from .commandExec import CommandExec, ComCancelTransform, ComStartTransform, ComNewShapeAddPoint, ComNewShapeNewWH
from .commandExec import ComMoveCursor, ComSetPivot, ComResizeView, ComScaleView, ComMoveView, ComApplyTransform
from .editorViewTransform import ContinuousTransform
from .database import Database
from .editorState import EditorState

from .pymunkTester import testShapes

from .shapeBuffer import ShapeBuffer
from .lineShader import LineDraw

from .textureContainerI import TextureContainerI
from .textureBuffer import TextureBuffer
from .textureShader import TextureDraw
from .gridShader import GridDraw
from .glContext import GLContextI

from .config import toJSON

class EditorShapeView:

    modes = ['SHAPE_EDIT_VERTEX', 'ROTATE_CURRENT', 'MOVE_CURRENT']

    def __init__(self, width, height, cursor:Cursor):
        self.viewOffset = EditorCamera(width, height)
        self.cursor = cursor
        self.pivot = EditorPoint()

        self.objectsUnderCursor = []
        self.hideOthers = False

        self.transform = ContinuousTransform()
        self.shader = LineDraw()
        self.texShader = TextureDraw()
        self.gridShader = GridDraw()


    def startMoveTransform(self):
        shape = EditorState.getInstance().getCurrentShape()
        if shape:
            CommandExec.addCommand(ComStartTransform(self.transform, shape, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.MOVE))

    def startRotateTransform(self):
        shape = EditorState.getInstance().getCurrentShape()
        if shape:
            CommandExec.addCommand(ComStartTransform(self.transform, shape, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.ROTATE))

    def startScaleTransform(self):
        shape = EditorState.getInstance().getCurrentShape()
        if shape:
            CommandExec.addCommand(ComStartTransform(self.transform, shape, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.SCALE))

    def startRotateScaleTransform(self):
        shape = EditorState.getInstance().getCurrentShape()
        if shape:
            CommandExec.addCommand(ComStartTransform(self.transform, shape, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.ROTATESCALE))

    def cancelTransform(self):
        CommandExec.addCommand(ComCancelTransform(self.transform))

    def applyTransform(self):
        CommandExec.addCommand(ComApplyTransform(self.transform))
    

    def pymunkTest(self):
        shape = EditorState.getInstance().getCurrentShape()
        if shape:
            tmp = {}
            shape.getJSONDict(tmp)
            testShapes(toJSON(tmp))


    def defaultAction(self):
        shape = EditorState.getInstance().getCurrentShape()
        if shape:
            if shape.type == ShapeI.POLYGON:
                CommandExec.addCommand(ComNewShapeAddPoint(self.cursor.viewCoords, shape))
            elif shape.type == ShapeI.CIRCLE:
                CommandExec.addCommand(ComNewShapeNewWH(self.cursor.viewCoords, shape))
            elif shape.type == ShapeI.BOX:
                CommandExec.addCommand(ComNewShapeNewWH(self.cursor.viewCoords, shape))
            elif shape.type == ShapeI.RECT:
                CommandExec.addCommand(ComNewShapeNewWH(self.cursor.viewCoords, shape))
            elif shape.type == ShapeI.LINE:
                CommandExec.addCommand(ComNewShapeAddPoint(self.cursor.viewCoords, shape))




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


    def swapHideState(self):
        self.hideOthers = not self.hideOthers

    def update(self):
        CommandExec.process()
        self.getSnappableObjects()
        self.selectObjectToSnap()

        # viewMat = self.viewOffset.getMat()
        # viewMat.mulV(self.pivot.world, self.pivot.screen)

        if self.transform.active:
            self.transform.update(self.cursor.viewCoords)

        database = Database.getInstance()
        parent = EditorState.getInstance().getCurrentBody()
        if parent:
            for shape in database.getAllNewShapesOfBody(parent.label):
                transform = shape.transform.getMat()
                shape.updatePos(transform)
                shape.recalcPhysics()
        
        for mapping in database.getAllMappingsOfBody(parent):
            mapping.updateShapeView()
 
    def draw(self):
        database = Database.getInstance()
        state = EditorState.getInstance()
        buffer = ShapeBuffer.getInstance()


        textures = TextureContainerI.getInstance()
        texBuffer = TextureBuffer.getInstance()
        
        context = GLContextI.getInstance()
        context.setProjectionAndViewportFromCamera(self.viewOffset)

        self.gridShader.drawGrid(self.viewOffset)
        
        parent = state.getCurrentBody()
        for channel in range(16):
            texBuffer.reset()
            for mapping in database.getAllMappingsOfBodyAndChannel(parent, channel): 
                texBuffer.addMapping(mapping)
            if texBuffer.indices:
                textures.use(channel, 0)
                self.texShader.update(texBuffer.verts, texBuffer.uvs, texBuffer.indices)
                self.texShader.draw()


        buffer.reset()
        buffer.drawScale = self.viewOffset.scale

        if self.hideOthers:
            shape = state.getCurrentShape()
            if shape:
                buffer.addBBox(shape.box.center.final, shape.box.halfWH.final, True, False)
                shape.bufferData(buffer)
                buffer.addCenterOfGravity(shape.physics.cog.final, True)

        else:
            parent = state.getCurrentBody()
            if parent:
                currentShape = state.getCurrentShape()
                for shape in parent.shapes:
                    active = (currentShape == shape)
                    buffer.addBBox(shape.box.center.final, shape.box.halfWH.final, active, False)
                    shape.bufferData(buffer)
                    buffer.addCenterOfGravity(shape.physics.cog.final, True)

        buffer.addHelperPoint(self.pivot.local)

        self.shader.update(buffer.verts, buffer.colors, buffer.indices)

        self.shader.draw()

    # ######## TODO
    def nextSnappableObject(self):
        return
        current = self.current
        if current and current in self.objectsUnderCursor:
            index = self.objectsUnderCursor.index(current)
            index = (index + 1) % len(self.objectsUnderCursor)
            self.current = self.objectsUnderCursor[index]
        elif self.objectsUnderCursor:
            self.current = self.objectsUnderCursor[0]

    def selectObjectToSnap(self):
        return
        if self.current:
            return
        elif self.objectsUnderCursor:
            self.current = self.objectsUnderCursor[0]

    def getSnappableObjects(self):
        return
        self.objectsUnderCursor.clear()
        parent = self.database.getCurrentBody()
        if parent:
            for shape in parent.shapes:
                shape = self.database.getNewShapeByIndex(ind)
                pass
                # for point in shape.points:
                #     if point.closeToScreenXY(self.cursor.screen.x, self.cursor.screen.y, 5):
                #         self.objectsUnderCursor.append(point)
                # if shape.closeToScreenXY(self.cursor.screen.x, self.cursor.screen.y, 5):
                #     self.objectsUnderCursor.append(shape)

    def undo(self):
        CommandExec.undo()

    def redo(self):
        CommandExec.redo()