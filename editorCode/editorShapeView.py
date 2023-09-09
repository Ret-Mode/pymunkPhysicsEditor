from .editorTypes import EditorPoint
from .editorCursor import Cursor
from .editorShapes import Container
from .shapeInternals.editorShapeI import ShapeI
from .editorViewOffset import ViewOffset
from .commandExec import CommandExec, ComCancelTransform, ComStartTransform, ComNewShapeAddPoint, ComNewShapeNewRadius, ComNewShapeNewWH
from .commandExec import ComMoveCursor, ComSetPivot, ComResizeView, ComScaleView, ComMoveView, ComApplyTransform
from .editorViewTransform import ContinuousTransform
from .database import Database

from .pymunkTester import testShapes

from .drawing import drawCursor, drawHelperPoint, drawShape

from .config import toJSON

class EditorShapeView:

    modes = ['SHAPE_EDIT_VERTEX', 'ROTATE_CURRENT', 'MOVE_CURRENT']

    def __init__(self, width, height, cursor:Cursor):
        self.viewOffset = ViewOffset(width, height)
        self.cursor = cursor
        self.pivot = EditorPoint()

        self.objectsUnderCursor = []
        self.hideOthers = False

        self.transform = ContinuousTransform()
        #self.moveView(-width/2, -height/2)



    def startMoveTransform(self):
        shape = Database.getInstance().getCurrentShape()
        if shape:
            CommandExec.addCommand(ComStartTransform(self.transform, shape, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.MOVE))

    def startRotateTransform(self):
        shape = Database.getInstance().getCurrentShape()
        if shape:
            CommandExec.addCommand(ComStartTransform(self.transform, shape, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.ROTATE))

    def startScaleTransform(self):
        shape = Database.getInstance().getCurrentShape()
        if shape:
            CommandExec.addCommand(ComStartTransform(self.transform, shape, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.SCALE))

    def startRotateScaleTransform(self):
        shape = Database.getInstance().getCurrentShape()
        if shape:
            CommandExec.addCommand(ComStartTransform(self.transform, shape, self.cursor.viewCoords, self.pivot.local, ContinuousTransform.ROTATESCALE))

    def cancelTransform(self):
        CommandExec.addCommand(ComCancelTransform(self.transform))

    def applyTransform(self):
        CommandExec.addCommand(ComApplyTransform(self.transform))
    

    def pymunkTest(self):
        shape = Database.getInstance().getCurrentShape()
        if shape:
            tmp = {}
            shape.getJSONDict(tmp)
            testShapes(toJSON(tmp))


    def defaultAction(self):
        shape = Database.getInstance().getCurrentShape()
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
        parent = database.getCurrentBody()
        if parent:
            for shape in database.getAllNewShapesOfBody(parent.label):
                transform = shape.transform.getMat()
                shape.updatePos(transform)
                shape.recalcPhysics()
                
 
    def draw(self):
        database = Database.getInstance()
        self.viewOffset.start()
        if self.hideOthers:
            shape = database.getCurrentShape()
            if shape:
                drawShape(shape, True, False)
        else:
            parent = database.getCurrentBody()
            if parent:
                currentShape = database.getCurrentShape()
                for shape in parent.shapes:
                    drawShape(shape, shape == currentShape, shape in self.objectsUnderCursor)

        drawHelperPoint(self.pivot.local)

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