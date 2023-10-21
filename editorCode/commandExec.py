from typing import List, Literal, Union, Tuple
from .editorShapes import Container
from .shapeInternals.editorShapeI import ShapeI
from .shapeInternals.editorBodyI import BodyI
from .constraintInternals.editorConstraintI import ConstraintI
from .textureMapping import TextureMapping
from .editorTypes import V2, Angle, EditorPoint, Selection
from .editorCursor import Cursor
from .database import Database
from .editorState import EditorState
from .editorViewTransform import ContinuousTransform
from .editorCamera import EditorCamera
from .constraintInternals.editorConstraint import DampedRotarySpring, DampedSpring, GearJoint
from .constraintInternals.editorConstraint import GrooveJoint, PinJoint, PivotJoint, RatchetJoint
from .constraintInternals.editorConstraint import RotaryLimitJoint, SimpleMotor, SlideJoint

import collections
import math

class Command:

    def execute(self):
        pass

    def hasUndo(self):
        return False


class CommandUndo(Command):

    def execute(self):
        pass

    def undo(self):
        pass

    def hasUndo(self):
        return True
    

class ComMoveCursor(Command):

    def __init__(self, view: EditorCamera, cursor: Cursor, x, y):
        self.view = view
        self.cursor = cursor
        self.x = x
        self.y = y
    
    def execute(self):
        self.cursor.screenCoords.setFromXY(self.x, self.y)
        if self.view:
            self.view.cusorToView(self.cursor)


# VIEW commands

class ComResizeView(Command):

    def __init__(self, view: EditorCamera, x, y, offsetX = 0, offsetY = 0):
        self.view = view
        self.x = x
        self.y = y
        self.offsetX = offsetX
        self.offsetY = offsetY
    
    def execute(self):
        self.view.resize(self.x, self.y, self.offsetX, self.offsetY)


class ComMoveView(Command):

    def __init__(self, view: EditorCamera, x, y):
        self.view = view
        self.x = x
        self.y = y
    
    def execute(self):
        self.view.move(self.x, self.y)


class ComScaleView(Command):

    def __init__(self, view: EditorCamera, cursorViewCoords: V2, scale):
        self.view = view
        self.viewCoords = cursorViewCoords
        self.scale = scale
    
    def execute(self):
        self.view.changeScale(self.scale, self.viewCoords)


# end of VIEW commands

# BODY commands

class ComShiftBodyUp(Command):

    def __init__(self, body:Container):
        self.database = Database.getInstance()
        self.body = body

    def execute(self):
        self.database.shiftBodyUp(self.body)


class ComShiftBodyDown(Command):

    def __init__(self, body:Container):
        self.database = Database.getInstance()
        self.body = body

    def execute(self):
        self.database.shiftBodyDown(self.body)


class ComSetLastBodyAsCurrent(Command):

    def __init__(self):
        self.state = EditorState.getInstance()

    def execute(self):
        self.state.setAnyBodyAsCurrent()


class ComBodyClone(CommandUndo):

    def __init__(self, body:Container):
        self.body = body
        self.database = Database.getInstance()
        self.newBody = None

    def execute(self):
        if self.body:
            pass
            # self.newBody = self.view.database.createBody(self.body.label + '_a')
            # newIndex = self.view.database.getBodyIndex(self.body) + 1
            # self.view.database.addBody(self.newBody, newIndex)
            # for shape in self.body.shapes:
            #     newShape = self.view.database.createShape(shape.label + '_a')
            #     self.view.database.addShape(newShape, self.newBody)
            #     for point in shape.points:
            #         newPoint = self.view.database.createPoint(point.world.x, point.world.y)
            #         self.view.database.addPoint(newPoint, newShape)
            # self.view.current = self.newBody

    def undo(self):
        if self.newBody:
            pass
            # self.view.current = self.body
            # for shape in self.newBody.shapes[:]:
            #     for point in shape.points[:]:
            #         self.view.database.deletePoint(point)
            #     self.view.database.deleteShape(shape.label)
            # self.view.database.deleteBody(self.newBody.label)


class ComRenameBody(CommandUndo):

    def __init__(self, body: Container, newName: str):
        self.body = body
        self.database = Database.getInstance()
        self.newName = newName
        self.oldName = body.label
    
    def execute(self):
        self.database.renameBody(self.body, self.newName)

    def undo(self):
        self.database.renameBody(self.body, self.oldName)


class ComAddBody(CommandUndo):

    def __init__(self, label: str, typeID:str = 'DYNAMIC'):
        self.state = EditorState.getInstance()
        self.database = Database.getInstance()
        self.object = self.database.createBody(label, typeID)
        self.prevCurrent = self.state.getCurrentBody()

    def execute(self):
        self.database.addBody(self.object)
        self.state.setCurrentBodyByLabel(self.object.label)

    def undo(self):
        self.state.setCurrentBodyByLabel(self.prevCurrent.label if self.prevCurrent else None)
        self.database.deleteBody(self.object.label)



class ComDelBody(CommandUndo):

    def __init__(self, label: str):
        self.database = Database.getInstance()
        self.state = EditorState.getInstance()
        self.object = self.database.getBodyByLabel(label)
        self.objIndex = -1
        self.deletedShapes: List[ShapeI] = []
        if self.object:
            self.constraintsOfDeletedBody = self.database.getConstraintsOfBody(label)
        else:
            self.constraintsOfDeletedBody = []

    def execute(self):           
        if self.object:
            # TODO remove this body from constraints
            self.objIndex = self.database.getBodyIndex(self.object)
            for shape in self.object.shapes:
                self.deletedShapes.append(shape)
                self.database.deleteNewShape(shape.label)
            self.database.deleteBody(self.object.label)
            self.state.setAnyBodyAsCurrent()
        

    def undo(self):
        if self.object:
            self.database.addBody(self.object, self.objIndex)
            for shape in self.deletedShapes:
                self.database.addNewShape(shape, self.object)
            self.state.setCurrentBodyByLabel(self.object.label)
            # TODO add this body to constraints


