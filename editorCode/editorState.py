from .shapeInternals.editorShapeI import ShapeI
from .shapeInternals.editorBodyI import BodyI
from .constraintInternals.editorConstraintI import ConstraintI
from .textureMapping import TextureMapping
from .database import Database

class EditorState:

    _instance: "EditorState" = None

    @staticmethod
    def getInstance() -> "EditorState":
        if EditorState._instance is None:
            EditorState._instance = EditorState()
        return EditorState._instance
    
    def __init__(self):
        self.currentBody: BodyI = None
        self.currentShape: ShapeI = None
        self.currentConstraint: ConstraintI = None
        self.currentMapping: TextureMapping = None
        self.currentMappingChannel: int = -1
        self.database:Database = Database.getInstance()

    def setCurrentBodyByLabel(self, label:str):
        body = self.database.getBodyByLabel(label)
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
            if self.currentBody not in self.database.bodies:
                self.currentBody = None
                self.currentShape = None

    def setAnyBodyAsCurrent(self):
        if self.database.bodies:
            self.setCurrentBodyByLabel(self.database.bodies[-1].label)
        else:
            self.currentBody = None
            self.currentShape = None

    def setAnyShapeAsCurrent(self):
        currentBody = self.getCurrentBody()
        if currentBody:
            shapes = self.database.getAllNewShapesOfBody(currentBody.label)
            if shapes:
                self.setCurrentShapeByLabel(shapes[-1].label)
                return
        self.setCurrentShapeByLabel(None)

    def getCurrentBody(self) -> BodyI:
        return self.currentBody
    
    def setCurrentShapeByLabel(self, label:str):
        shape = self.database.getNewShapeByLabel(label)
        if shape and self.currentShape != shape:
            self.currentShape = shape

    def getCurrentShape(self) -> ShapeI:
        return self.currentShape
    
    def setCurrentConstraintByLabel(self, label:str):
        entity = self.database.getConstraintByLabel(label)
        if entity:
            if self.currentConstraint != entity:
                self.currentConstraint = entity
        else:
            if self.currentConstraint not in self.database.constraints:
                self.currentConstraint = None

    def setAnyConstraintAsCurrent(self):
        if self.database.constraints:
            self.setCurrentConstraintByLabel(self.database.constraints[-1].label)
        else:
            self.currentConstraint = None

    def getCurrentConstraint(self) -> ConstraintI:
        return self.currentConstraint
        
    def getCurrentMapping(self) -> TextureMapping:
        return self.currentMapping
    
    def getCurrentMappingChannel(self) -> int:
        return self.currentMappingChannel
    
    def setCurrentMappingByLabel(self, label:str):
        mapping = self.database.getMappingByLabel(label)
        if mapping:
            if self.currentMapping != mapping:
                self.currentMapping = mapping
                self.currentMappingChannel = mapping.channel
        else:
            self.currentMapping = None
            self.currentMappingChannel = None

    def setAnyMappingAsCurrent(self):
        if self.database.mappings:
            self.setCurrentMappingByLabel(self.database.mappings[-1].label)
            self.currentMappingChannel = self.database.mappings[-1].channel
        else:
            self.currentMapping = None
            self.currentMappingChannel = None

    def setAnyMappingFromChannelAsCurrent(self, channel:int):
        mappings = self.database.getAllMappingLabelsOfChannel(channel)
        if mappings:
            self.setCurrentMappingByLabel(mappings[-1])
            self.currentMappingChannel = channel
        else:
            self.currentMapping = None
            self.currentMappingChannel = None