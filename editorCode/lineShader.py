import array
from arcade.gl import BufferDescription
from arcade import ArcadeContext
import pyglet.gl

from typing import List


class LineShader:

    def __init__(self, ctx:ArcadeContext,):
        vertexShader = """
            #version 330
            in vec2 in_vert;
            in vec3 in_color;
            out vec3 out_color;

            void main() {
                out_color = in_color;
                gl_Position = vec4(in_vert.x, in_vert.y, 0.0, 1.0);
            }
            """
        fragmentShader = """
            #version 330

            in vec3 out_color;
            out vec4 final_color;

            void main() {
                final_color = vec4(out_color.r, out_color.g, out_color.b, 1.0);
            }
            """
        self.program = ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)
        self.data = array.array('f', [ 0.0, 0.0, 0.0, 0.0, 0.0 ])
        self.buffer = ctx.buffer(data=self.data)
        self.bufferDescription = BufferDescription(self.buffer, '2f 3f', ['in_vert', 'in_color'] )
        self.geometry = ctx.geometry([self.bufferDescription], mode=ctx.LINES)
        self.smoothLineFlag = pyglet.gl.GL_LINE_SMOOTH
        self.enable = ctx.enable

    def draw(self):
        self.enable(self.smoothLineFlag)
        self.buffer.write(self.data)
        self.geometry.render(self.program)

    def updateBuffer(self, data: List[float]):
        dataLengthInBytes = len(self.data) * 4
        if dataLengthInBytes != self.buffer.size:
            self.buffer.orphan(size=dataLengthInBytes)
        self.buffer.write(array.array('f', data))