class ComSetBodyAsCurrent(CommandUndo):

    def __init__(self, label: str):
        self.state = EditorState.getInstance()
        self.label = label
        self.prev = self.state.getCurrentBody()

    def execute(self):
        self.state.setCurrentBodyByLabel(self.label)

    def undo(self):
        self.state.setCurrentBodyByLabel(self.prev.label if self.prev else None)


# END OF BODY functions

# SHAPE new functions
class ComShiftNewShapeUp(Command):

    def __init__(self):
        self.database = Database.getInstance()
        self.state = EditorState.getInstance()
        self.shape = self.state.getCurrentShape()

    def execute(self):
        if self.shape:
            self.database.shiftNewShapeUp(self.shape)


class ComShiftNewShapeDown(Command):

    def __init__(self):
        self.database = Database.getInstance()
        self.state = EditorState.getInstance()
        self.shape = self.state.getCurrentShape()

    def execute(self):
        if self.shape:
            self.database.shiftNewShapeDown(self.shape)


class ComRenameNewShape(CommandUndo):

    def __init__(self, newName:str):
        self.database = Database.getInstance()
        self.state = EditorState.getInstance()
        self.shape = self.state.getCurrentShape()
        self.newName = newName
        self.oldName = self.shape.label if self.shape else None
    
    def execute(self):
        if self.shape:
            self.database.renameNewShape(self.shape, self.newName)

    def undo(self):
        if self.shape:
            self.database.renameNewShape(self.shape, self.oldName)


class ComSelectNextBody(CommandUndo):

    def __init__(self):
        self.state = EditorState.getInstance()
        self.oldBody = self.state.getCurrentBody()
        self.oldShape = self.state.getCurrentShape()
        self.newBody:BodyI = None
        self.newShape:ShapeI = None
        self.executed:bool = False

    def execute(self):
        if not self.executed:
            self.state.setNextBodyAsCurrent()
            self.newBody = self.state.getCurrentBody()
            self.newShape = self.state.getCurrentShape()
            self.executed = True
        else:
            self.state.setCurrentBodyAndShape(self.newBody, self.newShape)

    def undo(self):
        self.state.setCurrentBodyAndShape(self.oldBody, self.oldShape)


class ComSelectPrevBody(CommandUndo):

    def __init__(self):
        self.state = EditorState.getInstance()
        self.oldBody = self.state.getCurrentBody()
        self.oldShape = self.state.getCurrentShape()
        self.newBody:BodyI = None
        self.newShape:ShapeI = None
        self.executed:bool = False

    def execute(self):
        if not self.executed:
            self.state.setPrevBodyAsCurrent()
            self.newBody = self.state.getCurrentBody()
            self.newShape = self.state.getCurrentShape()
            self.executed = True
        else:
            self.state.setCurrentBodyAndShape(self.newBody, self.newShape)

    def undo(self):
        self.state.setCurrentBodyAndShape(self.oldBody, self.oldShape)


class ComSetNewShapeAsCurrent(CommandUndo):

    def __init__(self, label: str):
        self.state = EditorState.getInstance()
        self.newShapeLabel = label
        oldShape = self.state.getCurrentShape()
        self.oldShapeLabel = oldShape.label if oldShape else None

    def execute(self):
        self.state.setCurrentShapeByLabel(self.newShapeLabel)

    def undo(self):
        self.state.setCurrentShapeByLabel(self.oldShapeLabel)


class ComNewShapeClone(CommandUndo):

    def __init__(self, shape:ShapeI):
        self.database = Database.getInstance()
        self.state = EditorState.getInstance()
        self.shape = shape
        self.body = self.database.getNewShapeParent(shape)
        self.newShape = None

    def execute(self):
        pass
        # if self.shape:
        #     self.newShape = self.view.database.createShape(self.shape.label + '_a')
        #     newIndex = self.view.database.getShapeIndex(self.shape) + 1
        #     self.view.database.addShape(self.newShape, self.body, newIndex)
        #     for point in self.shape.points:
        #         newPoint = self.view.database.createPoint(point.world.x, point.world.y)
        #         self.view.database.addPoint(newPoint, self.newShape)
        #     self.view.current = self.newShape

    def undo(self):
        pass
        # if self.newShape:
        #     self.view.current = self.shape
        #     for point in self.newShape.points[:]:
        #         self.view.database.deletePoint(point)
        #     self.view.database.deleteShape(self.newShape.label)


class ComAddNewShape(CommandUndo):

    def __init__(self, label:str, typeID:str):
        self.state = EditorState.getInstance()
        self.database = Database.getInstance()
        self.shape = self.database.createNewShape(label, typeID)
        self.prevShape = self.state.getCurrentShape()
        self.body = None

    def execute(self):
        self.body = self.state.getCurrentBody()
        if self.body:
            self.database.addNewShape(self.shape, self.body)
            self.state.setCurrentShapeByLabel(self.shape.label)

    def undo(self):
        if self.body:
            if self.prevShape:
                self.state.setCurrentShapeByLabel(self.prevShape.label)
            else:
                self.state.setCurrentShapeByLabel(None)
            self.database.deleteNewShape(self.shape.label)


class ComDelNewShape(CommandUndo):

    def __init__(self, label):
        self.database = Database.getInstance()
        self.state = EditorState.getInstance()
        self.label = label
        
        self.shape = self.database.getNewShapeByLabel(label)
        self.parent = self.database.getNewShapeParent(self.shape)

    def execute(self):
        self.database.deleteNewShape(self.label)
        self.state.setAnyShapeAsCurrent()

    def undo(self):
        self.database.addNewShape(self.shape, self.parent)
        self.state.setCurrentShapeByLabel(self.shape.label)


class ComNewShapeAddPoint(CommandUndo):

    def __init__(self, worldCoords: V2, shape: ShapeI):
        self.shape: ShapeI = shape

        self.point = EditorPoint()
        self.shape.transform.getInvMat().mulV(worldCoords, self.point.local)
        #self.point = EditorPoint(worldCoords.x, worldCoords.y)
        #self.point.world.unTV(shape.transform.objectAnchor).unRA(shape.transform.objectAngle).unSS(shape.transform.objectScale)
    
    def execute(self):
        self.shape.internal.addPoint(self.point)
        #self.shape.recalcPhysics()

    def undo(self):
        self.shape.internal.deletePoint(self.point)
        #self.shape.recalcPhysics()


