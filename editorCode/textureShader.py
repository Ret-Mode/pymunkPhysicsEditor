
import arcade
from arcade.gl import BufferDescription
from pyglet.math import Mat4

import array
from typing import List, Tuple

class TextureDraw:

    def __init__(self):
        self.ctx = arcade.get_window().ctx
        vertexShader="""
            #version 330

            uniform Projection {
                uniform mat4 matrix;
            } proj;

            in vec2 inVert;
            in vec2 inUV;

            out vec2 fUV;

            void main() {
                fUV = inUV;
                gl_Position = proj.matrix * vec4(inVert.xy, 0.0, 1.0);
            }
            """

        fragmentShader="""
            #version 330

            in vec2 fUV;

            uniform sampler2D currentTexture;

            void main() {
                gl_FragColor = texture(currentTexture, fUV);
            }
            """
        self.program = self.ctx.program(vertex_shader=vertexShader, fragment_shader=fragmentShader)

        verts = array.array('f', [
                        0, 0,
                        32.0, 0.0,
                        0.0, 32.0,
                        32.0, 32.0,

        ])
        
        self.verts = self.ctx.buffer(data=verts)
        vertsDescription = BufferDescription(self.verts, '2f', ['inVert'] )

        uvs = array.array('f', [0.0, 0.0,
                                   1.0, 0.0,
                                   0.0, 1.0,
                                   1.0, 1.0])
        self.uvs = self.ctx.buffer(data=uvs)
        uvDescription = BufferDescription(self.uvs, '2f', ['inUV'])

        indices = array.array('I', [0,1,2,1,2,3])
        self.indices = self.ctx.buffer(data=indices)

        self.program.set_uniform_safe('currentTexture', 0)

        self.geometry = self.ctx.geometry([vertsDescription, uvDescription], 
                                     index_buffer=self.indices, 
                                     mode=self.ctx.TRIANGLES)
        #self.ctx.disable(pyglet.gl.GL_DEPTH_TEST)

    def updateIndices(self, indices:List[int]):
        indicesInBytes = len(indices) * 4
        if indicesInBytes != self.indices.size:
            self.indices.orphan(size=indicesInBytes)
        self.indices.write(array.array('I', indices))
        self.geometry.num_vertices = len(indices)

    def updateVerts(self, verts:List[float]):
        vertsInBytes = len(verts) * 4
        if vertsInBytes > self.verts.size:
            self.verts.orphan(size=vertsInBytes)
        self.verts.write(array.array('f', verts))

    def updateUVs(self, uvs:List[float]):
        uvsInBytes = len(uvs) * 4
        if uvsInBytes > self.uvs.size:
            self.uvs.orphan(size=uvsInBytes)
        self.uvs.write(array.array('f', uvs))

    def update(self, verts:List[float], uvs:List[float], indices:List[int]):
        vertsInBytes = len(verts) * 4
        uvsInBytes = len(uvs) * 4
        indicesInBytes = len(indices) * 4

        if vertsInBytes > self.verts.size:
            self.verts.orphan(size=vertsInBytes)
        self.verts.write(array.array('f', verts))
        
        if uvsInBytes > self.uvs.size:
            self.uvs.orphan(size=uvsInBytes)
        self.uvs.write(array.array('f', uvs))
        
        if indicesInBytes != self.indices.size:
            self.indices.orphan(size=indicesInBytes)
            self.geometry.num_vertices = len(indices)
        self.indices.write(array.array('I', indices))

    def setProjection(self, viewport: Tuple[float], mat: Tuple[float]):
        self.ctx.viewport = viewport
        self.ctx.projection_2d_matrix = Mat4(values=mat)

    def draw(self):
        self.geometry.render(self.program)