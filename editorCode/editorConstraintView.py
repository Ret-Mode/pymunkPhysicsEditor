
from .editorCamera import EditorCamera
from .editorTypes import EditorPoint
from .editorCursor import Cursor
from .database import Database
from .editorState import EditorState
from .constraintInternals.editorConstraintI import ConstraintI

from .commandExec import CommandExec
from .commandExec import ComSetPivot, ComScaleView, ComResizeView, ComMoveCursor, ComMoveView
from .commandExec import ComSetRestAngleFromXYOffset, ComSetAnchorAFromCoords, ComSetAnchorBFromCoords, ComSetRestLengthFromCoords
from .commandExec import ComSetPhaseFromCoords, ComSetRatioFromCoords, ComSetGrooveAFromCoords, ComSetGrooveBFromCoords, ComSetAnchorsFromCoords
from .commandExec import ComSetRatchetFromCoords, ComSetRotaryMaxFromCoords, ComSetRotaryMinFromCoords, ComSetRateFromCoords
from .commandExec import ComSetSlideMaxFromCoords, ComSetSlideMinFromCoords

from .shapeBuffer import ShapeBuffer
from .lineShader import LineDraw
from .gridShader import GridDraw
from .glContext import GLContextI

from .config import toJSON

from .pymunkTester import testBodies