class ComNewShapeNewRadius(CommandUndo):

    def __init__(self, worldCoords: V2, shape: ShapeI):
        self.shape: ShapeI = shape
        self.oldRadius = shape.internal.radius.world
        self.point = EditorPoint()
        self.shape.transform.getInvMat().mulV(worldCoords, self.point.local)
    
    def execute(self):
        self.shape.internal.setRadiusFromPoint(self.point)

    def undo(self):
        self.shape.internal.setRadiusFromFloat(self.oldRadius)


class ComNewShapeNewWH(CommandUndo):

    def __init__(self, worldCoords: V2, shape: ShapeI):
        self.shape: ShapeI = shape
        self.oldWH = EditorPoint().setFromEP(self.shape.internal.points[1])
        self.point = EditorPoint()
        self.shape.transform.getInvMat().mulV(worldCoords, self.point.local)
        #self.point.world.unTV(shape.transform.objectAnchor).unRA(shape.transform.objectAngle).unSS(shape.transform.objectScale)
    
    def execute(self):
        self.shape.internal.resetWH(self.point)

    def undo(self):
        self.shape.internal.setWH(self.oldWH)

# End of Shape functions




# Constraints commands

class ComConstraintSetNewBodyA(CommandUndo):

    def __init__(self, entity:ConstraintI, label:str):
        self.entity = entity
        self.newBody = Database.getInstance().getBodyByLabel(label)
        self.oldBody = entity.bodyA

    def execute(self):
        if self.newBody:
            self.entity.bodyA = self.newBody
    
    def undo(self):
        self.entity.bodyA = self.oldBody


class ComConstraintSetNewBodyB(CommandUndo):

    def __init__(self, entity:ConstraintI, label:str):
        self.entity = entity
        self.newBody = Database.getInstance().getBodyByLabel(label)
        self.oldBody = entity.bodyB

    def execute(self):
        if self.newBody:
            self.entity.bodyB = self.newBody
    
    def undo(self):
        self.entity.bodyB = self.oldBody


class ComConstraintSwapBodies(CommandUndo):

    def __init__(self, entity:ConstraintI):
        self.entity = entity

    def execute(self):
        self.entity.bodyA, self.entity.bodyB = self.entity.bodyB, self.entity.bodyA

    def undo(self):
        self.execute()


class ComShiftConstraintUp(Command):

    def __init__(self, entity:ConstraintI):
        self.database = Database.getInstance()
        self.entity = entity

    def execute(self):
        self.database.shiftConstraintUp(self.entity)


class ComShiftConstraintDown(Command):

    def __init__(self, entity:ConstraintI):
        self.database = Database.getInstance()
        self.entity = entity

    def execute(self):
        self.database.shiftConstraintDown(self.entity)


class ComSetLastConstraintAsCurrent(Command):

    def __init__(self):
        self.state = EditorState.getInstance()

    def execute(self):
        self.state.setAnyConstraintAsCurrent()


class ComConstraintClone(CommandUndo):

    def __init__(self, entity:ConstraintI):
        self.entity = entity
        self.database = Database.getInstance()
        self.newEntity = None

    def execute(self):
        if self.entity:
            pass

    def undo(self):
        if self.newEntity:
            pass


class ComRenameConstraint(CommandUndo):

    def __init__(self, entity:ConstraintI, newName: str):
        self.entity = entity
        self.database = Database.getInstance()
        self.newName = newName
        self.oldName = entity.label
    
    def execute(self):
        self.database.renameBody(self.entity, self.newName)

    def undo(self):
        self.database.renameBody(self.entity, self.oldName)


class ComAddConstraint(CommandUndo):

    def __init__(self, label: str, typeID:str):
        self.database = Database.getInstance()
        self.state = EditorState.getInstance()
        self.object = self.database.createConstraint(label, typeID)
        self.prevCurrent = self.state.getCurrentConstraint()

    def execute(self):
        self.database.addConstraint(self.object)
        self.state.setCurrentConstraintByLabel(self.object.label)

    def undo(self):
        self.state.setCurrentConstraintByLabel(self.prevCurrent.label if self.prevCurrent else None)
        self.database.deleteConstraint(self.object.label)



class ComDelConstraint(CommandUndo):

    def __init__(self, label: str):
        self.database = Database.getInstance()
        self.state = EditorState.getInstance()
        self.object = self.database.getConstraintByLabel(label)
        self.objIndex = -1

    def execute(self):           
        if self.object:
            self.objIndex = self.database.getConstraintIndex(self.object)
            self.database.deleteConstraint(self.object.label)
            self.state.setAnyConstraintAsCurrent()
        

    def undo(self):
        if self.object:
            self.database.addConstraint(self.object, self.objIndex)
            self.state.setCurrentConstraintByLabel(self.object.label)


class ComSetConstraintAsCurrent(CommandUndo):

    def __init__(self, label: str):
        self.state = EditorState.getInstance()
        self.label = label
        self.prev = self.state.getCurrentConstraint()

    def execute(self):
        self.state.setCurrentConstraintByLabel(self.label)

    def undo(self):
        self.state.setCurrentConstraintByLabel(self.prev.label if self.prev else None)


# END OF Constraint functions


# Constraint Internal Params


class ComSetRestAngle(CommandUndo):

    def __init__(self, constraint:DampedRotarySpring, value:float):
        self.entity = constraint
        self.newValue = value
        self.oldValue = constraint.restAngle.angle

    def execute(self):
        self.entity.restAngle.set(self.newValue)

    def undo(self):
        self.entity.restAngle.set(self.oldValue)


class ComSetRestAngleFromXYOffset(CommandUndo):

    def __init__(self, constraint:DampedRotarySpring, coords:V2, center:V2):
        self.entity = constraint
        self.newValue = math.atan2(coords.y - center.y, coords.x - center.x)
        self.oldValue = constraint.restAngle.angle

    def execute(self):
        self.entity.restAngle.set(self.newValue)

    def undo(self):
        self.entity.restAngle.set(self.oldValue)


