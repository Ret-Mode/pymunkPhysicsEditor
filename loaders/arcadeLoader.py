import arcade
import pymunk
from .pymunkLoader import PymunkLoader

import json
from typing import Dict, List

class ArcadeProxy:
    def __init__(self, sprite, body, pos:pymunk.Vec2d, angle:float):
        self.sprite:arcade.Sprite = sprite
        self.body:pymunk.Body = body
        self.dPos = pos
        self.dAngle = angle

    def update(self):
        self.sprite.radians = self.body.angle + self.dAngle
        self.sprite.position = self.body.position + self.dPos.rotated(self.body.angle)

class SpriteLoader(PymunkLoader):
    def __init__(self, space:pymunk.Space):
        super().__init__(space)
        self.proxy:List[ArcadeProxy] = []

    def loadFile(self, path:str, offsetX:float=0.0, offsetY:float=0.0):
        data = None
        obj = None
        with open(path, 'r') as f:
            data = f.read()
        if data:
            obj = json.loads(data)
            super().loadData(obj, offsetX, offsetY)
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
            self.proxy.append(ArcadeProxy(sprite, body, pymunk.Vec2d(anchor[0], anchor[1]), rot))

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
