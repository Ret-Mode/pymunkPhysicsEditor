from .editorBodyI import BodyI
from .editorBody import BodyDynamic, BodyKinematic, BodyStatic


def bodyFactory(label: str, typeID: str) -> BodyI:
    if typeID == BodyI.DYNAMIC:
        return BodyDynamic(label)
    elif typeID == BodyI.KINEMATIC:
        return BodyKinematic(label)
    elif typeID == BodyI.STATIC:
        return BodyStatic(label)
    else:
        assert False