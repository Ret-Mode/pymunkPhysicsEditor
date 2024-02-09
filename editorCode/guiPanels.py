import arcade.gui
from arcade.gui.events import UIEvent
from arcade.gui.surface import Surface
from arcade import Color

from typing import List, Callable, Tuple, NamedTuple

from .config import massInPixelsToString, massInStringToPixels, densityInPixelsToString, densityInStringToPixels, distanceInPixelsToString, scaleToString, scaleFromString, angleToString, angleFromString, distanceInStringToPixels, areaInStringToPixels, areaInPixelsToString
from .config import momentInPixelsToString, momentInStringToPixels, floatFromString, floatToString, intToString, intFromString, hexToString, hexFromString

from .guiButtons import Button, Label, TextButton, TextInput, ScrollableCBLabel, ScrollableConstant, editorButtonSetup
from .guiTimeMeasure import TimeMeasure
from .editorTypes import V2
from .editorShapes import Container
from .commandExec import ComSetUserParam, ComResetUserParam, ComSetPivotXY, ComSetPivotRelativeXY, ComSetUserCoords, ComResetUserCoords, ComSetShapeRadius
from .commandExec import ComSetContainerPosXY, ComApplyContainerPosXY, ComSetContainerAngle, ComApplyContainerRotate, ComSetContainerScale, ComApplyContainerScale
from .commandExec import CommandExec, ComNewShapeSetMask, ComNewShapeSetCategory, ComNewShapeSetGroup, ComNewShapeSetSensor, ComNewShapeSetFriction, ComNewShapeSetElasticity

from .shapeInternals.editorShapeI import ShapeI
from .shapeInternals.editorPhysicsI import PhysicsProp



class ContainerTransformPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical=True)
        header = Label(text="--TRANSFORM--", align='center')
        self.pivotLine = SettableCoordButton('Pivot', setCB=self.setPivot, relativeCB=self.setPivotRelative)
        self.moveLine = SettableCoordButton('Move', setCB=self.setMoveCoords, relativeCB=self.setMoveCoordsRelative)
        self.angleLine = SettableOkResetButton('Angle', '0.0', okCB=self.setAngle, resetCB=self.setAngleRelative)
        self.scaleLine   = SettableOkResetButton('Scale', '1.0', okCB=self.setScale, resetCB=self.setScaleRelative)

        self.add(header)
        self.add(self.pivotLine)
        self.add(self.moveLine)
        self.add(self.angleLine)
        self.add(self.scaleLine)

        self.current: Container = None
        self.pivot: V2 = None

    def setCurrent(self, current:Container):
        self.current = current
        self.updateAngle(current.transform.objectAngle.angle)
        self.updateScale(current.transform.objectScale)

    def setPivot(self):
        x = self.getPivotX()
        y = self.getPivotY()
        CommandExec.addCommand(ComSetPivotXY(self.pivot, x, y))

    def setPivotRelative(self):
        x = self.getPivotX()
        y = self.getPivotY()
        CommandExec.addCommand(ComSetPivotRelativeXY(self.pivot, x, y))

    def setMoveCoords(self):
        if self.current:
            x = self.getMoveX()
            y = self.getMoveY()
            CommandExec.addCommand(ComSetContainerPosXY(self.current, x, y))

    def setMoveCoordsRelative(self):
        if self.current:
            x = self.getMoveX()
            y = self.getMoveY()
            CommandExec.addCommand(ComApplyContainerPosXY(self.current, x, y))

    def setAngle(self):
        if self.current:
            angle = self.getAngle()
            CommandExec.addCommand(ComSetContainerAngle(self.current, self.pivot, angle))

    def setAngleRelative(self):
        if self.current:
            angle = self.getAngle()
            CommandExec.addCommand(ComApplyContainerRotate(self.current, self.pivot, angle))

    def setScale(self):
        if self.current:
            scale = self.getScale()
            CommandExec.addCommand(ComSetContainerScale(self.current, self.pivot, scale))

    def setScaleRelative(self):
        if self.current:
            scale = self.getScale()
            CommandExec.addCommand(ComApplyContainerScale(self.current, self.pivot, scale))

    def updatePivot(self, coord:V2):
        xf = distanceInPixelsToString(coord.x, '0.0')
        yf = distanceInPixelsToString(coord.y, '0.0')
        self.pivotLine.setNewVal(xf, yf)

    def getPivotX(self) -> float:
        px = distanceInStringToPixels(self.pivotLine.getX(), 0.0)
        return px
    
    def getPivotY(self) -> float:
        py = distanceInStringToPixels(self.pivotLine.getY(), 0.0)
        return py
    
    def getMoveX(self) -> float:
        mx = distanceInStringToPixels(self.moveLine.getX(), 0.0)
        return mx
    
    def getMoveY(self) -> float:
        my = distanceInStringToPixels(self.moveLine.getY(), 0.0)
        return my

    def updateAngle(self, angle:float):
        af = angleToString(angle, '0.0')
        self.angleLine.setNewVal(af)

    def getAngle(self) -> float:
        a = angleFromString(self.angleLine.getVal(), 0.0)
        return a

    def updateScale(self, scale:float):
        sf = scaleToString(scale, '1.0')
        self.scaleLine.setNewVal(sf)

    def getScale(self) -> float:
        s = scaleFromString(self.scaleLine.getVal(), 1.0)
        return s

