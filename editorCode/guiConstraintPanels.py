from typing import List, Optional, Callable, Union

import arcade.gui

from .guiButtons import Button, Label, TextButton, ScrollableLayout, ScrollableCBLabel, ScrollableConstant, editorButtonSetup
from .guiPanels import SettableOkResetButton, AddNewPanel, SettableOkButton, SettableCoordOkButton, ScrollableConstantPanel, CursorPanel, SettableBoolButton
from .editorConstraintView import EditorConstraintView
from .editorCursor import Cursor
from .commandExec import CommandExec, ComRenameConstraint, ComSetConstraintAsCurrent, ComAddConstraint, ComConstraintSetNewBodyA, ComConstraintSetNewBodyB
from .commandExec import ComDelConstraint, ComConstraintClone, ComShiftConstraintDown, ComShiftConstraintUp, ComSetRestAngle, ComSetStiffness, ComSetDamping
from .commandExec import ComSetRestLength, ComSetAnchorA, ComSetAnchorB, ComSetPhase, ComSetRatio, ComSetGrooveA, ComSetGrooveB, ComSetRatchet
from .commandExec import ComSetRotaryMin, ComSetRotaryMax, ComSetRate, ComSetSlideMin, ComSetSlideMax, ComConstraintSwapBodies
from .commandExec import ComSetAnchorBFromCoords, ComSetAnchorAFromCoords, ComSetPivot, ComSetGrooveAFromCoords, ComSetGrooveBFromCoords
from .commandExec import ComSetSelfCollision, ComSetMaxBias, ComSetMaxForce, ComSetErrorBias
from .database import Database
from .editorState import EditorState

from .config import angleToString, angleFromString, floatToString, floatFromString

from .editorTypes import Angle
from .constraintInternals.editorConstraintI import ConstraintI
from .constraintInternals.editorConstraint import DampedRotarySpring, DampedSpring, GearJoint, GrooveJoint, PinJoint, PivotJoint
from .constraintInternals.editorConstraint import RatchetJoint, RotaryLimitJoint, SimpleMotor, SlideJoint
from .shapeInternals.editorBodyI import BodyI



class ConstraintPhysicsData(arcade.gui.UIBoxLayout):
    def __init__(self):
        super().__init__(vertical = True)
        self.inf = float("inf")
        self.current:ConstraintI = None
        self.sCollide:SettableBoolButton = SettableBoolButton("SelfColl", False, self.setSelfCollision)
        self.mBias = SettableOkButton('Max bias', "inf", self.setMBias)
        self.mForce = SettableOkButton('Max force', "inf", self.setMForce)
        self.eBias = SettableOkButton('Error bias', "0.001", self.setEBias)

        self.add(self.sCollide)
        self.add(self.mBias)
        self.add(self.mForce)
        self.add(self.eBias)

    def refresh(self, constraint:ConstraintI):
        self.current = constraint
        if constraint:
            self.sCollide.setNewVal(constraint.selfCollide)
            self.mBias.setNewVal(floatToString(constraint.maxBias, "inf"))
            self.mForce.setNewVal(floatToString(constraint.maxForce, "inf"))
            self.eBias.setNewVal(floatToString(constraint.errorBias, "0.001"))

    def setSelfCollision(self):
        if self.current:
            CommandExec.addCommand(ComSetSelfCollision(self.current, not self.sCollide.getVal()))

    def setMBias(self):
        if self.current:
            CommandExec.addCommand(ComSetMaxBias(self.current, floatFromString(self.mBias.getVal(), self.inf)))

    def setMForce(self):
        if self.current:
            CommandExec.addCommand(ComSetMaxForce(self.current, floatFromString(self.mForce.getVal(), self.inf)))

    def setEBias(self):
        if self.current:
            CommandExec.addCommand(ComSetErrorBias(self.current, floatFromString(self.eBias.getVal(), 0.001)))


