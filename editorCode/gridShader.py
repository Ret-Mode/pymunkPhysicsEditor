# code below is adapted from einarf grid generation example; 

import arcade

from .editorTypes import V2
from .editorCamera import EditorCamera

class GridDraw:
    
    def __init__(self):
        self.ctx = arcade.get_window().ctx
        vertexShader="""
            #version 330

            uniform int gridResX;
            uniform float gridSize;
            uniform vec2 gridStart;

            void main() {
                float x = gridStart.x + (gl_VertexID % gridResX)*gridSize;
                float y = gridStart.y + (gl_VertexID / gridResX)*gridSize;
                gl_Position = vec4(x, y, 0.0, 1.0);
            }
            """

        geometryShader="""
            #version 330 core
            layout (points) in;
            layout (line_strip, max_vertices = 4) out;

            uniform float crossSize;

            uniform WindowBlock
            {
                mat4 projection;
                mat4 view;
            } window;  

            void main() {
                float fX = gl_in[0].gl_Position.x;
                float fY = gl_in[0].gl_Position.y;
                        
                gl_Position = window.projection * vec4(fX-crossSize, fY, 0.0, 1.0); 
                EmitVertex();

                gl_Position = window.projection * vec4(fX+crossSize, fY, 0.0, 1.0); 
                EmitVertex();
                
                EndPrimitive();

                gl_Position = window.projection * vec4(fX, fY-crossSize, 0.0, 1.0); 
                EmitVertex();

                gl_Position = window.projection * vec4(fX, fY+crossSize, 0.0, 1.0); 
                EmitVertex();
                
                EndPrimitive();

            } 
            """

        fragmentShader="""
            #version 330

            uniform vec4 color;

            out vec4 fColor;

            void main() {
                fColor = vec4(color.rgb, 1.0);
            }
            """
        self.program = self.ctx.program(vertex_shader=vertexShader, geometry_shader=geometryShader, fragment_shader=fragmentShader)

        self.program.set_uniform_safe('color', (1.0, 1.0, 1.0, 1.0))
        self.program.set_uniform_safe('crossSize', 5)
        self.program.set_uniform_safe('gridStart', (-1.0, -1.0))
        self.program.set_uniform_safe('gridSize', 100)
        self.program.set_uniform_safe('gridResX', 20)

        self.geometry = self.ctx.geometry(mode=self.ctx.POINTS)
        #ctx.disable(pyglet.gl.GL_DEPTH_TEST)

    def setGrid(self, viewLowerBounds:V2, viewSize:V2, viewScale:float, gridSize:float, crossSize:int, roundFactor:int):
        armLength = crossSize * viewScale
        gridDisappear = 20.0
        gridSizeInPixels:float = gridSize / viewScale
        if gridSizeInPixels > gridDisappear:
            gridNormalView = 60.0

            colorLerp =  0.25 * max(gridDisappear, min(gridNormalView, gridSizeInPixels)) / (gridNormalView - gridDisappear)
            xLower = round(viewLowerBounds.x, roundFactor)
            yLower = round(viewLowerBounds.y, roundFactor)
            xUpper = round(viewLowerBounds.x + viewSize.x, roundFactor)
            yUpper = round(viewLowerBounds.y + viewSize.y, roundFactor)
            if xLower < 0.0:
                xLower -= gridSize
            if yLower < 0.0:
                yLower -= gridSize
            if xUpper > 0.0:
                xUpper += gridSize
            if yUpper + 0.0:
                yUpper += gridSize

            crossesX = int(round((xUpper-xLower)/gridSize, 0))
            crossesY = int(round((yUpper-yLower)/gridSize, 0))
            if crossesX*crossesY > 0:
                self.program.set_uniform_safe('color', (colorLerp, colorLerp, colorLerp, 1.0))
                self.program.set_uniform_safe('crossSize', armLength)
                self.program.set_uniform_safe('gridStart', (xLower, yLower))
                self.program.set_uniform_safe('gridSize', gridSize)
                self.program.set_uniform_safe('gridResX', crossesX)

                self.geometry.render(self.program, vertices=crossesX*crossesY)

    def drawGrid(self, camera:EditorCamera):
        # draw 10 cm grid:
        self.setGrid(camera.offsetScaled, camera.sizeScaled, camera.scale, 0.1, 1, 1)
        # draw 1 m grid:
        self.setGrid(camera.offsetScaled, camera.sizeScaled, camera.scale, 1.0, 3, 0)
        # draw 10 m grid:
        self.setGrid(camera.offsetScaled, camera.sizeScaled, camera.scale, 10.0, 5, -1)
        # draw 100 m grid:
        self.setGrid(camera.offsetScaled, camera.sizeScaled, camera.scale, 100.0, 7, -2)