import array
import arcade
from arcade.gl import BufferDescription
from arcade import ArcadeContext
from pyglet.math import Mat4, Vec2, Vec3
import random

from typing import List
import pymunk
import json

class Camera(arcade.Camera):

    def __init__(self):
        super().__init__()
        self._center:Vec2 = Vec2(self.viewport_width/2.0, self.viewport_height/2.0)

    def move(self, vector: Vec2):
        super().move(vector )

    def move_to(self, vector: Vec2, speed: float = 1):
        super().move_to(vector - self._center, speed)

class Proxy:
    def __init__(self, sprite, body): #, pos:Vec2, angle:float):
        self.sprite:arcade.Sprite = sprite
        self.body:pymunk.Body = body
        #self.dPos = pos
        #self.dAngle = angle

class PymunkLoader:

    def __init__(self, space):
        self.space = space
        self.proxy:List[Proxy] = []
        self.sprites: List = []
        self.bodies = {}
        self.bodiesPhysics = {}
        self.shapes = {}
        self.shapesPhysics = {}
        self.lines = {}
        self.linesPhysics = {}
        self.constraints = {}
        self.physicsParams = {}

    def move(self, x:float, y:float):
        for body in self.bodies.values():
            body.position = (body.position.x + x, body.position.y + y)

    def loadFile(self, path:str):
        data = None
        obj = None
        with open(path, 'r') as f:
            data = f.read()
        if data:
            obj = json.loads(data)
        if obj:
            self.loadBodies(obj['Bodies'])
            self.loadTextures(obj['Textures'], obj['Mappings'])

    def loadTextures(self,textures, mappings):
        for label, texture in textures.items():
            #print(texture)
            pass        
        for label, mapping in mappings.items():
            channel = mapping['textureChannel']
            texturePath = textures[channel]['path']
            textureSize = textures[channel]['size']
            offset = mapping['offset']
            size = mapping['size']
            anchor = mapping['anchor']
            #print(texturePath)
            currentTexture = arcade.load_texture(texturePath, offset[0], textureSize[1] - offset[1] - size[1], size[0], size[1])
            sprite = arcade.Sprite(texture = currentTexture)
            sprite.scale = mapping['subScale']
            body = self.bodies[mapping['body']]
            self.proxy.append(Proxy(sprite, body, ))
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
            proxy.sprite.position = proxy.body.position
            proxy.sprite.angle = proxy.body.angle

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
            print(proxy.body.position.x, proxy.body.position.y)

class Runner(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.space = pymunk.Space()
        self.space.gravity = (10.0, 10.0)
        self.loader = PymunkLoader(self.space)
        self.loader.loadFile('data/states/export.json')
        self.loader.addAll()
        self.sprite = arcade.Sprite('data/textures/wheel2.png')
        self.sprite.position = (300, 300)
        self.camera = Camera()
        self.camera.scale = 1/32.0
        self.camera.update()

    def on_resize(self, width: float, height: float):
        return super().on_resize(width, height)
    
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
        self.loader.debug()
        #self.sprite.draw()
        #arcade.draw_circle_filled(self.sprite.position[0], self.sprite.position[1], 2, (255, 0, 0))


Runner(800, 600, "ShaderTest").run()