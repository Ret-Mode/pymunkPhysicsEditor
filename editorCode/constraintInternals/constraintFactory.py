from .editorConstraint import DampedRotarySpring, DampedSpring, GearJoint, GrooveJoint, PinJoint, PivotJoint, RatchetJoint, RotaryLimitJoint, SimpleMotor, SlideJoint
from .editorConstraintI import ConstraintI

def constraintFactory(label: str, typeID: str) -> ConstraintI:
    if typeID == ConstraintI.DAMPEDROTARYSPRING:
        return DampedRotarySpring(label)
    elif typeID == ConstraintI.DAMPEDSPRING:
        return DampedSpring(label)
    elif typeID == ConstraintI.GEARJOINT:
        return GearJoint(label)
    elif typeID == ConstraintI.GROOVEJOINT:
        return GrooveJoint(label)
    elif typeID == ConstraintI.PINJOINT:
        return PinJoint(label)
    elif typeID == ConstraintI.PIVOTJOINT:
        return PivotJoint(label)
    elif typeID == ConstraintI.RATCHETJOINT:
        return RatchetJoint(label)
    elif typeID == ConstraintI.ROTARYLIMITJOINT:
        return RotaryLimitJoint(label)
    elif typeID == ConstraintI.SIMPLEMOTOR:
        return SimpleMotor(label)
    elif typeID == ConstraintI.SLIDEJOINT:
        return SlideJoint(label)
    else:
        assert False