# TODO -> need to add one more reset button
# currently theres set and reset, need to add functionaly for "Esc" button
class PhysicsPanel(arcade.gui.UIBoxLayout):

    def __init__(self, label:str = '--', newName:str = 'ENTITY'):
        super().__init__(vertical=True)
        header = Label(text=label, align='center')
        self.areaLine = LabelledValue('Area', '0.0')
        self.densityLine = SettableOkResetButton('Density', '1.0', self.setUserDensity, self.resetDensity)
        self.massLine = SettableOkResetButton('Mass', '1.0', self.setUserMass, self.resetMass)
        self.cogLine = None
        self.momentLine = SettableOkResetButton('Moment', '0.0', self.setUserMoment, self.resetMoment)
        self.add(header)
        self.add(self.areaLine)
        self.add(self.densityLine)
        self.add(self.massLine)
        self.add(self.momentLine)

        self.current: Container = None

    def setCurrent(self, current:Container):
        self.current = current
        if current:
            self.setCurrentDetails(current.physics)

    def setUserDensity(self):
        if self.current:
            density = self.getDensity()
            if density:
                CommandExec.addCommand(ComSetUserParam(self.current.physics.density, density))

    def setUserMass(self):
        if self.current:
            scale = self.current.transform.objectScale
            if scale != 0.0:
                mass = self.getMass() / (scale * scale)
                if mass:
                    CommandExec.addCommand(ComSetUserParam(self.current.physics.mass, mass))

    def setUserMoment(self):
        if self.current:
            scale = self.current.transform.objectScale
            if scale != 0.0:
                moment = self.getMoment() / (scale * scale * scale * scale)
                if moment:
                    CommandExec.addCommand(ComSetUserParam(self.current.physics.moment, moment))

    def resetDensity(self):
        if self.current:
            CommandExec.addCommand(ComResetUserParam(self.current.physics.density))

    def resetMass(self):
        if self.current:
            CommandExec.addCommand(ComResetUserParam(self.current.physics.mass))

    def resetMoment(self):
        if self.current:
            CommandExec.addCommand(ComResetUserParam(self.current.physics.moment))

    def resetAll(self):
        self.resetDensity()
        self.resetMass()
        self.resetMoment()

    def setCurrentDetails(self, current: PhysicsProp):
        #scale = current.transform.objectScale
        area = areaInPixelsToString(current.area, '0.0')
        self.areaLine.setNewVal(area)
        density = densityInPixelsToString(current.density.final, '1.0')
        self.densityLine.setNewVal(density)
        mass = massInPixelsToString(current.mass.final, '1.0')
        self.massLine.setNewVal(mass)
        moment = momentInPixelsToString(current.moment.final, '1.0')
        self.momentLine.setNewVal(moment)
    
    def getArea(self) -> float:
        area = areaInStringToPixels(self.areaLine.getVal(), 0.0)
        return area

    def getMass(self) -> float:
        mass = massInStringToPixels(self.massLine.getVal(), 0.0)
        return mass

    def getMoment(self) -> float:
        moment = momentInStringToPixels(self.momentLine.getVal(), 0.0)
        return moment
    
    def getDensity(self) -> float:
        density = densityInStringToPixels(self.densityLine.getVal(), 1.0)
        return density