class ConstraintBodiesSelector(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = False)
        self.bodyALabel: ScrollableCBLabel = ScrollableCBLabel('--', width='fiveTwelvthWidth', cbNext=self.nextConstraintA, cbPrev=self.prevConstraintA)
        self.bodyBLabel: ScrollableCBLabel = ScrollableCBLabel('--', width='fiveTwelvthWidth', cbNext=self.nextConstraintB, cbPrev=self.prevConstraintB)
        self.swap: Button = Button('SWAP', 'sixthWidth', self.swapCB)
        self.add(self.bodyALabel)
        self.add(self.bodyBLabel)
        self.add(self.swap)

    def _possibleConstraintBodies(self, current: ConstraintI, frm: BodyI, filt:BodyI):
        labels = list(Database.getInstance().getAllBodyLabels())
        if filt and filt.label in labels:
            ind = labels.index(filt.label)
            labels.pop(ind)
        if labels:
            if frm and frm.label in labels:
                index = labels.index(frm.label)
                labels = labels[index+1:] + labels[:index]
        return labels

    def nextConstraintA(self):
        current = EditorState.getInstance().getCurrentConstraint()
        if current:
            elems = self._possibleConstraintBodies(current, current.bodyA, current.bodyB)
            if elems:
                CommandExec.addCommand(ComConstraintSetNewBodyA(current, elems[-1]))

    def prevConstraintA(self):
        current = EditorState.getInstance().getCurrentConstraint()
        if current:
            elems = self._possibleConstraintBodies(current, current.bodyA, current.bodyB)
            if elems:
                CommandExec.addCommand(ComConstraintSetNewBodyA(current, elems[0]))

    def nextConstraintB(self):
        current = EditorState.getInstance().getCurrentConstraint()
        if current:
            elems = self._possibleConstraintBodies(current, current.bodyB, current.bodyA)
            if elems:
                CommandExec.addCommand(ComConstraintSetNewBodyB(current, elems[-1]))

    def prevConstraintB(self):
        current = EditorState.getInstance().getCurrentConstraint()
        if current:
            elems = self._possibleConstraintBodies(current, current.bodyB, current.bodyA)
            if elems:
                CommandExec.addCommand(ComConstraintSetNewBodyB(current, elems[0]))

    def swapCB(self):
        current = EditorState.getInstance().getCurrentConstraint()
        if current:
            CommandExec.addCommand(ComConstraintSwapBodies(current))

    def refresh(self, constraint:ConstraintI):
        if not constraint:
            self.bodyALabel.setLabel('--')
            self.bodyBLabel.setLabel('--')
            return
        if constraint.bodyA and self.bodyALabel.getCurrent() != constraint.bodyA.label: 
            self.bodyALabel.setLabel(constraint.bodyA.label)
        elif not constraint.bodyA :
            self.bodyALabel.setLabel('--')
        if constraint.bodyB and self.bodyBLabel.getCurrent() != constraint.bodyB.label:
            self.bodyBLabel.setLabel(constraint.bodyB.label)
        elif not constraint.bodyB:
            self.bodyBLabel.setLabel('--')


class NoneConstraintPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.label: Label = Label("--")
        self.add(self.label)

    def refresh(self, constraint:ConstraintI):
        pass


class BasicEditButtons(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.pivot = EditorState.getInstance().getPivot()
        row1 = arcade.gui.UIBoxLayout(vertical=False)

        row1.add(Button("P>CoGA", "halfWidth", self.pivotToCogA))
        row1.add(Button("P>CoGB", "halfWidth", self.pivotToCogB))

        self.add(row1)

    def pivotToCogA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.bodyA.physics.cog.final))

    def pivotToCogB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.bodyB.physics.cog.final))

    def refresh(self, constraint:ConstraintI):
        self.current = constraint


class AnchorButtons(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: Union[DampedSpring, PinJoint, PivotJoint, SlideJoint] = None
        self.pivot = EditorState.getInstance().getPivot()
        row1 = arcade.gui.UIBoxLayout(vertical=False)
        row2 = arcade.gui.UIBoxLayout(vertical=False)

        row1.add(Button("A>B", "sixthWidth", self.anchorAtoAnchorB))
        row1.add(Button("B>A", "sixthWidth", self.anchorBtoAnchorA))
        row1.add(Button("P>A", "sixthWidth", self.pivottoAnchorA))
        row1.add(Button("P>B", "sixthWidth", self.pivottoAnchorB))
        row1.add(Button("A>P", "sixthWidth", self.anchorAtoPivot))
        row1.add(Button("B>P", "sixthWidth", self.anchorBtoPivot))


        row2.add(Button("P>CA", "sixthWidth", self.pivottoCogA))
        row2.add(Button("A>CA", "sixthWidth", self.anchorAtoCogA))
        row2.add(Button("B>CA", "sixthWidth", self.anchorBtoCogA))
        row2.add(Button("P>CB", "sixthWidth", self.pivottoCogB))
        row2.add(Button("A>CB", "sixthWidth", self.anchorAtoCogB))
        row2.add(Button("B>CB", "sixthWidth", self.anchorBtoCogB))

        self.add(row1)
        self.add(row2)

    def pivottoCogA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.bodyA.physics.cog.final))

    def anchorAtoCogA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorAFromCoords(self.current, self.current.bodyA.physics.cog.final))

    def anchorBtoCogA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorBFromCoords(self.current, self.current.bodyA.physics.cog.final))

    def pivottoCogB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.bodyB.physics.cog.final))

    def anchorAtoCogB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorAFromCoords(self.current, self.current.bodyB.physics.cog.final))

    def anchorBtoCogB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorBFromCoords(self.current, self.current.bodyB.physics.cog.final))

    def anchorBtoPivot(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorBFromCoords(self.current, self.pivot))

    def anchorAtoPivot(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorAFromCoords(self.current, self.pivot))

    def pivottoAnchorA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.anchorA.final))

    def pivottoAnchorB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.anchorB.final))

    def anchorAtoAnchorB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorAFromCoords(self.current, self.current.anchorB.final))

    def anchorBtoAnchorA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorBFromCoords(self.current, self.current.anchorA.final))

    def refresh(self, constraint:ConstraintI):
        self.current = constraint