class ComSetRestLength(CommandUndo):

    def __init__(self, constraint:DampedSpring, value:float):
        self.entity = constraint
        self.newValue = abs(value)
        self.oldValue = constraint.restLength

    def execute(self):
        self.entity.restLength = self.newValue

    def undo(self):
        self.entity.restLength = self.oldValue


class ComSetRestLengthFromCoords(CommandUndo):

    def __init__(self, constraint:DampedSpring, coords:V2):
        dist = constraint.anchorA.final.distV(constraint.anchorB.final)
        if dist != 0.0:
            projA = constraint.anchorA.final.dotVV(coords, constraint.anchorB.final) / (dist)
            self.newValue = 2 * abs(dist/2.0 - projA)
        else:
            self.newValue = constraint.restLength

        self.entity = constraint
        self.oldValue = constraint.restLength

    def execute(self):
        self.entity.restLength = self.newValue

    def undo(self):
        self.entity.restLength = self.oldValue


class ComSetStiffness(CommandUndo):

    def __init__(self, constraint:Union[DampedRotarySpring, DampedSpring], value:float):
        self.entity = constraint
        self.newValue = value
        self.oldValue = constraint.stiffness

    def execute(self):
        self.entity.stiffness = self.newValue

    def undo(self):
        self.entity.stiffness = self.oldValue


class ComSetDamping(CommandUndo):

    def __init__(self, constraint:Union[DampedRotarySpring, DampedSpring], value:float):
        self.entity = constraint
        self.newValue = value
        self.oldValue = constraint.damping

    def execute(self):
        self.entity.damping = self.newValue

    def undo(self):
        self.entity.damping = self.oldValue


class ComSetAnchorA(CommandUndo):

    def __init__(self, constraint:Union[DampedRotarySpring, DampedSpring, GrooveJoint, PinJoint, PivotJoint, SlideJoint],
                  x:float, y:float):
        self.entity = constraint
        mat = self.entity.bodyA.transform.getInvMat()
        newX, newY = mat.mulRSXY(x, y)
        self.newXValue = newX
        self.newYValue = newY
        self.oldXValue = constraint.anchorA.offset.x
        self.oldYValue = constraint.anchorA.offset.y

    def execute(self):
        self.entity.anchorA.offset.x = self.newXValue
        self.entity.anchorA.offset.y = self.newYValue

    def undo(self):
        self.entity.anchorA.offset.x = self.oldXValue
        self.entity.anchorA.offset.y = self.oldYValue


class ComSetAnchorAFromCoords(CommandUndo):

    def __init__(self, constraint:Union[DampedRotarySpring, DampedSpring, GrooveJoint, PinJoint, PivotJoint, SlideJoint],
                  coords:V2):
        self.entity = constraint
        center = constraint.bodyA.physics.cog.final
        mat = self.entity.bodyA.transform.getInvMat()
        x, y = mat.mulRSXY(coords.x - center.x, coords.y - center.y)
        
        self.newXValue = x
        self.newYValue = y
        self.oldXValue = constraint.anchorA.offset.x
        self.oldYValue = constraint.anchorA.offset.y

    def execute(self):
        self.entity.anchorA.offset.x = self.newXValue
        self.entity.anchorA.offset.y = self.newYValue

    def undo(self):
        self.entity.anchorA.offset.x = self.oldXValue
        self.entity.anchorA.offset.y = self.oldYValue


class ComSetAnchorB(CommandUndo):

    def __init__(self, constraint:Union[DampedRotarySpring, DampedSpring, PinJoint, PivotJoint, SlideJoint],
                  x:float, y:float):
        self.entity = constraint
        mat = self.entity.bodyA.transform.getInvMat()
        newX, newY = mat.mulRSXY(x, y)
        self.newXValue = newX
        self.newYValue = newY
        self.oldXValue = constraint.anchorB.offset.x
        self.oldYValue = constraint.anchorB.offset.y

    def execute(self):
        self.entity.anchorB.offset.x = self.newXValue
        self.entity.anchorB.offset.y = self.newYValue

    def undo(self):
        self.entity.anchorB.offset.x = self.oldXValue
        self.entity.anchorB.offset.y = self.oldYValue


class ComSetAnchorBFromCoords(CommandUndo):

    def __init__(self, constraint:Union[DampedRotarySpring, DampedSpring, GrooveJoint, PinJoint, PivotJoint, SlideJoint],
                  coords:V2):
        self.entity = constraint
        center = constraint.bodyB.physics.cog.final
        mat = self.entity.bodyB.transform.getInvMat()
        x, y = mat.mulRSXY(coords.x - center.x, coords.y - center.y)
        
        self.newXValue = x
        self.newYValue = y
        self.oldXValue = constraint.anchorB.offset.x
        self.oldYValue = constraint.anchorB.offset.y

    def execute(self):
        self.entity.anchorB.offset.x = self.newXValue
        self.entity.anchorB.offset.y = self.newYValue

    def undo(self):
        self.entity.anchorB.offset.x = self.oldXValue
        self.entity.anchorB.offset.y = self.oldYValue


class ComSetAnchorsFromCoords(CommandUndo):

    def __init__(self, constraint:Union[DampedRotarySpring, DampedSpring, GrooveJoint, PinJoint, PivotJoint, SlideJoint],
                  coords:V2):
        self.entity = constraint
        centerA = constraint.bodyA.physics.cog.final
        matA = self.entity.bodyA.transform.getInvMat()
        xA, yA = matA.mulRSXY(coords.x - centerA.x, coords.y - centerA.y)
        
        centerB = constraint.bodyB.physics.cog.final
        matB = self.entity.bodyB.transform.getInvMat()
        xB, yB = matB.mulRSXY(coords.x - centerB.x, coords.y - centerB.y)

        self.newXAValue = xA
        self.newYAValue = yA
        self.newXBValue = xB
        self.newYBValue = yB

        self.oldXAValue = constraint.anchorA.offset.x
        self.oldYAValue = constraint.anchorA.offset.y
        self.oldXBValue = constraint.anchorB.offset.x
        self.oldYBValue = constraint.anchorB.offset.y

    def execute(self):
        self.entity.anchorA.offset.setFromXY(self.newXAValue, self.newYAValue)
        self.entity.anchorB.offset.setFromXY(self.newXBValue, self.newYBValue)

    def undo(self):
        self.entity.anchorA.offset.setFromXY(self.oldXAValue, self.oldYAValue)
        self.entity.anchorB.offset.setFromXY(self.oldXBValue, self.oldYBValue)


