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
        self.currentMappingChannel: int = 0
        self.database:Database = Database.getInstance()

    def clear(self):
        self.currentBody = None
        self.currentShape = None
        self.currentConstraint = None
        self.currentMapping = None
        self.currentMappingChannel = 0
        self.database = Database.getInstance()

        self.setAnyBodyAsCurrent()
        self.setAnyShapeAsCurrent()
        self.setAnyConstraintAsCurrent()
        self.setAnyMappingAsCurrent()

    def setCurrentBodyAndShape(self, body:BodyI, shape:ShapeI):
        if shape is not None and body is not None:
            # sanity check
            assert shape in body.shapes
        self.currentBody = body
        self.currentShape = shape

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

    def setNextBodyAsCurrent(self) -> None:
        bodies = self.database.bodies
        if not bodies:
            self.currentBody = None
            self.currentShape = None
            return
        amount = len(bodies)
        if amount == 1 or (self.currentBody not in bodies):
            self.setCurrentBodyByLabel(bodies[0].label)
            return
        self.setCurrentBodyByLabel(bodies[(bodies.index(self.currentBody) + 1) % amount].label)

    def setPrevBodyAsCurrent(self) -> None:
        bodies = self.database.bodies
        if not bodies:
            self.currentBody = None
            self.currentShape = None
            return
        amount = len(bodies)
        if amount == 1 or (self.currentBody not in bodies):
            self.setCurrentBodyByLabel(bodies[-1].label)
            return
        self.setCurrentBodyByLabel(bodies[(bodies.index(self.currentBody) - 1 + amount) % amount].label)

    def setAnyBodyAsCurrent(self):
        if self.database.bodies:
            self.setCurrentBodyByLabel(self.database.bodies[-1].label)
        else:
            self.currentBody = None
            self.currentShape = None

    def getCurrentBody(self) -> BodyI:
        if self.currentBody:
            return self.currentBody
        self.setAnyBodyAsCurrent()
        return self.currentBody
    
    def setAnyShapeAsCurrent(self):
        currentBody = self.getCurrentBody()
        if currentBody:
            shapes = self.database.getAllNewShapesOfBody(currentBody.label)
            if shapes:
                self.setCurrentShapeByLabel(shapes[-1].label)
                return
        self.setCurrentShapeByLabel(None)

    def setCurrentShapeByLabel(self, label:str):
        shape = self.database.getNewShapeByLabel(label)
        if shape and self.currentShape != shape:
            self.currentShape = shape

    def getCurrentShape(self) -> ShapeI:
        if self.currentShape:
            return self.currentShape
        self.setAnyShapeAsCurrent()
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
    
    def setCurrentMappingChannel(self, channel:int) -> None:
        if self.currentMappingChannel != channel:
            self.currentMappingChannel = channel
        if mappings := self.database.getAllMappingsOfChannel(channel):
            if self.currentMapping not in self.database.getAllMappingsOfChannel(channel):
                self.currentMapping = mappings[0]
        else:
            self.currentMapping = None


    def setCurrentMappingByLabel(self, label:str):
        mapping = self.database.getMappingByLabel(label)
        if mapping:
            if self.currentMapping != mapping:
                self.currentMapping = mapping
                self.currentMappingChannel = mapping.channel
        else:
            self.currentMapping = None

    def setAnyMappingAsCurrent(self):
        if self.database.mappings:
            self.setCurrentMappingByLabel(self.database.mappings[-1].label)
            self.currentMappingChannel = self.database.mappings[-1].channel
        else:
            self.currentMapping = None

    def setAnyMappingFromChannelAsCurrent(self, channel:int):
        mappings = self.database.getAllMappingLabelsOfChannel(channel)
        if mappings:
            self.setCurrentMappingByLabel(mappings[-1])
            self.currentMappingChannel = channel
        else:
            self.currentMapping = None