class GrooveButtons(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: GrooveJoint = None
        self.pivot = EditorState.getInstance().getPivot()
        
        row1 = arcade.gui.UIBoxLayout(vertical=False)
        row2 = arcade.gui.UIBoxLayout(vertical=False)
        row3 = arcade.gui.UIBoxLayout(vertical=False)
        row4 = arcade.gui.UIBoxLayout(vertical=False)

        row1.add(Button("GA>GB", "quartWidth", self.grooveAtoGrooveB))
        row1.add(Button("GB>GA", "quartWidth", self.grooveBtoGrooveA))
        row1.add(Button("GA>P", "quartWidth", self.grooveAtoPivot))
        row1.add(Button("P>GA", "quartWidth", self.pivottoGrooveA))
        row2.add(Button("GB>P", "quartWidth", self.grooveBtoPivot))
        row2.add(Button("P>GB", "quartWidth", self.pivottoGrooveB))
        row2.add(Button("B>P", "quartWidth", self.anchorBtoPivot))
        row2.add(Button("P>B", "quartWidth", self.pivottoAnchorB))

        row3.add(Button("P>CA", "quartWidth", self.pivottoCogA))
        row3.add(Button("GA>CA", "quartWidth", self.grooveAtoCogA))
        row3.add(Button("GB>CA", "quartWidth", self.grooveBtoCogA))
        row3.add(Button("B>CA", "quartWidth", self.anchorBtoCogA))
        row4.add(Button("P>CB", "quartWidth", self.pivottoCogB))
        row4.add(Button("GA>CB", "quartWidth", self.grooveAtoCogB))
        row4.add(Button("GB>CB", "quartWidth", self.grooveBtoCogB))
        row4.add(Button("B>CB", "quartWidth", self.anchorBtoCogB))

        self.add(row1)
        self.add(row2)
        self.add(row3)
        self.add(row4)

    def pivottoCogA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.bodyA.physics.cog.final))

    def grooveAtoCogA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetGrooveAFromCoords(self.current, self.current.bodyA.physics.cog.final))

    def grooveBtoCogA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetGrooveBFromCoords(self.current, self.current.bodyA.physics.cog.final))

    def anchorBtoCogA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorBFromCoords(self.current, self.current.bodyA.physics.cog.final))

    def pivottoCogB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.bodyB.physics.cog.final))

    def grooveAtoCogB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetGrooveAFromCoords(self.current, self.current.bodyB.physics.cog.final))

    def grooveBtoCogB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetGrooveBFromCoords(self.current, self.current.bodyB.physics.cog.final))

    def anchorBtoCogB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorBFromCoords(self.current, self.current.bodyB.physics.cog.final))



    def grooveAtoGrooveB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetGrooveAFromCoords(self.current, self.current.grooveB.final))

    def grooveBtoGrooveA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetGrooveBFromCoords(self.current, self.current.grooveA.final))

    def pivottoGrooveA(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.grooveA.final))

    def grooveAtoPivot(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetGrooveAFromCoords(self.current, self.pivot))

    def pivottoGrooveB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.grooveB.final))

    def grooveBtoPivot(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetGrooveBFromCoords(self.current, self.pivot))

    def pivottoAnchorB(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetPivot(self.pivot, self.current.anchorB.final))

    def anchorBtoPivot(self):
        if self.current and self.current.bodyA and self.current.bodyB:
            CommandExec.addCommand(ComSetAnchorBFromCoords(self.current, self.pivot))

    def refresh(self, constraint:ConstraintI):
        self.current = constraint


class DampedRotarySpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Damped Rotary Spring")
        self.restLine: SettableOkButton = SettableOkButton('Rest Ang.', '0.0', self.setRest)
        self.stiffnessLine: SettableOkButton = SettableOkButton('Stiffness', '0.0', self.setStiffness)
        self.dampingLine: SettableOkButton = SettableOkButton('Damping', '0.0', self.setDamping)
        self.buttons:BasicEditButtons = BasicEditButtons()

        self.add(self.label)
        self.add(self.restLine)
        self.add(self.stiffnessLine)
        self.add(self.dampingLine)
        self.add(self.buttons)

    def setRest(self):
        if self.current:
            CommandExec.addCommand(ComSetRestAngle(self.current, 
                                                     angleFromString(self.restLine.getVal(), 0.0)))

    def setStiffness(self):
        if self.current:
            CommandExec.addCommand(ComSetStiffness(self.current, 
                                                      floatFromString(self.stiffnessLine.getVal(), 0.0)))

    def setDamping(self):
        if self.current:
            CommandExec.addCommand(ComSetDamping(self.current, 
                                                   floatFromString(self.dampingLine.getVal(), 0.0)))

    def refresh(self, constraint:DampedRotarySpring):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.restLine.setNewVal(angleToString(self.current.restAngle.angle, '0.0'))
        self.stiffnessLine.setNewVal(floatToString(self.current.stiffness, '0.0'))
        self.dampingLine.setNewVal(floatToString(self.current.damping, '0.0'))


class DampedSpringSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Damped Spring")

        self.restLine: SettableOkButton = SettableOkButton('Rest Len.', '0.0', self.setRest)
        self.stiffnessLine: SettableOkButton = SettableOkButton('Stiffness', '0.0', self.setStiffness)
        self.dampingLine: SettableOkButton = SettableOkButton('Damping', '0.0', self.setDamping)
        self.anchorALine: SettableCoordOkButton = SettableCoordOkButton('Anchr A', '0.0', self.setAnchorA)
        self.anchorBLine: SettableCoordOkButton = SettableCoordOkButton('Anchr B', '0.0', self.setAnchorB)
        self.buttons:AnchorButtons = AnchorButtons()

        self.add(self.label)
        self.add(self.restLine)
        self.add(self.stiffnessLine)
        self.add(self.dampingLine)
        self.add(self.anchorALine)
        self.add(self.anchorBLine)
        self.add(self.buttons)

    def setRest(self):
        if self.current:
            CommandExec.addCommand(ComSetRestLength(self.current, 
                                                      floatFromString(self.restLine.getVal(), 0.0)))

    def setStiffness(self):
        if self.current:
            CommandExec.addCommand(ComSetStiffness(self.current, 
                                                     floatFromString(self.stiffnessLine.getVal(), 0.0)))

    def setDamping(self):
        if self.current:
            CommandExec.addCommand(ComSetDamping(self.current, 
                                                   floatFromString(self.dampingLine.getVal(), 0.0)))

    def setAnchorA(self):
        if self.current:
            x = floatFromString(self.anchorALine.getX(), 0.0)
            y = floatFromString(self.anchorALine.getY(), 0.0)
            CommandExec.addCommand(ComSetAnchorA(self.current, 
                                                   x, y))

    def setAnchorB(self):
        if self.current:
            x = floatFromString(self.anchorBLine.getX(), 0.0)
            y = floatFromString(self.anchorBLine.getY(), 0.0)
            CommandExec.addCommand(ComSetAnchorB(self.current, x, y))

    def refresh(self, constraint:DampedSpring):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.restLine.setNewVal(floatToString(self.current.restLength, '0.0'))
        self.stiffnessLine.setNewVal(floatToString(self.current.stiffness, '0.0'))
        self.dampingLine.setNewVal(floatToString(self.current.damping, '0.0'))
        self.anchorALine.setNewVal(floatToString(self.current.anchorA.local.x, '0.0'), floatToString(self.current.anchorA.local.y, '0.0'))
        self.anchorBLine.setNewVal(floatToString(self.current.anchorB.local.x, '0.0'), floatToString(self.current.anchorB.local.y, '0.0'))


class GearJointSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Gear Joint")
        self.phaseLine: SettableOkButton = SettableOkButton('Phase', '0.0', self.setPhase)
        self.ratioLine: SettableOkButton = SettableOkButton('Ratio', '0.0', self.setRatio)
        self.buttons:BasicEditButtons = BasicEditButtons()

        self.add(self.label)
        self.add(self.phaseLine)
        self.add(self.ratioLine)
        self.add(self.buttons)

    def setPhase(self):
        if self.current:
            CommandExec.addCommand(ComSetPhase(self.current, 
                                                 angleFromString(self.phaseLine.getVal(), 0.0)))

    def setRatio(self):
        if self.current:
            CommandExec.addCommand(ComSetRatio(self.current, 
                                                 floatFromString(self.ratioLine.getVal(), 0.0)))

    def refresh(self, constraint:GearJoint):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.phaseLine.setNewVal(angleToString(self.current.phase.angle, '0.0'))
        self.ratioLine.setNewVal(floatToString(self.current.ratio, '0.0'))


class GrooveJointSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Groove Joint")
        self.grooveALine: SettableCoordOkButton = SettableCoordOkButton('Grv A', '0.0', self.setGrooveA)
        self.grooveBLine: SettableCoordOkButton = SettableCoordOkButton('Grv B', '0.0', self.setGrooveB)
        self.anchorBLine: SettableCoordOkButton = SettableCoordOkButton('Anchr B', '0.0', self.setAnchorB)
        self.buttons:GrooveButtons = GrooveButtons()

        self.add(self.label)
        self.add(self.grooveALine)
        self.add(self.grooveBLine)
        self.add(self.anchorBLine)
        self.add(self.buttons)

    def setGrooveA(self):
        if self.current:
            x = floatFromString(self.grooveALine.getX(), 0.0)
            y = floatFromString(self.grooveALine.getY(), 0.0)
            CommandExec.addCommand(ComSetGrooveA(self.current, x, y))

    def setGrooveB(self):
        if self.current:
            x = floatFromString(self.grooveBLine.getX(), 0.0)
            y = floatFromString(self.grooveBLine.getY(), 0.0)
            CommandExec.addCommand(ComSetGrooveB(self.current, x, y))

    def setAnchorB(self):
        if self.current:
            x = floatFromString(self.anchorBLine.getX(), 0.0)
            y = floatFromString(self.anchorBLine.getY(), 0.0)
            CommandExec.addCommand(ComSetAnchorB(self.current, x, y))

    def refresh(self, constraint:GrooveJoint):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.grooveALine.setNewVal(floatToString(self.current.grooveA.local.x, '0.0'), floatToString(self.current.grooveA.local.y, '0.0'))
        self.grooveBLine.setNewVal(floatToString(self.current.grooveB.local.x, '0.0'), floatToString(self.current.grooveB.local.y, '0.0'))
        self.anchorBLine.setNewVal(floatToString(self.current.anchorB.local.x, '0.0'), floatToString(self.current.anchorB.local.y, '0.0'))


class PinJointSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Pin Joint")
        self.anchorALine: SettableCoordOkButton = SettableCoordOkButton('Anchr A', '0.0', self.setAnchorA)
        self.anchorBLine: SettableCoordOkButton = SettableCoordOkButton('Anchr B', '0.0', self.setAnchorB)
        self.buttons:AnchorButtons = AnchorButtons()

        self.add(self.label)
        self.add(self.anchorALine)
        self.add(self.anchorBLine)
        self.add(self.buttons)

    def setAnchorA(self):
        if self.current:
            x = floatFromString(self.anchorALine.getX(), 0.0)
            y = floatFromString(self.anchorALine.getY(), 0.0)
            CommandExec.addCommand(ComSetAnchorA(self.current, 
                                                   x, y))

    def setAnchorB(self):
        if self.current:
            x = floatFromString(self.anchorBLine.getX(), 0.0)
            y = floatFromString(self.anchorBLine.getY(), 0.0)
            CommandExec.addCommand(ComSetAnchorB(self.current, x, y))

    def refresh(self, constraint:PinJoint):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.anchorALine.setNewVal(floatToString(self.current.anchorA.local.x, '0.0'), floatToString(self.current.anchorA.local.y, '0.0'))
        self.anchorBLine.setNewVal(floatToString(self.current.anchorB.local.x, '0.0'), floatToString(self.current.anchorB.local.y, '0.0'))
        

class PivotJointSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Pivot Joint")
        self.anchorALine: SettableCoordOkButton = SettableCoordOkButton('Anchr A', '0.0', self.setAnchorA)
        self.anchorBLine: SettableCoordOkButton = SettableCoordOkButton('Anchr B', '0.0', self.setAnchorB)
        self.pivotLine: SettableCoordOkButton = SettableCoordOkButton('Pivot', '0.0', self.setPivot)
        self.buttons:AnchorButtons = AnchorButtons()

        self.add(self.label)
        self.add(self.anchorALine)
        self.add(self.anchorBLine)
        self.add(self.pivotLine)
        self.add(self.buttons)

    def setAnchorA(self):
        if self.current:
            x = floatFromString(self.anchorALine.getX(), 0.0)
            y = floatFromString(self.anchorALine.getY(), 0.0)
            CommandExec.addCommand(ComSetAnchorA(self.current, 
                                                   x, y))

    def setAnchorB(self):
        if self.current:
            x = floatFromString(self.anchorBLine.getX(), 0.0)
            y = floatFromString(self.anchorBLine.getY(), 0.0)
            CommandExec.addCommand(ComSetAnchorB(self.current, x, y))

    def setPivot(self):
        if self.current:
            pass

    def refresh(self, constraint:PivotJoint):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.anchorALine.setNewVal(floatToString(self.current.anchorA.local.x, '0.0'), floatToString(self.current.anchorA.local.y, '0.0'))
        self.anchorBLine.setNewVal(floatToString(self.current.anchorB.local.x, '0.0'), floatToString(self.current.anchorB.local.y, '0.0'))


class RatchetJointSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Ratchet Joint")
        self.phaseLine: SettableOkButton = SettableOkButton('Phase', '0.0', self.setPhase)
        self.ratchetLine: SettableOkButton = SettableOkButton('Ratch', '0.0', self.setRatio)
        self.buttons:BasicEditButtons = BasicEditButtons()

        self.add(self.label)
        self.add(self.phaseLine)
        self.add(self.ratchetLine)
        self.add(self.buttons)

    def setPhase(self):
        if self.current:
            CommandExec.addCommand(ComSetPhase(self.current, 
                                                 angleFromString(self.phaseLine.getVal(), 0.0)))

    def setRatio(self):
        if self.current:
            CommandExec.addCommand(ComSetRatchet(self.current, 
                                                 angleFromString(self.ratchetLine.getVal(), 0.0)))

    def refresh(self, constraint:RatchetJoint):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.phaseLine.setNewVal(angleToString(self.current.phase.angle, '0.0'))
        self.ratchetLine.setNewVal(angleToString(self.current.ratchet.angle, '0.0'))


class RotaryLimitJointSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Rotary Limit")
        self.minLine: SettableOkButton = SettableOkButton('Min', '0.0', self.setMin)
        self.maxLine: SettableOkButton = SettableOkButton('Max', '0.0', self.setMax)
        self.buttons:BasicEditButtons = BasicEditButtons()

        self.add(self.label)
        self.add(self.minLine)
        self.add(self.maxLine)
        self.add(self.buttons)

    def setMin(self):
        if self.current:
            CommandExec.addCommand(ComSetRotaryMin(self.current, 
                                                 angleFromString(self.minLine.getVal(), 0.0)))

    def setMax(self):
        if self.current:
            CommandExec.addCommand(ComSetRotaryMax(self.current, 
                                                 angleFromString(self.maxLine.getVal(), 0.0)))

    def refresh(self, constraint:RotaryLimitJoint):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.minLine.setNewVal(angleToString(self.current.min.angle, '0.0'))
        self.maxLine.setNewVal(angleToString(self.current.max.angle, '0.0'))


class SimpleMotorSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Simple Motor")
        self.rateLine: SettableOkButton = SettableOkButton('Rate', '0.0', self.setPhase)
        self.buttons:BasicEditButtons = BasicEditButtons()

        self.add(self.label)
        self.add(self.rateLine)
        self.add(self.buttons)

    def setPhase(self):
        if self.current:
            CommandExec.addCommand(ComSetRate(self.current, 
                                                 angleFromString(self.rateLine.getVal(), 0.0)))

    def refresh(self, constraint:SimpleMotor):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.rateLine.setNewVal(angleToString(self.current.rate.angle, '0.0'))


class SlideJointSpecPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)
        self.current: ConstraintI = None
        self.label: Label = Label("Slide Joint")
        self.anchorALine: SettableCoordOkButton = SettableCoordOkButton('Anchr A', '0.0', self.setAnchorA)
        self.anchorBLine: SettableCoordOkButton = SettableCoordOkButton('Anchr B', '0.0', self.setAnchorB)
        self.minLine: SettableOkButton = SettableOkButton('Min', '0.0', self.setMin)
        self.maxLine: SettableOkButton = SettableOkButton('Max', '0.0', self.setMax)
        self.buttons:AnchorButtons = AnchorButtons()

        self.add(self.label)
        self.add(self.anchorALine)
        self.add(self.anchorBLine)
        self.add(self.minLine)
        self.add(self.maxLine)
        self.add(self.buttons)

    def setAnchorA(self):
        if self.current:
            x = floatFromString(self.anchorALine.getX(), 0.0)
            y = floatFromString(self.anchorALine.getY(), 0.0)
            CommandExec.addCommand(ComSetAnchorA(self.current, 
                                                   x, y))

    def setAnchorB(self):
        if self.current:
            x = floatFromString(self.anchorBLine.getX(), 0.0)
            y = floatFromString(self.anchorBLine.getY(), 0.0)
            CommandExec.addCommand(ComSetAnchorB(self.current, x, y))

    def setMin(self):
        if self.current:
            CommandExec.addCommand(ComSetSlideMin(self.current, 
                                                 floatFromString(self.minLine.getVal(), 0.0)))

    def setMax(self):
        if self.current:
            CommandExec.addCommand(ComSetSlideMax(self.current, 
                                                 floatFromString(self.maxLine.getVal(), 0.0)))

    def refresh(self, constraint:SlideJoint):
        if self.current != constraint:
            self.current = constraint
        self.buttons.refresh(constraint)
        self.anchorALine.setNewVal(floatToString(self.current.anchorA.local.x, '0.0'), floatToString(self.current.anchorA.local.y, '0.0'))
        self.anchorBLine.setNewVal(floatToString(self.current.anchorB.local.x, '0.0'), floatToString(self.current.anchorB.local.y, '0.0'))
        self.minLine.setNewVal(floatToString(self.current.min, '0.0'))
        self.maxLine.setNewVal(floatToString(self.current.max, '0.0'))


