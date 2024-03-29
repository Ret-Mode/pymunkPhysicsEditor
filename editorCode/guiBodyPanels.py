from typing import List

import arcade.gui

from .shapeInternals.editorBodyI import BodyI
from .editorTypes import V2, UnboundAngle
from .editorCursor import Cursor
from .editorBodyView import EditorBodyView
from .editorShapes import Container
from .guiButtons import Button, Label, TextButton, ScrollableLayout, editorButtonSetup
from .guiPanels import BodyPhysicsPanel, AddNewPanel, SettableOkResetButton, ContainerTransformPanel, CursorPanel
from .commandExec import ComAddBody, ComDelBody, ComSetContainerPosXY, ComApplyContainerPosXY, ComSetContainerAngleDeg, ComApplyContainerRotateDeg, ComSetContainerScale, ComApplyContainerScale
from .commandExec import ComShiftBodyUp, ComShiftBodyDown, ComSetBodyAsCurrent, ComBodyClone
from .commandExec import CommandExec, ComRenameBody, ComSetLastBodyAsCurrent, ComSetPivot, ComMoveObject
from .database import Database
from .editorState import EditorState

class BasicEditButtons(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.pivot = EditorState.getInstance().getPivot()
        row1 = arcade.gui.UIBoxLayout(vertical=False)

        row1.add(Button("P>CoG", "halfWidth", self.pivotToCog))
        row1.add(Button("M>P", "halfWidth", self.moveToPivot))

        self.add(row1)

    def pivotToCog(self):
        current:BodyI = EditorState.getInstance().getCurrentBody()
        if current:
            CommandExec.addCommand(ComSetPivot(self.pivot, current.physics.cog.final))

    def moveToPivot(self):
        current:BodyI = EditorState.getInstance().getCurrentBody()
        if current:
            CommandExec.addCommand(ComMoveObject(current, self.pivot))


class BodyButtons(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical=True)
        self.rows: List[arcade.gui.UIBoxLayout] = [self.add(arcade.gui.UIBoxLayout(vertical=False)) for i in range(11)]

        self.rows[0].add(Label(text="--BODY--", align='center'))
        
        self.bodyType: AddNewPanel = AddNewPanel(BodyI.getTypes(), addCallback=self.add_btn_cb)
        
        self.rows[1].add(self.bodyType)

        self.rows[2].add(Button(text="FIT", width='thirdWidth', callback=self.fit_cb))

        self.rows[2].add(Button(text="DEL", width='thirdWidth', callback=self.del_btn_cb))
        
        self.rows[2].add(Button(text="UP", width='thirdWidth', callback=self.up_btn_cb))
        
        self.rows[3].add(Button(text="SH/HID", width='thirdWidth', callback=self.swap_cb))

        self.rows[3].add(Button(text="CLONE", width='thirdWidth', callback=self.clone_cb))
        
        self.rows[3].add(Button(text="DOWN", width='thirdWidth', callback=self.down_btn_cb))
        
        self.bodyList: ScrollableLayout = ScrollableLayout(8, self.select)

        self.rows[4].add(self.bodyList)

        self.labelLine = SettableOkResetButton('Label', 'BODY', self.rename, self.resetDetails)

        self.rows[5].add(self.labelLine)

        self.typeLine = Label('--', align='left')

        self.rows[6].add(self.typeLine)

        self.cursorLine: CursorPanel = CursorPanel()
        self.rows[7].add(self.cursorLine)

        buttons = BasicEditButtons()
        self.rows[8].add(buttons)

        self.currentDetails: BodyPhysicsPanel = BodyPhysicsPanel(label='--PHYSICS PROP--', newName='BODY')

        self.rows[9].add(self.currentDetails)

        self.transform: ContainerTransformPanel = ContainerTransformPanel()
        self.rows[10].add(self.transform)

        self.view: EditorBodyView = None
        self.cursor: Cursor = None
        self.current = None

    def setCommandPipeline(self, view: EditorBodyView):
        self.view = view
        self.cursor = view.cursor
        self.transform.pivot = view.pivot

    def on_update(self, dt):
        retVal = super().on_update(dt)

        # update cursor coordinates
        self.cursorLine.setNewVal(self.cursor.viewCoords.x, self.cursor.viewCoords.y)
        # get all bodies
        labels: List[str] = Database.getInstance().getAllBodyLabels()
        # update list of bodies
        self.updateListOfLabels(labels, self.bodyList)
        # if current body changed
        current = EditorState.getInstance().getCurrentBody()
        if current and self.current != current:
            self.current = current
            
        if current:
            self.labelLine.setNewVal(current.label)
            self.typeLine.setText(current.type)
            self.currentDetails.setCurrent(current)
            self.transform.setCurrent(current)
        else:
            self.typeLine.setText('--')

        self.transform.updatePivot(self.view.pivot)
        
        return retVal

    def updateListOfLabels(self, currentViewLabels: List[str], panel) -> None:
        editorLabels: List[str] = panel.labels
        if len(currentViewLabels) != len(editorLabels):
            panel.setLabels(currentViewLabels)
        else:
            for i, j in zip(currentViewLabels, editorLabels):
                if i != j:
                    panel.setLabels(currentViewLabels)
                    break

    def select(self, label:str) -> None:
        CommandExec.addCommand(ComSetBodyAsCurrent(label))

    def fit_cb(self):
        current:BodyI = EditorState.getInstance().getCurrentBody()
        if current:
            self.view.viewOffset.fitToBox(current.box)

    def add_btn_cb(self) -> None:
        label: str = self.labelLine.getVal()
        typeID:str = self.bodyType.getCurrent()
        CommandExec.addCommand(ComAddBody(label, typeID))
        #self.view.commands.addCommand(ComSetLastBodyAsCurrent(self.view.database))

    def del_btn_cb(self) -> None:
        label: str = self.labelLine.getVal()
        if label in Database.getInstance().getAllBodyLabels():
            CommandExec.addCommand(ComDelBody(label))

    def up_btn_cb(self) -> None:
        CommandExec.addCommand(ComShiftBodyUp(self.current))

    def down_btn_cb(self) -> None:
        CommandExec.addCommand(ComShiftBodyDown(self.current))

    def swap_cb(self) -> None:
        self.view.swapHideState()

    def clone_cb(self) -> None:
        CommandExec.addCommand(ComBodyClone(self.current))

    def rename(self):
        if self.current:
            newName = self.labelLine.getVal()
            oldName = self.current.label
            if newName != oldName:
                CommandExec.addCommand(ComRenameBody(self.current, newName))

    def resetDetails(self):
        if self.current:
            self.labelLine.refresh()
        self.currentDetails.resetAll()