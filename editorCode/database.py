from typing import List
from .shapeInternals.editorShapeI import ShapeI
from .shapeInternals.editorBodyI import BodyI
from .constraintInternals.editorConstraintI import ConstraintI
from .constraintInternals.constraintFactory import constraintFactory
from .shapeInternals.shapeFactory import shapeFactory
from .shapeInternals.bodyFactory import bodyFactory


def _getUniqueLabel(label:str, listOfLabels: List[str], default:str = 'NEW'):
    if label == '':
        label = default
    while label in listOfLabels:
        ind: int = label.rfind('_')
        newend: str = '_1'
        if ind > 0:
            end: str = label[ind+1:]
            if end:
                try:
                    newend: str = f'_{str(int(end) + 1)}'
                    label = label[:ind]
                except:
                    pass
        label += newend
    return label


class Database:

    _instance: "Database" = None

    @staticmethod
    def getInstance() -> "Database":
        if Database._instance is None:
            Database._instance = Database()
        return Database._instance

    def __init__(self):
        self.bodies: List[BodyI] = []
        self.shapeList: List[ShapeI] = []
        self.constraints: List[ConstraintI] = []
        self.currentBody: BodyI = None
        self.currentShape: ShapeI = None
        self.currentConstraint: ConstraintI = None


    # TODO 
    # get common functionality to utility functions

    # BODY management

    def setCurrentBodyByLabel(self, label:str):
        body = self.getBodyByLabel(label)
        if body:
            if self.currentBody != body:
                self.currentBody = body
                if body.shapes:
                    self.currentShape = body.shapes[-1]
                    return
                else:
                    self.currentShape = None
                    return
        else:
            if self.currentBody not in self.bodies:
                self.currentBody = None
                self.currentShape = None

    def setAnyBodyAsCurrent(self):
        if self.bodies:
            self.setCurrentBodyByLabel(self.bodies[-1].label)
        else:
            self.currentBody = None
            self.currentShape = None

    def setAnyShapeAsCurrent(self):
        currentBody = self.getCurrentBody()
        if currentBody:
            shapes = self.getAllNewShapesOfBody(currentBody.label)
            if shapes:
                self.setCurrentShapeByLabel(shapes[-1].label)
                return
        self.setCurrentShapeByLabel(None)

    def setCurrentShapeByLabel(self, label:str):
        shape = self.getNewShapeByLabel(label)
        if shape and self.currentShape != shape:
            self.currentShape = shape

    def getCurrentBody(self) -> BodyI:
        return self.currentBody
    
    def getCurrentShape(self) -> ShapeI:
        return self.currentShape

    def swap(self, index1: int, index2: int, array:List):
        body = array[index1]
        array[index1] = array[index2]
        array[index2] = body

    def shiftBodyUp(self, body):
        if len(self.bodies) > 1:
            index = self.getBodyIndex(body)
            if index > -1:
                swapIndex = (index + len(self.bodies) - 1) % len(self.bodies)
                self.swap(index, swapIndex, self.bodies)

    def shiftBodyDown(self, body):
        if len(self.bodies) > 1:
            index = self.getBodyIndex(body)
            if index > -1:
                swapIndex = (index + 1) % len(self.bodies)
                self.swap(index, swapIndex, self.bodies)

    def getAllBodyLabels(self):
        return tuple(map(lambda x: x.label, self.bodies))

    def getNextBody(self, body:BodyI):
        index = self.getBodyIndex(body)
        if len(self.bodies) > 1:
            newIndex = (len(self.bodies) + index - 1) % len(self.bodies)
            return self.bodies[newIndex]
        else:
            return None
        
    def getNextBodyLabel(self, body:BodyI):
        index = self.getBodyIndex(body)
        if len(self.bodies) > 1:
            newIndex = (len(self.bodies) + index - 1) % len(self.bodies)
            return self.bodies[newIndex].label
        else:
            return None

    def renameBody(self, body:BodyI, label):
        newLabel = _getUniqueLabel(label, self.getAllBodyLabels(), 'BODY')
        body.label = newLabel

    def getBodyByLabel(self, label:str):
        for s in self.bodies:
            if s.label == label:
                return s
        return None

    def cloneBodyFully(self, label:str):
        pass

    def addBody(self, body:BodyI, at: int = -1):
        if at < 0:
            at = len(self.bodies)
        self.bodies.insert(at, body)
        return body
        
    def createBody(self, label: str, typeID:str):
        newLabel = _getUniqueLabel(label, self.getAllBodyLabels(), 'BODY')
        return bodyFactory(newLabel, typeID)

    def getBodyIndex(self, body):
        if body in self.bodies:
            return self.bodies.index(body)
        return -1

    def deleteBody(self, label):
        body = self.getBodyByLabel(label)
        if body:
            self.bodies.remove(body)
        return body


    # NEW SHAPE management
    def shiftNewShapeUp(self, shape: ShapeI):
        parent = self.getNewShapeParent(shape)
        if parent:
            shapeCount = len(parent.shapes)
            if shapeCount > 1:
                oldIndex = parent.shapes.index(shape)
                newIndex = (oldIndex - 1 + shapeCount) % shapeCount
                self.swap(oldIndex, newIndex, parent.shapes)

    def shiftNewShapeDown(self, shape: ShapeI):
        parent = self.getNewShapeParent(shape)
        if parent:
            shapeCount = len(parent.shapes)
            if shapeCount > 1:
                oldIndex = parent.shapes.index(shape)
                newIndex = (oldIndex + 1) % shapeCount
                self.swap(oldIndex, newIndex, parent.shapes)
        
    def getNewShapeParent(self, shape: ShapeI) -> BodyI:
        for parent in self.bodies:
            if shape in parent.shapes:
                return parent
        return None
    
    def getAllNewShapeLabels(self):
        return [x.label for x in self.shapeList]

    def getAllNewShapeLabelsForBody(self, bodyLabel:str) -> List[str]:
        return [x.label for x in self.getAllNewShapesOfBody(bodyLabel)]
    
    def getAllNewShapesOfBody(self, bodyLabel:str) -> List[ShapeI]:
        body = self.getBodyByLabel(bodyLabel)
        if body:
            return body.shapes
        return []

    def getNewShapeByLabel(self, label:str) -> ShapeI:
        for s in self.shapeList:
            if s.label == label:
                return s
        return None

    def getNewShapeByIndex(self, ind:int) -> ShapeI:
        if ind < len(self.shapeList):
            return self.shapeList[ind]
        return None
        
    def renameNewShape(self, shape:ShapeI, label):
        newLabel = _getUniqueLabel(label, self.getAllNewShapeLabels(), 'SHAPE')
        shape.label = newLabel

    def createNewShape(self, label: str, typeID:str):
        newLabel = _getUniqueLabel(label, self.getAllNewShapeLabels(), 'SHAPE')
        return shapeFactory(newLabel, typeID)

    def addNewShape(self, shape:ShapeI, parent:BodyI, at: int = -1):
        if parent in self.bodies:
            if at < 0:
                at = len(parent.shapes)
            self.shapeList.append(shape)
            parent.shapes.insert(at, shape)
            return shape
        return None

    def deleteNewShape(self, label):
        shape = self.getNewShapeByLabel(label)
        if shape:
            parent = self.getNewShapeParent(shape)
            if parent:
                parent.shapes.remove(shape)
            self.shapeList.remove(shape)
        return shape
    



    # CONSTRAINT management

    def setCurrentConstraintByLabel(self, label:str):
        entity = self.getConstraintByLabel(label)
        if entity:
            if self.currentConstraint != entity:
                self.currentConstraint = entity
        else:
            if self.currentConstraint not in self.constraints:
                self.currentConstraint = None

    def setAnyConstraintAsCurrent(self):
        if self.constraints:
            self.setCurrentConstraintByLabel(self.constraints[-1].label)
        else:
            self.currentConstraint = None

    def getCurrentConstraint(self) -> ConstraintI:
        return self.currentConstraint

    def shiftConstraintUp(self, constraint):
        if len(self.constraints) > 1:
            index = self.getConstraintIndex(constraint)
            if index > -1:
                swapIndex = (index + len(self.constraints) - 1) % len(self.constraints)
                self.swap(index, swapIndex, self.constraints)

    def shiftConstraintDown(self, constraint):
        if len(self.bodies) > 1:
            index = self.getConstraintIndex(constraint)
            if index > -1:
                swapIndex = (index + 1) % len(self.constraints)
                self.swap(index, swapIndex, self.constraints)

    def getAllConstraintLabels(self):
        return tuple(map(lambda x: x.label, self.constraints))

    def getNextConstraint(self, constraint:ConstraintI):
        index = self.getConstraintIndex(constraint)
        if len(self.constraints) > 1:
            newIndex = (len(self.constraints) + index - 1) % len(self.constraints)
            return self.constraints[newIndex]
        else:
            return None

    def renameConstraint(self, constraint:ConstraintI, label):
        newLabel = _getUniqueLabel(label, self.getAllConstraintLabels(), 'CSTR')
        constraint.label = newLabel

    def getConstraintByLabel(self, label:str) -> ConstraintI:
        for s in self.constraints:
            if s.label == label:
                return s
        return None

    def cloneConstraintFully(self, label:str):
        pass

    def addConstraint(self, constraint:ConstraintI, at: int = -1):
        if at < 0:
            at = len(self.constraints)
        self.constraints.insert(at, constraint)
        return constraint
        
    def createConstraint(self, label: str, typeID:str):
        newLabel = _getUniqueLabel(label, self.getAllConstraintLabels(), 'CSTR')
        return constraintFactory(newLabel, typeID)

    def getConstraintIndex(self, constraint):
        if constraint in self.constraints:
            return self.constraints.index(constraint)
        return -1

    def deleteConstraint(self, label):
        constraint = self.getConstraintByLabel(label)
        if constraint:
            self.constraints.remove(constraint)
        return constraint
    
    def getConstraintsOfBody(self, label):
        body = self.getBodyByLabel(label)
        result = []
        if body:
            for constraint in self.constraints:
                if body == constraint.bodyA:
                    result.append((constraint, True))
                elif body == constraint.bodyB:
                    result.append((constraint, False))
        return result