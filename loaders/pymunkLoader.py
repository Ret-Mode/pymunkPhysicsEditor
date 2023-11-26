import pymunk


from typing import Dict, List
import json
import math

class PymunkLoader:

    def __init__(self, space:pymunk.Space):
        self.space = space
        self.constraints:Dict[str, pymunk.Constraint] = {}
        self.bodies:Dict[str, pymunk.Body]  = {}
        self.bodiesPhysics = {}
        # 4 dicts below are not needed i guess
        self.shapes:Dict[str, pymunk.Shape] = {}
        self.lines:Dict[str, List[pymunk.Shape]] = {}

    def move(self, x:float, y:float):
        for body in self.bodies.values():
            pos:pymunk.Vec2d = body.position
            body.position = (pos.x + x, pos.y + y)

    def loadFile(self, path:str):
        data = None
        obj = None
        with open(path, 'r') as f:
            data = f.read()
        if data:
            obj = json.loads(data)
            self.loadData(obj)

    def loadData(self, obj:Dict, offsetX:float=0.0, offsetY:float=0.0):
        self.loadBodies(obj['Bodies'], offsetX, offsetY)
        self.loadConstraints(obj['Constraints'])

    def loadBodies(self, data:Dict, offsetX:float=0.0, offsetY:float=0.0):
        for label, body in data.items():
            self.loadBody(body, label, offsetX, offsetY)

    def loadBody(self, data:Dict, label:str, offsetX:float=0.0, offsetY:float=0.0):
        typ:str = data['type']
        if typ == 'Dynamic':
            body = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
        elif typ == 'Kinematic':
            body = pymunk.Body(body_type = pymunk.Body.KINEMATIC)
        else:
            body = pymunk.Body(body_type = pymunk.Body.STATIC)

        if not body:
            return
        body.position = (offsetX, offsetY)
        self.bodies[label] = body

        physics:Dict = data['physics']
        shapes:Dict = data['shapes']

        for sLabel, shape in shapes.items():
            self.loadShape(shape, sLabel, self.bodies[label])

        self.bodiesPhysics[label] = physics

    def loadShape(self, shape:Dict, label:str, body:pymunk.Body):
        type = shape['type']
        physics = shape['physics']
        if type in ('Polygon', "Box", "Rect"):
            points = []
            for point in shape['internal']['points']:
                points.append((point[0], point[1]))
            s = pymunk.Poly(body=body, vertices=points, radius=shape['internal']['radius'])
            s.friction = 1.0
            self.shapes[label] = s
            if physics['hasCustomMass']:
                s.mass = physics['customMass']
            else:
                s.density = physics['customDensity']
        elif type == 'Circle':
            placement = shape['internal']['offset']
            s = pymunk.Circle(body=body, radius=shape['internal']['radius'], offset=placement)
            s.friction = 1.0
            self.shapes[label] = s
            if physics['hasCustomMass']:
                s.mass = physics['customMass']
            else:
                s.density = physics['customDensity']
        elif type == 'Line':
            self.lines[label] = []
            for point in shape['internal']['points']:
                p1 = (point[0], point[1])
                p2 = (point[2], point[3])
                s = pymunk.Segment(body=body, a=p1, b=p2, radius=shape['internal']['radius'])
                s.friction = 1.0
                if physics['hasCustomMass']:
                    length = math.sqrt((point[0] - point[2]) ** 2 + (point[1] - point[3]) ** 2)
                    s.mass = length / physics['customMass']
                else:
                    s.density = physics['customDensity']
                self.lines[label].append(s)

    def loadBodyPhysics(self, body: pymunk.Body, physics:dict):
        if physics['hasCustomMass']:
            body.mass = physics['customMass']
        if physics['hasCustomCog']:
            body.center_of_gravity = physics['cog'][0], physics['cog'][1]
            body.moment = physics['customMoment']
        elif physics['hasCustomMoment']:
            body.moment = physics['customMoment']

    def loadConstraints(self, data:Dict):
        for label in data:
            self.loadConstraint(data[label], label)

    def loadConstraint(self, constraint:Dict, label:str):
        type = constraint['type']
        if type == "Rotary Spring":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            restAngle = constraint['restAngle']
            stiffness = constraint['stiffness']
            damping = constraint['damping']
            constraint = pymunk.constraints.DampedRotarySpring(bodyA, bodyB, restAngle, stiffness, damping)
            constraint.collide_bodies = False
        elif type == "Damped Spring":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            anchorA = tuple(constraint['anchorA'])
            anchorB = tuple(constraint['anchorB'])
            restLength = constraint['restLength']
            stiffness = constraint['stiffness']
            damping = constraint['damping']
            constraint = pymunk.constraints.DampedSpring(bodyA, bodyB, anchorA, anchorB, restLength, stiffness, damping)
            constraint.collide_bodies = False
        elif type == "Gear":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            phase = constraint['phase']
            ratio = constraint['ratio']
            constraint = pymunk.constraints.GearJoint(bodyA, bodyB, phase, ratio)
            constraint.collide_bodies = False
        elif type == "Groove":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            grooveA = tuple(constraint['grooveA'])
            grooveB = tuple(constraint['grooveB'])
            anchorB = tuple(constraint['anchorB'])
            constraint = pymunk.constraints.GrooveJoint(bodyA, bodyB, grooveA, grooveB, anchorB)
            constraint.collide_bodies = False
        elif type == "Pin":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            anchorA = tuple(constraint['anchorA'])
            anchorB = tuple(constraint['anchorB'])
            constraint = pymunk.constraints.PinJoint(bodyA, bodyB, anchorA, anchorB)
            constraint.collide_bodies = False
        elif type == "Pivot":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            anchorA = tuple(constraint['anchorA'])
            anchorB = tuple(constraint['anchorB'])
            constraint = pymunk.constraints.PivotJoint(bodyA, bodyB, anchorA, anchorB)
            constraint.collide_bodies = False
        elif type == "Ratchet":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            phase = constraint['phase']
            ratchet = constraint['ratchet']
            constraint = pymunk.constraints.RatchetJoint(bodyA, bodyB, phase, ratchet)
            constraint.collide_bodies = False
        elif type == "Rotary Limit":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            fMin = constraint['min']
            fMax = constraint['max']
            constraint = pymunk.constraints.RotaryLimitJoint(bodyA, bodyB, fMin, fMax)
            constraint.collide_bodies = False
        elif type == "Motor":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            rate = constraint['rate']
            constraint = pymunk.constraints.SimpleMotor(bodyA, bodyB, rate)
            constraint.collide_bodies = False
        elif type == "Slide":
            bodyA = self.bodies[constraint['bodyA']]
            bodyB = self.bodies[constraint['bodyB']]
            anchorA = tuple(constraint['anchorA'])
            anchorB = tuple(constraint['anchorB'])
            fMin = constraint['min']
            fMax = constraint['max']
            constraint = pymunk.constraints.SlideJoint(bodyA, bodyB, anchorA, anchorB, fMin, fMax)
            constraint.collide_bodies = False
        else:
             return
        self.constraints[label] = constraint

    def addAll(self):
        for l, b in self.bodies.items():
            self.space.add(b)
            for shape in b.shapes:
                self.space.add(shape)
            self.loadBodyPhysics(b, self.bodiesPhysics[l])
        for c in self.constraints.values():
            self.space.add(c)
        