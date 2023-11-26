import arcade
from arcade.gl import Texture

import pymunk
from .pymunkLoader import PymunkLoader

import json
from typing import Dict, List


class GLProxy:
    def __init__(self, arrayIndex:int, body, pos:pymunk.Vec2d, angle:float):
        self.arrayIndex = arrayIndex
        self.body:pymunk.Body = body
        self.dPos = pos
        self.dAngle = angle

    def update(self):
        radians = self.body.angle + self.dAngle
        position = self.body.position + self.dPos.rotated(self.body.angle)


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
            self.proxy.append(GLProxy(0, body, pymunk.Vec2d(anchor[0], anchor[1]), rot))

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