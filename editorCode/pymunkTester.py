import pymunk
from typing import List, Tuple

from .shapeInternals.editorShapeI import ShapeI
from .config import fromJSON

def readPolygon(internal:dict, physics:dict):
    points = []
    for point in internal['points']:
        points.append((point[0], point[1]))
    shape = pymunk.Poly(body=None, vertices=points, radius=internal['radius'])
    readShapePhysics(shape, physics)
    return shape

def readCircle(internal:dict, physics:dict):
    placement = internal['offset']
    shape = pymunk.Circle(body=None, radius=internal['radius'], offset=placement)
    readShapePhysics(shape, physics)
    return shape

def readLine(internal:dict, physics:dict):
    shapes = []
    for point in internal['points']:
        p1 = (point[0], point[1])
        p2 = (point[2], point[3])
        shape = pymunk.Segment(body = None, a=p1, b=p2, radius=internal['radius'])
        readShapePhysics(shape, physics)
        shapes.append(shape)
    return shapes

def readShapePhysics(shape: pymunk.Shape, physics:dict):
    shape.density = physics['customDensity']
    if physics['hasCustomMass']:
        shape.mass = physics['customMass']

def readShape(shape:dict, space: pymunk.Space, body:pymunk.Body):
    type = shape.pop('type')
    if type in ('POLYGON', "BOX", "RECT"):
        s = readPolygon(shape['internal'], shape['physics'])
        s.body = body
        space.add(s)
    elif type == 'CIRCLE':
        s = readCircle(shape['internal'], shape['physics'])
        s.body = body
        space.add(s)
    elif type == 'LINE':
        ss = readLine(shape['internal'], shape['physics'])
        for s in ss:
            s.body = body
            space.add(s)

def readBodyPhysics(body: pymunk.Body, physics:dict):
    if physics['hasCustomMass']:
        body.mass = physics['customMass']
    if physics['hasCustomCog']:
        body.center_of_gravity = physics['cog'][0], physics['cog'][1]
        body.moment = physics['customMoment']
    elif physics['hasCustomMoment']:
        body.moment = physics['customMoment']

def readBody(data:dict, space):
    type = data.pop('type')
    if type == 'DYNAMIC':
        body = pymunk.Body(pymunk.Body.DYNAMIC)
    elif type == 'KINEMATIC':
        body = pymunk.Body(pymunk.Body.KINEMATIC)
    else:
        body = pymunk.Body(pymunk.Body.STATIC)

    space.add(body)

    physics = data.pop('physics')
    shapes = data.pop('shapes')

    for shape in shapes:
        readShape(shapes[shape], space, body)

    readBodyPhysics(body, physics)

    print("BODY MASS ", body.mass, "\tBODY MOMENT ", body.moment)
    print("BODY COG ", body.center_of_gravity, "\tBODY POS ", body.position)

def readEntity(data:dict):
    space = pymunk.Space()

    for body in data:
        readBody(data[body], space)

    clearSpace(space)

def clearSpace(space: pymunk.Space):
    constraints = space.constraints
    for c in constraints:
        space.remove(c)
        del c

    bodies = space.bodies
    for b in bodies:
        space.remove(b)
        del b

    shapes = space.shapes
    for s in shapes:
        space.remove(s)
        del s

    del space

def testShapes(jsonString: str):

    data = fromJSON(jsonString)
    assert data
    config = data.pop('config')
    assert config
    
 
    for shape in data:
        space = pymunk.Space()
        body = pymunk.Body(pymunk.Body.DYNAMIC)
        space.add(body)
        readShape(data[shape], space, body)

        print("BODY MASS ", body.mass, "\tBODY MOMENT ", body.moment)
        print("BODY COG ", body.center_of_gravity, "\tBODY POS ", body.position)

        clearSpace(space)

    del config
    del data

def testBodies(jsonString: str):

    data = fromJSON(jsonString)
    assert data
    config = data.pop('config')
    assert config
    readEntity(data)
    del config
    del data