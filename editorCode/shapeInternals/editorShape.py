from ..shapeBuffer import ShapeBuffer
from .editorShapeI import ShapeI
from .editorShapeSpec import PolygonSpec, CircleSpec, BoxSpec, RectSpec, LineSpec
from .editorShapePhysics import PolygonPhysics, CirclePhysics, BoxPhysics, RectPhysics, LinePhysics


class Polygon(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.POLYGON
        self.internal:PolygonSpec = PolygonSpec()
        self.physics = PolygonPhysics()
    
    def bufferData(self, buffer:ShapeBuffer):
        buffer.addPolygon(self.internal.points)



class Circle(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.CIRCLE
        self.internal:CircleSpec = CircleSpec()
        self.physics = CirclePhysics()

    def bufferData(self, buffer:ShapeBuffer):
        buffer.addCircle(self.internal.center.final, self.internal.radius.final,
                         self.internal.drawLines)


    # def clone(self, source:"Circle"):
    #     # self.box.clone(source.box)
    #     # self.transform.clone(source.transform)
    #     # self.internal.clone(source.internal)
    #     # self.physics.clone(source.physics)
    #     # self.elasticity = source.elasticity
    #     # self.friction = source.friction
    #     # self.isSensor = source.isSensor
    #     # self.shapeFilterGroup = source.shapeFilterGroup
    #     # self.shapeFilterCategory = source.shapeFilterCategory
    #     # self.shapeFilterMask = source.shapeFilterMask
    #     pass

class Box(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.BOX
        self.internal:BoxSpec = BoxSpec()
        self.physics = BoxPhysics()

    def bufferData(self, buffer:ShapeBuffer):
        buffer.addBox(self.internal.points)


class Rect(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.RECT
        self.internal:RectSpec = RectSpec()
        self.physics = RectPhysics()
        
    def bufferData(self, buffer:ShapeBuffer):
        buffer.addRect(self.internal.points)


class Line(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.LINE
        self.internal = LineSpec()
        self.physics = LinePhysics()

    def bufferData(self, buffer:ShapeBuffer):
        buffer.addLineShape(self.internal.points)
