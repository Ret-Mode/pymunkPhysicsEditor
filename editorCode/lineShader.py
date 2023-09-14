import array
from arcade.gl import BufferDescription
from arcade import ArcadeContext
import pyglet.gl

from typing import List


class LineDraw:

    _instance: "LineDraw" = None

    @staticmethod
    def getInstance() -> "LineDraw":
        if LineDraw._instance == None:
            LineDraw._instance = LineDraw()
        return LineDraw._instance

    def __init__(self, ctx:ArcadeContext):
        vertexShader="""
            #version 330

            in vec2 inVert;
            in vec4 inColor;

            out vec4 fColor;

            void main() {
                fColor = inColor;
                gl_Position = vec4(inVert.xy, 0.0, 1.0);
            }
            """

        fragmentShader="""
            #version 330

            in vec4 fColor;

            void main() {
                gl_FragColor = vec4(fColor.rgb, 1.0);
            }
            """
        self.program = ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)

        verts = array.array('f', [
                        -0.5, -0.5,
                        0.5, -0.5,
                        0.5, 0.5,
                        -0.5,  0.5,
        ])
        
        self.verts = ctx.buffer(data=verts)
        vertsDescription = BufferDescription(self.verts, '2f', ['inVert'] )

        colors = array.array('B', [255, 0, 0, 255, 
                                   0, 255, 0, 255,
                                   0, 0, 255, 255,
                                   255, 255, 255, 255])
        self.colors = ctx.buffer(data=colors)
        colorsDescription = BufferDescription(self.colors, '4f1', ['inColor'], normalized=['inColor'])

        indices = array.array('I', [0,1,2,1])
        self.indices = ctx.buffer(data=indices)

        self.geometry = ctx.geometry([vertsDescription, colorsDescription], 
                                     index_buffer=self.indices, 
                                     mode=ctx.LINES)
        ctx.enable(pyglet.gl.GL_LINE_SMOOTH)
        ctx.disable(pyglet.gl.GL_DEPTH_TEST)

    def update(self, verts:List[float], colors:List[int], indices:List[int]):
        vertsInBytes = len(verts) * 4
        colorsInBytes = len(colors)
        indicesInBytes = len(indices) * 4

        if vertsInBytes > self.verts.size:
            self.verts.orphan(size=vertsInBytes)
        self.verts.write(array.array('f', verts))
        
        if colorsInBytes > self.colors.size:
            self.colors.orphan(size=colorsInBytes)
        self.colors.write(array.array('B', colors))
        
        if indicesInBytes > self.indices.size:
            self.indices.orphan(size=indicesInBytes)
        self.indices.write(array.array('I', indices))

    def draw(self):
        self.geometry.render(self.program)


