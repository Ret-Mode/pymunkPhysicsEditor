from typing import List, Optional

import arcade.gui

from .guiButtons import Button, Label, TextButton, ScrollableLayout, ScrollableSelector, ScrollableConstant, editorButtonSetup
from .guiPanels import ShapePhysicsPanel, SettableOkResetButton, ContainerTransformPanel, AddNewPanel
from .editorShapeView import EditorShapeView
from .shapeInternals.editorShapeI import ShapeI
from .shapeInternals.editorShape import Polygon
from .commandExec import ComNewShapeClone,  ComSetNewShapeAsCurrent, ComShiftNewShapeUp, ComShiftNewShapeDown
from .commandExec import ComRenameNewShape, ComSelectNewParentBody, ComAddNewShape, ComDelNewShape, CommandExec
from .database import Database
from .editorState import EditorState

class NoneShapePanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.label: Label = Label("--")
        self.add(self.label)
        # next/prev point button
        # flip button
        # radius textfield
        # pt to pivot
        # add at pivot


    def refresh(self, shape:Polygon):
        pass

class PolygonSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.label: Label = Label("Polygon")
        self.add(self.label)
        # next/prev point button
        # flip button
        # radius textfield
        # pt to pivot
        # add at pivot


    def refresh(self, shape:Polygon):
        # update radius
        pass


class DetailsPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.currentType: str = ShapeI.NONE
        self.polyPanel:PolygonSpecPanel = PolygonSpecPanel()
        self.nonePanel:NoneShapePanel = NoneShapePanel()
        self.currentPanel = self.nonePanel
        self.add(self.currentPanel)

    def switchTo(self, shape:ShapeI = None):
        if not shape and self.currentPanel == self.nonePanel:
            return
        self.remove(self.currentPanel)
        if not shape:
            self.currentPanel = self.nonePanel
        elif shape.type == ShapeI.POLYGON:
            self.currentPanel = self.polyPanel
        else:
            self.currentPanel = self.nonePanel
        self.add(self.currentPanel)
    
    def refresh(self, shape:ShapeI):
        if self.currentPanel:
            self.currentPanel.refresh(shape.internal)


class ShapeButtons(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical = True)
        self.rows: List[arcade.gui.UIBoxLayout] = [self.add(arcade.gui.UIBoxLayout(vertical=False)) for i in range(11)]

        self.rows[0].add(Label(text="--PARENT--", align='center'))
        
        self.bodyList: ScrollableSelector = ScrollableSelector(self.bodySelect)

        self.rows[1].add(self.bodyList)

        self.shapeType: AddNewPanel = AddNewPanel(ShapeI.getTypes(), addCallback=self.add_btn)
        
        self.rows[2].add(self.shapeType)


        self.rows[3].add(Label(text="--SHAPE--", align='center'))
        
        self.rows[4].add(Button(text="ADD", width='thirdWidth', callback=self.add_btn))

        self.rows[4].add(Button(text="DEL", width='thirdWidth', callback=self.del_btn))
        
        self.rows[4].add(Button(text="UP", width='thirdWidth', callback=self.up_btn_cb))
        
        self.rows[5].add(Button(text="SH/HID", width='thirdWidth', callback=self.swap_cb))

        self.rows[5].add(Button(text="CLONE", width='thirdWidth', callback=self.clone_cb))
        
        self.rows[5].add(Button(text="DOWN", width='thirdWidth', callback=self.down_btn_cb))
        
        

        self.shapeList: ScrollableLayout = ScrollableLayout(8, self.select)

        self.rows[6].add(self.shapeList)

        self.labelLine = SettableOkResetButton('Label', 'SHAPE', self.rename, self.resetDetails)

        self.rows[7].add(self.labelLine)

        self.currentDetails: ShapePhysicsPanel = ShapePhysicsPanel(label='--PHYSICS PROP--', newName='SHAPE')

        self.rows[8].add(self.currentDetails)

        self.transform: ContainerTransformPanel = ContainerTransformPanel()

        self.rows[9].add(self.transform)

        self.shapeProp: DetailsPanel = DetailsPanel()
        
        self.rows[10].add(self.shapeProp)

        self.view: EditorShapeView = None

        # self.commands = None
        self.current: Optional[ShapeI] = None


    def setCommandPipeline(self, view: EditorShapeView):
        self.view = view
        self.transform.pivot = view.pivot.local


    def on_update(self, dt):
        retVal = super().on_update(dt)

        database = Database.getInstance()
        state = EditorState.getInstance()
        # update list of bodies
        bodyLabels: List[str] = database.getAllBodyLabels()
        self.updateListOfLabels(bodyLabels, self.bodyList)
        
        # select active body
        parent = state.getCurrentBody()

        if parent:
            # update entry
            self.bodyList.setCurrent(parent.label)
            # update list of shapes
            labels: List[str] = database.getAllNewShapeLabelsForBody(parent.label)
            self.updateListOfLabels(labels, self.shapeList)

            # select active shape
            currentShape = state.getCurrentShape()
            
            # if shape was changed then update entries
            if currentShape and self.current != currentShape:
                self.current = currentShape
                self.shapeProp.switchTo(currentShape)
                
            if currentShape:
#                self.shapeProp.refresh(currentShape)
                self.labelLine.setNewVal(currentShape.label)
                self.currentDetails.setCurrent(currentShape)
                self.transform.setCurrent(currentShape)
        
        self.transform.updatePivot(self.view.pivot.local)
        
        return retVal
        

    def updateListOfLabels(self, currentViewLabels: List[str], panel: ScrollableLayout) -> None:
        editorLabels: List[str] = panel.labels
        if len(currentViewLabels) != len(editorLabels):
            panel.setLabels(currentViewLabels)
        else:
            for i, j in zip(currentViewLabels, editorLabels):
                if i != j:
                    panel.setLabels(currentViewLabels)
                    break

    def bodySelect(self, label:str) -> None:
        currentParent = EditorState.getInstance().getCurrentBody()
        if not currentParent or currentParent.label != label:
            CommandExec.addCommand(ComSelectNewParentBody(label))

    def select(self, label:str) -> None:
        CommandExec.addCommand(ComSetNewShapeAsCurrent(label))

    def add_btn(self) -> None:
        parent = EditorState.getInstance().getCurrentBody()
        if parent:
            label: str = self.labelLine.getVal()
            CommandExec.addCommand(ComAddNewShape(label, self.shapeType.getCurrent()))

    def del_btn(self) -> None:
        parent = EditorState.getInstance().getCurrentBody()
        label: str = self.labelLine.getVal()
        if parent and label in Database.getInstance().getAllNewShapeLabelsForBody(parent.label):
            CommandExec.addCommand(ComDelNewShape(label))

    def up_btn_cb(self) -> None:
        CommandExec.addCommand(ComShiftNewShapeUp())

    def down_btn_cb(self) -> None:
        CommandExec.addCommand(ComShiftNewShapeDown())

    def swap_cb(self) -> None:
        self.view.swapHideState()

    def clone_cb(self) -> None:
        CommandExec.addCommand(ComNewShapeClone(self.current))

    def rename(self):
        if self.current:
            newName = self.labelLine.getVal()
            oldName = self.current.label
            if newName != oldName:
                CommandExec.addCommand(ComRenameNewShape(newName))

    def resetDetails(self):
        if self.current:
            self.labelLine.refresh()
        self.currentDetails.resetAll()
