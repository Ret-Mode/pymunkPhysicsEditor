from .editorShapeI import ShapeI
from .editorShape import Polygon, Circle, Box, Rect, Line


def shapeFactory(label: str, typeID: str) -> ShapeI:
    if typeID == ShapeI.POLYGON:
        return Polygon(label)
    elif typeID == ShapeI.CIRCLE:
        return  Circle(label)
    elif typeID == ShapeI.BOX:
        return  Box(label)
    elif typeID == ShapeI.RECT:
        return  Rect(label)
    elif typeID == ShapeI.LINE:
        return  Line(label)
    else:
        assert False