class EditorConstraintView:

    DEFAULT = "Default"
    ANCHORA = "Anchor A"
    ANCHORB = "Anchor B"
    GROOVEA = "Groove A"
    GROOVEB = "Groove B"
    ANGLE   = "Angle"
    OFFSET  = "Offset"
    DISTMIN = "Dist MIN"
    DISTMAX = "Dist MAX"
    PHASE   = "Phase"
    PHASEMIN = "Phase MIN"
    PHASEMAX = "Phase MAX"
    RATIO   = "Ratio"
    RATCHET   = "Ratchet"

    allowedModes = {ConstraintI.DAMPEDROTARYSPRING: [DEFAULT],
                    ConstraintI.DAMPEDSPRING: [DEFAULT, ANCHORA, ANCHORB],
                    ConstraintI.GEARJOINT: [DEFAULT, RATIO],
                    ConstraintI.GROOVEJOINT: [DEFAULT, GROOVEA, GROOVEB],
                    ConstraintI.PINJOINT: [DEFAULT, ANCHORB],
                    ConstraintI.PIVOTJOINT: [DEFAULT, ANCHORA, ANCHORB],
                    ConstraintI.RATCHETJOINT: [DEFAULT, RATCHET],
                    ConstraintI.ROTARYLIMITJOINT: [DEFAULT, PHASEMAX],
                    ConstraintI.SIMPLEMOTOR: [DEFAULT],
                    ConstraintI.SLIDEJOINT: [DEFAULT, DISTMAX, ANCHORA, ANCHORB]
                    }

    def __init__(self, width, height, cursor:Cursor):
        self.viewAllOffset = EditorCamera(width//2, height)
        self.viewBodyAOffset = EditorCamera(width//2, width//2, width//2, height//2)
        self.viewBodyBOffset = EditorCamera(width//2, width//2, width//2, 0)
        self.cursor = cursor
        self.pivot = EditorPoint()

        self.mode = EditorConstraintView.DEFAULT

        self.objectsUnderCursor = []
        self.hideOthers = False

        self.shader = LineDraw()
        self.gridShader = GridDraw()
        #self.moveView(-width/2, -height/2)


    def pymunkTest(self):
        body = EditorState.getInstance().getCurrentBody()
        if body:
            tmp = {}
            body.getJSONDict(tmp)
            testBodies(toJSON(tmp))


    def setHelperPoint(self):
        CommandExec.addCommand(ComSetPivot(self.pivot.local, self.cursor.viewCoords))

    def resize(self, x:float, y:float):
        CommandExec.addCommand(ComResizeView(self.viewAllOffset, x//2, y))
        CommandExec.addCommand(ComResizeView(self.viewBodyAOffset, x//2, y//2, x//2, y//2))
        CommandExec.addCommand(ComResizeView(self.viewBodyBOffset, x//2, y//2, x//2, 0))

    def moveView(self, dx:float, dy:float):
        view = self._selectView()
        if view:
            CommandExec.addCommand(ComMoveView(view, dx, dy))

    def changeScale(self, dy:float):
        view = self._selectView()
        if view:
            CommandExec.addCommand(ComScaleView(view, self.cursor.viewCoords, dy))

    def moveCursor(self, x:float, y:float):
        view = self._selectView()
        CommandExec.addCommand(ComMoveCursor(view, self.cursor, x, y))

    def clearCurrentOperations(self):
        pass

    def swapHideState(self):
        self.hideOthers = not self.hideOthers

    def setConstraintEditMode(self, mode:str):
        constraint:ConstraintI = EditorState.getInstance().getCurrentConstraint()
        if constraint:
            if mode == EditorConstraintView.ANCHORA and \
                constraint.type == ConstraintI.DAMPEDSPRING:
                self.mode = mode
                return
            if mode == EditorConstraintView.ANCHORB and \
                constraint.type == ConstraintI.DAMPEDSPRING:
                self.mode = mode
                return
            
        self.mode = EditorConstraintView.DEFAULT

    def _selectView(self):
        for view in [self.viewAllOffset, self.viewBodyAOffset, self.viewBodyBOffset]:
            if view.coordsInView(self.cursor.screenCoords.x, self.cursor.screenCoords.y):
                return view
        return None

    def nextMode(self):
        constraint:ConstraintI = EditorState.getInstance().getCurrentConstraint()

        if constraint:
            cType = constraint.type
            if self.mode not in EditorConstraintView.allowedModes[cType]:
                self.mode = EditorConstraintView.DEFAULT
            else:
                length = len(EditorConstraintView.allowedModes[cType])
                index = EditorConstraintView.allowedModes[cType].index(self.mode)
                self.mode = EditorConstraintView.allowedModes[cType][(index + 1) % length]
                pass

    def prevMode(self):
        constraint:ConstraintI = EditorState.getInstance().getCurrentConstraint()

        if constraint:
            cType = constraint.type
            if self.mode not in EditorConstraintView.allowedModes[cType]:
                self.mode = EditorConstraintView.DEFAULT
            else:
                length = len(EditorConstraintView.allowedModes[cType])
                index = EditorConstraintView.allowedModes[cType].index(self.mode)
                self.mode = EditorConstraintView.allowedModes[cType][(length + index - 1) % length]
                pass

    def update(self):
        CommandExec.process()
        self._selectView()

        constraint:ConstraintI = EditorState.getInstance().getCurrentConstraint()
        
        if constraint:
            if self.mode not in EditorConstraintView.allowedModes[constraint.type]:
                self.mode = EditorConstraintView.DEFAULT

            constraint.updateBodies()
            constraint.updateInternals()

    def draw(self):
        
        constraint:ConstraintI = EditorState.getInstance().getCurrentConstraint()

        if constraint:

            context = GLContextI.getInstance()
            buffer = ShapeBuffer.getInstance()
            context.setProjectionAndViewportFromCamera(self.viewAllOffset)

            self.gridShader.drawGrid(self.viewAllOffset)

            
            
            buffer.reset()
            buffer.drawScale = self.viewAllOffset.scale

            constraint.bufferBodies(buffer)
            constraint.bufferInternals(buffer)

            buffer.addHelperPoint(self.pivot.local)
            self.shader.update(buffer.verts, buffer.colors, buffer.indices)

            self.shader.draw()
            

            buffer.reset()
            buffer.drawScale = self.viewBodyAOffset.scale

            context.setProjectionAndViewportFromCamera(self.viewBodyAOffset)

            self.gridShader.drawGrid(self.viewBodyAOffset)

            constraint.bufferBodyA(buffer)
            constraint.bufferInternalA(buffer)

            buffer.addHelperPoint(self.pivot.local)
            self.shader.update(buffer.verts, buffer.colors, buffer.indices)

            self.shader.draw()

            buffer.reset()
            buffer.drawScale = self.viewBodyBOffset.scale

            context.setProjectionAndViewportFromCamera(self.viewBodyBOffset)
            self.gridShader.drawGrid(self.viewBodyBOffset)

            constraint.bufferBodyB(buffer)
            constraint.bufferInternalB(buffer)

            buffer.addHelperPoint(self.pivot.local)
            self.shader.update(buffer.verts, buffer.colors, buffer.indices)

            self.shader.draw()

    def defaultAction(self):
        constraint:ConstraintI = EditorState.getInstance().getCurrentConstraint()

        if constraint and constraint.bodyA and constraint.bodyB:
            view = self._selectView()
            coords = self.cursor.viewCoords
            if constraint.type == ConstraintI.DAMPEDROTARYSPRING:
                if view == self.viewBodyAOffset:
                    center = constraint.bodyA.physics.cog.final
                    CommandExec.addCommand(ComSetRestAngleFromXYOffset(constraint, coords, center))
                else:
                    center = constraint.bodyB.physics.cog.final
                    CommandExec.addCommand(ComSetRestAngleFromXYOffset(constraint, coords, center))
                
            elif constraint.type == ConstraintI.DAMPEDSPRING:
                if view == self.viewBodyAOffset or self.mode == EditorConstraintView.ANCHORA:
                    CommandExec.addCommand(ComSetAnchorAFromCoords(constraint, coords))
                elif view == self.viewBodyBOffset or self.mode == EditorConstraintView.ANCHORB:
                    CommandExec.addCommand(ComSetAnchorBFromCoords(constraint, coords))
                elif view == self.viewAllOffset:
                    CommandExec.addCommand(ComSetRestLengthFromCoords(constraint, coords))

            elif constraint.type == ConstraintI.GEARJOINT:
                if view == self.viewBodyAOffset:
                    isBodyB = False
                else:
                    isBodyB = True
                if self.mode == EditorConstraintView.RATIO:
                    CommandExec.addCommand(ComSetRatioFromCoords(constraint, coords, isBodyB))
                else:
                    CommandExec.addCommand(ComSetPhaseFromCoords(constraint, coords, isBodyB))

            elif constraint.type == ConstraintI.GROOVEJOINT:
                if view == self.viewBodyAOffset:
                    if self.mode == EditorConstraintView.GROOVEB:
                        CommandExec.addCommand(ComSetGrooveBFromCoords(constraint, coords))
                    else:
                        CommandExec.addCommand(ComSetGrooveAFromCoords(constraint, coords))
                elif view == self.viewAllOffset:
                    if self.mode == EditorConstraintView.GROOVEB:
                        CommandExec.addCommand(ComSetGrooveBFromCoords(constraint, coords))
                    elif self.mode == EditorConstraintView.GROOVEA:
                        CommandExec.addCommand(ComSetGrooveAFromCoords(constraint, coords))
                    else:
                        CommandExec.addCommand(ComSetAnchorBFromCoords(constraint, coords))
                else:
                    CommandExec.addCommand(ComSetAnchorBFromCoords(constraint, coords))

            elif constraint.type == ConstraintI.PINJOINT:
                if view == self.viewBodyAOffset:
                    CommandExec.addCommand(ComSetAnchorAFromCoords(constraint, coords))
                elif view == self.viewBodyBOffset:
                    CommandExec.addCommand(ComSetAnchorBFromCoords(constraint, coords))
                elif  self.mode == EditorConstraintView.ANCHORB:
                    CommandExec.addCommand(ComSetAnchorBFromCoords(constraint, coords))
                else:
                    CommandExec.addCommand(ComSetAnchorAFromCoords(constraint, coords))

            elif constraint.type == ConstraintI.PIVOTJOINT:
                if view == self.viewBodyAOffset:
                    CommandExec.addCommand(ComSetAnchorAFromCoords(constraint, coords))
                elif view == self.viewBodyBOffset:
                    CommandExec.addCommand(ComSetAnchorBFromCoords(constraint, coords))
                elif self.mode == EditorConstraintView.ANCHORA:
                    CommandExec.addCommand(ComSetAnchorAFromCoords(constraint, coords))
                elif self.mode == EditorConstraintView.ANCHORB:
                    CommandExec.addCommand(ComSetAnchorBFromCoords(constraint, coords))
                else:
                    CommandExec.addCommand(ComSetAnchorsFromCoords(constraint, coords))

            elif constraint.type == ConstraintI.RATCHETJOINT:
                if view == self.viewBodyAOffset:
                    isBodyB = False
                else:
                    isBodyB = True
                if self.mode == EditorConstraintView.RATCHET:
                    CommandExec.addCommand(ComSetRatchetFromCoords(constraint, coords, isBodyB))
                else:
                    CommandExec.addCommand(ComSetPhaseFromCoords(constraint, coords, isBodyB))

            elif constraint.type == ConstraintI.ROTARYLIMITJOINT:
                if view == self.viewBodyAOffset:
                    isBodyB = False
                else:
                    isBodyB = True
                if self.mode == EditorConstraintView.PHASEMAX:
                    CommandExec.addCommand(ComSetRotaryMaxFromCoords(constraint, coords, isBodyB))
                else:
                    CommandExec.addCommand(ComSetRotaryMinFromCoords(constraint, coords, isBodyB))

            elif constraint.type == ConstraintI.SIMPLEMOTOR:
                if view == self.viewBodyAOffset:
                    isBodyB = False
                else:
                    isBodyB = True
                CommandExec.addCommand(ComSetRateFromCoords(constraint, coords, isBodyB))

            elif constraint.type == ConstraintI.SLIDEJOINT:
                if view == self.viewBodyAOffset or self.mode == EditorConstraintView.ANCHORA:
                    CommandExec.addCommand(ComSetAnchorAFromCoords(constraint, coords))
                elif view == self.viewBodyBOffset or self.mode == EditorConstraintView.ANCHORB:
                    CommandExec.addCommand(ComSetAnchorBFromCoords(constraint, coords))
                else:
                    if self.mode == EditorConstraintView.DISTMAX:
                        CommandExec.addCommand(ComSetSlideMaxFromCoords(constraint, coords))
                    else:
                        CommandExec.addCommand(ComSetSlideMinFromCoords(constraint, coords))

    def undo(self):
        self.clearCurrentOperations()
        CommandExec.undo()

    def redo(self):
        CommandExec.redo()