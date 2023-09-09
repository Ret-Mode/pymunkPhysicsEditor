from .editorTypes import V2, Angle


class MousePivotParams:

    def __init__(self):
        self.pivot       = V2()
        self.begin       = V2()
        self.end         = V2()
        self.dPivot      = V2()
        self.dEnd        = V2()
        self.dA          = Angle()
        self.dS          = 1.0
        self.angleOffset = 0.0
        self.length      = 0.0

    def reset(self):
        self.begin.setFromV(self.end)
        self.dPivot.setFromV(self.end).unTV(self.pivot)
        self.dEnd.setFromV(self.end).unTV(self.begin)
        self.dA.set(0)
        self.dS = 1.0
        self.angleOffset = self.dPivot.atan2()
        self.length      = self.dPivot.length()

    def set(self, pivot: V2, init: V2):
        self.pivot.setFromV(pivot)
        self.end.setFromV(init)
        self.reset()

    def update(self, end:V2):
        self.end.setFromV(end)
        self.dPivot.setFromV(self.end).unTV(self.pivot)
        self.dEnd.setFromV(self.end).unTV(self.begin)
        self.dA.set(self.dPivot.atan2() - self.angleOffset)
        self.dS = 1.0 if self.length == 0.0 else (self.dPivot.length() / self.length)
