from .editorTypes import V2
from .drawing import drawCursor

class Cursor:

    def __init__(self) -> None:
        self.screenCoords: V2 = V2()
        self.viewCoords: V2 = V2()

    def draw(self):
        drawCursor(self.screenCoords)