class ComSetPhase(CommandUndo):

    def __init__(self, constraint:Union[GearJoint, RatchetJoint], value:float):
        self.entity = constraint
        self.newValue = value
        self.oldValue = constraint.phase.angle

    def execute(self):
        self.entity.phase.set(self.newValue)

    def undo(self):
        self.entity.phase.set(self.oldValue)


class ComSetPhaseFromCoords(CommandUndo):

    def __init__(self, constraint:Union[GearJoint, RatchetJoint], coords:V2, isBodyB:bool):
        center = constraint.bodyB.physics.cog.final if isBodyB else constraint.bodyA.physics.cog.final
        self.entity = constraint
        self.newValue = math.atan2(coords.y - center.y, coords.x - center.x)
        self.oldValue = constraint.phase.angle

    def execute(self):
        self.entity.phase.set(self.newValue)

    def undo(self):
        self.entity.phase.set(self.oldValue)


class ComSetRatio(CommandUndo):

    def __init__(self, constraint:GearJoint, value:float):
        self.entity = constraint
        self.newValue = value
        self.oldValue = constraint.ratio

    def execute(self):
        self.entity.ratio = self.newValue

    def undo(self):
        self.entity.ratio = self.oldValue


class ComSetRatioFromCoords(CommandUndo):

    def __init__(self, constraint:GearJoint, coords:V2, isBodyB:bool):
        center = constraint.bodyB.physics.cog.final if isBodyB else constraint.bodyA.physics.cog.final
        mat = constraint.bodyB.transform.getInvMat() if isBodyB else constraint.bodyA.transform.getInvMat()
        x, y = mat.mulRSXY(coords.x - center.x, coords.y - center.y)
        angle = (math.atan2(y, x) - constraint.phase.angle) if isBodyB else math.atan2(y, x)
        while angle > math.pi:
            angle = angle - 2.0 * math.pi
        while angle < - math.pi:
            angle = angle + 2.0 * math.pi

        if angle < -math.pi/2.0:
            angle = - math.pi - angle
        elif angle > math.pi/2.0:
            angle = math.pi - angle
        
        ratio = 1.0 / math.tan(-angle) if angle != 0.0 else 1.0
        self.entity = constraint
        self.newValue = ratio
        self.oldValue = constraint.ratio

    def execute(self):
        self.entity.ratio = self.newValue

    def undo(self):
        self.entity.ratio = self.oldValue


class ComSetGrooveA(CommandUndo):

    def __init__(self, constraint:GrooveJoint, x:float, y:float):
        self.entity = constraint
        mat = self.entity.bodyA.transform.getInvMat()
        newX, newY = mat.mulRSXY(x, y)
        self.newXValue = newX
        self.newYValue = newY
        self.oldXValue = constraint.grooveA.offset.x
        self.oldYValue = constraint.grooveA.offset.y

    def execute(self):
        self.entity.grooveA.offset.x = self.newXValue
        self.entity.grooveA.offset.y = self.newYValue

    def undo(self):
        self.entity.grooveA.offset.x = self.oldXValue
        self.entity.grooveA.offset.y = self.oldYValue


class ComSetGrooveAFromCoords(CommandUndo):

    def __init__(self, constraint:GrooveJoint,
                  coords:V2):
        self.entity = constraint
        center = constraint.bodyA.physics.cog.final
        mat = self.entity.bodyA.transform.getInvMat()
        x, y = mat.mulRSXY(coords.x - center.x, coords.y - center.y)
        
        self.newXValue = x
        self.newYValue = y
        self.oldXValue = constraint.grooveA.offset.x
        self.oldYValue = constraint.grooveA.offset.y

    def execute(self):
        self.entity.grooveA.offset.x = self.newXValue
        self.entity.grooveA.offset.y = self.newYValue

    def undo(self):
        self.entity.grooveA.offset.x = self.oldXValue
        self.entity.grooveA.offset.y = self.oldYValue


class ComSetGrooveB(CommandUndo):

    def __init__(self, constraint:GrooveJoint, x:float, y:float):
        self.entity = constraint
        mat = self.entity.bodyA.transform.getInvMat()
        newX, newY = mat.mulRSXY(x, y)
        self.newXValue = newX
        self.newYValue = newY
        self.oldXValue = constraint.grooveB.offset.x
        self.oldYValue = constraint.grooveB.offset.y

    def execute(self):
        self.entity.grooveB.offset.x = self.newXValue
        self.entity.grooveB.offset.y = self.newYValue

    def undo(self):
        self.entity.grooveB.offset.x = self.oldXValue
        self.entity.grooveB.offset.y = self.oldYValue


class ComSetGrooveBFromCoords(CommandUndo):

    def __init__(self, constraint:GrooveJoint,
                  coords:V2):
        self.entity = constraint
        center = constraint.bodyA.physics.cog.final
        mat = self.entity.bodyA.transform.getInvMat()
        x, y = mat.mulRSXY(coords.x - center.x, coords.y - center.y)
        
        self.newXValue = x
        self.newYValue = y
        self.oldXValue = constraint.grooveB.offset.x
        self.oldYValue = constraint.grooveB.offset.y

    def execute(self):
        self.entity.grooveB.offset.x = self.newXValue
        self.entity.grooveB.offset.y = self.newYValue

    def undo(self):
        self.entity.grooveB.offset.x = self.oldXValue
        self.entity.grooveB.offset.y = self.oldYValue


class ComSetRatchet(CommandUndo):

    def __init__(self, constraint:RatchetJoint, value:float):
        self.entity = constraint
        self.newValue = value
        self.oldValue = constraint.ratchet.angle

    def execute(self):
        self.entity.ratchet.set(self.newValue)

    def undo(self):
        self.entity.ratchet.set(self.oldValue)


