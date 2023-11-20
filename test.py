import array
import arcade
from arcade.gl import BufferDescription, Texture
from arcade import ArcadeContext
from pyglet.math import Mat4, Vec2, Vec3, Vec4
import random

from typing import List, Dict
import pymunk
import json
import math


class Camera(arcade.Camera):

    def __init__(self):
        super().__init__()
        self.cursorCoords:Vec2 = Vec2(0,0)
        self.scale = 1.0

    def updateCursor(self, x, y):
        self.cursorCoords.x = (x - self.viewport_width/2.0) * self.scale + self.position.x
        self.cursorCoords.y = (y - self.viewport_height/2.0) * self.scale + self.position.y

    def setWidthInMeters(self, meters:float):
        self.meters = meters
        self.scale = self.meters / self.viewport_width

    def resize(self, width, height):
        self.scale = 1.0
        super().resize(width, height)
        self.scale = self.meters / width

    def set_projection(self):
        self.projection_matrix = Mat4.orthogonal_projection(
            -self.scale * self.viewport_width / 2.0,
            self.scale * self.viewport_width / 2.0,
            -self.scale * self.viewport_height / 2.0,
            self.scale * self.viewport_height / 2.0,
            self.near,
            self.far
        )


class ArcadeProxy:
    def __init__(self, sprite, body, pos:Vec2, angle:float):
        self.sprite:arcade.Sprite = sprite
        self.body:pymunk.Body = body
        self.dPos = pos
        self.dAngle = angle

    def update(self):
        self.sprite.radians = self.body.angle + self.dAngle
        self.sprite.position = self.body.position + self.dPos.rotate(self.body.angle)


class GLProxy:
    def __init__(self, arrayIndex:int, body, pos:Vec2, angle:float):
        self.arrayIndex = arrayIndex
        self.body:pymunk.Body = body
        self.dPos = pos
        self.dAngle = angle

    def update(self):
        self.sprite.radians = self.body.angle + self.dAngle
        self.sprite.position = self.body.position + self.dPos.rotate(self.body.angle)


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
            pos:Vec2 = body.position
            body.position = (pos.x + x, pos.y + y)

    def loadFile(self, path:str):
        data = None
        obj = None
        with open(path, 'r') as f:
            data = f.read()
        if data:
            obj = json.loads(data)
            self.loadData(obj)

    def loadData(self, obj:Dict):
        self.loadBodies(obj['Bodies'])

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
        physics = shape['physics']
        if type in ('Polygon', "Box", "Rect"):
            points = []
            for point in shape['internal']['points']:
                points.append((point[0], point[1]))
            s = pymunk.Poly(body=body, vertices=points, radius=shape['internal']['radius'])
            self.shapes[label] = s
            if physics['hasCustomMass']:
                s.mass = physics['customMass']
            else:
                s.density = physics['customDensity']
        elif type == 'Circle':
            placement = shape['internal']['offset']
            s = pymunk.Circle(body=body, radius=shape['internal']['radius'], offset=placement)
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

    def addAll(self):
        for l, b in self.bodies.items():
            self.space.add(b)
            for shape in b.shapes:
                self.space.add(shape)
            self.loadBodyPhysics(b, self.bodiesPhysics[l])


class SpriteLoader(PymunkLoader):
    def __init__(self, space:pymunk.Space):
        super().__init__(space)
        self.proxy:List[ArcadeProxy] = []

    def loadFile(self, path:str):
        data = None
        obj = None
        with open(path, 'r') as f:
            data = f.read()
        if data:
            obj = json.loads(data)
            super().loadData(obj)
            self.loadData(obj)

    def loadData(self, obj:Dict):
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

    def update(self):
        for proxy in self.proxy:
            #proxy.body.angle += 0.01
            proxy.update()

    def draw(self):
        for proxy in self.proxy:
            proxy.sprite.draw()
    
    def debug(self):
        for proxy in self.proxy:
            print(proxy.body.position.x, proxy.body.position.y, proxy.body.angle)


class GLLoader(PymunkLoader):
    def __init__(self, space:pymunk.Space):
        super().__init__(space)
        self.proxy:List[GLProxy] = []
        self.textures : Dict[str, Texture] = {}

    def loadFile(self, path:str):
        data = None
        obj = None
        with open(path, 'r') as f:
            data = f.read()
        if data:
            obj = json.loads(data)
            super().loadData(obj)
            self.loadData(obj)

    def loadData(self, obj:Dict):
        self.loadGL(obj['Textures'], obj['Mappings'])

    # TODO
    def loadGL(self,textures, mappings):     
        for channel, path in textures.items():
            self.textures[channel] = arcade.get_window().ctx.load_texture(path)

        for label, mapping in mappings.items():
            channel = mapping['textureChannel']
            texturePath = textures[channel]['path']
            textureSize = textures[channel]['size']
            offset = mapping['offset']
            size = mapping['size']
            scale = mapping['subScale']
            body = self.bodies[mapping['body']]
            rot = mapping['subRotate']
            anchor = mapping['subAnchor']
            self.proxy.append(GLProxy(0, body, Vec2(anchor[0], anchor[1]), rot))

    def update(self):
        for proxy in self.proxy:
            proxy.body.angle += 0.01
            proxy.update()

    def draw(self):
        for proxy in self.proxy:
            pass
    
    def debug(self):
        for proxy in self.proxy:
            print(proxy.body.position.x, proxy.body.position.y, proxy.body.angle)


class Runner(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.space = pymunk.Space()
        self.space.gravity = (0.0, 0.0)
        self.loader = SpriteLoader(self.space)
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
        vec = self.loader.bodies['BODY'].position
        arcade.draw_circle_outline(self.camera.cursorCoords.x, self.camera.cursorCoords.y, 1.0, (255,0,0), border_width=0.1, num_segments=16)
        #self.loader.debug()



Runner(800, 600, "ShaderTest").run()