class BodyPhysicsPanel(PhysicsPanel):

    def __init__(self, label:str = '--', newName:str = 'ENTITY'):
        super().__init__(label, newName = 'ENTITY')
        self.cogLine = SettableCoordButton('CoG', '0.0', self.setUserCog, self.resetCog)
        self.add(self.cogLine)

    def setUserCog(self):
        if self.current:
            x = self.getCogX()
            y = self.getCogY()
            x, y = self.current.transform.getInvMat().mulXY(x, y)
            CommandExec.addCommand(ComSetUserCoords(self.current.physics.cog, x, y))

    def resetCog(self):
        if self.current:
            CommandExec.addCommand(ComResetUserCoords(self.current.physics.cog))

    def resetAll(self):
        super().resetAll()
        self.resetCog()

    def setCurrentDetails(self, current: PhysicsProp):
        super().setCurrentDetails(current)
        cog = current.cog.final
        cogX = distanceInPixelsToString(cog.x, '0.0')
        cogY = distanceInPixelsToString(cog.y, '0.0')
        self.cogLine.setNewVal(cogX, cogY)

    def getCogX(self) -> str:
        cogX = distanceInStringToPixels(self.cogLine.getX(), 0.0)
        return cogX 
    
    def getCogY(self) -> str:
        cogY = distanceInStringToPixels(self.cogLine.getY(), 0.0)
        return cogY
    

class ShapePhysicsPanel(PhysicsPanel):

    def __init__(self, label:str = '--', newName:str = 'ENTITY'):
        super().__init__(label = '--', newName = 'ENTITY')
        self.cogLine = LabelledCoord('CoG', '0.0')
        self.radiusLine = SettableOkButton('Radius', "0.000", self.setRadius)
        self.elasticity = SettableOkButton('Elasticity', "0.000", self.setElasticity)
        self.friction = SettableOkButton('Friction', "1.000", self.setFriction)
        self.sensor:SettableBoolButton = SettableBoolButton("Sensor", False, self.setSensor)
        self.filterGroup = SettableOkButton('Group', "0", self.setFilterGroup)
        self.filterCategory = SettableOkButton('Category', "0", self.setFilterCategory)
        self.filterMask = SettableOkButton('Mask', "0", self.setFilterMask)

        self.add(self.cogLine)
        self.add(self.radiusLine)
        self.add(self.elasticity)
        self.add(self.friction)
        self.add(self.sensor)
        self.add(self.filterGroup)
        self.add(self.filterCategory)
        self.add(self.filterMask)

    def setCurrent(self, current:ShapeI):
        super().setCurrent(current)
        self.radiusLine.setNewVal(floatToString(current.internal.radius.final, "0.000"))
        self.elasticity.setNewVal(floatToString(current.elasticity, "0.000"))
        self.friction.setNewVal(floatToString(current.friction, "1.000"))
        self.sensor.setNewVal(current.isSensor)
        self.filterGroup.setNewVal(hexToString(current.shapeFilterGroup, "0"))
        self.filterCategory.setNewVal(hexToString(current.shapeFilterCategory, "0"))
        self.filterMask.setNewVal(hexToString(current.shapeFilterMask, "0"))

    def setRadius(self):
        if self.current:
            CommandExec.addCommand(ComSetShapeRadius(self.current, floatFromString(self.radiusLine.getVal(), '0.000')))

    def setFilterMask(self):
        if self.current:
            CommandExec.addCommand(ComNewShapeSetMask(self.current, hexFromString(self.filterMask.getVal(), "0.000")))

    def setFilterCategory(self):
        if self.current:
            CommandExec.addCommand(ComNewShapeSetCategory(self.current, hexFromString(self.filterCategory.getVal(), "0")))

    def setFilterGroup(self):
        if self.current:
            CommandExec.addCommand(ComNewShapeSetGroup(self.current, hexFromString(self.filterGroup.getVal(), "0")))

    def setSensor(self):
        if self.current:
            CommandExec.addCommand(ComNewShapeSetSensor(self.current, not self.sensor.getVal()))

    def setElasticity(self):
        if self.current:
            CommandExec.addCommand(ComNewShapeSetElasticity(self.current, floatFromString(self.elasticity.getVal(), "0.000")))

    def setFriction(self):
        if self.current:
            CommandExec.addCommand(ComNewShapeSetFriction(self.current, floatFromString(self.friction.getVal(), "1.000")))

    def setCurrentDetails(self, current: PhysicsProp):
        super().setCurrentDetails(current)
        cog = current.cog.final
        cogX = distanceInPixelsToString(cog.x, '0.000')
        cogY = distanceInPixelsToString(cog.y, '0.000')
        self.cogLine.setNewVal(cogX, cogY)
    

class CursorPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical=False)
        self.description = Label(text="Cursor", width='thirdWidth', align='left')
        self.xCoord = Label(text='0.000', width='thirdWidth', align='left')
        self.yCoord = Label(text='0.000', width='thirdWidth', align='left')
        self.oldX:float = 0.0
        self.oldY:float = 0.0
        self.add(self.description)
        self.add(self.xCoord)
        self.add(self.yCoord)

    def setNewVal(self, x:float, y:float):
        if self.oldX != x:
            self.oldX = x
            x = floatToString(x, '0.000')
            self.xCoord.setText(x)
        if self.oldY != y:
            self.oldY = y
            y = floatToString(y, '0.000')
            self.yCoord.setText(y)


class TopButtons(arcade.gui.UIBoxLayout):

    def __init__(self, callback: Callable[[str], None]):
        self._callback = callback
        super().__init__(vertical=True)
        self.rows: List[arcade.gui.UIBoxLayout] = [self.add(arcade.gui.UIBoxLayout(vertical=False)), 
                     self.add(arcade.gui.UIBoxLayout(vertical=False)), 
                     self.add(arcade.gui.UIBoxLayout(vertical=False))]

        self.rows[0].add(Label(text="--MAIN--", align='center'))
        
        self.rows[1].add(TextButton(text="BODY", width='thirdWidth', callback=self.change))

        self.rows[1].add(TextButton(text="SHAPE", width='thirdWidth', callback=self.change))
        
        self.rows[1].add(TextButton(text="CNSTRNT", width='thirdWidth', callback=self.change))
        
        self.rows[2].add(TextButton(text="TEX", width='thirdWidth', callback=self.change))

        self.rows[2].add(TextButton(text="LD/SV", width='thirdWidth', callback=self.change))
        
        self.rows[2].add(TextButton(text="OPTIONS", width='thirdWidth', callback=self.change))

    def change(self, text:str) -> None:
        self._callback(text)


class ButtonPanel(arcade.gui.UIBoxLayout):

    def __init__(self, view: arcade.View) -> None:
        self._view: arcade.View = view
        super().__init__(x=view.window.width - editorButtonSetup['width'], y=view.window.height, vertical=True)

    def resize(self) -> None:
        old_x: float = self.rect.x
        old_y: float = self.rect.y
        old_h: float = self.rect.height
        dx: float = self._view.window.width - editorButtonSetup['width'] - old_x
        dy: float = self._view.window.height - old_y - old_h
        self.move(int(dx), int(dy))
        self.do_layout()

    def widthOfPanel(self) -> int:
        return editorButtonSetup['width']
    

