import arcade
from arcade.gl import BufferDescription
from pyglet.math import Mat4

import array
from typing import List, Tuple

class GridDraw:
    
    def __init__(self):
        self.ctx = arcade.get_window().ctx
        vertexShader="""
            #version 330

            in vec2 inVert;

            uniform WindowBlock
            {
                mat4 projection;
                mat4 view;
            } window;  

            uniform ABC {
                vec4 color;
                vec2 delta;
            } abc;

            void main() {
                gl_Position = window.projection * vec4(inVert.xy, 0.0, 1.0);
            }
            """

        geometryShader="""
            #version 330 core
            layout (points) in;
            layout (line_strip, max_vertices = 256) out;


            uniform ABC {
                vec4 color;
                vec2 delta;
            } abc;

            void main() {
                int dx;
                int dy;
                float fX = gl_in[0].gl_Position.x;
                float fY = gl_in[0].gl_Position.y;
                for (dx = 0; dx < 8; ++dx)
                {
                    for (dy = 0; dy < 8; ++dy)
                    {
                        
                        float x = fX + dx * abc.delta.x;
                        float y = fY + dy * abc.delta.y;

                        gl_Position = vec4(x-0.01, y, 0.0, 1.0); 
                        EmitVertex();

                        gl_Position = vec4(x+0.01, y, 0.0, 1.0); 
                        EmitVertex();
                        
                        EndPrimitive();

                        gl_Position = vec4(x, y-0.01, 0.0, 1.0); 
                        EmitVertex();

                        gl_Position = vec4(x, y+0.01, 0.0, 1.0); 
                        EmitVertex();
                        
                        EndPrimitive();
                    }
                }
            } 
            """

        fragmentShader="""
            #version 330

            uniform ABC {
                vec4 color;
                vec2 delta;
            } abc;

            out vec4 fColor;

            void main() {
                fColor = vec4(abc.color.rgb, 1.0);
            }
            """
        self.program = self.ctx.program(vertex_shader=vertexShader, geometry_shader=geometryShader, fragment_shader=fragmentShader)

        verts = array.array('f', [
                        -1.0, -1.0, -0.89, -0.89
        ])
        
        self.verts = self.ctx.buffer(data=verts)
        vertsDescription = BufferDescription(self.verts, '2f', ['inVert'] )

        indices = array.array('I', [0,0])
        self.indices = self.ctx.buffer(data=indices)

        uniform = array.array('f', [
                        1.0, 0.5, 1.0, 1.0, 0.1, 0.1, 0.0, 0.0])
        self.uniform = self.ctx.buffer(data=uniform)
        
        self.uniform.bind_to_uniform_block(1)

        self.program.set_uniform_safe('ABC', 1)
        # keep Window Block uniform
        self.program.set_uniform_safe('WindowBlock', 0)

        self.geometry = self.ctx.geometry([vertsDescription],
                                     mode=self.ctx.POINTS, 
                                     index_buffer=self.indices)
        #ctx.disable(pyglet.gl.GL_DEPTH_TEST)

    def updateVerts(self, verts:List[float]):
        vertsInBytes = len(verts) * 4
        if vertsInBytes != self.verts.size:
            self.verts.orphan(size=vertsInBytes)
        self.verts.write(array.array('f', verts))

        indices = [i for i in range(len(verts)//2)]
        indicesInBytes = len(indices) * 4
        if indicesInBytes != self.indices.size:
            self.indices.orphan(size=indicesInBytes)
            self.geometry.num_vertices = len(indices)
        self.indices.write(array.array('I', indices))

    def updateParams(self, deltas:List[float], color:List[float]):
        arr = color + [1.0] + deltas + [0.0, 0.0]
        self.uniform.write(array.array('f', arr))

    def setProjection(self, viewport: Tuple[float], mat: Tuple[float]):
        self.ctx.viewport = viewport
        self.ctx.projection_2d_matrix = Mat4(values=mat)

    def draw(self):
        self.geometry.render(self.program)