class ComSetRatchetFromCoords(CommandUndo):

    def __init__(self, constraint:RatchetJoint, coords:V2, isBodyB:bool):
        center = constraint.bodyB.physics.cog.final if isBodyB else constraint.bodyA.physics.cog.final
        self.entity = constraint
        self.newValue = math.atan2(coords.y - center.y, coords.x - center.x)
        if isBodyB:
            self.newValue = constraint.phase.angle - self.newValue
            while self.newValue > math.pi:
                self.newValue -= 2.0 * math.pi
            while self.newValue < - math.pi:
                self.newValue += 2.0 * math.pi
        
        self.oldValue = constraint.ratchet.angle

    def execute(self):
        self.entity.ratchet.set(self.newValue)

    def undo(self):
        self.entity.ratchet.set(self.oldValue)


class ComSetRotaryMin(CommandUndo):

    def __init__(self, constraint:RotaryLimitJoint, value:float):
        self.entity = constraint
        self.newValue = min(value, self.entity.max.angle)
        self.oldValue = constraint.min.angle

    def execute(self):
        self.entity.min.set(self.newValue)

    def undo(self):
        self.entity.min.set(self.oldValue)


class ComSetRotaryMinFromCoords(CommandUndo):

    def __init__(self, constraint:RotaryLimitJoint, coords:V2, isBodyB:bool):
        self.entity = constraint
        center = constraint.bodyB.physics.cog.final if isBodyB else constraint.bodyA.physics.cog.final
        value = math.atan2(coords.y - center.y, coords.x - center.x)
        if not isBodyB:
            value = - value
        self.newValue = min(value, self.entity.max.angle)
        self.oldValue = constraint.min.angle

    def execute(self):
        self.entity.min.set(self.newValue)

    def undo(self):
        self.entity.min.set(self.oldValue)


class ComSetRotaryMax(CommandUndo):

    def __init__(self, constraint:RotaryLimitJoint, value:float):
        self.entity = constraint
        self.newValue = max(value, self.entity.min.angle)
        self.oldValue = constraint.max.angle

    def execute(self):
        self.entity.max.set(self.newValue)

    def undo(self):
        self.entity.max.set(self.oldValue)


class ComSetRotaryMaxFromCoords(CommandUndo):

    def __init__(self, constraint:RotaryLimitJoint, coords:V2, isBodyB:bool):
        self.entity = constraint
        center = constraint.bodyB.physics.cog.final if isBodyB else constraint.bodyA.physics.cog.final
        value = math.atan2(coords.y - center.y, coords.x - center.x)
        if not isBodyB:
            value = - value
        self.newValue = max(value, self.entity.min.angle)
        self.oldValue = constraint.min.angle

    def execute(self):
        self.entity.max.set(self.newValue)

    def undo(self):
        self.entity.max.set(self.oldValue)


class ComSetRate(CommandUndo):

    def __init__(self, constraint:SimpleMotor, value:float):
        self.entity = constraint
        self.newValue = value
        self.oldValue = constraint.rate.angle

    def execute(self):
        self.entity.rate.set(self.newValue)

    def undo(self):
        self.entity.rate.set(self.oldValue)


class ComSetRateFromCoords(CommandUndo):

    def __init__(self, constraint:SimpleMotor, coords:V2, isBodyB:bool):
        self.entity = constraint
        center = constraint.bodyB.physics.cog.final if isBodyB else constraint.bodyA.physics.cog.final
        value = math.atan2(coords.y - center.y, coords.x - center.x)
        if not isBodyB:
            value = - value
        self.newValue = value
        self.oldValue = constraint.rate.angle

    def execute(self):
        self.entity.rate.set(self.newValue)

    def undo(self):
        self.entity.rate.set(self.oldValue)


class ComSetSlideMin(CommandUndo):

    def __init__(self, constraint:SlideJoint, value:float):
        self.entity = constraint
        self.newValue = max(min(value, constraint.max), 0.0)
        self.oldValue = constraint.min

    def execute(self):
        self.entity.min = self.newValue

    def undo(self):
        self.entity.min = self.oldValue


class ComSetSlideMinFromCoords(CommandUndo):

    def __init__(self, constraint:SlideJoint, coords:V2):
        dist = constraint.anchorA.final.distV(constraint.anchorB.final)
        value = constraint.min
        if dist != 0.0:
            projA = constraint.anchorA.final.dotVV(coords, constraint.anchorB.final) / (dist)
            value = max(min(2 * abs(dist/2.0 - projA), constraint.max), 0.0)

        self.entity = constraint
        self.newValue = value
        self.oldValue = constraint.min

    def execute(self):
        self.entity.min = self.newValue

    def undo(self):
        self.entity.min = self.oldValue


class ComSetSlideMax(CommandUndo):

    def __init__(self, constraint:SlideJoint, value:float):
        self.entity = constraint
        self.newValue = max(value, constraint.min, 0.0)
        self.oldValue = constraint.max

    def execute(self):
        self.entity.max = self.newValue

    def undo(self):
        self.entity.max = self.oldValue


class ComSetSlideMaxFromCoords(CommandUndo):

    def __init__(self, constraint:SlideJoint, coords:V2):
        dist = constraint.anchorA.final.distV(constraint.anchorB.final)
        value = constraint.min
        if dist != 0.0:
            projA = constraint.anchorA.final.dotVV(coords, constraint.anchorB.final) / (dist)
            value = max(2 * abs(dist/2.0 - projA), constraint.min, 0.0)

        self.entity = constraint
        self.newValue = value
        self.oldValue = constraint.max

    def execute(self):
        self.entity.max = self.newValue

    def undo(self):
        self.entity.max = self.oldValue


# User settable params

class ComSetUserParam(CommandUndo):

    def __init__(self, param, value):
        self.param = param
        self.oldUserFlag = self.param.userDefined
        self.oldUserVal = self.param.user
        self.value = value
    
    def execute(self):
        self.param.setFromUser(self.value)

    def undo(self):
        self.param.userDefined = self.oldUserFlag
        self.param.user = self.oldUserVal


