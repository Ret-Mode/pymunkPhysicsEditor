import array
import arcade
from arcade.gl import BufferDescription
from arcade import ArcadeContext
import pyglet.gl
import random

from typing import List
import pymunk
import json

class Proxy:
    def __init__(self):
        self.sprite:arcade.Sprite
        self.physicsBody:pymunk.Body

class PymunkLoader:

    def __init__(self, space):
        self.space = space
        self.proxy:List[Proxy] = []
        self.sprites: List = []
        self.bodies = {}
        self.shapes = {}
        self.lines = {}
        self.constraints = {}


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
            offset = mapping['offset']
            size = mapping['size']
            anchor = mapping['anchor']
            print(texturePath)
            currentTexture = arcade.load_texture(texturePath, offset[0], offset[1], size[0], size[1])
            self.sprites.append(arcade.Sprite(texture = currentTexture))
            #print(mapping)

    def loadBodies(self, data):
        for label, body in data.items():
            self.loadBody(body, label)

    def loadBody(self, data, label):
        typ = data['type']
        if typ == 'DYNAMIC':
            self.bodies[label] = pymunk.Body(pymunk.Body.DYNAMIC)
        elif typ == 'KINEMATIC':
            self.bodies[label] = pymunk.Body(pymunk.Body.KINEMATIC)
        else:
            self.bodies[label] = pymunk.Body(pymunk.Body.STATIC)

        physics = data['physics']
        shapes = data['shapes']

        for sLabel, shape in shapes.items():
            self.loadShape(shape, sLabel, self.bodies[label])

        self.loadBodyPhysics(self.bodies[label], physics)

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

    def loadShape(self, shape:dict, label:str, body:pymunk.Body):
        type = shape['type']
        if type in ('POLYGON', "BOX", "RECT"):
            points = []
            for point in shape['internal']['points']:
                points.append((point[0], point[1]))
            self.shapes[label] = pymunk.Poly(body=body, vertices=points, radius=shape['internal']['radius'])
            self.loadShapePhysics(self.shapes[label], shape['physics'])
            #s = self.loadPolygon(shape['internal'], shape['physics'])
            #s.body = body
        elif type == 'CIRCLE':
            placement = shape['internal']['offset']
            self.shapes[label] = pymunk.Circle(body=body, radius=shape['internal']['radius'], offset=placement)
            self.loadShapePhysics(self.shapes[label], shape['physics'])
            # s = self.loadCircle(shape['internal'], shape['physics'])
            # s.body = body
        elif type == 'LINE':
            #ss = self.loadLine(shape['internal'], shape['physics'])
            self.lines[label] = []
            for point in shape['internal']['points']:
                p1 = (point[0], point[1])
                p2 = (point[2], point[3])
                shape = pymunk.Segment(body=body, a=p1, b=p2, radius=shape['internal']['radius'])
                self.loadShapePhysics(shape, shape['physics'])
                self.lines[label].append(shape)
            # for s in ss:
            #     s.body = body

    def step(self):
        pass

    def addAll(self):
        for s in self.shapes.values():
            print("PRE", s.mass)
            print("PRE", s.moment)
            self.space.add(s)
            print("POST", s.mass)
            print("POST", s.moment)
        for ls in self.lines.values():
            for l in ls:
                self.space.add(l)
        for b in self.bodies.values():
            print("PRE", b.mass)
            print("PRE", b.moment)
            self.space.add(b)
            print("POST", b.mass)
            print("POST", b.moment)

    def draw(self):
        for sprite in self.sprites:
            sprite.draw()
        

class Runner(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.space = pymunk.Space()
        self.space.gravity = (-10.0, 0.0)
        self.loader = PymunkLoader(self.space)
        self.loader.loadFile('data/states/export.json')
        self.loader.addAll()
        

    def on_resize(self, width: float, height: float):
        return super().on_resize(width, height)
    
    def on_update(self, delta_time: float):
        self.space.step(0.016)
        return super().on_update(delta_time)

    def on_draw(self):
        self.clear()
        self.loader.draw()


Runner(800, 600, "ShaderTest").run()