class PerfPanel2(arcade.gui.UIWidget):

    def __init__(self, width='width', scale: float = 32.0, yPad: int = editorButtonSetup['height']):
        super().__init__(width=editorButtonSetup[width], height=scale*6 + yPad*3)
        self.yPad: int = yPad
        self.scale: float = scale
        self.timeToHeight: float = self.scale * 60.0
        self.colorOK: Color = (0, 128, 0)
        self.colorBad: Color = (128, 0, 0)
        self.colorVeryBad: Color = (255, 0, 0)
        TimeMeasure.resize(self.width)

    def on_update(self, dt):
        val = super().on_update(dt)
        self.trigger_render()
        return val
    
    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        surface.clear(color=(0, 0, 0, 0))
        self.drawPerf()

    def getColorAndClamp(self, value: float) -> Tuple[Color, float]:
        val: float  = value * self.timeToHeight
        if val > self.scale * 2.0:
            return self.colorVeryBad, self.scale * 2.0
        elif val > self.scale:
            return self.colorBad, val
        else:
            return self.colorOK, val

    def drawPerf(self) -> None:
        x: int = 0
        y1: int = self.yPad
        y2: float = y1 + self.scale*2.0 + self.yPad
        y3: float = y2 + self.scale*2.0 + self.yPad
        currentfr: int = TimeMeasure.current + 1
        for frame in range(currentfr, TimeMeasure.size):
            frameVal: NamedTuple("frame", [("update", float), ("draw", float), ("sum", float)]) = TimeMeasure.getFrame(frame)
            current = self.getColorAndClamp(frameVal.sum)
            arcade.draw_line(x, y1, x, y1 + current[1], current[0])
            current = self.getColorAndClamp(frameVal.draw)
            arcade.draw_line(x, y2, x, y2 + current[1], current[0])
            current = self.getColorAndClamp(frameVal.update)
            arcade.draw_line(x, y3, x, y3 + current[1], current[0])
            x += 1

        for frame in range(currentfr):
            frameVal: NamedTuple("frame", [("update", float), ("draw", float), ("sum", float)]) = TimeMeasure.getFrame(frame)
            current = self.getColorAndClamp(frameVal.sum)
            arcade.draw_line(x, y1, x, y1 + current[1], current[0])
            current = self.getColorAndClamp(frameVal.draw)
            arcade.draw_line(x, y2, x, y2 + current[1], current[0])
            current = self.getColorAndClamp(frameVal.update)
            arcade.draw_line(x, y3, x, y3 + current[1], current[0])
            x += 1


class LabelledValue(arcade.gui.UIBoxLayout):

    def __init__(self, label:str, default:str = '') -> None:
        super().__init__(vertical=False)
        self.description = Label(text=label, width='thirdWidth', align='left')
        self.value = Label(text=default, width='twoThirdsWidth', align='left')
        self.oldVal = default

        self.add(self.description)
        self.add(self.value)

    def refresh(self):
        self.value.setText(self.oldVal)

    def setNewVal(self, val:str):
        if val != self.oldVal:
            self.oldVal = val
            self.value.setText(self.oldVal)

    def getVal(self):
        return self.value.text


class LabelledCoord(arcade.gui.UIBoxLayout):

    def __init__(self, label:str, default:str = '0.0') -> None:
        super().__init__(vertical=False)
        self.description = Label(text=label, width='thirdWidth', align='left')
        self.xCoord = Label(text=default, width='thirdWidth', align='left')
        self.yCoord = Label(text=default, width='thirdWidth', align='left')
        self.oldX = default
        self.oldY = default

        self.add(self.description)
        self.add(self.xCoord)
        self.add(self.yCoord)

    def setNewVal(self, valX:str, valY:str):
        if valX != self.oldX:
            self.oldX = valX
            self.xCoord.setText(self.oldX)
        if valY != self.oldY:
            self.oldY = valY
            self.yCoord.setText(self.oldY)

    def refresh(self):
        self.xCoord.setText(self.oldX)
        self.yCoord.setText(self.oldY)

    def getX(self):
        return self.xCoord.getText()
    
    def getY(self):
        return self.yCoord.getText()
    

