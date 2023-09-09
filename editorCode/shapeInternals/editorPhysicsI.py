from ..editorTypes import UserSettableFloat, ContainerTransform, CenterOfGravity
from ..config import physicsSetup


class PhysicsProp:

    def __init__(self):
        self.cog = CenterOfGravity()
        self.area: float = 1.0
        self.density: UserSettableFloat = UserSettableFloat(1.0 / (physicsSetup['pixelPerMeter'] * physicsSetup['pixelPerMeter']))
        self.mass: UserSettableFloat = UserSettableFloat(1.0)
        self.moment: UserSettableFloat = UserSettableFloat(1.0)

    def recalcPhysics(self, internal, transform:ContainerTransform):
        raise NotImplementedError
    
    def recalcArea(self, internal):
        raise NotImplementedError
    
    def recalcMoment(self, internal):
        raise NotImplementedError