class DetailsPanel(arcade.gui.UIBoxLayout):

    def __init__(self):
        super().__init__(vertical = True)

        self.view:EditorConstraintView = None
        self.possibleModes:ScrollableCBLabel = ScrollableCBLabel(label='--', width='width', cbNext=self.nextViewMode, cbPrev=self.prevViewMode)

        self.dampedRotaryPanel:DampedRotarySpecPanel = DampedRotarySpecPanel()
        self.dampedSpringPanel:DampedSpringSpecPanel = DampedSpringSpecPanel()
        self.gearJointPanel:GearJointSpecPanel = GearJointSpecPanel()
        self.grooveJointPanel:GrooveJointSpecPanel = GrooveJointSpecPanel()
        self.pinJointPanel:PinJointSpecPanel = PinJointSpecPanel()
        self.pivotJointPanel:PivotJointSpecPanel = PivotJointSpecPanel()
        self.ratchetJointPanel:RatchetJointSpecPanel = RatchetJointSpecPanel()
        self.rotaryLimitJointPanel:RotaryLimitJointSpecPanel = RotaryLimitJointSpecPanel()
        self.simpleMotorPanel:SimpleMotorSpecPanel = SimpleMotorSpecPanel()
        self.slideJointPanel:SlideJointSpecPanel = SlideJointSpecPanel()
        
        self.nonePanel:NoneConstraintPanel = NoneConstraintPanel()
        self.bodySelectorPanel = ConstraintBodiesSelector()

        self.constraintPhysicsData = ConstraintPhysicsData()
        
        self.currentPanel = self.nonePanel

        self.add(self.possibleModes)
        self.add(self.currentPanel)
        
    def getALabel(self) -> str:
        return self.bodySelectorPanel.bodyALabel.getCurrent()
    
    def getBLabel(self) -> str:
        return self.bodySelectorPanel.bodyBLabel.getCurrent()

    def switchTo(self, constraint:ConstraintI = None):
        if not constraint and self.currentPanel == self.nonePanel:
            return
        self.remove(self.currentPanel)
        if self.currentPanel != self.nonePanel:
            self.remove(self.constraintPhysicsData)
            self.remove(self.bodySelectorPanel)

        if not constraint:
            self.currentPanel = self.nonePanel
        elif constraint.type == ConstraintI.DAMPEDROTARYSPRING:
            self.currentPanel = self.dampedRotaryPanel
        elif constraint.type == ConstraintI.DAMPEDSPRING:
            self.currentPanel = self.dampedSpringPanel
        elif constraint.type == ConstraintI.GEARJOINT:
            self.currentPanel = self.gearJointPanel
        elif constraint.type == ConstraintI.GROOVEJOINT:
            self.currentPanel = self.grooveJointPanel
        elif constraint.type == ConstraintI.PINJOINT:
            self.currentPanel = self.pinJointPanel
        elif constraint.type == ConstraintI.PIVOTJOINT:
            self.currentPanel = self.pivotJointPanel
        elif constraint.type == ConstraintI.RATCHETJOINT:
            self.currentPanel = self.ratchetJointPanel
        elif constraint.type == ConstraintI.ROTARYLIMITJOINT:
            self.currentPanel = self.rotaryLimitJointPanel
        elif constraint.type == ConstraintI.SIMPLEMOTOR:
            self.currentPanel = self.simpleMotorPanel
        elif constraint.type == ConstraintI.SLIDEJOINT:
            self.currentPanel = self.slideJointPanel
        else:
            self.currentPanel = self.nonePanel

        self.add(self.currentPanel)
        if self.currentPanel != self.nonePanel:
            self.add(self.constraintPhysicsData)
            self.add(self.bodySelectorPanel)
    
    def refresh(self, constraint:ConstraintI):
        if self.currentPanel:
            self.possibleModes.setLabel(self.view.mode)
            self.currentPanel.refresh(constraint)
            self.bodySelectorPanel.refresh(constraint)
            self.constraintPhysicsData.refresh(constraint)

    def nextViewMode(self):
        self.view.nextMode()

    def prevViewMode(self):
        self.view.prevMode()