class SettableOkResetButton(arcade.gui.UIBoxLayout):

    def __init__(self, label:str, default:str = '', okCB=None, resetCB=None) -> None:
        super().__init__(vertical=False)
        self.description = Label(text=label, width='thirdWidth', align='left')
        self.value = TextInput(text=default, width='halfWidth', okCB=okCB, resetCB=self.refresh)
        self.okButton = Button(text="Reset", width='sixthWidth', callback=resetCB)
        self.oldVal = default

        self.add(self.description)
        self.add(self.value)
        self.add(self.okButton)

    def refresh(self):
        self.value.setText(self.oldVal)

    def setNewVal(self, val:str):
        if val != self.oldVal:
            self.oldVal = val
            self.value.setText(self.oldVal)

    def getVal(self):
        return self.value.getText()
        

class SettableCoordButton(arcade.gui.UIBoxLayout):

    def __init__(self, label:str, default:str = '0.000', setCB=None, relativeCB=None) -> None:
        super().__init__(vertical=False)
        self.description = Label(text=label, width='sixthWidth', align='left')
        self.xCoord = TextInput(text=default, width='thirdWidth', okCB=setCB, resetCB=self.refresh)
        self.yCoord = TextInput(text=default, width='thirdWidth', okCB=setCB, resetCB=self.refresh)
        #self.setButton = Button(text="Set", width='tvelveWidth', callback=setCB)
        self.relButton = Button(text="Relat", width='sixthWidth', callback=relativeCB)
        self.oldX = default
        self.oldY = default

        self.add(self.description)
        self.add(self.xCoord)
        self.add(self.yCoord)
        #self.add(self.setButton)
        self.add(self.relButton)

    def setNewVal(self, valX:str, valY:str):
        if valX != self.oldX:
            self.oldX = valX
            self.xCoord.setText(self.oldX)
        if valY != self.oldY:
            self.oldY = valY
            self.yCoord.setText(self.oldY)

    def refresh(self):
        self.xCoord.setText(self.oldX)
        self.yCoord.setText(self.oldY)

    def getX(self):
        return self.xCoord.getText()
    
    def getY(self):
        return self.yCoord.getText()
    

class SettableBoolButton(arcade.gui.UIBoxLayout):

    def __init__(self, label:str, default:bool = False, okCB:Callable[[None], None]=None) -> None:
        super().__init__(vertical=False)
        initText = "YES" if default else "NO" 
        self.description = Label(text=label, width='thirdWidth', align='left')
        self.value = Label(text=initText, width='halfWidth', align='left')
        self.okButton = Button(text="Change", width='sixthWidth', callback=self.exec)
        self.internal = default
        self.callback = okCB

        self.add(self.description)
        self.add(self.value)
        self.add(self.okButton)

    def exec(self):
        self.callback()

    def refresh(self):
        if self.internal:
            self.value.setText("YES")
        else:
            self.value.setText("NO")

    def setNewVal(self, val:bool):
        if val != self.internal:
            self.internal = val
            self.refresh()

    def getVal(self):
        return self.internal

    
class SettableOkButton(arcade.gui.UIBoxLayout):

    def __init__(self, label:str, default:str = '', okCB=None) -> None:
        super().__init__(vertical=False)
        self.description = Label(text=label, width='thirdWidth', align='left')
        self.value = TextInput(text=default, width='twoThirdsWidth', okCB=okCB, resetCB=self.refresh)
        #self.okButton = Button(text="Set", width='tvelveWidth', callback=okCB)
        #self.resetButton = Button(text="Reset", width='tvelveWidth', callback=self.refresh)
        self.oldVal = default

        self.add(self.description)
        self.add(self.value)
        #self.add(self.okButton)
        #self.add(self.resetButton)

    def refresh(self):
        if self.oldVal != self.value.getText():
            self.value.setText(self.oldVal)

    def setNewVal(self, val:str):
        if self.oldVal != val:
            self.oldVal = val
            self.value.setText(val)

    def getVal(self):
        return self.value.getText()
    

