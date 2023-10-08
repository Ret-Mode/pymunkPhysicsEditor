from typing import List, Tuple
from .shapeInternals.editorShapeI import ShapeI
from .shapeInternals.editorBodyI import BodyI
from .constraintInternals.editorConstraintI import ConstraintI
from .textureMapping import TextureMapping
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
        self.mappings: List[TextureMapping] = []
        self.currentBody: BodyI = None
        self.currentShape: ShapeI = None
        self.currentConstraint: ConstraintI = None
        self.currentMapping: TextureMapping = None
        self.currentMappingChannel: int = -1


    # TODO 
    # get common functionality to utility functions

    # BODY management

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
    

    # TEXTURE management

    def createMapping(self, channel:int, textureSize:Tuple[int]):
        label = f'MAP:{channel}'
        newLabel = _getUniqueLabel(label, self.getAllMappingLabels(), f'MAP:{channel}')
        return TextureMapping(newLabel, channel, textureSize)

    def addMapping(self, mapping:TextureMapping, at: int = -1):
        if at < 0:
            at = len(self.mappings)
        self.mappings.insert(at, mapping)
        return mapping
    
    def getAllMappingLabels(self):
        return tuple(map(lambda x: x.label, self.mappings))
    
    def getAllMappings(self):
        return self.mappings
    
    def getAllMappingLabelsOfChannel(self, channel:int):
        return tuple(map(lambda x: x.label, filter(lambda x: x.channel == channel, self.mappings)))

    def getAllMappingsOfChannel(self, channel:int):
        return tuple(filter(lambda x: x.channel == channel, self.mappings))
    
    def getAllMappingsOfBodyAndChannel(self, body:BodyI, channel:int):
        return tuple(filter(lambda x: x.channel == channel and x.body == body, self.mappings))
    
    def getAllMappingsOfBody(self, body:BodyI):
        return tuple(filter(lambda x: x.body == body, self.mappings))

    def getMappingIndex(self, mapping:TextureMapping):
        if mapping in self.mappings:
            return self.mappings.index(mapping)
        return -1

    def deleteMapping(self, label):
        mapping = self.getMappingByLabel(label)
        if mapping:
            self.mappings.remove(mapping)
        return mapping
    
    def getNextMapping(self, mapping:TextureMapping):
        index = self.getMappingIndex(mapping)
        if len(self.mappings) > 1:
            newIndex = (len(self.mappings) + index - 1) % len(self.mappings)
            return self.mappings[newIndex]
        else:
            return None

    def getNextMappingOfChannel(self, mapping:TextureMapping, channel:int):
        mappings = self.getAllMappingLabelsOfChannel(channel)
        if mapping in mappings:
            ind = mappings.index(mapping)
        if len(mappings) > 1:
            newIndex = (len(mappings) + ind - 1) % len(mappings)
            return mappings[newIndex]
        else:
            return None
        
    def getNextMappingLabel(self, mapping:TextureMapping):
        index = self.getMappingIndex(mapping)
        if len(self.mappings) > 1:
            newIndex = (len(self.mappings) + index - 1) % len(self.mappings)
            return self.mappings[newIndex].label
        else:
            return None

    def getNextMappingLabelOfChannel(self, mapping:TextureMapping, channel:int):
        mappings = self.getAllMappingLabelsOfChannel(channel)
        if mapping in mappings:
            ind = mappings.index(mapping)
        if len(mappings) > 1:
            newIndex = (len(mappings) + ind - 1) % len(mappings)
            return self.getMappingByLabel(mappings[newIndex])
        else:
            return None

    def renameMapping(self, mapping:TextureMapping, label):
        newLabel = _getUniqueLabel(label, self.getAllMappingLabels(), f'MAP_{mapping.channel}')
        mapping.label = newLabel

    def getMappingByLabel(self, label:str):
        for s in self.mappings:
            if s.label == label:
                return s
        return None