class ConstraintButtons(arcade.gui.UIBoxLayout):

    def __init__(self) -> None:
        super().__init__(vertical = True)
        self.rows: List[arcade.gui.UIBoxLayout] = [self.add(arcade.gui.UIBoxLayout(vertical=False)) for i in range(9)]

        self.rows[0].add(Label(text="--NEW CNSTRNT TYPE--", align='center'))

        self.constraintType = AddNewPanel(ConstraintI.getTypes(), self.add_btn)

        self.rows[1].add(self.constraintType)

        self.rows[2].add(Label(text="--CNSTRNT--", align='center'))
        
        self.rows[3].add(Button(text="FIT", width='thirdWidth', callback=self.fit_cb))

        self.rows[3].add(Button(text="DEL", width='thirdWidth', callback=self.del_btn))
        
        self.rows[3].add(Button(text="UP", width='thirdWidth', callback=self.up_btn_cb))
        
        self.rows[4].add(Button(text="SH/HID", width='thirdWidth', callback=self.swap_cb))

        self.rows[4].add(Button(text="CLONE", width='thirdWidth', callback=self.clone_cb))
        
        self.rows[4].add(Button(text="DOWN", width='thirdWidth', callback=self.down_btn_cb))
        
        self.constraintList: ScrollableLayout = ScrollableLayout(8, self.select)

        self.rows[5].add(self.constraintList)

        self.labelLine = SettableOkResetButton('Label', 'CNSTRNT', self.rename, self.resetDetails)

        self.rows[6].add(self.labelLine)

        self.cursorLine: CursorPanel = CursorPanel()
        self.rows[7].add(self.cursorLine)

        self.constraintProp: DetailsPanel = DetailsPanel()
        
        self.rows[8].add(self.constraintProp)

        self.view: EditorConstraintView = None
        self.cursor: Cursor = None
        # self.commands = None
        self.current: Optional[ConstraintI] = None


    def setCommandPipeline(self, view: EditorConstraintView):
        self.view = view
        self.cursor = view.cursor
        self.constraintProp.view = view

    def on_update(self, dt):
        retVal = super().on_update(dt)

        self.cursorLine.setNewVal(self.cursor.viewCoords.x, self.cursor.viewCoords.y)
        
        # update list of constraints
        labels: List[str] = Database.getInstance().getAllConstraintLabels()
        self.updateListOfLabels(labels, self.constraintList)

        # select active constraint
        current = EditorState.getInstance().getCurrentConstraint()
        
        # if constraint was changed then update entries
        if current and self.current != current:
            self.current = current
            self.constraintProp.switchTo(current)
            
        if current:
            self.constraintProp.refresh(current)
            self.labelLine.setNewVal(current.label)
            #self.currentDetails.setCurrent(current)
        
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

    def select(self, label:str) -> None:
        CommandExec.addCommand(ComSetConstraintAsCurrent(label))

    def fit_cb(self):
        current:ConstraintI = EditorState.getInstance().getCurrentConstraint()
        if current:
            bA = current.bodyA
            bB = current.bodyB
            if bA and bB:
                self.view.viewBodyAOffset.fitToBox(bA.box)
                self.view.viewBodyBOffset.fitToBox(bB.box)
                self.view.viewAllOffset.fitToBoxes((bA.box, bB.box))

    def add_btn(self) -> None:
        label: str = self.labelLine.getVal()
        CommandExec.addCommand(ComAddConstraint(label, self.constraintType.getCurrent()))

    def del_btn(self) -> None:
        label: str = self.labelLine.getVal()
        if label in Database.getInstance().getAllConstraintLabels():
            CommandExec.addCommand(ComDelConstraint(label))

    def up_btn_cb(self) -> None:
        CommandExec.addCommand(ComShiftConstraintUp())

    def down_btn_cb(self) -> None:
        CommandExec.addCommand(ComShiftConstraintDown())

    def swap_cb(self) -> None:
        self.view.swapHideState()

    def clone_cb(self) -> None:
        if self.current:
            CommandExec.addCommand(ComConstraintClone(self.current))

    def rename(self):
        if self.current:
            newName = self.labelLine.getVal()
            oldName = self.current.label
            if newName != oldName:
                CommandExec.addCommand(ComRenameConstraint(self.current, newName))

    def resetDetails(self):
        if self.current:
            self.labelLine.refresh()