class SettableCoordOkButton(arcade.gui.UIBoxLayout):

    def __init__(self, label:str, default:str = '0.0', setCB=None) -> None:
        super().__init__(vertical=False)
        self.description = Label(text=label, width='sixthWidth', align='left')
        self.xCoord = TextInput(text=default, width='thirdWidth',okCB=setCB, resetCB=self.refresh)
        self.yCoord = TextInput(text=default, width='thirdWidth',okCB=setCB, resetCB=self.refresh)
        self.setButton = Button(text="S", width='tvelveWidth', callback=setCB)
        self.relButton = Button(text="R", width='tvelveWidth', callback=self.refresh)
        self.oldX = default
        self.oldY = default

        self.add(self.description)
        self.add(self.xCoord)
        self.add(self.yCoord)
        self.add(self.setButton)
        self.add(self.relButton)

    def setNewVal(self, valX:str, valY:str):
        if valX != self.oldX:
            self.oldX = valX
            self.xCoord.setText(self.oldX)
        if valY != self.oldY:
            self.oldY = valY
            self.yCoord.setText(self.oldY)

    def refresh(self):
        self.xCoord.setText(self.oldX)
        self.yCoord.setText(self.oldY)

    def getX(self):
        return self.xCoord.getText()
    
    def getY(self):
        return self.yCoord.getText()
    

class ScrollableConstantPanel(arcade.gui.UIBoxLayout):

    def __init__(self, labels: List[str] = [], lrWidth='quartWidth', labelWidth='halfWidth') -> None:
        super().__init__(vertical=False)
        
        self.label = ScrollableConstant(labels, labelWidth)
        self.lButton = Button('<', lrWidth, self.label.setNext)
        self.rButton = Button('>', lrWidth, self.label.setPrev)

        self.add(self.lButton)
        self.add(self.label)
        self.add(self.rButton)

    def setLabels(self, labels: List[str]) -> None:
        self.label.setLabels(labels)

    def getCurrent(self) -> str:
        return self.label.getCurrent()


class ScrollableCBLabelPanel(arcade.gui.UIBoxLayout):

    def __init__(self, label:str ='--', lrWidth='quartWidth', labelWidth='halfWidth', cbNext:Callable[[None], None]=None, cbPrev:Callable[[None], None] = None) -> None:
        super().__init__(vertical=False)
        
        self.lButton = Button('<', lrWidth, cbPrev)
        self.label = ScrollableCBLabel(label, labelWidth, cbNext, cbPrev)
        self.rButton = Button('>', lrWidth, cbNext)

        self.add(self.lButton)
        self.add(self.label)
        self.add(self.rButton)

    def setLabel(self, label:str) -> None:
        self.label.setLabel(label)

    def getCurrent(self) -> str:
        return self.label.getCurrent()
    

class EmptyPanel(arcade.gui.UIBoxLayout):

    def __init__(self, label='--'):
        super().__init__(vertical=False)
        label = Label(label)
        self.add(label)


class AddNewPanel(arcade.gui.UIBoxLayout):

    def __init__(self, entries: List[str], addCallback:Callable[[None], None]):
        super().__init__(vertical = False)
        self.addButton: Button = Button("ADD", 'thirdWidth', self.addCB)
        self.selectableType: ScrollableConstantPanel = ScrollableConstantPanel(entries, 'tvelveWidth', 'halfWidth')
        self._cb = addCallback
        self.add(self.addButton)
        self.add(self.selectableType)

    def getCurrent(self) -> str:
        return self.selectableType.getCurrent()

    def addCB(self) -> None:
        if self._cb:
            self._cb()