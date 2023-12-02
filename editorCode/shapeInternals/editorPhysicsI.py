from ..editorTypes import UserSettableFloat, ContainerTransform, CenterOfGravity


class PhysicsProp:

    def __init__(self):
        self.cog = CenterOfGravity()
        self.area: float = 1.0
        self.density: UserSettableFloat = UserSettableFloat(1.0)
        self.mass: UserSettableFloat = UserSettableFloat(1.0)
        self.moment: UserSettableFloat = UserSettableFloat(1.0)

    def recalcPhysics(self, internal, transform:ContainerTransform):
        raise NotImplementedError
    
    def recalcArea(self, internal):
        raise NotImplementedError
    
    def recalcMoment(self, internal):
        raise NotImplementedError
    
    def clone(self, source:"PhysicsProp") -> "PhysicsProp":
        self.cog.clone(source.cog)
        self.area = source.area
        self.density.clone(source.density)
        self.mass.clone(source.mass)
        self.moment.clone(source.moment)
        return self