class ComResetUserParam(CommandUndo):

    def __init__(self, param):
        self.param = param
        self.oldUserFlag = self.param.userDefined
    
    def execute(self):
        self.param.userDefined = False
        

    def undo(self):
        self.param.userDefined = self.oldUserFlag


class ComSetUserCoords(CommandUndo):

    def __init__(self, coord, x:float, y:float):
        self.coord = coord
        self.oldUserFlag = self.coord.userDefined
        self.oldUserCoord = self.coord.user.clone()
        self.newCoord = V2(x, y)
    
    def execute(self):
        self.coord.setFromUserV(self.newCoord)

    def undo(self):
        self.coord.userDefined = self.oldUserFlag
        self.coord.user.setFromV(self.oldUserCoord)


class ComResetUserCoords(CommandUndo):

    def __init__(self, coords):
        self.coords = coords
        self.oldUserFlag = self.coords.userDefined
    
    def execute(self):
        self.coords.userDefined = False
        

    def undo(self):
        self.coords.userDefined = self.oldUserFlag

# END of User settable params



class ComSetPivot(CommandUndo):

    def __init__(self, pivot:V2, point:V2):
        self.pivot = pivot
        self.newWorld = point.clone()
        self.oldWorld = pivot.clone()

    def execute(self):
        self.pivot.setFromV(self.newWorld)

    def undo(self):
        self.pivot.setFromV(self.oldWorld)


class ComSetPivotXY(CommandUndo):

    def __init__(self, pivot:V2, x:float, y:float):
        self.pivot = pivot
        self.newWorld = V2(x, y)
        self.oldWorld = pivot.clone()

    def execute(self):
        self.pivot.setFromV(self.newWorld)

    def undo(self):
        self.pivot.setFromV(self.oldWorld)


class ComSetPivotRelativeXY(CommandUndo):

    def __init__(self, pivot:V2, dx:float, dy:float):
        self.pivot = pivot
        self.newWorld = V2(dx, dy).tV(pivot)
        self.oldWorld = pivot.clone()
        

    def execute(self):
        self.pivot.setFromV(self.newWorld)

    def undo(self):
        self.pivot.setFromV(self.oldWorld)


# #################


class ComSetContainerPosXY(CommandUndo):

    def __init__(self, obj: Container, x:float, y:float):
        self.object = obj
        cog = obj.physics.cog.get()
        self.newAnchor = V2().unTV(cog).tD(x, y)
        self.oldAnchor = self.object.transform.objectAnchor.clone()

    def execute(self):
        self.object.transform.objectAnchor.setFromV(self.newAnchor)
        #self.object.recalcPhysics()

    def undo(self):
        self.object.transform.objectAnchor.setFromV(self.oldAnchor)
        #self.object.recalcPhysics()


class ComApplyContainerPosXY(CommandUndo):

    def __init__(self, obj: Container, dx:float, dy:float):
        self.object = obj
        self.newAnchor = self.object.transform.objectAnchor.clone().tD(dx,dy)
        self.oldAnchor = self.object.transform.objectAnchor.clone()

    def execute(self):
        self.object.transform.objectAnchor.setFromV(self.newAnchor)
        #self.object.recalcPhysics()

    def undo(self):
        self.object.transform.objectAnchor.setFromV(self.oldAnchor)
        #self.object.recalcPhysics()


class ComSetContainerAngle(CommandUndo):

    def __init__(self, obj:Container, pivot: V2, angle:float):
        self.object = obj
        self.pivot = pivot.clone()
        self.angle = Angle().set(angle).sub(obj.transform.objectAngle.angle)
        self.negAngle = Angle().set( - self.angle.angle)
        

    def execute(self):
        self.object.transform.rotate(self.angle, self.pivot)
        #self.object.recalcPhysics()

    def undo(self):
        self.object.transform.rotate(self.negAngle, self.pivot)
        #self.object.recalcPhysics()


class ComApplyContainerRotate(CommandUndo):

    def __init__(self, obj: Container, pivot: V2, angle:float):

        self.object = obj
        self.pivot = pivot.clone()
        self.angle = Angle().set( angle)
        self.negAngle = Angle().set( - angle)

    def execute(self):
        self.object.transform.rotate(self.angle, self.pivot)
        #self.object.recalcPhysics()

    def undo(self):
        self.object.transform.rotate(self.negAngle, self.pivot)
        #self.object.recalcPhysics()


class ComSetContainerAngleDeg(CommandUndo):

    def __init__(self, obj:Container, pivot: V2, angleDeg:float):
        self.object = obj
        self.pivot = pivot.clone()
        self.angle = Angle().fromDeg(angleDeg).sub(obj.transform.objectAngle.angle)
        self.negAngle = Angle().set( - self.angle.angle)
        

    def execute(self):
        self.object.transform.rotate(self.angle, self.pivot)
        #self.object.recalcPhysics()

    def undo(self):
        self.object.transform.rotate(self.negAngle, self.pivot)
        #self.object.recalcPhysics()


class ComApplyContainerRotateDeg(CommandUndo):

    def __init__(self, obj: Container, pivot: V2, angleDeg:float):

        self.object = obj
        self.pivot = pivot.clone()
        self.angle = Angle().fromDeg(angleDeg)
        self.negAngle = Angle().set( - self.angle.angle)

    def execute(self):
        self.object.transform.rotate(self.angle, self.pivot)
        #self.object.recalcPhysics()

    def undo(self):
        self.object.transform.rotate(self.negAngle, self.pivot)
        #self.object.recalcPhysics()


class ComSetContainerScale(CommandUndo):

    def __init__(self, obj:Container, pivot:V2, scale:float):
        self.object = obj
        self.pivot = pivot
        self.factor = scale / obj.transform.objectScale

    def execute(self):
        self.object.transform.scale(self.factor, self.pivot)
        #self.object.recalcPhysics()

    def undo(self):
        self.object.transform.scale(1.0/self.factor, self.pivot)
        #self.object.recalcPhysics()


