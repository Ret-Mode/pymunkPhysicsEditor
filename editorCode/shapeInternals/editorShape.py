from .editorShapeI import ShapeI
from .editorShapeSpec import PolygonSpec, CircleSpec, BoxSpec, RectSpec, LineSpec
from .editorShapePhysics import PolygonPhysics, CirclePhysics, BoxPhysics, RectPhysics, LinePhysics


class Polygon(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.POLYGON
        self.internal = PolygonSpec()
        self.physics = PolygonPhysics()


class Circle(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.CIRCLE
        self.internal = CircleSpec()
        self.physics = CirclePhysics()


class Box(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.BOX
        self.internal = BoxSpec()
        self.physics = BoxPhysics()


class Rect(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.RECT
        self.internal = RectSpec()
        self.physics = RectPhysics()
        

class Line(ShapeI):

    def __init__(self, label):
        super().__init__(label)
        self.type :str = ShapeI.LINE
        self.internal = LineSpec()
        self.physics = LinePhysics()
