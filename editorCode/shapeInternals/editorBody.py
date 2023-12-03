from ..editorTypes import Mat, ContainerTransform, BoundingBox
from .editorBodyPhysics import BodyPhysics, BodyStaticPhysics
from .editorShapeI import ShapeI
from .editorBodyI import BodyI
from typing import List


class BodyDynamic(BodyI):
    
    def __init__(self, label:str):
        super().__init__(label)
        
        self.label: str 

        self.box = BoundingBox()
        self.transform = ContainerTransform()
        
        self.type :str = BodyI.DYNAMIC
        self.shapes: List[ShapeI] = []

        self.physics : BodyPhysics = BodyPhysics()

    def updatePos(self, transform:Mat):
        for shape in self.shapes:
            shape.updatePos(shape.transform.getMat().mulPre(transform))
        if self.shapes:
            shape = self.shapes[0]
            xmin = shape.box.center.final.x - shape.box.halfWH.final.x
            xmax = shape.box.center.final.x + shape.box.halfWH.final.x
            ymin = shape.box.center.final.y - shape.box.halfWH.final.y
            ymax = shape.box.center.final.y + shape.box.halfWH.final.y
            for shape in self.shapes[1:]:
                xmin2 = shape.box.center.final.x - shape.box.halfWH.final.x
                xmax2 = shape.box.center.final.x + shape.box.halfWH.final.x
                ymin2 = shape.box.center.final.y - shape.box.halfWH.final.y
                ymax2 = shape.box.center.final.y + shape.box.halfWH.final.y
                xmin = min(xmin, xmin2)
                xmax = max(xmax, xmax2)
                ymin = min(ymin, ymin2)
                ymax = max(ymax, ymax2)
            self.box.setFinal(xmin, ymin, xmax, ymax)
        else:
            self.box.setFinal(0.0, 0.0, 0.0, 0.0)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['physics'] = {'hasCustomMass' : self.physics.mass.userDefined,
                           'hasCustomMoment' : self.physics.moment.userDefined,
                           'hasCustomCog' : self.physics.cog.userDefined}

        this['physics']['customMass'] = self.physics.mass.final
        this['physics']['customMoment'] = self.physics.moment.final
        this['physics']['cog'] = [self.physics.cog.final.x, self.physics.cog.final.y]

        this['type'] = self.type
        this['shapes'] = {}
        for shape in self.shapes:
            shape.getJSONDict(this['shapes'])
        parent[self.label] = this

    def recalcPhysics(self):
        self.physics.recalcPhysics(self.shapes, self.transform)


class BodyKinematic(BodyI):
    
    def __init__(self, label:str):
        super().__init__(label)
        
        self.label: str 

        self.box = BoundingBox()
        self.transform = ContainerTransform()
        
        self.type :str = BodyI.KINEMATIC
        self.shapes: List[ShapeI] = []

        self.physics : BodyPhysics = BodyStaticPhysics()

    def updatePos(self, transform:Mat):
        for shape in self.shapes:
            shape.updatePos(shape.transform.getMat().mulPre(transform))
        if self.shapes:
            shape = self.shapes[0]
            xmin = shape.box.center.final.x - shape.box.halfWH.final.x
            xmax = shape.box.center.final.x + shape.box.halfWH.final.x
            ymin = shape.box.center.final.y - shape.box.halfWH.final.y
            ymax = shape.box.center.final.y + shape.box.halfWH.final.y
            for shape in self.shapes[1:]:
                xmin2 = shape.box.center.final.x - shape.box.halfWH.final.x
                xmax2 = shape.box.center.final.x + shape.box.halfWH.final.x
                ymin2 = shape.box.center.final.y - shape.box.halfWH.final.y
                ymax2 = shape.box.center.final.y + shape.box.halfWH.final.y
                xmin = min(xmin, xmin2)
                xmax = max(xmax, xmax2)
                ymin = min(ymin, ymin2)
                ymax = max(ymax, ymax2)
            self.box.setFinal(xmin, ymin, xmax, ymax)
        else:
            self.box.setFinal(0.0, 0.0, 0.0, 0.0)

    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['physics'] = {'hasCustomMass' : self.physics.mass.userDefined,
                           'hasCustomMoment' : self.physics.moment.userDefined,
                           'hasCustomCog' : self.physics.cog.userDefined}

        this['physics']['customMass'] = self.physics.mass.final
        this['physics']['customMoment'] = self.physics.moment.final
        this['physics']['cog'] = [self.physics.cog.final.x, self.physics.cog.final.y]

        this['type'] = self.type
        this['shapes'] = {}
        for shape in self.shapes:
            shape.getJSONDict(this['shapes'])
        parent[self.label] = this

    def recalcPhysics(self):
        pass


class BodyStatic(BodyI):
    
    def __init__(self, label:str):
        super().__init__(label)
        
        self.label: str 

        self.box = BoundingBox()
        self.transform = ContainerTransform()
        
        self.type :str = BodyI.STATIC
        self.shapes: List[ShapeI] = []

        self.physics : BodyPhysics = BodyStaticPhysics()

    # TODO
    def updatePos(self, transform:Mat):
        for shape in self.shapes:
            shape.updatePos(shape.transform.getMat().mulPre(transform))
        if self.shapes:
            shape = self.shapes[0]
            xmin = shape.box.center.final.x - shape.box.halfWH.final.x
            xmax = shape.box.center.final.x + shape.box.halfWH.final.x
            ymin = shape.box.center.final.y - shape.box.halfWH.final.y
            ymax = shape.box.center.final.y + shape.box.halfWH.final.y
            for shape in self.shapes[1:]:
                xmin2 = shape.box.center.final.x - shape.box.halfWH.final.x
                xmax2 = shape.box.center.final.x + shape.box.halfWH.final.x
                ymin2 = shape.box.center.final.y - shape.box.halfWH.final.y
                ymax2 = shape.box.center.final.y + shape.box.halfWH.final.y
                xmin = min(xmin, xmin2)
                xmax = max(xmax, xmax2)
                ymin = min(ymin, ymin2)
                ymax = max(ymax, ymax2)
            self.box.setFinal(xmin, ymin, xmax, ymax)
        else:
            self.box.setFinal(0.0, 0.0, 0.0, 0.0)

    # TODO
    def getJSONDict(self, parent:dict):
        assert self.label not in parent
        this = {}
        this['physics'] = {'hasCustomMass' : self.physics.mass.userDefined,
                           'hasCustomMoment' : self.physics.moment.userDefined,
                           'hasCustomCog' : self.physics.cog.userDefined}

        this['physics']['customMass'] = self.physics.mass.final
        this['physics']['customMoment'] = self.physics.moment.final
        this['physics']['cog'] = [self.physics.cog.final.x, self.physics.cog.final.y]

        this['type'] = self.type
        this['shapes'] = {}
        for shape in self.shapes:
            shape.getJSONDict(this['shapes'])
        parent[self.label] = this

    def recalcPhysics(self):
        pass