class ComApplyContainerScale(CommandUndo):

    def __init__(self, obj: Container, pivot:V2, scale:float):
        self.object = obj
        self.pivot = pivot
        self.factor = scale

    def execute(self):
        self.object.transform.scale(self.factor, self.pivot)
        #self.object.recalcPhysics()

    def undo(self):
        self.object.transform.scale(1.0/self.factor, self.pivot)
        #self.object.recalcPhysics()


# #################



# MAPPING Commands

# class ComSetMappingOffset(CommandUndo):

#     def __init__(self, mapping:TextureMapping, newOffset:Tuple[int, int]):
#         self.mapping = mapping
#         self.newOffset = newOffset
#         self.oldOffset = mapping.mappingOffset
#         self.oldSize = mapping.mappingSize

#     def execute(self):
#         self.mapping.setMappingOffset(self.newOffset)

#     def undo(self):
#         self.mapping.mappingOffset = self.oldOffset
#         self.mapping.mappingSize = self.oldSize


# class ComSetMappingSize(CommandUndo):

#     def __init__(self, mapping:TextureMapping, newSize:Tuple[int, int]):
#         self.mapping = mapping
#         self.newSize = newSize
#         self.oldOffset = mapping.mappingOffset
#         self.oldSize = mapping.mappingSize

#     def execute(self):
#         self.mapping.setMappingSize(self.newSize)

#     def undo(self):
#         self.mapping.mappingOffset = self.oldOffset
#         self.mapping.mappingSize = self.oldSize


class ComSetMappingFromSelection(CommandUndo):

    def __init__(self, mapping:TextureMapping, selection:Selection):
        self.mapping = mapping
        self.selection = selection
        self.oldOffset = mapping.mappingOffset
        self.oldSize = mapping.mappingSize

    def execute(self):
        self.mapping.setMappingFromSelection(self.selection)

    def undo(self):
        self.mapping.mappingOffset = self.oldOffset
        self.mapping.mappingSize = self.oldSize


class ComSetMappingAnchor(CommandUndo):

    def __init__(self, mapping:TextureMapping, anchor:V2):
        self.mapping = mapping
        self.newAnchor = anchor
        self.oldAnchor = mapping.anchor

    def execute(self):
        self.mapping.setAnchor(self.newAnchor.x, self.newAnchor.y)

    def undo(self):
        self.mapping.setAnchor(self.oldAnchor[0], self.oldAnchor[1])

# END OF MAPPING commands

# begin of TRANSFORM COMMANDS
class ComCancelTransform(Command):

    def __init__(self, transform: ContinuousTransform):
        self.transform = transform
    
    def execute(self):
        if self.transform.obj:
            self.transform.obj.transform.objectAnchor.setFromV(self.transform.transform.objectAnchor)
            self.transform.obj.transform.objectAngle.setA(self.transform.transform.objectAngle)
            self.transform.obj.transform.objectScale = self.transform.transform.objectScale
        self.transform.active = False


class ComStartTransform(CommandUndo):

    def __init__(self, transform: ContinuousTransform, obj: Union[BodyI, ShapeI, TextureMapping], 
                 startPoint: V2, pivot: V2, mode: Literal[0,1,2,3,4,5,6,7]):
        self.transform = transform
        
        self.newObj = obj
        self.startPoint = startPoint.clone()
        self.pivot = pivot.clone()
        self.mode = mode
        self.processed = False

        if self.newObj:
            self.oldObjectAnchor = self.newObj.transform.objectAnchor.clone()
            self.oldObjectAngle = self.newObj.transform.objectAngle.clone()
            self.oldObjectScale = self.newObj.transform.objectScale
    
    def execute(self):
        if self.processed:
            self.newObj.transform.objectAnchor.setFromV(self.newObjectAnchor)
            self.newObj.transform.objectAngle.setA(self.newObjectAngle)
            self.newObj.transform.objectScale = self.newObjectScale
            self.transform.active = False
        else:
            self.transform.setMode(self.mode)
            self.transform.init(self.newObj, self.startPoint, self.pivot)
            self.transform.active = True

    def undo(self):
        if self.newObj:
            if not self.processed:
                self.newObjectAnchor = self.newObj.transform.objectAnchor.clone()
                self.newObjectAngle = self.newObj.transform.objectAngle.clone()
                self.newObjectScale = self.newObj.transform.objectScale
                self.processed = True
            self.newObj.transform.objectAnchor.setFromV(self.oldObjectAnchor)
            self.newObj.transform.objectAngle.setA(self.oldObjectAngle)
            self.newObj.transform.objectScale = self.oldObjectScale
        self.transform.active = False


class ComApplyTransform(Command):

    def __init__(self, transform: ContinuousTransform):
        self.transform = transform
    
    def execute(self):
        self.transform.active = False


# DEBUG info
coms = []

class CommandExec:

    _instance: "CommandExec" = None

    @staticmethod
    def getInstance() -> "CommandExec":
        if CommandExec._instance is None:
            CommandExec._instance = CommandExec()
        return CommandExec._instance
    
    def __init__(self):
        self.processed = collections.deque(maxlen=100)
        self.reverse   = collections.deque()
        self.toProcess = collections.deque()

    @staticmethod
    def addCommand(command:Command):
        CommandExec.getInstance().toProcess.append(command)

    @staticmethod
    def clearFuture() -> None:
        CommandExec.getInstance().reverse.clear()

    @staticmethod
    def clearAll() -> None:
        instance = CommandExec.getInstance()
        instance.processed.clear()
        instance.reverse.clear()
        instance.toProcess.clear()

    @staticmethod
    def process() -> None:
        instance = CommandExec.getInstance()
        while len(instance.toProcess):
            command:Command = instance.toProcess.popleft()
            command.execute()
            if command.hasUndo():
                instance.clearFuture()
                instance.processed.append(command)
            
    @staticmethod
    def undo():
        instance = CommandExec.getInstance()
        if len(instance.processed):
            command:CommandUndo = instance.processed.pop()
            command.undo()
            instance.reverse.appendleft(command)

    @staticmethod
    def redo():
        instance = CommandExec.getInstance()
        if len(instance.reverse):
            command:CommandUndo = instance.reverse.popleft()
            command.execute()
            instance.processed.append(command)