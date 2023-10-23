import array
import arcade
from arcade.gl import BufferDescription
from arcade import ArcadeContext
from pyglet.math import Mat4, Vec2, Vec3, Vec4
import random

from typing import List, Dict
import pymunk
import json

class Camera(arcade.Camera):

    def __init__(self):
        super().__init__()
        self._center:Vec2 = Vec2(self.viewport_width/2.0, self.viewport_height/2.0)
        self.cursorCoords:Vec2 = Vec2(0,0)
        self.scale = 1.0

    def updateCursor(self, x, y):
        self.cursorCoords = (Vec2(x,y) - self._center).scale(self.scale)

    def setWidthInMeters(self, meters:float):
        self.meters = meters
        self.scale = self.meters / self.viewport_width

    def resize(self, width, height):
        self.scale = 1.0
        super().resize(width, height)
        self.scale = self.meters / width
        self._center:Vec2 = Vec2(width/2.0, height/2.0)

    def move_to(self, vector: Vec2, speed: float = 1):
        super().move_to(vector - self._center, speed)

class ArcadeProxy:
    def __init__(self, sprite, body, pos:Vec2, angle:float):
        self.sprite:arcade.Sprite = sprite
        self.body:pymunk.Body = body
        self.dPos = pos
        self.dAngle = angle

    def update(self):
        self.sprite.radians = self.body.angle + self.dAngle
        self.sprite.position = self.body.position + self.dPos.rotate(self.body.angle)


class PymunkLoader:

    def __init__(self, space:pymunk.Space):
        self.space = space
        self.proxy:List[ArcadeProxy] = []
        self.constraints:Dict[str, pymunk.Constraint] = {}
        self.bodies:Dict[str, pymunk.Body]  = {}
        self.bodiesPhysics = {}
        # 4 dicts below are not needed i guess
        self.shapes:Dict[str, pymunk.Shape] = {}
        self.shapesPhysics = {}
        self.lines:Dict[str, pymunk.Shape] = {}
        self.linesPhysics = {}

    def move(self, x:float, y:float):
        for body in self.bodies.values():
            pos:Vec2 = body.position
            body.position = (pos.x + x, pos.y + y)

    def loadFile(self, path:str):
        data = None
        obj = None
        with open(path, 'r') as f:
            data = f.read()
        if data:
            obj = json.loads(data)
        if obj:
            self.loadBodies(obj['Bodies'])
            self.loadSprites(obj['Textures'], obj['Mappings'])

    def loadSprites(self,textures, mappings):     
        for label, mapping in mappings.items():
            channel = mapping['textureChannel']
            texturePath = textures[channel]['path']
            textureSize = textures[channel]['size']
            offset = mapping['offset']
            size = mapping['size']
            currentTexture = arcade.load_texture(texturePath, offset[0], textureSize[1] - offset[1] - size[1], size[0], size[1])
            sprite = arcade.Sprite(texture = currentTexture)
            sprite.scale = mapping['subScale']
            body = self.bodies[mapping['body']]
            rot = mapping['subRotate']
            anchor = mapping['subAnchor']
            self.proxy.append(ArcadeProxy(sprite, body, Vec2(anchor[0], anchor[1]), rot))
            #print(mapping)

    def loadBodies(self, data):
        for label, body in data.items():
            self.loadBody(body, label)

    def loadBody(self, data, label):
        typ = data['type']
        if typ == 'Dynamic':
            self.bodies[label] = pymunk.Body(pymunk.Body.DYNAMIC)
        elif typ == 'Kinematic':
            self.bodies[label] = pymunk.Body(pymunk.Body.KINEMATIC)
        else:
            self.bodies[label] = pymunk.Body(pymunk.Body.STATIC)

        physics = data['physics']
        shapes = data['shapes']

        for sLabel, shape in shapes.items():
            self.loadShape(shape, sLabel, self.bodies[label])

        self.bodiesPhysics[label] = physics

    def loadShape(self, shape:dict, label:str, body:pymunk.Body):
        type = shape['type']
        if type in ('Polygon', "Box", "Rect"):
            points = []
            for point in shape['internal']['points']:
                points.append((point[0], point[1]))
            self.shapes[label] = pymunk.Poly(body=body, vertices=points, radius=shape['internal']['radius'])
            #s = self.loadPolygon(shape['internal'], shape['physics'])
            #s.body = body
        elif type == 'Circle':
            placement = shape['internal']['offset']
            self.shapes[label] = pymunk.Circle(body=body, radius=shape['internal']['radius'], offset=placement)
            # s = self.loadCircle(shape['internal'], shape['physics'])
            # s.body = body
        elif type == 'Line':
            #ss = self.loadLine(shape['internal'], shape['physics'])
            self.lines[label] = []
            for point in shape['internal']['points']:
                p1 = (point[0], point[1])
                p2 = (point[2], point[3])
                s = pymunk.Segment(body=body, a=p1, b=p2, radius=shape['internal']['radius'])
                self.lines[label].append(s)
        self.shapesPhysics[label] = shape['physics']

    def loadBodyPhysics(self, body: pymunk.Body, physics:dict):
        if physics['hasCustomMass']:
            body.mass = physics['customMass']
        if physics['hasCustomCog']:
            body.center_of_gravity = physics['cog'][0], physics['cog'][1]
            body.moment = physics['customMoment']
        elif physics['hasCustomMoment']:
            body.moment = physics['customMoment']

    def loadShapePhysics(self, shape: pymunk.Shape, physics:dict):
        shape.density = physics['customDensity']
        if physics['hasCustomMass']:
            shape.mass = physics['customMass']

    def update(self):
        for proxy in self.proxy:
            proxy.body.angle += 0.01
            proxy.update()

    def addAll(self):
        for l, b in self.bodies.items():
            self.loadBodyPhysics(b, self.bodiesPhysics[l])
            self.space.add(b)
        for l, s in self.shapes.items():
            self.space.add(s)
            self.loadShapePhysics(s, self.shapesPhysics[l])
        for ls in self.lines.values():
            for l in ls:
                self.space.add(l)
        for l, b in self.bodies.items():
            self.loadBodyPhysics(b, self.bodiesPhysics[l])

    def draw(self):
        for proxy in self.proxy:
            proxy.sprite.draw()
    
    def debug(self):
        for proxy in self.proxy:
            print(proxy.body.position.x, proxy.body.position.y, proxy.body.angle)


class Runner(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 0.0)
        self.loader = PymunkLoader(self.space)
        self.loader.loadFile('data/states/export.json')
        self.loader.addAll()
        self.camera = Camera()
        self.camera.setWidthInMeters(40.0)
        self.camera.update()

    def on_resize(self, width: float, height: float):
        self.camera.resize(width, height)
        return super().on_resize(width, height)
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.camera.updateCursor(float(x),float(y))
        return super().on_mouse_motion(x, y, dx, dy)
    
    def on_update(self, delta_time: float):
        self.space.step(0.016)
        self.loader.update()
        self.vec = self.loader.bodies['BODY'].position
        self.camera.move(self.vec)
        self.camera.update()
        return super().on_update(delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.loader.draw()
        arcade.draw_point(self.camera.cursorCoords.x, self.camera.cursorCoords.y, (255,0,0), 0.1)
        #arcade.draw_circle_outline(self.camera.cursorCoords.x, self.camera.cursorCoords.y, 1.0, (255,0,0), border_width=0.1, num_segments=16)
        self.loader.debug()
        print(self.camera.cursorCoords.x, self.camera.cursorCoords.y)


Runner(800, 600, "ShaderTest").run()