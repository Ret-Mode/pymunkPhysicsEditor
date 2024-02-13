import arcade
from pyglet.math import Mat4, Vec2
import random
import pymunk

from loaders.arcadeLoader import SpriteLoader

import sys

class Keys:
    def __init__(self):
        self.k = {arcade.key.W: False,
                  arcade.key.S: False,
                  arcade.key.A: False,
                  arcade.key.D: False,
                  arcade.key.E: False,
                  arcade.key.LSHIFT: False,
                  arcade.key.SPACE: False
                  }

    def setKey(self, key):
        if key in self.k:
            self.k[key] = True

    def unsetKey(self, key):
        if key in self.k:
            self.k[key] = False

    def isPressed(self, key):
        if key in self.k:
            return self.k[key]
        return False

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



class Runner(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.keys = Keys()
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -9.81)
        self.level = SpriteLoader(self.space)
        self.level.loadFile('data/states/level.json')
        self.level.addAll()
        self.vehicle = SpriteLoader(self.space)
        self.vehicle.loadFile('data/states/car1.json')
        self.vehicle.addAll()

        self.camera = Camera()
        self.camera.setWidthInMeters(40.0)
        self.camera.update()

        self.dt = 0.016

    def on_resize(self, width: float, height: float):
        self.camera.resize(width, height)
        return super().on_resize(width, height)
    
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.camera.updateCursor(float(x),float(y))
        return super().on_mouse_motion(x, y, dx, dy)
    
    def on_key_press(self, key, modifiers):
        self.keys.setKey(key)
        print(key)

    def on_key_release(self, key: int, modifiers: int):
        self.keys.unsetKey(key)

    def on_update(self, delta_time: float):
        if 'Wheel' not in self.vehicle.bodies:
            print(self.vehicle.bodies.keys())

            sys.exit(-1)
        wheel = self.vehicle.bodies['Wheel']

        # TODO ###############
        wheel.angular_velocity *= 0.95
        if self.keys.isPressed(arcade.key.W):
            wheel.angular_velocity = max(-30.0, wheel.angular_velocity - 10.5 * self.dt / 0.016)
        if self.keys.isPressed(arcade.key.S):
            wheel.angular_velocity = min(7.0, wheel.angular_velocity + 5 * self.dt / 0.016)
        print(wheel.angular_velocity)
        if self.keys.isPressed(arcade.key.LSHIFT):
            self.dt = max (0.002, self.dt - 0.0003)
        else:
            self.dt = min (0.016, self.dt + 0.0003)
        # ###################
        
        self.space.step(self.dt)
        self.level.update()
        self.vehicle.update()
        #self.ttest.update()
        self.vec = self.vehicle.bodies["BODY"].position
        self.camera.move(self.vec)
        self.camera.update()
        return super().on_update(delta_time)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.level.draw()
        self.vehicle.draw()


Runner(800, 600, "ShaderTest").run()