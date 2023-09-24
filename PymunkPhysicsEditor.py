from typing import Optional

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED
import time
import arcade
import PIL.Image
import io
import arcade.gui
import pickle

from editorCode.editorOptionView import EditorOptionView


from editorCode.guiPanels import ButtonPanel, TopButtons
from editorCode.guiBodyPanels import BodyButtons
from editorCode.guiShapePanels import ShapeButtons
from editorCode.guiConstraintPanels import ConstraintButtons
from editorCode.guiOptionPanels import OptionsButtons
from editorCode.guiTexturePanels import TextureButtons
from editorCode.editorBodyView import EditorBodyView
from editorCode.editorShapeView import EditorShapeView
from editorCode.editorConstraintView import EditorConstraintView
from editorCode.editorTextureView import EditorTextureView
from editorCode.guiTimeMeasure import TimeMeasure
from editorCode.config import globalWindowSetup

from editorCode.database import Database
from editorCode.editorCursor import Cursor
from editorCode.editorCamera import CursorCamera
from editorCode.bufferContainer import BufferContainer
from editorCode.lineShader import LineDraw

class EditorView(arcade.View):

    modes = {'BODY': None,
             'SHAPE': None,
             'CNSTRNT': None,
             'OPTIONS': None,
             'TEX': None}


    def _getActiveView(self):
        if self.currentMode == 'BODY':
            return self.editorBodyView
        elif self.currentMode == 'SHAPE':
            return self.editorShapeView
        elif self.currentMode == 'CNSTRNT':
            return self.editorConstraintView
        elif self.currentMode == 'OPTIONS':
            return self.editorOptionView
        elif self.currentMode == 'TEX':
            return self.editorTextureView
        else:
            assert False

    def __init__(self):
        super().__init__()

        self.cursor = Cursor()
        self.cursorView = CursorCamera(globalWindowSetup['width'], globalWindowSetup['height'])

        self.manager = arcade.gui.UIManager()

        self.buttonPanel = ButtonPanel(self)
        self.manager.add(self.buttonPanel)

        self.topButtons = self.buttonPanel.add(TopButtons(self.changeMainMode))

        self.midbtn = False

        self.editableWidth = globalWindowSetup['width'] - self.buttonPanel.widthOfPanel()
        self.editorShapeView = EditorShapeView(self.editableWidth, globalWindowSetup['height'], self.cursor)
        self.editorBodyView = EditorBodyView(self.editableWidth, globalWindowSetup['height'], self.cursor)
        self.editorConstraintView = EditorConstraintView(self.editableWidth, globalWindowSetup['height'], self.cursor)
        self.editorOptionView = EditorOptionView(self.editableWidth, globalWindowSetup['height'], self.cursor)
        self.editorTextureView = EditorTextureView(self.editableWidth, globalWindowSetup['height'], self.cursor)

        self.setupModes()

        self.cursorShader = LineDraw()

    def setupModes(self):
        EditorView.modes['BODY'] = BodyButtons()
        EditorView.modes['SHAPE'] = ShapeButtons()
        EditorView.modes['CNSTRNT'] = ConstraintButtons()
        EditorView.modes['OPTIONS'] = OptionsButtons()
        EditorView.modes['TEX'] = TextureButtons()

        # set panels
        EditorView.modes['BODY'].setCommandPipeline(self.editorBodyView)
        EditorView.modes['SHAPE'].setCommandPipeline(self.editorShapeView)
        EditorView.modes['CNSTRNT'].setCommandPipeline(self.editorConstraintView)

        self.currentMode = 'BODY'
        self.buttonPanel.add(EditorView.modes[self.currentMode]) 

    def on_show_view(self):
        self.manager.enable()
        return super().on_show_view()

    def on_hide_view(self):
        self.manager.disable()
        return super().on_hide_view()

    #@TimeMeasure.measureUpdate
    def on_update(self, delta_time: float):
        self._getActiveView().update()

    def draw_cursor(self):
        buffer = BufferContainer.getInstance()
        buffer.reset()
        buffer.drawScale = 1.0
        buffer.addCursor(self.cursor.screenCoords, 
                         self.cursorView.sizeInPixels, 
                         self.cursorView.offset, 
                         self.cursorView.sizeInPixels.x - self.editableWidth)
        
        self.cursorShader.update(buffer.verts, buffer.colors, buffer.indices)
        self.cursorShader.setProjection((0, 0, 
                    self.cursorView.sizeInPixels.x, 
                    self.cursorView.sizeInPixels.y), 
                    self.cursorView.mat)
        self.cursorShader.draw()


    def on_draw(self):
        self.clear(arcade.color.BLACK)
        self.manager.draw()
        self._getActiveView().draw()
        self.draw_cursor()
        
    def on_key_press(self, key, modifiers):
        if key == arcade.key.F5:
            data = pickle.dumps(Database.getInstance())
            if data:
                with open('data/states/save.car', 'wb') as f:
                    f.write(data)
        elif key == arcade.key.F9:
            with open('data/states/save.car', 'rb') as f:
                data = f.read()
                database:Database = pickle.loads(data)
                Database._instance.bodies = database.bodies
                Database._instance.shapeList = database.shapeList
                Database._instance.constraints = database.constraints
                Database._instance.currentBody = database.currentBody
                Database._instance.currentConstraint = database.currentConstraint
                Database._instance.currentShape = database.currentShape

        view = self._getActiveView()
        if self.currentMode == 'BODY':
            if key == ord('m'):
                view.startMoveTransform()
            elif key == ord('r'):
                view.startRotateTransform()
            elif key == ord('s'):
                view.startScaleTransform()
            elif key == ord('q'):
                view.startRotateScaleTransform()
            elif key == ord('z'):
                view.undo()
            elif key == ord('y'):
                view.redo()
            elif key == ord('t'):
                view.pymunkTest()
            
        elif self.currentMode == 'SHAPE':
            if key == ord(' '):
                view.nextSnappableObject()
                # if view.current:
                #     EditorView.modes[self.currentMode].currentDetails.setCurrentDetails(self.editorShapeView.current)
            elif key == ord('m'):
                view.startMoveTransform()
            elif key == ord('r'):
                view.startRotateTransform()
            elif key == ord('s'):
                view.startScaleTransform()
            elif key == ord('q'):
                view.startRotateScaleTransform()
            elif key == ord('z'):
                view.undo()
            elif key == ord('y'):
                view.redo()
            elif key == ord('t'):
                view.pymunkTest()

        elif self.currentMode == 'CNSTRNT':
            if key == ord('z'):
                view.undo()
            elif key == ord('y'):
                view.redo()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        pass

    def on_mouse_enter(self, x: int, y: int):
        self.window.set_mouse_visible(False)

    def on_mouse_leave(self, x: int, y: int):
        self.window.set_mouse_visible(True)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        view = self._getActiveView()
        if x < self.editableWidth:
            if button == arcade.MOUSE_BUTTON_MIDDLE:
                self.midbtn = True
            elif self.currentMode == 'BODY':
                if button == arcade.MOUSE_BUTTON_RIGHT:
                    if view.transform.active:
                        view.cancelTransform()
                    else:
                        view.setHelperPoint()
                else:
                    if view.transform.active:
                        view.applyTransform()
                    else:
                        pass
                        #self.editorBodyView.addPointAtCursor()

            elif self.currentMode == 'SHAPE':
                if button == arcade.MOUSE_BUTTON_RIGHT:
                    if view.transform.active:
                        view.cancelTransform()
                    else:
                        view.setHelperPoint()
                else:
                    if view.transform.active:
                        view.applyTransform()
                    else:
                        view.defaultAction()

            elif self.currentMode == 'CNSTRNT':
                view.defaultAction()

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
       #if x < self.editableWidth:
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            self.midbtn = False

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        view = self._getActiveView()
        if self.midbtn and x < self.editableWidth:
            if self.currentMode == 'BODY':
                view.moveView(float(-dx),float(-dy))
            elif self.currentMode == 'SHAPE':
                view.moveView(float(-dx),float(-dy))
            elif self.currentMode == 'CNSTRNT':
                view.moveView(float(-dx),float(-dy))
            elif self.currentMode == 'TEX':
                view.moveView(float(-dx),float(-dy))
        else:
            if self.currentMode == 'BODY':
                view.moveCursor(float(x),float(y))
            elif self.currentMode == 'SHAPE':
                view.moveCursor(float(x),float(y))
            elif self.currentMode == 'CNSTRNT':
                view.moveCursor(float(x),float(y))
            elif self.currentMode == 'TEX':
                view.moveCursor(float(x),float(y))
        
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        if x < self.editableWidth:
            self._getActiveView().changeScale(scroll_y)

    def on_resize(self, width: int, height: int):
        self.cursorView.resize(width, height)
        self.editableWidth = width - self.buttonPanel.widthOfPanel()
        self.editorShapeView.resize(self.editableWidth, height)
        self.editorBodyView.resize(self.editableWidth, height)
        self.editorConstraintView.resize(self.editableWidth, height)
        self.editorTextureView.resize(self.editableWidth, height)
        self.buttonPanel.resize()

    def changeMainMode(self, toMode:str):
        if toMode in EditorView.modes:
            if self.currentMode:
                self.buttonPanel.remove(EditorView.modes[self.currentMode])
            self.currentMode = toMode
            self.buttonPanel.add(EditorView.modes[self.currentMode])


def main():
    window = arcade.Window(**globalWindowSetup)
    window.show_view(EditorView())
    arcade.run()


if __name__ == "__main__":
    main()
